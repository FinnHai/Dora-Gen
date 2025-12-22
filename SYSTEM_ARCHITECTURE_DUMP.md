# System Architecture Dump
**Source of Truth für aktuelle Implementierung**

**Erstellt:** 2025-01-XX  
**Zweck:** Dokumentation der aktuellen Codebase für Bachelor-Thesis "Implementation" Kapitel

---

## 1. Project Structure

```
BA/
├── agents/
│   ├── __init__.py
│   ├── critic_agent.py          # Validierungs-Agent (Reflect-Refine Loop)
│   ├── generator_agent.py       # Inject-Generierungs-Agent (LLM-basiert)
│   ├── intel_agent.py          # TTP-Abfrage-Agent (ChromaDB Vector DB)
│   └── manager_agent.py        # Storyline-Planungs-Agent
├── workflows/
│   ├── __init__.py
│   ├── scenario_workflow.py    # LangGraph Workflow (Haupt-Orchestrierung)
│   ├── state_schema.py         # WorkflowState TypedDict Definition
│   └── fsm.py                  # CrisisFSM (Phasen-Übergangs-Logik)
├── state_models.py             # Pydantic Models (Inject, ScenarioState, etc.)
├── neo4j_client.py             # Neo4j Knowledge Graph Client
├── dashboard.py                # Streamlit Frontend (Haupt-Dashboard)
├── utils/
│   ├── __init__.py
│   └── retry_handler.py        # Retry-Logik für LLM-Calls
├── evaluation/
│   ├── automatic_evaluator.py
│   ├── analysis_metrics.py
│   └── hallucination_test_cases.py
├── tests/
│   ├── test_agents.py
│   ├── test_workflow_basic.py
│   └── test_workflow_integration.py
└── scripts/
    ├── populate_ttp_database.py
    └── start_neo4j.sh
```

---

## 2. Core Architecture (LangGraph)

### 2.1 StateGraph Definition

**Datei:** `workflows/scenario_workflow.py`

Der Workflow wird in `ScenarioWorkflow._create_graph()` erstellt:

```python
workflow = StateGraph(WorkflowState)
```

**State Schema:** `WorkflowState` (TypedDict) definiert in `workflows/state_schema.py`:
- `scenario_id: str`
- `scenario_type: ScenarioType`
- `current_phase: CrisisPhase`
- `injects: List[Inject]`
- `system_state: Dict[str, Any]` (Neo4j Entities)
- `iteration: int`
- `max_iterations: int`
- `manager_plan: Optional[Dict[str, Any]]`
- `selected_action: Optional[Dict[str, Any]]` (TTP)
- `draft_inject: Optional[Inject]`
- `validation_result: Optional[ValidationResult]`
- `available_ttps: List[Dict[str, Any]]`
- `mode: Literal['legacy', 'thesis']` (Default: 'thesis')
- `user_feedback: Optional[str]` (Human-in-the-Loop)

### 2.2 Nodes (Agenten)

**Entry Point:** `state_check` → `manager` → `intel` → `action_selection` → `generator` → `critic` → `state_update`

1. **`state_check`** (`_state_check_node`)
   - **Funktion:** Holt aktuellen Systemzustand aus Neo4j
   - **Filter:** Überspringt Entities mit IDs `INJ-*` oder `SCEN-*`
   - **Fallback:** Erstellt Standard-Assets (`SRV-001`, `SRV-002`) wenn keine Assets gefunden
   - **Output:** `system_state: Dict[str, Any]`

2. **`manager`** (`_manager_node`)
   - **Agent:** `ManagerAgent`
   - **Funktion:** Erstellt Storyline-Plan basierend auf Szenario-Typ und aktueller Phase
   - **Output:** `manager_plan: Dict[str, Any]` (next_phase, narrative, key_events)

3. **`intel`** (`_intel_node`)
   - **Agent:** `IntelAgent`
   - **Funktion:** Holt relevante MITRE ATT&CK TTPs aus ChromaDB (Vector DB)
   - **Filter:** Basierend auf aktueller Phase (`CrisisPhase`)
   - **Output:** `available_ttps: List[Dict[str, Any]]`

4. **`action_selection`** (`_action_selection_node`)
   - **Funktion:** Wählt TTP aus `available_ttps` basierend auf `manager_plan`
   - **Logik:** Erste passende TTP oder Fallback
   - **Output:** `selected_action: Dict[str, Any]` (ttp, mitre_id, name)

5. **`generator`** (`_generator_node`)
   - **Agent:** `GeneratorAgent`
   - **Funktion:** Generiert rohen Inject (JSON → Pydantic `Inject`)
   - **Input:** `user_feedback: Optional[str]` (Human-in-the-Loop)
   - **Output:** `draft_inject: Inject`
   - **Besonderheit:** Berechnet `time_offset` dynamisch basierend auf narrativem Kontext (`T+DD:HH:MM`)

6. **`critic`** (`_critic_node`)
   - **Agent:** `CriticAgent`
   - **Funktion:** Validiert `draft_inject` auf Logik, Konsistenz, DORA-Compliance
   - **Mode:** `mode == 'legacy'` → Skip Validation (simuliert altes System)
   - **Output:** `validation_result: ValidationResult`

7. **`state_update`** (`_state_update_node`)
   - **Funktion:** Aktualisiert Neo4j mit neuen Asset-Status-Änderungen
   - **Logik:** Parst `affected_assets` aus Inject und aktualisiert Status
   - **Output:** `injects: List[Inject]` (fügt validierten Inject hinzu)

### 2.3 Edges (Transitions)

**Sequenzielle Edges:**
- `state_check` → `manager`
- `manager` → `intel`
- `intel` → `action_selection`
- `action_selection` → `generator`
- `generator` → `critic`

**Conditional Edge: Critic → Generator (Refine) oder State Update**
```python
workflow.add_conditional_edges(
    "critic",
    self._should_refine,
    {
        "refine": "generator",    # Zurück zum Generator bei Fehlern
        "update": "state_update"  # Weiter bei Validierung
    }
)
```

**Conditional Edge: State Update → Continue oder End**
```python
workflow.add_conditional_edges(
    "state_update",
    self._should_continue,
    {
        "continue": "state_check",  # Loop zurück
        "end": END
    }
)
```

### 2.4 Conditional Logic

#### `_should_refine(state: WorkflowState) -> str`

**Datei:** `workflows/scenario_workflow.py:1607`

**Logik:**
- Wenn `validation_result.is_valid == False` → `"refine"`
- Max. 2 Refine-Versuche pro Inject (gezählt in `state.metadata["refine_count_{inject_id}"]`)
- Wenn `validation_result.is_valid == True` → `"update"`

**Code:**
```python
if not validation.is_valid:
    refine_key = f"refine_count_{current_inject_id}"
    refine_count = metadata.get(refine_key, 0)
    if refine_count < 2:
        return "refine"
return "update"
```

#### `_should_continue(state: WorkflowState) -> str`

**Datei:** `workflows/scenario_workflow.py:1648`

**Stopp-Bedingungen:**
1. `len(injects) >= max_iterations` → `"end"`
2. `iteration >= max_iterations * 2` → `"end"` (Fallback für Refine-Loops)
3. `len(errors) > 20` → `"end"`
4. `current_phase == RECOVERY` und `len(injects) >= max(3, int(max_iterations * 0.8))` → `"end"`

**Sonst:** → `"continue"` (Loop zurück zu `state_check`)

---

## 3. Data Models (The Symbol Layer)

### 3.1 Inject Schema

**Datei:** `state_models.py:91`

**Pydantic Model:** `Inject`

**Felder:**
- `inject_id: str` (Pattern: `^INJ-\d{3,}$`)
- `time_offset: str` (Pattern: `^T\+(\d{2}):(\d{2})(?::(\d{2}))?$`) - **Akzeptiert `T+DD:HH` und `T+DD:HH:MM`**
- `phase: CrisisPhase` (Enum)
- `source: str` (z.B. "Red Team / Attacker")
- `target: str` (z.B. "Blue Team / SOC")
- `modality: InjectModality` (Enum: SIEM_ALERT, EMAIL, PHONE_CALL, etc.)
- `content: str` (min_length=10)
- `technical_metadata: TechnicalMetadata`
- `dora_compliance_tag: Optional[str]`
- `business_impact: Optional[str]`
- `created_at: Optional[datetime]`

**TechnicalMetadata:**
- `mitre_id: Optional[str]`
- `affected_assets: List[str]` (Asset-IDs)
- `ioc_hash: Optional[str]`
- `ioc_ip: Optional[str]`
- `ioc_domain: Optional[str]`
- `severity: Optional[str]` (Low, Medium, High, Critical)

### 3.2 CrisisPhase Enum

**Datei:** `state_models.py:17`

**Werte:**
- `NORMAL_OPERATION`
- `SUSPICIOUS_ACTIVITY`
- `INITIAL_INCIDENT`
- `ESCALATION_CRISIS`
- `CONTAINMENT`
- `RECOVERY`

**FSM-Übergänge:** Definiert in `workflows/fsm.py:22` (`CrisisFSM.ALLOWED_TRANSITIONS`)

### 3.3 ScenarioType Enum

**Datei:** `state_models.py:27`

**Werte:**
- `RANSOMWARE_DOUBLE_EXTORTION`
- `DDOS_CRITICAL_FUNCTIONS`
- `SUPPLY_CHAIN_COMPROMISE`
- `INSIDER_THREAT_DATA_MANIPULATION`

### 3.4 KnowledgeGraphEntity

**Datei:** `state_models.py:187`

**Felder:**
- `entity_id: str`
- `entity_type: str` (z.B. "Server", "Application", "Database")
- `name: str`
- `status: str` (z.B. "normal", "compromised", "offline", "encrypted")
- `properties: Dict[str, Any]`
- `relationships: List[Dict[str, str]]`

---

## 4. Agent Configuration (The Neuro Layer)

### 4.1 Generator Agent

**Datei:** `agents/generator_agent.py`

**LLM:** `ChatOpenAI(model="gpt-4o", temperature=0.8)`

**System Prompt Highlights:**

1. **CRITICAL ASSET BINDING RULES:**
   - Muss exakte Asset-IDs aus System State verwenden
   - Keine Aliase erfinden (z.B. nicht "DC-01" wenn ID "SRV-001" ist)
   - Keine neuen Assets halluzinieren

2. **Dynamic Time Management Rules:**
   - `time_offset` wird basierend auf narrativem Kontext berechnet
   - High Intensity Events → Kurze Sprünge (`T+00:00:15`)
   - Investigation Phases → Mittlere Sprünge (`T+00:03:00`)
   - Stealth/APT Phases → Lange Sprünge (`T+01:00:00`)
   - Format: `T+DD:HH:MM`

3. **Human-in-the-Loop Integration:**
   - Wenn `user_feedback` vorhanden, muss nächster Inject Konsequenzen reflektieren
   - Beispiel: "Shutdown SRV-001" → Nächster Inject zeigt Service-Offline

4. **Refine-Modus:**
   - Wenn `validation_feedback` vorhanden, korrigiert Generator Fehler
   - **TTP FREEZE:** Generator darf TTP nicht ändern, außer Critic sagt explizit TTP ist falsch

**Validierung:**
- Regex-Check für `time_offset`: `r'^T\+\d{2}:\d{2}(?::\d{2})?$'` (akzeptiert beide Formate)
- Fallback auf übergebenen `time_offset` wenn LLM-Output ungültig

### 4.2 Critic Agent

**Datei:** `agents/critic_agent.py`

**LLM:** `ChatOpenAI(model="gpt-4o", temperature=0.3)` (niedrig für konsistente Validierung)

**Validierungs-Phasen:**

**Phase 1: Symbolische Validierung (OHNE LLM-Call)**
- Pydantic-Validierung (automatisch)
- Asset-ID-Check: Prüft ob `affected_assets` in `system_state` existieren
- Phase-Transition-Check: Prüft ob Übergang erlaubt ist (`CrisisFSM.can_transition`)
- Temporal-Check: Prüft ob `time_offset` chronologisch nach letztem Inject liegt

**Phase 2: LLM-basierte Validierung**
- Logische Konsistenz (Widerspruchsfreiheit zur Historie)
- DORA-Compliance (generische Regulatorik-Prüfung)
- Causal Validity (MITRE ATT&CK Graph Konformität)

**Legacy Mode:**
```python
if mode == 'legacy':
    return ValidationResult(
        is_valid=True,
        logical_consistency=True,
        dora_compliance=True,
        causal_validity=True,
        errors=[],
        warnings=[]
    )
```

**Output:** `ValidationResult` mit:
- `is_valid: bool`
- `logical_consistency: bool`
- `dora_compliance: bool`
- `causal_validity: bool`
- `errors: List[str]`
- `warnings: List[str]`

### 4.3 Manager Agent

**Datei:** `agents/manager_agent.py`

**LLM:** `ChatOpenAI(model="gpt-4o", temperature=0.7)`

**Funktion:** Erstellt Storyline-Plan (`manager_plan`) mit:
- `next_phase: CrisisPhase`
- `narrative: str`
- `key_events: List[str]`

**Logik:** Nutzt `CrisisFSM.suggest_next_phase()` für Phasen-Vorschläge

### 4.4 Intel Agent

**Datei:** `agents/intel_agent.py`

**Vector DB:** ChromaDB (Persistent Client)

**Funktion:** Holt relevante MITRE ATT&CK TTPs basierend auf Phase

**Fallback:** Wenn ChromaDB leer, verwendet `_get_fallback_ttps()` mit hardcodierten TTPs

**TTP-Mapping zu Phasen:**
- `NORMAL_OPERATION` → Reconnaissance TTPs
- `SUSPICIOUS_ACTIVITY` → Initial Access TTPs
- `INITIAL_INCIDENT` → Execution/Persistence TTPs
- `ESCALATION_CRISIS` → Lateral Movement/Exfiltration TTPs
- `CONTAINMENT` → Defense Evasion/Impact TTPs
- `RECOVERY` → Recovery TTPs

---

## 5. Database Integration (Neo4j)

### 5.1 Neo4j Client

**Datei:** `neo4j_client.py`

**Klasse:** `Neo4jClient`

**Connection:** `bolt://localhost:7687` (Standard), Credentials aus `.env`

**Haupt-Methoden:**

1. **`get_current_state(entity_type: Optional[str] = None) -> List[Dict[str, Any]]`**
   - Holt alle Entities aus Neo4j
   - Optional Filter nach `entity_type`
   - **WICHTIG:** Frontend filtert `INJ-*` und `SCEN-*` IDs heraus

2. **`update_entity_status(entity_id: str, new_status: str, inject_id: Optional[str] = None) -> bool`**
   - Aktualisiert Status einer Entity
   - Optional: Verknüpft mit Inject-ID

3. **`calculate_cascading_impact(entity_id: str, new_status: str, max_depth: int = 3) -> Dict[str, Any]`**
   - Berechnet kaskadierende Auswirkungen basierend auf Relationships
   - Verwendet Cypher-Query mit `[*1..max_depth]` für Pfad-Suche
   - Relationship-Typen: `RUNS_ON`, `DEPENDS_ON`, `USES`, `CONNECTS_TO`, `REQUIRES`

### 5.2 Seed Enterprise Infrastructure (Stress Test)

**Datei:** `neo4j_client.py:507`

**Funktion:** `seed_enterprise_infrastructure() -> int`

**Aktion:**
1. **Löscht ALLE bestehenden Entities:** `MATCH (n) DETACH DELETE n`
2. **Erstellt genau 40 Assets:**
   - 5x Core Servers: `SRV-CORE-001` bis `SRV-CORE-005`
   - 15x App Servers: `SRV-APP-001` bis `SRV-APP-015`
   - 10x Databases: `DB-PROD-01` bis `DB-PROD-05` + `DB-DEV-01` bis `DB-DEV-05` (verwirrend ähnlich!)
   - 10x Workstations: `WS-FINANCE-01` bis `WS-FINANCE-10`
3. **Erstellt Relationships:**
   - `SRV-APP-001 RUNS_ON SRV-CORE-001`
   - `SRV-APP-001 USES DB-PROD-01`
   - `WS-FINANCE-01 CONNECTS_TO SRV-APP-001`
   - etc.

**Zweck:** Stress-Test für LLM-Hallucinations (verwirrend ähnliche Asset-Namen)

**Frontend-Integration:** Button "Seed Chaos (40 Assets)" in `dashboard.py:783`

### 5.3 Asset Binding

**Problem:** Generator muss exakte Asset-IDs verwenden, die in Neo4j existieren

**Lösung:**

1. **State Check Node:** Filtert Entities und erstellt `system_state` Dict mit Asset-IDs als Keys
2. **Generator Prompt:** Enthält explizite Liste "VERFÜGBARE ASSET-IDs" aus `system_state`
3. **Critic Validierung:** Prüft ob `affected_assets` in `system_state` existieren

**Code-Beispiel (State Check):**
```python
system_state_dict = {}
for entity in entities:
    entity_id = entity.get("entity_id")
    if entity_id.startswith("INJ-") or entity_id.startswith("SCEN-"):
        continue  # Filter Inject-IDs
    system_state_dict[entity_id] = {
        "status": entity.get("status", "unknown"),
        "entity_type": entity.get("entity_type", "Asset"),
        "name": entity.get("name", entity_id)
    }
```

**Fallback:** Wenn keine Assets gefunden → Erstellt `SRV-001`, `SRV-002`

---

## 6. Frontend Features (Streamlit)

### 6.1 Tab 1: Live Simulation

**Datei:** `dashboard.py:752`

**Features:**

1. **Cyber-HUD Asset Grid:**
   - CSS-basiertes Grid-Layout (`asset-grid-container`)
   - Asset-Cards mit Status-Farben:
     - `compromised` → Rot (`#ff4b4b`)
     - `suspicious` → Orange (`#ffa500`)
     - `degraded` → Gelb (`#ffff00`)
     - `normal` → Grün (`#10b981`)
   - Sortierung: Kompromittierte Assets zuerst
   - HTML-Rendering: `st.markdown(..., unsafe_allow_html=True)`

2. **Clean Start:**
   - Beim "Start Simulation" oder "Reset": Alle Assets auf `status='normal'`
   - Aktualisiert Neo4j State falls Backend verfügbar
   - `get_default_assets()` gibt Standard-Assets zurück

3. **Interactive Mode (Human-in-the-Loop):**
   - Text Input: `st.text_input("Incident Response Action", key="user_action_input")`
   - Button: "Execute Response & Generate Next Inject"
   - `user_action` wird an `run_next_step(scenario_type, num_steps=1, user_action=user_action)` übergeben
   - **State Management:** Flag-Mechanismus (`clear_user_action`) zum Leeren des Inputs nach Generierung

4. **Generation Modes:**
   - **Single Step:** Generiert 1 Inject (mit optionalem `user_action`)
   - **Multiple Steps:** Generiert N Injects (`st.number_input("Number of Injects")`)

5. **Infinite Run:**
   - Keine hardcodierte `max_iterations` Limit im Frontend
   - Workflow stoppt nur bei End-Bedingungen (`_should_continue`)

**Backend Integration:**
- `run_next_step()` erstellt `WorkflowState` und ruft `workflow.graph.stream()` auf
- Sammelt State-Updates und fügt neue Injects zu `st.session_state.history` hinzu

### 6.2 Tab 2: Batch Experiment (A/B Testing)

**Datei:** `dashboard.py:600` (geschätzt, nicht vollständig gelesen)

**Funktion:** `run_batch_evaluation(scenario_type: ScenarioType, num_scenarios: int) -> pd.DataFrame`

**Logik:**

1. **A/B Loop:**
   ```python
   for i in range(num_scenarios):
       # Run A (Legacy Mode)
       state_legacy = {...}
       state_legacy["mode"] = "legacy"
       result_legacy = workflow.graph.invoke(state_legacy)
       
       # Run B (Thesis Mode)
       state_thesis = {...}
       state_thesis["mode"] = "thesis"
       result_thesis = workflow.graph.invoke(state_thesis)
       
       # Compare
       comparison_data.append({
           "scenario_id": ...,
           "legacy_errors_missed": ...,
           "thesis_errors_caught": ...,
           "hallucinations_prevented": ...
       })
   ```

2. **Visualization:**
   - Plotly Bar Chart: Legacy vs Thesis Hallucinations
   - DataFrame mit detaillierten Metriken

**Metriken:**
- `legacy_errors_missed`: Anzahl Fehler, die Legacy Mode akzeptiert hat
- `thesis_errors_caught`: Anzahl Fehler, die Thesis Mode gefangen hat
- `hallucinations_prevented`: Differenz zwischen Legacy und Thesis

### 6.3 Tab 3: Thesis Results

**Nicht vollständig analysiert** (muss noch gelesen werden)

**Vermutlich:** Analyse-Metriken aus `evaluation/analysis_metrics.py`

---

## 7. Current Limitations & "Hacks"

### 7.1 Hardcoded Values

1. **Default Assets:** `get_default_assets()` in `dashboard.py:206` hardcodiert `SRV-001`, `SRV-002`, `APP-001`, `APP-002`
2. **Max Refine Versuche:** Hardcodiert auf 2 in `_should_refine()` (`refine_count < 2`)
3. **Max Errors:** Hardcodiert auf 20 in `_should_continue()` (`len(errors) > 20`)
4. **Recovery Phase Threshold:** Hardcodiert auf `max(3, int(max_iterations * 0.8))` für Recovery-End-Bedingung

### 7.2 Temporary Fixes

1. **Streamlit State Management für `user_action_input`:**
   - Flag-Mechanismus (`clear_user_action`) statt direkter State-Modifikation
   - **Grund:** Streamlit erlaubt keine State-Modifikation nach Widget-Erstellung

2. **Time Offset Format-Kompatibilität:**
   - Pydantic Pattern akzeptiert beide Formate (`T+DD:HH` und `T+DD:HH:MM`)
   - **Grund:** Generator generiert `T+DD:HH:MM`, aber Fallback verwendet `T+DD:HH`

3. **Asset-ID Fallback:**
   - Wenn keine Assets in Neo4j gefunden → Erstellt `SRV-001`, `SRV-002`
   - **Grund:** Verhindert Fehler wenn Datenbank leer ist

### 7.3 Known Issues

1. **Generator Asset-ID Hallucinations:**
   - Generator verwendet manchmal alte/generische IDs (`SRV-001`) statt neue Enterprise-IDs (`SRV-CORE-001`)
   - **Ursache:** LLM ist nicht immer konsistent mit Asset-Liste im Prompt
   - **Workaround:** Critic fängt diese Fehler ab (State-Consistency Check)

2. **ChromaDB TTP Database:**
   - Kann leer sein beim ersten Start
   - **Fallback:** `IntelAgent._get_fallback_ttps()` mit hardcodierten TTPs
   - **Auto-Population:** Versucht automatisch TTPs zu laden, kann fehlschlagen

3. **Neo4j Relationship-Namen in `seed_enterprise_infrastructure`:**
   - Code zeigt `DB-SQL-03`, `DB-SQL-04` in Relationships, aber Assets heißen `DB-PROD-01`, `DB-DEV-01`
   - **Vermutung:** Inkonsistenz zwischen Code-Kommentaren und tatsächlicher Implementierung

### 7.4 Missing Features

1. **Interaktiver Modus (`interactive_mode=True`):**
   - `decision_point` Node existiert im Workflow, aber nicht vollständig implementiert
   - Frontend verwendet `user_feedback` statt `decision_point` Mechanismus

2. **Workflow-Logs im Dashboard:**
   - `workflow_logs` werden im State gesammelt, aber nicht im Frontend angezeigt
   - `agent_decisions` werden gesammelt, aber nicht visualisiert

3. **Cascading Impact Visualization:**
   - `calculate_cascading_impact()` existiert, aber Frontend zeigt keine Impact-Visualisierung

---

## 8. Key Implementation Details

### 8.1 Workflow Execution

**Frontend → Backend:**
```python
# dashboard.py:run_next_step()
current_state: WorkflowState = {
    "scenario_id": ...,
    "scenario_type": scenario_type,
    "current_phase": current_phase,
    "injects": st.session_state.history.copy(),
    "system_state": get_assets_from_backend(),
    "mode": "thesis",
    "user_feedback": user_action
}

stream = workflow.graph.stream(current_state, config={"recursion_limit": 50})
```

**Backend → Frontend:**
- Sammelt State-Updates aus Stream
- Extrahiert neue Injects: `new_injects = step_final_state.get("injects", [])`
- Aktualisiert `st.session_state.history`

### 8.2 State Persistence

- **Neo4j:** Persistiert Asset-Status zwischen Workflow-Runs
- **Streamlit Session State:** Persistiert `history`, `system_state`, `current_scenario_id` während Session
- **Keine persistente Szenario-Historie:** Jeder "Start Simulation" beginnt neu

### 8.3 Error Handling

- **LLM-Calls:** `utils/retry_handler.safe_llm_call()` mit Retry-Logik
- **Neo4j:** Try-Catch in `get_current_state()`, Fallback auf Default-Assets
- **Workflow:** Fehler werden in `state.errors` gesammelt, stoppen Workflow nach 20 Fehlern

---

**Ende des Dokuments**

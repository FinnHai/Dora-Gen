# CRUX Backend-Workflow - Detaillierte Dokumentation

## Übersicht

Das CRUX-Backend verwendet **LangGraph** zur Orchestrierung eines Multi-Agenten-Systems für die Generierung von Krisenszenarien. Der Workflow verwaltet State über **Neo4j** (Knowledge Graph) und **In-Memory State** (LangGraph WorkflowState).

---

## 🏗️ Architektur-Übersicht

```
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Workflow                        │
│                  (In-Memory State Management)                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │      WorkflowState (TypedDict)        │
        │  - Szenario-Metadaten                 │
        │  - Injects (List[Inject])             │
        │  - System State (Dict)                 │
        │  - Agenten-Outputs                   │
        │  - Workflow-Logs                      │
        └───────────────┬───────────────────────┘
                        │
                        │ State Updates
                        │
        ┌───────────────▼───────────────────────┐
        │      Neo4j Knowledge Graph              │
        │  - Entities (Assets, Services)         │
        │  - Relationships (Dependencies)         │
        │  - Status (online, compromised, etc.)   │
        │  - Temporal State (last_updated)      │
        └─────────────────────────────────────────┘
```

---

## 📊 WorkflowState Schema

### Definition (`workflows/state_schema.py`)

```python
class WorkflowState(TypedDict):
    # Szenario-Metadaten
    scenario_id: str                    # Eindeutige Szenario-ID (z.B. "SCEN-ABC123")
    scenario_type: ScenarioType         # RANSOMWARE_DOUBLE_EXTORTION, DDoS, etc.
    current_phase: CrisisPhase          # Aktuelle Krisenphase
    
    # Generierte Injects
    injects: List[Inject]               # Liste aller validierten Injects
    
    # Aktueller Systemzustand (aus Neo4j)
    system_state: Dict[str, Any]        # entity_id -> entity_data
                                        # Beispiel: {"SRV-001": {"status": "online", ...}}
    
    # Workflow-Kontrolle
    iteration: int                      # Aktuelle Iteration (0-basiert)
    max_iterations: int                 # Maximale Anzahl Injects
    
    # Agenten-Outputs
    manager_plan: Optional[Dict]       # Storyline vom Manager Agent
    selected_action: Optional[Dict]     # Ausgewählte TTP
    draft_inject: Optional[Inject]      # Roher Inject vom Generator
    validation_result: Optional[ValidationResult]  # Validierung vom Critic
    
    # Intel & Kontext
    available_ttps: List[Dict]          # Verfügbare TTPs vom Intel Agent
    historical_context: List[Dict]      # Vorherige Injects für Konsistenz
    
    # Fehlerbehandlung
    errors: List[str]
    warnings: List[str]
    
    # Metadaten
    start_time: datetime
    metadata: Dict[str, Any]            # Refinement-Counts, etc.
    
    # Workflow-Logs für Dashboard
    workflow_logs: List[Dict]           # Logs von jedem Node
    agent_decisions: List[Dict]         # Entscheidungen der Agenten
    
    # Interaktive Entscheidungen
    pending_decision: Optional[Dict]
    user_decisions: List[Dict]
    end_condition: Optional[str]
    interactive_mode: bool
    
    # Mode für A/B Testing
    mode: Literal['legacy', 'thesis']   # 'legacy' = Skip Validation
    
    # Human-in-the-Loop Feedback
    user_feedback: Optional[str]
```

### State-Lifecycle

1. **Initialisierung:** `scenario_id`, `scenario_type`, `current_phase` werden gesetzt
2. **Iteration 0:** `system_state` wird aus Neo4j geladen
3. **Pro Iteration:** State wird durch Agenten-Nodes aktualisiert
4. **Finalisierung:** `injects` Liste enthält alle generierten Injects

---

## 🔄 Workflow-Flow (LangGraph)

### Node-Sequenz

```
┌──────────────┐
│ State Check  │  ← Entry Point
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Manager    │  ← Storyline-Planung
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Intel     │  ← TTP-Abfrage (ChromaDB)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Action     │  ← TTP-Auswahl
│  Selection   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Generator   │  ← Inject-Generierung (LLM)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Critic    │  ← Validierung
└──────┬───────┘
       │
       ├─── Valid? ───┐
       │              │
       │          ┌───▼───┐
       │          │Refine │  ← Zurück zu Generator
       │          └───┬───┘
       │              │
       └─── Invalid? ──┘
              │
              ▼
       ┌──────────────┐
       │ State Update │  ← Neo4j Update
       └──────┬───────┘
              │
              ├─── Continue? ───┐
              │                 │
              │             ┌───▼────┐
              │             │  END   │
              │             └────────┘
              │
              └─── Loop? ───► State Check (neue Iteration)
```

### Conditional Edges

**Critic → State Update / Generator:**
```python
def _should_refine(state: WorkflowState) -> str:
    validation = state.get("validation_result")
    if not validation or validation.is_valid:
        return "update"  # Weiter zu State Update
    else:
        refine_count = state.get("metadata", {}).get(f"refine_count_{inject_id}", 0)
        if refine_count < 2:
            return "refine"  # Zurück zu Generator
        else:
            return "update"  # Max. Refinements erreicht
```

**State Update → Continue / End:**
```python
def _should_continue(state: WorkflowState) -> str:
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 10)
    
    if iteration >= max_iterations:
        return "end"
    elif state.get("end_condition") in ["FATAL", "VICTORY"]:
        return "end"
    else:
        return "continue"  # Loop zurück zu State Check
```

---

## 🗄️ Neo4j State Management

### Datenbank-Schema

#### Entity-Struktur

```cypher
(:Entity {
    id: String,              // Eindeutige Asset-ID (z.B. "SRV-001")
    type: String,           // "Server", "Application", "Database", etc.
    name: String,           // Anzeigename
    status: String,         // "online", "offline", "compromised", "encrypted", "degraded", "suspicious"
    criticality: String,   // "critical", "high", "standard", "low"
    last_updated: DateTime,
    last_updated_by_inject: String  // Inject-ID, der Status geändert hat
})
```

#### Relationship-Typen

```cypher
(:Entity)-[:RUNS_ON]->(:Entity)        // App läuft auf Server
(:Entity)-[:DEPENDS_ON]->(:Entity)     // Service-Abhängigkeit
(:Entity)-[:USES]->(:Entity)            // App nutzt Datenbank
(:Entity)-[:CONNECTS_TO]->(:Entity)     // Netzwerk-Verbindung
(:Entity)-[:REQUIRES]->(:Entity)        // Kritische Abhängigkeit
```

### Neo4j Client (`neo4j_client.py`)

#### Wichtige Methoden

**1. `get_current_state(entity_type: Optional[str] = None)`**
```python
# Ruft alle Entities mit ihren Relationships ab
# Returns: List[Dict] mit entity_id, entity_type, status, relationships
```

**Query:**
```cypher
MATCH (e)
OPTIONAL MATCH (e)-[r]->(related)
RETURN e, collect(r) as relationships, collect(related) as related_entities
LIMIT 100
```

**2. `update_entity_status(entity_id: str, new_status: str, inject_id: Optional[str])`**
```python
# Aktualisiert Status einer Entity
# Setzt last_updated und last_updated_by_inject
```

**Query:**
```cypher
MATCH (e {id: $entity_id})
SET e.status = $new_status,
    e.last_updated = datetime(),
    e.last_updated_by_inject = $inject_id
```

**3. `get_affected_entities(entity_id: str, max_depth: int = 3)`**
```python
# Rekursive Abhängigkeitsanalyse
# Findet alle Entities, die von Statusänderung betroffen sind
```

**Query:**
```cypher
MATCH path = (source {id: $entity_id})-[*1..3]->(target)
WHERE ALL(r in relationships(path) 
    WHERE type(r) IN ['RUNS_ON', 'DEPENDS_ON', 'USES', 'CONNECTS_TO', 'REQUIRES'])
RETURN DISTINCT target.id as affected_id, length(path) as depth
ORDER BY depth, target.id
```

**4. `calculate_cascading_impact(entity_id: str, new_status: str, max_depth: int = 3)`**
```python
# Berechnet kaskadierende Auswirkungen
# Returns: {
#     "affected_entities": List[Dict],
#     "critical_paths": List[Dict],
#     "estimated_recovery_time": str,
#     "impact_severity": str
# }
```

**Query:**
```cypher
MATCH path = (source {id: $entity_id})-[*1..3]->(target)
WHERE ALL(r in relationships(path) 
    WHERE type(r) IN ['RUNS_ON', 'DEPENDS_ON', 'USES', 'CONNECTS_TO', 'REQUIRES'])
WITH target, length(path) as depth, path
RETURN DISTINCT 
    target.id as entity_id,
    target.name as entity_name,
    target.type as entity_type,
    target.status as current_status,
    depth,
    [r in relationships(path) | type(r)] as relationship_chain
ORDER BY depth, target.type
```

### State-Update-Mechanismus

#### State Check Node (`_state_check_node`)

**Zweck:** Lädt aktuellen Systemzustand aus Neo4j in WorkflowState

**Performance-Tracking:**
```python
node_start_time = time.time()  # Zu Beginn
# ... Node-Logik ...
self.performance_monitor.end_node("state_check", node_start_time, success=True)
```

**Prozess:**
1. Startet Performance-Tracking (`node_start_time = time.time()`)
2. Ruft `neo4j_client.get_current_state()` auf
3. Filtert Entities (überspringt `INJ-*` und `SCEN-*` IDs)
4. Validiert Entity-Typen (nur Server, Application, Database, etc.)
5. Konvertiert zu Dictionary: `entity_id -> entity_data`
6. Fallback: Erstellt Standard-Assets wenn DB leer
7. Beendet Performance-Tracking (`performance_monitor.end_node()`)

**Filter-Logik:**
- Überspringt alle IDs die mit `INJ-` oder `SCEN-` beginnen
- Akzeptiert nur Entities mit:
  - Gültigem Entity-Type (`server`, `application`, `database`, `service`, `asset`, `system`)
  - ODER Asset-Präfix (`SRV-`, `APP-`, `DB-`, `SVC-`, `SYS-`)

**Output:**
```python
{
    "system_state": {
        "SRV-001": {
            "status": "online",
            "entity_type": "Server",
            "name": "SRV-001",
            "criticality": "standard"
        },
        ...
    },
    "workflow_logs": [...]
}
```

#### State Update Node (`_state_update_node`)

**Zweck:** Schreibt Inject-Auswirkungen in Neo4j

**Prozess:**

1. **Direkte Asset-Updates:**
```python
for asset_id in draft_inject.technical_metadata.affected_assets:
    new_status = self._determine_asset_status(
        draft_inject.phase,
        draft_inject.technical_metadata.mitre_id
    )
    neo4j_client.update_entity_status(
        entity_id=asset_id,
        new_status=new_status,
        inject_id=draft_inject.inject_id
    )
```

2. **Second-Order Effects (Kaskadierende Auswirkungen):**
```python
cascading_impact = neo4j_client.calculate_cascading_impact(
    entity_id=asset_id,
    new_status=new_status,
    max_depth=3
)

# Update betroffene Entitäten basierend auf Tiefe
for affected_entity in cascading_impact["affected_entities"]:
    if affected_entity["depth"] == 1:
        affected_status = "degraded" if new_status != "compromised" else "suspicious"
    else:
        affected_status = "degraded"
    
    neo4j_client.update_entity_status(
        entity_id=affected_entity["entity_id"],
        new_status=affected_status,
        inject_id=draft_inject.inject_id
    )
```

**Status-Mapping (Phase → Status):**
```python
def _determine_asset_status(phase: CrisisPhase, mitre_id: str) -> str:
    if phase == CrisisPhase.NORMAL_OPERATION:
        return "online"
    elif phase == CrisisPhase.SUSPICIOUS_ACTIVITY:
        return "suspicious"
    elif phase == CrisisPhase.INITIAL_INCIDENT:
        return "compromised"
    elif phase == CrisisPhase.ESCALATION_CRISIS:
        return "compromised"  # Oder "encrypted" bei Ransomware
    elif phase == CrisisPhase.CONTAINMENT:
        return "degraded"
    elif phase == CrisisPhase.RECOVERY:
        return "degraded"  # Oder "online" bei vollständiger Recovery
```

---

## 🔀 Finite State Machine (FSM)

### Phasen-Übergänge (`workflows/fsm.py`)

```python
ALLOWED_TRANSITIONS = {
    CrisisPhase.NORMAL_OPERATION: [
        CrisisPhase.SUSPICIOUS_ACTIVITY,
        CrisisPhase.INITIAL_INCIDENT  # Kann direkt springen
    ],
    CrisisPhase.SUSPICIOUS_ACTIVITY: [
        CrisisPhase.INITIAL_INCIDENT,
        CrisisPhase.NORMAL_OPERATION  # False Positive
    ],
    CrisisPhase.INITIAL_INCIDENT: [
        CrisisPhase.ESCALATION_CRISIS,
        CrisisPhase.CONTAINMENT  # Schnelle Eindämmung
    ],
    CrisisPhase.ESCALATION_CRISIS: [
        CrisisPhase.CONTAINMENT
    ],
    CrisisPhase.CONTAINMENT: [
        CrisisPhase.RECOVERY,
        CrisisPhase.ESCALATION_CRISIS  # Re-Eskalation möglich
    ],
    CrisisPhase.RECOVERY: [
        CrisisPhase.NORMAL_OPERATION
    ]
}
```

### FSM-Validierung (Critic Agent)

**Prüfung:**
```python
def _validate_phase_transition_detailed(inject: Inject, current_phase: CrisisPhase, previous_injects: List[Inject]) -> Dict:
    inject_phase = inject.phase
    
    # Prüfe erlaubten Übergang
    if not CrisisFSM.can_transition(current_phase, inject_phase):
        return {
            "valid": False,
            "errors": [f"Phase-Übergang nicht erlaubt: {current_phase.value} → {inject_phase.value}"]
        }
    
    # Prüfe temporale Konsistenz (Phase darf nicht zurückgehen)
    if inject_phase.value < current_phase.value:
        return {
            "valid": False,
            "errors": [f"Phase kann nicht zurückgehen: {current_phase.value} → {inject_phase.value}"]
        }
    
    return {"valid": True}
```

---

## 📈 State-Persistierung

### WorkflowState → Neo4j

**Trigger:** Nach erfolgreicher Inject-Validierung

**Persistierte Daten:**

1. **Entity-Status-Updates:**
   - Direkte betroffene Assets
   - Second-Order betroffene Assets (kaskadierend)
   - Status-Änderungen mit Timestamp
   - Inject-ID als Referenz

2. **Metadaten:**
   - `last_updated`: DateTime
   - `last_updated_by_inject`: Inject-ID

### Neo4j → WorkflowState

**Trigger:** Zu Beginn jeder Iteration (State Check Node)

**Geladene Daten:**

1. **Alle Entities:**
   - Entity-ID, Type, Name
   - Status, Criticality
   - Relationships (für Abhängigkeitsanalyse)

2. **Filterung:**
   - Überspringt `INJ-*` und `SCEN-*` IDs
   - Nur echte Assets (Server, Application, Database, etc.)

### State-Synchronisation

**Problem:** WorkflowState ist In-Memory, Neo4j ist persistent

**Lösung:**
- **Read:** State Check lädt State aus Neo4j zu Beginn jeder Iteration
- **Write:** State Update schreibt Änderungen sofort nach Inject-Validierung
- **Konsistenz:** Jede Iteration startet mit aktuellem Neo4j-State

---

## 🔍 Detaillierte State-Übergänge

### Iteration 0 (Initialisierung)

```python
WorkflowState = {
    "scenario_id": "SCEN-ABC123",
    "scenario_type": ScenarioType.RANSOMWARE_DOUBLE_EXTORTION,
    "current_phase": CrisisPhase.NORMAL_OPERATION,
    "injects": [],
    "system_state": {},  # Noch leer
    "iteration": 0,
    "max_iterations": 10,
    ...
}
```

**State Check Node:**
```python
# Lädt aus Neo4j
entities = neo4j_client.get_current_state()
# Konvertiert zu Dictionary
system_state = {
    "SRV-001": {"status": "online", ...},
    "SRV-002": {"status": "online", ...},
    ...
}
```

**WorkflowState nach State Check:**
```python
{
    "system_state": {
        "SRV-001": {"status": "online", ...},
        ...
    },
    "workflow_logs": [{"node": "State Check", ...}]
}
```

### Iteration N (Inject-Generierung)

**Nach Generator Node:**
```python
{
    "draft_inject": Inject(
        inject_id="INJ-001",
        phase=CrisisPhase.SUSPICIOUS_ACTIVITY,
        technical_metadata=TechnicalMetadata(
            affected_assets=["SRV-001", "SRV-002"]
        )
    )
}
```

**Nach Critic Node:**
```python
{
    "validation_result": ValidationResult(
        is_valid=True,
        logical_consistency=True,
        causal_validity=True,
        errors=[],
        warnings=["Regulatory compliance could be improved"]
    )
}
```

**Nach State Update Node:**
```python
# Neo4j Updates:
# - SRV-001.status = "suspicious"
# - SRV-002.status = "suspicious"
# - SRV-001.last_updated_by_inject = "INJ-001"
# - SRV-002.last_updated_by_inject = "INJ-001"

# WorkflowState Updates:
{
    "injects": [Inject(...)],  # Inject hinzugefügt
    "iteration": 1,  # Erhöht
    "workflow_logs": [...]
}
```

### Iteration N+1 (Nächste Iteration)

**State Check Node (neu):**
```python
# Lädt AKTUELLEN State aus Neo4j (inkl. Updates von Iteration N)
entities = neo4j_client.get_current_state()
# SRV-001 und SRV-002 haben jetzt status="suspicious"
```

**WorkflowState nach State Check:**
```python
{
    "system_state": {
        "SRV-001": {"status": "suspicious", ...},  # ← Aktualisiert!
        "SRV-002": {"status": "suspicious", ...},  # ← Aktualisiert!
        ...
    }
}
```

---

## 🎯 Second-Order Effects (Kaskadierende Auswirkungen)

### Beispiel: Server fällt aus

**Initial State:**
```
SRV-CORE-001 (online)
    ↓ RUNS_ON
SRV-APP-001 (online)
    ↓ USES
DB-SQL-001 (online)
```

**Inject:** "SRV-CORE-001 ist offline"

**Direkte Auswirkung:**
```python
neo4j_client.update_entity_status("SRV-CORE-001", "offline", "INJ-001")
```

**Kaskadierende Auswirkungen:**
```python
cascading_impact = neo4j_client.calculate_cascading_impact(
    entity_id="SRV-CORE-001",
    new_status="offline",
    max_depth=3
)

# Returns:
{
    "affected_entities": [
        {"entity_id": "SRV-APP-001", "depth": 1, ...},  # Direkte Abhängigkeit
        {"entity_id": "DB-SQL-001", "depth": 2, ...}    # Indirekte Abhängigkeit
    ],
    "critical_paths": [...],
    "impact_severity": "High",
    "estimated_recovery_time": "8-12 hours"
}
```

**Updates:**
```python
# SRV-APP-001 → degraded (depth=1, direkte Abhängigkeit)
neo4j_client.update_entity_status("SRV-APP-001", "degraded", "INJ-001")

# DB-SQL-001 → degraded (depth=2, indirekte Abhängigkeit)
neo4j_client.update_entity_status("DB-SQL-001", "degraded", "INJ-001")
```

**Final State:**
```
SRV-CORE-001 (offline) ← INJ-001
    ↓ RUNS_ON
SRV-APP-001 (degraded) ← INJ-001 (Second-Order)
    ↓ USES
DB-SQL-001 (degraded) ← INJ-001 (Second-Order)
```

---

## 🔐 State-Konsistenz & Validierung

### Konsistenz-Regeln

1. **Temporale Konsistenz:**
   - Phase darf nicht zurückgehen (außer False Positive)
   - Zeitstempel müssen chronologisch sein

2. **Asset-Konsistenz:**
   - Assets müssen in Neo4j existieren
   - Status-Änderungen müssen logisch sein (online → offline, nicht umgekehrt)

3. **Abhängigkeits-Konsistenz:**
   - Wenn Server offline → Apps müssen degraded sein
   - Wenn App offline → Services müssen degraded sein

### Validierung im Critic Agent

**Phase 1: Symbolische Validierung (OHNE LLM):**
- Pydantic-Validierung
- FSM-Validierung (Phase-Übergang)
- State-Consistency-Check (Asset-Existenz)
- Temporale Konsistenz

**Phase 2: LLM-Validierung (NUR wenn Phase 1 OK):**
- Logical Consistency
- DORA Compliance
- Causal Validity

---

## 📊 State-Metriken & Monitoring

### Workflow-Logs

**Jeder Node loggt:**
```python
{
    "timestamp": "2025-12-20T10:33:52",
    "node": "State Check",
    "iteration": 0,
    "action": "Systemzustand abfragen",
    "details": {
        "entities_found": 30,
        "assets_after_filter": 30,
        "asset_ids": ["SRV-001", ...],
        "status": "success"
    }
}
```

### Agent-Decisions

**Jeder Agent loggt Entscheidungen:**
```python
{
    "timestamp": "2025-12-20T10:33:52",
    "agent": "Manager",
    "iteration": 0,
    "decision_type": "Phase Transition",
    "input": {...},
    "output": {
        "next_phase": "SUSPICIOUS_ACTIVITY",
        "narrative": "..."
    }
}
```

### Forensic Trace

**Persistiert in `logs/forensic/forensic_trace.jsonl`:**
- Draft Injects (vor Validierung)
- Critic-Validierungen
- Refinement-History
- State-Updates

---

## 🚀 Performance-Optimierungen

### 1. State-Caching (`WorkflowOptimizer`)

**Problem:** Neo4j-Queries sind langsam (~100-200ms)

**Lösung:** State wird pro Iteration nur einmal geladen (State Check Node)

**Implementierung:**
```python
class WorkflowOptimizer:
    def __init__(self):
        self.state_cache: Dict[str, tuple] = {}  # key -> (data, timestamp)
        self.cache_ttl = timedelta(seconds=30)
    
    def get_cached_state(self, cache_key: str, fetch_function: callable, force_refresh: bool = False):
        # Prüft Cache (TTL: 30 Sekunden)
        # Bei Cache-Miss: Lädt neu und speichert im Cache
```

**Cache-Verhalten:**
- TTL: 30 Sekunden
- Automatische Invalidierung nach TTL
- Manuelles Clearing möglich

### 2. Batch-Updates

**Problem:** Viele einzelne Updates sind langsam

**Lösung:** State Update Node sammelt alle Updates und führt sie sequenziell aus

### 3. Rekursive Abhängigkeitsanalyse

**Problem:** Tiefe Rekursion kann langsam sein

**Lösung:** `max_depth=3` begrenzt Rekursionstiefe

### 4. Early Exit-Strategien

**Problem:** Workflow sollte bei kritischen Fehlern stoppen

**Implementierung:**
```python
def should_early_exit(
    self,
    errors: List[str],
    warnings: List[str],
    consecutive_failures: int
) -> Tuple[bool, str]:
    # Exit wenn:
    # - 3+ aufeinanderfolgende Fehler
    # - 20+ Gesamtfehler
    # - FATAL-Fehler vorhanden
```

**Exit-Bedingungen:**
- `max_consecutive_errors = 3`
- `max_total_errors = 20`
- FATAL-Fehler im State

### 5. Performance-Monitoring (`WorkflowPerformanceMonitor`)

**Zweck:** Misst Ausführungszeit jedes Nodes für Performance-Analysen

**Implementierung:**
```python
class WorkflowPerformanceMonitor:
    def start_node(self, node_name: str) -> float:
        return time.time()
    
    def end_node(self, node_name: str, start_time: float, success: bool):
        duration = time.time() - start_time
        # Speichert Metriken für Analyse
```

**Gemessene Metriken:**
- Node-Ausführungszeit (Millisekunden)
- Erfolgsrate pro Node
- Durchschnittliche Ausführungszeit
- Fehlerrate
- Gesamt-Workflow-Zeit

---

## 🐛 Bekannte Limitationen

### 1. State-Synchronisation

**Problem:** WorkflowState ist In-Memory, kann bei Crash verloren gehen

**Mitigation:** Neo4j ist persistent, State kann neu geladen werden

### 2. Concurrent Updates

**Problem:** Mehrere Workflows können gleichzeitig Neo4j updaten

**Mitigation:** Neo4j Transactions gewährleisten Konsistenz

### 3. Performance bei vielen Entities

**Problem:** `get_current_state()` kann bei >1000 Entities langsam sein

**Mitigation:** Limit auf 100 Entities, Filterung nach Entity-Type

---

## 📚 Code-Struktur

```
workflows/
├── scenario_workflow.py       # LangGraph Workflow-Orchestrierung
├── state_schema.py             # WorkflowState TypedDict Definition
├── fsm.py                      # Finite State Machine für Phasen
└── workflow_optimizations.py  # Performance-Optimierungen & Monitoring

neo4j_client.py                 # Neo4j Client & State Management
state_models.py                 # Pydantic Models (Inject, etc.)
forensic_logger.py              # Forensic Trace Logging
```

### Wichtige Abhängigkeiten

**Externe Bibliotheken:**
- `langgraph`: Workflow-Orchestrierung
- `langchain`: LLM-Integration
- `neo4j`: Graph-Datenbank
- `pydantic`: Datenvalidierung
- `python-multipart`: File-Uploads (FastAPI)

**Interne Module:**
- `agents/`: Manager, Intel, Generator, Critic Agents
- `Compliance/`: Compliance-Frameworks (DORA, NIST, ISO27001)
- `utils/`: Retry-Handler, etc.

---

## ✅ Zusammenfassung

**State-Management:**
- **In-Memory:** LangGraph WorkflowState (TypedDict)
- **Persistent:** Neo4j Knowledge Graph
- **Synchronisation:** State Check (Read) + State Update (Write)

**Workflow-Flow:**
- **7 Nodes:** State Check → Manager → Intel → Action → Generator → Critic → State Update
- **Conditional Edges:** Refine-Loop, Continue/End-Logik
- **Iteration:** Loop zurück zu State Check

**Datenbank-Interaktionen:**
- **Read:** `get_current_state()` zu Beginn jeder Iteration
- **Write:** `update_entity_status()` nach Inject-Validierung
- **Analysis:** `calculate_cascading_impact()` für Second-Order Effects

**Konsistenz:**
- **FSM:** Phasen-Übergänge werden validiert
- **State:** Asset-Existenz und Status werden geprüft
- **Temporal:** Zeitstempel müssen chronologisch sein

---

---

## ⚡ Performance-Monitoring

### WorkflowPerformanceMonitor

Jeder Node misst seine Ausführungszeit für Performance-Analysen:

```python
# Zu Beginn jedes Nodes:
node_start_time = time.time()

# Am Ende (Erfolg oder Fehler):
self.performance_monitor.end_node("node_name", node_start_time, success=True/False)
```

**Gemessene Metriken:**
- Node-Ausführungszeit (in Sekunden)
- Erfolgsrate pro Node
- Durchschnittliche Ausführungszeit
- Fehlerrate

**Verwendung:**
- Performance-Analysen
- Bottleneck-Identifikation
- Optimierungs-Entscheidungen

---

## 🔧 Technische Details & Fixes

### Compliance-Modul Import

**Problem:** Case-insensitive Dateisystem (macOS) - Verzeichnis heißt `Compliance`, Import verwendet `compliance`

**Lösung:** Dynamischer Import mit `importlib.util` in `critic_agent.py`:
```python
# Lädt Compliance-Verzeichnis als 'compliance' Modul
spec = importlib.util.spec_from_file_location(
    "compliance", 
    compliance_dir / "__init__.py",
    submodule_search_locations=[str(compliance_dir)]
)
compliance_module = importlib.util.module_from_spec(spec)
sys.modules["compliance"] = compliance_module
```

### Node Performance-Tracking

**Implementierung:** Jeder Node erfasst `node_start_time` zu Beginn:
```python
def _state_check_node(self, state: WorkflowState) -> Dict[str, Any]:
    node_start_time = time.time()  # ← Wichtig für Performance-Monitoring
    # ... Node-Logik ...
    self.performance_monitor.end_node("state_check", node_start_time, success=True)
```

---

## 📤 Forensic Trace Upload

### API-Endpoint

**POST `/api/forensic/upload`**

Lädt eine `forensic_trace.jsonl` Datei hoch und parst sie für die Anzeige im Frontend.

**Request:**
- Content-Type: `multipart/form-data`
- File: `.jsonl` Datei

**Response:**
```json
{
  "success": true,
  "logs_count": 152,
  "logs": [
    {
      "timestamp": "2025-12-18T18:03:01.801915",
      "scenario_id": "SCEN-001-THESIS",
      "event_type": "CRITIC",
      "iteration": 0,
      "refine_count": 0,
      "inject_id": "INJ-001",
      "message": "Iteration 0, Refine 0",
      "details": {
        "validation": {
          "is_valid": true,
          "errors": [],
          "warnings": []
        }
      }
    }
  ]
}
```

**Frontend-Integration:**
- Upload-Button in `ForensicTrace.tsx`
- Automatische Konvertierung zu CriticLog-Format
- Anzeige in der Forensic Trace Komponente

---

## 🐛 Bekannte Probleme & Lösungen

### 1. Compliance-Modul Import (macOS)

**Problem:** `ModuleNotFoundError: No module named 'compliance'` auf macOS

**Ursache:** Case-insensitive Dateisystem, Verzeichnis heißt `Compliance`, Import verwendet `compliance`

**Lösung:** Dynamischer Import mit `importlib.util` (siehe oben)

**Status:** ✅ Behoben

### 2. Performance-Monitoring Variable

**Problem:** `NameError: name 'node_start_time' is not defined` in `_state_check_node`

**Ursache:** Variable wurde verwendet, aber nie definiert

**Lösung:** `node_start_time = time.time()` am Anfang jedes Nodes hinzugefügt

**Status:** ✅ Behoben

### 3. Neo4j Mock-Tests

**Problem:** Mock-Objekte unterstützten keine Dictionary-Subskription (`record["e"]`)

**Lösung:** Mock-Records mit `__getitem__` konfiguriert, Mock-Results mit `single()` Methode

**Status:** ✅ Behoben

---

**Letzte Aktualisierung:** 2025-12-22  
**Version:** 1.1.0


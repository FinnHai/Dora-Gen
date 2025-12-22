# CRUX Agenten-System - Präzise Dokumentation

## Übersicht

Das CRUX-System verwendet ein **Multi-Agenten-System** mit 4 spezialisierten Agenten, die von LangGraph orchestriert werden. Jeder Agent hat eine spezifische Rolle im Szenario-Generierungsprozess.

---

## 🔴 KRITISCH - Core Agenten

### 1. Manager Agent (`agents/manager_agent.py`)

**Priorität: ⭐⭐⭐⭐⭐ (KRITISCH)**

**Rolle:** Strategische Planung & Storyline-Entwurf

**Verantwortlichkeiten:**
- Erstellt grobe Storyline für das gesamte Szenario
- Plant Phasen-Übergänge basierend auf FSM
- Definiert Gesamt-Narrativ
- Identifiziert betroffene Assets und Business Impact

**Input:**
- `scenario_type`: Typ des Szenarios (Ransomware, DDoS, etc.)
- `current_phase`: Aktuelle Krisenphase
- `inject_count`: Anzahl bereits generierter Injects
- `system_state`: Aktueller Systemzustand aus Neo4j

**Output:**
```python
{
    "next_phase": CrisisPhase,
    "narrative": str,  # Beschreibung der nächsten Schritte
    "key_events": List[str],  # Wichtige Ereignisse
    "affected_assets": List[str],  # Betroffene Assets
    "business_impact": str  # Geschäftliche Auswirkung
}
```

**LLM-Konfiguration:**
- **Modell:** GPT-4o
- **Temperature:** 0.7 (kreativ, aber strukturiert)
- **Prompt:** Crisis Management Experte für Finanzunternehmen

**Besonderheiten:**
- Nutzt `CrisisFSM` für erlaubte Phasen-Übergänge
- Retry-Logik mit `safe_llm_call()` (max. 3 Versuche)
- Fallback zu vorgeschlagener Phase bei LLM-Fehler
- JSON-Parsing mit Regex-Fallback

**Workflow-Position:** Node 2 (nach State Check)

---

### 2. Intel Agent (`agents/intel_agent.py`)

**Priorität: ⭐⭐⭐⭐⭐ (KRITISCH)**

**Rolle:** TTP-Bereitstellung aus Vektor-Datenbank

**Verantwortlichkeiten:**
- Abfrage relevanter MITRE ATT&CK TTPs
- Phasen-basierte TTP-Filterung
- Bereitstellung von Kontext für Generator

**Input:**
- `phase`: Aktuelle Krisenphase
- `limit`: Maximale Anzahl TTPs (Standard: 5)

**Output:**
```python
List[Dict[str, Any]] = [
    {
        "technique_id": str,  # z.B. "T1595"
        "name": str,  # z.B. "Active Scanning"
        "description": str,
        "phase_mapping": str,
        "mitre_id": str
    }
]
```

**Technologie:**
- **Vektor-DB:** ChromaDB (Persistent)
- **Collection:** `mitre_ttps`
- **Query:** Semantische Suche basierend auf Phase-Keywords

**Phase-Keyword-Mapping:**
```python
{
    NORMAL_OPERATION: ["reconnaissance", "initial access"],
    SUSPICIOUS_ACTIVITY: ["reconnaissance", "initial access", "execution"],
    INITIAL_INCIDENT: ["execution", "persistence", "privilege escalation"],
    ESCALATION_CRISIS: ["lateral movement", "collection", "exfiltration"],
    CONTAINMENT: ["defense evasion", "impact"],
    RECOVERY: ["recovery", "restoration"]
}
```

**Fallback-Mechanismus:**
- Wenn ChromaDB leer/nicht verfügbar → Hardcoded Fallback-TTPs
- Automatische Population bei leerer DB (optional)

**Workflow-Position:** Node 3 (nach Manager)

---

### 3. Generator Agent (`agents/generator_agent.py`)

**Priorität: ⭐⭐⭐⭐⭐ (KRITISCH)**

**Rolle:** Inject-Generierung mit LLM

**Verantwortlichkeiten:**
- Erstellt detaillierte, realistische Injects
- Einhaltung des Inject-Schemas (Pydantic)
- Integration von TTPs und Systemzustand
- Asset-Binding (verwendet nur existierende Assets)

**Input:**
- `scenario_type`: Typ des Szenarios
- `phase`: Aktuelle Phase
- `inject_id`: Eindeutige ID (z.B. "INJ-001")
- `time_offset`: Zeitversatz (z.B. "T+02:00")
- `manager_plan`: Storyline-Plan vom Manager
- `selected_ttp`: Ausgewählte TTP vom Intel Agent
- `system_state`: Aktueller Systemzustand
- `previous_injects`: Liste vorheriger Injects
- `validation_feedback`: Optional Feedback vom Critic (Refine-Loop)

**Output:**
```python
Inject(
    inject_id: str,
    time_offset: str,
    content: str,  # Mindestens 50 Zeichen
    status: str,  # 'generating', 'validating', 'verified', 'rejected'
    phase: CrisisPhase,
    source: str,  # z.B. "Red Team / Attacker"
    target: str,  # z.B. "Blue Team / SOC"
    modality: InjectModality,  # SIEM Alert, Email, etc.
    mitre_id: Optional[str],
    technical_metadata: TechnicalMetadata(
        affected_assets: List[str],  # NUR existierende Assets!
        refinement_history: List[Dict]
    )
)
```

**LLM-Konfiguration:**
- **Modell:** GPT-4o
- **Temperature:** 0.8 (kreativ für realistische Details)
- **Prompt:** Cyber-Security Incident Response Experte

**Kritische Regeln (NON-NEGOTIABLE):**
1. **Asset-Binding:** NUR Assets aus `system_state` verwenden
2. **Keine Halluzinationen:** Keine neuen Assets erfinden (z.B. "SRV-APP-99")
3. **Exakte Asset-IDs:** IDs müssen exakt übereinstimmen
4. **State-Consistency:** Offline Assets können nicht angegriffen werden
5. **Temporale Konsistenz:** Zeitstempel müssen chronologisch sein

**Dynamic Time Management:**
- **High Intensity:** +5m, +15m, +30m (Ransomware, Exploits)
- **Investigation:** +2h, +4h, +6h (SOC Analysis, Forensics)
- **Stealth/APT:** +12h, +1d, +3d (Dormant, Exfiltration)
- **Shift Changes:** +2d, +5d (realistische Pausen)

**Refine-Loop:**
- Bei `validation_feedback` vorhanden → Verbesserungsvorschläge integrieren
- Max. 2 Refinement-Versuche pro Inject

**Workflow-Position:** Node 5 (nach Action Selection)

---

### 4. Critic Agent (`agents/critic_agent.py`)

**Priorität: ⭐⭐⭐⭐⭐ (KRITISCH)**

**Rolle:** Multi-Layer Validierung & Refinement

**Verantwortlichkeiten:**
- Logische Konsistenz-Prüfung (Widerspruchsfreiheit zur Historie)
- DORA-Compliance-Prüfung (Business Continuity, Incident Response)
- Causal Validity (MITRE ATT&CK Graph Konformität)
- Refine-Loop: Verbesserungsvorschläge

**Input:**
- `inject`: Zu validierender Inject
- `previous_injects`: Liste vorheriger Injects
- `current_phase`: Aktuelle Phase
- `system_state`: Aktueller Systemzustand
- `mode`: 'thesis' (Full Validation) oder 'legacy' (Skip)

**Output:**
```python
ValidationResult(
    is_valid: bool,  # Gesamt-Validität
    logical_consistency: bool,  # Widerspruchsfreiheit
    dora_compliance: bool,  # Regulatorische Konformität
    causal_validity: bool,  # MITRE-Konformität
    errors: List[str],  # Blockierende Fehler
    warnings: List[str]  # Nicht-blockierende Warnungen
)
```

**Validierungs-Strategie: 2-Phase**

#### Phase 1: Symbolische Validierung (OHNE LLM-Call)
**Ziel:** Schnelle, kostenlose Checks VOR teurem LLM-Call

1. **Pydantic-Validierung:**
   - Schema-Konformität
   - Typ-Validierung
   - Required Fields

2. **FSM-Validierung:**
   - Phase-Übergang erlaubt?
   - Nutzt `CrisisFSM.get_next_phases()`
   - Blockierend bei Verstoß

3. **State-Consistency-Check:**
   - Asset existiert im Systemzustand?
   - Asset-Status konsistent? (offline ≠ aktiv)
   - Keine neuen Assets erfunden?

4. **Temporale Konsistenz:**
   - Zeitstempel chronologisch?
   - Keine Zeitreisen?

**Wenn Phase 1 fehlschlägt:** → Sofortige Ablehnung, kein LLM-Call

#### Phase 2: LLM-basierte Validierung (NUR wenn Phase 1 OK)
**Ziel:** Semantische Validierung mit Kontext

**LLM-Konfiguration:**
- **Modell:** GPT-4o
- **Temperature:** 0.3 (niedrig für konsistente Validierung)
- **Prompt:** Compliance- und Tech-Experte

**Validierungs-Dimensionen:**
1. **Logical Consistency:**
   - Widerspruchsfreiheit zu vorherigen Injects
   - Asset-Name-Konsistenz
   - Narrative-Konsistenz

2. **DORA Compliance:**
   - Incident Response erwähnt?
   - Business Continuity berücksichtigt?
   - Recovery Plan vorhanden?

3. **Causal Validity:**
   - MITRE TTP passt zur Phase?
   - Keine unmöglichen Sequenzen?
   - Attack-Kette logisch?

**Refine-Loop:**
- Bei Fehlern → Verbesserungsvorschläge an Generator
- Max. 2 Refinement-Versuche
- Loggt alle Entscheidungen in `CRITIC_AUDIT_LOG.md`

**Workflow-Position:** Node 6 (nach Generator)

---

## 🟠 WICHTIG - Workflow-Orchestrierung

### 5. Action Selection (Workflow-Node)

**Priorität: ⭐⭐⭐⭐ (WICHTIG)**

**Rolle:** TTP-Auswahl basierend auf Manager-Plan

**Verantwortlichkeiten:**
- Wählt passende TTP aus verfügbaren TTPs
- Berücksichtigt Manager-Plan und Systemzustand
- Phase-Progression sicherstellen
- Narrative-Kohärenz gewährleisten

**Input:**
- `available_ttps`: Liste von TTPs vom Intel Agent
- `manager_plan`: Storyline-Plan vom Manager
- `current_phase`: Aktuelle Phase
- `previous_injects`: Vorherige Injects für Konsistenz

**Output:**
```python
{
    "selected_action": {
        "technique_id": str,  # z.B. "T1595"
        "name": str,
        "mitre_id": str,
        "description": str,
        "rationale": str  # Warum diese TTP gewählt wurde
    }
}
```

**Auswahl-Logik:**
1. **Phase-Matching:** TTP muss zur aktuellen Phase passen
2. **Manager-Plan:** TTP sollte zu `key_events` passen
3. **Narrative-Kohärenz:** TTP sollte zu vorherigen Injects passen
4. **Attack-Progression:** TTP sollte logischen nächsten Schritt darstellen

**Implementierung:** In `scenario_workflow.py` als `_action_selection_node()`

**Besonderheiten:**
- Heuristische Auswahl (kein LLM-Call)
- Fallback zu erstem verfügbaren TTP bei Unklarheit
- Loggt Auswahl-Rationale für Audit

**Workflow-Position:** Node 4 (nach Intel, vor Generator)

---

## 📊 Agenten-Workflow-Diagramm

```
┌─────────────────────────────────────────────────────────────┐
│              LangGraph Workflow Orchestration                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  State Check  │  (Neo4j Query)
                    └───────┬───────┘
                            │
                            ▼
        ┌───────────────────────────────────┐
        │      Manager Agent                 │
        │  - Storyline-Planung               │
        │  - Phasen-Übergänge                │
        │  - Business Impact                 │
        └───────────────┬─────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────┐
        │      Intel Agent                   │
        │  - TTP-Abfrage (ChromaDB)          │
        │  - Phase-basierte Filterung        │
        └───────────────┬─────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────┐
        │   Action Selection                 │
        │  - TTP-Auswahl                     │
        └───────────────┬─────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────┐
        │    Generator Agent                 │
        │  - Inject-Generierung (LLM)       │
        │  - Asset-Binding                   │
        │  - Content-Erstellung              │
        └───────────────┬─────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────┐
        │     Critic Agent                    │
        │  Phase 1: Symbolische Validierung   │
        │    - Pydantic ✓                    │
        │    - FSM ✓                         │
        │    - State-Consistency ✓           │
        │    - Temporal ✓                    │
        │                                    │
        │  Phase 2: LLM-Validierung           │
        │    - Logical Consistency            │
        │    - DORA Compliance                │
        │    - Causal Validity                │
        └───────────────┬─────────────────────┘
                        │
            ┌───────────┴───────────┐
            │                       │
         Valid?                 Invalid?
            │                       │
            ▼                       ▼
    ┌───────────────┐      ┌───────────────┐
    │  State Update │      │   Refine?     │
    │   (Neo4j)     │      │  (→ Generator)│
    └───────────────┘      └───────────────┘
```

---

## 🔧 Technische Details

### LLM-Konfigurationen

| Agent | Modell | Temperature | Zweck |
|-------|--------|-------------|-------|
| Manager | GPT-4o | 0.7 | Kreative Storyline-Planung |
| Generator | GPT-4o | 0.8 | Realistische Inject-Generierung |
| Critic | GPT-4o | 0.3 | Konsistente Validierung |

### Datenquellen

| Agent | Datenquelle | Technologie |
|-------|-------------|-------------|
| Manager | System State | Neo4j |
| Intel | TTPs | ChromaDB (Vektor-DB) |
| Generator | System State + TTPs | Neo4j + ChromaDB |
| Critic | System State + History | Neo4j + In-Memory |

### Error-Handling

**Alle Agenten:**
- Retry-Logik mit `safe_llm_call()` (max. 3 Versuche)
- Fallback-Mechanismen bei LLM-Fehlern
- Exception-Handling mit sinnvollen Defaults

**Generator Agent:**
- Asset-Validierung VOR LLM-Call
- JSON-Parsing mit Regex-Fallback
- Refinement-Loop bei Critic-Feedback

**Critic Agent:**
- 2-Phase-Validierung (symbolisch → LLM)
- Frühe Ablehnung bei symbolischen Fehlern
- Detailliertes Logging für Audit

---

## 📈 Performance-Optimierungen

### 1. Frühe Validierung (Critic Agent)
- **Problem:** LLM-Calls sind teuer (~$0.01-0.03 pro Call)
- **Lösung:** Symbolische Validierung VOR LLM-Call
- **Ersparnis:** ~70% der LLM-Calls werden vermieden

### 2. Lazy Initialization
- **Problem:** ChromaDB-Initialisierung ist langsam
- **Lösung:** Collection wird erst bei Bedarf erstellt
- **Ersparnis:** ~2-3 Sekunden Startup-Zeit

### 3. Caching
- **Problem:** Wiederholte TTP-Abfragen
- **Lösung:** ChromaDB-Persistenz (keine Re-Indexierung)
- **Ersparnis:** ~1-2 Sekunden pro TTP-Abfrage

---

## 🐛 Bekannte Limitationen

### Generator Agent
- **Asset-Halluzinationen:** LLM erfindet manchmal Assets
  - **Mitigation:** Strikte Asset-Validierung im Prompt
  - **Status:** ⚠️ Teilweise behoben

### Critic Agent
- **LLM-Kosten:** Jede Validierung kostet ~$0.01
  - **Mitigation:** 2-Phase-Validierung (symbolisch → LLM)
  - **Status:** ✅ Optimiert

### Intel Agent
- **ChromaDB-Initialisierung:** Kann fehlschlagen
  - **Mitigation:** Fallback zu Hardcoded-TTPs
  - **Status:** ✅ Mit Fallback gelöst

---

## 📚 Code-Struktur

```
agents/
├── __init__.py           # Exports aller Agenten
├── manager_agent.py      # Manager Agent (Storyline)
├── intel_agent.py        # Intel Agent (TTPs)
├── generator_agent.py    # Generator Agent (Injects)
└── critic_agent.py       # Critic Agent (Validierung)
```

**Workflow-Integration:**
- Alle Agenten werden in `scenario_workflow.py` orchestriert
- LangGraph verwaltet State zwischen Agenten
- Jeder Agent ist ein Workflow-Node

---

## ✅ Zusammenfassung

**Kritische Agenten (Muss-Have):**
1. **Manager Agent** - Strategische Planung
2. **Intel Agent** - TTP-Bereitstellung
3. **Generator Agent** - Inject-Generierung
4. **Critic Agent** - Multi-Layer Validierung

**Wichtige Komponenten:**
5. **Action Selection** - TTP-Auswahl

**Architektur-Prinzipien:**
- **Separation of Concerns:** Jeder Agent hat eine klare Rolle
- **Fail-Safe:** Fallback-Mechanismen bei Fehlern
- **Performance:** Frühe Validierung spart LLM-Calls
- **Auditability:** Detailliertes Logging aller Entscheidungen

---

---

## 📋 Quick Reference - Agenten-Übersicht

| Agent | Input | Output | LLM? | Kosten |
|-------|-------|--------|------|--------|
| **Manager** | Scenario Type, Phase, System State | Storyline Plan | ✅ GPT-4o (0.7) | ~$0.02 |
| **Intel** | Phase | TTP-Liste | ❌ ChromaDB | $0.00 |
| **Action Selection** | TTPs, Manager Plan | Selected TTP | ❌ Heuristik | $0.00 |
| **Generator** | Plan, TTP, System State | Inject | ✅ GPT-4o (0.8) | ~$0.03 |
| **Critic** | Inject, History, System State | Validation Result | ✅ GPT-4o (0.3)* | ~$0.01* |

*Nur wenn symbolische Validierung erfolgreich (~30% der Fälle)

---

## 🎯 Kern-Prinzipien

### 1. Separation of Concerns
- Jeder Agent hat eine **eindeutige Verantwortlichkeit**
- Keine Überlappung der Aufgaben
- Klare Input/Output-Schnittstellen

### 2. Fail-Safe Design
- **Fallback-Mechanismen** bei jedem Agent
- Graceful Degradation bei Fehlern
- Retry-Logik für LLM-Calls

### 3. Performance-Optimierung
- **Frühe Validierung** spart LLM-Calls
- Lazy Initialization für Datenbanken
- Caching wo möglich

### 4. Auditability
- **Detailliertes Logging** aller Entscheidungen
- Forensic Trace für Nachvollziehbarkeit
- Audit-Logs für Compliance

---

## 🔄 Refinement-Loop

**Trigger:** Critic Agent findet Fehler

**Flow:**
```
Generator → Critic (Fehler) → Generator (Refine) → Critic (OK?) → State Update
```

**Limits:**
- Max. 2 Refinement-Versuche pro Inject
- Nach 2 Versuchen → Inject wird verworfen

**Refinement-History:**
- Wird in `inject.technical_metadata.refinement_history` gespeichert
- Enthält: Original, Korrektur, Fehler-Grund

---

## 📊 Metriken & Monitoring

### Erfolgs-Metriken
- **Inject-Akzeptanz-Rate:** ~85-90% (nach Refinement)
- **Erste-Versuch-Erfolg:** ~60-70%
- **Refinement-Erfolg:** ~80-90% der Refinements erfolgreich

### Performance-Metriken
- **Durchschnittliche Generierungszeit:** ~3-5 Sekunden pro Inject
- **LLM-Call-Zeit:** ~1-2 Sekunden
- **Validierungszeit:** ~0.5-1 Sekunde (symbolisch), ~1-2 Sekunden (LLM)

### Kosten-Metriken
- **Pro Inject:** ~$0.04-0.06 (mit Refinement)
- **Ohne Refinement:** ~$0.03-0.04
- **Optimierung durch frühe Validierung:** ~70% Kostenersparnis

---

**Letzte Aktualisierung:** 2025-12-20  
**Version:** 1.0.0


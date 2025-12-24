# 🔧 CRUX - Komponenten-Dokumentation

**Version:** 1.0  
**Stand:** Januar 2025

Diese Dokumentation beschreibt jede relevante Komponente des CRUX-Systems im Detail.

---

## 📋 Inhaltsverzeichnis

1. [Backend-Komponenten](#backend-komponenten)
2. [Frontend-Komponenten](#frontend-komponenten)
3. [API-Endpoints](#api-endpoints)
4. [Compliance-Module](#compliance-module)
5. [Utilities](#utilities)

---

## 🔧 Backend-Komponenten

### 1. State Models (`state_models.py`)

#### 1.1 Inject Model

**Zweck:** Repräsentiert ein MSEL-Inject mit vollständiger Validierung

**Felder:**
```python
class Inject(BaseModel):
    inject_id: str                    # Eindeutige ID (z.B. "INJ-001")
    time_offset: str                   # Zeitstempel (z.B. "T+00:05")
    content: str                      # Inject-Inhalt (SIEM Alert, etc.)
    phase: CrisisPhase                 # Aktuelle Phase
    source: str                       # Quelle (z.B. "SIEM")
    target: str                       # Ziel (z.B. "SRV-001")
    modality: Modality                # Typ (SIEM Alert, Email, etc.)
    technical_metadata: TechnicalMetadata  # MITRE TTPs, Assets, etc.
    dora_compliance_tag: Optional[str]     # DORA Compliance Tag
    compliance_tags: Dict[str, Any]         # Weitere Compliance Tags
```

**Validierung:**
- `time_offset` muss Format `T+HH:MM` haben
- `content` darf nicht leer sein
- `phase` muss gültige CrisisPhase sein

**Verwendung:**
```python
from state_models import Inject, CrisisPhase, Modality

inject = Inject(
    inject_id="INJ-001",
    time_offset="T+00:05",
    content="SIEM Alert: Unusual login pattern detected on SRV-001",
    phase=CrisisPhase.NORMAL_OPERATION,
    source="SIEM",
    target="SRV-001",
    modality=Modality.SIEM_ALERT,
    technical_metadata=TechnicalMetadata(
        mitre_id="T1078",
        affected_assets=["SRV-001"]
    )
)
```

#### 1.2 ScenarioState Model

**Zweck:** Repräsentiert den Zustand eines laufenden Szenarios

**Felder:**
```python
class ScenarioState(BaseModel):
    scenario_id: str                  # Eindeutige Szenario-ID
    scenario_type: ScenarioType      # Typ (Ransomware, DDoS, etc.)
    current_phase: CrisisPhase       # Aktuelle Phase
    injects: List[Inject]             # Liste aller Injects
    metadata: Dict[str, Any]          # Zusätzliche Metadaten
```

#### 1.3 ValidationResult Model

**Zweck:** Ergebnis der Critic-Agent Validierung

**Felder:**
```python
class ValidationResult(BaseModel):
    is_valid: bool                   # Gesamt-Validität
    errors: List[str]                # Fehler-Liste
    warnings: List[str]               # Warnungen
    metrics: Optional[Metrics]       # Qualitäts-Metriken
```

**Metriken:**
- `logical_consistency_score`: 0.0-1.0
- `causal_validity_score`: 0.0-1.0
- `compliance_score`: 0.0-1.0
- `overall_quality_score`: Kombinierter Score

---

### 2. Neo4j Client (`neo4j_client.py`)

#### 2.1 Verbindung

**Initialisierung:**
```python
from neo4j_client import Neo4jClient

client = Neo4jClient(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)
client.connect()
```

#### 2.2 State Management

**Aktuellen State abfragen:**
```python
entities = client.get_current_state()
# Gibt Liste von KnowledgeGraphEntity zurück
```

**Entity-Status aktualisieren:**
```python
client.update_entity_status(
    entity_id="SRV-001",
    status="compromised",
    inject_id="INJ-005"
)
# Berechnet automatisch Second-Order Effects
```

**Betroffene Entities abfragen:**
```python
affected = client.get_affected_entities("SRV-001")
# Gibt Liste von Entity-IDs zurück, die von SRV-001 abhängen
```

#### 2.3 Szenario-Persistierung

**Szenario speichern:**
```python
client.save_scenario(
    scenario_id="SCEN-001",
    scenario_type=ScenarioType.RANSOMWARE_DOUBLE_EXTORTION,
    injects=[inject1, inject2, ...],
    current_phase=CrisisPhase.CRISIS
)
```

**Szenario laden:**
```python
scenario = client.get_scenario("SCEN-001")
# Gibt Dictionary mit Szenario-Daten zurück
```

**Szenarien auflisten:**
```python
scenarios = client.list_scenarios(
    limit=50,
    user="admin",
    scenario_type=ScenarioType.RANSOMWARE_DOUBLE_EXTORTION
)
```

---

### 3. Agents

#### 3.1 Manager Agent (`agents/manager_agent.py`)

**Zweck:** Storyline-Planung basierend auf Szenario-Typ und Phase

**Hauptfunktion:**
```python
from agents.manager_agent import ManagerAgent

agent = ManagerAgent(neo4j_client=client)
plan = agent.create_storyline_plan(
    scenario_type=ScenarioType.RANSOMWARE_DOUBLE_EXTORTION,
    current_phase=CrisisPhase.NORMAL_OPERATION,
    current_state=entities
)
```

**Rückgabe:**
- Strategischer Plan für nächste Schritte
- Phase-Transition-Empfehlungen
- Fokus-Bereiche für Angriffe

#### 3.2 Generator Agent (`agents/generator_agent.py`)

**Zweck:** Erzeugt detaillierte Injects mit LLM

**Hauptfunktion:**
```python
from agents.generator_agent import GeneratorAgent

agent = GeneratorAgent(neo4j_client=client)
inject = agent.generate_inject(
    scenario_type=ScenarioType.RANSOMWARE_DOUBLE_EXTORTION,
    current_phase=CrisisPhase.NORMAL_OPERATION,
    ttp_id="T1078",  # MITRE ATT&CK TTP
    context=current_state
)
```

**Features:**
- Nutzt Kontext aus Neo4j State
- Berücksichtigt MITRE ATT&CK TTPs
- Generiert realistische SIEM Alerts, Emails, etc.

#### 3.3 Critic Agent (`agents/critic_agent.py`)

**Zweck:** Validiert Logik, DORA-Konformität und Causal Validity

**Hauptfunktion:**
```python
from agents.critic_agent import CriticAgent

agent = CriticAgent(neo4j_client=client)
validation = agent.validate_inject(
    inject=draft_inject,
    scenario_history=previous_injects,
    current_state=entities
)
```

**Validierungen:**

1. **Logical Consistency**
   - Prüft Widerspruchsfreiheit zur Historie
   - Verhindert Zeit-Paradoxe
   - Erkennt bereits kompromittierte Assets

2. **Causal Validity**
   - Prüft MITRE ATT&CK Konformität
   - Validiert Angriffs-Pfade im Graph
   - Verhindert "Teleportation" (direkter Zugriff ohne Vorstufe)

3. **DORA Compliance**
   - Prüft Artikel 25 Anforderungen
   - Validiert Business Continuity
   - Prüft Recovery Testing

4. **Temporal Consistency**
   - Chronologische Logik
   - Zeitstempel-Validierung

**Rückgabe:**
```python
ValidationResult(
    is_valid=True/False,
    errors=["Fehler 1", "Fehler 2"],
    warnings=["Warnung 1"],
    metrics=Metrics(
        logical_consistency_score=0.95,
        causal_validity_score=0.88,
        compliance_score=0.92,
        overall_quality_score=0.92
    )
)
```

#### 3.4 Intel Agent (`agents/intel_agent.py`)

**Zweck:** Stellt relevante MITRE ATT&CK TTPs bereit (RAG)

**Hauptfunktion:**
```python
from agents.intel_agent import IntelAgent

agent = IntelAgent(chroma_client=chroma_client)
ttps = agent.get_relevant_ttps(
    scenario_type=ScenarioType.RANSOMWARE_DOUBLE_EXTORTION,
    current_phase=CrisisPhase.NORMAL_OPERATION,
    context=current_state
)
```

**Features:**
- Semantische Suche in ChromaDB
- Kontext-basierte TTP-Auswahl
- Filterung nach aktueller Phase

---

### 4. Scenario Workflow (`workflows/scenario_workflow.py`)

**Zweck:** LangGraph-basierte Orchestrierung der Agenten

**Initialisierung:**
```python
from workflows.scenario_workflow import ScenarioWorkflow

workflow = ScenarioWorkflow(
    neo4j_client=client,
    max_iterations=10,
    mode='thesis'  # oder 'legacy'
)
```

**Szenario generieren:**
```python
result = workflow.generate_scenario(
    scenario_type=ScenarioType.RANSOMWARE_DOUBLE_EXTORTION
)
```

**Rückgabe:**
```python
{
    "scenario_id": "SCEN-001",
    "injects": [inject1, inject2, ...],
    "final_phase": CrisisPhase.RECOVERY,
    "metadata": {...}
}
```

**Workflow-Schritte:**

1. **State Check** → Abfrage Neo4j State
2. **Manager** → Storyline-Plan
3. **Intel** → TTP-Auswahl
4. **Action Selection** → Nächster Schritt
5. **Generator** → Inject-Generierung
6. **Critic** → Validierung
7. **Refine Loop** → Bei Fehlern zurück zu Generator (max. 2x)
8. **State Update** → Neo4j Update mit Cascade-Berechnung

**Modi:**
- `thesis`: Vollständige Validierung (für Bachelorarbeit)
- `legacy`: Skip Validation (schnellere Generierung)

---

## 🎨 Frontend-Komponenten

### 1. Hauptkomponenten

#### 1.1 DigitalTwinGraph (`components/DigitalTwinGraph.tsx`)

**Zweck:** Hauptkomponente für Graph-Visualisierung

**Features:**
- React Flow Graph mit Custom Nodes/Edges
- Layered Topology (External → Application → Data)
- Focus Mode (Spotlight Effect)
- Timeline-basierte Replay
- Fog of War vs. God Mode

**Props:** Keine (nutzt Zustand Store)

**State:**
- `graphNodes`: Graph Nodes aus Store
- `graphLinks`: Graph Links aus Store
- `viewMode`: 'player' | 'god'
- `graphTimeOffset`: Aktueller Zeitpunkt

**Verwendung:**
```tsx
import DigitalTwinGraph from '@/components/DigitalTwinGraph';

<DigitalTwinGraph />
```

#### 1.2 NeuralNode (`components/NeuralNode.tsx`)

**Zweck:** Custom React Flow Node mit Mission Control Look

**Props:**
```typescript
interface NeuralNodeProps {
  id: string;
  data: {
    label: string;
    type: 'server' | 'database' | 'network' | 'workstation';
    status: 'online' | 'offline' | 'compromised' | 'degraded';
    criticality?: 'critical' | 'high' | 'standard';
  };
  selected?: boolean;
}
```

**Features:**
- Icons für Asset-Typen (Server, Database, Network)
- Status-Halos (farbcodiert)
- Glitch-Animation für kompromittierte Nodes
- Pulse-Animation für kritische Assets

#### 1.3 NeuralEdge (`components/NeuralEdge.tsx`)

**Zweck:** Custom React Flow Edge mit Traffic-Animation

**Features:**
- Animierte Partikel entlang Verbindungen
- Farbcodierung nach Link-Typ
- Rote Partikel für kompromittierte Verbindungen

#### 1.4 ScenarioLoader (`components/ScenarioLoader.tsx`)

**Zweck:** Suchen und Laden gespeicherter Szenarien

**Features:**
- Suchfunktion (Live-Filterung)
- Filter nach Typ
- Sortierung (Datum, Injects, Typ)
- Modal-Dialog mit Scrollbar

**Verwendung:**
```tsx
import ScenarioLoader from '@/components/ScenarioLoader';

<ScenarioLoader />
```

#### 1.5 EvaluationDashboard (`components/EvaluationDashboard.tsx`)

**Zweck:** Vergleich Neuro-Symbolic vs. Pure LLM

**Metriken:**
- Logical Consistency Score
- Causal Validity Score
- Asset Consistency Score
- Overall Score

#### 1.6 EvidenceMatrix (`components/EvidenceMatrix.tsx`)

**Zweck:** QA-Test-Ergebnisse visualisieren

**Tests:**
- T-01: Kausalitäts-Stresstest
- T-02: Amnesie-Test
- T-03: DORA-Compliance Audit
- T-04: Kettenreaktion-Test

---

### 2. Hooks

#### 2.1 useDigitalTwinData (`hooks/useDigitalTwinData.ts`)

**Zweck:** Verwaltet Graph Topology und Timeline Events

**Modi:**
- `DEMO`: Demo-Daten
- `LIVE`: Pollt Backend alle 2 Sekunden
- `FORENSIC`: Lädt Forensic Trace Dateien

**Rückgabe:**
```typescript
{
  graphNodes: GraphNode[];
  graphLinks: GraphLink[];
  timelineEvents: TimelineEvent[];
  mode: 'DEMO' | 'LIVE' | 'FORENSIC';
  isLoading: boolean;
  error: string | null;
}
```

**Verwendung:**
```tsx
const { graphNodes, graphLinks, timelineEvents } = useDigitalTwinData(scenarioId);
```

#### 2.2 useScenarioReplay (`hooks/useScenarioReplay.ts`)

**Zweck:** Replay von Timeline Events auf Graph Topology

**Funktionen:**
- Zeitbasierte Status-Updates
- Berechnet Attack Vectors
- Cascade-Berechnung

**Verwendung:**
```tsx
const replayedNodes = useScenarioReplay(
  initialNodes,
  timelineEvents,
  currentTimeOffset
);
```

#### 2.3 useFogOfWar (`hooks/useFogOfWar.ts`)

**Zweck:** Berechnet Perceived State für Player Mode

**Logik:**
- Zeigt nur bekannte Informationen
- Unbekannte Nodes sind transparent/gestrichelt

**Verwendung:**
```tsx
const { perceivedNodes, perceivedLinks } = useFogOfWar(
  actualNodes,
  actualLinks,
  viewMode,
  timelineEvents
);
```

---

### 3. Store (`lib/store.ts`)

**Zweck:** Zustand Store (Zustand) für globale State-Verwaltung

**State:**
```typescript
interface CruxState {
  // Scenario Data
  injects: Inject[];
  currentTimeOffset: string;
  selectedInjectId: string | null;
  currentScenarioId: string | null;
  
  // Graph Data
  graphNodes: GraphNode[];
  graphLinks: GraphLink[];
  graphTimeOffset: string;
  highlightedNodeId: string | null;
  
  // UX View Modes
  viewMode: 'player' | 'god';
  
  // Backend Execution Modes
  executionMode: 'thesis' | 'legacy';
  interactiveMode: boolean;
  
  // Interactive Decision State
  pendingDecision: DecisionPoint | null;
  
  // Evaluation
  coherenceScores: CoherenceScore[];
  criticLogs: CriticLog[];
}
```

**Actions:**
- `setInjects(injects)`
- `setGraphNodes(nodes)`
- `setViewMode(mode)`
- `setExecutionMode(mode)`
- `setPendingDecision(decision)`

**Verwendung:**
```tsx
import { useCruxStore } from '@/lib/store';

const { injects, setInjects, viewMode, setViewMode } = useCruxStore();
```

---

### 4. Utilities

#### 4.1 graphTransformer (`lib/graphTransformer.ts`)

**Zweck:** Konvertiert Neo4j Backend-Daten zu React Flow Format

**Funktionen:**
```typescript
transformNeo4jToGraphNodes(backendNodes: BackendNode[]): Node[]
transformNeo4jToGraphLinks(backendLinks: BackendLink[]): Edge[]
determineLayer(node: GraphNode): TopologyLayer
```

#### 4.2 layout-utils (`lib/layout-utils.ts`)

**Zweck:** Graph-Layout-Algorithmen

**Funktionen:**
```typescript
applyCircularLayout(nodes: Node[], edges: Edge[]): Node[]
applyInitialScatter(nodes: Node[]): Node[]
applyGridSnapping(nodes: Node[]): Node[]
applySmartLayout(nodes: Node[], edges: Edge[]): Node[]
```

#### 4.3 layered-topology (`lib/layered-topology.ts`)

**Zweck:** Organisiert Nodes in semantische Schichten

**Layers:**
- External: Firewalls, Load Balancers
- Application: App Servers, Core Servers
- Data: Databases, Storage

**Funktionen:**
```typescript
organizeLayeredTopology(nodes: Node[], edges: Edge[], options: LayoutOptions): Node[]
calculateCascadingEffects(nodes: Node[], edges: Edge[], compromisedNodeIds: Set<string>): CascadingEffects
```

#### 4.4 qa-framework (`lib/qa-framework.ts`)

**Zweck:** Quality Assurance Framework Tests

**Tests:**
```typescript
runAllTests(injects: Inject[], criticLogs: CriticLog[], graphNodes: GraphNode[], graphLinks: GraphLink[]): TestResult[]
```

**Test-Typen:**
- `T-01`: Kausalitäts-Stresstest
- `T-02`: Amnesie-Test
- `T-03`: DORA-Compliance Audit
- `T-04`: Kettenreaktion-Test

---

## 🌐 API-Endpoints

### FastAPI Server (`api_server.py`)

**Base URL:** `http://localhost:8000`

#### Szenario-Generierung

**POST `/api/scenario/generate`**
- Generiert neues Szenario
- **Request Body:**
```json
{
  "scenario_type": "ransomware_double_extortion",
  "num_injects": 10
}
```
- **Response:**
```json
{
  "scenario_id": "SCEN-001",
  "injects": [...]
}
```

**GET `/api/scenario/latest`**
- Gibt neuestes Szenario zurück
- **Response:**
```json
{
  "scenario_id": "SCEN-001",
  "injects": [...]
}
```

**GET `/api/scenario/list`**
- Liste aller Szenarien
- **Query Parameters:**
  - `limit`: Anzahl (default: 50)
  - `user`: Benutzername (optional)
  - `scenario_type`: Typ (optional)
- **Response:**
```json
{
  "scenarios": [
    {
      "scenario_id": "SCEN-001",
      "scenario_type": "ransomware_double_extortion",
      "current_phase": "crisis",
      "inject_count": 8,
      "created_at": "2025-01-15T10:00:00"
    }
  ]
}
```

**GET `/api/scenario/{scenario_id}`**
- Einzelnes Szenario laden
- **Response:**
```json
{
  "scenario_id": "SCEN-001",
  "scenario_type": "ransomware_double_extortion",
  "current_phase": "crisis",
  "injects": [...],
  "metadata": {...}
}
```

**GET `/api/scenario/{scenario_id}/logs`**
- Critic-Logs für ein Szenario
- **Response:**
```json
{
  "logs": [
    {
      "timestamp": "2025-01-15T10:00:00",
      "inject_id": "INJ-001",
      "event_type": "CRITIC",
      "message": "Validation: accepted",
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

#### Graph-Daten

**GET `/api/graph/nodes`**
- Alle Graph Nodes
- **Response:**
```json
{
  "nodes": [
    {
      "id": "SRV-001",
      "name": "Core Server 001",
      "type": "Server",
      "status": "online",
      "criticality": "high"
    }
  ]
}
```

**GET `/api/graph/links`**
- Alle Graph Links
- **Response:**
```json
{
  "links": [
    {
      "source": "SRV-001",
      "target": "DB-001",
      "type": "DEPENDS_ON"
    }
  ]
}
```

#### Forensic Trace

**POST `/api/forensic/upload`**
- Upload Forensic Trace Datei
- **Request:** Multipart Form Data
- **Response:**
```json
{
  "status": "success",
  "logs": [...]
}
```

---

## ✅ Compliance-Module

### DORA Validator (`Compliance/dora.py`)

**Zweck:** DORA-Verordnung Validierung

**Anforderungen:**
- Business Continuity
- Recovery Testing
- Incident Response
- Monitoring & Detection
- Crisis Communication

**Verwendung:**
```python
from Compliance.dora import DORAValidator

validator = DORAValidator()
result = validator.validate_inject(inject)
```

### NIS2 Validator (`Compliance/nis2.py`)

**Zweck:** NIS2-Richtlinie Validierung

### ISO 27001 Validator (`Compliance/iso27001.py`)

**Zweck:** ISO 27001 Standard Validierung

---

## 🛠️ Utilities

### Retry Handler (`utils/retry_handler.py`)

**Zweck:** Retry-Logik für LLM-Calls

**Features:**
- Exponential Backoff
- Max Retries konfigurierbar
- Error-Handling

**Verwendung:**
```python
from utils.retry_handler import retry_with_backoff

@retry_with_backoff(max_retries=3)
def call_llm(prompt):
    # LLM-Call
    pass
```

### Safe JSON (`utils/safe_json.py`)

**Zweck:** Sichere JSON-Serialisierung für datetime-Objekte

**Verwendung:**
```python
from utils.safe_json import safe_json_dumps

json_str = safe_json_dumps(data_with_datetime)
```

---

## 📖 Weitere Dokumentation

- **Vollständige Dokumentation:** [COMPLETE_DOCUMENTATION.md](COMPLETE_DOCUMENTATION.md)
- **Backend:** [backend/BACKEND_DOKUMENTATION.md](backend/BACKEND_DOKUMENTATION.md)
- **Frontend:** [frontend/README.md](frontend/README.md)
- **API:** [api/README.md](api/README.md)

---

**Erstellt:** Januar 2025  
**Status:** ✅ Vollständig


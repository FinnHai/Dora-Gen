# 📚 CRUX - Vollständige Projekt-Dokumentation

**Version:** 1.0  
**Stand:** Januar 2025  
**Projekt:** CRUX - The Glass Box (Bachelorarbeit)

---

## 📑 Inhaltsverzeichnis

1. [Projekt-Übersicht](#projekt-übersicht)
2. [Architektur](#architektur)
3. [Backend-Komponenten](#backend-komponenten)
4. [Frontend-Komponenten](#frontend-komponenten)
5. [API-Server](#api-server)
6. [Compliance-Module](#compliance-module)
7. [Evaluation & Testing](#evaluation--testing)
8. [Utilities & Tools](#utilities--tools)
9. [Setup & Deployment](#setup--deployment)

---

## 🎯 Projekt-Übersicht

**CRUX (Crisis Response & Understanding eXperience)** ist ein Neuro-Symbolisches AI-System zur Generierung realistischer, logisch konsistenter Krisenszenarien für Finanzunternehmen. Das System kombiniert Generative AI (LLMs) mit symbolischer Logik (Knowledge Graphs) zur Hallucination-Mitigation.

### Kern-Features

- ✅ **Multi-Agenten-System** mit LangGraph
- ✅ **Knowledge Graph** (Neo4j) für Topologie & State Management
- ✅ **DORA/NIS2 Compliance** Validierung
- ✅ **Digital Twin** Visualisierung (React Flow)
- ✅ **Forensic Trace** Logging
- ✅ **Quality Assurance Framework**

### Tech Stack

- **Backend:** Python 3.10+, LangGraph, Neo4j, OpenAI GPT-4o
- **Frontend:** Next.js 16, React Flow, TypeScript, Tailwind CSS
- **API:** FastAPI
- **Database:** Neo4j (Graph), ChromaDB (Vector)

---

## 🏗️ Architektur

### High-Level Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                            │
│  Next.js App → React Flow Graph → Zustand Store             │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼──────────────────────────────────────┐
│                    API Server Layer                          │
│  FastAPI → Endpoints → Request Validation                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Orchestration Layer (LangGraph)                 │
│  ScenarioWorkflow → State Management → Agent Coordination   │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌────▼──────┐ ┌────▼──────┐
│ Agent Layer  │ │ Knowledge │ │ LLM Layer │
│              │ │   Graph   │ │            │
│ Manager      │ │   Neo4j   │ │  OpenAI    │
│ Generator    │ │           │ │  GPT-4o    │
│ Critic       │ │ ChromaDB  │ │            │
│ Intel        │ │  (RAG)    │ │            │
└──────────────┘ └───────────┘ └────────────┘
```

### Datenfluss

1. **Frontend** → API Request → **API Server**
2. **API Server** → Workflow Trigger → **LangGraph**
3. **LangGraph** → Agent Calls → **LLM/Neo4j**
4. **Neo4j** → State Updates → **Knowledge Graph**
5. **API Server** → Response → **Frontend**

**📖 Detaillierte Architektur:** Siehe [docs/architecture/ARCHITECTURE.md](architecture/ARCHITECTURE.md)

---

## 🔧 Backend-Komponenten

### 1. State Models (`state_models.py`)

**Zweck:** Pydantic-Modelle für Type-Safety und Validierung

**Wichtige Modelle:**
- `Inject`: MSEL-Inject Schema mit Validierung
- `ScenarioState`: Zustand eines laufenden Szenarios
- `KnowledgeGraphEntity`: Entität für Neo4j Graph
- `ValidationResult`: Ergebnis der Critic-Agent Validierung
- `CrisisPhase`: Enum für Phasen (Normal Operation → Crisis → Recovery)

**Verwendung:**
```python
from state_models import Inject, ScenarioType, CrisisPhase

inject = Inject(
    inject_id="INJ-001",
    content="SIEM Alert: Unusual login pattern detected",
    phase=CrisisPhase.NORMAL_OPERATION,
    time_offset="T+00:05"
)
```

**📖 Vollständige Dokumentation:** Siehe [docs/backend/BACKEND_DOKUMENTATION.md](backend/BACKEND_DOKUMENTATION.md)

---

### 2. Neo4j Client (`neo4j_client.py`)

**Zweck:** Verwaltung des Knowledge Graph States

**Hauptfunktionen:**
- `get_current_state()`: Abfrage aller Entities
- `update_entity_status()`: Status-Update mit Cascade-Berechnung
- `get_affected_entities()`: Second-Order Effects berechnen
- `save_scenario()`: Szenario in Neo4j persistieren
- `get_scenario()`: Gespeichertes Szenario laden

**Beispiel:**
```python
from neo4j_client import Neo4jClient

client = Neo4jClient()
client.connect()

# Status aktualisieren (automatische Cascade-Berechnung)
client.update_entity_status(
    entity_id="SRV-001",
    status="compromised",
    inject_id="INJ-005"
)

# Betroffene Entities abfragen
affected = client.get_affected_entities("SRV-001")
```

**📖 Vollständige Dokumentation:** Siehe [docs/backend/BACKEND_DOKUMENTATION.md](backend/BACKEND_DOKUMENTATION.md)

---

### 3. Agents (`agents/`)

#### 3.1 Manager Agent (`manager_agent.py`)

**Zweck:** Storyline-Planung basierend auf Szenario-Typ und Phase

**Funktionen:**
- Analysiert aktuellen Systemzustand
- Erstellt strategischen Plan für nächste Schritte
- Bestimmt Phase-Transitions

#### 3.2 Generator Agent (`generator_agent.py`)

**Zweck:** Erzeugt detaillierte Injects mit LLM

**Funktionen:**
- Generiert realistische Inject-Inhalte
- Nutzt Kontext aus Neo4j State
- Berücksichtigt MITRE ATT&CK TTPs

#### 3.3 Critic Agent (`critic_agent.py`)

**Zweck:** Validiert Logik, DORA-Konformität und Causal Validity

**Validierungen:**
- Logical Consistency (keine Widersprüche)
- Causal Validity (MITRE ATT&CK Konformität)
- DORA Compliance (Artikel 25)
- Temporal Consistency (chronologische Logik)

**Metriken:**
- `logical_consistency_score`: 0.0-1.0
- `causal_validity_score`: 0.0-1.0
- `compliance_score`: 0.0-1.0
- `overall_quality_score`: Kombinierter Score

#### 3.4 Intel Agent (`intel_agent.py`)

**Zweck:** Stellt relevante MITRE ATT&CK TTPs bereit (RAG)

**Funktionen:**
- Semantische Suche in ChromaDB
- Kontext-basierte TTP-Auswahl
- Filterung nach aktueller Phase

**📖 Vollständige Dokumentation:** Siehe [docs/backend/AGENTEN_DOKUMENTATION.md](backend/AGENTEN_DOKUMENTATION.md)

---

### 4. Workflows (`workflows/`)

#### 4.1 Scenario Workflow (`scenario_workflow.py`)

**Zweck:** LangGraph-basierte Orchestrierung der Agenten

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

**Beispiel:**
```python
from workflows.scenario_workflow import ScenarioWorkflow
from state_models import ScenarioType

workflow = ScenarioWorkflow(
    neo4j_client=client,
    max_iterations=10,
    mode='thesis'
)

result = workflow.generate_scenario(
    scenario_type=ScenarioType.RANSOMWARE_DOUBLE_EXTORTION
)
```

**📖 Vollständige Dokumentation:** Siehe [docs/backend/BACKEND_WORKFLOW_DOKUMENTATION.md](backend/BACKEND_WORKFLOW_DOKUMENTATION.md)

---

### 5. Forensic Logger (`forensic_logger.py`)

**Zweck:** Thread-safe JSONL-Logging für forensische Nachvollziehbarkeit

**Event-Typen:**
- `DRAFT`: Rohe, abgelehnte Injects
- `CRITIC`: Validierungsfehler/Warnungen
- `REFINED`: Finale, akzeptierte Injects

**Format:** JSONL (eine Zeile = ein Event)

**Verwendung:**
```python
from forensic_logger import get_forensic_logger

logger = get_forensic_logger(scenario_id="SCEN-001")
logger.log_draft(scenario_id, draft_inject)
logger.log_critic(scenario_id, inject_id, validation_result)
logger.log_refined(scenario_id, final_inject)
```

---

## 🎨 Frontend-Komponenten

### 1. Hauptkomponenten (`crux-frontend/components/`)

#### 1.1 DigitalTwinGraph (`DigitalTwinGraph.tsx`)

**Zweck:** Hauptkomponente für Graph-Visualisierung

**Features:**
- React Flow Graph mit Custom Nodes/Edges
- Layered Topology (External → Application → Data)
- Focus Mode (Spotlight Effect)
- Timeline-basierte Replay
- Fog of War vs. God Mode

**Props:** Keine (nutzt Zustand Store)

**Verwendung:**
```tsx
import DigitalTwinGraph from '@/components/DigitalTwinGraph';

<DigitalTwinGraph />
```

#### 1.2 NeuralNode (`NeuralNode.tsx`)

**Zweck:** Custom React Flow Node mit Mission Control Look

**Features:**
- Icons für Asset-Typen (Server, Database, Network)
- Status-Halos (farbcodiert)
- Glitch-Animation für kompromittierte Nodes
- Pulse-Animation für kritische Assets

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
}
```

#### 1.3 NeuralEdge (`NeuralEdge.tsx`)

**Zweck:** Custom React Flow Edge mit Traffic-Animation

**Features:**
- Animierte Partikel entlang Verbindungen
- Farbcodierung nach Link-Typ
- Rote Partikel für kompromittierte Verbindungen

#### 1.4 ScenarioLoader (`ScenarioLoader.tsx`)

**Zweck:** Suchen und Laden gespeicherter Szenarien

**Features:**
- Suchfunktion (Live-Filterung)
- Filter nach Typ
- Sortierung (Datum, Injects, Typ)
- Modal-Dialog mit Scrollbar

#### 1.5 EvaluationDashboard (`EvaluationDashboard.tsx`)

**Zweck:** Vergleich Neuro-Symbolic vs. Pure LLM

**Metriken:**
- Logical Consistency Score
- Causal Validity Score
- Asset Consistency Score
- Overall Score

#### 1.6 EvidenceMatrix (`EvidenceMatrix.tsx`)

**Zweck:** QA-Test-Ergebnisse visualisieren

**Tests:**
- T-01: Kausalitäts-Stresstest
- T-02: Amnesie-Test
- T-03: DORA-Compliance Audit
- T-04: Kettenreaktion-Test

**📖 Vollständige Dokumentation:** Siehe [docs/frontend/README.md](frontend/README.md)

---

### 2. Hooks (`crux-frontend/hooks/`)

#### 2.1 useDigitalTwinData (`useDigitalTwinData.ts`)

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

#### 2.2 useScenarioReplay (`useScenarioReplay.ts`)

**Zweck:** Replay von Timeline Events auf Graph Topology

**Funktionen:**
- Zeitbasierte Status-Updates
- Berechnet Attack Vectors
- Cascade-Berechnung

#### 2.3 useFogOfWar (`useFogOfWar.ts`)

**Zweck:** Berechnet Perceived State für Player Mode

**Logik:**
- Zeigt nur bekannte Informationen
- Unbekannte Nodes sind transparent/gestrichelt

---

### 3. Store (`crux-frontend/lib/store.ts`)

**Zweck:** Zustand Store (Zustand) für globale State-Verwaltung

**State:**
- `injects`: Array von Injects
- `graphNodes`: Graph Nodes
- `graphLinks`: Graph Links
- `viewMode`: 'player' | 'god'
- `executionMode`: 'thesis' | 'legacy'
- `interactiveMode`: boolean
- `pendingDecision`: Decision Point State

**Actions:**
- `setInjects()`, `setGraphNodes()`, `setViewMode()`, etc.

---

### 4. Utilities (`crux-frontend/lib/`)

#### 4.1 graphTransformer (`graphTransformer.ts`)

**Zweck:** Konvertiert Neo4j Backend-Daten zu React Flow Format

**Funktionen:**
- `transformNeo4jToGraphNodes()`
- `transformNeo4jToGraphLinks()`
- `determineLayer()`: Layer-Zuordnung (External/Application/Data)

#### 4.2 layout-utils (`layout-utils.ts`)

**Zweck:** Graph-Layout-Algorithmen

**Funktionen:**
- `applyCircularLayout()`: Konzentrische Ringe
- `applyInitialScatter()`: Zufällige Verteilung
- `applyGridSnapping()`: Grid-Alignment

#### 4.3 layered-topology (`layered-topology.ts`)

**Zweck:** Organisiert Nodes in semantische Schichten

**Layers:**
- External: Firewalls, Load Balancers
- Application: App Servers, Core Servers
- Data: Databases, Storage

#### 4.4 qa-framework (`qa-framework.ts`)

**Zweck:** Quality Assurance Framework Tests

**Tests:**
- `runAllTests()`: Führt alle 4 Tests aus
- `TestResult`: Interface für Test-Ergebnisse

**📖 Vollständige Dokumentation:** Siehe [docs/frontend/README.md](frontend/README.md)

---

## 🌐 API-Server

### FastAPI Server (`api_server.py`)

**Zweck:** REST API für Frontend-Backend-Kommunikation

**Endpoints:**

#### Szenario-Generierung
- `POST /api/scenario/generate`: Generiert neues Szenario
- `GET /api/scenario/latest`: Neuestes Szenario
- `GET /api/scenario/list`: Liste aller Szenarien
- `GET /api/scenario/{scenario_id}`: Einzelnes Szenario
- `GET /api/scenario/{scenario_id}/logs`: Critic-Logs

#### Graph-Daten
- `GET /api/graph/nodes`: Alle Graph Nodes
- `GET /api/graph/links`: Alle Graph Links

#### Forensic Trace
- `POST /api/forensic/upload`: Upload Forensic Trace Datei

**Beispiel:**
```bash
# Szenario generieren
curl -X POST http://localhost:8000/api/scenario/generate \
  -H "Content-Type: application/json" \
  -d '{"scenario_type": "ransomware_double_extortion", "num_injects": 10}'

# Graph Nodes abfragen
curl http://localhost:8000/api/graph/nodes
```

**📖 Vollständige Dokumentation:** Siehe [docs/api/README.md](api/README.md)

---

## ✅ Compliance-Module

### Compliance Frameworks (`Compliance/`)

#### DORA (`dora.py`)

**Zweck:** DORA-Verordnung Validierung

**Anforderungen:**
- Business Continuity
- Recovery Testing
- Incident Response
- Monitoring & Detection
- Crisis Communication

#### NIS2 (`nis2.py`)

**Zweck:** NIS2-Richtlinie Validierung

#### ISO 27001 (`iso27001.py`)

**Zweck:** ISO 27001 Standard Validierung

**Verwendung:**
```python
from Compliance.dora import DORAValidator

validator = DORAValidator()
result = validator.validate_inject(inject)
```

**📖 Vollständige Dokumentation:** Siehe [Compliance/README.md](../Compliance/README.md)

---

## 🧪 Evaluation & Testing

### 1. Quality Assurance Framework (`lib/qa-framework.ts`)

**Zweck:** Strategische Tests zur Validierung der Neuro-Symbolischen Architektur

**Tests:**

#### T-01: Kausalitäts-Stresstest (Teleportation Test)
- **Ziel:** Beweist, dass Graph unlogische Angriffe verhindert
- **Methode:** Versuche direkten Angriff auf isolierte DB ohne Vorstufe
- **Erwartung:** Critic lehnt ab

#### T-02: Amnesie-Test (State Persistence)
- **Ziel:** Beweist, dass System State behält
- **Methode:** Versuche Re-Kompromittierung bereits kompromittierter Assets
- **Erwartung:** System erkennt bereits kompromittierte Assets

#### T-03: DORA-Compliance Audit
- **Ziel:** Beweist, dass Compliance-Tags auf Fakten basieren
- **Methode:** Prüfe ob Blue Team Injects vorhanden sind
- **Erwartung:** Compliance-Tags entsprechen tatsächlichen Injects

#### T-04: Kettenreaktion-Test (Second-Order Effects)
- **Ziel:** Beweist automatische Cascade-Berechnung
- **Methode:** Setze IdP offline, prüfe abhängige Apps
- **Erwartung:** Abhängige Apps automatisch auf Degraded/Offline

**Ausführung:**
```bash
python scripts/run_qa_tests_simple.py
```

**📖 Vollständige Dokumentation:** Siehe [docs/QA_TESTS_BESCHREIBUNG.md](QA_TESTS_BESCHREIBUNG.md)

---

### 2. Unit Tests (`tests/`)

**Test-Dateien:**
- `test_agents.py`: Agent-Tests
- `test_workflow.py`: Workflow-Tests
- `test_neo4j_client.py`: Neo4j Client Tests
- `test_api_endpoints.py`: API Endpoint Tests

**Ausführung:**
```bash
python tests/run_all_tests.py
```

**📖 Vollständige Dokumentation:** Siehe [tests/README.md](../tests/README.md)

---

## 🛠️ Utilities & Tools

### 1. Retry Handler (`utils/retry_handler.py`)

**Zweck:** Retry-Logik für LLM-Calls

**Features:**
- Exponential Backoff
- Max Retries konfigurierbar
- Error-Handling

### 2. Safe JSON (`utils/safe_json.py`)

**Zweck:** Sichere JSON-Serialisierung für datetime-Objekte

**Features:**
- `DateTimeEncoder`: Custom JSON Encoder
- `safe_json_dumps()`: Sichere Serialisierung

### 3. Scripts (`scripts/`)

- `check_setup.py`: Setup-Prüfung
- `populate_ttp_database.py`: TTP-Datenbank Setup
- `run_qa_tests_simple.py`: QA-Tests ausführen
- `start_neo4j.sh`: Neo4j Start-Skript

---

## 🚀 Setup & Deployment

### Backend Setup

```bash
# Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# Neo4j starten
./scripts/start_neo4j.sh

# API Server starten
python api_server.py
# oder
uvicorn api_server:app --reload
```

### Frontend Setup

```bash
cd crux-frontend

# Dependencies installieren
npm install

# Development Server starten
npm run dev
```

**📖 Vollständige Anleitung:** Siehe [docs/getting-started/SETUP.md](getting-started/SETUP.md)

---

## 📖 Weitere Dokumentation

- **Architektur:** [docs/architecture/ARCHITECTURE.md](architecture/ARCHITECTURE.md)
- **Backend:** [docs/backend/BACKEND_DOKUMENTATION.md](backend/BACKEND_DOKUMENTATION.md)
- **Frontend:** [docs/frontend/README.md](frontend/README.md)
- **API:** [docs/api/README.md](api/README.md)
- **User Guides:** [docs/user-guides/README.md](user-guides/README.md)
- **Thesis:** [docs/thesis/THESIS_DOCUMENTATION.md](thesis/THESIS_DOCUMENTATION.md)

---

## 📝 Changelog

### Version 1.0 (Januar 2025)
- ✅ Vollständige Dokumentation aller Komponenten
- ✅ Backend-Komponenten dokumentiert
- ✅ Frontend-Komponenten dokumentiert
- ✅ API-Server dokumentiert
- ✅ QA-Framework dokumentiert

---

**Erstellt:** Januar 2025  
**Autor:** CRUX Development Team  
**Status:** ✅ Vollständig


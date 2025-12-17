# 📁 Projektstruktur

Diese Datei dokumentiert die organisierte Projektstruktur.

## Verzeichnisstruktur

```
BA/
├── app.py                          # Hauptanwendung (Streamlit)
├── neo4j_client.py                 # Neo4j Client (Core)
├── state_models.py                  # Pydantic Models (Core)
├── requirements.txt                 # Python Dependencies
├── README.md                        # Projektübersicht
├── .env.example                     # Umgebungsvariablen Template
├── .gitignore                       # Git Ignore Rules
│
├── agents/                          # Agent-Implementierungen
│   ├── __init__.py
│   ├── manager_agent.py            # Manager Agent
│   ├── generator_agent.py           # Generator Agent
│   ├── critic_agent.py              # Critic Agent
│   └── intel_agent.py               # Intel Agent
│
├── workflows/                       # LangGraph Workflows
│   ├── __init__.py
│   ├── scenario_workflow.py        # Haupt-Workflow
│   ├── fsm.py                       # Finite State Machine
│   └── state_schema.py              # State Schema
│
├── frontend/                        # Frontend-Anwendungen
│   ├── __init__.py
│   ├── crisis_cockpit.py           # Crisis Cockpit
│   ├── thesis_frontend.py           # Thesis Frontend
│   └── README.md
│
├── scripts/                         # Hilfsskripte
│   ├── __init__.py
│   ├── check_setup.py               # Setup-Prüfung
│   ├── create_pdf_final.py          # PDF-Generierung
│   ├── start_neo4j.sh               # Neo4j Start-Skript
│   ├── PUSH_TO_GITHUB.sh            # Deployment-Skript
│   ├── populate_ttp_database.py     # TTP-Datenbank Setup
│   └── README.md
│
├── examples/                        # Beispiel-Szenarien
│   ├── __init__.py
│   ├── demo_scenarios.py            # Demo-Szenarien
│   └── README.md
│
├── templates/                       # Infrastruktur-Templates
│   ├── __init__.py
│   ├── infrastructure_templates.py  # Neo4j Templates
│   └── README.md
│
├── tests/                          # Tests
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_workflow.py
│   ├── test_workflow_basic.py
│   ├── test_workflow_integration.py
│   ├── test_workflow_nodes.py
│   ├── test_crisis_cockpit.py
│   ├── test_interactive_workflow.py
│   ├── test_setup.py
│   ├── test_system_state_format.py
│   ├── run_all_tests.py
│   ├── README.md
│   └── TEST_RESULTS.md
│
├── evaluation/                     # Evaluation & Metriken
│   ├── __init__.py
│   ├── automatic_evaluator.py
│   ├── hallucination_test_cases.py
│   ├── run_evaluation.py
│   ├── analysis_metrics.py
│   ├── EVALUATION_SUMMARY.md
│   ├── EVALUATION_METHODOLOGY.md
│   └── README.md
│
├── utils/                          # Utilities
│   ├── __init__.py
│   └── retry_handler.py            # Retry-Logik
│
├── docs/                           # Dokumentation
│   ├── README.md                   # Dokumentationsübersicht
│   ├── getting-started/            # Schnellstart & Setup
│   ├── user-guides/                # Benutzeranleitungen
│   ├── architecture/               # Architektur & Design
│   ├── development/                 # Entwicklung & Deployment
│   ├── evaluation/                 # Evaluation & Tests
│   ├── thesis/                     # Thesis-Dokumentation
│   ├── PROJECT_STATUS.md
│   ├── IMPLEMENTATION_REALITY.md
│   └── DOCUMENTATION_ORGANIZATION.md
│
├── logs/                           # Automatisch generierte Logs
│   ├── CRITIC_AUDIT_LOG.md
│   └── README.md
│
├── archive/                        # Archivierte Dateien
│   ├── QUICKSTART.md
│   ├── DOKUMENTATION_UEBERSICHT.md
│   └── README.md
│
└── Compliance/                     # Compliance-Dokumente
    └── dora-regulation-rts--2024-1532_en.pdf
```

## Kategorien

### Core-Module (Root)
- `app.py` - Hauptanwendung
- `neo4j_client.py` - Neo4j Client
- `state_models.py` - Pydantic Models

### Agenten (`agents/`)
Alle Agent-Implementierungen für das Multi-Agenten-System.

### Workflows (`workflows/`)
LangGraph-basierte Workflow-Orchestrierung.

### Frontend (`frontend/`)
Streamlit-Frontend-Anwendungen (außer Hauptanwendung).

### Scripts (`scripts/`)
Hilfsskripte für Setup, Deployment und Utilities.

### Examples (`examples/`)
Beispiel-Szenarien und Demo-Code.

### Templates (`templates/`)
Infrastruktur-Templates für Neo4j.

### Tests (`tests/`)
Alle Test-Dateien und Test-Utilities.

### Evaluation (`evaluation/`)
Evaluation-Tools, Metriken und Analyse-Skripte.

### Utils (`utils/`)
Gemeinsame Utilities und Helper-Funktionen.

### Dokumentation (`docs/`)
Strukturierte Dokumentation nach Kategorien.

### Logs (`logs/`)
Automatisch generierte Log-Dateien.

### Archive (`archive/`)
Veraltete oder archivierte Dateien.

## Import-Pfade

### Core-Module (direkt importierbar)
```python
from neo4j_client import Neo4jClient
from state_models import ScenarioType, CrisisPhase, Inject
```

### Pakete (mit Verzeichnis-Präfix)
```python
from agents.generator_agent import GeneratorAgent
from workflows.scenario_workflow import ScenarioWorkflow
from examples.demo_scenarios import get_available_demo_scenarios
from templates.infrastructure_templates import get_available_templates
```

## Verwendung

### Hauptanwendung starten
```bash
streamlit run app.py
```

### Crisis Cockpit starten
```bash
streamlit run frontend/crisis_cockpit.py
```

### Tests ausführen
```bash
python tests/run_all_tests.py
```

### Setup prüfen
```bash
python scripts/check_setup.py
```

## Hinweise

- Core-Module (`neo4j_client.py`, `state_models.py`) bleiben im Root für einfache Imports
- Hauptanwendung (`app.py`) bleibt im Root für einfachen Zugriff
- Alle anderen Dateien sind in logischen Verzeichnissen organisiert
- Jedes Verzeichnis hat eine `README.md` mit Erklärungen

---

**Erstellt:** 2025-01-15
**Status:** ✅ Organisiert

# 📚 Dokumentations-Übersicht

Übersicht aller verfügbaren Dokumentationen für den DORA-Szenariengenerator.

## 🚀 Schnelleinstieg

### Für neue Nutzer
1. **[QUICKSTART.md](QUICKSTART.md)** - In 5 Minuten zum ersten Szenario
2. **[SETUP.md](SETUP.md)** - Detaillierte Setup-Anleitung
3. **[FRONTEND.md](FRONTEND.md)** - Frontend-Bedienungsanleitung

## 📖 Hauptdokumentation

### [README.md](README.md)
**Hauptdokumentation des Projekts**
- Projektziel und Architektur
- Tech Stack Übersicht
- Setup-Anleitung
- Verwendungsbeispiele
- Komponenten-Übersicht

### [ARCHITECTURE.md](ARCHITECTURE.md)
**Detaillierte Architektur-Dokumentation**
- High-Level Architektur-Diagramme
- Workflow-Diagramme (Mermaid)
- Komponenten-Architektur
- Datenfluss-Diagramme
- FSM (Finite State Machine) Diagramme
- Entity-Relationship Diagramme

## 📊 Status & Capabilities

### [STATUS.md](STATUS.md)
**Detaillierte Status-Übersicht**
- ✅ Was das System jetzt kann
- ⚠️ Was noch fehlt / Verbesserungspotenzial
- 🚀 Wie das System eingesetzt werden kann
- 📈 Roadmap
- 🎓 Best Practices

**Empfohlen für:**
- Projekt-Manager
- Entwickler, die Features hinzufügen wollen
- Stakeholder, die den aktuellen Stand verstehen wollen

## 🔧 Setup & Installation

### [SETUP.md](SETUP.md)
**Detaillierte Setup-Anleitung**
- Schritt-für-Schritt Installation
- Umgebungsvariablen-Konfiguration
- Neo4j Setup
- Troubleshooting

### [QUICKSTART.md](QUICKSTART.md)
**Schnellstart in 5 Minuten**
- Minimales Setup
- Erste Schritte
- Häufige Probleme

## 🎨 Frontend

### [FRONTEND.md](FRONTEND.md)
**Streamlit Frontend Anleitung**
- Features-Übersicht
- Verwendungsanleitung
- Tabs-Erklärung
- Export-Funktionen
- Troubleshooting

## 💻 Code-Dokumentation

### Python-Dateien
Alle Python-Module enthalten Docstrings:

- **`state_models.py`**: Pydantic-Modelle mit vollständiger Dokumentation
- **`neo4j_client.py`**: Neo4j Client mit Methoden-Dokumentation
- **`workflows/scenario_workflow.py`**: LangGraph Workflow
- **`agents/`**: Alle Agenten mit Funktions-Dokumentation

### Test-Dateien
- **`test_setup.py`**: Setup-Tests
- **`test_workflow.py`**: Workflow-Tests
- **`check_setup.py`**: Erweiterte Setup-Prüfung

## 📋 Verwendungsbeispiele

### Frontend (Empfohlen)
```bash
streamlit run app.py
```
Siehe [FRONTEND.md](FRONTEND.md)

### Programmgesteuert
```python
from neo4j_client import Neo4jClient
from workflows.scenario_workflow import ScenarioWorkflow
from state_models import ScenarioType

neo4j = Neo4jClient()
neo4j.connect()

workflow = ScenarioWorkflow(neo4j_client=neo4j, max_iterations=10)
result = workflow.generate_scenario(ScenarioType.RANSOMWARE_DOUBLE_EXTORTION)
```

Siehe [README.md](README.md) für weitere Beispiele.

## 🗂️ Dokumentations-Struktur

```
BA/
├── README.md          # Hauptdokumentation
├── ARCHITECTURE.md    # Architektur-Diagramme
├── STATUS.md          # Status & Capabilities
├── QUICKSTART.md      # Schnellstart
├── SETUP.md           # Setup-Anleitung
├── FRONTEND.md        # Frontend-Anleitung
├── DOCUMENTATION.md    # Diese Datei
│
├── state_models.py     # Code-Dokumentation (Docstrings)
├── neo4j_client.py    # Code-Dokumentation (Docstrings)
├── workflows/         # Workflow-Dokumentation
└── agents/            # Agenten-Dokumentation
```

## 🎯 Nach Anwendungsfall

### Ich möchte...
- **...schnell starten**: [QUICKSTART.md](QUICKSTART.md)
- **...alles verstehen**: [README.md](README.md)
- **...den aktuellen Stand wissen**: [STATUS.md](STATUS.md)
- **...das Frontend nutzen**: [FRONTEND.md](FRONTEND.md)
- **...Setup-Probleme lösen**: [SETUP.md](SETUP.md)
- **...Code verstehen**: Siehe Docstrings in den Python-Dateien

## 📞 Support

Bei Fragen oder Problemen:
1. Prüfe die entsprechende Dokumentation
2. Siehe Troubleshooting-Abschnitte
3. Prüfe `check_setup.py` für System-Status

## 🔄 Dokumentation aktualisieren

Diese Dokumentationen werden regelmäßig aktualisiert:
- **README.md**: Bei größeren Änderungen
- **STATUS.md**: Bei neuen Features oder Änderungen
- **Code-Dokumentation**: Bei Code-Änderungen

**Letzte Aktualisierung**: 2025-01-XX


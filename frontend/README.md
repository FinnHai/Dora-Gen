# Frontend

Dieses Verzeichnis enthält die Streamlit-Frontend-Anwendungen.

## Dateien

- **`app.py`** - Hauptanwendung (DORA Scenario Generator)
  - Enterprise-Grade Streamlit Interface
  - Multi-Agenten-System Integration
  - Interaktiver Modus mit Decision-Points
  - Export-Funktionalität (CSV, JSON, Excel, MSEL)

- **`crisis_cockpit.py`** - Crisis Cockpit (Thesis-Evaluation-Tool)
  - Split-Screen Layout
  - Dungeon Master Mode
  - Hallucination-Rating-System
  - Debug-Informationen

- **`thesis_frontend.py`** - Thesis-spezifisches Frontend
  - Für wissenschaftliche Evaluation
  - Spezielle Visualisierungen

- **`scientific_frontend.py`** - Wissenschaftliches Analyse-Frontend ⭐
  - 30 verschiedene Analysen in 3 Kategorien
  - Zeitanalyse & Prozess-Mining (10 Analysen)
  - Textanalyse & Semantik (10 Analysen)
  - Qualitätsmetriken & Performance (10 Analysen)
  - Interaktive Visualisierungen (Plotly)
  - Dashboard-Übersicht mit Key Metrics
  - Grid-Layout für bessere Übersichtlichkeit
  - JSONL-File-Upload für Forensic-Trace-Daten

- **`TOOLS_AND_ALTERNATIVES.md`** - Dokumentation alternativer Analyse-Tools
  - Vergleich verschiedener Tools (Streamlit, JupyterLab, ELK Stack, KNIME, etc.)
  - Empfehlungen für verschiedene Use Cases

- **`system_simulation.html`** - HTML-System-Simulation 🎨
  - Interaktive Visualisierung des Multi-Agenten-Systems
  - Live-Status der Agenten (Manager, Intel, Generator, Critic)
  - Workflow-Visualisierung mit vis.js
  - Netzwerk-Graph der System-Architektur
  - Aktivitäts-Log in Echtzeit
  - Statistik-Dashboard (Iterationen, Injects, Akzeptierte, Refinements)
  - Animierte Simulation des Workflows

## Verwendung

### Hauptanwendung starten

```bash
streamlit run app.py
```

### Crisis Cockpit starten

```bash
streamlit run frontend/crisis_cockpit.py
```

### Wissenschaftliches Frontend starten

```bash
streamlit run frontend/scientific_frontend.py
```

### System-Simulation öffnen

Öffne die HTML-Datei direkt im Browser:

```bash
open frontend/system_simulation.html
# oder
xdg-open frontend/system_simulation.html  # Linux
```

Die Simulation zeigt:
- **Agenten-Status**: Live-Status aller 4 Agenten
- **Workflow-Visualisierung**: Schritt-für-Schritt Prozess
- **Netzwerk-Graph**: System-Architektur mit vis.js
- **Aktivitäts-Log**: Echtzeit-Logging aller Aktionen
- **Statistiken**: Iterationen, Injects, Akzeptierte, Refinements

## Hinweis

Die Hauptanwendung `app.py` befindet sich im Root-Verzeichnis für einfachen Zugriff.

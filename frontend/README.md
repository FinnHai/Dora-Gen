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

## Verwendung

### Hauptanwendung starten

```bash
streamlit run app.py
```

### Crisis Cockpit starten

```bash
streamlit run frontend/crisis_cockpit.py
```

## Hinweis

Die Hauptanwendung `app.py` befindet sich im Root-Verzeichnis für einfachen Zugriff.

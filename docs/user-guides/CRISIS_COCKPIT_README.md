# The Crisis Cockpit - User Guide

## Übersicht

**The Crisis Cockpit** ist ein interaktives Streamlit-Frontend für die Bachelor-Thesis "Neuro-Symbolic Crisis Generator". Es ermöglicht die Visualisierung, Steuerung und Evaluation von Krisenszenarien.

## Features

### 1. Split-Screen Layout ("Split-Screen of Truth")

- **Linke Spalte (Story Feed):** Zeigt alle generierten Injects chronologisch
  - Zeitstempel und Inject-ID
  - Source → Target Information
  - Vollständiger Content
  - Phase-Badges mit Farbcodierung
  - MITRE ATT&CK IDs und betroffene Assets

- **Rechte Spalte (State Reality):** Live-Dashboard des Systemzustands
  - Resource Metrics (Diesel Tank, Server Health, Database Status, Network Bandwidth)
  - Asset Status (Compromised/Online Assets)
  - Automatische Updates nach jedem Inject

### 2. Dungeon Master Mode (Sidebar)

- **Manual Event Injection:** Manuelles Einfügen von Events zur Simulation-Steuerung
- **Force Step Button:** Erzwingt den nächsten AI-Schritt (bei hängenden Loops)
- **Auto-Play Button:** Führt automatisch 5 Schritte aus

### 3. Thesis Evaluation Module

- **Mode Toggle:** Wechsel zwischen "Legacy Mode" und "Logic Guard Mode"
- **Rating Buttons:** 
  - 👍 (Consistent) - Markiert Inject als konsistent
  - 👎 (Hallucination) - Markiert Inject als Hallucination, öffnet Text-Input für Error Reason
- **CSV Export:** Download-Button für alle Evaluation-Daten
  - Format: `inject_id`, `mode`, `rating`, `reason`, `timestamp`

### 4. Debugging & Transparency

- **Raw Data Expander:** Unter jedem Inject
  - Zeigt Raw JSON vom LLM
  - Zeigt Logic-Check Result (z.B. "Logic Guard rejected draft 2 times")

## Verwendung

### Starten der App

```bash
streamlit run frontend/crisis_cockpit.py
```

Die App läuft standardmäßig auf `http://localhost:8501`

### Mock-Daten

Die App startet mit Mock-Daten für UI-Testing. Diese können später durch echte Backend-Integration ersetzt werden.

### Backend-Integration

Um die App mit dem echten LangGraph-Backend zu verbinden:

1. **Injects vom Backend holen:**
   ```python
   # In crisis_cockpit.py, ersetze get_mock_injects() mit:
   from workflows.scenario_workflow import ScenarioWorkflow
   # ... Workflow initialisieren und Injects abrufen
   ```

2. **State vom Backend holen:**
   ```python
   # In frontend/crisis_cockpit.py, ersetze get_mock_state() mit:
   from neo4j_client import Neo4jClient
   # ... Neo4j State abrufen und formatieren
   ```

3. **Live-Updates:**
   - Die `update_state_after_inject()` Funktion sollte echte State-Updates vom Backend durchführen
   - `force_next_step()` sollte den echten Workflow-Schritt auslösen

## Evaluation-Daten Format

Die CSV-Datei enthält folgende Spalten:

- `inject_id`: Eindeutige Inject-ID
- `mode`: "Legacy Mode" oder "Logic Guard Mode"
- `rating`: "Consistent" oder "Hallucination"
- `reason`: Optionaler Text mit der Begründung (nur bei Hallucination)
- `timestamp`: ISO-Format Timestamp

## Nächste Schritte

1. ✅ UI-Layout implementiert
2. ✅ Mock-Daten für Testing
3. ⏳ Backend-Integration (Workflow + Neo4j)
4. ⏳ Live-State-Updates
5. ⏳ Echte Logic-Guard-Ergebnisse anzeigen

## Technische Details

- **Python 3.10+**
- **Streamlit** für UI
- **Pandas** für CSV-Export
- **Session State** für State Management


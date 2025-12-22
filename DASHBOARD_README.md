# Thesis Mission Control Dashboard

Professionelles Streamlit-Dashboard für die Thesis-Evaluation des Neuro-Symbolic Crisis Generators.

## Funktionalität

### ✅ Vollständig implementiert:

1. **Live Simulation Tab**
   - Story Feed mit Chat-Interface
   - Logic Guard Monitor mit Live Asset-Status
   - Auto-Refresh alle 3 Sekunden
   - Start/Stop/Reset Controls
   - Mock-Backend für sofortige Demonstration

2. **Batch Experiment Tab**
   - Konfigurierbare Anzahl Szenarien (10-100)
   - Toggle zwischen Legacy Mode und Thesis Mode
   - Live Progress Bar und Metriken
   - Automatisches CSV-Export
   - Hallucination-Tracking

3. **Thesis Results Tab**
   - CSV-Datenvisualisierung
   - Bar Chart: Legacy vs Thesis Mode Vergleich
   - Pie Chart: Error Types Distribution
   - Metric Cards: Key Performance Indicators
   - Export-Funktion für Report Assets

### 🎨 Design Features:

- Professionelles Dark Theme
- Konsistente Farbpalette (Blau/Grün/Rot)
- Moderne Typografie
- Keine Emojis
- Responsive Layout

## Verwendung

### Dashboard starten:

```bash
streamlit run dashboard.py
```

### Workflow:

1. **Live Demo für Professor:**
   - Tab 1 öffnen
   - "Start Simulation" klicken
   - Injects erscheinen automatisch alle 3 Sekunden

2. **Batch Experiment für Daten:**
   - Tab 2 öffnen
   - Anzahl Szenarien wählen (z.B. 50)
   - Mode wählen (Legacy oder Thesis)
   - "Run Batch Evaluation" klicken
   - Ergebnisse werden in `experiment_results.csv` gespeichert

3. **Visualisierung für Thesis:**
   - Tab 3 öffnen
   - CSV wird automatisch geladen
   - Charts anzeigen und exportieren

## Backend-Integration

Das Dashboard verwendet aktuell Mock-Daten für sofortige Funktionalität. Um das echte Backend zu verwenden:

1. Entferne Mock-Funktionen (`mock_generate_inject`, `mock_validate_inject`, `mock_get_system_state`)
2. Ersetze mit echten Backend-Calls:
   ```python
   # Statt mock_generate_inject():
   workflow = ScenarioWorkflow(neo4j_client=neo4j)
   result = workflow.generate_scenario(ScenarioType.RANSOMWARE_DOUBLE_EXTORTION)
   
   # Statt mock_get_system_state():
   system_state = neo4j_client.get_current_state()
   ```

## Dateien

- `dashboard.py` - Haupt-Dashboard
- `experiment_results.csv` - Generierte Experiment-Daten (wird automatisch erstellt)

## Hinweise

- Mock-Daten sind für Demonstration und Testing gedacht
- CSV-Export funktioniert automatisch nach Batch-Experiment
- Auto-Refresh läuft nur wenn Simulation aktiv ist
- Alle Daten werden im Session State gespeichert (verloren bei Reload)

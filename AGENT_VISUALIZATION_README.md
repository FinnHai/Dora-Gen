# 🤖 Agenten Live-Visualisierung

Eine interaktive HTML-Visualisierung für das Multi-Agenten-System, die den Workflow-Fluss und den Status der einzelnen Agenten in Echtzeit anzeigt.

## 📋 Übersicht

Die `agent_visualization.html` Datei bietet eine visuelle Darstellung des Agenten-Workflows mit folgenden Features:

- **Netzwerk-Graph**: Zeigt alle Agenten als Nodes mit dem Workflow-Fluss als Edges
- **Live-Status**: Farbcodierte Status-Anzeige für jeden Agenten (Bereit/Aktiv/Abgeschlossen)
- **Statistiken**: Zeigt Anzahl von Injects, Entscheidungen und Logs
- **Log-Anzeige**: Zeigt die letzten Workflow-Logs in Echtzeit
- **Interaktivität**: Klickbare Nodes für detaillierte Informationen

## 🚀 Verwendung

### Schritt 1: Daten exportieren

1. Starte das Dashboard: `streamlit run dashboard.py`
2. Generiere einige Injects im "Live Simulation" Tab
3. Scrolle nach unten zum Abschnitt "🤖 Agent Visualization"
4. Klicke auf "📊 Agent-Daten für Visualisierung exportieren"
5. Speichere die JSON-Datei (z.B. `agent_data_20241218_120000.json`)

### Schritt 2: Visualisierung öffnen

1. Öffne `agent_visualization.html` in einem modernen Browser (Chrome, Firefox, Edge)
2. Klicke auf "📁 JSON laden" und wähle die exportierte JSON-Datei
3. Die Visualisierung wird automatisch aktualisiert

### Schritt 3: Live-Modus (optional)

Für kontinuierliche Updates:

1. Exportiere die JSON-Datei regelmäßig aus dem Dashboard
2. Speichere sie als `agent_data.json` im gleichen Ordner wie `agent_visualization.html`
3. Klicke auf "▶️ Live-Modus" in der Visualisierung
4. Die Visualisierung aktualisiert sich alle 2 Sekunden automatisch

## 🎨 Features

### Agenten-Nodes

Die Visualisierung zeigt folgende Agenten:

- **🔍 State Check**: Überprüft den aktuellen Systemzustand
- **👔 Manager**: Erstellt die Storyline
- **📡 Intel**: Holt relevante TTPs aus der Datenbank
- **🎯 Action Selection**: Wählt die passende Aktion aus
- **✍️ Generator**: Generiert den Inject-Entwurf
- **🔍 Critic**: Validiert den Inject
- **🔄 State Update**: Aktualisiert den Systemzustand
- **⚖️ Decision Point**: Benutzer-Entscheidungspunkte (nur im interaktiven Modus)

### Status-Farben

- **Grau**: Agent ist bereit (idle)
- **Grün**: Agent ist aktuell aktiv
- **Blau**: Agent hat seine Aufgabe abgeschlossen
- **Rot**: Fehler aufgetreten

### Workflow-Fluss

Die Edges (Verbindungen) zeigen den Workflow-Fluss:

- **Durchgezogene Linien**: Normale Workflow-Schritte
- **Gestrichelte Linien**: Optionale oder bedingte Schritte (z.B. Refine-Loops)

## 📊 Datenstruktur

Die JSON-Datei enthält folgende Informationen:

```json
{
  "workflow_logs": [
    {
      "timestamp": "2024-12-18T12:00:00",
      "node": "Manager",
      "iteration": 1,
      "action": "Storyline erstellen",
      "details": {}
    }
  ],
  "agent_decisions": [
    {
      "agent": "Generator",
      "timestamp": "2024-12-18T12:00:05",
      "input": {},
      "output": {}
    }
  ],
  "injects": [...],
  "scenario_id": "SCEN-001",
  "scenario_type": "RANSOMWARE_DOUBLE_EXTORTION",
  "export_timestamp": "2024-12-18T12:00:10",
  "total_injects": 5,
  "total_logs": 42,
  "total_decisions": 15
}
```

## 🔧 Technische Details

### Abhängigkeiten

Die Visualisierung verwendet:
- **vis-network**: Für die Netzwerk-Graph-Visualisierung (via CDN)
- **Vanilla JavaScript**: Keine zusätzlichen Build-Tools erforderlich

### Browser-Kompatibilität

- ✅ Chrome/Edge (empfohlen)
- ✅ Firefox
- ✅ Safari
- ❌ Internet Explorer (nicht unterstützt)

### Dateigröße

Die HTML-Datei ist standalone und benötigt keine zusätzlichen Dateien. Alle Abhängigkeiten werden über CDN geladen.

## 💡 Tipps

1. **Große Datensätze**: Bei vielen Injects kann die Visualisierung langsamer werden. Verwende Filter oder exportiere nur relevante Zeiträume.

2. **Offline-Nutzung**: Die Visualisierung benötigt eine Internetverbindung für das Laden von vis-network. Für Offline-Nutzung kannst du vis-network lokal speichern.

3. **Anpassungen**: Die HTML-Datei kann leicht angepasst werden (Farben, Layout, etc.) ohne zusätzliche Tools.

4. **Performance**: Bei sehr großen Datensätzen (>1000 Logs) kann es zu Performance-Problemen kommen. In diesem Fall filtere die Daten vor dem Export.

## 🐛 Fehlerbehebung

### Visualisierung zeigt keine Daten

- Prüfe, ob die JSON-Datei korrekt formatiert ist
- Öffne die Browser-Konsole (F12) für Fehlermeldungen
- Stelle sicher, dass die JSON-Datei die Felder `workflow_logs` und `agent_decisions` enthält

### Live-Modus funktioniert nicht

- Stelle sicher, dass die JSON-Datei als `agent_data.json` im gleichen Ordner gespeichert ist
- Prüfe die Browser-Konsole auf CORS-Fehler
- Verwende stattdessen den manuellen "JSON laden" Button

### Nodes werden nicht angezeigt

- Prüfe, ob vis-network korrekt geladen wurde (Netzwerk-Tab im Browser)
- Stelle sicher, dass JavaScript aktiviert ist
- Versuche einen Hard-Refresh (Strg+F5)

## 📝 Lizenz

Diese Visualisierung ist Teil des DORA-Szenariengenerator-Projekts.

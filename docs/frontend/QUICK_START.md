# CRUX Frontend - Quick Start Guide

## 🚀 Schnellstart

### 1. Backend starten

```bash
# Im Hauptverzeichnis (BA/)
cd /Users/finnheintzann/Desktop/BA

# Virtual Environment aktivieren (falls vorhanden)
source venv/bin/activate

# FastAPI installieren (falls noch nicht installiert)
pip install fastapi "uvicorn[standard]"

# API-Server starten
python api_server.py
```

Backend läuft auf: `http://localhost:8000`

### 2. Frontend starten

```bash
# In neuem Terminal
cd /Users/finnheintzann/Desktop/BA/crux-frontend
npm run dev
```

Frontend läuft auf: `http://localhost:3000`

### 3. Browser öffnen

Öffne `http://localhost:3000` im Browser.

## 📊 Was wird angezeigt?

### Backend-Mode (Standard)
- **Graph-Nodes/Links:** Aus Neo4j Knowledge Graph
- **Szenario-Daten:** Neuestes Szenario aus Forensic Logs
- **Critic-Logs:** Alle Logs für das Szenario

### Demo-Mode (Fallback)
- Falls Backend nicht verfügbar, werden Demo-Daten verwendet
- Toggle in `lib/demo-data.ts`: `DEMO_MODE = false`

## 🔧 Troubleshooting

### Backend nicht erreichbar
- Prüfe ob `api_server.py` läuft
- Prüfe Console-Logs im Browser (F12)
- Frontend fällt automatisch auf Demo-Daten zurück

### Keine Daten angezeigt
- Prüfe Backend-Status im Header (✓ Verbunden / ✗ Offline)
- Prüfe Browser-Console für Fehler
- Prüfe ob Neo4j läuft und Daten enthält

### Graph nicht sichtbar
- Prüfe ob Nodes/Links geladen wurden (Legende zeigt Anzahl)
- Verwende Zoom-Controls zum Zoomen
- Klicke auf "Reset View" Button

## 📝 Nächste Schritte

1. **Szenario generieren:** Verwende Streamlit Dashboard um neue Szenarien zu generieren
2. **Daten aktualisieren:** Frontend lädt automatisch beim Start
3. **Interaktion:** Klicke auf Inject-Cards oder Graph-Nodes für Details


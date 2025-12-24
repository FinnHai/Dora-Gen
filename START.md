# 🚀 CRUX System Start-Anleitung

**Schnellstart für Backend und Frontend**

> 📖 **Für eine vollständige Setup-Anleitung auf einem neuen Computer:** Siehe [README.md](README.md#-setup-anleitung)

---

## Voraussetzungen

- ✅ Python 3.10+ mit Virtual Environment (bereits installiert)
- ✅ Node.js 18+ und npm (bereits installiert)
- ✅ Neo4j läuft (optional für Demo-Mode)
- ✅ OpenAI API Key in `.env` Datei konfiguriert

**⚠️ Falls Sie das System zum ersten Mal einrichten:** Führen Sie zuerst das Setup-Skript aus:
```bash
# macOS/Linux:
./setup.sh

# Windows:
# Führen Sie die Schritte in README.md manuell aus
```

---

## 1. Backend starten

### Schritt 1: Virtual Environment aktivieren

```bash
cd /Users/finnheintzann/Desktop/BA
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows
```

### Schritt 2: Dependencies installieren (falls noch nicht geschehen)

```bash
pip install -r requirements.txt
```

### Schritt 3: API Server starten

```bash
python api_server.py
```

**Erwartete Ausgabe:**
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**Backend läuft jetzt auf:** `http://localhost:8000`

---

## 2. Frontend starten

### Schritt 1: In Frontend-Verzeichnis wechseln

```bash
cd crux-frontend
```

### Schritt 2: Dependencies installieren (falls noch nicht geschehen)

```bash
npm install
```

### Schritt 3: Development Server starten

```bash
npm run dev
```

**Erwartete Ausgabe:**
```
▲ Next.js 16.1.0 (Turbopack)
- Local:         http://localhost:3000
- Network:       http://192.168.0.87:3000
✓ Ready in XXXXms
```

**Frontend läuft jetzt auf:** `http://localhost:3000`

---

## 3. System verwenden

### Normal Mode (3 Spalten)
- Öffne `http://localhost:3000` im Browser
- Sieh dir die drei Panels an:
  - **Panel A**: Scenario Composer (30%)
  - **Panel B**: Digital Twin Graph (50%)
  - **Panel C**: Forensic Trace (20%)

### Transparency Mode (4 Spalten)
- Klicke auf **"🔬 Show Transparency"** im Header
- Sieh dir die erweiterten Panels an:
  - **Panel A**: Scenario Composer (25%)
  - **Panel B**: Digital Twin Graph (35%)
  - **Panel C**: Critic Validation (20%) ← **NEU**
  - **Panel D**: Workflow & Forensic Trace (20%) ← **NEU**

### Demo-Mode aktivieren
- Im Code: `DEMO_MODE = true` in `crux-frontend/lib/demo-data.ts`
- Klicke auf **"▶ Play Demo"** im Header
- Sieh dir die automatische Demo-Animation

---

## 4. Troubleshooting

### Backend startet nicht

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`

**Lösung:**
```bash
pip install fastapi "uvicorn[standard]"
```

### Frontend zeigt CSS-Fehler

**Problem:** `@import rules must precede all rules`

**Lösung:** Die `@import` Regeln wurden bereits entfernt. Falls der Fehler weiterhin auftritt:
```bash
cd crux-frontend
rm -rf .next node_modules/.cache .turbo
npm run dev
```

### Backend nicht erreichbar

**Problem:** Frontend zeigt "Backend Offline"

**Lösung:**
1. Prüfe ob Backend läuft: `curl http://localhost:8000/docs`
2. Prüfe CORS-Einstellungen in `api_server.py`
3. Verwende Demo-Mode als Fallback

### Neo4j-Verbindungsfehler

**Problem:** `Neo4j connection failed`

**Lösung:**
- Demo-Mode funktioniert ohne Neo4j
- Für Backend-Mode: Neo4j starten und Credentials in `.env` prüfen

---

## 5. Wichtige URLs

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **API Health:** http://localhost:8000/health

---

## 6. Entwicklung

### Backend neu starten
```bash
# Terminal 1
cd /Users/finnheintzann/Desktop/BA
source venv/bin/activate
python api_server.py
```

### Frontend neu starten
```bash
# Terminal 2
cd crux-frontend
npm run dev
```

### Beide gleichzeitig
```bash
# Terminal 1: Backend
cd /Users/finnheintzann/Desktop/BA && source venv/bin/activate && python api_server.py

# Terminal 2: Frontend
cd crux-frontend && npm run dev
```

---

## 7. Features testen

### Critic Validation Panel
1. Transparency Mode aktivieren
2. Einen Inject im Scenario Composer auswählen
3. Panel C zeigt:
   - Validierungsschritte
   - Wissenschaftliche Metriken
   - Statistische Signifikanz
   - Fehler & Warnungen

### Workflow Visualization
1. Transparency Mode aktivieren
2. Panel D zeigt:
   - Alle Workflow-Nodes
   - Status-Indikatoren
   - Performance-Metriken

### Demo Flow
1. Demo-Mode aktivieren (`DEMO_MODE = true`)
2. "▶ Play Demo" klicken
3. Sieh dir die automatische Animation an

---

**Viel Erfolg! 🎉**






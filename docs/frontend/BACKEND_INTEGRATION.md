# Backend-Integration - Frontend ↔ Backend Verbindung

## ✅ Implementiert

### 1. API-Server Erweiterungen (`api_server.py`)

**Neue/Verbesserte Endpoints:**

#### `GET /api/graph/nodes`
- Holt alle Nodes aus Neo4j Knowledge Graph
- Verwendet `get_current_state()` für vollständige Entity-Daten
- Mappt Neo4j-Entities zu Frontend-Format

#### `GET /api/graph/links`
- Holt alle Relationships aus Neo4j
- Extrahiert Verbindungen aus Entity-Beziehungen
- Mappt zu Frontend Link-Format

#### `GET /api/scenario/latest`
- **NEU:** Holt das neueste Szenario aus Forensic Logs
- Parst `forensic_trace.jsonl` für Szenario-IDs
- Rekonstruiert Injects aus Log-Daten
- Gibt `scenario_id` und `injects` zurück

#### `GET /api/scenario/{scenario_id}/logs`
- Verbessert: Parst Forensic Logs korrekt
- Extrahiert Validation-Details (errors, warnings)
- Formatiert Messages für Frontend
- Sortiert nach Timestamp

### 2. Frontend API Client (`lib/api.ts`)

**Neue API-Klasse:**
- `CruxAPI` - Zentralisierter API-Client
- Methoden:
  - `fetchGraphNodes()` - Lädt Graph-Nodes
  - `fetchGraphLinks()` - Lädt Graph-Links
  - `fetchLatestScenario()` - Lädt neuestes Szenario
  - `fetchScenarioLogs()` - Lädt Critic-Logs
  - `generateScenario()` - Generiert neues Szenario

**Features:**
- Error Handling mit Fallbacks
- TypeScript-Typisierung
- Konfigurierbare Base URL (`NEXT_PUBLIC_API_URL`)

### 3. Frontend Integration (`app/page.tsx`)

**Backend-Mode:**
- Lädt Daten beim Start automatisch
- Zeigt Loading-State während Datenladen
- Backend-Status-Anzeige (✓ Verbunden / ✗ Offline)
- Fallback zu Demo-Daten wenn Backend nicht verfügbar

**Datenfluss:**
1. **Graph-Daten:** Nodes + Links vom Backend
2. **Szenario-Daten:** Neuestes Szenario mit Injects
3. **Logs:** Critic-Logs für das Szenario

### 4. Demo-Mode Toggle

**Konfiguration:** `lib/demo-data.ts`
```typescript
export const DEMO_MODE = false; // false = Backend verwenden
```

**Verhalten:**
- `DEMO_MODE = true`: Verwendet hardcoded Demo-Daten
- `DEMO_MODE = false`: Lädt Daten vom Backend

---

## 🔧 Setup & Verwendung

### Backend starten:

```bash
# Im Hauptverzeichnis
python api_server.py
```

Backend läuft auf: `http://localhost:8000`

### Frontend starten:

```bash
cd crux-frontend
npm run dev
```

Frontend läuft auf: `http://localhost:3000`

### Environment Variables (Optional):

Erstelle `.env.local` im `crux-frontend` Verzeichnis:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📊 Datenfluss

```
┌─────────────────┐
│  Neo4j Graph    │
│  (Knowledge DB) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI Server │
│  (api_server.py)│
└────────┬────────┘
         │ REST API
         ▼
┌─────────────────┐
│  Next.js Frontend│
│  (crux-frontend) │
└─────────────────┘
```

### Datenquellen:

1. **Graph Nodes/Links:** Neo4j Database
2. **Szenarien/Injects:** Forensic Logs (`logs/forensic/forensic_trace.jsonl`)
3. **Critic Logs:** Forensic Logs (gleiche Datei)

---

## 🐛 Troubleshooting

### Backend nicht erreichbar:
- Prüfe ob `api_server.py` läuft
- Prüfe CORS-Einstellungen
- Prüfe Neo4j-Verbindung
- Frontend fällt automatisch auf Demo-Daten zurück

### Keine Graph-Daten:
- Prüfe Neo4j-Verbindung
- Prüfe ob `get_current_state()` Daten zurückgibt
- Prüfe Console-Logs im Browser

### Keine Szenario-Daten:
- Prüfe ob `forensic_trace.jsonl` existiert
- Prüfe Log-Format (JSONL)
- Prüfe ob Szenario-IDs vorhanden sind

---

## 📝 Nächste Schritte

### Verbesserungen:
1. **WebSocket-Support:** Live-Updates während Szenario-Generierung
2. **Besseres Error-Handling:** Detaillierte Fehlermeldungen
3. **Caching:** Reduziere API-Calls
4. **Polling:** Automatisches Aktualisieren der Daten

### Features:
1. **Szenario-Generierung:** Button zum Generieren neuer Szenarien
2. **Refresh-Button:** Manuelles Aktualisieren der Daten
3. **Szenario-Auswahl:** Dropdown für verschiedene Szenarien

---

**Status:** ✅ **Backend-Integration funktionsfähig**

Das Frontend lädt jetzt automatisch echte Daten vom Backend, wenn verfügbar!


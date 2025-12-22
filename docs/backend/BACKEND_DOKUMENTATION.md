# CRUX Backend & Frontend Integration - Dokumentation

## Übersicht

Diese Dokumentation beschreibt alle implementierten Backend- und Frontend-Features, gerankt nach Wichtigkeit für die Bachelorarbeit.

---

## 🔴 KRITISCH - Core Backend Features

### 1. FastAPI REST API Server (`api_server.py`)

**Priorität: ⭐⭐⭐⭐⭐ (KRITISCH)**

**Beschreibung:**
- REST API Server für Frontend-Integration
- Basis für alle Backend-Kommunikation
- CORS-enabled für Frontend-Zugriff

**Endpoints:**
- `GET /` - Health Check
- `GET /api/graph/nodes` - Graph-Nodes aus Neo4j
- `GET /api/graph/links` - Graph-Links aus Neo4j
- `GET /api/scenario/latest` - Neuestes Szenario
- `GET /api/scenario/{scenario_id}/logs` - Critic-Logs für Szenario
- `POST /api/scenario/generate` - Neues Szenario generieren

**Technologie:**
- FastAPI 0.125.0
- Uvicorn (ASGI Server)
- Port: 8000

**Status:** ✅ Implementiert & Lauffähig

---

### 2. Neo4j Knowledge Graph Integration

**Priorität: ⭐⭐⭐⭐⭐ (KRITISCH)**

**Beschreibung:**
- Direkte Abfrage des Knowledge Graphs
- Extraktion von Nodes (Assets) und Links (Relationships)
- Mapping zu Frontend-Format

**Features:**
- `get_current_state()` - Aktueller Systemzustand
- Entity-Typ-Mapping (Server, Database, Network, Workstation)
- Status-Mapping (online, offline, compromised, degraded)

**Datenstruktur:**
```python
GraphNode {
  id: str,
  label: str,
  type: 'server' | 'database' | 'network' | 'workstation',
  status: 'online' | 'offline' | 'compromised' | 'degraded'
}
```

**Status:** ✅ Implementiert

---

### 3. Forensic Logs Parser (`api_server.py`)

**Priorität: ⭐⭐⭐⭐⭐ (KRITISCH)**

**Beschreibung:**
- Parsing von `logs/forensic/forensic_trace.jsonl`
- Extraktion von Szenario-Daten, Injects und Critic-Logs
- Refinement-History-Extraktion

**Features:**
- JSONL-Line-by-Line Parsing
- Szenario-ID-Extraktion
- Inject-Status-Mapping (accept/reject)
- Refinement-Count-Tracking

**Log-Format:**
```json
{
  "timestamp": "2025-12-19T19:14:56.172558",
  "scenario_id": "SCEN-D677B574",
  "event_type": "CRITIC",
  "iteration": 0,
  "refine_count": 0,
  "data": {
    "inject_id": "INJ-001",
    "validation": {...},
    "decision": "accept"
  }
}
```

**Status:** ✅ Implementiert

---

## 🟠 WICHTIG - Szenario-Management

### 4. Szenario-Endpoints (`/api/scenario/*`)

**Priorität: ⭐⭐⭐⭐ (WICHTIG)**

**Beschreibung:**
- Verwaltung von Szenarien
- Neuestes Szenario finden
- Szenario-spezifische Logs abrufen

**Endpoints:**

#### `GET /api/scenario/latest`
- Findet neuestes Szenario aus Forensic Logs
- Extrahiert alle Injects für das Szenario
- Fallback zu Neo4j wenn verfügbar

**Response:**
```json
{
  "scenario_id": "SCEN-D677B574",
  "injects": [...],
  "logs": [...]
}
```

#### `GET /api/scenario/{scenario_id}/logs`
- Alle Critic-Logs für ein Szenario
- Gefiltert nach Szenario-ID
- Sortiert nach Timestamp

**Status:** ✅ Implementiert

---

### 5. Graph-Daten-Endpoints (`/api/graph/*`)

**Priorität: ⭐⭐⭐⭐ (WICHTIG)**

**Beschreibung:**
- Bereitstellung von Graph-Daten für Frontend-Visualisierung
- Direkte Neo4j-Abfragen
- Format-Konvertierung für React Force Graph

**Endpoints:**

#### `GET /api/graph/nodes`
- Alle Nodes aus Neo4j
- Typ- und Status-Mapping
- Deduplizierung

#### `GET /api/graph/links`
- Alle Relationships aus Neo4j
- Link-Typ-Extraktion
- Source/Target-Mapping

**Status:** ✅ Implementiert

---

## 🟡 MITTEL - Frontend-Integration

### 6. Frontend API Client (`lib/api.ts`)

**Priorität: ⭐⭐⭐ (MITTEL)**

**Beschreibung:**
- TypeScript-Client für Backend-Kommunikation
- Type-safe API-Calls
- Error-Handling

**Features:**
- `fetchGraphNodes()` - Graph-Nodes laden
- `fetchGraphLinks()` - Graph-Links laden
- `fetchLatestScenario()` - Neuestes Szenario
- `fetchScenarioLogs()` - Critic-Logs laden

**Status:** ✅ Implementiert

---

### 7. Demo-Mode mit Echten Daten (`lib/real-data.ts`)

**Priorität: ⭐⭐⭐ (MITTEL)**

**Beschreibung:**
- Statische Daten aus Forensic Logs
- Funktioniert ohne Backend-Verbindung
- Perfekt für Präsentationen

**Daten:**
- 6 Injects (INJ-001 bis INJ-006)
- 7 Critic-Logs
- 13 Graph-Nodes
- 11 Graph-Links

**Szenario:** `SCEN-D677B574`

**Toggle:** `DEMO_MODE` in `demo-data.ts`

**Status:** ✅ Implementiert

---

### 8. Zustand State Management (`lib/store.ts`)

**Priorität: ⭐⭐⭐ (MITTEL)**

**Beschreibung:**
- Globaler State für Frontend
- Zustand Store (Zustand Library)
- Reaktive Updates

**State:**
- `injects` - Liste aller Injects
- `graphData` - Graph-Nodes und Links
- `selectedInjectId` - Aktuell ausgewähltes Inject
- `hoveredAsset` - Hovered Asset für Semantic Hovering
- `criticLogs` - Critic-Logs

**Status:** ✅ Implementiert

---

## 🟢 NICE-TO-HAVE - Zusätzliche Features

### 9. Error-Handling & Fallbacks

**Priorität: ⭐⭐ (NICE-TO-HAVE)**

**Beschreibung:**
- Graceful Degradation
- Fallback zu Demo-Daten bei Backend-Fehler
- Loading-States

**Features:**
- Backend-Status-Anzeige
- Automatischer Fallback
- Error-Logging

**Status:** ✅ Implementiert

---

### 10. CORS-Konfiguration

**Priorität: ⭐⭐ (NICE-TO-HAVE)**

**Beschreibung:**
- Cross-Origin Resource Sharing
- Erlaubt Frontend-Zugriff von `localhost:3000`

**Konfiguration:**
```python
CORSMiddleware(
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Status:** ✅ Implementiert

---

## 🔄 Lazy Initialization Pattern

**Priorität: ⭐⭐⭐ (MITTEL)**

**Beschreibung:**
- Neo4j Client wird erst bei Bedarf initialisiert
- Workflow wird erst bei Bedarf erstellt
- Spart Ressourcen bei Startup

**Implementierung:**
```python
def get_neo4j_client():
    global neo4j_client
    if neo4j_client is None:
        neo4j_client = Neo4jClient()
        neo4j_client.connect()
    return neo4j_client
```

**Status:** ✅ Implementiert

---

## 📊 Datenfluss-Diagramm

```
┌─────────────────────────────────────────┐
│      Next.js Frontend (Port 3000)       │
│  ┌───────────────────────────────────┐ │
│  │  Components:                      │ │
│  │  - ScenarioComposer               │ │
│  │  - DigitalTwinGraph               │ │
│  │  - ForensicTrace                 │ │
│  └──────────────┬────────────────────┘ │
│                 │                       │
│  ┌──────────────▼────────────────────┐ │
│  │  API Client (lib/api.ts)          │ │
│  │  - fetchGraphNodes()              │ │
│  │  - fetchGraphLinks()              │ │
│  │  - fetchLatestScenario()          │ │
│  │  - fetchScenarioLogs()            │ │
│  └──────────────┬────────────────────┘ │
└─────────────────┼───────────────────────┘
                  │ HTTP REST API
                  │ (JSON)
                  ▼
┌─────────────────────────────────────────┐
│    FastAPI Server (Port 8000)            │
│  ┌───────────────────────────────────┐ │
│  │  Endpoints:                       │ │
│  │  GET  /api/graph/nodes            │ │
│  │  GET  /api/graph/links            │ │
│  │  GET  /api/scenario/latest        │ │
│  │  GET  /api/scenario/{id}/logs     │ │
│  │  POST /api/scenario/generate      │ │
│  └──────────────┬────────────────────┘ │
└─────────────────┼───────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌──────────────┐   ┌──────────────────┐
│   Neo4j      │   │  Forensic Logs    │
│   Graph DB   │   │  (JSONL Format)   │
│              │   │                   │
│  - Nodes     │   │  - Critic Events  │
│  - Links     │   │  - Validations    │
│  - Status    │   │  - Refinements    │
└──────────────┘   └──────────────────┘
```

## 🔀 Fallback-Strategie

**Priorität: ⭐⭐⭐ (MITTEL)**

**Beschreibung:**
- Neo4j-First: Versucht zuerst Daten aus Neo4j zu holen
- Fallback zu Forensic Logs wenn Neo4j nicht verfügbar
- Finaler Fallback zu Demo-Daten im Frontend

**Flow:**
```
1. Versuche Neo4j → Erfolg ✅
2. Falls Fehler → Forensic Logs → Erfolg ✅
3. Falls Fehler → Demo-Daten (Frontend) → Erfolg ✅
```

---

## 🚀 Setup & Installation

### Backend Setup

```bash
# 1. Virtual Environment aktivieren
source venv/bin/activate

# 2. FastAPI installieren
pip install fastapi "uvicorn[standard]"

# 3. API-Server starten
python api_server.py
```

**Backend läuft auf:** `http://localhost:8000`

### Frontend Setup

```bash
# 1. In Frontend-Verzeichnis wechseln
cd crux-frontend

# 2. Dev-Server starten
npm run dev
```

**Frontend läuft auf:** `http://localhost:3000`

---

## 🔧 Konfiguration

### Demo-Mode Toggle

**Datei:** `crux-frontend/lib/demo-data.ts`

```typescript
export const DEMO_MODE = false; // false = Backend, true = Statische Daten
```

### Backend-URL

**Datei:** `crux-frontend/lib/api.ts`

```typescript
const API_BASE_URL = 'http://localhost:8000';
```

---

## 📝 API-Dokumentation

### Swagger UI

Nach dem Start des Backends:
- **URL:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## 🐛 Bekannte Probleme

1. **Datetime Serialization**
   - Problem: `Object of type datetime is not JSON serializable`
   - Workaround: Timestamp als String speichern
   - Status: ⚠️ Teilweise behoben

2. **Neo4j Connection**
   - Problem: Verbindung kann fehlschlagen
   - Fallback: Forensic Logs werden verwendet
   - Status: ✅ Mit Fallback gelöst

---

## 📈 Performance

- **Backend Response Time:** ~100-500ms
- **Graph-Daten:** ~30 Nodes, ~20 Links
- **Forensic Logs:** ~148 Zeilen (JSONL)

---

## 🔐 Sicherheit

- CORS auf `localhost:3000` beschränkt
- Keine Authentifizierung (Development)
- Keine Rate-Limiting (Development)

---

## 📚 Technologie-Stack

### Backend
- **FastAPI** 0.125.0
- **Uvicorn** 0.38.0
- **Neo4j** 5.15.0+
- **Python** 3.10+

### Frontend
- **Next.js** 16.1.0
- **React** 19.x
- **TypeScript** 5.x
- **Zustand** (State Management)
- **React Force Graph** (Graph-Visualisierung)

---

## ✅ Checkliste - Implementierungsstatus

- [x] FastAPI Server Setup
- [x] Neo4j Integration
- [x] Forensic Logs Parser
- [x] Graph-Endpoints
- [x] Szenario-Endpoints
- [x] Frontend API Client
- [x] Demo-Mode mit echten Daten
- [x] Error-Handling & Fallbacks
- [x] CORS-Konfiguration
- [x] State Management
- [ ] WebSocket für Live-Updates (TODO)
- [ ] Authentifizierung (TODO)
- [ ] Rate-Limiting (TODO)

---

## 🎯 Zusammenfassung

**Kritische Features (Muss-Have):**
1. FastAPI REST API Server
2. Neo4j Knowledge Graph Integration
3. Forensic Logs Parser

**Wichtige Features (Soll-Have):**
4. Szenario-Management-Endpoints
5. Graph-Daten-Endpoints

**Mittlere Features (Kann-Have):**
6. Frontend API Client
7. Demo-Mode mit echten Daten
8. State Management

**Nice-to-Have Features:**
9. Error-Handling & Fallbacks
10. CORS-Konfiguration

---

**Letzte Aktualisierung:** 2025-12-20
**Version:** 1.0.0


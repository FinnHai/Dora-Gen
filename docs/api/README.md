# API & Integration - Wissenschaftliche Dokumentation

**Version:** 1.0.0  
**Letzte Aktualisierung:** 2025-12-20  
**Status:** Produktiv

---

## Abstract

Die API-Schicht der CRUX-Plattform stellt eine REST-basierte Schnittstelle zwischen Frontend und Backend bereit. Die Implementierung basiert auf FastAPI (Python) und ermöglicht den Zugriff auf Neo4j-Daten, Szenario-Generierung und Forensic-Logs.

---

## Inhaltsverzeichnis

### 1. [Backend Connection](BACKEND_CONNECTION_COMPLETE.md)
   - 1.1 FastAPI REST API Server
   - 1.2 API-Endpunkte
   - 1.3 Datenquellen
   - 1.4 Frontend-Integration

---

## API-Architektur

### Komponenten-Übersicht

```
API Layer
├── FastAPI Server
│   ├── REST Endpoints
│   ├── CORS Configuration
│   └── Error Handling
├── Data Sources
│   ├── Neo4j Client
│   ├── Forensic Logger
│   └── Scenario Workflow
└── Frontend Client
    └── CruxAPI (TypeScript)
```

### Datenfluss

```
Frontend Request
    ↓
FastAPI Endpoint
    ↓
Data Source (Neo4j / Logs / Workflow)
    ↓
Response (JSON)
    ↓
Frontend Update
```

---

## API-Endpunkte

### Graph-Daten

#### `GET /api/graph/nodes`
**Beschreibung:** Ruft alle Graph-Nodes aus Neo4j ab.

**Response:**
```json
{
  "nodes": [
    {
      "id": "SRV-001",
      "type": "Server",
      "name": "SRV-001",
      "status": "online",
      "criticality": "standard"
    }
  ]
}
```

#### `GET /api/graph/links`
**Beschreibung:** Ruft alle Graph-Links (Relationships) aus Neo4j ab.

**Response:**
```json
{
  "links": [
    {
      "source": "SRV-001",
      "target": "SRV-002",
      "type": "RUNS_ON"
    }
  ]
}
```

### Szenario-Management

#### `GET /api/scenario/latest`
**Beschreibung:** Ruft das neueste Szenario mit zugehörigen Injects und Logs ab.

**Response:**
```json
{
  "scenario_id": "SCEN-ABC123",
  "injects": [...],
  "logs": [...]
}
```

#### `GET /api/scenario/{scenario_id}/logs`
**Beschreibung:** Ruft Critic-Logs für ein spezifisches Szenario ab.

**Parameters:**
- `scenario_id` (path): Szenario-ID

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2025-12-20T10:33:52",
      "event_type": "CRITIC",
      "inject_id": "INJ-001",
      "message": "..."
    }
  ]
}
```

#### `POST /api/scenario/generate`
**Beschreibung:** Generiert ein neues Szenario.

**Request Body:**
```json
{
  "scenario_type": "RANSOMWARE_DOUBLE_EXTORTION",
  "max_iterations": 10
}
```

**Response:**
```json
{
  "scenario_id": "SCEN-ABC123",
  "status": "completed",
  "injects": [...]
}
```

---

## Datenquellen

### Neo4j Knowledge Graph

**Verwendung:**
- Graph-Nodes (Assets, Services)
- Graph-Links (Relationships, Dependencies)
- Entity-Status (online, compromised, etc.)

**Client:** `Neo4jClient` (Python)

### Forensic Logs

**Verwendung:**
- Critic-Validierungen
- Refinement-History
- Workflow-Logs

**Format:** JSONL (`logs/forensic/forensic_trace.jsonl`)

### Scenario Workflow

**Verwendung:**
- Szenario-Generierung
- Inject-Erstellung
- State Management

**Client:** `ScenarioWorkflow` (LangGraph)

---

## Frontend-Integration

### CruxAPI Client

**Implementierung:** TypeScript (`crux-frontend/lib/api.ts`)

**Methoden:**
- `getGraphNodes()` - Graph-Nodes abrufen
- `getGraphLinks()` - Graph-Links abrufen
- `getLatestScenario()` - Neuestes Szenario abrufen
- `getScenarioLogs(scenario_id)` - Logs abrufen

### Error-Handling

**Strategie:**
- Retry-Logik bei Netzwerk-Fehlern
- Fallback zu Demo-Daten
- User-freundliche Fehlermeldungen

---

## CORS-Konfiguration

**Aktuelle Konfiguration:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Dokumentations-Priorität

### 🔴 Kritisch (Muss-Have)

1. **[Backend Connection](BACKEND_CONNECTION_COMPLETE.md)** ⭐⭐⭐⭐⭐
   - FastAPI REST API Server
   - API-Endpunkte
   - Frontend-Integration

---

## Schnellzugriff

### API verstehen
→ [Backend Connection](BACKEND_CONNECTION_COMPLETE.md)

### Backend-Features
→ [Backend-Dokumentation](../backend/BACKEND_DOKUMENTATION.md)

---

## Referenzen

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Neo4j Python Driver: https://neo4j.com/docs/python-manual/current/
- REST API Best Practices: https://restfulapi.net/

---

**Letzte Aktualisierung:** 2025-12-20  
**Maintainer:** API Development Team

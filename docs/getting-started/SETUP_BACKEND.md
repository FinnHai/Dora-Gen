# Backend Setup - FastAPI Server

## Installation

### 1. FastAPI installieren

```bash
# Im Hauptverzeichnis (BA/)
source venv/bin/activate  # Falls Virtual Environment verwendet wird
pip install fastapi "uvicorn[standard]"
```

Oder falls `pip` nicht verfügbar:
```bash
python3 -m pip install fastapi "uvicorn[standard]"
```

### 2. API-Server starten

```bash
cd /Users/finnheintzann/Desktop/BA
python api_server.py
```

Der Server läuft dann auf: `http://localhost:8000`

### 3. API-Dokumentation

Nach dem Start ist die interaktive API-Dokumentation verfügbar unter:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Verfügbare Endpoints

### `GET /`
Health Check

### `GET /api/graph/nodes`
Holt alle Nodes aus Neo4j Knowledge Graph

### `GET /api/graph/links`
Holt alle Relationships aus Neo4j

### `GET /api/scenario/latest`
Holt das neueste Szenario mit allen Injects aus Forensic Logs

### `GET /api/scenario/{scenario_id}/logs`
Holt Critic-Logs für ein spezifisches Szenario

### `POST /api/scenario/generate`
Generiert ein neues Szenario

**Request Body:**
```json
{
  "scenario_type": "ransomware_double_extortion",
  "num_injects": 10
}
```

## Troubleshooting

### FastAPI nicht gefunden
```bash
pip install fastapi uvicorn[standard]
```

### Neo4j-Verbindungsfehler
- Prüfe ob Neo4j läuft: `neo4j status`
- Prüfe Umgebungsvariablen: `.env` Datei mit `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`

### CORS-Fehler
- Prüfe ob Frontend auf `http://localhost:3000` läuft
- CORS ist bereits für `localhost:3000` und `localhost:3001` konfiguriert

## Frontend-Integration

Das Frontend lädt automatisch Daten vom Backend, wenn:
1. `DEMO_MODE = false` in `crux-frontend/lib/demo-data.ts`
2. Backend läuft auf `http://localhost:8000`
3. Frontend läuft auf `http://localhost:3000`


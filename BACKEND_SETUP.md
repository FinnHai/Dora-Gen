# 🚀 Backend Setup für CRUX Frontend

## Voraussetzungen

1. **Python Virtual Environment aktiviert**
```bash
cd /Users/finnheintzann/Desktop/BA
source venv/bin/activate
```

2. **FastAPI installieren**
```bash
pip install fastapi "uvicorn[standard]"
```

3. **Neo4j läuft**
- Neo4j sollte auf `localhost:7687` laufen
- Credentials in `.env` Datei:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

## Backend starten

```bash
cd /Users/finnheintzann/Desktop/BA
source venv/bin/activate
python api_server.py
```

Der Server läuft dann auf: `http://localhost:8000`

## Frontend starten

```bash
cd crux-frontend
npm run dev
```

Das Frontend läuft dann auf: `http://localhost:3000`

## API Endpoints

- `GET /api/graph/nodes` - Graph Nodes aus Neo4j
- `GET /api/graph/links` - Graph Links aus Neo4j
- `GET /api/scenario/latest` - Neuestes Szenario mit Injects
- `GET /api/scenario/{scenario_id}/logs` - Critic Logs für Szenario
- `POST /api/scenario/generate` - Neues Szenario generieren

## Troubleshooting

### Backend zeigt "Offline"
1. Prüfe ob `api_server.py` läuft
2. Prüfe ob Neo4j läuft
3. Prüfe `.env` Datei für Credentials
4. Prüfe Browser Console für CORS-Fehler

### Keine Graph-Daten
1. Prüfe ob Neo4j Daten enthält: `MATCH (n) RETURN n LIMIT 10`
2. Prüfe Backend Logs für Fehler
3. Verwende "Refresh" Button im Frontend

### Keine Szenario-Daten
1. Generiere ein neues Szenario über Dashboard
2. Prüfe `logs/forensic/forensic_trace.jsonl`
3. Prüfe ob Szenario in Neo4j gespeichert ist






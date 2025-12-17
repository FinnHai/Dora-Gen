# 🚀 Schnellstart-Anleitung

## Schritt 1: Python Virtual Environment erstellen

```bash
# Virtual Environment erstellen
python3 -m venv venv

# Aktivieren (macOS/Linux)
source venv/bin/activate

# Aktivieren (Windows)
venv\Scripts\activate
```

## Schritt 2: Dependencies installieren

```bash
pip install -r requirements.txt
```

## Schritt 3: Umgebungsvariablen konfigurieren

```bash
# .env Datei erstellen
cp .env.example .env
```

Dann öffne `.env` und trage deine Werte ein:

```env
# Neo4j (optional für jetzt - kann später konfiguriert werden)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=dein_passwort_hier

# OpenAI (wird später für LLM benötigt)
OPENAI_API_KEY=dein_api_key_hier
```

## Schritt 4: Setup testen

```bash
python tests/test_setup.py
```

Dieser Test prüft:
- ✅ Pydantic-Modelle funktionieren
- ✅ Neo4j-Verbindung (falls konfiguriert)

## Schritt 5: Neo4j starten (optional)

Falls du Neo4j testen möchtest:

```bash
# Mit Docker
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

Dann in `.env` eintragen:
```
NEO4J_PASSWORD=password
```

## ✅ Fertig!

Wenn `test_setup.py` erfolgreich durchläuft, ist die Grundstruktur bereit.

## Nächste Entwicklungsschritte

1. **LangGraph Workflow** implementieren
2. **Agenten** entwickeln (Manager, Generator, Critic, Intel)
3. **ChromaDB** für RAG einrichten
4. **Streamlit Frontend** erstellen


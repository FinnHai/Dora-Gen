# Quick Start Guide

## 🚀 In 5 Minuten zum ersten Szenario

### Schritt 1: Dependencies installieren

```bash
# Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Install
pip install -r requirements.txt
```

### Schritt 2: Umgebung konfigurieren

Erstelle `.env` Datei:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
OPENAI_API_KEY=your_api_key
```

### Schritt 3: Neo4j starten

```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:latest
```

### Schritt 4: Setup testen

```bash
python check_setup.py
```

### Schritt 5: App starten

**Option A: DORA Scenario Generator**
```bash
streamlit run app.py
```

**Option B: Crisis Cockpit (Thesis-Evaluation)**
```bash
streamlit run crisis_cockpit.py
```

### Schritt 6: Erste Szenario generieren

1. Öffne Browser: http://localhost:8501
2. Wähle Scenario Type
3. Setze Anzahl Injects (z.B. 5)
4. Klicke "Generate Scenario"
5. Warte auf Ergebnisse

**Fertig! 🎉**

---

## 📚 Weitere Ressourcen

- **Vollständige Anleitung**: [ANWENDUNGSANLEITUNG.md](ANWENDUNGSANLEITUNG.md)
- **Architektur**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Projekt-Status**: [PROJECT_STATUS.md](PROJECT_STATUS.md)


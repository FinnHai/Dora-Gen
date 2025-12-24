# Quick Start Guide

## 🚀 In 5 Minuten zum ersten Szenario

> 📖 **Für eine vollständige Setup-Anleitung:** Siehe [README.md](../../README.md#-setup-anleitung)

### Automatisches Setup (Empfohlen)

**macOS/Linux:**
```bash
./setup.sh
```

**Windows:**
```bash
setup.bat
```

Das Setup-Skript installiert automatisch alle Dependencies und konfiguriert die Umgebung.

---

### Manuelles Setup

#### Schritt 1: Dependencies installieren

```bash
# Virtual Environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install
pip install -r requirements.txt
```

#### Schritt 2: Umgebung konfigurieren

```bash
# Kopiere .env.example zu .env
cp .env.example .env

# Bearbeite .env und füge deinen OPENAI_API_KEY ein
nano .env  # oder code .env
```

**Wichtig:** Füge deinen OpenAI API Key in `.env` ein:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

#### Schritt 3: Neo4j starten

```bash
# Mit dem bereitgestellten Skript
./scripts/start_neo4j.sh

# Oder manuell mit Docker
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

#### Schritt 4: Setup testen

```bash
python scripts/check_setup.py
```

---

### System starten

#### Option A: Next.js Frontend (Empfohlen)

**Terminal 1 - Backend:**
```bash
source venv/bin/activate  # Windows: venv\Scripts\activate
python api_server.py
```

**Terminal 2 - Frontend:**
```bash
cd crux-frontend
npm install  # Falls noch nicht installiert
npm run dev
```

**Öffne Browser:** http://localhost:3000

#### Option B: Streamlit Frontend

**DORA Scenario Generator:**
```bash
source venv/bin/activate
streamlit run app.py
```

**Crisis Cockpit (Thesis-Evaluation):**
```bash
source venv/bin/activate
streamlit run frontend/crisis_cockpit.py
```

**Öffne Browser:** http://localhost:8501

---

### Erste Szenario generieren

1. Öffne Browser: http://localhost:3000 (Next.js) oder http://localhost:8501 (Streamlit)
2. Wähle Scenario Type (z.B. "Ransomware Double Extortion")
3. Setze Anzahl Injects (z.B. 5)
4. Klicke "Generate Scenario"
5. Warte auf Ergebnisse

**Fertig! 🎉**

---

---

## 📚 Weitere Ressourcen

- **Vollständige Setup-Anleitung**: [README.md](../../README.md#-setup-anleitung)
- **Start-Anleitung**: [START.md](../../START.md)
- **Vollständige Anleitung**: [Anwendungsanleitung](../user-guides/ANWENDUNGSANLEITUNG.md)
- **Architektur**: [Architektur-Dokumentation](../architecture/ARCHITECTURE.md)
- **Projekt-Status**: [PROJECT_STATUS.md](../../PROJECT_STATUS.md)

---

## ⚠️ Troubleshooting

**Problem:** Backend startet nicht
- Prüfe ob Virtual Environment aktiviert ist
- Prüfe ob alle Dependencies installiert sind: `pip install -r requirements.txt`

**Problem:** Frontend zeigt "Backend Offline"
- Prüfe ob Backend läuft: `curl http://localhost:8000/health`
- Prüfe Browser-Konsole (F12) auf Fehler

**Problem:** Neo4j-Verbindungsfehler
- Prüfe ob Docker läuft: `docker ps`
- Starte Neo4j neu: `./scripts/start_neo4j.sh`

Für weitere Hilfe siehe [README.md Troubleshooting](../../README.md#troubleshooting)


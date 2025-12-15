# 🚀 GitHub Setup Anleitung

## Repository auf GitHub hochladen

### Schritt 1: Git Repository initialisieren (bereits erledigt)

```bash
git init
```

### Schritt 2: Erste Commit erstellen

```bash
# Alle Dateien hinzufügen
git add .

# Commit erstellen
git commit -m "Initial commit: DORA Szenariengenerator MVP"
```

### Schritt 3: GitHub Repository erstellen

1. Gehe zu [GitHub.com](https://github.com)
2. Klicke auf "New repository"
3. Repository-Name: z.B. `dora-scenario-generator` oder `BA-DORA-Szenariengenerator`
4. Beschreibung: "DORA-konformer Szenariengenerator für Krisenmanagement (MVP)"
5. Wähle **Private** oder **Public**
6. **NICHT** "Initialize with README" aktivieren (haben wir schon)
7. Klicke auf "Create repository"

### Schritt 4: GitHub Repository verbinden

```bash
# Ersetze USERNAME und REPO-NAME mit deinen Werten
git remote add origin https://github.com/USERNAME/REPO-NAME.git

# Oder mit SSH (wenn SSH-Keys konfiguriert):
# git remote add origin git@github.com:USERNAME/REPO-NAME.git
```

### Schritt 5: Code hochladen

```bash
# Branch umbenennen (optional, aber empfohlen)
git branch -M main

# Code hochladen
git push -u origin main
```

## ⚠️ Wichtige Hinweise

### Was wird NICHT hochgeladen (dank .gitignore)

- ✅ `venv/` - Virtual Environment
- ✅ `.env` - Umgebungsvariablen (mit sensiblen Daten)
- ✅ `__pycache__/` - Python Cache
- ✅ `chroma_db/` - ChromaDB Datenbank
- ✅ `*.log` - Log-Dateien

### Was wird hochgeladen

- ✅ Alle Python-Dateien
- ✅ Dokumentationen (README.md, STATUS.md, etc.)
- ✅ requirements.txt
- ✅ .gitignore
- ✅ Test-Skripte
- ✅ Shell-Skripte (start_neo4j.sh)

### ⚠️ Sicherheit: .env Datei

Die `.env` Datei enthält:
- **Neo4j Passwort**
- **OpenAI API Key**

Diese wird **NICHT** hochgeladen (dank .gitignore).

**WICHTIG**: Erstelle eine `.env.example` Datei für andere Nutzer (bereits vorhanden).

## 🔄 Weitere Commits

Nach Änderungen:

```bash
# Änderungen hinzufügen
git add .

# Commit erstellen
git commit -m "Beschreibung der Änderungen"

# Hochladen
git push
```

## 📋 Repository-Struktur auf GitHub

Nach dem Upload sollte die Struktur so aussehen:

```
dora-scenario-generator/
├── .gitignore
├── README.md
├── STATUS.md
├── QUICKSTART.md
├── SETUP.md
├── FRONTEND.md
├── DOCUMENTATION.md
├── requirements.txt
├── app.py
├── state_models.py
├── neo4j_client.py
├── start_neo4j.sh
├── agents/
│   ├── __init__.py
│   ├── manager_agent.py
│   ├── generator_agent.py
│   ├── critic_agent.py
│   └── intel_agent.py
├── workflows/
│   ├── __init__.py
│   ├── scenario_workflow.py
│   ├── state_schema.py
│   └── fsm.py
└── utils/
    └── __init__.py
```

## 🎯 GitHub Features nutzen

### Issues
- Bug-Reports
- Feature-Requests
- Fragen

### Releases
- Version-Tags erstellen
- Releases für wichtige Meilensteine

### GitHub Actions (optional)
- Automatische Tests
- CI/CD Pipeline

## 📝 README auf GitHub

Die README.md wird automatisch auf der GitHub-Hauptseite angezeigt. Stelle sicher, dass sie aktuell ist!

## ✅ Checkliste vor dem Upload

- [ ] `.env` ist in `.gitignore`
- [ ] `venv/` ist in `.gitignore`
- [ ] `.env.example` existiert (ohne echte Werte)
- [ ] README.md ist aktuell
- [ ] Alle Dokumentationen sind vorhanden
- [ ] Keine sensiblen Daten in Code-Dateien

## 🔐 Private vs. Public Repository

### Private Repository
- ✅ Nur du (und Collaborators) können es sehen
- ✅ Gut für: Proprietäre Projekte, API Keys
- ⚠️ Kostenlos für: Einzelpersonen (unlimited private repos)

### Public Repository
- ✅ Jeder kann es sehen
- ✅ Gut für: Open Source, Portfolio
- ⚠️ ACHTUNG: Keine API Keys oder Passwörter committen!

**Empfehlung**: Starte mit **Private**, mache später **Public** wenn gewünscht.


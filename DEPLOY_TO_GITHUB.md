# 🚀 Repository auf GitHub hochladen

## Repository-Name: `dora-scenario-generator`

## Schritt-für-Schritt Anleitung

### Schritt 1: GitHub Repository erstellen

1. Gehe zu [github.com](https://github.com) und logge dich ein
2. Klicke auf das **"+"** Symbol oben rechts → **"New repository"**
3. Fülle die Felder aus:
   - **Repository name**: `dora-scenario-generator`
   - **Description**: `DORA-konformer Szenariengenerator für Krisenmanagement (MVP) - Multi-Agenten-System mit LangGraph, Neo4j und OpenAI`
   - **Visibility**: 
     - ✅ **Private** (empfohlen - enthält API Keys in .env.example)
     - Oder **Public** (wenn du es teilen möchtest)
   - ⚠️ **WICHTIG**: **NICHT** "Add a README file" aktivieren (haben wir schon!)
   - ⚠️ **WICHTIG**: **NICHT** "Add .gitignore" aktivieren (haben wir schon!)
   - ⚠️ **WICHTIG**: **NICHT** "Choose a license" aktivieren (kannst du später hinzufügen)
4. Klicke auf **"Create repository"**

### Schritt 2: Repository verbinden

Nach dem Erstellen zeigt GitHub dir Befehle an. Führe diese aus:

```bash
# Wechsle ins Projekt-Verzeichnis
cd /Users/finnheintzann/Desktop/BA

# Ersetze USERNAME mit deinem GitHub-Username
git remote add origin https://github.com/USERNAME/dora-scenario-generator.git

# Branch umbenennen (empfohlen)
git branch -M main

# Code hochladen
git push -u origin main
```

### Schritt 3: Authentifizierung

Beim ersten `git push` wirst du möglicherweise nach Credentials gefragt:

**Option A: Personal Access Token (empfohlen)**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token (classic)"
3. Scopes: `repo` aktivieren
4. Token kopieren und als Passwort verwenden

**Option B: GitHub CLI**
```bash
# Installiere GitHub CLI (falls nicht vorhanden)
brew install gh

# Authentifiziere dich
gh auth login

# Dann normal pushen
git push -u origin main
```

**Option C: SSH (wenn SSH-Keys konfiguriert)**
```bash
# Verwende SSH-URL statt HTTPS
git remote set-url origin git@github.com:USERNAME/dora-scenario-generator.git
git push -u origin main
```

## ✅ Prüfen ob es funktioniert hat

```bash
# Prüfe Remote-URL
git remote -v

# Sollte zeigen:
# origin  https://github.com/USERNAME/dora-scenario-generator.git (fetch)
# origin  https://github.com/USERNAME/dora-scenario-generator.git (push)
```

Dann öffne im Browser: `https://github.com/USERNAME/dora-scenario-generator`

## 📋 Was wird hochgeladen?

### ✅ Wird hochgeladen:
- Alle Python-Dateien
- Alle Dokumentationen (README.md, ARCHITECTURE.md, etc.)
- requirements.txt
- .gitignore
- .env.example (ohne echte Werte)
- Test-Skripte
- Shell-Skripte

### ❌ Wird NICHT hochgeladen (dank .gitignore):
- `.env` (enthält API Keys & Passwörter)
- `venv/` (Virtual Environment)
- `chroma_db/` (Datenbank-Dateien)
- `__pycache__/` (Python Cache)
- `*.log` (Log-Dateien)

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

## 🎯 Repository-URL Format

Nach dem Upload:
- **HTTPS**: `https://github.com/USERNAME/dora-scenario-generator.git`
- **SSH**: `git@github.com:USERNAME/dora-scenario-generator.git`
- **Web**: `https://github.com/USERNAME/dora-scenario-generator`

## ⚠️ Wichtige Hinweise

1. **API Keys**: Die `.env` Datei wird NICHT hochgeladen (sicher!)
2. **Erste Push**: Kann einige Minuten dauern (viele Dateien)
3. **README.md**: Wird automatisch auf der GitHub-Hauptseite angezeigt
4. **Mermaid-Diagramme**: Werden automatisch von GitHub gerendert

## 🎉 Fertig!

Nach erfolgreichem Upload:
- ✅ Code ist auf GitHub
- ✅ Dokumentation ist sichtbar
- ✅ Architektur-Diagramme werden gerendert
- ✅ Andere können das Repository klonen (wenn Public)

Viel Erfolg! 🚀


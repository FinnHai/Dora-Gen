# 🚀 Quick Start Guide

Schnellstart-Anleitung für den DORA-Szenariengenerator.

## ⚡ In 5 Minuten zum ersten Szenario

### Schritt 1: Voraussetzungen prüfen

```bash
# Python 3.10+ installiert?
python3 --version

# Docker installiert? (für Neo4j)
docker --version
```

### Schritt 2: Projekt einrichten

```bash
# Repository klonen/öffnen
cd BA

# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt
```

### Schritt 3: Konfiguration

```bash
# .env Datei erstellen
cp .env.example .env

# .env bearbeiten und eintragen:
# - NEO4J_PASSWORD=dein_passwort
# - OPENAI_API_KEY=dein_api_key
```

### Schritt 4: Neo4j starten

```bash
# Docker starten (falls nicht läuft)
# Dann Neo4j Container starten
./start_neo4j.sh
```

### Schritt 5: Setup testen

```bash
# Prüfe ob alles funktioniert
python check_setup.py
```

### Schritt 6: Frontend starten

```bash
streamlit run app.py
```

### Schritt 7: Erstes Szenario generieren

1. Öffne Browser: `http://localhost:8501`
2. Wähle Szenario-Typ (z.B. "Ransomware Double Extortion")
3. Setze Anzahl Injects auf 3 (für schnellen Test)
4. Klicke auf "🎯 Szenario generieren"
5. Warte ~2-5 Minuten
6. Prüfe Ergebnisse im "Ergebnisse" Tab

## 📚 Weitere Dokumentation

- **README.md**: Vollständige Projekt-Dokumentation
- **STATUS.md**: Was kann das System, was fehlt, wie einsetzen
- **SETUP.md**: Detaillierte Setup-Anleitung
- **FRONTEND.md**: Frontend-Bedienungsanleitung

## 🆘 Häufige Probleme

### Neo4j-Verbindungsfehler
```bash
# Prüfe ob Neo4j läuft
docker ps | grep neo4j

# Starte Neo4j falls nicht
./start_neo4j.sh
```

### OpenAI API Fehler
- Prüfe `.env` Datei
- Stelle sicher, dass `OPENAI_API_KEY` gesetzt ist
- Prüfe API Key Gültigkeit

### Import-Fehler
```bash
# Stelle sicher, dass venv aktiviert ist
source venv/bin/activate

# Reinstalliere Dependencies
pip install -r requirements.txt
```

## ✅ Erfolg!

Wenn du dein erstes Szenario generiert hast, kannst du:
- Injects im Frontend ansehen
- Als CSV/JSON exportieren
- Visualisierungen prüfen
- Mit verschiedenen Szenario-Typen experimentieren

Viel Erfolg! 🎯


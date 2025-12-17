# 🎨 Streamlit Frontend

## 🚀 Starten

```bash
# Virtual Environment aktivieren
source venv/bin/activate

# Streamlit App starten
streamlit run app.py
```

Die App öffnet sich automatisch im Browser unter `http://localhost:8501`

## 📋 Features

### 1. **Generierung Tab**
- Szenario-Typ auswählen (Ransomware, DDoS, Supply Chain, Insider Threat)
- Anzahl Injects konfigurieren (1-20)
- Erweiterte Optionen:
  - Automatische Phasen-Übergänge
  - Validierungsdetails anzeigen

### 2. **Ergebnisse Tab**
- Übersicht aller generierten Injects
- Detaillierte Anzeige pro Inject:
  - Inject ID & Zeitversatz
  - Phase (mit farblicher Markierung)
  - Quelle & Ziel
  - Modalität
  - Inhalt
  - MITRE ID
  - Betroffene Assets
  - DORA Compliance Tag
  - Business Impact
- Export-Funktionen:
  - CSV Export
  - JSON Export

### 3. **Visualisierung Tab**
- Phasen-Verteilung (Balkendiagramm)
- Timeline-Übersicht
- Betroffene Assets-Liste

## 🎯 Verwendung

1. **Konfiguration** (Sidebar):
   - Wähle Szenario-Typ
   - Setze Anzahl Injects
   - Aktiviere/deaktiviere erweiterte Optionen

2. **Generierung**:
   - Klicke auf "🎯 Szenario generieren"
   - Warte auf Abschluss (kann einige Minuten dauern)
   - Erfolgsmeldung erscheint

3. **Ergebnisse ansehen**:
   - Wechsle zum "📊 Ergebnisse" Tab
   - Scrolle durch alle Injects
   - Exportiere bei Bedarf

4. **Visualisierung**:
   - Wechsle zum "📈 Visualisierung" Tab
   - Analysiere Phasen-Verteilung und Timeline

## ⚠️ Wichtige Hinweise

- **Neo4j muss laufen**: Stelle sicher, dass Neo4j läuft (`./start_neo4j.sh`)
- **OpenAI API Key**: Muss in `.env` konfiguriert sein
- **Erste Generierung**: Kann länger dauern (LLM-Aufrufe)
- **Session State**: Ergebnisse bleiben während der Session erhalten

## 🔧 Troubleshooting

### App startet nicht
```bash
# Prüfe ob Streamlit installiert ist
pip install streamlit

# Prüfe Python-Version
python --version  # Sollte 3.10+ sein
```

### Neo4j-Verbindungsfehler
```bash
# Starte Neo4j
./scripts/start_neo4j.sh

# Prüfe Verbindung
python scripts/check_setup.py
```

### OpenAI API Fehler
- Prüfe `.env` Datei
- Stelle sicher, dass `OPENAI_API_KEY` gesetzt ist
- Prüfe API Key Gültigkeit


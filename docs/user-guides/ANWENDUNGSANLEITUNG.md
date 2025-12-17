# Anwendungsanleitung - DORA Szenariengenerator

## 📋 Inhaltsverzeichnis

1. [Übersicht](#übersicht)
2. [Installation](#installation)
3. [Schnellstart](#schnellstart)
4. [Hauptanwendung: DORA Scenario Generator](#hauptanwendung-dora-scenario-generator)
5. [Thesis-Evaluation: Crisis Cockpit](#thesis-evaluation-crisis-cockpit)
6. [Backend-Integration](#backend-integration)
7. [Troubleshooting](#troubleshooting)

---

## Übersicht

Das Projekt besteht aus zwei Hauptkomponenten:

1. **DORA Scenario Generator** (`app.py`) - Enterprise-Grade Szenario-Generierung
2. **Crisis Cockpit** (`crisis_cockpit.py`) - Thesis-Evaluation-Tool

---

## Installation

### Voraussetzungen

- Python 3.10+
- Neo4j (lokal oder Docker)
- OpenAI API Key
- ChromaDB (optional, für TTP-Datenbank)

### Schritt 1: Repository klonen

```bash
cd /Users/finnheintzann/Desktop/BA
```

### Schritt 2: Virtual Environment erstellen

```bash
python3 -m venv venv
source venv/bin/activate  # Auf Windows: venv\Scripts\activate
```

### Schritt 3: Dependencies installieren

```bash
pip install -r requirements.txt
```

### Schritt 4: Umgebungsvariablen konfigurieren

Erstelle eine `.env` Datei im Projektroot:

```env
# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# ChromaDB (optional)
CHROMA_PERSIST_DIR=./chroma_db
```

### Schritt 5: Neo4j starten

```bash
# Mit Docker
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:latest

# Oder lokal installiert
./start_neo4j.sh
```

### Schritt 6: Basis-Infrastruktur initialisieren

```bash
python check_setup.py
```

---

## Schnellstart

### Option 1: DORA Scenario Generator starten

```bash
streamlit run app.py
```

Die App läuft auf: **http://localhost:8501**

### Option 2: Crisis Cockpit starten

```bash
streamlit run crisis_cockpit.py
```

Die App läuft auf: **http://localhost:8501**

---

## Hauptanwendung: DORA Scenario Generator

### Übersicht

Der DORA Scenario Generator ist eine Enterprise-Grade Anwendung zur Generierung von Krisenszenarien für Finanzunternehmen, die den DORA-Anforderungen entsprechen.

### Features

- **Multi-Agenten-System**: Manager, Intel, Generator, Critic Agents
- **LangGraph Workflow**: Orchestrierte Szenario-Generierung
- **Neo4j Knowledge Graph**: State Management und Second-Order Effects
- **Interaktiver Modus**: Live-Entscheidungen während der Generierung
- **DORA-Compliance**: Automatische Validierung nach Artikel 25

### Verwendung

#### 1. Szenario generieren

1. **Sidebar konfigurieren:**
   - Scenario Type auswählen (z.B. Ransomware Double Extortion)
   - Anzahl Injects festlegen (1-20)
   - Interactive Mode aktivieren (optional)

2. **"Generate Scenario" klicken:**
   - Der Workflow startet automatisch
   - Fortschrittsanzeige zeigt Status
   - Bei Interactive Mode: Pausen für Entscheidungen

3. **Ergebnisse ansehen:**
   - Generierte Injects werden angezeigt
   - System State wird visualisiert
   - Workflow-Logs zeigen den Prozess

#### 2. Interaktiver Modus

Im interaktiven Modus pausiert der Workflow an Decision-Points:

1. **Decision-Point erreicht:**
   - Workflow pausiert automatisch
   - Entscheidungsoptionen werden angezeigt

2. **Entscheidung treffen:**
   - Option auswählen (z.B. "Contain Threat")
   - "Apply Decision" klicken

3. **Workflow fortsetzen:**
   - Workflow läuft weiter
   - Nächster Decision-Point oder Ende

#### 3. Ergebnisse exportieren

- **MSEL Format**: Export für Exercise-Plattformen
- **JSON Export**: Vollständige Szenario-Daten
- **CSV Export**: Tabellarische Übersicht

### Workflow-Phasen

1. **NORMAL_OPERATION** → Normalbetrieb
2. **SUSPICIOUS_ACTIVITY** → Verdächtige Aktivität
3. **INITIAL_INCIDENT** → Initialer Vorfall
4. **ESCALATION_CRISIS** → Eskalation/Krise
5. **CONTAINMENT** → Eindämmung
6. **RECOVERY** → Wiederherstellung

---

## Thesis-Evaluation: Crisis Cockpit

### Übersicht

Das Crisis Cockpit ist ein spezielles Frontend für die Bachelor-Thesis Evaluation. Es ermöglicht den direkten Vergleich zwischen "Legacy Mode" (Pure LLM/RAG) und "Logic Guard Mode" (Neuro-Symbolic).

### Features

- **Split-Screen Layout**: Story Feed + State Reality
- **Dungeon Master Mode**: Manuelle Event-Injection
- **Evaluation Module**: Rating-System für Hallucinations
- **CSV Export**: Thesis-Daten exportieren

### Verwendung

#### 1. App starten

```bash
streamlit run crisis_cockpit.py
```

#### 2. Mock-Modus (Standard)

Die App startet mit Mock-Daten für UI-Testing:

- **Story Feed (links)**: Zeigt generierte Injects
- **State Reality (rechts)**: Zeigt Systemzustand
- **Sidebar**: Dungeon Master Controls

#### 3. Evaluation durchführen

1. **Mode wählen:**
   - Toggle zwischen "Legacy Mode" und "Logic Guard Mode"

2. **Injects bewerten:**
   - 👍 (Consistent) - Inject ist logisch konsistent
   - 👎 (Hallucination) - Inject enthält Fehler
   - Bei Hallucination: Error Reason eingeben

3. **Daten exportieren:**
   - "Download Thesis Data (CSV)" klicken
   - CSV enthält: `inject_id`, `mode`, `rating`, `reason`, `timestamp`

#### 4. Manuelle Events injizieren

1. **Event beschreiben:**
   - Textfeld in Sidebar: "Technician repairs server SRV-001"

2. **"Inject Event" klicken:**
   - Event wird als Inject hinzugefügt
   - State wird aktualisiert

#### 5. Auto-Play

- **"Auto-Play (5 steps)" klicken:**
  - Führt automatisch 5 Schritte aus
  - Nützlich für Batch-Testing

#### 6. Debug-Informationen

- **"Show Raw Data" expanden:**
  - Zeigt Raw JSON vom LLM
  - Zeigt Logic-Check-Ergebnisse

### CSV-Export Format

```csv
inject_id,mode,rating,reason,timestamp
INJ-001,Logic Guard Mode,Consistent,,2024-01-15T10:30:00
INJ-002,Legacy Mode,Hallucination,"Server name inconsistent",2024-01-15T10:31:00
```

---

## Backend-Integration

### Crisis Cockpit mit echtem Backend verbinden

#### Schritt 1: Imports aktivieren

In `crisis_cockpit.py`:

```python
# Auskommentieren:
from neo4j_client import Neo4jClient
from workflows.scenario_workflow import ScenarioWorkflow
from state_models import Inject, ScenarioType
```

#### Schritt 2: Helper-Funktionen implementieren

```python
def inject_to_dict(inject: Inject) -> Dict[str, Any]:
    """Konvertiert Inject-Objekt zu Dictionary."""
    return {
        "inject_id": inject.inject_id,
        "time_offset": inject.time_offset,
        "timestamp": datetime.now(),
        "source": inject.source,
        "target": inject.target,
        "content": inject.content,
        "modality": inject.modality.value,
        "phase": inject.phase.value,
        "mitre_id": inject.technical_metadata.mitre_id or "N/A",
        "affected_assets": inject.technical_metadata.affected_assets,
        "raw_json": inject.model_dump(),
        "logic_checks": "Logic Guard check result"  # Aus validation_result
    }
```

#### Schritt 3: State-Konvertierung

```python
def convert_neo4j_state_to_ui_format(system_state: Dict[str, Any]) -> Dict[str, Any]:
    """Konvertiert Neo4j State zu UI-Format."""
    # Analysiere system_state und erstelle Metriken
    # Beispiel:
    return {
        "diesel_tank": calculate_diesel_from_entities(system_state),
        "server_health": determine_server_health(system_state),
        # ...
    }
```

#### Schritt 4: Workflow initialisieren

```python
# In init_session_state() oder main():
if "workflow" not in st.session_state:
    neo4j_client = Neo4jClient()
    neo4j_client.connect()
    st.session_state.workflow = ScenarioWorkflow(
        neo4j_client=neo4j_client,
        max_iterations=10,
        interactive_mode=False
    )
```

#### Schritt 5: force_next_step() verbinden

```python
def force_next_step():
    """Echter Workflow-Schritt."""
    if "workflow" in st.session_state:
        result = st.session_state.workflow._execute_interactive_workflow(
            st.session_state.current_workflow_state,
            recursion_limit=20
        )
        # Konvertiere Injects
        new_injects = [inject_to_dict(inj) for inj in result.get("injects", [])]
        st.session_state.injects = new_injects
        update_state_from_backend(result)
```

---

## Troubleshooting

### Problem: "No injects were generated"

**Lösung:**
1. Prüfe Neo4j-Verbindung: `python check_setup.py`
2. Prüfe OpenAI API Key in `.env`
3. Prüfe Console-Logs für Fehler
4. Stelle sicher, dass `interactive_mode=False` für automatische Generierung

### Problem: "Neo4j Connection Error"

**Lösung:**
1. Prüfe ob Neo4j läuft: `docker ps` oder `neo4j status`
2. Prüfe `.env` Konfiguration
3. Teste Verbindung: `python -c "from neo4j_client import Neo4jClient; Neo4jClient().connect()"`

### Problem: "OpenAI API Error"

**Lösung:**
1. Prüfe API Key in `.env`
2. Prüfe API Quota/Limits
3. Prüfe Internet-Verbindung

### Problem: "Streamlit App läuft nicht"

**Lösung:**
1. Prüfe ob Port belegt: `lsof -i :8501`
2. Beende alte Prozesse: `pkill -f streamlit`
3. Starte neu: `streamlit run app.py`

### Problem: "Crisis Cockpit zeigt keine Daten"

**Lösung:**
1. Prüfe Session State: `st.session_state` in der App
2. Stelle sicher, dass Mock-Daten geladen werden
3. Prüfe Browser-Console für JavaScript-Fehler

---

## Nützliche Befehle

### Projekt neu starten

```bash
# Alle Streamlit-Prozesse beenden
pkill -f streamlit

# Crisis Cockpit starten
streamlit run crisis_cockpit.py

# Oder DORA Generator
streamlit run app.py
```

### Neo4j zurücksetzen

```bash
# Neo4j stoppen
docker stop neo4j

# Daten löschen (Vorsicht!)
docker rm neo4j
docker volume rm neo4j_data

# Neu starten
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
```

### Logs ansehen

```bash
# Streamlit Logs
tail -f ~/.streamlit/logs/streamlit.log

# Neo4j Logs
docker logs neo4j
```

---

## Weitere Ressourcen

- **Architektur**: Siehe [Architektur-Dokumentation](../architecture/ARCHITECTURE.md)
- **Thesis-Dokumentation**: Siehe `THESIS_DOCUMENTATION.md`
- **Projekt-Status**: Siehe `PROJECT_STATUS.md`
- **Crisis Cockpit**: Siehe [Crisis Cockpit Guide](CRISIS_COCKPIT_README.md)

---

## Support

Bei Problemen:
1. Prüfe die Troubleshooting-Sektion
2. Prüfe die Logs
3. Öffne ein Issue im Repository

**Viel Erfolg mit deiner Bachelor-Thesis! 🎓**


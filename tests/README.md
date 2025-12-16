# Test Suite Dokumentation

## Übersicht

Die Test-Suite umfasst umfassende Tests für alle Komponenten des DORA Scenario Generators.

## Test-Kategorien

### 1. Workflow Tests

**Datei:** `test_workflow_basic.py`
- Workflow-Initialisierung
- State Management
- Workflow-Logik (should_continue, should_refine)
- Interaktiver Modus

**Datei:** `test_workflow_integration.py`
- Vollständiger Workflow-Durchlauf
- Graph-Struktur
- Initial State Struktur

**Datei:** `test_workflow_nodes.py`
- Einzelne Node-Tests (State Check, Manager, Intel, Action Selection, State Update)
- Isolierte Node-Funktionalität

### 2. Agent Tests

**Datei:** `test_agents.py`
- Manager Agent Initialisierung und Storyline-Erstellung
- Intel Agent TTP-Abfrage
- Generator Agent System-State-Formatierung
- Critic Agent Validierung

### 3. System State Format Tests

**Datei:** `test_system_state_format.py`
- Kompatibilität mit neuem system_state Format (direktes Dictionary)
- Formatierung in allen Agents
- Leerer System State Handling

### 4. Frontend Tests

**Datei:** `test_crisis_cockpit.py`
- Mock-Daten-Generierung
- State Management
- Evaluation-Funktionalität
- Datenkonvertierung

## Test-Ausführung

### Alle Tests ausführen

```bash
# Mit pytest
pytest tests/ -v

# Oder mit dem Test Runner
python tests/run_all_tests.py
```

### Spezifische Tests ausführen

```bash
# Nur Workflow-Tests
pytest tests/test_workflow_basic.py -v

# Nur Agent-Tests
pytest tests/test_agents.py -v

# Mit Coverage
pytest tests/ --cov=. --cov-report=html
```

## Test-Anforderungen

### Voraussetzungen

- Python 3.10+
- pytest installiert: `pip install pytest`
- Neo4j läuft (für Integrationstests)
- OpenAI API Key (für Agent-Tests mit LLM)
- ChromaDB (optional, für Intel Agent Tests)

### Mock vs. Integration Tests

- **Unit Tests:** Verwenden Mocks, keine externen Dependencies
- **Integration Tests:** Benötigen Neo4j, können LLM-Aufrufe machen

## Test-Coverage

Aktuell getestet:
- ✅ Workflow-Initialisierung
- ✅ State Management
- ✅ System State Format-Kompatibilität
- ✅ Node-Funktionalität
- ✅ Agent-Interaktionen
- ⚠️ Vollständiger Workflow-Durchlauf (benötigt LLM)
- ⚠️ Crisis Cockpit UI (benötigt Streamlit)

## Nächste Schritte

- [ ] E2E Tests für vollständigen Szenario-Durchlauf
- [ ] Performance-Tests für große Szenarien
- [ ] Load-Tests für Neo4j-Integration
- [ ] UI-Tests mit Streamlit-Testing-Framework


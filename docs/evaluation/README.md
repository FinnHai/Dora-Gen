# Evaluationsframework für Halluzinations-Erkennung

## Übersicht

Dieses Framework ermöglicht eine **quantitative, wissenschaftlich fundierte Evaluierung** der Halluzinations-Erkennung im Vergleich zwischen Baseline RAG/LLM und dem Neuro-Symbolic Agenten-System.

## Schnellstart

### 1. Evaluierung ausführen

```bash
# Alle Testfälle evaluieren
python evaluation/run_evaluation.py

# Mit spezifischen Halluzinationstypen
python evaluation/run_evaluation.py --test-types FSM_VIOLATION,STATE_INCONSISTENCY

# Mit detaillierter Ausgabe
python evaluation/run_evaluation.py --verbose

# Mit eigenem Ausgabeverzeichnis
python evaluation/run_evaluation.py --output-dir meine_ergebnisse
```

### 2. Ergebnisse interpretieren

Die Evaluierung generiert:
- **JSON-Report**: Detaillierte Metriken und Ergebnisse
- **CSV-Export**: Tabellarische Daten für weitere Analyse

## Komponenten

### 1. Edge-Case-Generator (`hallucination_test_cases.py`)

Generiert systematisch Testfälle, die spezifische Halluzinationen provozieren:

- **FSM-Verstöße**: Ungültige Phasen-Übergänge
- **State-Inkonsistenzen**: Widersprüche zum Systemzustand
- **MITRE-Sequenz-Fehler**: Unmögliche ATT&CK-Sequenzen
- **Temporale Inkonsistenzen**: Zeitliche Widersprüche

### 2. Automatischer Evaluator (`automatic_evaluator.py`)

Führt quantitative Evaluierung durch:

- Testet Baseline (ohne Validierung)
- Testet Agenten-System (mit Critic Agent)
- Berechnet Metriken (Precision, Recall, F1, Accuracy)
- Generiert Reports

### 3. Metriken

Standard-Classification-Metriken:

- **Precision**: Anteil korrekt erkannter Halluzinationen
- **Recall**: Anteil tatsächlicher Halluzinationen, die erkannt wurden
- **F1-Score**: Harmonisches Mittel von Precision und Recall
- **Accuracy**: Anteil korrekter Klassifikationen

## Verwendung

### Programmgesteuert

```python
from evaluation import AutomaticEvaluator, HallucinationTestGenerator
from pathlib import Path

# Initialisiere Evaluator
evaluator = AutomaticEvaluator()

# Generiere Testfälle
test_generator = HallucinationTestGenerator()
test_cases = test_generator.generate_all_test_cases()

# Führe Evaluierung durch
results = evaluator.evaluate_all(test_cases)

# Berechne Metriken
metrics = evaluator.calculate_metrics()

# Generiere Report
report = evaluator.generate_report(Path("report.json"))

# Exportiere CSV
evaluator.export_to_csv(Path("results.csv"))
```

### Spezifische Halluzinationstypen testen

```python
from evaluation import HallucinationTestGenerator, HallucinationType

generator = HallucinationTestGenerator()

# Nur FSM-Verstöße
fsm_cases = generator.get_test_cases_by_type(HallucinationType.FSM_VIOLATION)

# Nur State-Inkonsistenzen
state_cases = generator.get_test_cases_by_type(HallucinationType.STATE_INCONSISTENCY)
```

## Halluzinationstypen

1. **FSM_VIOLATION**: Verstöße gegen Finite State Machine Constraints
2. **STATE_INCONSISTENCY**: Widersprüche zum Systemzustand
3. **MITRE_SEQUENCE_ERROR**: Unmögliche MITRE ATT&CK Sequenzen
4. **TEMPORAL_INCONSISTENCY**: Zeitliche Widersprüche
5. **CAUSAL_CONTRADICTION**: Kausale Widersprüche
6. **ASSET_NONEXISTENT**: Assets existieren nicht im Graph
7. **ASSET_NAME_INCONSISTENCY**: Inkonsistente Asset-Namen
8. **SEVERITY_MISMATCH**: Schweregrad passt nicht zur Phase

## Ausgabe-Format

### JSON-Report

```json
{
  "timestamp": "2024-01-01T12:00:00",
  "total_test_cases": 10,
  "overall_metrics": {
    "baseline": {
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0,
      "accuracy": 0.5
    },
    "agent_system": {
      "precision": 0.9,
      "recall": 0.8,
      "f1": 0.85,
      "accuracy": 0.9
    },
    "improvement": {
      "precision": 0.9,
      "recall": 0.8,
      "f1": 0.85,
      "accuracy": 0.4
    }
  },
  "metrics_by_type": {
    "FSM_VIOLATION": { ... },
    "STATE_INCONSISTENCY": { ... }
  },
  "detailed_results": [ ... ]
}
```

### CSV-Export

| test_id | hallucination_type | ground_truth | baseline_detected | agent_detected | baseline_correct | agent_correct |
|---------|-------------------|--------------|-------------------|----------------|------------------|---------------|
| FSM-001 | FSM_VIOLATION     | True         | False             | True           | False            | True          |

## Wissenschaftliche Fundierung

Siehe [EVALUATION_METHODOLOGY.md](EVALUATION_METHODOLOGY.md) für detaillierte Beschreibung der wissenschaftlichen Methodik.

## Beispiel-Output

```
================================================================
Automatische Evaluierung: Halluzinations-Erkennung
================================================================

📋 10 Testfälle werden evaluiert...

================================================================
ERGEBNISSE
================================================================

Baseline RAG/LLM (ohne Validierung):
  Precision:  0.000
  Recall:      0.000
  F1-Score:   0.000
  Accuracy:   0.500

Agenten-System (mit Logik-Guard):
  Precision:  0.900
  Recall:     0.800
  F1-Score:  0.850
  Accuracy:  0.900

Verbesserung:
  Precision:  +0.900
  Recall:     +0.800
  F1-Score:   +0.850
  Accuracy:   +0.400

📄 Generiere Reports...
   ✅ Report: evaluation_results/evaluation_report_20240101_120000.json
   ✅ CSV: evaluation_results/evaluation_results_20240101_120000.csv

================================================================
✅ Evaluierung abgeschlossen!
================================================================
```

## Nächste Schritte

1. **Erweitere Testfälle**: Füge weitere Edge Cases hinzu
2. **Analysiere Ergebnisse**: Nutze CSV für weitere Analysen
3. **Vergleiche Varianten**: Teste verschiedene Konfigurationen
4. **Visualisiere**: Erstelle Diagramme aus den Metriken

## Troubleshooting

### Import-Fehler

Stelle sicher, dass alle Abhängigkeiten installiert sind:
```bash
pip install -r requirements.txt
```

### Neo4j-Verbindung

Für State-Checks muss Neo4j laufen:
```bash
./scripts/start_neo4j.sh
```

### OpenAI API Key

Stelle sicher, dass `OPENAI_API_KEY` in `.env` gesetzt ist.

## Literatur

- Information Retrieval Metriken (Precision/Recall)
- Classification Metriken (F1, Accuracy)
- LLM-Halluzinations-Studien (TruthfulQA, HaluEval)
- Neuro-Symbolic AI Evaluierungen

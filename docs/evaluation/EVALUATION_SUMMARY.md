# Evaluationsframework - Zusammenfassung

## Was wurde erstellt?

Ein **quantitatives, wissenschaftlich fundiertes Evaluationsframework** für die automatische Evaluierung der Halluzinations-Erkennung.

## Hauptkomponenten

### 1. Edge-Case-Generator (`evaluation/hallucination_test_cases.py`)

- **Systematische Generierung** von Testfällen, die Halluzinationen provozieren
- **8 Halluzinationstypen**:
  - FSM-Verstöße (ungültige Phasen-Übergänge)
  - State-Inkonsistenzen (Widersprüche zum Systemzustand)
  - MITRE-Sequenz-Fehler (unmögliche ATT&CK-Sequenzen)
  - Temporale Inkonsistenzen (zeitliche Widersprüche)
  - Asset-Non-Existent (Assets existieren nicht)
  - Asset-Name-Inkonsistenzen
  - Kausale Widersprüche
  - Schweregrad-Mismatches

- **Aktuell**: ~10 systematisch generierte Testfälle
- **Erweiterbar**: Einfach weitere Testfälle hinzufügen

### 2. Automatischer Evaluator (`evaluation/automatic_evaluator.py`)

- **Quantitative Evaluierung**:
  - Testet Baseline RAG/LLM (ohne Validierung)
  - Testet Agenten-System (mit Critic Agent)
  - Berechnet Metriken automatisch

- **Metriken**:
  - Precision (Anteil korrekt erkannter Halluzinationen)
  - Recall (Anteil tatsächlicher Halluzinationen, die erkannt wurden)
  - F1-Score (Harmonisches Mittel)
  - Accuracy (Anteil korrekter Klassifikationen)

- **Reports**:
  - JSON-Report mit detaillierten Metriken
  - CSV-Export für weitere Analysen

### 3. Wissenschaftliche Dokumentation (`evaluation/EVALUATION_METHODOLOGY.md`)

- **Methodik-Beschreibung**: Wie die Evaluierung funktioniert
- **Metriken-Erklärung**: Was Precision, Recall, F1 bedeuten
- **Wissenschaftliche Fundierung**: Basierend auf Standard-Evaluationsmethoden

### 4. Einfaches Ausführungsskript (`run_evaluation.py`)

- **Einfache Nutzung**: `python evaluation/run_evaluation.py`
- **Optionen**: Spezifische Testtypen, Ausgabeverzeichnis, Verbose-Modus

## Verwendung

### Schnellstart

```bash
# Alle Testfälle evaluieren
python evaluation/run_evaluation.py

# Mit spezifischen Typen
python evaluation/run_evaluation.py --test-types FSM_VIOLATION,STATE_INCONSISTENCY

# Mit detaillierter Ausgabe
python evaluation/run_evaluation.py --verbose
```

### Programmgesteuert

```python
from evaluation import AutomaticEvaluator

evaluator = AutomaticEvaluator()
results = evaluator.evaluate_all()
metrics = evaluator.calculate_metrics()
report = evaluator.generate_report(Path("report.json"))
```

## Vorteile gegenüber qualitativer Evaluierung

✅ **Quantitativ**: Objektive Metriken statt subjektiver Bewertung  
✅ **Reproduzierbar**: Testfälle sind konsistent und wiederholbar  
✅ **Wissenschaftlich fundiert**: Basierend auf Standard-Metriken  
✅ **Automatisiert**: Keine manuelle Bewertung nötig  
✅ **Vergleichbar**: Klare Metriken für Baseline vs. Agenten-System  
✅ **Erweiterbar**: Einfach weitere Testfälle hinzufügen  

## Erwartete Ergebnisse

### Baseline RAG/LLM
- **Precision**: 0.0 (erkennt keine Halluzinationen)
- **Recall**: 0.0 (erkennt keine Halluzinationen)
- **F1**: 0.0
- **Accuracy**: Abhängig von Verhältnis Halluzinationen zu Nicht-Halluzinationen

### Agenten-System
- **Precision**: > 0.0 (erkennt einige Halluzinationen korrekt)
- **Recall**: > 0.0 (erkennt einige Halluzinationen)
- **F1**: > 0.0
- **Accuracy**: Höher als Baseline

### Verbesserung
- **Positive Werte**: Agenten-System ist besser als Baseline
- **Hohe Precision**: Wenige False Positives
- **Hohe Recall**: Wenige False Negatives
- **Hohe F1**: Gute Balance zwischen Precision und Recall

## Nächste Schritte

1. **Evaluierung ausführen**: `python evaluation/run_evaluation.py`
2. **Ergebnisse analysieren**: JSON-Report und CSV prüfen
3. **Testfälle erweitern**: Weitere Edge Cases hinzufügen
4. **Visualisieren**: Diagramme aus Metriken erstellen
5. **In Thesis einbauen**: Ergebnisse für Bachelorarbeit verwenden

## Dateien

- `evaluation/hallucination_test_cases.py`: Edge-Case-Generator
- `evaluation/automatic_evaluator.py`: Automatischer Evaluator
- `evaluation/__init__.py`: Package-Initialisierung
- `evaluation/EVALUATION_METHODOLOGY.md`: Wissenschaftliche Dokumentation
- `evaluation/README.md`: Nutzungsanleitung
- `run_evaluation.py`: Einfaches Ausführungsskript

## Wichtige Hinweise

1. **Neo4j muss laufen**: Für State-Checks benötigt das System Neo4j
2. **OpenAI API Key**: Muss in `.env` gesetzt sein
3. **Baseline-Simplifikation**: Baseline akzeptiert alles (realistischere Baseline könnte anders sein)
4. **Testfall-Abdeckung**: Nicht alle möglichen Halluzinationen sind abgedeckt (erweiterbar)

## Unterschied zu DORA

Das Framework ist **nicht mehr DORA-spezifisch**, sondern fokussiert auf:
- **Halluzinations-Erkennung**: Wie gut erkennt das System Fehler?
- **Quantitative Metriken**: Objektive Messung statt Compliance-Checks
- **Edge Cases**: Systematische Provokation von Fehlern
- **Vergleichbarkeit**: Baseline vs. Agenten-System

Dies macht die Evaluierung **vergleichbarer** und **wissenschaftlich fundierter**.

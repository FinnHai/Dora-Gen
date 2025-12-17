# Wissenschaftliche Evaluationsmethodik

## Übersicht

Dieses Dokument beschreibt die wissenschaftlich fundierte Methodik zur quantitativen Evaluierung der Halluzinations-Erkennung im Vergleich zwischen Baseline RAG/LLM und dem Neuro-Symbolic Agenten-System.

## Forschungsfrage

**Reduziert ein Neuro-Symbolic Logic Guard (LangGraph + State Tracking) Halluzinationen in Krisenszenarien im Vergleich zu einem reinen LLM/RAG-Ansatz?**

## Evaluationsmethodik

### 1. Edge-Case-basierte Evaluierung

Statt qualitativer manueller Analyse verwenden wir **systematisch generierte Edge Cases**, die spezifische Halluzinationstypen provozieren.

#### Vorteile:
- **Reproduzierbarkeit**: Testfälle sind konsistent und wiederholbar
- **Quantifizierbarkeit**: Jeder Testfall hat ein klares Ground Truth
- **Vollständigkeit**: Systematische Abdeckung verschiedener Halluzinationstypen
- **Objektivität**: Keine subjektive Bewertung nötig

### 2. Halluzinationstypen

Basierend auf wissenschaftlicher Literatur zu LLM-Halluzinationen kategorisieren wir:

1. **FSM_VIOLATION**: Verstöße gegen Finite State Machine Constraints
   - Ungültige Phasen-Übergänge
   - Rückwärts-Übergänge
   - Übersprungene Phasen

2. **STATE_INCONSISTENCY**: Widersprüche zum Systemzustand
   - Assets existieren nicht im Knowledge Graph
   - Status-Inkonsistenzen (Asset offline, aber als online behandelt)
   - Asset-Name-Inkonsistenzen

3. **MITRE_SEQUENCE_ERROR**: Unmögliche MITRE ATT&CK Sequenzen
   - Exfiltration vor Initial Access
   - Persistence vor Execution
   - Unmögliche TTP-Kombinationen

4. **TEMPORAL_INCONSISTENCY**: Zeitliche Widersprüche
   - Zeitstempel gehen zurück
   - Events passieren vor ihren kausalen Vorgängern

5. **CAUSAL_CONTRADICTION**: Kausale Widersprüche
   - Events ohne kausale Vorgänger
   - Unmögliche Kausalitätsketten

### 3. Metriken

Wir verwenden Standard-Classification-Metriken:

#### Confusion Matrix

|                    | Ground Truth: Halluzination | Ground Truth: Keine Halluzination |
|--------------------|----------------------------|-----------------------------------|
| **Erkannt**        | True Positive (TP)         | False Positive (FP)               |
| **Nicht erkannt**  | False Negative (FN)       | True Negative (TN)                |

#### Berechnete Metriken

- **Precision**: TP / (TP + FP)
  - Anteil der erkannten Halluzinationen, die wirklich Halluzinationen sind
  
- **Recall**: TP / (TP + FN)
  - Anteil der tatsächlichen Halluzinationen, die erkannt wurden
  
- **F1-Score**: 2 * (Precision * Recall) / (Precision + Recall)
  - Harmonisches Mittel von Precision und Recall
  
- **Accuracy**: (TP + TN) / (TP + FP + FN + TN)
  - Anteil der korrekten Klassifikationen

#### Vergleichsmetriken

- **Precision Improvement**: Agenten-System Precision - Baseline Precision
- **Recall Improvement**: Agenten-System Recall - Baseline Recall
- **F1 Improvement**: Agenten-System F1 - Baseline F1
- **Accuracy Improvement**: Agenten-System Accuracy - Baseline Accuracy

### 4. Baseline Definition

**Baseline RAG/LLM**: 
- Direkter LLM-Call ohne Validierung
- Keine FSM-Constraints
- Keine State-Checks
- Keine Critic-Agent-Validierung
- **Erwartetes Verhalten**: Akzeptiert alle Injects (erkennt keine Halluzinationen)

**Agenten-System**:
- Vollständiges Neuro-Symbolic System
- FSM-Validierung
- Neo4j State-Checks
- Critic-Agent Multi-Layer-Validierung
- **Erwartetes Verhalten**: Erkennt Halluzinationen durch Constraints

### 5. Testfall-Generierung

#### Systematische Generierung

Testfälle werden systematisch generiert für:
- Jeden Halluzinationstyp
- Verschiedene Phasen-Kombinationen
- Verschiedene State-Konfigurationen
- Verschiedene MITRE-Sequenzen

#### Ground Truth

Jeder Testfall hat ein klares Ground Truth:
- **True**: Testfall provoziert eine echte Halluzination
- **False**: Testfall ist valide (keine Halluzination)

### 6. Evaluationsprozess

1. **Testfall-Generierung**: Systematische Generierung aller Edge Cases
2. **Baseline-Test**: Teste jeden Fall mit Baseline (ohne Validierung)
3. **Agenten-System-Test**: Teste jeden Fall mit Agenten-System (mit Validierung)
4. **Metriken-Berechnung**: Berechne Precision, Recall, F1, Accuracy
5. **Vergleichsanalyse**: Vergleiche Baseline vs. Agenten-System
6. **Report-Generierung**: Erstelle detaillierten Report mit allen Metriken

### 7. Wissenschaftliche Fundierung

#### Literatur-Basis

Diese Methodik basiert auf:
- **Information Retrieval Metriken** (Precision/Recall) - Standard in NLP-Evaluierung
- **Classification Metriken** (F1, Accuracy) - Standard in ML-Evaluierung
- **Edge-Case-Testing** - Standard in Software-Testing und LLM-Evaluierung
- **Confusion Matrix** - Standard in Evaluierung von Klassifikationssystemen

#### Vergleichbare Studien

Ähnliche Evaluationsmethoden werden verwendet in:
- LLM-Halluzinations-Studien (z.B. TruthfulQA, HaluEval)
- Neuro-Symbolic AI Evaluierungen
- Multi-Agenten-System Evaluierungen

### 8. Validierung der Methodik

#### Interne Validität
- Klare Ground Truth für jeden Testfall
- Reproduzierbare Testfälle
- Objektive Metriken (keine subjektive Bewertung)

#### Externe Validität
- Realistische Edge Cases basierend auf typischen Halluzinationen
- Abdeckung verschiedener Halluzinationstypen
- Systematische Testfall-Generierung

### 9. Limitationen

1. **Testfall-Abdeckung**: Nicht alle möglichen Halluzinationen sind abgedeckt
2. **Synthetische Testfälle**: Testfälle sind konstruiert, nicht aus echten Szenarien
3. **Baseline-Simplifikation**: Baseline akzeptiert alles (realistischere Baseline könnte anders sein)

### 10. Interpretation der Ergebnisse

#### Erwartete Ergebnisse

- **Baseline**: 
  - Precision: 0.0 (erkennt keine Halluzinationen)
  - Recall: 0.0 (erkennt keine Halluzinationen)
  - F1: 0.0
  - Accuracy: Abhängig von Verhältnis Halluzinationen zu Nicht-Halluzinationen

- **Agenten-System**:
  - Precision: > 0.0 (erkennt einige Halluzinationen korrekt)
  - Recall: > 0.0 (erkennt einige Halluzinationen)
  - F1: > 0.0
  - Accuracy: Höher als Baseline

#### Interpretation

- **Positive Verbesserung**: Agenten-System ist besser als Baseline
- **Hohe Precision**: Wenige False Positives (selten falsche Erkennung)
- **Hohe Recall**: Wenige False Negatives (selten übersehene Halluzinationen)
- **Hohe F1**: Gute Balance zwischen Precision und Recall

## Zusammenfassung

Diese Evaluationsmethodik bietet:
- ✅ Quantitative, objektive Metriken
- ✅ Reproduzierbare Testfälle
- ✅ Wissenschaftlich fundierte Methodik
- ✅ Systematische Abdeckung verschiedener Halluzinationstypen
- ✅ Klare Vergleichbarkeit zwischen Baseline und Agenten-System

Die Methodik ermöglicht eine fundierte wissenschaftliche Aussage über die Wirksamkeit des Neuro-Symbolic Logic Guards zur Reduzierung von Halluzinationen.

# Transparency Mode - Critic & Workflow Visualisierung

**Version:** 1.0.0  
**Letzte Aktualisierung:** 2025-12-20

---

## Übersicht

Der Transparency Mode zeigt detaillierte Informationen über die Funktionsweise des Critic Agents und des Workflows. Dies ermöglicht es, die wissenschaftlich basierte Validierung und den Workflow-Ablauf zu verstehen.

---

## Aktivierung

Der Transparency Mode kann über den Button "🔬 Show Transparency" im Header aktiviert werden. Er wechselt das Layout von 3 Spalten auf 4 Spalten.

---

## Komponenten

### 1. Critic Validation Panel

**Position:** Panel C (20% Breite)

**Features:**
- **Validation Steps**: Zeigt alle Validierungsschritte mit Status und Dauer
  - Pydantic Schema Validation
  - FSM Phase Transition
  - State Consistency Check
  - Temporal Consistency
  - LLM-based Validation
  - Compliance Validation

- **Scientific Metrics**: Quantifizierbare Metriken
  - Overall Quality Score (mit Konfidenz-Intervall)
  - Logical Consistency Score (30% Gewichtung)
  - Causal Validity Score (25% Gewichtung)
  - Compliance Score (15% Gewichtung)
  - Temporal Consistency Score (15% Gewichtung)
  - Asset Consistency Score (15% Gewichtung)

- **Statistical Significance**: 
  - p-value
  - Signifikanz-Status

- **Errors & Warnings**: 
  - Erweiterbare Liste von Fehlern
  - Erweiterbare Liste von Warnungen

### 2. Workflow Visualization

**Position:** Panel D (20% Breite, oben)

**Features:**
- **Workflow Nodes**: Visualisierung aller Workflow-Schritte
  - State Check
  - Manager Agent
  - Intel Agent
  - Action Selection
  - Generator Agent
  - Critic Agent
  - State Update

- **Status-Indikatoren**:
  - ✓ Completed (Grün)
  - ⚡ Running (Violett, animiert)
  - ⏳ Pending (Grau)
  - ✗ Error (Rot)

- **Performance Metrics**:
  - Total Duration
  - Completed Nodes
  - Node-spezifische Dauer

- **Legende**: Erklärt die Status-Farben

---

## Layout-Modi

### Normal Mode (3 Spalten)
```
[Scenario Composer 30%] [Digital Twin Graph 50%] [Forensic Trace 20%]
```

### Transparency Mode (4 Spalten)
```
[Scenario Composer 25%] [Digital Twin Graph 35%] [Critic Validation 20%] [Workflow & Trace 20%]
```

---

## Datenquellen

### Critic Validation Panel

Die Metriken werden aus den `CriticLog`-Einträgen extrahiert:

```typescript
interface CriticLog {
  details?: {
    validation?: {
      metrics?: {
        logical_consistency_score?: number;
        causal_validity_score?: number;
        compliance_score?: number;
        temporal_consistency_score?: number;
        asset_consistency_score?: number;
        overall_quality_score?: number;
        confidence_interval?: [number, number];
        p_value?: number;
        statistical_significance?: boolean;
      };
    };
  };
}
```

### Workflow Visualization

Der Workflow-Status wird basierend auf dem Inject-Status abgeleitet:

- `verified` → Alle Nodes bis Critic completed
- `validating` → Critic Node running
- `generating` → Generator Node running
- `rejected` → Error-Status

---

## Verwendung

1. **Aktiviere Transparency Mode**: Klicke auf "🔬 Show Transparency" im Header
2. **Wähle einen Inject**: Klicke auf einen Inject-Card im Scenario Composer
3. **Sehe Validierung**: Das Critic Validation Panel zeigt alle Details
4. **Sehe Workflow**: Das Workflow Visualization Panel zeigt den Ablauf

---

## Wissenschaftliche Metriken

### Overall Quality Score

Gewichteter Durchschnitt aller Metriken:

```
Overall Quality Score = 
  (Logical Consistency × 0.30) +
  (Causal Validity × 0.25) +
  (Compliance × 0.15) +
  (Temporal Consistency × 0.15) +
  (Asset Consistency × 0.15)
```

### Schwellenwerte

- **Critical**: < 0.70 → Blocking-Fehler
- **Warning**: < 0.85 → Warnung
- **Excellent**: ≥ 0.95 → Exzellent

### Konfidenz-Intervalle

95% Konfidenz-Intervalle werden angezeigt, wenn genug Daten vorhanden sind (≥ 2 vorherige Injects).

### Statistische Signifikanz

p-value < 0.05 → Statistisch signifikant

---

## Design

- **Farben**: Verwendet die CRUX-Semantik-Farben
  - Symbolic (Grün) für Erfolg
  - Neural (Violett) für Running
  - Intervention (Rot) für Fehler
  - Void (Schwarz) für Hintergrund

- **Typografie**: 
  - Inter für Labels
  - JetBrains Mono für Metriken und Werte

- **Animationen**: 
  - Pulse für Running-Status
  - Smooth Transitions für Status-Änderungen

---

**Letzte Aktualisierung:** 2025-12-20






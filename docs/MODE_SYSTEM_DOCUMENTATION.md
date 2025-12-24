# CRUX Mode System Dokumentation

## Übersicht

Das CRUX-System verwendet **zwei Kategorien von Modi**, die klar getrennt sind:

1. **Konzeptionelle Sicht-Modi (UX)** - Steuern, *wie viel* Information der Nutzer sieht
2. **Technische Ausführungs-Modi (Backend)** - Steuern, *wie* die Engine (LangGraph) arbeitet

---

## 1. Konzeptionelle Sicht-Modi (User Experience)

Diese Modi entscheiden darüber, *wie viel* Information der Nutzer sieht. Das ist zentral für den **"Fog of War"**-Aspekt der Thesis.

### 🛡️ Player Mode (Manager-Sicht / Fog of War)

**Zielgruppe:** Der Crisis Manager (der "Spieler")

**Funktion:** Zeigt nur das **"Perceived State"** (Wahrgenommener Zustand)

**Verhalten:**
- Assets bleiben **grün**, auch wenn sie im Backend schon kompromittiert sind
- Erst wenn ein Inject (z.B. SIEM Alert) generiert wird oder der Spieler eine "Investigation" auf dem Knoten startet, ändert sich die Farbe
- Unbekannte Assets sind transparent/gestrichelt dargestellt

**Zweck:** Simulation von Unsicherheit und Stress (realistische Krisenbedingungen)

**Code:**
```typescript
viewMode: 'player' // Im Store
```

### 👁️ God Mode (Trainer-Sicht / Ground Truth)

**Zielgruppe:** Entwickler, Übungsleiter oder Auditor

**Funktion:** Zeigt den **"Actual State"** (Tatsächlicher Zustand) direkt aus Neo4j

**Verhalten:**
- Zeigt sofort alle kompromittierten Knoten (rot) und Angriffsvektoren
- Zeigt Metadaten wie `last_updated_by_inject` und versteckte Abhängigkeiten
- Keine Filterung basierend auf Alerts/Investigations

**Zweck:** Debugging, Erklärung der Kausalitäten nach der Übung (Debriefing)

**Code:**
```typescript
viewMode: 'god' // Im Store
```

---

## 2. Technische Ausführungs-Modi (Backend Konfiguration)

Diese Modi steuern, wie die Engine (LangGraph) arbeitet. Sie sind in der `WorkflowState`-Definition definiert.

### 🎓 Thesis Mode (Full Validation)

**Status:** Im Code definiert als `mode: 'thesis'`

**Funktion:** Der **Critic Agent** ist voll aktiv. Jeder Inject wird gegen MITRE, DORA und logische Konsistenz geprüft.

**Verhalten:**
- Vollständige Validierung durch Critic Agent
- Refine-Loop bei fehlerhaften Injects
- Hohe logische Konsistenz
- Längere Generierungszeit

**Zweck:** Erzeugt wissenschaftlich valide, kausal korrekte Szenarien für die Arbeit

**Code:**
```python
mode: Literal['legacy', 'thesis']  # Default: 'thesis'
```

### 🚀 Legacy Mode (Skip Validation)

**Status:** Im Code definiert als `mode: 'legacy'`

**Funktion:** Überspringt die strenge Validierung ("Skip Validation")

**Verhalten:**
- Critic Agent gibt immer `is_valid=True` zurück
- Keine Refine-Loops
- Schnellere Generierung
- Niedrigere logische Konsistenz

**Zweck:** Schnelles Prototyping oder Demos, wenn Wartezeiten (durch den Critic) stören

**Code:**
```python
mode: 'legacy'
```

### 🎮 Interactive Mode (Human-in-the-Loop)

**Status:** Im Code als Feld `interactive_mode: bool` vorhanden

**Funktion:** Der Workflow pausiert an Entscheidungspunkten (`pending_decision`). Der Nutzer kann die Richtung des Szenarios beeinflussen (z.B. "Zahlen wir das Lösegeld?").

**Verhalten:**
- Workflow pausiert bei `pending_decision`
- Benutzer kann Entscheidungen treffen
- Workflow setzt mit Benutzer-Entscheidung fort

**Zweck:** Macht aus einer statischen Geschichte eine echte Simulation

**Code:**
```python
interactive_mode: bool  # Default: False
```

---

## Kombination der Modi

Die Modi können kombiniert werden:

| UX View Mode | Backend Execution Mode | Use Case |
|--------------|------------------------|----------|
| Player Mode | Thesis Mode | **Thesis-Demonstration**: Realistische Simulation mit voller Validierung |
| God Mode | Thesis Mode | **Debugging**: Ground Truth mit voller Validierung |
| Player Mode | Legacy Mode | **Schnelle Demo**: Fog of War ohne Validierung |
| God Mode | Legacy Mode | **Prototyping**: Ground Truth ohne Validierung |
| Player Mode | Interactive Mode | **Live Training**: Manager-Sicht mit Entscheidungen |

---

## Implementation

### Frontend (React)

```typescript
// Store
const { viewMode, executionMode, interactiveMode } = useCruxStore();

// View Mode Toggle
setViewMode('player' | 'god');

// Execution Mode (wird vom Backend gesteuert)
// executionMode wird aus Backend-State gelesen
```

### Backend (Python)

```python
# WorkflowState
state = {
    "mode": "thesis",  # 'thesis' oder 'legacy'
    "interactive_mode": False,  # True für Human-in-the-Loop
    # ...
}

# Critic Agent
critic.validate(draft_inject, mode=state.get("mode", "thesis"))
```

---

## Thesis Value

Für die Bachelorarbeit ist der Fokus auf den Kontrast zwischen **Player Mode** und **God Mode** wichtig, da dies den innovativen "Dungeons & Dragons"-Charakter des Systems am besten illustriert.

**Thesis-Argument:**
- Player Mode simuliert realistische Krisensituationen mit Unsicherheit
- God Mode ermöglicht wissenschaftliche Analyse und Debugging
- Die Kombination zeigt, dass das System sowohl für Training als auch für Evaluation geeignet ist

Technisch stützt sich die Thesis auf den **Thesis Mode**, um die logische Qualität sicherzustellen.


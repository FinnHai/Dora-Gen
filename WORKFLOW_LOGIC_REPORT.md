# Workflow Logic & Conditional Edges Report

**Erstellt:** 2025-12-15  
**Quelle:** `workflows/scenario_workflow.py`  
**Zweck:** Dokumentation der State Graph-Struktur und Entscheidungslogik

---

## 1. Graph-Struktur

### 1.1 Node-Definitionen

**Methode:** `_create_graph()`  
**Zeile:** 72-133

```python
def _create_graph(self) -> StateGraph:
    """Erstellt den LangGraph Workflow."""
    workflow = StateGraph(WorkflowState)
    
    # Nodes hinzufügen
    workflow.add_node("state_check", self._state_check_node)
    workflow.add_node("manager", self._manager_node)
    workflow.add_node("intel", self._intel_node)
    workflow.add_node("action_selection", self._action_selection_node)
    workflow.add_node("generator", self._generator_node)
    workflow.add_node("critic", self._critic_node)
    workflow.add_node("state_update", self._state_update_node)
    
    # Decision-Point Node (nur im interaktiven Modus)
    if self.interactive_mode:
        workflow.add_node("decision_point", self._decision_point_node)
```

### 1.2 Edge-Definitionen

#### Entry Point
```python
workflow.set_entry_point("state_check")
```

#### Sequenzielle Edges (Linear Flow)
```python
workflow.add_edge("state_check", "manager")
workflow.add_edge("manager", "intel")
workflow.add_edge("intel", "action_selection")
workflow.add_edge("action_selection", "generator")
workflow.add_edge("generator", "critic")
```

#### Conditional Edge: Critic → Refine oder Update
```python
# Conditional Edge: Critic → State Update oder Generator (Refine)
workflow.add_conditional_edges(
    "critic",
    self._should_refine,
    {
        "refine": "generator",  # Zurück zum Generator bei Fehlern
        "update": "state_update"  # Weiter bei Validierung (auch mit Warnungen)
    }
)
```

#### Conditional Edge: State Update → Decision Point oder Continue/End

**Interaktiver Modus:**
```python
if self.interactive_mode:
    workflow.add_conditional_edges(
        "state_update",
        self._should_ask_decision,
        {
            "decision": "decision_point",  # Benutzer-Entscheidung erforderlich
            "continue": "state_check",  # Weiter ohne Entscheidung
            "end": END  # End-Bedingung erreicht
        }
    )
    
    # Decision Point → State Check (nach Entscheidung)
    workflow.add_edge("decision_point", "state_check")
```

**Nicht-interaktiver Modus:**
```python
else:
    # Conditional Edge: State Update → End oder Loop (nicht-interaktiv)
    workflow.add_conditional_edges(
        "state_update",
        self._should_continue,
        {
            "continue": "state_check",  # Loop zurück
            "end": END
        }
    )
```

### 1.3 Vollständige Graph-Visualisierung

```
[START]
  ↓
[state_check]
  ↓
[manager]
  ↓
[intel]
  ↓
[action_selection]
  ↓
[generator]
  ↓
[critic]
  ↓
  ├─→ [refine] ─→ [generator] (wenn _should_refine == "refine")
  │
  └─→ [update] ─→ [state_update]
                    ↓
                    ├─→ [decision_point] ─→ [state_check] (interaktiv, wenn _should_ask_decision == "decision")
                    │
                    ├─→ [state_check] (wenn _should_ask_decision/_should_continue == "continue")
                    │
                    └─→ [END] (wenn _should_ask_decision/_should_continue == "end")
```

---

## 2. `_should_refine` Funktion

**Methode:** `_should_refine()`  
**Zeile:** 1607-1646

**Vollständiger Code:**

```python
def _should_refine(self, state: WorkflowState) -> str:
    """Entscheidet, ob Refine nötig ist."""
    iteration = state.get('iteration', 0)
    injects_count = len(state.get('injects', []))
    validation = state.get("validation_result")
    draft_inject = state.get("draft_inject")
    
    print(f"🔀 [Should Refine] Iteration {iteration}, Injects: {injects_count}")
    print(f"   Validation vorhanden: {validation is not None}")
    print(f"   Draft Inject vorhanden: {draft_inject is not None}")
    
    if not validation:
        print(f"   → Keine Validierung, gehe zu State Update")
        return "update"  # Weiter auch ohne Validierung
    
    # Refine wenn nicht valide (max. 2 Versuche pro Inject)
    if not validation.is_valid:
        metadata = state.get("metadata", {})
        current_inject_id = draft_inject.inject_id if draft_inject else None
        
        # Zähle Refine-Versuche pro Inject
        refine_key = f"refine_count_{current_inject_id}"
        refine_count = metadata.get(refine_key, 0)
        
        print(f"   ❌ Validation nicht valide")
        print(f"   Fehler: {validation.errors[:2] if validation.errors else 'Keine Details'}")
        print(f"   Refine-Versuche für {current_inject_id}: {refine_count}/2")
        
        if refine_count < 2:  # Max. 2 Refine-Versuche
            metadata[refine_key] = refine_count + 1
            print(f"   → Gehe zurück zu Generator (Refine-Versuch {refine_count + 1})")
            return "refine"
        else:
            # Nach 2 Versuchen: Akzeptiere trotzdem (mit Warnung)
            print(f"⚠️  Inject nach {refine_count} Refine-Versuchen akzeptiert (mit Warnungen)")
            print(f"   → Gehe zu State Update trotzdem")
            return "update"
    
    print(f"   ✅ Validation valide → Gehe zu State Update")
    return "update"
```

### 2.1 Entscheidungslogik

| Bedingung | Rückgabewert | Beschreibung |
|-----------|--------------|-------------|
| Keine Validierung vorhanden | `"update"` | Weiter ohne Validierung |
| `validation.is_valid == False` UND `refine_count < 2` | `"refine"` | Zurück zum Generator für Refine |
| `validation.is_valid == False` UND `refine_count >= 2` | `"update"` | Nach 2 Versuchen trotzdem akzeptieren |
| `validation.is_valid == True` | `"update"` | Valide, weiter zu State Update |

### 2.2 Refine-Count Mechanismus

**Wichtig:** Der `refine_count` wird **pro Inject** gezählt:

```python
# Zähle Refine-Versuche pro Inject
refine_key = f"refine_count_{current_inject_id}"
refine_count = metadata.get(refine_key, 0)

if refine_count < 2:  # Max. 2 Refine-Versuche
    metadata[refine_key] = refine_count + 1
    return "refine"
```

**Speicherung:** `state["metadata"][f"refine_count_{inject_id}"]`

**Beispiel:**
- Inject `INJ-001` wird generiert → `refine_count_INJ-001 = 0`
- Critic lehnt ab → `refine_count_INJ-001 = 1` → zurück zu Generator
- Critic lehnt erneut ab → `refine_count_INJ-001 = 2` → trotzdem akzeptieren
- Neuer Inject `INJ-002` → `refine_count_INJ-002 = 0` (neuer Zähler)

---

## 3. `_should_continue` Funktion

**Methode:** `_should_continue()`  
**Zeile:** 1648-1689

**Vollständiger Code:**

```python
def _should_continue(self, state: WorkflowState) -> str:
    """Entscheidet, ob Workflow fortgesetzt werden soll."""
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", self.max_iterations)
    current_phase = state.get("current_phase", CrisisPhase.NORMAL_OPERATION)
    injects = state.get("injects", [])
    errors = state.get("errors", [])
    
    # Stoppe wenn:
    # 1. Anzahl generierter Injects erreicht (HAUPTPRÜFUNG)
    if len(injects) >= max_iterations:
        print(f"🛑 Stoppe: Anzahl Injects erreicht ({len(injects)}/{max_iterations})")
        return "end"
    
    # 2. Maximale Iterationen erreicht (Fallback)
    if iteration >= max_iterations * 2:  # Erlaube mehr Iterationen für Refine-Loops
        print(f"🛑 Stoppe: Maximale Iterationen erreicht ({iteration}/{max_iterations * 2})")
        return "end"
    
    # 3. Zu viele Fehler (verhindert Endlosschleife)
    if len(errors) > 20:  # Erhöht von 10 auf 20
        print(f"🛑 Stoppe: Zu viele Fehler ({len(errors)})")
        return "end"
    
    # 4. Recovery-Phase erreicht und genug Injects generiert (mindestens 80% von max_iterations)
    if current_phase == CrisisPhase.RECOVERY:
        min_injects_for_recovery = max(3, int(max_iterations * 0.8))
        if len(injects) >= min_injects_for_recovery:
            print(f"🛑 Stoppe: Recovery-Phase erreicht mit {len(injects)} Injects (Minimum: {min_injects_for_recovery})")
            return "end"
    
    # 5. Sicherheits-Stop: Zu viele Workflow-Logs (dynamisch basierend auf max_iterations)
    # Jeder Inject benötigt ~7 Nodes + mögliche Refine-Loops (2 pro Inject) = ~9 Nodes pro Inject
    workflow_logs = state.get("workflow_logs", [])
    max_logs = max_iterations * 15  # 15 Logs pro Inject (7 Nodes + 2 Refine + Puffer)
    if len(workflow_logs) > max_logs:
        print(f"🛑 Stoppe: Sicherheitsgrenze erreicht ({len(workflow_logs)}/{max_logs} Logs)")
        return "end"
    
    # Weiter mit nächster Iteration
    print(f"➡️  Weiter: Iteration {iteration}/{max_iterations}, Injects: {len(injects)}/{max_iterations}, Logs: {len(workflow_logs)}")
    return "continue"
```

### 3.1 End-Bedingungen (Priorität)

| # | Bedingung | Rückgabewert | Beschreibung |
|---|-----------|--------------|--------------|
| **1** | `len(injects) >= max_iterations` | `"end"` | **HAUPTPRÜFUNG:** Anzahl Injects erreicht |
| **2** | `iteration >= max_iterations * 2` | `"end"` | Fallback: Maximale Iterationen erreicht (erlaubt Refine-Loops) |
| **3** | `len(errors) > 20` | `"end"` | Zu viele Fehler (verhindert Endlosschleife) |
| **4** | `phase == RECOVERY` UND `len(injects) >= max(3, int(max_iterations * 0.8))` | `"end"` | Recovery-Phase mit mindestens 80% Injects |
| **5** | `len(workflow_logs) > max_iterations * 15` | `"end"` | Sicherheits-Stop: Zu viele Logs |

### 3.2 Berechnungen

**Recovery-Minimum:**
```python
min_injects_for_recovery = max(3, int(max_iterations * 0.8))
```
- Beispiel: `max_iterations = 10` → `min_injects_for_recovery = 8`
- Beispiel: `max_iterations = 5` → `min_injects_for_recovery = 3` (Minimum)

**Max Logs:**
```python
max_logs = max_iterations * 15  # 15 Logs pro Inject (7 Nodes + 2 Refine + Puffer)
```
- Beispiel: `max_iterations = 10` → `max_logs = 150`

**Max Iterations (mit Refine-Loops):**
```python
if iteration >= max_iterations * 2:  # Erlaube mehr Iterationen für Refine-Loops
```
- Beispiel: `max_iterations = 10` → `max_iteration_limit = 20`

---

## 4. State Passing: `user_feedback` an Generator

### 4.1 Extraktion aus State

**Methode:** `_generator_node()`  
**Zeile:** 558-571

```python
# Hole user_feedback aus State (Human-in-the-Loop)
user_feedback = state.get("user_feedback")

inject = self.generator_agent.generate_inject(
    scenario_type=state["scenario_type"],
    phase=state["current_phase"],
    inject_id=inject_id,
    time_offset=time_offset,
    manager_plan=manager_plan,
    selected_ttp=selected_ttp,
    system_state=state["system_state"],
    previous_injects=state["injects"],
    validation_feedback=validation_feedback,
    user_feedback=user_feedback  # ← Hier wird user_feedback übergeben
)
```

### 4.2 State-Update nach Benutzer-Entscheidung

**Methode:** `_apply_user_decision()`  
**Zeile:** 1105-1179

**Wichtig:** `user_feedback` wird **nicht direkt** in `_apply_user_decision` gesetzt, sondern indirekt über `user_decisions`:

```python
def _apply_user_decision(self, state: WorkflowState, decision: Dict[str, Any]) -> Dict[str, Any]:
    """Wendet eine Benutzer-Entscheidung auf den State an und generiert entsprechende Events."""
    choice_id = decision.get("choice_id")
    decision_type = decision.get("decision_type")
    
    # ... Entscheidung wird verarbeitet ...
    
    # Speichere Entscheidung mit Impact
    user_decisions = state.get("user_decisions", [])
    user_decisions.append({
        **decision,
        "applied_impact": impact,
        "assets_protected": protected_count,
        "timestamp": datetime.now().isoformat()
    })
    state["user_decisions"] = user_decisions
    state["system_state"] = system_state
    
    return state
```

### 4.3 `user_feedback` Setzung (Externe Quelle)

**Hinweis:** `user_feedback` wird **extern** gesetzt, z.B. durch:
- Frontend/API-Call
- Dashboard-Interaktion
- Direkte State-Manipulation

**Typischer Flow:**

1. **Benutzer gibt Feedback:** `"Shutdown SRV-001"` oder `"Isolate compromised systems"`
2. **State wird aktualisiert:** `state["user_feedback"] = "Shutdown SRV-001"`
3. **Generator Node liest:** `user_feedback = state.get("user_feedback")`
4. **Generator verwendet Feedback:** Siehe `agents/generator_agent.py` Zeile 258-273

### 4.4 Generator-Verwendung von `user_feedback`

**Aus `agents/generator_agent.py` (Zeile 258-273):**

```python
# User Feedback Formatierung (Human-in-the-Loop)
user_feedback_section = ""
if user_feedback and user_feedback.strip():
    user_feedback_section = f"""
### HUMAN RESPONSE TO LAST INJECT:
The Incident Response Team performed the following action: "{user_feedback}"

INSTRUCTION:
The next Inject MUST reflect the consequences of this action.
- If they mitigated the threat (e.g., isolated server, blocked IP, shutdown service) → Show recovery or a new, different attack vector.
- If they ignored it or took insufficient action → Escalate the crisis drastically.
- If they took defensive action → Show how the attacker adapts or how the system responds.
- Be realistic: Actions have consequences. If SRV-001 was shut down, it cannot be attacked in the next inject, but services depending on it may be affected.

CRITICAL: The inject content must logically follow from the response action. Do not ignore the human action."""
```

### 4.5 Vollständiger Flow: `user_feedback` → Generator

```
[Benutzer gibt Feedback]
  ↓
state["user_feedback"] = "Shutdown SRV-001"
  ↓
[State Check Node] (lädt State)
  ↓
[Manager Node]
  ↓
[Intel Node]
  ↓
[Action Selection Node]
  ↓
[Generator Node]
  ↓
  user_feedback = state.get("user_feedback")  # ← Extraktion
  ↓
  generator_agent.generate_inject(
      ...,
      user_feedback=user_feedback  # ← Übergabe
  )
  ↓
[Generator verwendet Feedback im Prompt]
  ↓
[Nächster Inject reflektiert Benutzer-Aktion]
```

---

## 5. Zusätzliche Entscheidungsfunktionen

### 5.1 `_should_ask_decision` (Interaktiver Modus)

**Methode:** `_should_ask_decision()`  
**Zeile:** 1200-1250

**Vereinfachte Logik:**

```python
def _should_ask_decision(self, state: WorkflowState) -> str:
    """Entscheidet, ob eine Benutzer-Entscheidung erforderlich ist."""
    # ... Prüfungen ...
    
    # Entscheidung erforderlich nach jedem 2. Inject
    decision_points = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
    if injects_count in decision_points:
        return "decision"
    
    # Entscheidung bei kritischen Phasen
    if current_phase in [CrisisPhase.ESCALATION_CRISIS, CrisisPhase.CONTAINMENT]:
        # ... Prüfe ob bereits Entscheidung für Phase getroffen ...
        return "decision"
    
    # Normale Continue-Logik
    if injects_count >= max_iterations:
        return "end"
    
    return "continue"
```

**Rückgabewerte:**
- `"decision"`: Benutzer-Entscheidung erforderlich
- `"continue"`: Weiter ohne Entscheidung
- `"end"`: End-Bedingung erreicht

---

## Zusammenfassung: Entscheidungslogik

### Refine-Logik (`_should_refine`)

| Input | Bedingung | Output | Ziel-Node |
|-------|-----------|--------|-----------|
| Keine Validierung | - | `"update"` | `state_update` |
| Nicht valide | `refine_count < 2` | `"refine"` | `generator` |
| Nicht valide | `refine_count >= 2` | `"update"` | `state_update` |
| Valide | - | `"update"` | `state_update` |

### Continue-Logik (`_should_continue`)

| Bedingung | Output | Ziel-Node |
|-----------|--------|-----------|
| `len(injects) >= max_iterations` | `"end"` | `END` |
| `iteration >= max_iterations * 2` | `"end"` | `END` |
| `len(errors) > 20` | `"end"` | `END` |
| `phase == RECOVERY` UND `len(injects) >= min_injects` | `"end"` | `END` |
| `len(workflow_logs) > max_logs` | `"end"` | `END` |
| Sonst | `"continue"` | `state_check` |

### State Passing: `user_feedback`

1. **Setzung:** Extern (Frontend/API)
2. **Extraktion:** `_generator_node()` → `state.get("user_feedback")`
3. **Übergabe:** `generator_agent.generate_inject(..., user_feedback=user_feedback)`
4. **Verwendung:** Generator integriert Feedback in Prompt für nächsten Inject

---

**Ende des Berichts**

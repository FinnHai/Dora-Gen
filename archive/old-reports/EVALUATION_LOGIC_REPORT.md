# Evaluation Logic Report

**Erstellt:** 2025-12-15  
**Quelle:** `dashboard.py` (Tab 2 Logic) und `evaluation/`  
**Zweck:** Dokumentation der Erfolgsmessung und A/B Testing Logik

---

## 1. A/B Testing Loop

### 1.1 Code-Block: `run_batch_evaluation`

**Methode:** `run_batch_evaluation()`  
**Zeile:** 998-1112 in `dashboard.py`

**Vollständiger Code-Block:**

```python
def run_batch_evaluation(scenario_type: ScenarioType, num_scenarios: int = 50):
    """
    Führt A/B Testing Batch-Evaluation aus.
    
    Für jedes Szenario:
    - Run A (Legacy): mode='legacy' (Skip Validation)
    - Run B (Thesis): mode='thesis' (Full Validation)
    - Vergleich: Welche Fehler wurden im Legacy Mode übersehen?
    """
    if not BACKEND_AVAILABLE or st.session_state.workflow is None:
        st.error("Backend not available for batch evaluation.")
        return
    
    st.session_state.batch_running = True
    st.session_state.batch_results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(num_scenarios):
        try:
            scenario_base_id = f"SCEN-{i:03d}"
            
            # ===== RUN A: LEGACY MODE (Skip Validation) =====
            status_text.text(f"Scenario {i+1}/{num_scenarios}: Running Legacy Mode...")
            result_legacy = st.session_state.workflow.generate_scenario(
                scenario_type=scenario_type,
                scenario_id=f"{scenario_base_id}-LEGACY",
                mode='legacy'  # ← MODE FLAG SETZUNG
            )
            
            legacy_injects = result_legacy.get('injects', [])
            legacy_errors = result_legacy.get('errors', [])
            legacy_warnings = result_legacy.get('warnings', [])
            
            # ... Hallucination Counting (siehe Abschnitt 2) ...
            
            # ===== RUN B: THESIS MODE (Full Validation) =====
            status_text.text(f"Scenario {i+1}/{num_scenarios}: Running Thesis Mode...")
            result_thesis = st.session_state.workflow.generate_scenario(
                scenario_type=scenario_type,
                scenario_id=f"{scenario_base_id}-THESIS",
                mode='thesis'  # ← MODE FLAG SETZUNG
            )
            
            thesis_injects = result_thesis.get('injects', [])
            thesis_errors = result_thesis.get('errors', [])
            thesis_warnings = result_thesis.get('warnings', [])
            
            # ... Vergleich und Metrik-Berechnung (siehe Abschnitt 2) ...
            
        except Exception as e:
            st.warning(f"Error in scenario {i+1}: {e}")
            continue
    
    st.session_state.batch_running = False
    # ... Ergebnis-Visualisierung ...
```

### 1.2 Mode Flag Setzung

**Wichtig:** Der `mode` Parameter wird **direkt** an `workflow.generate_scenario()` übergeben:

| Run | Mode Value | Beschreibung | Zeile |
|-----|------------|--------------|-------|
| **Run A (Legacy)** | `'legacy'` | Skip Validation (simuliert altes System ohne Logic Guard) | 1026 |
| **Run B (Thesis)** | `'thesis'` | Full Validation (vollständige Validierung mit Critic Agent) | 1055 |

**Code-Auszug:**

```python
# Legacy Mode
result_legacy = st.session_state.workflow.generate_scenario(
    scenario_type=scenario_type,
    scenario_id=f"{scenario_base_id}-LEGACY",
    mode='legacy'  # ← Skip Validation
)

# Thesis Mode
result_thesis = st.session_state.workflow.generate_scenario(
    scenario_type=scenario_type,
    scenario_id=f"{scenario_base_id}-THESIS",
    mode='thesis'  # ← Full Validation
)
```

### 1.3 Mode-Weiterleitung im Workflow

**In `workflows/scenario_workflow.py` (Zeile 1706-1751):**

Der `mode` Parameter wird im `initial_state` gesetzt:

```python
initial_state: WorkflowState = {
    # ... andere Felder ...
    "mode": mode  # 'legacy' oder 'thesis'
}
```

**In `agents/critic_agent.py` (Zeile 47-80):**

Der Critic Agent prüft den Mode:

```python
def validate_inject(
    self,
    inject: Inject,
    previous_injects: List[Inject],
    current_phase: CrisisPhase,
    system_state: Dict[str, Any],
    mode: str = 'thesis'  # ← Mode Parameter
) -> ValidationResult:
    # LEGACY MODE: Skip Validation komplett
    if mode == 'legacy':
        print(f"[Critic] Legacy Mode: Skipping validation for {inject.inject_id}")
        return ValidationResult(
            is_valid=True,  # ← Immer True im Legacy Mode!
            logical_consistency=True,
            dora_compliance=True,
            causal_validity=True,
            errors=[],
            warnings=[]
        )
    
    # THESIS MODE: Vollständige Validierung
    # ... normale Validierungslogik ...
```

**Zusammenfassung:**
- `mode='legacy'` → Critic gibt immer `is_valid=True` zurück (keine Validierung)
- `mode='thesis'` → Critic führt vollständige Validierung durch

---

## 2. Metrik-Berechnung: "Hallucinations Prevented"

### 2.1 Hallucination Counting (Legacy Mode)

**Zeile:** 1033-1048 in `dashboard.py`

```python
# Zähle Hallucinations im Legacy Mode (Assets die nicht existieren)
legacy_hallucinations = 0
legacy_workflow_logs = result_legacy.get('workflow_logs', [])

# Prüfe auf invalid assets in Legacy Injects
system_state_assets = set()
if result_legacy.get('system_state'):
    system_state_assets = set(k for k in result_legacy['system_state'].keys() 
                             if not k.startswith(("INJ-", "SCEN-")))

for inject in legacy_injects:
    if hasattr(inject, 'technical_metadata') and inject.technical_metadata:
        affected = inject.technical_metadata.affected_assets or []
        for asset in affected:
            if asset not in system_state_assets and asset:
                legacy_hallucinations += 1
```

**Logik:**
1. Extrahiere alle verfügbaren Asset-IDs aus `system_state` (filtere INJ-* und SCEN-* IDs)
2. Iteriere über alle Legacy-Injects
3. Prüfe für jedes `affected_asset`: Existiert es in `system_state_assets`?
4. Wenn **NICHT** → Zähle als Hallucination

### 2.2 Hallucination Counting (Thesis Mode)

**Zeile:** 1068-1078 in `dashboard.py`

```python
# Zähle Hallucinations im Thesis Mode (sollten weniger sein)
thesis_hallucinations = 0
if result_thesis.get('system_state'):
    thesis_system_state_assets = set(k for k in result_thesis['system_state'].keys() 
                                    if not k.startswith(("INJ-", "SCEN-")))
    for inject in thesis_injects:
        if hasattr(inject, 'technical_metadata') and inject.technical_metadata:
            affected = inject.technical_metadata.affected_assets or []
            for asset in affected:
                if asset not in thesis_system_state_assets and asset:
                    thesis_hallucinations += 1
```

**Logik:** Identisch zu Legacy Mode, aber auf Thesis-Injects angewendet.

### 2.3 Berechnung: "Hallucinations Prevented"

**Zeile:** 1080-1082 in `dashboard.py`

```python
# Vergleich: Fehler die Legacy übersehen hat
errors_missed_by_legacy = legacy_hallucinations - thesis_hallucinations
hallucinations_prevented = max(0, errors_missed_by_legacy)
```

**Formel:**
```
hallucinations_prevented = max(0, legacy_hallucinations - thesis_hallucinations)
```

**Erklärung:**
- **`errors_missed_by_legacy`**: Differenz zwischen Legacy- und Thesis-Hallucinations
- **`hallucinations_prevented`**: Anzahl der Hallucinations, die durch Thesis Mode verhindert wurden
- **`max(0, ...)`**: Verhindert negative Werte (falls Thesis Mode mehr Hallucinations hätte)

**Beispiel:**
- Legacy Mode: 15 Hallucinations
- Thesis Mode: 3 Hallucinations
- `errors_missed_by_legacy = 15 - 3 = 12`
- `hallucinations_prevented = max(0, 12) = 12`

### 2.4 Speicherung im Batch-Ergebnis

**Zeile:** 1084-1097 in `dashboard.py`

```python
st.session_state.batch_results.append({
    "scenario_id": scenario_base_id,
    "legacy_injects": len(legacy_injects),
    "legacy_errors": len(legacy_errors),
    "legacy_warnings": len(legacy_warnings),
    "legacy_hallucinations": legacy_hallucinations,
    "thesis_injects": len(thesis_injects),
    "thesis_errors": len(thesis_errors),
    "thesis_warnings": len(thesis_warnings),
    "thesis_refines": thesis_refines,
    "thesis_hallucinations": thesis_hallucinations,
    "hallucinations_prevented": hallucinations_prevented,  # ← Hauptmetrik
    "errors_missed_by_legacy": errors_missed_by_legacy
})
```

### 2.5 Visualisierung der Metrik

**Zeile:** 1127-1140 in `dashboard.py`

```python
# A/B Comparison Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_prevented = df["hallucinations_prevented"].sum()
    st.metric("Hallucinations Prevented", total_prevented)

with col2:
    avg_legacy_hallucinations = df["legacy_hallucinations"].mean()
    st.metric("Avg Legacy Hallucinations", f"{avg_legacy_hallucinations:.1f}")

with col3:
    avg_thesis_hallucinations = df["thesis_hallucinations"].mean()
    st.metric("Avg Thesis Hallucinations", f"{avg_thesis_hallucinations:.1f}")

with col4:
    reduction_pct = ((avg_legacy_hallucinations - avg_thesis_hallucinations) / avg_legacy_hallucinations * 100) if avg_legacy_hallucinations > 0 else 0
    st.metric("Reduction %", f"{reduction_pct:.1f}%")
```

**Zusätzliche Metriken:**
- **Total Prevented**: Summe aller `hallucinations_prevented` über alle Szenarien
- **Avg Legacy Hallucinations**: Durchschnittliche Hallucinations pro Szenario (Legacy Mode)
- **Avg Thesis Hallucinations**: Durchschnittliche Hallucinations pro Szenario (Thesis Mode)
- **Reduction %**: Prozentuale Reduktion: `((legacy - thesis) / legacy) * 100`

---

## 3. "Seed Chaos" Button

### 3.1 Button-Definition

**Zeile:** 1233-1245 in `dashboard.py`

```python
# Database Seeding (Stress Test)
st.subheader("Database Management")
if BACKEND_AVAILABLE and st.session_state.neo4j_client:
    if st.button("Seed Chaos (40 Assets)", width='stretch', type="secondary"):
        try:
            with st.spinner("Seeding enterprise infrastructure (this will clear all existing data)..."):
                num_assets = st.session_state.neo4j_client.seed_enterprise_infrastructure()
                st.success("Infrastructure expanded to Enterprise Scale!")
                st.info(f"✅ Successfully seeded {num_assets} assets (5 Core Servers, 15 App Servers, 10 Databases, 10 Workstations)")
                # Refresh system state
                st.session_state.system_state = get_assets_from_backend()
                st.rerun()
        except Exception as e:
            st.error(f"Seeding failed: {e}")
            import traceback
            st.error(traceback.format_exc())
else:
    st.info("Backend not available for seeding")
```

### 3.2 Backend-Verbindung

**Bestätigt:** Der Button ruft direkt die Backend-Funktion auf:

```python
num_assets = st.session_state.neo4j_client.seed_enterprise_infrastructure()
```

**Backend-Funktion:** `neo4j_client.py` → `seed_enterprise_infrastructure()`  
**Zeile:** 507-646 in `neo4j_client.py`

### 3.3 Funktionsweise

1. **Button-Klick** → `st.button("Seed Chaos (40 Assets)")`
2. **Backend-Call** → `neo4j_client.seed_enterprise_infrastructure()`
3. **Datenbank-Operation:**
   - Löscht alle bestehenden Entities: `MATCH (n) DETACH DELETE n`
   - Erstellt genau 40 Assets (siehe `DATABASE_ARCHITECTURE_REPORT.md`)
4. **State-Refresh** → `st.session_state.system_state = get_assets_from_backend()`
5. **UI-Update** → `st.rerun()`

### 3.4 Rückgabewert

Die Funktion gibt die Anzahl der erstellten Assets zurück:

```python
return len(enterprise_assets)  # Sollte immer 40 sein
```

**Erwartete Assets:**
- 5 Core Servers (SRV-CORE-001 bis 005)
- 15 Application Servers (SRV-APP-001 bis 015)
- 5 Production Databases (DB-PROD-01 bis 05)
- 5 Development Databases (DB-DEV-01 bis 05)
- 10 Finance Workstations (WS-FINANCE-01 bis 10)

**Gesamt:** 40 Assets

---

## 4. Zusammenfassung: Erfolgsmessung

### 4.1 A/B Testing Flow

```
Für jedes Szenario (i = 0 bis num_scenarios-1):
  │
  ├─→ Run A: Legacy Mode
  │   ├─ mode='legacy'
  │   ├─ Critic: Skip Validation (is_valid=True)
  │   └─ Zähle: legacy_hallucinations
  │
  ├─→ Run B: Thesis Mode
  │   ├─ mode='thesis'
  │   ├─ Critic: Full Validation
  │   └─ Zähle: thesis_hallucinations
  │
  └─→ Berechne: hallucinations_prevented = max(0, legacy - thesis)
```

### 4.2 Metrik-Definitionen

| Metrik | Formel | Beschreibung |
|--------|--------|--------------|
| **Hallucinations Prevented** | `max(0, legacy_hallucinations - thesis_hallucinations)` | Anzahl verhinderter Hallucinations |
| **Reduction %** | `((legacy - thesis) / legacy) * 100` | Prozentuale Reduktion |
| **Legacy Hallucinations** | Anzahl nicht-existierender Assets in Legacy-Injects | Fehler im Legacy Mode |
| **Thesis Hallucinations** | Anzahl nicht-existierender Assets in Thesis-Injects | Fehler im Thesis Mode |

### 4.3 Seed Chaos Button

| Aspekt | Details |
|--------|---------|
| **Location** | Tab 1 (Live Simulation) → Sidebar → Database Management |
| **Button Text** | "Seed Chaos (40 Assets)" |
| **Backend Call** | `neo4j_client.seed_enterprise_infrastructure()` |
| **Erstellt** | 40 Assets (5 Core + 15 App + 10 DB + 10 WS) |
| **Löscht** | Alle bestehenden Entities vor Seeding |
| **Rückgabewert** | Anzahl erstellter Assets (40) |

---

## 5. CSV-Export

**Zeile:** 1119 in `dashboard.py`

```python
# Speichere Ergebnisse als CSV
df.to_csv("experiment_results.csv", index=False)
st.success(f"Results saved to experiment_results.csv")
```

**CSV-Spalten:**
- `scenario_id`
- `legacy_injects`
- `legacy_errors`
- `legacy_warnings`
- `legacy_hallucinations`
- `thesis_injects`
- `thesis_errors`
- `thesis_warnings`
- `thesis_refines`
- `thesis_hallucinations`
- `hallucinations_prevented` ← **Hauptmetrik**
- `errors_missed_by_legacy`

---

**Ende des Berichts**

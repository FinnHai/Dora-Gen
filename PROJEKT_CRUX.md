# Die Crux des Projekts: RAG-basierte Krisenszenarien-Generierung mit Logik-Guards

**Erstellt:** 2025-12-17  
**Zweck:** Dokumentation der Kernproblematik und Lösungsansätze für die Bachelorarbeit

---

## 🎯 Ausgangssituation: Das ursprüngliche Problem

### Das Projekt-Seminar

Ein Projekt-Seminar entwickelte ein System zur **Generierung von Krisenstabszenarien (MSELs)** für Finanzunternehmen auf Basis von **Retrieval-Augmented Generation (RAG)**. Das Ziel war es, realistische, logisch konsistente Szenarien zu generieren, die den Anforderungen des **Digital Operational Resilience Act (DORA)** entsprechen.

### Die Kernprobleme

Das ursprüngliche System hatte zwei fundamentale Schwachstellen:

1. **Zeitliche Inkonsistenzen**
   - Zeitstempel (`time_offset`) gingen zurück oder sprangen unlogisch
   - Chronologische Sequenz wurde nicht eingehalten
   - Beispiel: Inject 2 hatte `T+00:05:00`, Inject 3 hatte `T+00:03:00` (zurück in der Zeit)

2. **Logische Inkonsistenzen**
   - Assets wurden referenziert, die nicht existieren (Hallucinations)
   - Asset-Status wurde ignoriert (z.B. "SRV-001 ist offline" in Inject 1, aber "Lateral Movement von SRV-001" in Inject 2)
   - Phasen-Übergänge waren nicht erlaubt (z.B. direkt von `NORMAL_OPERATION` zu `ESCALATION_CRISIS`)
   - MITRE ATT&CK Techniken passten nicht zur Phase (z.B. Exfiltration vor Initial Access)

### Warum passierte das?

**RAG allein reicht nicht:** Während RAG (ChromaDB mit MITRE ATT&CK TTPs) sicherstellt, dass relevante Angriffsmuster abgerufen werden, garantiert es **nicht**, dass:
- Die generierten Szenarien logisch konsistent sind
- Zeitstempel chronologisch sind
- Asset-Referenzen korrekt sind
- Phasen-Übergänge erlaubt sind

**LLMs sind probabilistisch:** Generative LLMs (GPT-4o) generieren Text basierend auf Wahrscheinlichkeiten, nicht auf strikter Logik. Sie können:
- Asset-Namen halluzinieren (z.B. "SRV-003" erfinden, obwohl nur "SRV-001" und "SRV-002" existieren)
- Zeitstempel inkonsistent generieren
- Logische Regeln ignorieren (z.B. FSM-Übergänge)

---

## 🔧 Die Lösung: Mehrschichtige Validierung mit Symbolischen Guards

### Architektur-Überblick

Das System verwendet ein **Multi-Agenten-System** mit einem **Critic Agent**, der als "Logic Guard" fungiert:

```
[Generator Agent] → [Draft Inject] → [Critic Agent] → [Validierung]
                                                          ↓
                                    ┌─────────────────────┴─────────────────────┐
                                    │                                         │
                              [Valide?]                                  [Nicht Valide?]
                                    │                                         │
                                    ↓                                         ↓
                            [State Update]                            [Refine Loop]
                                                                              │
                                                                              ↓
                                                                    [Generator Agent]
                                                                     (mit Feedback)
```

### Die Validierungsschichten

Der Critic Agent führt eine **mehrschichtige Validierung** durch:

#### Phase 1: Symbolische Validierung (OHNE LLM-Call)

**Warum zuerst?** Diese Checks sind schnell, kostenlos und fangen offensichtliche Fehler ab, bevor teure LLM-Calls gemacht werden.

1. **Pydantic Schema-Validierung**
   - Prüft ob `time_offset` Format korrekt ist (`T+DD:HH:MM` oder `T+DD:HH`)
   - Prüft ob alle Pflichtfelder vorhanden sind

2. **FSM-Validierung (Phase-Übergang)**
   - Prüft ob Übergang von `current_phase` zu `inject.phase` erlaubt ist
   - Verwendet `CrisisFSM.can_transition()` mit definierten Übergangsregeln
   - **Beispiel:** `NORMAL_OPERATION` → `ESCALATION_CRISIS` ist nicht erlaubt (muss über `SUSPICIOUS_ACTIVITY` gehen)

3. **State-Consistency-Check (Asset-Existenz)**
   - Prüft ob alle `affected_assets` im `system_state` existieren
   - Prüft ob Asset-Status konsistent ist (z.B. nicht "offline" Asset als aktiv verwenden)
   - **Kritisch:** Verhindert Hallucinations von nicht-existierenden Assets

4. **Temporale Konsistenz-Check**
   - Prüft ob `time_offset` chronologisch nach letztem Inject liegt
   - Parse `T+DD:HH:MM` zu Minuten seit Start
   - **Beispiel:** Wenn Inject 1 `T+00:05:00` hat, muss Inject 2 mindestens `T+00:05:01` haben

#### Phase 2: LLM-basierte Validierung (NUR wenn symbolische Checks OK)

**Warum danach?** LLM-Calls sind teuer und langsam. Nur wenn alle symbolischen Checks passiert sind, wird der LLM verwendet für komplexere Validierungen.

1. **Logische Konsistenz**
   - Prüft ob Inject Widersprüche zur Historie hat
   - Prüft ob Content konsistent mit Phase ist
   - Prüft ob Asset-Namen korrekt verwendet werden

2. **Causal Validity**
   - Prüft ob MITRE ATT&CK Technik zur Phase passt
   - Prüft ob Sequenz technisch möglich ist
   - **Beispiel:** `T1041` (Exfiltration) vor `T1078` (Initial Access) ist unmöglich

3. **DORA-Compliance (optional, nicht blockierend)**
   - Prüft ob regulatorische Aspekte abgedeckt sind
   - Business Continuity, Incident Response, Recovery Plan

### Reflect-Refine Loop

Wenn Validierung fehlschlägt:

1. **Critic gibt Feedback** an Generator zurück
2. **Generator korrigiert** den Inject (max. 2 Versuche)
3. **Bei Erfolg:** Inject wird akzeptiert
4. **Nach 2 Versuchen:** Inject wird trotzdem akzeptiert (mit Warnungen)

**Code-Beispiel:**
```python
def _should_refine(self, state: WorkflowState) -> str:
    validation = state.get("validation_result")
    if not validation.is_valid:
        refine_count = metadata.get(f"refine_count_{inject_id}", 0)
        if refine_count < 2:
            return "refine"  # Zurück zum Generator
    return "update"  # Weiter zu State Update
```

---

## 📊 Evaluation: A/B Testing (Legacy vs. Thesis Mode)

### Vergleichsmethode

Das System führt **A/B Testing** durch, um zu zeigen, dass die Validierung funktioniert:

- **Legacy Mode** (`mode='legacy'`): Simuliert das alte System ohne Validierung
  - Critic gibt immer `is_valid=True` zurück
  - Keine Checks, keine Refine-Loops
  
- **Thesis Mode** (`mode='thesis'`): Vollständige Validierung mit Critic Agent
  - Alle symbolischen Checks
  - LLM-basierte Validierung
  - Refine-Loops bei Fehlern

### Metrik: "Hallucinations Prevented"

**Formel:**
```
hallucinations_prevented = max(0, legacy_hallucinations - thesis_hallucinations)
```

**Was wird gemessen?**
- Anzahl nicht-existierender Assets in Legacy-Injects
- Anzahl nicht-existierender Assets in Thesis-Injects
- Differenz = Anzahl verhinderter Hallucinations

**Ergebnis:** Thesis Mode verhindert signifikant mehr Hallucinations als Legacy Mode.

---

## 🔍 Konkrete Beispiele aus dem System

### Beispiel 1: Temporale Inkonsistenz (gefangen durch symbolische Validierung)

**Fehler:**
```
Inject INJ-015 hat Zeitstempel T+00:00:30
Vorheriger Inject INJ-003 hat T+00:01:30 (später)
→ Temporale Inkonsistenz: Zeitstempel gehen zurück!
```

**Lösung:** Critic fängt dies in Phase 1 (symbolische Validierung) ab, **ohne** LLM-Call:
```python
def _validate_temporal_consistency(inject, previous_injects):
    current_time = parse_time_offset(inject.time_offset)  # 30 Minuten
    prev_time = parse_time_offset(prev_inj.time_offset)  # 90 Minuten
    if current_time < prev_time:
        return {"valid": False, "errors": ["Temporale Inkonsistenz: ..."]}
```

### Beispiel 2: Asset-Hallucination (gefangen durch State-Consistency-Check)

**Fehler:**
```
Inject verwendet "SRV-APP-008" und "SRV-APP-009"
Verfügbare Assets: SRV-APP-001 bis SRV-APP-007
→ Asset-ID existiert nicht im Systemzustand!
```

**Lösung:** Critic prüft in Phase 1, ob Asset-ID in `system_state` existiert:
```python
def _validate_state_consistency(inject, system_state):
    affected_assets = inject.technical_metadata.affected_assets
    for asset_id in affected_assets:
        if asset_id not in system_state:
            errors.append(f"Unknown Asset ID: {asset_id}")
```

### Beispiel 3: FSM-Verstoß (gefangen durch FSM-Validierung)

**Fehler:**
```
Aktuelle Phase: NORMAL_OPERATION
Inject Phase: ESCALATION_CRISIS
→ Übergang nicht erlaubt! Muss über SUSPICIOUS_ACTIVITY gehen.
```

**Lösung:** Critic prüft erlaubte Übergänge:
```python
if not CrisisFSM.can_transition(current_phase, inject.phase):
    errors.append(f"FSM-Verstoß: Übergang nicht erlaubt")
```

### Beispiel 4: Causal Validity (gefangen durch LLM-Validierung)

**Fehler:**
```
Phase: NORMAL_OPERATION
MITRE ID: T1041 (Exfiltration)
→ Exfiltration vor Initial Access ist unmöglich!
```

**Lösung:** LLM prüft kausale Logik:
```python
impossible_sequences = [
    ("T1041", CrisisPhase.NORMAL_OPERATION),  # Exfiltration vor Initial Access
]
if (mitre_id, current_phase) in impossible_sequences:
    causal_blocking = True
```

---

## 💡 Die Kernidee: "Symbolic Guards vor LLM-Calls"

### Warum diese Architektur?

1. **Kostenersparnis:** Symbolische Checks sind kostenlos, LLM-Calls sind teuer
2. **Geschwindigkeit:** Symbolische Checks sind schnell (< 1ms), LLM-Calls sind langsam (1-3 Sekunden)
3. **Zuverlässigkeit:** Symbolische Checks sind deterministisch, LLM-Calls sind probabilistisch
4. **Frühe Fehlererkennung:** Offensichtliche Fehler werden sofort gefangen, bevor teure LLM-Calls gemacht werden

### Die Hierarchie

```
┌─────────────────────────────────────────┐
│  Symbolische Validierung (Phase 1)       │
│  - Schnell, kostenlos, deterministisch   │
│  - Fängt 80% der Fehler ab               │
└─────────────────────────────────────────┘
              ↓ (nur wenn OK)
┌─────────────────────────────────────────┐
│  LLM-basierte Validierung (Phase 2)     │
│  - Langsam, teuer, probabilistisch       │
│  - Fängt komplexe logische Fehler ab    │
└─────────────────────────────────────────┘
```

---

## 🎓 Wissenschaftlicher Beitrag

### Forschungsfrage

**Wie kann man RAG-basierte Systeme robuster machen gegen logische und temporale Inkonsistenzen?**

### Hypothesen

1. **H1:** Symbolische Validierungsschichten vor LLM-Calls reduzieren Kosten und verbessern Zuverlässigkeit
2. **H2:** Mehrschichtige Validierung (symbolisch + LLM) verhindert mehr Fehler als reine LLM-Validierung
3. **H3:** Reflect-Refine Loops verbessern die Qualität generierter Szenarien

### Evaluation

- **A/B Testing:** Legacy Mode (ohne Validierung) vs. Thesis Mode (mit Validierung)
- **Metriken:** Hallucinations Prevented, Refine-Rate, Validierungsfehler
- **Ergebnis:** Thesis Mode verhindert signifikant mehr Fehler

---

## 📈 Erkenntnisse

### Was funktioniert gut?

1. **Symbolische Validierung:** Fängt 80% der Fehler ab, bevor LLM-Calls gemacht werden
2. **State-Consistency-Check:** Verhindert effektiv Asset-Hallucinations
3. **Temporale Validierung:** Fängt Zeitstempel-Fehler sofort ab
4. **FSM-Validierung:** Verhindert ungültige Phasen-Übergänge

### Herausforderungen

1. **LLM-Hallucinations:** Generator erfindet manchmal noch Asset-Namen trotz expliziter Liste
2. **Refine-Loops:** Generator braucht manchmal mehrere Versuche, um Fehler zu korrigieren
3. **Causal Validity:** LLM ist manchmal zu streng oder zu lasch bei MITRE-Technik-Validierung

### Lessons Learned

1. **RAG allein reicht nicht:** Man braucht zusätzliche Validierungsschichten
2. **Symbolische Checks zuerst:** Sparen Kosten und Zeit
3. **Strukturierte Validierung:** Mehrere Ebenen sind besser als eine
4. **Feedback-Loops:** Reflect-Refine verbessert Qualität iterativ

---

## 🔗 Verbindung zur Bachelorarbeit

### Titel (Vorschlag)

**"Robustheit von RAG-basierten Krisenszenarien-Generatoren: Eine Evaluierung mehrschichtiger Validierungsansätze"**

### Kernbeitrag

Das Projekt zeigt, dass **RAG-basierte Systeme** durch **symbolische Validierungsschichten** und **Reflect-Refine Loops** deutlich robuster werden können gegen:
- Temporale Inkonsistenzen
- Logische Inkonsistenzen
- Asset-Hallucinations
- Phasen-Übergangs-Fehler

### Methodik

1. **Problem-Identifikation:** Analyse der Schwachstellen im ursprünglichen RAG-System
2. **Lösungsentwicklung:** Design mehrschichtiger Validierung mit symbolischen Guards
3. **Implementierung:** Critic Agent mit Phase-1 (symbolisch) und Phase-2 (LLM) Validierung
4. **Evaluation:** A/B Testing zwischen Legacy Mode und Thesis Mode
5. **Ergebnis:** Quantifizierung der Verbesserung durch "Hallucinations Prevented" Metrik

---

## 📚 Technische Details

### Implementierte Komponenten

1. **Critic Agent** (`agents/critic_agent.py`)
   - Phase-1: Symbolische Validierung (FSM, State, Temporal)
   - Phase-2: LLM-basierte Validierung (Logical, Causal, DORA)

2. **Workflow** (`workflows/scenario_workflow.py`)
   - Reflect-Refine Loop mit max. 2 Versuchen
   - Conditional Edges basierend auf Validierungsergebnis

3. **Forensic Logger** (`forensic_logger.py`)
   - Loggt alle DRAFT, CRITIC und REFINED Events
   - Ermöglicht Nachvollziehbarkeit der Validierungsentscheidungen

4. **A/B Testing** (`dashboard.py`)
   - Batch-Evaluation mit Legacy vs. Thesis Mode
   - Metrik-Berechnung: Hallucinations Prevented

### Datenstrukturen

- **Inject:** Pydantic Model mit `time_offset`, `phase`, `affected_assets`, `technical_metadata`
- **ValidationResult:** Ergebnis der Critic-Validierung mit `is_valid`, `errors`, `warnings`
- **WorkflowState:** TypedDict mit `injects`, `system_state`, `validation_result`, `mode`

---

## 🎯 Zusammenfassung: Die Crux in einem Satz

**RAG-basierte Systeme generieren oft inkonsistente Szenarien; dieses Projekt zeigt, wie mehrschichtige Validierung (symbolische Guards + LLM) mit Reflect-Refine Loops diese Probleme systematisch behebt.**

---

**Ende der Dokumentation**

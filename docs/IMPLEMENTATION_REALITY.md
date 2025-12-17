# Implementierungs-Realität: Wie das System wirklich funktioniert

**Stand:** Dezember 2025  
**Status:** Funktionsfähig, aber mit bekannten Limitationen

---

## 1. Architektur-Übersicht

### 1.1 Multi-Agent-System mit LangGraph

Das System verwendet **LangGraph** zur Orchestrierung von 4 spezialisierten LLM-Agents:

```
State Check (Neo4j) 
  → Manager Agent (Storyline-Planung)
  → Intel Agent (MITRE TTP-Auswahl)
  → Action Selection (Heuristik)
  → Generator Agent (Inject-Erstellung)
  → Critic Agent (Validierung)
  → [Refine-Loop falls nötig]
  → State Update (Neo4j)
  → Loop oder End
```

**Realität:**
- LangGraph funktioniert zuverlässig für die Orchestrierung
- Die sequenzielle Abarbeitung ist deterministisch
- State wird zwischen Nodes über `WorkflowState` TypedDict übergeben
- Neo4j dient als persistenter State-Store (nicht als Knowledge Graph im klassischen Sinne)

### 1.2 Knowledge Graph (Neo4j)

**Was es ist:**
- Neo4j speichert Assets (SRV-001, APP-001, etc.) als Nodes
- Assets haben Properties: `status`, `entity_type`, `name`, `criticality`
- Injects werden als Nodes gespeichert mit Relationships zu Assets
- Szenarien werden als Container-Nodes gespeichert

**Was es NICHT ist:**
- Kein klassischer Knowledge Graph mit semantischen Beziehungen
- Keine automatische Inferenz oder Reasoning
- Keine komplexen Graph-Queries für Validierung
- Im Wesentlichen ein strukturierter Key-Value-Store mit Relationships

**Realität:**
- Neo4j wird hauptsächlich für State-Persistenz verwendet
- Assets werden als Dictionary-ähnliche Strukturen gespeichert
- Die Graph-Struktur wird kaum für Validierung genutzt
- Hauptzweck: State zwischen Workflow-Runs persistieren

---

## 2. Agent-Implementierungen

### 2.1 Manager Agent

**Aufgabe:** Erstellt grobe Storyline-Pläne für das Szenario.

**Wie es wirklich funktioniert:**
- Einfacher LLM-Call mit Prompt: "Erstelle Storyline-Plan für Phase X"
- Output: JSON mit `next_phase`, `narrative`, `key_events`, `affected_assets`
- **Temperature: 0.7** (relativ kreativ)

**Limitationen:**
- Der Plan wird generiert, aber nicht strikt befolgt
- Generator Agent ignoriert manchmal Teile des Plans
- Plan dient eher als "Inspiration" als als strikte Vorgabe
- Keine Validierung ob Plan eingehalten wird

**Realität:**
- Manager Agent ist eher dekorativ
- Die eigentliche Logik kommt vom Intel Agent (TTP-Auswahl) und Generator
- Plan wird im Prompt an Generator übergeben, aber nicht erzwungen

### 2.2 Intel Agent

**Aufgabe:** Wählt relevante MITRE ATT&CK TTPs basierend auf Phase und Kontext.

**Wie es wirklich funktioniert:**
- Query zu Neo4j: Holt TTPs die mit aktueller Phase kompatibel sind
- Filtert nach `scenario_type` (z.B. RANSOMWARE_DOUBLE_EXTORTION)
- Gibt Liste von 5-10 TTPs zurück
- **Kein LLM-Call** - reine Datenbank-Abfrage

**Realität:**
- Funktioniert zuverlässig
- TTPs werden korrekt gefiltert
- Problem: Manchmal werden TTPs ausgewählt, die nicht zur Phase passen (z.B. T1480 in CONTAINMENT)
- Keine Validierung ob TTP zur Phase passt

### 2.3 Action Selection

**Aufgabe:** Wählt eine konkrete TTP aus der Liste aus.

**Wie es wirklich funktioniert:**
- **Heuristik-basiert** (kein LLM)
- Wählt TTP basierend auf:
  - Aktuelle Phase
  - Bereits verwendete TTPs (Vermeidung von Wiederholungen)
  - Zufällige Auswahl aus kompatiblen TTPs
- **Keine intelligente Auswahl** - einfache Heuristik

**Realität:**
- Funktioniert, aber nicht besonders intelligent
- Manchmal werden unpassende TTPs ausgewählt (z.B. T1480 für CONTAINMENT)
- Keine Berücksichtigung von kausalen Sequenzen
- Generator muss dann mit unpassender TTP arbeiten

### 2.4 Generator Agent

**Aufgabe:** Erstellt konkrete Injects (Krisenszenario-Events) basierend auf TTP und Kontext.

**Wie es wirklich funktioniert:**
- **LLM-Call** mit großem Prompt (ca. 200 Zeilen)
- Prompt enthält:
  - System State (Assets und deren Status)
  - Vorherige Injects (für Konsistenz)
  - Manager Plan (wird ignoriert)
  - Selected TTP (wird verwendet)
  - Validation Feedback (wenn Refine-Loop)
- **Temperature: 0.8** (sehr kreativ)

**Hauptprobleme:**

1. **Asset-Halluzinationen:**
   - Generator erstellt manchmal neue Assets (SRV-003, APP-XXX)
   - Verwendet Asset-Namen statt IDs (z.B. "DC-01" statt "SRV-001")
   - **Workaround:** Post-Processing `_validate_and_correct_assets()` korrigiert Assets automatisch

2. **Prompt-Ignoranz:**
   - Trotz expliziter Anweisungen verwendet Generator manchmal falsche Assets
   - "ABSOLUT VERBINDLICHE REGELN" werden ignoriert
   - **Workaround:** Post-Processing korrigiert Assets, aber Content bleibt inkonsistent

3. **Refine-Loop:**
   - Generator erhält Feedback vom Critic
   - Manchmal ignoriert Generator Feedback komplett
   - Max. 2 Refine-Versuche, dann wird Inject trotzdem akzeptiert

**Realität:**
- Generator ist der "kreative" Teil, aber auch der unzuverlässigste
- Post-Processing ist notwendig, um grundlegende Fehler zu korrigieren
- Content-Qualität variiert stark
- Manchmal werden Injects akzeptiert, die eigentlich fehlerhaft sind

### 2.5 Critic Agent

**Aufgabe:** Validiert Injects auf Logik, Konsistenz und technische Plausibilität.

**Wie es wirklich funktioniert:**

#### Phase 1: Symbolische Validierung (ohne LLM)
- **Pydantic-Validierung:** Automatisch (Schema-Check)
- **FSM-Validierung:** Prüft ob Phasen-Übergang erlaubt ist
- **State-Consistency:** Prüft ob Assets im System-State existieren
- **Temporale Konsistenz:** Prüft ob Zeitstempel chronologisch sind

**Realität:**
- Diese Checks funktionieren zuverlässig
- Blockieren echte Fehler früh (spart API-Costs)
- FSM-Validierung verhindert unmögliche Phasen-Übergänge

#### Phase 2: LLM-basierte Validierung
- **LLM-Call** mit Validierungs-Prompt
- Prüft:
  - Logische Konsistenz (Widerspruchsfreiheit)
  - Causal Validity (MITRE-Technik zur Phase)
  - Regulatory Compliance (optional, nicht blockierend)

**Hauptprobleme:**

1. **LLM-Halluzinationen:**
   - Critic meldet manchmal falsche "Asset-Name-Inkonsistenzen"
   - Beispiel: "APP-001 wird als Payment Processing System bezeichnet, sollte aber Payment Processing System (APP-001, Application) sein"
   - **Workaround:** Post-Processing filtert diese Fehler automatisch heraus

2. **Zu strenge Validierung:**
   - Critic erwartet explizite Erwähung von kausalen Vorgängern
   - Ignoriert dass Phasen-Übergänge bereits Logik zeigen
   - **Workaround:** Prompt wurde angepasst, aber LLM ignoriert es manchmal

3. **Inkonsistente Entscheidungen:**
   - Gleicher Inject kann unterschiedlich validiert werden
   - LLM-Temperature: 0.3 (niedrig), aber trotzdem Variationen

**Post-Processing (neu implementiert):**
```python
# Konvertiert falsche "Asset-Name-Inkonsistenz" Fehler zu Warnungen
# Filtert echte Fehler (falsche Asset-ID, offline Asset) heraus
```

**Realität:**
- Critic ist der "Qualitätsgarant", aber auch fehleranfällig
- Post-Processing ist notwendig, um LLM-Halluzinationen zu filtern
- Symbolische Checks sind zuverlässig, LLM-Checks nicht immer

---

## 3. Refine-Loop

**Wie es funktioniert:**
1. Generator erstellt Inject
2. Critic validiert Inject
3. Wenn nicht valide:
   - Feedback wird an Generator gesendet
   - Generator erstellt neuen Inject (max. 2 Versuche)
   - Wenn nach 2 Versuchen immer noch nicht valide → Inject wird trotzdem akzeptiert

**Realität:**
- Refine-Loop funktioniert manchmal, manchmal nicht
- Generator ignoriert Feedback oft
- Nach 2 Versuchen wird Inject akzeptiert, auch wenn fehlerhaft
- **Workaround:** System akzeptiert Injects mit Warnungen

**Probleme:**
- Generator kann Feedback nicht immer umsetzen
- Critic-Feedback ist manchmal unklar oder widersprüchlich
- Keine Garantie dass Refine-Loop Verbesserung bringt

---

## 4. State Management

### 4.1 Neo4j State

**Wie es funktioniert:**
- Assets werden als Nodes gespeichert
- Status wird nach jedem Inject aktualisiert
- Injects werden als Nodes mit Relationships gespeichert

**Realität:**
- State wird korrekt aktualisiert
- Assets werden konsistent verwaltet
- Problem: Manchmal werden Assets mit falschen Namen gespeichert (z.B. "APP-SRV-01" statt "SRV-002")

### 4.2 Workflow State

**Wie es funktioniert:**
- `WorkflowState` TypedDict wird zwischen Nodes übergeben
- Enthält: `injects`, `system_state`, `manager_plan`, `selected_action`, etc.
- State wird nicht zwischen Runs persistiert (nur Neo4j)

**Realität:**
- Funktioniert zuverlässig
- State wird korrekt zwischen Nodes übergeben
- Keine bekannten Probleme

---

## 5. Bekannte Probleme und Limitationen

### 5.1 LLM-Halluzinationen

**Problem:**
- Generator erstellt manchmal neue Assets oder verwendet falsche Namen
- Critic meldet manchmal falsche "Asset-Name-Inkonsistenzen"
- LLMs ignorieren explizite Anweisungen im Prompt

**Workarounds:**
- Post-Processing korrigiert Assets automatisch
- Post-Processing filtert falsche Critic-Fehler heraus
- Explizite Prompts mit "ABSOLUT VERBINDLICHE REGELN"

**Status:**
- Teilweise gelöst durch Post-Processing
- Prompts werden weiterhin ignoriert
- Keine vollständige Lösung

### 5.2 Kausale Inkonsistenzen

**Problem:**
- Critic erwartet explizite Erwähnung von kausalen Vorgängern
- Phasen-Übergänge zeigen bereits Logik, aber Critic ignoriert das
- Generator erstellt manchmal Sequenzen ohne kausale Vorgänger

**Workarounds:**
- Prompt wurde angepasst: "Phasen-Übergänge zeigen bereits Logik"
- Causal Validity ist nicht mehr blockierend (nur Warnung)
- Post-Processing könnte helfen, aber noch nicht implementiert

**Status:**
- Teilweise gelöst durch Prompt-Anpassungen
- LLM ignoriert Anweisungen manchmal
- Keine vollständige Lösung

### 5.3 MITRE-Technik zur Phase

**Problem:**
- Action Selection wählt manchmal unpassende TTPs (z.B. T1480 für CONTAINMENT)
- Generator muss dann mit unpassender TTP arbeiten
- Critic meldet dies als Fehler, aber Inject wird trotzdem akzeptiert

**Workarounds:**
- Causal Validity ist nicht mehr blockierend (nur Warnung)
- Generator kann TTP ändern wenn Feedback gegeben wird
- Keine Validierung in Action Selection

**Status:**
- Nicht gelöst
- System akzeptiert unpassende TTPs mit Warnungen

### 5.4 Asset-Name-Inkonsistenzen

**Problem:**
- Generator verwendet sowohl Asset-IDs (SRV-001) als auch Namen (DC-01)
- Critic meldet dies als Fehler, obwohl es erlaubt sein sollte
- Content wird inkonsistent (manchmal ID, manchmal Name)

**Workarounds:**
- Prompt wurde angepasst: "Beide Namen sind erlaubt"
- Post-Processing filtert falsche Fehler heraus
- Generator-Prompt wurde verstärkt

**Status:**
- Teilweise gelöst durch Post-Processing
- Prompts werden weiterhin ignoriert
- Keine vollständige Lösung

---

## 6. Was funktioniert zuverlässig

### 6.1 Symbolische Validierung
- ✅ Pydantic-Validierung (Schema-Check)
- ✅ FSM-Validierung (Phasen-Übergänge)
- ✅ State-Consistency (Asset-Existenz)
- ✅ Temporale Konsistenz (Zeitstempel)

### 6.2 Workflow-Orchestrierung
- ✅ LangGraph orchestriert Agents zuverlässig
- ✅ State wird korrekt zwischen Nodes übergeben
- ✅ Refine-Loop funktioniert technisch

### 6.3 Neo4j State Management
- ✅ Assets werden korrekt gespeichert und aktualisiert
- ✅ State wird zwischen Runs persistiert
- ✅ Injects werden korrekt gespeichert

### 6.4 Post-Processing
- ✅ Asset-Korrektur funktioniert zuverlässig
- ✅ Falsche Critic-Fehler werden herausgefiltert
- ✅ System ist robuster durch Post-Processing

---

## 7. Was NICHT zuverlässig funktioniert

### 7.1 LLM-Prompt-Compliance
- ❌ Generator ignoriert explizite Anweisungen
- ❌ Critic meldet falsche Fehler trotz klarer Anweisungen
- ❌ Prompts werden nicht konsistent befolgt

### 7.2 Refine-Loop-Effektivität
- ❌ Generator kann Feedback nicht immer umsetzen
- ❌ Refine-Loop bringt nicht immer Verbesserung
- ❌ Nach 2 Versuchen wird Inject trotzdem akzeptiert

### 7.3 Kausale Logik
- ❌ Critic erwartet explizite Erwähnung von Vorgängern
- ❌ Phasen-Übergänge werden nicht immer als kausale Logik erkannt
- ❌ Generator erstellt manchmal unmögliche Sequenzen

### 7.4 MITRE-Technik-Auswahl
- ❌ Action Selection wählt manchmal unpassende TTPs
- ❌ Keine Validierung ob TTP zur Phase passt
- ❌ System akzeptiert unpassende TTPs mit Warnungen
- ❌ Generator kann TTP ändern wenn Feedback gegeben wird (z.B. T1480 → T1562)

### 7.5 Neo4j-Speicherung
- ⚠️ Pydantic-Validierungsfehler beim Speichern (Inject-Objekte müssen zu Dict konvertiert werden)
- ⚠️ Injects werden manchmal nicht korrekt gespeichert
- ⚠️ Fehler wird ignoriert, Szenario wird trotzdem als "erfolgreich" markiert

---

## 8. Aktuelle Workarounds

### 8.1 Post-Processing für Assets
```python
# In generator_agent.py
def _validate_and_correct_assets(...):
    # Korrigiert Assets automatisch wenn falsch
    # Ersetzt nicht-existierende Assets durch verfügbare
```

### 8.2 Post-Processing für Critic-Fehler
```python
# In critic_agent.py
# Konvertiert falsche "Asset-Name-Inkonsistenz" Fehler zu Warnungen
# Filtert echte Fehler (falsche Asset-ID, offline Asset) heraus
```

### 8.3 Explizite Prompts
- "ABSOLUT VERBINDLICHE REGELN" im Generator-Prompt
- "❌❌❌ ABSOLUT VERBOTEN" im Critic-Prompt
- Mehrfache Warnungen und Beispiele

**Realität:**
- Workarounds helfen, lösen aber nicht das Grundproblem
- LLMs ignorieren Prompts weiterhin
- Post-Processing ist notwendig, aber nicht ideal

---

## 9. Deep Truth Logging

**Implementierung:**
- `CRITIC_AUDIT_LOG.md` wird nach jeder Validierung aktualisiert
- Enthält:
  - Ground Truth (System State, Assets, Rules)
  - Generator's Draft (vollständiger Inject JSON)
  - Critic's Reasoning (Raw LLM Output)
  - Verdict (Entscheidung, Fehler, Warnungen)

**Zweck:**
- Debugging von LLM-Halluzinationen
- Verstehen warum Critic bestimmte Entscheidungen trifft
- Identifizieren ob Problem im Code oder im LLM liegt

**Realität:**
- Funktioniert zuverlässig
- Sehr hilfreich für Debugging
- Zeigt klar: LLM ignoriert Prompts manchmal komplett

---

## 10. Performance und Kosten

### 10.1 API-Calls
- **Manager Agent:** 1 Call pro Iteration
- **Intel Agent:** 0 Calls (Datenbank-Abfrage)
- **Generator Agent:** 1-3 Calls pro Inject (abhängig von Refine-Loops)
- **Critic Agent:** 1 Call pro Validierung (nur wenn symbolische Checks OK)

**Realität:**
- Durchschnittlich: 3-5 LLM-Calls pro Inject
- Bei Refine-Loops: bis zu 7 Calls pro Inject
- Kosten: ~$0.01-0.05 pro Inject (abhängig von Modell)

### 10.2 Latenz
- **Symbolische Validierung:** < 10ms
- **LLM-Call:** 1-5 Sekunden (abhängig von Modell)
- **Neo4j-Query:** < 100ms
- **Gesamt pro Inject:** 5-15 Sekunden

**Realität:**
- System ist nicht besonders schnell
- Hauptbottleneck: LLM-Calls
- Parallelisierung nicht möglich (sequenzielle Abhängigkeiten)

---

## 11. Fazit

### Was das System IST:
- Ein funktionsfähiges Multi-Agent-System für Krisenszenario-Generierung
- Verwendet LLMs für kreative Aufgaben (Generator) und Validierung (Critic)
- Verwendet symbolische Systeme (FSM, Pydantic, Neo4j) für strukturelle Validierung
- Hat Post-Processing-Layer um LLM-Fehler zu korrigieren

### Was das System NICHT IST:
- Kein perfektes System ohne Fehler
- Kein System das Prompts zuverlässig befolgt
- Kein System das immer konsistente Ergebnisse liefert
- Kein System das ohne Workarounds funktioniert

### Aktuelle Prioritäten:
1. ✅ Post-Processing funktioniert (Assets, Critic-Fehler)
2. ✅ Symbolische Validierung funktioniert zuverlässig
3. ⚠️ LLM-Prompt-Compliance ist problematisch
4. ⚠️ Refine-Loop-Effektivität ist begrenzt
5. ❌ MITRE-Technik-Auswahl ist nicht intelligent

### Empfehlungen:
- Post-Processing weiter ausbauen
- Mehr symbolische Validierung, weniger LLM-Validierung
- Prompts vereinfachen (weniger ist mehr)
- Action Selection intelligenter machen (LLM-basiert?)
- Refine-Loop verbessern (besseres Feedback-Format?)

---

---

## 12. Aktuelle Fehler aus Logs

### 12.1 Neo4j-Speicherung
```
⚠️ Fehler beim Speichern in Neo4j: 3 validation errors for ScenarioState
injects.0: Input should be a valid dictionary or instance of Inject
```

**Problem:**
- Injects werden als Pydantic-Objekte gespeichert, aber Neo4j erwartet Dicts
- Fehler wird ignoriert, Szenario wird trotzdem als "erfolgreich" markiert

**Status:** Nicht behoben

### 12.2 Asset-Name-Inkonsistenzen (trotz Post-Processing)
```
Asset-Name-Inkonsistenz: APP-001 wird als Payment Processing System bezeichnet, 
sollte aber Payment Processing System (APP-001, Application) sein.
```

**Problem:**
- Critic LLM meldet absurde Fehler (sagt genau das Gegenteil von dem was gewollt ist)
- Post-Processing filtert diese heraus, aber LLM meldet sie weiterhin

**Status:** Teilweise behoben (Post-Processing filtert), aber LLM-Verhalten nicht geändert

### 12.3 Generator ändert TTP bei Refine
```
Phase: CONTAINMENT, TTP: T1480
→ Refine-Loop
→ Generator ändert zu T1562 (ohne Anweisung)
```

**Problem:**
- Generator ändert TTP wenn Feedback gegeben wird
- Keine explizite Anweisung dazu im Prompt
- Kann zu Inkonsistenzen führen

**Status:** Nicht behoben, aber funktioniert manchmal besser

---

**Letzte Aktualisierung:** 2025-12-17  
**Autor:** System-Analyse basierend auf Code-Review, Audit-Logs und Terminal-Outputs

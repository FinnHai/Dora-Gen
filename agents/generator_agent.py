"""
Generator Agent - Erstellt konkrete Injects basierend auf der Storyline.

Verantwortlich für:
- Generierung von realistischen, detaillierten Injects
- Einhaltung des Inject-Schemas (Pydantic)
- Integration von TTPs und Systemzustand
"""

from typing import Dict, Any, Optional, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from state_models import (
    Inject,
    TechnicalMetadata,
    CrisisPhase,
    InjectModality,
    ScenarioType
)
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()


class GeneratorAgent:
    """
    Generator Agent für Inject-Erstellung.
    
    Verwendet LLM, um realistische, detaillierte Injects zu generieren,
    die dem Inject-Schema entsprechen und DORA-konform sind.
    """
    
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.8):
        """
        Initialisiert den Generator Agent.
        
        Args:
            model_name: OpenAI Modell-Name
            temperature: Temperature für LLM
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def generate_inject(
        self,
        scenario_type: ScenarioType,
        phase: CrisisPhase,
        inject_id: str,
        time_offset: str,
        manager_plan: Dict[str, Any],
        selected_ttp: Dict[str, Any],
        system_state: Dict[str, Any],
        previous_injects: list,
        validation_feedback: Optional[Dict[str, Any]] = None,
        user_feedback: Optional[str] = None
    ) -> Inject:
        """
        Generiert einen neuen Inject.
        
        Args:
            scenario_type: Typ des Szenarios
            phase: Aktuelle Phase
            inject_id: Eindeutige Inject-ID
            time_offset: Zeitversatz (z.B. "T+02:00")
            manager_plan: Storyline-Plan vom Manager Agent
            selected_ttp: Ausgewählte TTP
            system_state: Aktueller Systemzustand
            previous_injects: Liste vorheriger Injects für Konsistenz
            validation_feedback: Optional Feedback vom Critic Agent für Refine-Loops
        
        Returns:
            Inject-Objekt (Pydantic)
        """
        # Erstelle Prompt für Inject-Generierung
        is_refine = validation_feedback is not None
        
        system_prompt = """Du bist ein Experte für Cyber-Security Incident Response und Krisenmanagement.
Deine Aufgabe ist es, realistische, detaillierte Injects für Krisenszenarien zu erstellen.

### CRITICAL ASSET BINDING RULES (NON-NEGOTIABLE) ###
1. YOU MUST USE EXACT ASSET IDs from the provided "System State" (e.g., "SRV-001").
2. DO NOT invent aliases (e.g., do NOT write "DC-01" if the ID is "SRV-001").
3. DO NOT hallucinate new assets (e.g., "APP-SRV-99").
4. If you mention an asset, you MUST include its ID in parentheses, e.g., "The Domain Controller (SRV-001)..."

KRITISCHE ANFORDERUNGEN (MUSS erfüllt werden):

1. LOGISCHE KONSISTENZ (KRITISCH):
   - Injects müssen logisch konsistent mit vorherigen Injects sein
   - Asset-Namen müssen konsistent sein (verwende dieselben Namen wie in vorherigen Injects)
   - Berücksichtige den aktuellen Systemzustand (welche Assets sind bereits offline/compromised?)
   - Keine temporalen Inkonsistenzen (Zeitstempel müssen chronologisch sein)

2. CAUSAL VALIDITY (KRITISCH):
   - MITRE TTP muss zur aktuellen Phase passen
   - INITIAL_INCIDENT erfordert Initial Access/Execution, NICHT Persistence oder Exfiltration
   - Keine unmöglichen Sequenzen (z.B. Exfiltration vor Initial Access)

3. STATE-CONSISTENCY (KRITISCH - ABSOLUT VERBINDLICH):
   - Verwende NUR Assets, die in der Liste "VERFÜGBARE ASSET-IDs" stehen
   - Erstelle KEINE neuen Assets (keine SRV-003, APP-XXX, etc. wenn nicht in Liste)
   - Wenn keine Assets verfügbar sind, verwende Standard-Assets: SRV-001, SRV-002
   - Berücksichtige Asset-Status (offline Assets können nicht angegriffen werden)
   - Keine Asset-Name-Inkonsistenzen
   - Asset-IDs müssen EXAKT übereinstimmen (Groß-/Kleinschreibung beachten)

4. REGULATORISCHE ASPEKTE (optional, nicht blockierend):
   - INCIDENT RESPONSE: In INITIAL_INCIDENT/SUSPICIOUS_ACTIVITY → SOC-Aktivitäten erwähnen
   - BUSINESS CONTINUITY: In ESCALATION_CRISIS/CONTAINMENT → Backup-Systeme erwähnen
   - RECOVERY PLAN: In RECOVERY → Recovery-Maßnahmen erwähnen
   - CRITICAL FUNCTIONS: Erwähne kritische Funktionen (generisch, keine spezifische Branche)

5. REALISTIC SCENARIO:
   - Verwende realistische technische Details (IPs, Hashes, Domains)
   - Mindestens 50 Zeichen detaillierter Beschreibung
   - Realistische Modalitäten (SIEM Alert, Email, etc.)

FEHLER VERMEIDEN (KRITISCH - DIESE FEHLER FÜHREN ZURÜCKWEISUNG):
- ❌ Asset existiert nicht im Systemzustand → IMMER zurückgewiesen!
- ❌ Neue Assets erstellt (SRV-003, APP-XXX, etc.) → IMMER zurückgewiesen!
- ❌ Asset-ID stimmt nicht exakt überein → IMMER zurückgewiesen!
- ❌ Asset ist offline, wird aber als aktiv behandelt
- ❌ MITRE-Technik passt nicht zur Phase
- ❌ Temporale Inkonsistenz (Zeitstempel geht zurück)
- ❌ Asset-Name-Inkonsistenz (verschiedene Namen für dasselbe Asset)
- ❌ Kausale Inkonsistenz (Event ohne Vorgänger)

ASSET-VALIDIERUNG (MUSS BEACHTET WERDEN):
1. Prüfe die Liste "VERFÜGBARE ASSET-IDs" im Systemzustand
2. Verwende NUR Asset-IDs aus dieser Liste
3. Wenn Liste leer oder nur INJ-/SCEN-IDs: Verwende SRV-001, SRV-002
4. Kopiere Asset-IDs EXAKT (keine Variationen!)

### DYNAMIC TIME MANAGEMENT RULES ###
You MUST calculate the `time_offset` based on the NARRATIVE CONTEXT, not just add 30 minutes.

**CRITICAL:** The time_offset must reflect the REALISTIC PACE of events:
- **High Intensity Events (Ransomware Encryption, Active Exploits, Lateral Movement):** Short jumps (e.g., +5m, +15m, +30m).
- **Investigation Phases (SOC Analysis, Forensics, Log Review):** Medium jumps (e.g., +2h, +4h, +6h).
- **Stealth/APT Phases (Dormant Persistence, Data Exfiltration):** Long jumps (e.g., +12h, +1d, +3d).
- **Shift Changes/Weekends:** You can jump multiple days if realistic (e.g., +2d, +5d).

**Format:** Always use `T+DD:HH:MM` format:
- Minutes: `T+00:00:15` (15 minutes)
- Hours: `T+00:02:00` (2 hours)
- Days: `T+01:00:00` (1 day)
- Mixed: `T+00:04:30` (4 hours 30 minutes)

**Examples:**
- Active ransomware encryption → `T+00:00:05` (5 minutes later)
- SOC investigation → `T+00:03:00` (3 hours later)
- Stealth data exfiltration → `T+01:00:00` (1 day later)
- Weekend gap → `T+02:00:00` (2 days later)

**IMPORTANT:** The time_offset MUST be chronologically AFTER the last inject's time_offset. Check previous_injects to ensure consistency."""
        
        if is_refine:
            system_prompt += """

⚠️ REFINE-MODUS: Der vorherige Inject wurde zurückgewiesen.
Korrigiere die folgenden Fehler:
{validation_errors}

WICHTIG: Behebe ALLE genannten Fehler. Verwende dieselbe Inject-ID und denselben Zeitstempel.

🚫 TTP FREEZE (FORBIDDEN): Your task is to FIX the logical errors reported by the Critic. You are FORBIDDEN from changing the selected MITRE TTP or the affected assets unless the Critic explicitly tells you they are wrong. Keep the core scenario stable."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            
            ("human", """Erstelle einen Inject für ein {scenario_type} Szenario.

Kontext:
- Inject ID: {inject_id}
- Vorgeschlagener Zeitversatz (NUR VORSCHLAG - berechne neu basierend auf Kontext!): {time_offset}
- Phase: {phase}
- TTP: {ttp_name} ({ttp_id})
{temporal_context}
{normal_operation_rule}

Storyline-Plan:
{manager_plan}

⚠️ KRITISCH - SYSTEMZUSTAND (VERFÜGBARE ASSETS):
{system_state}

⚠️ KRITISCH - VORHERIGE INJECTS (für Konsistenz - verwende dieselben Asset-Namen!):
{previous_injects}

{user_feedback_section}

{validation_feedback_section}

⚠️ ABSOLUT VERBINDLICHE REGELN:
1. Verwende NUR Asset-IDs aus der Liste "VERFÜGBARE ASSET-IDs" oben
2. Erstelle KEINE neuen Assets (keine SRV-003, APP-XXX, DC-01, APP-SRV-01, DB-SRV-03, etc.)
3. Wenn keine Assets verfügbar sind, verwende: SRV-001, SRV-002
4. Asset-IDs müssen EXAKT übereinstimmen (Groß-/Kleinschreibung beachten)
5. Kopiere Asset-IDs EXAKT aus der Liste - keine Variationen!
6. WICHTIG: Verwende im Content-Feld NUR die Asset-IDs aus der Liste (z.B. "SRV-002", nicht "APP-SRV-01" oder "SRV-002 (APP-SRV-01)")
7. Wenn ein Asset einen Namen hat (z.B. "SRV-002" = "Domain Controller"), verwende IMMER die Asset-ID "SRV-002" im Content, nicht den Namen!

Erstelle einen realistischen Inject im folgenden JSON-Format:
{{
    "time_offset": "<Berechne basierend auf narrativem Kontext! Siehe Dynamic Time Management Rules oben. Format: T+DD:HH:MM>",
    "source": "<Quelle, z.B. 'Red Team / Attacker' oder 'Blue Team / SOC'>",
    "target": "<Empfänger, z.B. 'Blue Team / SOC' oder 'Management'>",
    "modality": "<SIEM Alert|Email|Phone Call|Physical Event|News Report|Internal Report>",
    "content": "<Detaillierter Inhalt des Injects, mindestens 50 Zeichen>",
    "technical_metadata": {{
        "mitre_id": "{ttp_id}",
        "affected_assets": ["<Asset 1>", "<Asset 2>"],
        "ioc_hash": "<SHA256 Hash>",
        "ioc_ip": "<IP-Adresse>",
        "ioc_domain": "<Domain>",
        "severity": "<Low|Medium|High|Critical>"
    }},
    "business_impact": "<Beschreibung der geschäftlichen Auswirkung, optional>"
}}

⚠️ WICHTIG - TIME_OFFSET BERECHNUNG:
- Der bereitgestellte Zeitversatz "{time_offset}" ist nur ein VORSCHLAG.
- Du MUSST den time_offset basierend auf dem narrativen Kontext neu berechnen!
- Prüfe die vorherigen Injects: Was ist der letzte time_offset?
- Berechne einen REALISTISCHEN Sprung basierend auf:
  * Art des Events (High Intensity → kurz, Investigation → mittel, Stealth → lang)
  * Phase des Szenarios (frühe Phasen → kürzer, späte Phasen → länger)
  * User Feedback (wenn vorhanden: Wie lange dauert die Response Action?)
- Stelle sicher, dass der neue time_offset CHRONOLOGISCH NACH dem letzten liegt!

REGULATORISCHE ASPEKTE für Phase {phase} (optional, nicht blockierend):
- Wenn Phase INITIAL_INCIDENT oder SUSPICIOUS_ACTIVITY: Content KÖNNTE SOC-Aktivitäten, Incident Response oder Security Operations erwähnen
- Wenn Phase ESCALATION_CRISIS oder CONTAINMENT: Content KÖNNTE Business Continuity, Backup-Systeme oder Service-Wiederherstellung erwähnen
- Wenn Phase RECOVERY: Content KÖNNTE Recovery-Maßnahmen, Backup-Wiederherstellung oder System-Recovery erwähnen
- Diese Aspekte sind optional und blockieren nicht die Validierung

Weitere Anforderungen:
- Der Content muss realistisch und detailliert sein (mindestens 50 Zeichen)
- Verwende echte technische Details (aber keine echten IOCs)
- Stelle sicher, dass der Inject zur Phase und zum TTP passt (TTP {ttp_id} sollte zur Phase {phase} passen)
- Berücksichtige den Systemzustand (welche Assets sind betroffen?)
- Business Impact sollte kritische Geschäftsfunktionen erwähnen""")
        ])
        
        # Formatierung
        ttp_name = selected_ttp.get("name", "Unknown TTP")
        ttp_id = selected_ttp.get("mitre_id", selected_ttp.get("technique_id", "T0000"))
        system_state_str = self._format_system_state(system_state)
        previous_injects_str = self._format_previous_injects(previous_injects)
        manager_plan_str = self._format_manager_plan(manager_plan)
        
        # Temporale Konsistenz: Hole letzten Zeitstempel
        last_timestamp = None
        last_inject_id = None
        if previous_injects:
            last_inject = previous_injects[-1]
            last_timestamp = last_inject.time_offset
            last_inject_id = last_inject.inject_id
        
        # Normal Operation Regel
        normal_operation_rule = ""
        if phase == CrisisPhase.NORMAL_OPERATION:
            normal_operation_rule = """
⚠️ PHASE: NORMAL_OPERATION - SPEZIELLE REGELN:
- Generiere KEINE offensichtlichen Angriffe (wie Ransomware, C2 Traffic, aktive Exploits).
- ERLAUBT sind:
  * False Positives (fehlerhafte SIEM-Alerts, verdächtige aber harmlose Aktivitäten)
  * Wartungsfehler (falsche Konfigurationen, unbeabsichtigte Änderungen)
  * Fehlgeschlagene Logins (Brute-Force-Versuche die fehlschlagen)
  * Subtile Reconnaissance (Port-Scanning, OSINT-Sammlung, passive Scanning)
- Falls du einen Angriff startest, MUSS der Inject eine Transition zu 'SUSPICIOUS_ACTIVITY' vorschlagen.
- Der Content sollte eher "verdächtig" als "bedrohlich" klingen."""
        
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
        else:
            user_feedback_section = ""
        
        # Validation Feedback Formatierung
        validation_feedback_section = ""
        if validation_feedback:
            errors = validation_feedback.get("errors", [])
            warnings = validation_feedback.get("warnings", [])
            if errors or warnings:
                validation_feedback_section = "\n" + "="*60 + "\n"
                validation_feedback_section += "⚠️ VALIDIERUNGSFEEDBACK - VORHERIGER VERSUCH ZURÜCKGEWIESEN\n"
                validation_feedback_section += "="*60 + "\n"
                if errors:
                    validation_feedback_section += "\n❌ KRITISCHE FEHLER (MUSS behoben werden):\n"
                    for i, error in enumerate(errors, 1):
                        validation_feedback_section += f"  {i}. {error}\n"
                
                # Extrahiere verfügbare Assets aus Fehlermeldungen falls vorhanden
                available_assets_from_error = []
                for error in errors:
                    if "Verfügbare Assets:" in error:
                        # Verwende das global importierte re-Modul
                        match = re.search(r"Verfügbare Assets: \[(.*?)\]", error)
                        if match:
                            assets_str = match.group(1)
                            available_assets_from_error = [a.strip().strip("'\"") for a in assets_str.split(",")]
                            # Filtere echte Assets (keine INJ-*, SCEN-* IDs)
                            available_assets_from_error = [a for a in available_assets_from_error 
                                                          if not a.startswith(("INJ-", "SCEN-"))]
                
                if available_assets_from_error:
                    validation_feedback_section += f"\n✅ VERFÜGBARE ASSET-IDs (NUR DIESE VERWENDEN!): {', '.join(available_assets_from_error)}\n"
                
                if warnings:
                    validation_feedback_section += "\n⚠️ WARNUNGEN (sollten beachtet werden):\n"
                    for i, warning in enumerate(warnings, 1):
                        validation_feedback_section += f"  {i}. {warning}\n"
                
                validation_feedback_section += "\n" + "="*60 + "\n"
                validation_feedback_section += "ANWEISUNG: Korrigiere ALLE genannten Fehler.\n"
                validation_feedback_section += "WICHTIG: Verwende NUR Asset-IDs aus der Liste oben!\n"
                validation_feedback_section += "="*60 + "\n"
        
        # ================== TEMPORAL CONTEXT DEFINITION (FIX) ==================
        # 1. Letzten Inject und Zeitstempel holen
        if previous_injects:
            last_inject = previous_injects[-1]
            last_time_str = last_inject.time_offset
        else:
            last_time_str = "T+00:00:00"
        
        # 2. Variable 'temporal_context' DEFINIEREN (das fehlte!)
        temporal_context = (
            f"Der letzte validierte Inject fand um {last_time_str} statt. "
            f"Dein neuer Inject MUSS zwingend zeitlich danach liegen (z.B. +15 bis +60 Minuten). "
            f"Berechne den neuen Offset basierend auf {last_time_str}."
        )
        # ================== ENDE TEMPORAL CONTEXT DEFINITION ==================
        
        chain = prompt | self.llm
        
        # Retry-Logik für LLM-Call
        from utils.retry_handler import safe_llm_call
        
        print(f"🔧 [Generator] Starte LLM-Call für Inject {inject_id}")
        print(f"   Phase: {phase.value}, TTP: {ttp_id}")
        print(f"   System State Keys: {list(system_state.keys())[:5] if system_state else 'Keine'}")
        print(f"   Validation Feedback: {'Ja' if validation_feedback else 'Nein'}")
        
        try:
            def _invoke_chain():
                return chain.invoke({
                    "scenario_type": scenario_type.value,
                    "inject_id": inject_id,
                    "time_offset": time_offset,
                    "phase": phase.value,
                    "ttp_name": ttp_name,
                    "ttp_id": ttp_id,
                    "temporal_context": temporal_context,
                    "normal_operation_rule": normal_operation_rule,
                    "manager_plan": manager_plan_str,
                    "system_state": system_state_str,
                    "previous_injects": previous_injects_str,
                    "user_feedback_section": user_feedback_section,
                    "validation_feedback_section": validation_feedback_section,
                    "validation_errors": "\n".join(validation_feedback.get("errors", [])) if validation_feedback else ""
                })
            
            response = safe_llm_call(
                _invoke_chain,
                max_attempts=3,
                default_return=None
            )
            
            if response is None:
                print(f"❌ [Generator] LLM-Call fehlgeschlagen für {inject_id}")
                raise Exception("LLM-Call fehlgeschlagen nach mehreren Versuchen")
            
            print(f"✅ [Generator] LLM-Call erfolgreich für {inject_id}")
            
            # Parse JSON aus Response
            content = response.content
            print(f"🔧 [Generator] Parse JSON aus Response (Länge: {len(content)} Zeichen)")
            
            # Verwende das global importierte re-Modul
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            print(f"🔧 [Generator] JSON Match gefunden: {json_match is not None}")
            
            if json_match:
                print(f"🔧 [Generator] Parse JSON-Daten...")
                inject_data = json.loads(json_match.group())
                
                # POST-PROCESSING: Validiere und korrigiere Assets
                requested_assets = inject_data.get("technical_metadata", {}).get("affected_assets", [])
                print(f"🔧 [Generator] Angeforderte Assets vom LLM: {requested_assets}")
                
                valid_assets = self._validate_and_correct_assets(requested_assets, system_state)
                print(f"✅ [Generator] Korrigierte Assets: {valid_assets}")
                
                # Erstelle TechnicalMetadata mit korrigierten Assets
                tech_meta = TechnicalMetadata(
                    mitre_id=inject_data.get("technical_metadata", {}).get("mitre_id", ttp_id),
                    affected_assets=valid_assets,  # Verwende korrigierte Assets
                    ioc_hash=inject_data.get("technical_metadata", {}).get("ioc_hash"),
                    ioc_ip=inject_data.get("technical_metadata", {}).get("ioc_ip"),
                    ioc_domain=inject_data.get("technical_metadata", {}).get("ioc_domain"),
                    severity=inject_data.get("technical_metadata", {}).get("severity", "Medium")
                )
                
                # Verwende Generator-generierten time_offset falls vorhanden, sonst Fallback
                generated_time_offset = inject_data.get("time_offset")
                if generated_time_offset and generated_time_offset.strip():
                    # Validiere Format (akzeptiert sowohl T+DD:HH:MM als auch T+DD:HH)
                    if re.match(r'^T\+\d{2}:\d{2}(?::\d{2})?$', generated_time_offset):
                        final_time_offset = generated_time_offset
                        print(f"✅ [Generator] Verwende Generator-generierten time_offset: {final_time_offset}")
                    else:
                        print(f"⚠️  [Generator] Ungültiges time_offset Format '{generated_time_offset}', verwende Fallback")
                        final_time_offset = time_offset
                else:
                    # Fallback auf übergebenen time_offset
                    final_time_offset = time_offset
                    print(f"ℹ️  [Generator] Kein Generator-generierter time_offset, verwende Fallback: {final_time_offset}")
                
                # Erstelle Inject
                inject = Inject(
                    inject_id=inject_id,
                    time_offset=final_time_offset,
                    phase=phase,
                    source=inject_data.get("source", "Red Team / Attacker"),
                    target=inject_data.get("target", "Blue Team / SOC"),
                    modality=InjectModality(inject_data.get("modality", "SIEM Alert")),
                    content=inject_data.get("content", "Generic security event detected."),
                    technical_metadata=tech_meta,
                    dora_compliance_tag=None,  # Nicht mehr verwendet, für Rückwärtskompatibilität None
                    business_impact=inject_data.get("business_impact")
                )
                
                print(f"✅ [Generator] Inject {inject_id} erfolgreich erstellt")
                print(f"   Assets: {valid_assets}")
                print(f"   Content Preview: {inject.content[:80]}...")
                
                return inject
            else:
                print(f"⚠️  [Generator] Kein JSON-Match gefunden in Response")
                print(f"   Response Preview: {content[:200]}...")
                # Fallback: Erstelle minimalen Inject
                return self._create_fallback_inject(
                    inject_id, time_offset, phase, ttp_id, selected_ttp
                )
                
        except Exception as e:
            import traceback
            print(f"❌ [Generator] Fehler bei Inject-Generierung für {inject_id}: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            return self._create_fallback_inject(
                inject_id, time_offset, phase, ttp_id, selected_ttp
            )
    
    def _create_fallback_inject(
        self,
        inject_id: str,
        time_offset: str,
        phase: CrisisPhase,
        ttp_id: str,
        ttp: Dict[str, Any]
    ) -> Inject:
        """Erstellt einen Fallback-Inject bei Fehlern."""
        tech_meta = TechnicalMetadata(
            mitre_id=ttp_id,
            affected_assets=["SRV-001"],
            severity="Medium"
        )
        
        return Inject(
            inject_id=inject_id,
            time_offset=time_offset,
            phase=phase,
            source="Red Team / Attacker",
            target="Blue Team / SOC",
            modality=InjectModality.SIEM_ALERT,
            content=f"Security event detected related to {ttp.get('name', 'unknown technique')} (MITRE {ttp_id}).",
            technical_metadata=tech_meta,
            dora_compliance_tag=None  # Nicht mehr verwendet
        )
    
    def _format_system_state(self, system_state: Dict[str, Any]) -> str:
        """
        Formatiert den Systemzustand mit Fokus auf verfügbare Assets.
        
        Filtert nur echte Assets (Server, Applications) heraus, keine Inject-IDs oder Szenario-IDs.
        """
        if not system_state or not isinstance(system_state, dict):
            return "Keine Systemzustand-Informationen verfügbar"
        
        # Filtere echte Assets heraus (keine INJ-*, SCEN-* IDs)
        valid_assets = {}
        for entity_id, entity_data in system_state.items():
            # Überspringe Inject-IDs und Szenario-IDs
            if entity_id.startswith("INJ-") or entity_id.startswith("SCEN-"):
                continue
            
            # Nur echte Assets (Server, Applications, etc.)
            if isinstance(entity_data, dict):
                entity_type = entity_data.get("entity_type", "").lower()
                if entity_type in ["server", "application", "database", "service", "asset"] or \
                   entity_id.startswith(("SRV-", "APP-", "DB-", "SVC-")):
                    valid_assets[entity_id] = entity_data
        
        if not valid_assets:
            return "Keine Assets im Systemzustand verfügbar. Verwende Standard-Assets: SRV-001, SRV-002"
        
        lines = []
        asset_list = []
        for entity_id, entity_data in valid_assets.items():
            status = entity_data.get("status", "unknown")
            name = entity_data.get("name", entity_id)
            entity_type = entity_data.get("entity_type", "Asset")
            lines.append(f"- {name} ({entity_id}, {entity_type}): {status}")
            asset_list.append(entity_id)
        
        # WICHTIG: Liste der verfügbaren Asset-IDs explizit angeben
        result = "\n".join(lines) if lines else "Alle Systeme im Normalbetrieb"
        result += f"\n\n⚠️ KRITISCH - VERFÜGBARE ASSET-IDs (NUR DIESE VERWENDEN!): {', '.join(asset_list)}"
        result += f"\n❌ VERBOTEN: Erstelle KEINE neuen Assets! Verwende NUR die oben genannten Asset-IDs!"
        
        return result
    
    def _format_previous_injects(self, previous_injects: list) -> str:
        """Formatiert vorherige Injects für Konsistenz (inklusive time_offsets für chronologische Berechnung)."""
        if not previous_injects:
            return "Keine vorherigen Injects - Starte bei T+00:00:00"
        
        lines = []
        lines.append("⚠️ WICHTIG - CHRONOLOGISCHE REIHENFOLGE:")
        for inj in previous_injects[-5:]:  # Letzte 5 für besseren Kontext
            if isinstance(inj, Inject):
                lines.append(f"- {inj.inject_id} | Time: {inj.time_offset} | Phase: {inj.phase.value} | Content: {inj.content[:60]}...")
            elif isinstance(inj, dict):
                inj_time = inj.get('time_offset', 'Unknown')
                inj_phase = inj.get('phase', 'Unknown')
                inj_content = inj.get('content', '')[:60] if isinstance(inj.get('content'), str) else str(inj.get('content', ''))[:60]
                lines.append(f"- {inj.get('inject_id', 'Unknown')} | Time: {inj_time} | Phase: {inj_phase} | Content: {inj_content}...")
        
        # Extrahiere letzten time_offset für Berechnung
        last_inject = previous_injects[-1]
        if isinstance(last_inject, Inject):
            last_time = last_inject.time_offset
        elif isinstance(last_inject, dict):
            last_time = last_inject.get('time_offset', 'T+00:00:00')
        else:
            last_time = 'T+00:00:00'
        
        lines.append(f"\n📅 LETZTER TIME_OFFSET: {last_time}")
        lines.append("💡 Berechne den neuen time_offset CHRONOLOGISCH NACH diesem Zeitpunkt!")
        
        return "\n".join(lines)
    
    def _format_manager_plan(self, manager_plan: Dict[str, Any]) -> str:
        """Formatiert den Manager-Plan."""
        lines = []
        if manager_plan.get("narrative"):
            lines.append(f"Narrative: {manager_plan['narrative']}")
        if manager_plan.get("key_events"):
            lines.append(f"Key Events: {', '.join(manager_plan['key_events'])}")
        if manager_plan.get("affected_assets"):
            lines.append(f"Affected Assets: {', '.join(manager_plan['affected_assets'])}")
        return "\n".join(lines) if lines else "Kein spezifischer Plan"
    
    def _validate_and_correct_assets(
        self, 
        requested_assets: List[str], 
        system_state: Dict[str, Any]
    ) -> List[str]:
        """
        Validiert und korrigiert Asset-IDs.
        
        Filtert nicht-existierende Assets heraus und ersetzt sie durch verfügbare.
        
        Args:
            requested_assets: Vom LLM angeforderte Assets
            system_state: Aktueller Systemzustand
            
        Returns:
            Liste von validen Asset-IDs
        """
        if not requested_assets:
            # Fallback: Verwende Standard-Assets
            return ["SRV-001"]
        
        # Filtere echte Assets aus system_state
        valid_asset_ids = []
        for entity_id in system_state.keys():
            if not (entity_id.startswith("INJ-") or entity_id.startswith("SCEN-")):
                if isinstance(system_state[entity_id], dict):
                    entity_type = system_state[entity_id].get("entity_type", "").lower()
                    if entity_type in ["server", "application", "database", "service", "asset"] or \
                       entity_id.startswith(("SRV-", "APP-", "DB-", "SVC-")):
                        valid_asset_ids.append(entity_id)
        
        # Falls keine Assets verfügbar, verwende Standard-Assets
        if not valid_asset_ids:
            valid_asset_ids = ["SRV-001", "SRV-002"]
        
        # Validiere angeforderte Assets
        corrected_assets = []
        for asset_id in requested_assets:
            # Prüfe ob Asset existiert
            if asset_id in valid_asset_ids:
                corrected_assets.append(asset_id)
            else:
                # Asset existiert nicht - ersetze durch erstes verfügbares Asset
                if valid_asset_ids:
                    replacement = valid_asset_ids[0]
                    if replacement not in corrected_assets:
                        corrected_assets.append(replacement)
                        print(f"⚠️  Asset '{asset_id}' existiert nicht. Ersetzt durch '{replacement}'")
        
        # Falls alle Assets ungültig waren, verwende mindestens ein Standard-Asset
        if not corrected_assets and valid_asset_ids:
            corrected_assets = [valid_asset_ids[0]]
            print(f"⚠️  Alle angeforderte Assets ungültig. Verwende Standard-Asset: {corrected_assets[0]}")
        
        return corrected_assets if corrected_assets else ["SRV-001"]


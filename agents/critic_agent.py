"""
Critic Agent - Validiert Injects auf Logik, Konsistenz und DORA-Konformität.

Verantwortlich für:
- Logische Konsistenz-Prüfung (Widerspruchsfreiheit zur Historie)
- DORA-Compliance-Prüfung (Artikel 25)
- Causal Validity (MITRE ATT&CK Graph Konformität)
- Refine-Loop: Verbesserungsvorschläge
"""

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from state_models import Inject, ValidationResult, CrisisPhase
from workflows.fsm import CrisisFSM
import os
from dotenv import load_dotenv

load_dotenv()


class CriticAgent:
    """
    Critic Agent für Inject-Validierung.
    
    Simuliert Compliance- und Tech-Experten zur Validierung von Injects.
    Führt Reflect-Refine Loop durch, um Injects zu verbessern.
    """
    
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.3):
        """
        Initialisiert den Critic Agent.
        
        Args:
            model_name: OpenAI Modell-Name
            temperature: Temperature (niedrig für konsistente Validierung)
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def validate_inject(
        self,
        inject: Inject,
        previous_injects: List[Inject],
        current_phase: CrisisPhase,
        system_state: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validiert einen Inject.
        
        Args:
            inject: Zu validierender Inject
            previous_injects: Liste vorheriger Injects für Konsistenz
            current_phase: Aktuelle Phase
            system_state: Aktueller Systemzustand
        
        Returns:
            ValidationResult mit Validierungs-Ergebnissen
        """
        # 1. Pydantic-Validierung (automatisch)
        try:
            # Inject ist bereits ein Pydantic-Model, Validierung erfolgt automatisch
            pydantic_valid = True
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                logical_consistency=False,
                dora_compliance=False,
                causal_validity=False,
                errors=[f"Pydantic-Validierung fehlgeschlagen: {e}"]
            )
        
        # 2. FSM-Validierung (Phase-Übergang)
        fsm_valid = self._validate_phase_transition(inject, current_phase, previous_injects)
        
        # 3. LLM-basierte Validierung (Logik, DORA, Causal)
        llm_validation = self._llm_validate(inject, previous_injects, current_phase, system_state)
        
        # Kombiniere Ergebnisse
        is_valid = (
            pydantic_valid and
            fsm_valid and
            llm_validation["logical_consistency"] and
            llm_validation["dora_compliance"] and
            llm_validation["causal_validity"]
        )
        
        return ValidationResult(
            is_valid=is_valid,
            logical_consistency=llm_validation["logical_consistency"] and fsm_valid,
            dora_compliance=llm_validation["dora_compliance"],
            causal_validity=llm_validation["causal_validity"],
            errors=llm_validation.get("errors", []),
            warnings=llm_validation.get("warnings", [])
        )
    
    def _validate_phase_transition(
        self,
        inject: Inject,
        current_phase: CrisisPhase,
        previous_injects: List[Inject]
    ) -> bool:
        """Validiert, ob der Phase-Übergang erlaubt ist."""
        # Prüfe ob Phase-Übergang erlaubt ist
        if inject.phase != current_phase:
            # Phase hat sich geändert - prüfe ob Übergang erlaubt
            return CrisisFSM.can_transition(current_phase, inject.phase)
        
        # Phase bleibt gleich - das ist immer erlaubt
        return True
    
    def _check_dora_article_25_compliance(self, inject: Inject, current_phase: CrisisPhase) -> Dict[str, Any]:
        """
        Prüft DORA Article 25 Compliance mit detaillierter Checkliste.
        
        DORA Article 25: Testing of ICT risk management framework, ICT business continuity 
        policy and ICT response and recovery plans.
        
        Returns:
            Dict mit compliance_status (bool) und checklist_results (dict)
        """
        checklist = {
            "risk_management_framework_tested": False,
            "business_continuity_policy_tested": False,
            "response_plan_tested": False,
            "recovery_plan_tested": False,
            "critical_functions_covered": False,
            "realistic_scenario": False,
            "documentation_adequate": False
        }
        
        issues = []
        warnings = []
        
        # Prüfe ob Inject relevante DORA-Tags hat
        dora_tag = inject.dora_compliance_tag or ""
        content_lower = inject.content.lower()
        
        # 1. Risk Management Framework Testing
        if any(keyword in content_lower for keyword in ["risk assessment", "risk management", "vulnerability", "threat"]):
            checklist["risk_management_framework_tested"] = True
        elif "Art25" in dora_tag or "Risk" in dora_tag:
            checklist["risk_management_framework_tested"] = True
        else:
            warnings.append("Inject könnte Risk Management Framework Testing besser abdecken")
        
        # 2. Business Continuity Policy Testing
        if any(keyword in content_lower for keyword in ["business continuity", "continuity plan", "operational resilience", "service disruption"]):
            checklist["business_continuity_policy_tested"] = True
        elif "Continuity" in dora_tag or "BCP" in dora_tag:
            checklist["business_continuity_policy_tested"] = True
        else:
            if current_phase in [CrisisPhase.ESCALATION_CRISIS, CrisisPhase.CONTAINMENT]:
                warnings.append("Business Continuity Policy sollte in dieser Phase getestet werden")
        
        # 3. Response Plan Testing
        if any(keyword in content_lower for keyword in ["incident response", "response plan", "soc", "security operations", "alert", "detection"]):
            checklist["response_plan_tested"] = True
        elif "Response" in dora_tag or "Incident" in dora_tag:
            checklist["response_plan_tested"] = True
        else:
            if current_phase in [CrisisPhase.INITIAL_INCIDENT, CrisisPhase.SUSPICIOUS_ACTIVITY]:
                warnings.append("Response Plan sollte in dieser Phase getestet werden")
        
        # 4. Recovery Plan Testing
        if any(keyword in content_lower for keyword in ["recovery", "restore", "backup", "restoration", "remediation"]):
            checklist["recovery_plan_tested"] = True
        elif "Recovery" in dora_tag:
            checklist["recovery_plan_tested"] = True
        else:
            if current_phase == CrisisPhase.RECOVERY:
                issues.append("Recovery Plan sollte in Recovery-Phase getestet werden")
        
        # 5. Critical Functions Covered
        if inject.business_impact or any(keyword in content_lower for keyword in ["critical", "essential", "core business", "payment", "transaction"]):
            checklist["critical_functions_covered"] = True
        else:
            warnings.append("Inject könnte kritische Geschäftsfunktionen besser abdecken")
        
        # 6. Realistic Scenario
        if inject.technical_metadata.mitre_id and len(inject.technical_metadata.affected_assets) > 0:
            checklist["realistic_scenario"] = True
        else:
            warnings.append("Inject könnte realistischere technische Details enthalten")
        
        # 7. Documentation Adequate
        if len(inject.content) > 50 and inject.technical_metadata.mitre_id:
            checklist["documentation_adequate"] = True
        else:
            warnings.append("Inject-Dokumentation könnte detaillierter sein")
        
        # Bewerte Compliance
        critical_checks = [
            checklist["risk_management_framework_tested"],
            checklist["realistic_scenario"],
            checklist["documentation_adequate"]
        ]
        
        compliance_status = all(critical_checks) and len(issues) == 0
        
        return {
            "compliance_status": compliance_status,
            "checklist_results": checklist,
            "issues": issues,
            "warnings": warnings
        }
    
    def _llm_validate(
        self,
        inject: Inject,
        previous_injects: List[Inject],
        current_phase: CrisisPhase,
        system_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """LLM-basierte Validierung mit erweiterter DORA-Compliance-Prüfung."""
        
        # DORA Article 25 Compliance Check (vor LLM-Call)
        dora_check = self._check_dora_article_25_compliance(inject, current_phase)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Du bist ein erfahrener Compliance- und Security-Experte für Finanzunternehmen.
Deine Aufgabe ist es, Injects für Krisenszenarien zu validieren.

Prüfe:
1. LOGISCHE KONSISTENZ: Widerspricht der Inject vorherigen Injects? Ist die Sequenz logisch?
2. DORA-COMPLIANCE: Erfüllt der Inject DORA Artikel 25 Anforderungen?
   - Testing of ICT risk management framework
   - Testing of ICT business continuity policy
   - Testing of ICT response and recovery plans
   - Coverage of critical functions
   - Realistic scenario testing
3. CAUSAL VALIDITY: Ist der Inject kausal valide (passt er zur MITRE ATT&CK Sequenz)?

DORA Article 25 Checkliste:
- Risk Management Framework Testing: Wird das Risikomanagement-Framework getestet?
- Business Continuity Policy Testing: Wird die Business Continuity Policy getestet?
- Response Plan Testing: Wird der Incident Response Plan getestet?
- Recovery Plan Testing: Wird der Recovery Plan getestet?
- Critical Functions: Werden kritische Geschäftsfunktionen abgedeckt?
- Realistic Scenario: Ist das Szenario realistisch und relevant?
- Documentation: Ist die Dokumentation ausreichend?

Antworte im JSON-Format:
{{
    "logical_consistency": true/false,
    "dora_compliance": true/false,
    "causal_validity": true/false,
    "dora_checklist": {{
        "risk_management_framework_tested": true/false,
        "business_continuity_policy_tested": true/false,
        "response_plan_tested": true/false,
        "recovery_plan_tested": true/false,
        "critical_functions_covered": true/false,
        "realistic_scenario": true/false,
        "documentation_adequate": true/false
    }},
    "errors": ["Fehler 1", "Fehler 2"],
    "warnings": ["Warnung 1", "Warnung 2"]
}}"""),
            
            ("human", """Validiere folgenden Inject:

Inject:
{inject}

Aktuelle Phase: {current_phase}

Vorherige Injects (für Konsistenz):
{previous_injects}

Systemzustand:
{system_state}

DORA Article 25 Checkliste (automatisch geprüft):
{dora_checklist_results}

Prüfe:
1. Ist der Inject logisch konsistent mit der Historie?
2. Erfüllt er DORA Artikel 25 Anforderungen? (siehe Checkliste oben)
3. Ist er kausal valide (passt MITRE {mitre_id} zur aktuellen Phase)?

Antworte im JSON-Format.""")
        ])
        
        # Formatierung
        previous_injects_str = self._format_previous_injects(previous_injects)
        system_state_str = self._format_system_state(system_state)
        inject_str = self._format_inject(inject)
        
        # Formatiere DORA Checkliste für Prompt
        dora_checklist_str = "\n".join([
            f"- {key.replace('_', ' ').title()}: {'✓' if value else '✗'}"
            for key, value in dora_check["checklist_results"].items()
        ])
        
        chain = prompt | self.llm
        
        # Retry-Logik für LLM-Call
        from utils.retry_handler import safe_llm_call
        
        try:
            def _invoke_chain():
                return chain.invoke({
                    "inject": inject_str,
                    "current_phase": current_phase.value,
                    "previous_injects": previous_injects_str,
                    "system_state": system_state_str,
                    "mitre_id": inject.technical_metadata.mitre_id or "Unknown",
                    "dora_checklist_results": dora_checklist_str
                })
            
            response = safe_llm_call(
                _invoke_chain,
                max_attempts=3,
                default_return=None
            )
            
            if response is None:
                # Fallback: Verwende DORA-Check Ergebnisse
                return {
                    "logical_consistency": True,
                    "dora_compliance": dora_check["compliance_status"],
                    "causal_validity": True,
                    "errors": dora_check["issues"],
                    "warnings": dora_check["warnings"] + ["Validierung konnte nicht durchgeführt werden - LLM-Call fehlgeschlagen"]
                }
            
            # Parse JSON
            import json
            import re
            
            content = response.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            
            if json_match:
                validation = json.loads(json_match.group())
                
                # Kombiniere LLM-Validierung mit DORA-Check
                combined_errors = validation.get("errors", []) + dora_check["issues"]
                combined_warnings = validation.get("warnings", []) + dora_check["warnings"]
                
                # DORA Compliance: Muss sowohl LLM als auch Checkliste erfüllen
                llm_dora_compliance = validation.get("dora_compliance", True)
                checklist_dora_compliance = dora_check["compliance_status"]
                final_dora_compliance = llm_dora_compliance and checklist_dora_compliance
                
                return {
                    "logical_consistency": validation.get("logical_consistency", True),
                    "dora_compliance": final_dora_compliance,
                    "causal_validity": validation.get("causal_validity", True),
                    "errors": combined_errors,
                    "warnings": combined_warnings,
                    "dora_checklist": dora_check["checklist_results"]
                }
            else:
                # Fallback: Verwende DORA-Check Ergebnisse
                return {
                    "logical_consistency": True,
                    "dora_compliance": dora_check["compliance_status"],
                    "causal_validity": True,
                    "errors": dora_check["issues"],
                    "warnings": dora_check["warnings"] + ["Validierung konnte nicht vollständig durchgeführt werden"]
                }
                
        except Exception as e:
            # Fallback bei Fehler: Verwende DORA-Check Ergebnisse
            return {
                "logical_consistency": True,
                "dora_compliance": dora_check["compliance_status"],
                "causal_validity": True,
                "errors": dora_check["issues"],
                "warnings": dora_check["warnings"] + [f"Validierungsfehler: {e}"]
            }
    
    def _format_inject(self, inject: Inject) -> str:
        """Formatiert einen Inject für den Prompt."""
        lines = [
            f"Inject ID: {inject.inject_id}",
            f"Time Offset: {inject.time_offset}",
            f"Phase: {inject.phase.value}",
            f"Source: {inject.source}",
            f"Target: {inject.target}",
            f"Modality: {inject.modality.value}",
            f"Content: {inject.content}",
            f"MITRE ID: {inject.technical_metadata.mitre_id}",
            f"Affected Assets: {', '.join(inject.technical_metadata.affected_assets)}",
            f"DORA Tag: {inject.dora_compliance_tag or 'None'}"
        ]
        return "\n".join(lines)
    
    def _format_previous_injects(self, previous_injects: List[Inject]) -> str:
        """Formatiert vorherige Injects."""
        if not previous_injects:
            return "Keine vorherigen Injects"
        
        lines = []
        for inj in previous_injects[-5:]:  # Letzte 5
            lines.append(f"- {inj.inject_id} ({inj.time_offset}): {inj.content[:60]}...")
        
        return "\n".join(lines)
    
    def _format_system_state(self, system_state: Dict[str, Any]) -> str:
        """Formatiert den Systemzustand."""
        if not system_state or not isinstance(system_state, dict):
            return "Keine Systemzustand-Informationen"
        
        # system_state ist jetzt ein direktes Dictionary: entity_id -> entity_data
        if not system_state:
            return "Alle Systeme im Normalbetrieb"
        
        lines = []
        for entity_id, entity_data in list(system_state.items())[:5]:
            if isinstance(entity_data, dict):
                status = entity_data.get("status", "unknown")
                name = entity_data.get("name", entity_id)
                lines.append(f"- {name} ({entity_id}): {status}")
            else:
                lines.append(f"- {entity_id}: {entity_data}")
        
        return "\n".join(lines) if lines else "Alle Systeme im Normalbetrieb"


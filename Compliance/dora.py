"""
DORA (Digital Operational Resilience Act) Compliance-Framework.
"""

from typing import Dict, Any, Optional, List
from .base import ComplianceFramework, ComplianceRequirement, ComplianceResult, ComplianceStandard
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()


class DORAComplianceFramework(ComplianceFramework):
    """
    DORA Compliance-Framework Implementation.
    
    Fokus auf DORA Article 25 (Testing Requirements).
    """
    
    def __init__(self):
        super().__init__(ComplianceStandard.DORA)
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def _load_requirements(self) -> List[ComplianceRequirement]:
        """Lädt DORA-spezifische Anforderungen."""
        return [
            ComplianceRequirement(
                requirement_id="DORA_Art25_RiskManagement",
                name="Risk Management Framework Testing",
                description="Testszenarien müssen das Risk Management Framework testen",
                category="Testing",
                mandatory=True,
                validation_criteria=[
                    "Szenario testet Risikomanagement-Prozesse",
                    "Risiken werden identifiziert und bewertet",
                    "Risikobewertung ist dokumentiert"
                ]
            ),
            ComplianceRequirement(
                requirement_id="DORA_Art25_BusinessContinuity",
                name="Business Continuity Policy Testing",
                description="Testszenarien müssen Business Continuity Policies testen",
                category="Business Continuity",
                mandatory=True,
                validation_criteria=[
                    "Szenario testet Business Continuity Maßnahmen",
                    "Kritische Funktionen werden identifiziert",
                    "Backup-Systeme werden erwähnt"
                ]
            ),
            ComplianceRequirement(
                requirement_id="DORA_Art25_IncidentResponse",
                name="Incident Response Plan Testing",
                description="Testszenarien müssen Incident Response Pläne testen",
                category="Incident Response",
                mandatory=True,
                validation_criteria=[
                    "SOC-Aktivitäten werden erwähnt",
                    "Incident Response Prozesse werden getestet",
                    "Eskalationswege werden getestet"
                ]
            ),
            ComplianceRequirement(
                requirement_id="DORA_Art25_Recovery",
                name="Recovery Plan Testing",
                description="Testszenarien müssen Recovery Pläne testen",
                category="Recovery",
                mandatory=False,  # Nicht immer in jedem Inject erforderlich
                validation_criteria=[
                    "Recovery-Maßnahmen werden erwähnt",
                    "Wiederherstellungsprozesse werden getestet",
                    "Recovery-Zeiten werden berücksichtigt"
                ]
            ),
            ComplianceRequirement(
                requirement_id="DORA_Art25_CriticalFunctions",
                name="Critical Functions Coverage",
                description="Testszenarien müssen kritische Funktionen abdecken",
                category="Critical Functions",
                mandatory=True,
                validation_criteria=[
                    "Kritische Funktionen werden identifiziert",
                    "Auswirkungen auf kritische Funktionen werden getestet",
                    "Business Impact wird bewertet"
                ]
            ),
            ComplianceRequirement(
                requirement_id="DORA_Art25_Realistic",
                name="Realistic Scenario",
                description="Testszenarien müssen realistisch sein",
                category="Scenario Quality",
                mandatory=True,
                validation_criteria=[
                    "Szenario ist technisch realistisch",
                    "Zeitablauf ist realistisch",
                    "Auswirkungen sind realistisch"
                ]
            ),
            ComplianceRequirement(
                requirement_id="DORA_Art25_Documentation",
                name="Documentation Adequacy",
                description="Testszenarien müssen angemessen dokumentiert sein",
                category="Documentation",
                mandatory=False,
                validation_criteria=[
                    "Inhalt ist detailliert genug",
                    "Technische Details sind vorhanden",
                    "Kontext ist klar"
                ]
            )
        ]
    
    def validate_inject(
        self,
        inject_content: str,
        inject_phase: str,
        inject_metadata: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ComplianceResult:
        """
        Validiert einen Inject auf DORA-Compliance.
        
        Verwendet LLM für semantische Validierung.
        """
        # Erstelle Prompt für LLM-Validierung
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Du bist ein Compliance-Experte für DORA (Digital Operational Resilience Act).
Deine Aufgabe ist es, Injects auf DORA Article 25 Konformität zu prüfen.

DORA Article 25 Anforderungen:
1. Risk Management Framework Testing
2. Business Continuity Policy Testing
3. Incident Response Plan Testing
4. Recovery Plan Testing (optional)
5. Critical Functions Coverage
6. Realistic Scenario
7. Documentation Adequacy (optional)

Prüfe den Inject auf diese Anforderungen und gib eine strukturierte Bewertung zurück."""),
            
            ("human", """Prüfe folgenden Inject auf DORA Article 25 Konformität:

**Phase:** {phase}
**Content:** {content}
**Metadata:** {metadata}

**Vorherige Injects:** {previous_injects}

Bewerte jede Anforderung und gib zurück:
- Welche Anforderungen werden erfüllt?
- Welche Anforderungen fehlen?
- Gibt es Warnungen?

Antworte im JSON-Format:
{{
    "requirements_met": ["DORA_Art25_IncidentResponse", ...],
    "requirements_missing": ["DORA_Art25_BusinessContinuity", ...],
    "warnings": ["Business Continuity könnte stärker betont werden", ...],
    "compliance_score": 0.85,
    "details": {{
        "risk_management": true,
        "business_continuity": false,
        "incident_response": true,
        ...
    }}
}}""")
        ])
        
        # Formatierung für Prompt
        previous_injects_str = ""
        if context and "previous_injects" in context:
            prev_injects = context["previous_injects"]
            if isinstance(prev_injects, list):
                previous_injects_str = "\n".join([
                    f"- {inj.get('inject_id', 'N/A')}: {inj.get('content', '')[:100]}..."
                    for inj in prev_injects[:3]  # Nur letzte 3
                ])
        
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({
                "phase": inject_phase,
                "content": inject_content,
                "metadata": str(inject_metadata),
                "previous_injects": previous_injects_str or "Keine"
            })
            
            # Parse JSON aus Response
            import json
            import re
            
            content = response.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            
            if json_match:
                result_data = json.loads(json_match.group())
                
                # Bestimme ob compliant (alle mandatory requirements erfüllt)
                mandatory_reqs = [req.requirement_id for req in self.requirements if req.mandatory]
                requirements_met = result_data.get("requirements_met", [])
                requirements_missing = result_data.get("requirements_missing", [])
                
                # Prüfe ob alle mandatory requirements erfüllt sind
                mandatory_met = all(req_id in requirements_met for req_id in mandatory_reqs)
                mandatory_missing = [req_id for req_id in mandatory_reqs if req_id not in requirements_met]
                
                is_compliant = mandatory_met and len(mandatory_missing) == 0
                
                return ComplianceResult(
                    is_compliant=is_compliant,
                    standard=ComplianceStandard.DORA,
                    requirements_met=requirements_met,
                    requirements_missing=requirements_missing,
                    warnings=result_data.get("warnings", []),
                    details=result_data.get("details", {})
                )
            else:
                # Fallback: Basierend auf Phase heuristische Bewertung
                return self._heuristic_validation(inject_content, inject_phase, inject_metadata)
                
        except Exception as e:
            # Fallback bei Fehler
            return self._heuristic_validation(inject_content, inject_phase, inject_metadata)
    
    def _heuristic_validation(
        self,
        inject_content: str,
        inject_phase: str,
        inject_metadata: Dict[str, Any]
    ) -> ComplianceResult:
        """Heuristische Validierung als Fallback."""
        requirements_met = []
        requirements_missing = []
        warnings = []
        
        content_lower = inject_content.lower()
        
        # Heuristische Checks
        if "soc" in content_lower or "incident" in content_lower or "response" in content_lower:
            requirements_met.append("DORA_Art25_IncidentResponse")
        else:
            requirements_missing.append("DORA_Art25_IncidentResponse")
        
        if "continuity" in content_lower or "backup" in content_lower or "business" in content_lower:
            requirements_met.append("DORA_Art25_BusinessContinuity")
        else:
            requirements_missing.append("DORA_Art25_BusinessContinuity")
        
        if "recovery" in content_lower or "restore" in content_lower:
            requirements_met.append("DORA_Art25_Recovery")
        
        # Realistic Scenario (immer erfüllt wenn Content lang genug)
        if len(inject_content) > 50:
            requirements_met.append("DORA_Art25_Realistic")
        else:
            requirements_missing.append("DORA_Art25_Realistic")
        
        # Prüfe mandatory requirements
        mandatory_reqs = [req.requirement_id for req in self.requirements if req.mandatory]
        mandatory_met = all(req_id in requirements_met for req_id in mandatory_reqs)
        
        return ComplianceResult(
            is_compliant=mandatory_met,
            standard=ComplianceStandard.DORA,
            requirements_met=requirements_met,
            requirements_missing=requirements_missing,
            warnings=warnings,
            details={"method": "heuristic"}
        )






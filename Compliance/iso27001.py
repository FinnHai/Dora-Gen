"""
ISO 27001 Compliance-Framework.
"""

from typing import Dict, Any, Optional, List
from .base import ComplianceFramework, ComplianceRequirement, ComplianceResult, ComplianceStandard


class ISO27001ComplianceFramework(ComplianceFramework):
    """
    ISO 27001 Compliance-Framework Implementation.
    
    Fokus auf ISO 27001 Controls für Information Security Management.
    """
    
    def __init__(self):
        super().__init__(ComplianceStandard.ISO27001)
    
    def _load_requirements(self) -> List[ComplianceRequirement]:
        """Lädt ISO 27001-spezifische Anforderungen."""
        return [
            ComplianceRequirement(
                requirement_id="ISO27001_A.5.1",
                name="Information Security Policies",
                description="Information Security Policies werden getestet",
                category="Policies",
                mandatory=True,
                validation_criteria=[
                    "Security Policies werden erwähnt",
                    "Policy-Compliance wird getestet"
                ]
            ),
            ComplianceRequirement(
                requirement_id="ISO27001_A.12.6",
                name="Technical Vulnerability Management",
                description="Technische Schwachstellen werden verwaltet",
                category="Vulnerability Management",
                mandatory=True,
                validation_criteria=[
                    "Schwachstellen werden identifiziert",
                    "Vulnerability Management wird getestet"
                ]
            ),
            ComplianceRequirement(
                requirement_id="ISO27001_A.16.1",
                name="Management of Information Security Incidents",
                description="Incident Management wird getestet",
                category="Incident Management",
                mandatory=True,
                validation_criteria=[
                    "Incident Management wird erwähnt",
                    "Incident-Prozesse werden getestet"
                ]
            ),
            ComplianceRequirement(
                requirement_id="ISO27001_A.17.1",
                name="Information Security Continuity",
                description="Business Continuity wird getestet",
                category="Business Continuity",
                mandatory=True,
                validation_criteria=[
                    "Business Continuity wird erwähnt",
                    "Continuity-Pläne werden getestet"
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
        """Validiert einen Inject auf ISO 27001-Compliance."""
        requirements_met = []
        requirements_missing = []
        warnings = []
        
        content_lower = inject_content.lower()
        
        # Heuristische Checks für ISO 27001
        if "policy" in content_lower or "security" in content_lower:
            requirements_met.append("ISO27001_A.5.1")
        else:
            requirements_missing.append("ISO27001_A.5.1")
        
        if "vulnerability" in content_lower or "vuln" in content_lower or "exploit" in content_lower:
            requirements_met.append("ISO27001_A.12.6")
        else:
            requirements_missing.append("ISO27001_A.12.6")
        
        if "incident" in content_lower or "response" in content_lower:
            requirements_met.append("ISO27001_A.16.1")
        else:
            requirements_missing.append("ISO27001_A.16.1")
        
        if "continuity" in content_lower or "backup" in content_lower:
            requirements_met.append("ISO27001_A.17.1")
        else:
            requirements_missing.append("ISO27001_A.17.1")
        
        # Prüfe mandatory requirements
        mandatory_reqs = [req.requirement_id for req in self.requirements if req.mandatory]
        mandatory_met = all(req_id in requirements_met for req_id in mandatory_reqs)
        
        return ComplianceResult(
            is_compliant=mandatory_met,
            standard=ComplianceStandard.ISO27001,
            requirements_met=requirements_met,
            requirements_missing=requirements_missing,
            warnings=warnings,
            details={"method": "heuristic"}
        )






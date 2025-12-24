"""
NIST Cybersecurity Framework Compliance-Framework.
"""

from typing import Dict, Any, Optional, List
from .base import ComplianceFramework, ComplianceRequirement, ComplianceResult, ComplianceStandard


class NISTComplianceFramework(ComplianceFramework):
    """
    NIST Cybersecurity Framework Implementation.
    
    Fokus auf NIST CSF Core Functions: Identify, Protect, Detect, Respond, Recover
    """
    
    def __init__(self):
        super().__init__(ComplianceStandard.NIST)
    
    def _load_requirements(self) -> List[ComplianceRequirement]:
        """Lädt NIST-spezifische Anforderungen."""
        return [
            ComplianceRequirement(
                requirement_id="NIST_ID.AM",
                name="Asset Management",
                description="Assets werden identifiziert und verwaltet",
                category="Identify",
                mandatory=True,
                validation_criteria=[
                    "Assets werden im Inject erwähnt",
                    "Asset-Verwaltung wird getestet"
                ]
            ),
            ComplianceRequirement(
                requirement_id="NIST_PR.AC",
                name="Access Control",
                description="Zugriffskontrollen werden getestet",
                category="Protect",
                mandatory=True,
                validation_criteria=[
                    "Zugriffskontrollen werden erwähnt",
                    "Authentifizierung wird getestet"
                ]
            ),
            ComplianceRequirement(
                requirement_id="NIST_DE.AE",
                name="Security Event Detection",
                description="Sicherheitsereignisse werden erkannt",
                category="Detect",
                mandatory=True,
                validation_criteria=[
                    "SIEM oder Monitoring wird erwähnt",
                    "Ereigniserkennung wird getestet"
                ]
            ),
            ComplianceRequirement(
                requirement_id="NIST_RS.RP",
                name="Response Planning",
                description="Response-Pläne werden getestet",
                category="Respond",
                mandatory=True,
                validation_criteria=[
                    "Incident Response wird erwähnt",
                    "Response-Prozesse werden getestet"
                ]
            ),
            ComplianceRequirement(
                requirement_id="NIST_RC.RP",
                name="Recovery Planning",
                description="Recovery-Pläne werden getestet",
                category="Recover",
                mandatory=False,
                validation_criteria=[
                    "Recovery-Maßnahmen werden erwähnt",
                    "Wiederherstellung wird getestet"
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
        """Validiert einen Inject auf NIST-Compliance."""
        # Implementierung ähnlich wie DORA, aber mit NIST-spezifischen Kriterien
        requirements_met = []
        requirements_missing = []
        warnings = []
        
        content_lower = inject_content.lower()
        
        # Heuristische Checks für NIST
        if "asset" in content_lower or "server" in content_lower or "system" in content_lower:
            requirements_met.append("NIST_ID.AM")
        else:
            requirements_missing.append("NIST_ID.AM")
        
        if "access" in content_lower or "authentication" in content_lower or "login" in content_lower:
            requirements_met.append("NIST_PR.AC")
        else:
            requirements_missing.append("NIST_PR.AC")
        
        if "siem" in content_lower or "detect" in content_lower or "alert" in content_lower:
            requirements_met.append("NIST_DE.AE")
        else:
            requirements_missing.append("NIST_DE.AE")
        
        if "response" in content_lower or "incident" in content_lower:
            requirements_met.append("NIST_RS.RP")
        else:
            requirements_missing.append("NIST_RS.RP")
        
        if "recovery" in content_lower or "restore" in content_lower:
            requirements_met.append("NIST_RC.RP")
        
        # Prüfe mandatory requirements
        mandatory_reqs = [req.requirement_id for req in self.requirements if req.mandatory]
        mandatory_met = all(req_id in requirements_met for req_id in mandatory_reqs)
        
        return ComplianceResult(
            is_compliant=mandatory_met,
            standard=ComplianceStandard.NIST,
            requirements_met=requirements_met,
            requirements_missing=requirements_missing,
            warnings=warnings,
            details={"method": "heuristic"}
        )






"""
Compliance-Framework für variable Compliance-Anforderungen.

Unterstützt verschiedene Compliance-Standards:
- DORA (Digital Operational Resilience Act)
- NIST Cybersecurity Framework
- ISO 27001
- Custom Compliance Standards
"""

from .base import ComplianceFramework, ComplianceRequirement, ComplianceResult
from .dora import DORAComplianceFramework
from .nist import NISTComplianceFramework
from .iso27001 import ISO27001ComplianceFramework

__all__ = [
    "ComplianceFramework",
    "ComplianceRequirement",
    "ComplianceResult",
    "DORAComplianceFramework",
    "NISTComplianceFramework",
    "ISO27001ComplianceFramework",
]






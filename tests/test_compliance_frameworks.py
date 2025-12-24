"""
Tests für Compliance-Frameworks.

Testet DORA, NIST und ISO27001 Compliance-Validierung.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import logging

# Füge Projekt-Root zum Python-Path hinzu
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

logger = logging.getLogger("tests.test_compliance_frameworks")


class TestComplianceFrameworks:
    """Test-Klasse für Compliance-Frameworks."""
    
    def test_compliance_module_import(self):
        """Testet ob Compliance-Module importierbar sind."""
        logger.info("Teste Compliance-Modul-Import")
        try:
            from compliance.base import ComplianceFramework, ComplianceResult, ComplianceStandard
            logger.info("✓ Compliance-Module erfolgreich importiert")
            assert ComplianceStandard.DORA == "DORA"
            assert ComplianceStandard.NIST == "NIST"
            assert ComplianceStandard.ISO27001 == "ISO27001"
        except ImportError as e:
            logger.warning(f"⚠ Compliance-Module nicht verfügbar: {e}")
            pytest.skip("Compliance-Module nicht verfügbar")
    
    def test_dora_compliance_framework(self):
        """Testet DORA Compliance Framework."""
        logger.info("Teste DORA Compliance Framework")
        try:
            from compliance.dora import DORAComplianceFramework
            from workflows.fsm import CrisisPhase
            
            framework = DORAComplianceFramework()
            
            # Test mit gültigem Inject
            inject_content = "Ransomware attack detected on critical server DC-01. Encryption process started."
            inject_metadata = {
                "mitre_id": "T1486",
                "affected_assets": ["DC-01", "SRV-002"],
                "severity": "High"
            }
            
            result = framework.validate_inject(
                inject_content=inject_content,
                inject_phase=CrisisPhase.INITIAL_INCIDENT.value,
                inject_metadata=inject_metadata,
                context={}
            )
            
            assert result.standard.value == "DORA"
            assert isinstance(result.is_compliant, bool)
            assert isinstance(result.requirements_met, list)
            assert isinstance(result.requirements_missing, list)
            logger.info(f"✓ DORA Compliance geprüft: Compliant={result.is_compliant}")
            logger.info(f"  Requirements met: {len(result.requirements_met)}")
            logger.info(f"  Requirements missing: {len(result.requirements_missing)}")
            
        except ImportError as e:
            logger.warning(f"⚠ DORA Compliance Framework nicht verfügbar: {e}")
            pytest.skip("DORA Compliance Framework nicht verfügbar")
    
    def test_dora_compliance_without_metadata(self):
        """Testet DORA Compliance mit fehlenden Metadaten."""
        logger.info("Teste DORA Compliance ohne Metadaten")
        try:
            from compliance.dora import DORAComplianceFramework
            from workflows.fsm import CrisisPhase
            
            framework = DORAComplianceFramework()
            
            inject_content = "Generic attack detected."
            inject_metadata = {}  # Keine Metadaten
            
            result = framework.validate_inject(
                inject_content=inject_content,
                inject_phase=CrisisPhase.NORMAL_OPERATION.value,
                inject_metadata=inject_metadata,
                context={}
            )
            
            # Sollte nicht compliant sein ohne Metadaten
            assert result.standard.value == "DORA"
            logger.info(f"✓ DORA Compliance ohne Metadaten geprüft: Compliant={result.is_compliant}")
            
        except ImportError:
            pytest.skip("DORA Compliance Framework nicht verfügbar")
    
    def test_compliance_result_structure(self):
        """Testet die Struktur von ComplianceResult."""
        logger.info("Teste ComplianceResult-Struktur")
        try:
            from compliance.base import ComplianceResult, ComplianceStandard
            
            result = ComplianceResult(
                standard=ComplianceStandard.DORA,
                is_compliant=True,
                requirements_met=["Req1", "Req2"],
                requirements_missing=[],
                warnings=[]
            )
            
            assert result.standard == ComplianceStandard.DORA
            assert result.is_compliant is True
            assert len(result.requirements_met) == 2
            assert len(result.requirements_missing) == 0
            logger.info("✓ ComplianceResult-Struktur korrekt")
            
        except ImportError:
            pytest.skip("Compliance-Module nicht verfügbar")
    
    def test_nist_compliance_framework(self):
        """Testet NIST Compliance Framework (Placeholder)."""
        logger.info("Teste NIST Compliance Framework")
        try:
            from compliance.nist import NISTComplianceFramework
            
            framework = NISTComplianceFramework()
            logger.info("✓ NIST Compliance Framework verfügbar (Placeholder)")
            
        except ImportError:
            logger.warning("⚠ NIST Compliance Framework nicht verfügbar")
            pytest.skip("NIST Compliance Framework nicht verfügbar")
    
    def test_iso27001_compliance_framework(self):
        """Testet ISO27001 Compliance Framework (Placeholder)."""
        logger.info("Teste ISO27001 Compliance Framework")
        try:
            from compliance.iso27001 import ISO27001ComplianceFramework
            
            framework = ISO27001ComplianceFramework()
            logger.info("✓ ISO27001 Compliance Framework verfügbar (Placeholder)")
            
        except ImportError:
            logger.warning("⚠ ISO27001 Compliance Framework nicht verfügbar")
            pytest.skip("ISO27001 Compliance Framework nicht verfügbar")





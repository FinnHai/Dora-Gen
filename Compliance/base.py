"""
Basis-Compliance-Framework für abstrakte Compliance-Anforderungen.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


class ComplianceStandard(str, Enum):
    """Unterstützte Compliance-Standards."""
    DORA = "DORA"
    NIST = "NIST"
    ISO27001 = "ISO27001"
    CUSTOM = "CUSTOM"


class ComplianceRequirement(BaseModel):
    """Einzelne Compliance-Anforderung."""
    requirement_id: str = Field(
        ...,
        description="Eindeutige ID der Anforderung (z.B. 'DORA_Art25_Testing')"
    )
    name: str = Field(
        ...,
        description="Name der Anforderung"
    )
    description: str = Field(
        ...,
        description="Beschreibung der Anforderung"
    )
    category: str = Field(
        ...,
        description="Kategorie (z.B. 'Testing', 'Incident Response', 'Business Continuity')"
    )
    mandatory: bool = Field(
        True,
        description="Ist diese Anforderung obligatorisch?"
    )
    validation_criteria: List[str] = Field(
        default_factory=list,
        description="Liste von Validierungskriterien"
    )


class ComplianceResult(BaseModel):
    """Ergebnis einer Compliance-Validierung."""
    is_compliant: bool = Field(
        ...,
        description="Ist der Inject compliant?"
    )
    standard: ComplianceStandard = Field(
        ...,
        description="Verwendeter Compliance-Standard"
    )
    requirements_met: List[str] = Field(
        default_factory=list,
        description="Liste von erfüllten Anforderungen (IDs)"
    )
    requirements_missing: List[str] = Field(
        default_factory=list,
        description="Liste von nicht erfüllten Anforderungen (IDs)"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Compliance-Warnungen"
    )
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Zusätzliche Details zur Compliance-Prüfung"
    )


class ComplianceFramework(ABC):
    """
    Abstraktes Compliance-Framework.
    
    Jedes Compliance-Framework muss diese Methoden implementieren.
    """
    
    def __init__(self, standard: ComplianceStandard):
        """
        Initialisiert das Compliance-Framework.
        
        Args:
            standard: Der Compliance-Standard
        """
        self.standard = standard
        self.requirements = self._load_requirements()
    
    @abstractmethod
    def _load_requirements(self) -> List[ComplianceRequirement]:
        """
        Lädt die Compliance-Anforderungen für diesen Standard.
        
        Returns:
            Liste von Compliance-Anforderungen
        """
        pass
    
    @abstractmethod
    def validate_inject(
        self,
        inject_content: str,
        inject_phase: str,
        inject_metadata: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ComplianceResult:
        """
        Validiert einen Inject auf Compliance.
        
        Args:
            inject_content: Der Inhalt des Injects
            inject_phase: Die aktuelle Phase
            inject_metadata: Technische Metadaten des Injects
            context: Optional - Zusätzlicher Kontext (vorherige Injects, etc.)
        
        Returns:
            ComplianceResult mit Validierungsergebnissen
        """
        pass
    
    def get_requirements(self) -> List[ComplianceRequirement]:
        """
        Gibt alle Compliance-Anforderungen zurück.
        
        Returns:
            Liste von Compliance-Anforderungen
        """
        return self.requirements
    
    def get_requirement_by_id(self, requirement_id: str) -> Optional[ComplianceRequirement]:
        """
        Gibt eine spezifische Anforderung zurück.
        
        Args:
            requirement_id: ID der Anforderung
        
        Returns:
            ComplianceRequirement oder None
        """
        for req in self.requirements:
            if req.requirement_id == requirement_id:
                return req
        return None
    
    def get_requirements_by_category(self, category: str) -> List[ComplianceRequirement]:
        """
        Gibt alle Anforderungen einer Kategorie zurück.
        
        Args:
            category: Kategorie-Name
        
        Returns:
            Liste von Compliance-Anforderungen
        """
        return [req for req in self.requirements if req.category == category]






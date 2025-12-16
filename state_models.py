"""
State Models für DORA-konformen Szenariengenerator.

Definiert Pydantic-Modelle für:
- Inject-Schema (MSEL-Einwürfe)
- State Management (FSM-Phasen)
- Knowledge Graph Entitäten
- Technical Metadata
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class CrisisPhase(str, Enum):
    """Finite State Machine Phasen für Krisenszenarien."""
    NORMAL_OPERATION = "NORMAL_OPERATION"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    INITIAL_INCIDENT = "INITIAL_INCIDENT"
    ESCALATION_CRISIS = "ESCALATION_CRISIS"
    CONTAINMENT = "CONTAINMENT"
    RECOVERY = "RECOVERY"


class ScenarioType(str, Enum):
    """Unterstützte Szenario-Archetypen."""
    RANSOMWARE_DOUBLE_EXTORTION = "RANSOMWARE_DOUBLE_EXTORTION"
    DDOS_CRITICAL_FUNCTIONS = "DDOS_CRITICAL_FUNCTIONS"
    SUPPLY_CHAIN_COMPROMISE = "SUPPLY_CHAIN_COMPROMISE"
    INSIDER_THREAT_DATA_MANIPULATION = "INSIDER_THREAT_DATA_MANIPULATION"


class ScenarioEndCondition(str, Enum):
    """Mögliche End-Bedingungen für ein Szenario."""
    CONTINUE = "CONTINUE"
    FATAL = "FATAL"  # Fataler Ausgang - System komplett kompromittiert
    VICTORY = "VICTORY"  # Sieg - Bedrohung erfolgreich abgewehrt
    NORMAL_END = "NORMAL_END"  # Normales Ende - Recovery abgeschlossen


class UserDecision(BaseModel):
    """Benutzer-Entscheidung an einem Decision-Point."""
    decision_id: str = Field(..., description="Eindeutige Decision-ID")
    timestamp: datetime = Field(default_factory=datetime.now)
    decision_type: str = Field(..., description="Typ der Entscheidung (z.B. 'response_action', 'resource_allocation')")
    choice: str = Field(..., description="Gewählte Option")
    reasoning: Optional[str] = Field(None, description="Begründung der Entscheidung")
    impact: Optional[Dict[str, Any]] = Field(None, description="Erwartete Auswirkungen der Entscheidung")


class InjectModality(str, Enum):
    """Kommunikationsmodalität für Injects."""
    SIEM_ALERT = "SIEM Alert"
    EMAIL = "Email"
    PHONE_CALL = "Phone Call"
    PHYSICAL_EVENT = "Physical Event"
    NEWS_REPORT = "News Report"
    INTERNAL_REPORT = "Internal Report"


class TechnicalMetadata(BaseModel):
    """Technische Metadaten für einen Inject."""
    mitre_id: Optional[str] = Field(
        None,
        description="MITRE ATT&CK Technique ID (z.B. T1110)"
    )
    affected_assets: List[str] = Field(
        default_factory=list,
        description="Liste betroffener Assets (Server, Applikationen, etc.)"
    )
    ioc_hash: Optional[str] = Field(
        None,
        description="Indikator of Compromise Hash"
    )
    ioc_ip: Optional[str] = Field(
        None,
        description="Indikator of Compromise IP-Adresse"
    )
    ioc_domain: Optional[str] = Field(
        None,
        description="Indikator of Compromise Domain"
    )
    severity: Optional[str] = Field(
        None,
        description="Schweregrad (Low, Medium, High, Critical)"
    )


class Inject(BaseModel):
    """
    MSEL-Inject Modell gemäß DORA-Anforderungen.
    
    Jeder Inject repräsentiert einen einzelnen "Einwurf" in einem
    Krisenszenario und muss logisch konsistent und DORA-konform sein.
    """
    inject_id: str = Field(
        ...,
        description="Eindeutige Inject-ID (z.B. INJ-005)",
        pattern=r"^INJ-\d{3,}$"
    )
    time_offset: str = Field(
        ...,
        description="Zeitversatz vom Szenario-Start (z.B. T+02:00)",
        pattern=r"^T\+(\d{2}):(\d{2})$"
    )
    phase: CrisisPhase = Field(
        ...,
        description="Aktuelle Phase im FSM"
    )
    source: str = Field(
        ...,
        description="Quelle des Injects (z.B. 'Red Team / Attacker', 'Blue Team / SOC')"
    )
    target: str = Field(
        ...,
        description="Empfänger des Injects (z.B. 'Blue Team / SOC', 'Management')"
    )
    modality: InjectModality = Field(
        ...,
        description="Kommunikationsmodalität"
    )
    content: str = Field(
        ...,
        description="Inhalt des Injects (Text)",
        min_length=10
    )
    technical_metadata: TechnicalMetadata = Field(
        ...,
        description="Technische Metadaten (MITRE, IOCs, etc.)"
    )
    dora_compliance_tag: Optional[str] = Field(
        None,
        description="DORA Compliance Tag (z.B. 'Art25_VulnScan', 'Art25_IncidentResponse')"
    )
    business_impact: Optional[str] = Field(
        None,
        description="Geschäftliche Auswirkung (z.B. 'Zahlungsverkehr gestoppt')"
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="Erstellungszeitpunkt"
    )

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validiert, dass der Content nicht leer ist."""
        if not v or len(v.strip()) < 10:
            raise ValueError("Content muss mindestens 10 Zeichen lang sein")
        return v.strip()


class ScenarioState(BaseModel):
    """
    Zustand eines laufenden Szenarios.
    
    Wird von LangGraph für State Management verwendet.
    """
    scenario_id: str = Field(
        ...,
        description="Eindeutige Szenario-ID"
    )
    scenario_type: ScenarioType = Field(
        ...,
        description="Typ des Szenarios"
    )
    current_phase: CrisisPhase = Field(
        default=CrisisPhase.NORMAL_OPERATION,
        description="Aktuelle FSM-Phase"
    )
    injects: List[Inject] = Field(
        default_factory=list,
        description="Liste aller generierten Injects"
    )
    start_time: datetime = Field(
        default_factory=datetime.now,
        description="Startzeitpunkt des Szenarios"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Zusätzliche Metadaten"
    )


class KnowledgeGraphEntity(BaseModel):
    """
    Entität für den Neo4j Knowledge Graph.
    
    Repräsentiert Assets, Abteilungen, Systeme etc.
    """
    entity_id: str = Field(
        ...,
        description="Eindeutige Entity-ID"
    )
    entity_type: str = Field(
        ...,
        description="Typ der Entität (z.B. 'Server', 'Application', 'Department')"
    )
    name: str = Field(
        ...,
        description="Name der Entität"
    )
    status: str = Field(
        default="online",
        description="Status (online, offline, compromised, encrypted, etc.)"
    )
    properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Zusätzliche Properties"
    )
    relationships: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Beziehungen zu anderen Entitäten (z.B. [{'target': 'APP-001', 'type': 'RUNS_ON'}])"
    )


class GraphStateUpdate(BaseModel):
    """
    Update für den Knowledge Graph State.
    
    Wird verwendet, um Änderungen am Systemzustand zu tracken.
    """
    entity_id: str = Field(
        ...,
        description="ID der betroffenen Entität"
    )
    status_change: str = Field(
        ...,
        description="Neuer Status (z.B. 'offline', 'compromised')"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Zeitpunkt der Änderung"
    )
    caused_by_inject: Optional[str] = Field(
        None,
        description="Inject-ID, die diese Änderung verursacht hat"
    )
    second_order_effects: List[str] = Field(
        default_factory=list,
        description="IDs von Entitäten, die indirekt betroffen sind"
    )


class ValidationResult(BaseModel):
    """Ergebnis der Validierung durch den Critic-Agent."""
    is_valid: bool = Field(
        ...,
        description="Ist der Inject valide?"
    )
    logical_consistency: bool = Field(
        ...,
        description="Ist der Inject logisch konsistent mit der Historie?"
    )
    dora_compliance: bool = Field(
        ...,
        description="Erfüllt der Inject DORA-Anforderungen?"
    )
    causal_validity: bool = Field(
        ...,
        description="Ist der Inject kausal valide (MITRE ATT&CK Graph)?"
    )
    errors: List[str] = Field(
        default_factory=list,
        description="Liste von Fehlermeldungen"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Liste von Warnungen"
    )


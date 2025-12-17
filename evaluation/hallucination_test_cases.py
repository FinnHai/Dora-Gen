"""
Edge Cases für Halluzinations-Provokation.

Definiert systematisch Testfälle, die typische Halluzinationen provozieren:
- FSM-Phasen-Verstöße
- State-Inkonsistenzen
- MITRE ATT&CK Sequenz-Fehler
- Asset-Naming-Inkonsistenzen
- Temporale Inkonsistenzen
- Kausale Widersprüche

Basierend auf wissenschaftlichen Evaluationsmethoden für LLM-Halluzinationen.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
from state_models import Inject, CrisisPhase, InjectModality, TechnicalMetadata
from datetime import datetime


class HallucinationType(str, Enum):
    """Kategorien von Halluzinationen basierend auf wissenschaftlicher Literatur."""
    FSM_VIOLATION = "FSM_VIOLATION"  # Ungültiger Phasen-Übergang
    STATE_INCONSISTENCY = "STATE_INCONSISTENCY"  # Widerspruch zum Systemzustand
    MITRE_SEQUENCE_ERROR = "MITRE_SEQUENCE_ERROR"  # Unmögliche MITRE-Sequenz
    ASSET_NONEXISTENT = "ASSET_NONEXISTENT"  # Asset existiert nicht im Graph
    TEMPORAL_INCONSISTENCY = "TEMPORAL_INCONSISTENCY"  # Zeitliche Widersprüche
    CAUSAL_CONTRADICTION = "CAUSAL_CONTRADICTION"  # Kausale Widersprüche
    ASSET_NAME_INCONSISTENCY = "ASSET_NAME_INCONSISTENCY"  # Inkonsistente Asset-Namen
    SEVERITY_MISMATCH = "SEVERITY_MISMATCH"  # Schweregrad passt nicht zur Phase


@dataclass
class HallucinationTestCase:
    """
    Ein Testfall, der eine spezifische Halluzination provoziert.
    
    Attributes:
        test_id: Eindeutige Test-ID
        hallucination_type: Typ der provozierten Halluzination
        description: Beschreibung des Testfalls
        inject: Inject, der die Halluzination provoziert
        expected_detection: Ob das System die Halluzination erkennen sollte
        previous_injects: Vorherige Injects für Kontext
        system_state: Systemzustand zum Zeitpunkt des Tests
        current_phase: Aktuelle FSM-Phase
        ground_truth: Ground Truth (ob es wirklich eine Halluzination ist)
    """
    test_id: str
    hallucination_type: HallucinationType
    description: str
    inject: Inject
    expected_detection: bool
    previous_injects: List[Inject]
    system_state: Dict[str, Any]
    current_phase: CrisisPhase
    ground_truth: bool = True  # Ist es wirklich eine Halluzination?


class HallucinationTestGenerator:
    """
    Generiert systematisch Edge Cases für Halluzinations-Tests.
    
    Basierend auf:
    - FSM-Constraints (Phasen-Übergänge)
    - Neo4j State Constraints (Asset-Existenz, Status-Konsistenz)
    - MITRE ATT&CK Sequenz-Regeln
    - Temporale Konsistenz-Regeln
    """
    
    def __init__(self):
        """Initialisiert den Test-Generator."""
        pass
    
    def generate_fsm_violation_cases(self) -> List[HallucinationTestCase]:
        """
        Generiert Testfälle für FSM-Verstöße.
        
        Beispiele:
        - Direkter Sprung von NORMAL_OPERATION zu RECOVERY
        - Rückkehr von RECOVERY zu INITIAL_INCIDENT
        - Überspringen von CONTAINMENT
        """
        cases = []
        
        # Case 1: Direkter Sprung von NORMAL_OPERATION zu RECOVERY (unmöglich)
        case1 = HallucinationTestCase(
            test_id="FSM-001",
            hallucination_type=HallucinationType.FSM_VIOLATION,
            description="Direkter Sprung von NORMAL_OPERATION zu RECOVERY ohne Zwischenphasen",
            inject=Inject(
                inject_id="INJ-FSM-001",
                time_offset="T+01:00",
                phase=CrisisPhase.RECOVERY,  # Verstoß: Kann nicht direkt zu RECOVERY
                source="Red Team / Attacker",
                target="Blue Team / SOC",
                modality=InjectModality.SIEM_ALERT,
                content="System recovery completed. All services restored.",
                technical_metadata=TechnicalMetadata(
                    mitre_id="T1490",
                    affected_assets=["SRV-001"],
                    severity="Low"
                )
            ),
            expected_detection=True,
            previous_injects=[],
            system_state={},
            current_phase=CrisisPhase.NORMAL_OPERATION
        )
        cases.append(case1)
        
        # Case 2: Rückkehr von RECOVERY zu INITIAL_INCIDENT (unmöglich)
        case2 = HallucinationTestCase(
            test_id="FSM-002",
            hallucination_type=HallucinationType.FSM_VIOLATION,
            description="Rückkehr von RECOVERY zu INITIAL_INCIDENT (keine Rückwärts-Übergänge)",
            inject=Inject(
                inject_id="INJ-FSM-002",
                time_offset="T+10:00",
                phase=CrisisPhase.INITIAL_INCIDENT,  # Verstoß: Kann nicht zurück
                source="Red Team / Attacker",
                target="Blue Team / SOC",
                modality=InjectModality.SIEM_ALERT,
                content="New attack detected on server SRV-001.",
                technical_metadata=TechnicalMetadata(
                    mitre_id="T1055",
                    affected_assets=["SRV-001"],
                    severity="High"
                )
            ),
            expected_detection=True,
            previous_injects=[
                Inject(
                    inject_id="INJ-PREV-001",
                    time_offset="T+08:00",
                    phase=CrisisPhase.RECOVERY,
                    source="Blue Team / SOC",
                    target="Management",
                    modality=InjectModality.INTERNAL_REPORT,
                    content="Recovery phase initiated.",
                    technical_metadata=TechnicalMetadata(
                        mitre_id="T1490",
                        affected_assets=["SRV-001"],
                        severity="Low"
                    )
                )
            ],
            system_state={"SRV-001": {"status": "online", "name": "SRV-001"}},
            current_phase=CrisisPhase.RECOVERY
        )
        cases.append(case2)
        
        # Case 3: Überspringen von CONTAINMENT (möglich, aber verdächtig)
        case3 = HallucinationTestCase(
            test_id="FSM-003",
            hallucination_type=HallucinationType.FSM_VIOLATION,
            description="Direkter Sprung von ESCALATION_CRISIS zu RECOVERY ohne CONTAINMENT",
            inject=Inject(
                inject_id="INJ-FSM-003",
                time_offset="T+05:00",
                phase=CrisisPhase.RECOVERY,  # Verstoß: CONTAINMENT fehlt
                source="Blue Team / SOC",
                target="Management",
                modality=InjectModality.INTERNAL_REPORT,
                content="Recovery initiated after crisis escalation.",
                technical_metadata=TechnicalMetadata(
                    mitre_id="T1490",
                    affected_assets=["SRV-001"],
                    severity="Medium"
                )
            ),
            expected_detection=True,
            previous_injects=[
                Inject(
                    inject_id="INJ-PREV-002",
                    time_offset="T+04:00",
                    phase=CrisisPhase.ESCALATION_CRISIS,
                    source="Red Team / Attacker",
                    target="Blue Team / SOC",
                    modality=InjectModality.SIEM_ALERT,
                    content="Critical systems compromised.",
                    technical_metadata=TechnicalMetadata(
                        mitre_id="T1486",
                        affected_assets=["SRV-001"],
                        severity="Critical"
                    )
                )
            ],
            system_state={"SRV-001": {"status": "compromised", "name": "SRV-001"}},
            current_phase=CrisisPhase.ESCALATION_CRISIS
        )
        cases.append(case3)
        
        return cases
    
    def generate_state_inconsistency_cases(self) -> List[HallucinationTestCase]:
        """
        Generiert Testfälle für State-Inkonsistenzen.
        
        Beispiele:
        - Asset existiert nicht im Graph
        - Asset ist bereits offline, wird aber als online behandelt
        - Asset-Status widerspricht vorherigen Injects
        """
        cases = []
        
        # Case 1: Asset existiert nicht im Graph
        case1 = HallucinationTestCase(
            test_id="STATE-001",
            hallucination_type=HallucinationType.ASSET_NONEXISTENT,
            description="Inject referenziert Asset, das nicht im Knowledge Graph existiert",
            inject=Inject(
                inject_id="INJ-STATE-001",
                time_offset="T+02:00",
                phase=CrisisPhase.INITIAL_INCIDENT,
                source="Red Team / Attacker",
                target="Blue Team / SOC",
                modality=InjectModality.SIEM_ALERT,
                content="Attack detected on server NONEXISTENT-SRV-999.",
                technical_metadata=TechnicalMetadata(
                    mitre_id="T1055",
                    affected_assets=["NONEXISTENT-SRV-999"],  # Existiert nicht
                    severity="High"
                )
            ),
            expected_detection=True,
            previous_injects=[],
            system_state={
                "SRV-001": {"status": "online", "name": "SRV-001"},
                "SRV-002": {"status": "online", "name": "SRV-002"}
            },
            current_phase=CrisisPhase.INITIAL_INCIDENT
        )
        cases.append(case1)
        
        # Case 2: Asset ist bereits offline, wird aber als online attackiert
        case2 = HallucinationTestCase(
            test_id="STATE-002",
            hallucination_type=HallucinationType.STATE_INCONSISTENCY,
            description="Inject behandelt Asset als online, obwohl es bereits offline ist",
            inject=Inject(
                inject_id="INJ-STATE-002",
                time_offset="T+03:00",
                phase=CrisisPhase.ESCALATION_CRISIS,
                source="Red Team / Attacker",
                target="Blue Team / SOC",
                modality=InjectModality.SIEM_ALERT,
                content="Lateral movement detected from SRV-001 to SRV-002.",
                technical_metadata=TechnicalMetadata(
                    mitre_id="T1021",
                    affected_assets=["SRV-001", "SRV-002"],
                    severity="High"
                )
            ),
            expected_detection=True,
            previous_injects=[
                Inject(
                    inject_id="INJ-PREV-003",
                    time_offset="T+02:00",
                    phase=CrisisPhase.INITIAL_INCIDENT,
                    source="Red Team / Attacker",
                    target="Blue Team / SOC",
                    modality=InjectModality.SIEM_ALERT,
                    content="SRV-001 compromised and taken offline.",
                    technical_metadata=TechnicalMetadata(
                        mitre_id="T1486",
                        affected_assets=["SRV-001"],
                        severity="Critical"
                    )
                )
            ],
            system_state={
                "SRV-001": {"status": "offline", "name": "SRV-001"},  # Bereits offline
                "SRV-002": {"status": "online", "name": "SRV-002"}
            },
            current_phase=CrisisPhase.ESCALATION_CRISIS
        )
        cases.append(case2)
        
        # Case 3: Asset-Name-Inkonsistenz (verschiedene Namen für dasselbe Asset)
        case3 = HallucinationTestCase(
            test_id="STATE-003",
            hallucination_type=HallucinationType.ASSET_NAME_INCONSISTENCY,
            description="Asset wird mit unterschiedlichen Namen referenziert",
            inject=Inject(
                inject_id="INJ-STATE-003",
                time_offset="T+04:00",
                phase=CrisisPhase.CONTAINMENT,
                source="Blue Team / SOC",
                target="Management",
                modality=InjectModality.INTERNAL_REPORT,
                content="Containment measures applied to web-server-01.",  # Anderer Name
                technical_metadata=TechnicalMetadata(
                    mitre_id="T1490",
                    affected_assets=["web-server-01"],  # Name stimmt nicht mit SRV-001 überein
                    severity="Medium"
                )
            ),
            expected_detection=True,
            previous_injects=[
                Inject(
                    inject_id="INJ-PREV-004",
                    time_offset="T+03:00",
                    phase=CrisisPhase.INITIAL_INCIDENT,
                    source="Red Team / Attacker",
                    target="Blue Team / SOC",
                    modality=InjectModality.SIEM_ALERT,
                    content="Attack on SRV-001 detected.",  # Ursprünglicher Name
                    technical_metadata=TechnicalMetadata(
                        mitre_id="T1055",
                        affected_assets=["SRV-001"],
                        severity="High"
                    )
                )
            ],
            system_state={
                "SRV-001": {"status": "compromised", "name": "SRV-001"}
            },
            current_phase=CrisisPhase.CONTAINMENT
        )
        cases.append(case3)
        
        return cases
    
    def generate_mitre_sequence_error_cases(self) -> List[HallucinationTestCase]:
        """
        Generiert Testfälle für MITRE ATT&CK Sequenz-Fehler.
        
        Beispiele:
        - Exfiltration vor Initial Access
        - Persistence vor Execution
        - Unmögliche TTP-Kombinationen
        """
        cases = []
        
        # Case 1: Exfiltration vor Initial Access (unmöglich)
        case1 = HallucinationTestCase(
            test_id="MITRE-001",
            hallucination_type=HallucinationType.MITRE_SEQUENCE_ERROR,
            description="Exfiltration (T1041) vor Initial Access - unmögliche Sequenz",
            inject=Inject(
                inject_id="INJ-MITRE-001",
                time_offset="T+01:00",
                phase=CrisisPhase.INITIAL_INCIDENT,
                source="Red Team / Attacker",
                target="Blue Team / SOC",
                modality=InjectModality.SIEM_ALERT,
                content="Data exfiltration detected from SRV-001.",
                technical_metadata=TechnicalMetadata(
                    mitre_id="T1041",  # Exfiltration - sollte nicht als erstes kommen
                    affected_assets=["SRV-001"],
                    severity="High"
                )
            ),
            expected_detection=True,
            previous_injects=[],  # Keine vorherigen Injects = kein Initial Access
            system_state={"SRV-001": {"status": "online", "name": "SRV-001"}},
            current_phase=CrisisPhase.INITIAL_INCIDENT
        )
        cases.append(case1)
        
        # Case 2: Persistence vor Execution (unmöglich)
        case2 = HallucinationTestCase(
            test_id="MITRE-002",
            hallucination_type=HallucinationType.MITRE_SEQUENCE_ERROR,
            description="Persistence (T1543) vor Execution - unmögliche Sequenz",
            inject=Inject(
                inject_id="INJ-MITRE-002",
                time_offset="T+02:00",
                phase=CrisisPhase.SUSPICIOUS_ACTIVITY,
                source="Red Team / Attacker",
                target="Blue Team / SOC",
                modality=InjectModality.SIEM_ALERT,
                content="Persistence mechanism detected on SRV-001.",
                technical_metadata=TechnicalMetadata(
                    mitre_id="T1543",  # Persistence - sollte nach Execution kommen
                    affected_assets=["SRV-001"],
                    severity="Medium"
                )
            ),
            expected_detection=True,
            previous_injects=[
                Inject(
                    inject_id="INJ-PREV-005",
                    time_offset="T+01:00",
                    phase=CrisisPhase.NORMAL_OPERATION,
                    source="Red Team / Attacker",
                    target="Blue Team / SOC",
                    modality=InjectModality.SIEM_ALERT,
                    content="Suspicious network activity detected.",
                    technical_metadata=TechnicalMetadata(
                        mitre_id="T1595",  # Active Scanning - noch kein Execution
                        affected_assets=["SRV-001"],
                        severity="Low"
                    )
                )
            ],
            system_state={"SRV-001": {"status": "online", "name": "SRV-001"}},
            current_phase=CrisisPhase.SUSPICIOUS_ACTIVITY
        )
        cases.append(case2)
        
        return cases
    
    def generate_temporal_inconsistency_cases(self) -> List[HallucinationTestCase]:
        """
        Generiert Testfälle für temporale Inkonsistenzen.
        
        Beispiele:
        - Zeitstempel geht zurück
        - Event passiert vor seinem kausalen Vorgänger
        """
        cases = []
        
        # Case 1: Zeitstempel geht zurück
        case1 = HallucinationTestCase(
            test_id="TEMPORAL-001",
            hallucination_type=HallucinationType.TEMPORAL_INCONSISTENCY,
            description="Inject hat früheren Zeitstempel als vorheriger Inject",
            inject=Inject(
                inject_id="INJ-TEMPORAL-001",
                time_offset="T+01:00",  # Früher als vorheriger (T+02:00)
                phase=CrisisPhase.INITIAL_INCIDENT,
                source="Red Team / Attacker",
                target="Blue Team / SOC",
                modality=InjectModality.SIEM_ALERT,
                content="Initial attack detected.",
                technical_metadata=TechnicalMetadata(
                    mitre_id="T1078",
                    affected_assets=["SRV-001"],
                    severity="High"
                )
            ),
            expected_detection=True,
            previous_injects=[
                Inject(
                    inject_id="INJ-PREV-006",
                    time_offset="T+02:00",  # Später als neuer Inject
                    phase=CrisisPhase.ESCALATION_CRISIS,
                    source="Red Team / Attacker",
                    target="Blue Team / SOC",
                    modality=InjectModality.SIEM_ALERT,
                    content="Escalation detected.",
                    technical_metadata=TechnicalMetadata(
                        mitre_id="T1486",
                        affected_assets=["SRV-001"],
                        severity="Critical"
                    )
                )
            ],
            system_state={"SRV-001": {"status": "compromised", "name": "SRV-001"}},
            current_phase=CrisisPhase.ESCALATION_CRISIS
        )
        cases.append(case1)
        
        return cases
    
    def generate_all_test_cases(self) -> List[HallucinationTestCase]:
        """Generiert alle Testfälle."""
        all_cases = []
        all_cases.extend(self.generate_fsm_violation_cases())
        all_cases.extend(self.generate_state_inconsistency_cases())
        all_cases.extend(self.generate_mitre_sequence_error_cases())
        all_cases.extend(self.generate_temporal_inconsistency_cases())
        return all_cases
    
    def get_test_cases_by_type(self, hallucination_type: HallucinationType) -> List[HallucinationTestCase]:
        """Gibt Testfälle eines bestimmten Typs zurück."""
        all_cases = self.generate_all_test_cases()
        return [case for case in all_cases if case.hallucination_type == hallucination_type]

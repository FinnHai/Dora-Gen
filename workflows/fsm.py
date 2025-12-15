"""
Finite State Machine (FSM) für Krisenphasen-Übergänge.

Stellt sicher, dass Phasen-Übergänge nur unter logischen
Bedingungen erlaubt sind.
"""

from state_models import CrisisPhase
from typing import Dict, List, Callable, Optional


class CrisisFSM:
    """
    Finite State Machine für Krisenszenarien.
    
    Modelliert die erlaubten Übergänge zwischen Phasen:
    Normalbetrieb → Verdächtige Aktivität → Initialer Vorfall 
    → Eskalation/Krise → Eindämmung → Wiederherstellung
    """
    
    # Erlaubte Übergänge (von → zu)
    ALLOWED_TRANSITIONS: Dict[CrisisPhase, List[CrisisPhase]] = {
        CrisisPhase.NORMAL_OPERATION: [
            CrisisPhase.SUSPICIOUS_ACTIVITY,
            CrisisPhase.INITIAL_INCIDENT  # Kann direkt zum Vorfall springen
        ],
        CrisisPhase.SUSPICIOUS_ACTIVITY: [
            CrisisPhase.INITIAL_INCIDENT,
            CrisisPhase.NORMAL_OPERATION  # False Positive
        ],
        CrisisPhase.INITIAL_INCIDENT: [
            CrisisPhase.ESCALATION_CRISIS,
            CrisisPhase.CONTAINMENT  # Schnelle Eindämmung möglich
        ],
        CrisisPhase.ESCALATION_CRISIS: [
            CrisisPhase.CONTAINMENT,
            # Kann nicht zurück zu früheren Phasen
        ],
        CrisisPhase.CONTAINMENT: [
            CrisisPhase.RECOVERY,
            CrisisPhase.ESCALATION_CRISIS  # Re-Eskalation möglich
        ],
        CrisisPhase.RECOVERY: [
            CrisisPhase.NORMAL_OPERATION,
            # Endphase - kann nur zu Normalbetrieb zurück
        ]
    }
    
    @classmethod
    def can_transition(
        cls,
        from_phase: CrisisPhase,
        to_phase: CrisisPhase
    ) -> bool:
        """
        Prüft, ob ein Übergang von einer Phase zur anderen erlaubt ist.
        
        Args:
            from_phase: Aktuelle Phase
            to_phase: Gewünschte Zielphase
        
        Returns:
            True, wenn Übergang erlaubt ist
        """
        allowed = cls.ALLOWED_TRANSITIONS.get(from_phase, [])
        return to_phase in allowed
    
    @classmethod
    def get_next_phases(cls, current_phase: CrisisPhase) -> List[CrisisPhase]:
        """
        Gibt alle möglichen nächsten Phasen zurück.
        
        Args:
            current_phase: Aktuelle Phase
        
        Returns:
            Liste der möglichen nächsten Phasen
        """
        return cls.ALLOWED_TRANSITIONS.get(current_phase, [])
    
    @classmethod
    def suggest_next_phase(
        cls,
        current_phase: CrisisPhase,
        inject_count: int,
        severity: str = "medium"
    ) -> CrisisPhase:
        """
        Schlägt die nächste logische Phase vor basierend auf Kontext.
        
        Args:
            current_phase: Aktuelle Phase
            inject_count: Anzahl bereits generierter Injects
            severity: Schweregrad des aktuellen Vorfalls
        
        Returns:
            Vorgeschlagene nächste Phase
        """
        next_options = cls.get_next_phases(current_phase)
        
        if not next_options:
            return current_phase  # Keine Übergänge möglich
        
        # Heuristik: Basierend auf Phase und Kontext
        if current_phase == CrisisPhase.NORMAL_OPERATION:
            if inject_count == 0:
                return CrisisPhase.SUSPICIOUS_ACTIVITY
            else:
                return CrisisPhase.INITIAL_INCIDENT
        
        elif current_phase == CrisisPhase.SUSPICIOUS_ACTIVITY:
            if severity in ["high", "critical"]:
                return CrisisPhase.INITIAL_INCIDENT
            else:
                return CrisisPhase.NORMAL_OPERATION  # False Positive
        
        elif current_phase == CrisisPhase.INITIAL_INCIDENT:
            if severity == "critical" or inject_count > 3:
                return CrisisPhase.ESCALATION_CRISIS
            else:
                return CrisisPhase.CONTAINMENT
        
        elif current_phase == CrisisPhase.ESCALATION_CRISIS:
            return CrisisPhase.CONTAINMENT
        
        elif current_phase == CrisisPhase.CONTAINMENT:
            if inject_count > 5:
                return CrisisPhase.RECOVERY
            else:
                return CrisisPhase.ESCALATION_CRISIS  # Re-Eskalation möglich
        
        elif current_phase == CrisisPhase.RECOVERY:
            return CrisisPhase.NORMAL_OPERATION
        
        # Fallback: Erste verfügbare Option
        return next_options[0]


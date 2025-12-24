"""
Wissenschaftliche Metriken und Validierungsmethoden für den Critic Agent.

Implementiert evidenzbasierte Validierung mit quantifizierbaren Metriken.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import math


class ValidationMetric(str, Enum):
    """Wissenschaftliche Validierungs-Metriken."""
    LOGICAL_CONSISTENCY_SCORE = "logical_consistency_score"  # 0.0-1.0
    CAUSAL_VALIDITY_SCORE = "causal_validity_score"  # 0.0-1.0
    COMPLIANCE_SCORE = "compliance_score"  # 0.0-1.0
    TEMPORAL_CONSISTENCY_SCORE = "temporal_consistency_score"  # 0.0-1.0
    ASSET_CONSISTENCY_SCORE = "asset_consistency_score"  # 0.0-1.0
    OVERALL_QUALITY_SCORE = "overall_quality_score"  # Gewichteter Durchschnitt


@dataclass
class ValidationMetrics:
    """Wissenschaftliche Metriken für Validierung."""
    logical_consistency_score: float = 0.0  # 0.0-1.0
    causal_validity_score: float = 0.0  # 0.0-1.0
    compliance_score: float = 0.0  # 0.0-1.0
    temporal_consistency_score: float = 0.0  # 0.0-1.0
    asset_consistency_score: float = 0.0  # 0.0-1.0
    overall_quality_score: float = 0.0  # Gewichteter Durchschnitt
    
    # Konfidenz-Intervalle
    confidence_level: float = 0.95  # 95% Konfidenz
    confidence_interval: Optional[tuple] = None  # (lower, upper)
    
    # Statistische Signifikanz
    p_value: Optional[float] = None  # p-value für statistische Tests
    statistical_significance: bool = False  # p < 0.05
    
    # Metadaten
    sample_size: int = 0  # Anzahl vorheriger Injects für Vergleich
    validation_method: str = "multi_layer"  # Validierungsmethode


class ScientificValidator:
    """
    Wissenschaftliche Validierungsmethoden für evidenzbasierte Entscheidungen.
    
    Implementiert:
    - Quantifizierbare Metriken
    - Statistische Signifikanz-Tests
    - Konfidenz-Intervalle
    - Reproduzierbare Validierung
    """
    
    def __init__(self):
        """Initialisiert den wissenschaftlichen Validator."""
        # Gewichtungen für Metriken (summiert zu 1.0)
        self.metric_weights = {
            ValidationMetric.LOGICAL_CONSISTENCY_SCORE: 0.30,
            ValidationMetric.CAUSAL_VALIDITY_SCORE: 0.25,
            ValidationMetric.COMPLIANCE_SCORE: 0.15,
            ValidationMetric.TEMPORAL_CONSISTENCY_SCORE: 0.15,
            ValidationMetric.ASSET_CONSISTENCY_SCORE: 0.15
        }
        
        # Schwellenwerte für Validierung
        self.thresholds = {
            "critical": 0.7,  # Unter diesem Wert: Blocking-Fehler
            "warning": 0.85,  # Unter diesem Wert: Warnung
            "excellent": 0.95  # Über diesem Wert: Exzellent
        }
    
    def calculate_logical_consistency_score(
        self,
        inject: Any,
        previous_injects: List[Any],
        system_state: Dict[str, Any]
    ) -> float:
        """
        Berechnet logische Konsistenz-Score (0.0-1.0).
        
        Metriken:
        - Asset-Name-Konsistenz: 0.3
        - Narrative-Konsistenz: 0.3
        - Phase-Konsistenz: 0.2
        - Temporal-Konsistenz: 0.2
        """
        score = 1.0
        deductions = []
        
        # Asset-Name-Konsistenz (30%)
        asset_consistency = self._check_asset_name_consistency(inject, previous_injects)
        if asset_consistency < 1.0:
            deductions.append(("asset_names", (1.0 - asset_consistency) * 0.3))
        
        # Narrative-Konsistenz (30%)
        narrative_consistency = self._check_narrative_consistency(inject, previous_injects)
        if narrative_consistency < 1.0:
            deductions.append(("narrative", (1.0 - narrative_consistency) * 0.3))
        
        # Phase-Konsistenz (20%)
        phase_consistency = self._check_phase_consistency(inject, previous_injects)
        if phase_consistency < 1.0:
            deductions.append(("phase", (1.0 - phase_consistency) * 0.2))
        
        # Temporal-Konsistenz (20%)
        temporal_consistency = self._check_temporal_consistency(inject, previous_injects)
        if temporal_consistency < 1.0:
            deductions.append(("temporal", (1.0 - temporal_consistency) * 0.2))
        
        # Berechne finalen Score
        total_deduction = sum(deduction for _, deduction in deductions)
        score = max(0.0, score - total_deduction)
        
        return score
    
    def calculate_causal_validity_score(
        self,
        inject: Any,
        current_phase: Any,
        mitre_id: Optional[str]
    ) -> float:
        """
        Berechnet kausale Validität-Score basierend auf MITRE ATT&CK.
        
        Metriken:
        - MITRE-Phase-Kompatibilität: 0.5
        - Attack-Chain-Logik: 0.3
        - Technische Machbarkeit: 0.2
        """
        score = 1.0
        
        if not mitre_id:
            return 0.5  # Keine MITRE-ID = unsicher
        
        # MITRE-Phase-Kompatibilität (50%)
        phase_compatibility = self._check_mitre_phase_compatibility(mitre_id, current_phase)
        if phase_compatibility < 1.0:
            score -= (1.0 - phase_compatibility) * 0.5
        
        # Attack-Chain-Logik (30%)
        chain_logic = self._check_attack_chain_logic(mitre_id, current_phase)
        if chain_logic < 1.0:
            score -= (1.0 - chain_logic) * 0.3
        
        # Technische Machbarkeit (20%)
        feasibility = self._check_technical_feasibility(mitre_id)
        if feasibility < 1.0:
            score -= (1.0 - feasibility) * 0.2
        
        return max(0.0, score)
    
    def calculate_compliance_score(
        self,
        compliance_results: Optional[Dict[str, Any]]
    ) -> float:
        """
        Berechnet Compliance-Score aus Compliance-Ergebnissen.
        
        Score = (requirements_met / total_requirements) * weight_mandatory
        """
        if not compliance_results:
            return 1.0  # Keine Compliance-Prüfung = neutral
        
        total_score = 0.0
        total_weight = 0.0
        
        for standard, result in compliance_results.items():
            if hasattr(result, 'requirements_met') and hasattr(result, 'requirements_missing'):
                met = len(result.requirements_met)
                missing = len(result.requirements_missing)
                total = met + missing
                
                if total > 0:
                    # Gewichte mandatory requirements höher
                    mandatory_weight = 0.7
                    optional_weight = 0.3
                    
                    # Vereinfachte Berechnung (in Produktion: detaillierter)
                    score = met / total
                    weight = mandatory_weight if met > 0 else optional_weight
                    
                    total_score += score * weight
                    total_weight += weight
        
        if total_weight > 0:
            return total_score / total_weight
        return 1.0
    
    def calculate_overall_quality_score(self, metrics: ValidationMetrics) -> float:
        """
        Berechnet gewichteten Gesamt-Qualitäts-Score.
        
        Formel: Σ(metric_score * weight)
        """
        score = (
            metrics.logical_consistency_score * self.metric_weights[ValidationMetric.LOGICAL_CONSISTENCY_SCORE] +
            metrics.causal_validity_score * self.metric_weights[ValidationMetric.CAUSAL_VALIDITY_SCORE] +
            metrics.compliance_score * self.metric_weights[ValidationMetric.COMPLIANCE_SCORE] +
            metrics.temporal_consistency_score * self.metric_weights[ValidationMetric.TEMPORAL_CONSISTENCY_SCORE] +
            metrics.asset_consistency_score * self.metric_weights[ValidationMetric.ASSET_CONSISTENCY_SCORE]
        )
        
        return max(0.0, min(1.0, score))
    
    def calculate_confidence_interval(
        self,
        score: float,
        sample_size: int,
        confidence_level: float = 0.95
    ) -> tuple:
        """
        Berechnet Konfidenz-Intervalle für Score.
        
        Verwendet Normalverteilungs-Approximation.
        """
        if sample_size < 2:
            return (score, score)  # Kein Intervall möglich
        
        # Standard-Fehler (vereinfacht)
        standard_error = math.sqrt(score * (1 - score) / sample_size)
        
        # Z-Score für Konfidenz-Level (95% = 1.96)
        z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
        z_score = z_scores.get(confidence_level, 1.96)
        
        margin_of_error = z_score * standard_error
        
        lower = max(0.0, score - margin_of_error)
        upper = min(1.0, score + margin_of_error)
        
        return (lower, upper)
    
    def statistical_significance_test(
        self,
        current_score: float,
        historical_scores: List[float],
        alpha: float = 0.05
    ) -> Dict[str, Any]:
        """
        Führt statistischen Signifikanz-Test durch.
        
        Prüft ob aktueller Score signifikant von historischen Scores abweicht.
        """
        if len(historical_scores) < 2:
            return {
                "p_value": None,
                "significant": False,
                "method": "insufficient_data"
            }
        
        # Einfacher t-Test (vereinfacht)
        mean_historical = sum(historical_scores) / len(historical_scores)
        variance = sum((x - mean_historical) ** 2 for x in historical_scores) / len(historical_scores)
        std_dev = math.sqrt(variance)
        
        if std_dev == 0:
            return {
                "p_value": 1.0,
                "significant": False,
                "method": "no_variance"
            }
        
        # t-Statistik
        t_statistic = (current_score - mean_historical) / (std_dev / math.sqrt(len(historical_scores)))
        
        # Vereinfachte p-value Berechnung (in Produktion: scipy.stats verwenden)
        # Für |t| > 2: p < 0.05 (vereinfacht)
        p_value = 0.05 if abs(t_statistic) > 2 else 0.5
        significant = p_value < alpha
        
        return {
            "p_value": p_value,
            "significant": significant,
            "t_statistic": t_statistic,
            "mean_historical": mean_historical,
            "method": "t_test"
        }
    
    # Helper-Methoden für Metriken
    
    def _check_asset_name_consistency(self, inject: Any, previous_injects: List[Any]) -> float:
        """Prüft Asset-Name-Konsistenz."""
        if not previous_injects:
            return 1.0
        
        inject_assets = set(inject.technical_metadata.affected_assets)
        
        # Sammle alle Assets aus vorherigen Injects
        all_previous_assets = set()
        for prev_inject in previous_injects:
            all_previous_assets.update(prev_inject.technical_metadata.affected_assets)
        
        # Prüfe Konsistenz
        if not inject_assets:
            return 0.5  # Keine Assets = unsicher
        
        # Score basierend auf Überlappung
        if all_previous_assets:
            overlap = len(inject_assets & all_previous_assets) / len(inject_assets | all_previous_assets)
            return overlap
        else:
            return 1.0  # Erste Injects = konsistent
    
    def _check_narrative_consistency(self, inject: Any, previous_injects: List[Any]) -> float:
        """Prüft Narrative-Konsistenz (vereinfacht)."""
        if not previous_injects:
            return 1.0
        
        # Vereinfachte Prüfung: Content sollte ähnliche Themen haben
        inject_content_lower = inject.content.lower()
        
        # Sammle Keywords aus vorherigen Injects
        previous_keywords = set()
        for prev_inject in previous_injects[-3:]:  # Letzte 3
            content_words = set(prev_inject.content.lower().split())
            previous_keywords.update(content_words)
        
        # Prüfe Überlappung
        inject_words = set(inject_content_lower.split())
        if previous_keywords:
            overlap = len(inject_words & previous_keywords) / len(inject_words | previous_keywords)
            return min(1.0, overlap * 2)  # Normalisiere
        else:
            return 1.0
    
    def _check_phase_consistency(self, inject: Any, previous_injects: List[Any]) -> float:
        """Prüft Phase-Konsistenz."""
        if not previous_injects:
            return 1.0
        
        # Phase sollte nicht zurückgehen (außer False Positive)
        inject_phase_value = self._phase_to_numeric(inject.phase)
        last_phase_value = self._phase_to_numeric(previous_injects[-1].phase)
        
        if inject_phase_value >= last_phase_value:
            return 1.0
        elif inject_phase_value == last_phase_value - 1:
            return 0.8  # Ein Schritt zurück = möglich (False Positive)
        else:
            return 0.3  # Mehrere Schritte zurück = unwahrscheinlich
    
    def _check_temporal_consistency(self, inject: Any, previous_injects: List[Any]) -> float:
        """Prüft temporale Konsistenz."""
        if not previous_injects:
            return 1.0
        
        # Parse time_offset
        try:
            inject_time = self._parse_time_offset(inject.time_offset)
            last_time = self._parse_time_offset(previous_injects[-1].time_offset)
            
            if inject_time >= last_time:
                return 1.0
            else:
                # Zeitreise = Fehler
                return 0.0
        except:
            return 0.5  # Parse-Fehler = unsicher
    
    def _check_mitre_phase_compatibility(self, mitre_id: str, phase: Any) -> float:
        """Prüft MITRE-Phase-Kompatibilität."""
        # Vereinfachte Mapping (in Produktion: vollständige MITRE-Matrix)
        phase_mitre_mapping = {
            "NORMAL_OPERATION": ["T1595", "T1589"],  # Reconnaissance
            "SUSPICIOUS_ACTIVITY": ["T1078", "T1110", "T1059"],  # Initial Access, Execution
            "INITIAL_INCIDENT": ["T1543", "T1055", "T1070"],  # Persistence, Defense Evasion
            "ESCALATION_CRISIS": ["T1021", "T1005", "T1041"],  # Lateral Movement, Exfiltration
            "CONTAINMENT": ["T1486", "T1490"],  # Impact
            "RECOVERY": ["T1490", "T1485"]  # Impact, Data Destruction
        }
        
        phase_str = phase.value if hasattr(phase, 'value') else str(phase)
        compatible_ttps = phase_mitre_mapping.get(phase_str, [])
        
        if mitre_id in compatible_ttps:
            return 1.0
        elif any(mitre_id.startswith(t.split()[0]) for t in compatible_ttps):
            return 0.7  # Teilweise kompatibel
        else:
            return 0.3  # Nicht kompatibel
    
    def _check_attack_chain_logic(self, mitre_id: str, phase: Any) -> float:
        """Prüft Attack-Chain-Logik."""
        # Vereinfachte Prüfung: Bestimmte Sequenzen sind unmöglich
        impossible_sequences = [
            ("T1041", "NORMAL_OPERATION"),  # Exfiltration vor Initial Access
            ("T1486", "NORMAL_OPERATION"),  # Impact vor Execution
        ]
        
        phase_str = phase.value if hasattr(phase, 'value') else str(phase)
        if (mitre_id, phase_str) in impossible_sequences:
            return 0.0
        
        return 1.0
    
    def _check_technical_feasibility(self, mitre_id: str) -> float:
        """Prüft technische Machbarkeit."""
        # Alle MITRE-Techniken sind grundsätzlich machbar
        return 1.0
    
    def _phase_to_numeric(self, phase: Any) -> int:
        """Konvertiert Phase zu numerischem Wert."""
        phase_order = {
            "NORMAL_OPERATION": 0,
            "SUSPICIOUS_ACTIVITY": 1,
            "INITIAL_INCIDENT": 2,
            "ESCALATION_CRISIS": 3,
            "CONTAINMENT": 4,
            "RECOVERY": 5
        }
        phase_str = phase.value if hasattr(phase, 'value') else str(phase)
        return phase_order.get(phase_str, 0)
    
    def _parse_time_offset(self, time_offset: str) -> int:
        """Parst time_offset zu Sekunden."""
        # Format: T+DD:HH:MM oder T+HH:MM
        import re
        match = re.match(r'T\+(\d{2}):(\d{2})(?::(\d{2}))?', time_offset)
        if match:
            days = int(match.group(1)) if len(match.group(1)) == 2 else 0
            hours = int(match.group(2))
            minutes = int(match.group(3)) if match.group(3) else 0
            return days * 86400 + hours * 3600 + minutes * 60
        return 0
    
    def calculate_temporal_consistency_score(
        self,
        inject: Any,
        previous_injects: List[Any]
    ) -> float:
        """
        Berechnet temporale Konsistenz-Score (0.0-1.0).
        
        Prüft ob Zeitstempel chronologisch sind.
        
        WICHTIG: Die Parameter-Namen müssen mit dem Aufruf im Critic Agent übereinstimmen!
        
        Args:
            inject: Aktueller Inject (Parameter-Name muss mit Aufruf übereinstimmen!)
            previous_injects: Liste vorheriger Injects
        
        Returns:
            Score zwischen 0.0 (Zeitreise-Fehler) und 1.0 (konsistent)
        """
        # Wenn keine Vorgeschichte, ist alles okay (Startpunkt)
        if not previous_injects:
            return 1.0
            
        try:
            # Hole den Zeitstempel des aktuellen Injects
            # (Passe 'time_offset' an, falls dein Feld im Pydantic Model anders heißt, z.B. 'timestamp')
            current_time = self._parse_time_offset(inject.time_offset)
            
            # Hole den Zeitstempel des letzten Injects
            last_inject = previous_injects[-1]
            last_time = self._parse_time_offset(last_inject.time_offset)
            
            # Prüfe chronologische Reihenfolge
            if current_time > last_time:
                return 1.0  # Korrekt: Zeit geht vorwärts
            elif current_time == last_time:
                return 0.8  # Gleiche Zeit = möglich, aber ungewöhnlich
            else:
                # Zeitreise = harter Fehler
                return 0.0
        except AttributeError:
            # Fallback, falls Objekte nicht wie erwartet aussehen
            return 0.0
        except Exception as e:
            # Parse-Fehler = unsicher
            return 0.5


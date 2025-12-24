"""
Tests für Critic Metrics Calculator.

Testet wissenschaftliche Metriken für Inject-Validierung.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock
import logging

# Füge Projekt-Root zum Python-Path hinzu
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

logger = logging.getLogger("tests.test_critic_metrics")


class TestCriticMetrics:
    """Test-Klasse für Critic Metrics."""
    
    def test_metrics_calculator_import(self):
        """Testet ob Metrics Calculator importierbar ist."""
        logger.info("Teste Critic Metrics Calculator Import")
        try:
            from agents.critic_metrics import (
                CriticMetricsCalculator,
                ValidationMetric,
                ValidationMetrics
            )
            logger.info("✓ Critic Metrics Calculator erfolgreich importiert")
        except ImportError as e:
            logger.error(f"✗ Critic Metrics Calculator nicht verfügbar: {e}")
            pytest.skip("Critic Metrics Calculator nicht verfügbar")
    
    def test_metrics_calculator_initialization(self):
        """Testet Initialisierung des Metrics Calculators."""
        logger.info("Teste Metrics Calculator Initialisierung")
        try:
            from agents.critic_metrics import CriticMetricsCalculator
            
            calculator = CriticMetricsCalculator()
            assert calculator is not None
            assert hasattr(calculator, 'metric_weights')
            assert hasattr(calculator, 'thresholds')
            logger.info("✓ Metrics Calculator erfolgreich initialisiert")
            
        except ImportError:
            pytest.skip("Critic Metrics Calculator nicht verfügbar")
    
    def test_calculate_metrics(self):
        """Testet Metriken-Berechnung."""
        logger.info("Teste Metriken-Berechnung")
        try:
            from agents.critic_metrics import CriticMetricsCalculator
            
            calculator = CriticMetricsCalculator()
            
            # Mock Compliance Results
            compliance_results = {
                "DORA": Mock(is_compliant=True, requirements_met=["Req1"], requirements_missing=[])
            }
            
            metrics = calculator.calculate_metrics(
                pydantic_valid=True,
                fsm_valid=True,
                state_valid=True,
                temporal_valid=True,
                llm_logical_consistency=True,
                llm_causal_validity=True,
                compliance_results=compliance_results,
                inject_count=1
            )
            
            assert metrics.logical_consistency_score >= 0.0
            assert metrics.logical_consistency_score <= 1.0
            assert metrics.causal_validity_score >= 0.0
            assert metrics.causal_validity_score <= 1.0
            assert metrics.compliance_score >= 0.0
            assert metrics.compliance_score <= 1.0
            assert metrics.overall_quality_score >= 0.0
            assert metrics.overall_quality_score <= 1.0
            
            logger.info(f"✓ Metriken berechnet:")
            logger.info(f"  Logical Consistency: {metrics.logical_consistency_score:.2f}")
            logger.info(f"  Causal Validity: {metrics.causal_validity_score:.2f}")
            logger.info(f"  Compliance: {metrics.compliance_score:.2f}")
            logger.info(f"  Overall Quality: {metrics.overall_quality_score:.2f}")
            
        except ImportError:
            pytest.skip("Critic Metrics Calculator nicht verfügbar")
    
    def test_confidence_interval_calculation(self):
        """Testet Confidence Interval Berechnung."""
        logger.info("Teste Confidence Interval Berechnung")
        try:
            from agents.critic_metrics import CriticMetricsCalculator
            
            calculator = CriticMetricsCalculator()
            ci = calculator.calculate_confidence_interval(score=0.85, sample_size=10)
            
            assert len(ci) == 2
            assert ci[0] < ci[1]
            assert 0.0 <= ci[0] <= 1.0
            assert 0.0 <= ci[1] <= 1.0
            
            logger.info(f"✓ Confidence Interval berechnet: [{ci[0]:.3f}, {ci[1]:.3f}]")
            
        except ImportError:
            pytest.skip("Critic Metrics Calculator nicht verfügbar")
    
    def test_statistical_significance_test(self):
        """Testet statistische Signifikanz-Tests."""
        logger.info("Teste statistische Signifikanz-Tests")
        try:
            from agents.critic_metrics import CriticMetricsCalculator
            
            calculator = CriticMetricsCalculator()
            
            # Füge historische Scores hinzu
            calculator.historical_scores = [0.80, 0.82, 0.85, 0.83, 0.84]
            
            result = calculator.statistical_significance_test(
                current_score=0.90,
                historical_scores=calculator.historical_scores
            )
            
            assert "p_value" in result
            assert "is_significant" in result
            assert 0.0 <= result["p_value"] <= 1.0
            assert isinstance(result["is_significant"], bool)
            
            logger.info(f"✓ Statistische Signifikanz geprüft:")
            logger.info(f"  p-value: {result['p_value']:.4f}")
            logger.info(f"  Significant: {result['is_significant']}")
            
        except ImportError:
            pytest.skip("Critic Metrics Calculator nicht verfügbar")
    
    def test_metrics_with_invalid_inputs(self):
        """Testet Metriken-Berechnung mit ungültigen Eingaben."""
        logger.info("Teste Metriken mit ungültigen Eingaben")
        try:
            from agents.critic_metrics import CriticMetricsCalculator
            
            calculator = CriticMetricsCalculator()
            
            # Test mit False-Werten
            metrics = calculator.calculate_metrics(
                pydantic_valid=False,
                fsm_valid=False,
                state_valid=False,
                temporal_valid=False,
                llm_logical_consistency=False,
                llm_causal_validity=False,
                compliance_results={},
                inject_count=1
            )
            
            # Scores sollten niedrig sein, aber noch im gültigen Bereich
            assert metrics.overall_quality_score >= 0.0
            assert metrics.overall_quality_score <= 1.0
            
            logger.info(f"✓ Metriken mit ungültigen Eingaben berechnet: {metrics.overall_quality_score:.2f}")
            
        except ImportError:
            pytest.skip("Critic Metrics Calculator nicht verfügbar")





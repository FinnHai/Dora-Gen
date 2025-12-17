"""
Evaluationsframework für Halluzinations-Erkennung.

Bietet:
- Edge-Case-Generierung für Halluzinations-Provokation
- Automatische quantitative Evaluierung
- Wissenschaftlich fundierte Metriken
"""

from evaluation.hallucination_test_cases import (
    HallucinationTestCase,
    HallucinationTestGenerator,
    HallucinationType
)
from evaluation.automatic_evaluator import (
    AutomaticEvaluator,
    EvaluationResult,
    EvaluationMetrics,
    run_evaluation
)

__all__ = [
    "HallucinationTestCase",
    "HallucinationTestGenerator",
    "HallucinationType",
    "AutomaticEvaluator",
    "EvaluationResult",
    "EvaluationMetrics",
    "run_evaluation"
]

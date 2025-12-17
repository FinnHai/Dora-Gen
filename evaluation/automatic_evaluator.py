"""
Automatisches Evaluationsframework für Halluzinations-Erkennung.

Führt quantitative Evaluierung durch:
- Testet Baseline RAG/LLM (ohne Validierung)
- Testet Agenten-System (mit Logik-Guard)
- Berechnet Metriken: Precision, Recall, F1, Accuracy
- Generiert wissenschaftlich fundierte Reports

Basierend auf:
- Information Retrieval Metriken (Precision/Recall)
- Classification Metriken (F1, Accuracy)
- Confusion Matrix Analyse
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import pandas as pd
from pathlib import Path

from evaluation.hallucination_test_cases import (
    HallucinationTestCase,
    HallucinationTestGenerator,
    HallucinationType
)
from agents.critic_agent import CriticAgent
from state_models import ValidationResult, CrisisPhase


@dataclass
class EvaluationResult:
    """Ergebnis einer einzelnen Evaluierung."""
    test_id: str
    hallucination_type: HallucinationType
    ground_truth: bool  # Ist es wirklich eine Halluzination?
    baseline_detected: bool  # Hat Baseline es erkannt?
    agent_detected: bool  # Hat Agenten-System es erkannt?
    baseline_validation_result: Optional[ValidationResult] = None
    agent_validation_result: Optional[ValidationResult] = None
    baseline_errors: List[str] = None
    agent_errors: List[str] = None


@dataclass
class EvaluationMetrics:
    """Aggregierte Metriken für die Evaluierung."""
    # Baseline Metriken
    baseline_true_positives: int = 0  # Halluzination erkannt (korrekt)
    baseline_false_positives: int = 0  # Nicht-Halluzination als Halluzination erkannt
    baseline_false_negatives: int = 0  # Halluzination nicht erkannt
    baseline_true_negatives: int = 0  # Nicht-Halluzination korrekt als nicht-Halluzination erkannt
    
    # Agenten-System Metriken
    agent_true_positives: int = 0
    agent_false_positives: int = 0
    agent_false_negatives: int = 0
    agent_true_negatives: int = 0
    
    # Berechnete Metriken
    baseline_precision: float = 0.0
    baseline_recall: float = 0.0
    baseline_f1: float = 0.0
    baseline_accuracy: float = 0.0
    
    agent_precision: float = 0.0
    agent_recall: float = 0.0
    agent_f1: float = 0.0
    agent_accuracy: float = 0.0
    
    # Verbesserung
    precision_improvement: float = 0.0
    recall_improvement: float = 0.0
    f1_improvement: float = 0.0
    accuracy_improvement: float = 0.0
    
    def calculate(self):
        """Berechnet alle Metriken."""
        # Baseline Metriken
        baseline_tp_fp = self.baseline_true_positives + self.baseline_false_positives
        baseline_tp_fn = self.baseline_true_positives + self.baseline_false_negatives
        baseline_total = (self.baseline_true_positives + self.baseline_false_positives + 
                         self.baseline_false_negatives + self.baseline_true_negatives)
        
        self.baseline_precision = (
            self.baseline_true_positives / baseline_tp_fp 
            if baseline_tp_fp > 0 else 0.0
        )
        self.baseline_recall = (
            self.baseline_true_positives / baseline_tp_fn 
            if baseline_tp_fn > 0 else 0.0
        )
        self.baseline_f1 = (
            2 * (self.baseline_precision * self.baseline_recall) / 
            (self.baseline_precision + self.baseline_recall)
            if (self.baseline_precision + self.baseline_recall) > 0 else 0.0
        )
        self.baseline_accuracy = (
            (self.baseline_true_positives + self.baseline_true_negatives) / baseline_total
            if baseline_total > 0 else 0.0
        )
        
        # Agenten-System Metriken
        agent_tp_fp = self.agent_true_positives + self.agent_false_positives
        agent_tp_fn = self.agent_true_positives + self.agent_false_negatives
        agent_total = (self.agent_true_positives + self.agent_false_positives + 
                      self.agent_false_negatives + self.agent_true_negatives)
        
        self.agent_precision = (
            self.agent_true_positives / agent_tp_fp 
            if agent_tp_fp > 0 else 0.0
        )
        self.agent_recall = (
            self.agent_true_positives / agent_tp_fn 
            if agent_tp_fn > 0 else 0.0
        )
        self.agent_f1 = (
            2 * (self.agent_precision * self.agent_recall) / 
            (self.agent_precision + self.agent_recall)
            if (self.agent_precision + self.agent_recall) > 0 else 0.0
        )
        self.agent_accuracy = (
            (self.agent_true_positives + self.agent_true_negatives) / agent_total
            if agent_total > 0 else 0.0
        )
        
        # Verbesserung
        self.precision_improvement = self.agent_precision - self.baseline_precision
        self.recall_improvement = self.agent_recall - self.baseline_recall
        self.f1_improvement = self.agent_f1 - self.baseline_f1
        self.accuracy_improvement = self.agent_accuracy - self.baseline_accuracy


class AutomaticEvaluator:
    """
    Automatisches Evaluationsframework.
    
    Führt quantitative Evaluierung durch:
    1. Lädt Edge-Case-Testfälle
    2. Testet Baseline (ohne Validierung)
    3. Testet Agenten-System (mit Critic Agent)
    4. Berechnet Metriken
    5. Generiert Reports
    """
    
    def __init__(self, critic_agent: Optional[CriticAgent] = None):
        """
        Initialisiert den Evaluator.
        
        Args:
            critic_agent: Critic Agent für Validierung (optional, wird erstellt wenn None)
        """
        self.test_generator = HallucinationTestGenerator()
        self.critic_agent = critic_agent or CriticAgent()
        self.results: List[EvaluationResult] = []
    
    def evaluate_baseline(self, test_case: HallucinationTestCase) -> Tuple[bool, List[str]]:
        """
        Evaluiert Baseline (ohne Validierung).
        
        Baseline akzeptiert immer alles (keine Validierung).
        Daher: Baseline erkennt Halluzinationen nie.
        
        Args:
            test_case: Testfall
            
        Returns:
            (detected, errors): Ob erkannt, Liste von Fehlern
        """
        # Baseline hat keine Validierung - akzeptiert alles
        # Daher: Baseline erkennt Halluzinationen nie
        return False, []
    
    def evaluate_agent_system(self, test_case: HallucinationTestCase) -> Tuple[bool, ValidationResult]:
        """
        Evaluiert Agenten-System (mit Critic Agent Validierung).
        
        Args:
            test_case: Testfall
            
        Returns:
            (detected, validation_result): Ob erkannt, Validierungsergebnis
        """
        # Validiere mit Critic Agent
        validation_result = self.critic_agent.validate_inject(
            inject=test_case.inject,
            previous_injects=test_case.previous_injects,
            current_phase=test_case.current_phase,
            system_state=test_case.system_state
        )
        
        # Halluzination erkannt, wenn Validierung fehlschlägt
        detected = not validation_result.is_valid
        
        return detected, validation_result
    
    def evaluate_test_case(self, test_case: HallucinationTestCase) -> EvaluationResult:
        """
        Evaluiert einen einzelnen Testfall.
        
        Args:
            test_case: Testfall
            
        Returns:
            Evaluationsergebnis
        """
        # Baseline Evaluierung
        baseline_detected, baseline_errors = self.evaluate_baseline(test_case)
        
        # Agenten-System Evaluierung
        agent_detected, agent_validation_result = self.evaluate_agent_system(test_case)
        
        # Erstelle Ergebnis
        result = EvaluationResult(
            test_id=test_case.test_id,
            hallucination_type=test_case.hallucination_type,
            ground_truth=test_case.ground_truth,
            baseline_detected=baseline_detected,
            agent_detected=agent_detected,
            agent_validation_result=agent_validation_result,
            baseline_errors=baseline_errors,
            agent_errors=agent_validation_result.errors if agent_validation_result else []
        )
        
        return result
    
    def evaluate_all(self, test_cases: Optional[List[HallucinationTestCase]] = None) -> List[EvaluationResult]:
        """
        Evaluiert alle Testfälle.
        
        Args:
            test_cases: Liste von Testfällen (optional, verwendet alle wenn None)
            
        Returns:
            Liste von Evaluationsergebnissen
        """
        if test_cases is None:
            test_cases = self.test_generator.generate_all_test_cases()
        
        results = []
        for test_case in test_cases:
            result = self.evaluate_test_case(test_case)
            results.append(result)
        
        self.results = results
        return results
    
    def calculate_metrics(self, results: Optional[List[EvaluationResult]] = None) -> EvaluationMetrics:
        """
        Berechnet Metriken aus Evaluationsergebnissen.
        
        Args:
            results: Liste von Ergebnissen (optional, verwendet self.results wenn None)
            
        Returns:
            Berechnete Metriken
        """
        if results is None:
            results = self.results
        
        metrics = EvaluationMetrics()
        
        for result in results:
            ground_truth = result.ground_truth
            baseline_detected = result.baseline_detected
            agent_detected = result.agent_detected
            
            # Baseline Confusion Matrix
            if ground_truth and baseline_detected:
                metrics.baseline_true_positives += 1
            elif ground_truth and not baseline_detected:
                metrics.baseline_false_negatives += 1
            elif not ground_truth and baseline_detected:
                metrics.baseline_false_positives += 1
            else:
                metrics.baseline_true_negatives += 1
            
            # Agenten-System Confusion Matrix
            if ground_truth and agent_detected:
                metrics.agent_true_positives += 1
            elif ground_truth and not agent_detected:
                metrics.agent_false_negatives += 1
            elif not ground_truth and agent_detected:
                metrics.agent_false_positives += 1
            else:
                metrics.agent_true_negatives += 1
        
        # Berechne Metriken
        metrics.calculate()
        
        return metrics
    
    def generate_report(self, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Generiert einen detaillierten Evaluationsreport.
        
        Args:
            output_path: Pfad zum Speichern des Reports (optional)
            
        Returns:
            Report als Dictionary
        """
        metrics = self.calculate_metrics()
        
        # Gruppiere nach Halluzinationstyp
        by_type = {}
        for result in self.results:
            type_str = result.hallucination_type.value
            if type_str not in by_type:
                by_type[type_str] = []
            by_type[type_str].append(result)
        
        # Berechne Metriken pro Typ
        type_metrics = {}
        for type_str, type_results in by_type.items():
            type_metrics[type_str] = self.calculate_metrics(type_results)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_test_cases": len(self.results),
            "overall_metrics": {
                "baseline": {
                    "precision": metrics.baseline_precision,
                    "recall": metrics.baseline_recall,
                    "f1": metrics.baseline_f1,
                    "accuracy": metrics.baseline_accuracy,
                    "true_positives": metrics.baseline_true_positives,
                    "false_positives": metrics.baseline_false_positives,
                    "false_negatives": metrics.baseline_false_negatives,
                    "true_negatives": metrics.baseline_true_negatives
                },
                "agent_system": {
                    "precision": metrics.agent_precision,
                    "recall": metrics.agent_recall,
                    "f1": metrics.agent_f1,
                    "accuracy": metrics.agent_accuracy,
                    "true_positives": metrics.agent_true_positives,
                    "false_positives": metrics.agent_false_positives,
                    "false_negatives": metrics.agent_false_negatives,
                    "true_negatives": metrics.agent_true_negatives
                },
                "improvement": {
                    "precision": metrics.precision_improvement,
                    "recall": metrics.recall_improvement,
                    "f1": metrics.f1_improvement,
                    "accuracy": metrics.accuracy_improvement
                }
            },
            "metrics_by_type": {
                type_str: {
                    "baseline": {
                        "precision": m.baseline_precision,
                        "recall": m.baseline_recall,
                        "f1": m.baseline_f1,
                        "accuracy": m.baseline_accuracy
                    },
                    "agent_system": {
                        "precision": m.agent_precision,
                        "recall": m.agent_recall,
                        "f1": m.agent_f1,
                        "accuracy": m.agent_accuracy
                    },
                    "improvement": {
                        "precision": m.precision_improvement,
                        "recall": m.recall_improvement,
                        "f1": m.f1_improvement,
                        "accuracy": m.accuracy_improvement
                    }
                }
                for type_str, m in type_metrics.items()
            },
            "detailed_results": [
                {
                    "test_id": r.test_id,
                    "hallucination_type": r.hallucination_type.value,
                    "ground_truth": r.ground_truth,
                    "baseline_detected": r.baseline_detected,
                    "agent_detected": r.agent_detected,
                    "baseline_correct": (r.ground_truth == r.baseline_detected),
                    "agent_correct": (r.ground_truth == r.agent_detected),
                    "agent_errors": r.agent_errors
                }
                for r in self.results
            ]
        }
        
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        
        return report
    
    def export_to_csv(self, output_path: Path):
        """
        Exportiert Ergebnisse als CSV.
        
        Args:
            output_path: Pfad zur CSV-Datei
        """
        data = []
        for result in self.results:
            data.append({
                "test_id": result.test_id,
                "hallucination_type": result.hallucination_type.value,
                "ground_truth": result.ground_truth,
                "baseline_detected": result.baseline_detected,
                "agent_detected": result.agent_detected,
                "baseline_correct": (result.ground_truth == result.baseline_detected),
                "agent_correct": (result.ground_truth == result.agent_detected),
                "baseline_errors": "; ".join(result.baseline_errors or []),
                "agent_errors": "; ".join(result.agent_errors or [])
            })
        
        df = pd.DataFrame(data)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False, encoding="utf-8")


def run_evaluation(output_dir: Path = Path("evaluation_results")):
    """
    Führt vollständige Evaluierung durch.
    
    Args:
        output_dir: Ausgabeverzeichnis für Reports
    """
    print("🚀 Starte automatische Evaluierung...")
    
    # Initialisiere Evaluator
    evaluator = AutomaticEvaluator()
    
    # Generiere und evaluiere alle Testfälle
    print("📋 Generiere Testfälle...")
    test_cases = evaluator.test_generator.generate_all_test_cases()
    print(f"   {len(test_cases)} Testfälle generiert")
    
    print("🔍 Führe Evaluierung durch...")
    results = evaluator.evaluate_all(test_cases)
    print(f"   {len(results)} Testfälle evaluiert")
    
    # Berechne Metriken
    print("📊 Berechne Metriken...")
    metrics = evaluator.calculate_metrics()
    
    print("\n=== ERGEBNISSE ===")
    print(f"Baseline Precision: {metrics.baseline_precision:.3f}")
    print(f"Baseline Recall: {metrics.baseline_recall:.3f}")
    print(f"Baseline F1: {metrics.baseline_f1:.3f}")
    print(f"Baseline Accuracy: {metrics.baseline_accuracy:.3f}")
    print()
    print(f"Agenten-System Precision: {metrics.agent_precision:.3f}")
    print(f"Agenten-System Recall: {metrics.agent_recall:.3f}")
    print(f"Agenten-System F1: {metrics.agent_f1:.3f}")
    print(f"Agenten-System Accuracy: {metrics.agent_accuracy:.3f}")
    print()
    print(f"Verbesserung Precision: {metrics.precision_improvement:+.3f}")
    print(f"Verbesserung Recall: {metrics.recall_improvement:+.3f}")
    print(f"Verbesserung F1: {metrics.f1_improvement:+.3f}")
    print(f"Verbesserung Accuracy: {metrics.accuracy_improvement:+.3f}")
    
    # Generiere Reports
    print("\n📄 Generiere Reports...")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = output_dir / f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    evaluator.generate_report(report_path)
    print(f"   Report gespeichert: {report_path}")
    
    csv_path = output_dir / f"evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    evaluator.export_to_csv(csv_path)
    print(f"   CSV gespeichert: {csv_path}")
    
    print("\n✅ Evaluierung abgeschlossen!")


if __name__ == "__main__":
    run_evaluation()

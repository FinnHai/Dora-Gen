#!/usr/bin/env python3
"""
Einfaches Skript zur Ausführung der automatischen Evaluierung.

Nutzung:
    python run_evaluation.py
    
Optionen:
    --output-dir: Ausgabeverzeichnis für Reports (Standard: evaluation_results)
    --test-types: Spezifische Halluzinationstypen testen (komma-separiert)
    --verbose: Detaillierte Ausgabe
"""

import argparse
from pathlib import Path
from evaluation.automatic_evaluator import AutomaticEvaluator, run_evaluation
from evaluation.hallucination_test_cases import HallucinationType


def main():
    parser = argparse.ArgumentParser(
        description="Führt automatische Evaluierung der Halluzinations-Erkennung durch."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="evaluation_results",
        help="Ausgabeverzeichnis für Reports (Standard: evaluation_results)"
    )
    parser.add_argument(
        "--test-types",
        type=str,
        help="Spezifische Halluzinationstypen testen (komma-separiert, z.B. FSM_VIOLATION,STATE_INCONSISTENCY)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Detaillierte Ausgabe"
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    
    print("=" * 60)
    print("Automatische Evaluierung: Halluzinations-Erkennung")
    print("=" * 60)
    print()
    
    # Initialisiere Evaluator
    evaluator = AutomaticEvaluator()
    
    # Generiere Testfälle
    if args.test_types:
        # Spezifische Typen
        type_strings = [t.strip() for t in args.test_types.split(",")]
        test_types = [HallucinationType(t) for t in type_strings]
        
        test_cases = []
        for test_type in test_types:
            cases = evaluator.test_generator.get_test_cases_by_type(test_type)
            test_cases.extend(cases)
            if args.verbose:
                print(f"   {len(cases)} Testfälle für {test_type.value}")
    else:
        # Alle Testfälle
        test_cases = evaluator.test_generator.generate_all_test_cases()
        if args.verbose:
            print(f"   {len(test_cases)} Testfälle generiert")
    
    print(f"\n📋 {len(test_cases)} Testfälle werden evaluiert...")
    
    # Führe Evaluierung durch
    results = evaluator.evaluate_all(test_cases)
    
    # Berechne Metriken
    metrics = evaluator.calculate_metrics()
    
    # Zeige Ergebnisse
    print("\n" + "=" * 60)
    print("ERGEBNISSE")
    print("=" * 60)
    print()
    
    print("Baseline RAG/LLM (ohne Validierung):")
    print(f"  Precision:  {metrics.baseline_precision:.3f}")
    print(f"  Recall:     {metrics.baseline_recall:.3f}")
    print(f"  F1-Score:  {metrics.baseline_f1:.3f}")
    print(f"  Accuracy:  {metrics.baseline_accuracy:.3f}")
    print()
    
    print("Agenten-System (mit Logik-Guard):")
    print(f"  Precision:  {metrics.agent_precision:.3f}")
    print(f"  Recall:     {metrics.agent_recall:.3f}")
    print(f"  F1-Score:  {metrics.agent_f1:.3f}")
    print(f"  Accuracy:  {metrics.agent_accuracy:.3f}")
    print()
    
    print("Verbesserung:")
    print(f"  Precision:  {metrics.precision_improvement:+.3f}")
    print(f"  Recall:     {metrics.recall_improvement:+.3f}")
    print(f"  F1-Score:  {metrics.f1_improvement:+.3f}")
    print(f"  Accuracy:  {metrics.accuracy_improvement:+.3f}")
    print()
    
    # Confusion Matrix
    print("Confusion Matrix:")
    print()
    print("Baseline:")
    print(f"  True Positives:  {metrics.baseline_true_positives}")
    print(f"  False Positives: {metrics.baseline_false_positives}")
    print(f"  False Negatives: {metrics.baseline_false_negatives}")
    print(f"  True Negatives:  {metrics.baseline_true_negatives}")
    print()
    print("Agenten-System:")
    print(f"  True Positives:  {metrics.agent_true_positives}")
    print(f"  False Positives: {metrics.agent_false_positives}")
    print(f"  False Negatives: {metrics.agent_false_negatives}")
    print(f"  True Negatives:  {metrics.agent_true_negatives}")
    print()
    
    # Generiere Reports
    print("📄 Generiere Reports...")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    report_path = output_dir / f"evaluation_report_{timestamp}.json"
    evaluator.generate_report(report_path)
    print(f"   ✅ Report: {report_path}")
    
    csv_path = output_dir / f"evaluation_results_{timestamp}.csv"
    evaluator.export_to_csv(csv_path)
    print(f"   ✅ CSV: {csv_path}")
    
    print()
    print("=" * 60)
    print("✅ Evaluierung abgeschlossen!")
    print("=" * 60)


if __name__ == "__main__":
    main()

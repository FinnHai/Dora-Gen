"""
Test-Skript für den interaktiven Workflow-Modus.

Testet die Szenario-Generierung im interaktiven Modus mit Debug-Informationen.
"""

from neo4j_client import Neo4jClient
from workflows.scenario_workflow import ScenarioWorkflow
from state_models import ScenarioType
import os
from dotenv import load_dotenv

load_dotenv()


def test_interactive_workflow():
    """Testet den Workflow im interaktiven Modus."""
    print("=" * 60)
    print("Test: Interaktiver LangGraph Workflow")
    print("=" * 60)
    print()
    
    # Prüfe Neo4j-Verbindung
    try:
        with Neo4jClient() as neo4j:
            print("✅ Neo4j verbunden")
            
            # Initialisiere Basis-Infrastruktur (falls noch nicht geschehen)
            entities = neo4j.get_current_state()
            if len(entities) < 3:
                print("📊 Initialisiere Basis-Infrastruktur...")
                neo4j.initialize_base_infrastructure()
            
            # Erstelle Workflow IM INTERAKTIVEN MODUS
            print("\n🔧 Erstelle Workflow (INTERAKTIVER MODUS)...")
            workflow = ScenarioWorkflow(
                neo4j_client=neo4j, 
                max_iterations=3,
                interactive_mode=True  # WICHTIG: Interaktiver Modus aktiviert
            )
            
            # Generiere Test-Szenario
            print("\n🚀 Starte Szenario-Generierung im interaktiven Modus...")
            print("   (Dies kann einige Minuten dauern, da LLM-Aufrufe gemacht werden)")
            print()
            
            result = workflow.generate_scenario(
                scenario_type=ScenarioType.RANSOMWARE_DOUBLE_EXTORTION
            )
            
            # Zeige Ergebnisse
            print("\n" + "=" * 60)
            print("📊 Ergebnisse:")
            print("=" * 60)
            print(f"   Szenario ID: {result.get('scenario_id')}")
            print(f"   Typ: {result.get('scenario_type').value}")
            print(f"   Finale Phase: {result.get('current_phase').value}")
            print(f"   Iteration: {result.get('iteration', 0)}")
            print(f"   Max Iterations: {result.get('max_iterations', 0)}")
            print(f"   Anzahl Injects: {len(result.get('injects', []))}")
            print(f"   Workflow Logs: {len(result.get('workflow_logs', []))}")
            print(f"   Agent Decisions: {len(result.get('agent_decisions', []))}")
            print(f"   Pending Decision: {result.get('pending_decision') is not None}")
            print()
            
            # Zeige Workflow-Logs (erste 10)
            logs = result.get('workflow_logs', [])
            if logs:
                print("📋 Workflow-Logs (erste 10):")
                print("-" * 60)
                for i, log in enumerate(logs[:10]):
                    node = log.get('node', 'Unknown')
                    iteration = log.get('iteration', 'N/A')
                    action = log.get('action', 'N/A')
                    print(f"  {i+1}. [{node}] Iteration {iteration}: {action}")
                if len(logs) > 10:
                    print(f"  ... und {len(logs) - 10} weitere")
                print()
            
            # Zeige Injects
            injects = result.get('injects', [])
            if injects:
                print("📋 Generierte Injects:")
                print("-" * 60)
                for inject in injects:
                    print(f"\n{inject.inject_id} ({inject.time_offset})")
                    print(f"  Phase: {inject.phase.value}")
                    print(f"  Content: {inject.content[:80]}...")
                    print(f"  MITRE: {inject.technical_metadata.mitre_id}")
                    print(f"  Assets: {', '.join(inject.technical_metadata.affected_assets)}")
            else:
                print("⚠️  KEINE INJECTS GENERIERT!")
                print()
                print("🔍 Debug-Informationen:")
                print(f"   Draft Inject vorhanden: {result.get('draft_inject') is not None}")
                if result.get('draft_inject'):
                    print(f"   Draft Inject ID: {result.get('draft_inject').inject_id}")
                print(f"   Validation Result vorhanden: {result.get('validation_result') is not None}")
                if result.get('validation_result'):
                    val = result.get('validation_result')
                    print(f"   Validation is_valid: {val.is_valid if hasattr(val, 'is_valid') else 'N/A'}")
            
            # Zeige Fehler/Warnungen
            errors = result.get('errors', [])
            warnings = result.get('warnings', [])
            
            if errors:
                print("\n❌ Fehler:")
                for error in errors:
                    print(f"   - {error}")
            
            if warnings:
                print("\n⚠️  Warnungen:")
                for warning in warnings:
                    print(f"   - {warning}")
            
            print("\n" + "=" * 60)
            print("✅ Test abgeschlossen!")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_interactive_workflow()


"""
Test-Skript für den LangGraph Workflow.

Testet die Szenario-Generierung mit einem einfachen Beispiel.
"""

from neo4j_client import Neo4jClient
from workflows.scenario_workflow import ScenarioWorkflow
from state_models import ScenarioType
import os
from dotenv import load_dotenv

load_dotenv()


def test_workflow():
    """Testet den Workflow mit einem einfachen Szenario."""
    print("=" * 60)
    print("Test: LangGraph Workflow")
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
            
            # Erstelle Workflow
            print("\n🔧 Erstelle Workflow...")
            workflow = ScenarioWorkflow(neo4j_client=neo4j, max_iterations=3)
            
            # Generiere Test-Szenario
            print("\n🚀 Starte Szenario-Generierung...")
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
            print(f"   Anzahl Injects: {len(result.get('injects', []))}")
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
    test_workflow()


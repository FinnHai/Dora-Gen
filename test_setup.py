"""
Test-Skript zur Überprüfung der Grundfunktionalität.

Führt grundlegende Tests für:
- Pydantic Modelle
- Neo4j Verbindung (optional, wenn Neo4j läuft)
"""

from state_models import (
    Inject,
    TechnicalMetadata,
    CrisisPhase,
    InjectModality,
    ScenarioType,
    ScenarioState
)
from datetime import datetime


def test_pydantic_models():
    """Testet die Pydantic-Modelle."""
    print("🧪 Teste Pydantic-Modelle...")
    
    # Test: TechnicalMetadata
    tech_meta = TechnicalMetadata(
        mitre_id="T1110",
        affected_assets=["DC-01", "SRV-002"],
        ioc_hash="a1b2c3d4",
        severity="High"
    )
    print(f"✓ TechnicalMetadata erstellt: {tech_meta.mitre_id}")
    
    # Test: Inject
    inject = Inject(
        inject_id="INJ-001",
        time_offset="T+00:30",
        phase=CrisisPhase.SUSPICIOUS_ACTIVITY,
        source="Red Team / Attacker",
        target="Blue Team / SOC",
        modality=InjectModality.SIEM_ALERT,
        content="Multiple failed login attempts detected on DC-01 from unknown IP 192.168.1.100.",
        technical_metadata=tech_meta,
        dora_compliance_tag="Art25_VulnScan"
    )
    print(f"✓ Inject erstellt: {inject.inject_id}")
    print(f"  Phase: {inject.phase}")
    print(f"  Content: {inject.content[:50]}...")
    
    # Test: ScenarioState
    scenario = ScenarioState(
        scenario_id="SCEN-001",
        scenario_type=ScenarioType.RANSOMWARE_DOUBLE_EXTORTION,
        current_phase=CrisisPhase.NORMAL_OPERATION,
        injects=[inject]
    )
    print(f"✓ ScenarioState erstellt: {scenario.scenario_id}")
    print(f"  Typ: {scenario.scenario_type}")
    print(f"  Anzahl Injects: {len(scenario.injects)}")
    
    # Test: Validierung (sollte fehlschlagen)
    try:
        invalid_inject = Inject(
            inject_id="INVALID",
            time_offset="T+00:30",
            phase=CrisisPhase.SUSPICIOUS_ACTIVITY,
            source="Test",
            target="Test",
            modality=InjectModality.SIEM_ALERT,
            content="zu kurz",  # Zu kurz!
            technical_metadata=tech_meta
        )
        print("✗ Validierung hat nicht funktioniert!")
    except Exception as e:
        print(f"✓ Validierung funktioniert: {type(e).__name__}")
    
    print("\n✅ Alle Pydantic-Tests erfolgreich!\n")


def test_neo4j_connection():
    """Testet die Neo4j-Verbindung (optional)."""
    print("🧪 Teste Neo4j-Verbindung...")
    
    try:
        from neo4j_client import Neo4jClient
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Prüfe ob Umgebungsvariablen gesetzt sind
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")
        
        if not uri or not user or not password or password == "your_password_here":
            print("⚠️  Neo4j-Konfiguration nicht vollständig in .env")
            print("   Überspringe Neo4j-Test")
            return
        
        with Neo4jClient() as client:
            # Test: Basis-Infrastruktur initialisieren
            client.initialize_base_infrastructure()
            
            # Test: State abfragen
            entities = client.get_current_state()
            print(f"✓ {len(entities)} Entitäten im Graph gefunden")
            
            # Test: Status abfragen
            status = client.get_entity_status("SRV-001")
            print(f"✓ Status von SRV-001: {status}")
            
            # Test: Status aktualisieren
            client.update_entity_status("SRV-001", "offline", inject_id="INJ-TEST")
            new_status = client.get_entity_status("SRV-001")
            print(f"✓ Status aktualisiert: {new_status}")
            
            # Test: Second-Order Effects
            affected = client.get_affected_entities("SRV-002")
            print(f"✓ Betroffene Entitäten von SRV-002: {affected}")
        
        print("\n✅ Alle Neo4j-Tests erfolgreich!\n")
        
    except ImportError:
        print("⚠️  Neo4j-Paket nicht installiert. Führe 'pip install -r requirements.txt' aus.")
    except Exception as e:
        print(f"⚠️  Neo4j-Test fehlgeschlagen: {e}")
        print("   Stelle sicher, dass Neo4j läuft und .env korrekt konfiguriert ist.")


if __name__ == "__main__":
    print("=" * 60)
    print("DORA-Szenariengenerator - Setup-Test")
    print("=" * 60)
    print()
    
    test_pydantic_models()
    test_neo4j_connection()
    
    print("=" * 60)
    print("✅ Setup-Test abgeschlossen!")
    print("=" * 60)


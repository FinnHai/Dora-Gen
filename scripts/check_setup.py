"""
Erweiterte Setup-Prüfung mit Neo4j-Initialisierung.

Prüft alle Komponenten und initialisiert Neo4j, falls konfiguriert.
"""

import os
from dotenv import load_dotenv
from state_models import Inject, TechnicalMetadata, CrisisPhase, InjectModality
from neo4j_client import Neo4jClient

load_dotenv()


def check_neo4j():
    """Prüft und initialisiert Neo4j."""
    print("🔍 Prüfe Neo4j-Konfiguration...")
    
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    
    if not uri or not user or not password or password == "your_password_here":
        print("⚠️  Neo4j nicht konfiguriert in .env")
        print("   Überspringe Neo4j-Test")
        return False
    
    print(f"   URI: {uri}")
    print(f"   User: {user}")
    print(f"   Password: {'*' * len(password)}")
    
    try:
        print("\n🔌 Verbinde zu Neo4j...")
        with Neo4jClient() as client:
            print("✅ Verbindung erfolgreich!")
            
            print("\n📊 Initialisiere Basis-Infrastruktur...")
            client.initialize_base_infrastructure()
            
            print("\n🔍 Teste Funktionalität...")
            entities = client.get_current_state()
            print(f"   ✓ {len(entities)} Entitäten gefunden")
            
            status = client.get_entity_status("SRV-001")
            print(f"   ✓ Status von SRV-001: {status}")
            
            # Test: Status Update
            client.update_entity_status("SRV-001", "online", inject_id="INJ-TEST")
            new_status = client.get_entity_status("SRV-001")
            print(f"   ✓ Status Update funktioniert: {new_status}")
            
            # Test: Second-Order Effects
            affected = client.get_affected_entities("SRV-002")
            print(f"   ✓ Second-Order Effects: {len(affected)} betroffene Entitäten")
            
            return True
            
    except Exception as e:
        print(f"❌ Neo4j-Fehler: {e}")
        print("\n💡 Mögliche Lösungen:")
        print("   1. Stelle sicher, dass Neo4j läuft:")
        print("      ./start_neo4j.sh")
        print("   2. Prüfe die .env Konfiguration")
        print("   3. Prüfe ob Docker läuft (docker info)")
        return False


def check_openai():
    """Prüft OpenAI Konfiguration."""
    print("\n🔍 Prüfe OpenAI-Konfiguration...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key or api_key == "your_openai_api_key_here":
        print("⚠️  OpenAI API Key nicht konfiguriert")
        print("   Wird für LLM-Funktionalität benötigt")
        return False
    
    print(f"   API Key: {'*' * 20}...{api_key[-4:] if len(api_key) > 4 else '****'}")
    print("✅ OpenAI konfiguriert")
    return True


def main():
    print("=" * 60)
    print("DORA-Szenariengenerator - Erweiterte Setup-Prüfung")
    print("=" * 60)
    print()
    
    # Prüfe Pydantic
    print("✅ Pydantic-Modelle: OK (bereits getestet)")
    
    # Prüfe Neo4j
    neo4j_ok = check_neo4j()
    
    # Prüfe OpenAI
    openai_ok = check_openai()
    
    print("\n" + "=" * 60)
    print("📊 Zusammenfassung:")
    print("=" * 60)
    print(f"   Pydantic-Modelle: ✅")
    print(f"   Neo4j:           {'✅' if neo4j_ok else '⚠️  Nicht konfiguriert/erreichbar'}")
    print(f"   OpenAI:           {'✅' if openai_ok else '⚠️  Nicht konfiguriert'}")
    print()
    
    if neo4j_ok and openai_ok:
        print("🎉 Alles bereit für die Entwicklung!")
    elif not neo4j_ok:
        print("💡 Tipp: Starte Neo4j mit: ./start_neo4j.sh")
    elif not openai_ok:
        print("💡 Tipp: Füge OPENAI_API_KEY in .env ein (für LLM-Funktionalität)")
    
    print("=" * 60)


if __name__ == "__main__":
    main()


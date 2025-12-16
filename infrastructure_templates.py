"""
Infrastructure Templates für Finanzinstitute.

Vordefinierte Infrastruktur-Modelle, die in Neo4j geladen werden können.
"""

from typing import List, Dict, Any, Optional
from state_models import KnowledgeGraphEntity


class InfrastructureTemplate:
    """Basis-Klasse für Infrastructure Templates."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def get_entities(self) -> List[Dict[str, Any]]:
        """Gibt Liste von Entitäten zurück."""
        raise NotImplementedError
    
    def get_relationships(self) -> List[Dict[str, Any]]:
        """Gibt Liste von Beziehungen zurück."""
        raise NotImplementedError


class StandardBankTemplate(InfrastructureTemplate):
    """Standard-Bank-Infrastruktur Template."""
    
    def __init__(self):
        super().__init__(
            name="Standard Bank Infrastructure",
            description="Standard IT-Infrastruktur für eine mittelgroße Bank mit Core Banking, Payment Processing und Security Systems"
        )
    
    def get_entities(self) -> List[Dict[str, Any]]:
        """Gibt Entitäten für Standard-Bank zurück."""
        return [
            # Core Banking System
            {"id": "SRV-CORE-01", "type": "Server", "name": "Core Banking Server 1", "status": "online", "criticality": "critical"},
            {"id": "SRV-CORE-02", "type": "Server", "name": "Core Banking Server 2 (Backup)", "status": "online", "criticality": "critical"},
            {"id": "APP-CORE", "type": "Application", "name": "Core Banking System", "status": "online", "criticality": "critical"},
            
            # Payment Processing
            {"id": "SRV-PAY-01", "type": "Server", "name": "Payment Processing Server", "status": "online", "criticality": "critical"},
            {"id": "APP-PAY", "type": "Application", "name": "Payment Processing System", "status": "online", "criticality": "critical"},
            {"id": "DB-PAY", "type": "Database", "name": "Payment Transaction Database", "status": "online", "criticality": "critical"},
            
            # Customer Systems
            {"id": "SRV-CUST-01", "type": "Server", "name": "Customer Portal Server", "status": "online", "criticality": "important"},
            {"id": "APP-CUST", "type": "Application", "name": "Customer Portal", "status": "online", "criticality": "important"},
            {"id": "DB-CUST", "type": "Database", "name": "Customer Database", "status": "online", "criticality": "critical"},
            
            # Security Infrastructure
            {"id": "SRV-SEC-01", "type": "Server", "name": "Security Operations Center (SOC) Server", "status": "online", "criticality": "important"},
            {"id": "APP-SIEM", "type": "Application", "name": "SIEM System", "status": "online", "criticality": "important"},
            {"id": "APP-FW", "type": "Application", "name": "Firewall Management", "status": "online", "criticality": "important"},
            
            # Network Infrastructure
            {"id": "NET-DMZ", "type": "Network", "name": "DMZ Network", "status": "online", "criticality": "important"},
            {"id": "NET-INT", "type": "Network", "name": "Internal Network", "status": "online", "criticality": "critical"},
            {"id": "NET-BACKUP", "type": "Network", "name": "Backup Network", "status": "online", "criticality": "standard"},
            
            # Backup Systems
            {"id": "SRV-BACKUP-01", "type": "Server", "name": "Backup Server 1", "status": "online", "criticality": "important"},
            {"id": "APP-BACKUP", "type": "Application", "name": "Backup Management System", "status": "online", "criticality": "important"},
            
            # Departments
            {"id": "DEPT-IT", "type": "Department", "name": "IT Operations", "status": "operational", "criticality": "standard"},
            {"id": "DEPT-SEC", "type": "Department", "name": "IT Security", "status": "operational", "criticality": "important"},
            {"id": "DEPT-PAY", "type": "Department", "name": "Payment Operations", "status": "operational", "criticality": "critical"},
        ]
    
    def get_relationships(self) -> List[Dict[str, Any]]:
        """Gibt Beziehungen für Standard-Bank zurück."""
        return [
            # Core Banking Dependencies
            {"source": "APP-CORE", "target": "SRV-CORE-01", "type": "RUNS_ON"},
            {"source": "APP-CORE", "target": "SRV-CORE-02", "type": "RUNS_ON"},
            
            # Payment Processing Dependencies
            {"source": "APP-PAY", "target": "SRV-PAY-01", "type": "RUNS_ON"},
            {"source": "APP-PAY", "target": "DB-PAY", "type": "USES"},
            {"source": "APP-PAY", "target": "APP-CORE", "type": "DEPENDS_ON"},
            
            # Customer Systems
            {"source": "APP-CUST", "target": "SRV-CUST-01", "type": "RUNS_ON"},
            {"source": "APP-CUST", "target": "DB-CUST", "type": "USES"},
            {"source": "APP-CUST", "target": "APP-CORE", "type": "DEPENDS_ON"},
            
            # Security Infrastructure
            {"source": "APP-SIEM", "target": "SRV-SEC-01", "type": "RUNS_ON"},
            {"source": "APP-SIEM", "target": "NET-INT", "type": "MONITORS"},
            {"source": "APP-SIEM", "target": "NET-DMZ", "type": "MONITORS"},
            {"source": "APP-FW", "target": "SRV-SEC-01", "type": "RUNS_ON"},
            
            # Network Connections
            {"source": "SRV-CUST-01", "target": "NET-DMZ", "type": "CONNECTS_TO"},
            {"source": "SRV-CORE-01", "target": "NET-INT", "type": "CONNECTS_TO"},
            {"source": "SRV-PAY-01", "target": "NET-INT", "type": "CONNECTS_TO"},
            
            # Backup Dependencies
            {"source": "APP-BACKUP", "target": "SRV-BACKUP-01", "type": "RUNS_ON"},
            {"source": "APP-BACKUP", "target": "DB-PAY", "type": "BACKS_UP"},
            {"source": "APP-BACKUP", "target": "DB-CUST", "type": "BACKS_UP"},
            {"source": "SRV-BACKUP-01", "target": "NET-BACKUP", "type": "CONNECTS_TO"},
            
            # Department Usage
            {"source": "DEPT-PAY", "target": "APP-PAY", "type": "USES"},
            {"source": "DEPT-IT", "target": "APP-CORE", "type": "MANAGES"},
            {"source": "DEPT-SEC", "target": "APP-SIEM", "type": "USES"},
        ]


class LargeBankTemplate(InfrastructureTemplate):
    """Große Bank-Infrastruktur mit mehreren Standorten."""
    
    def __init__(self):
        super().__init__(
            name="Large Bank Infrastructure",
            description="Erweiterte Infrastruktur für eine große Bank mit Multi-Site-Setup, High Availability und Disaster Recovery"
        )
    
    def get_entities(self) -> List[Dict[str, Any]]:
        """Gibt Entitäten für Large Bank zurück."""
        entities = StandardBankTemplate().get_entities()
        
        # Zusätzliche Entitäten für große Bank
        additional = [
            # Secondary Site
            {"id": "SRV-CORE-03", "type": "Server", "name": "Core Banking Server 3 (DR Site)", "status": "online", "criticality": "critical"},
            {"id": "SRV-PAY-02", "type": "Server", "name": "Payment Processing Server 2 (HA)", "status": "online", "criticality": "critical"},
            
            # Load Balancer
            {"id": "APP-LB", "type": "Application", "name": "Load Balancer", "status": "online", "criticality": "critical"},
            
            # Additional Security
            {"id": "APP-IDS", "type": "Application", "name": "Intrusion Detection System", "status": "online", "criticality": "important"},
            {"id": "APP-DLP", "type": "Application", "name": "Data Loss Prevention", "status": "online", "criticality": "important"},
            
            # Compliance Systems
            {"id": "APP-COMP", "type": "Application", "name": "Compliance Monitoring System", "status": "online", "criticality": "important"},
        ]
        
        return entities + additional
    
    def get_relationships(self) -> List[Dict[str, Any]]:
        """Gibt Beziehungen für Large Bank zurück."""
        relationships = StandardBankTemplate().get_relationships()
        
        additional = [
            {"source": "APP-LB", "target": "SRV-CORE-01", "type": "ROUTES_TO"},
            {"source": "APP-LB", "target": "SRV-CORE-02", "type": "ROUTES_TO"},
            {"source": "APP-PAY", "target": "SRV-PAY-02", "type": "RUNS_ON"},
            {"source": "APP-IDS", "target": "SRV-SEC-01", "type": "RUNS_ON"},
            {"source": "APP-DLP", "target": "SRV-SEC-01", "type": "RUNS_ON"},
            {"source": "APP-COMP", "target": "SRV-SEC-01", "type": "RUNS_ON"},
        ]
        
        return relationships + additional


class MinimalBankTemplate(InfrastructureTemplate):
    """Minimale Bank-Infrastruktur für kleine Institute."""
    
    def __init__(self):
        super().__init__(
            name="Minimal Bank Infrastructure",
            description="Minimale IT-Infrastruktur für eine kleine Bank oder Sparkasse"
        )
    
    def get_entities(self) -> List[Dict[str, Any]]:
        """Gibt Entitäten für Minimal Bank zurück."""
        return [
            {"id": "SRV-01", "type": "Server", "name": "Main Server", "status": "online", "criticality": "critical"},
            {"id": "APP-CORE", "type": "Application", "name": "Core Banking System", "status": "online", "criticality": "critical"},
            {"id": "DB-01", "type": "Database", "name": "Main Database", "status": "online", "criticality": "critical"},
            {"id": "APP-WEB", "type": "Application", "name": "Web Portal", "status": "online", "criticality": "important"},
            {"id": "NET-INT", "type": "Network", "name": "Internal Network", "status": "online", "criticality": "critical"},
        ]
    
    def get_relationships(self) -> List[Dict[str, Any]]:
        """Gibt Beziehungen für Minimal Bank zurück."""
        return [
            {"source": "APP-CORE", "target": "SRV-01", "type": "RUNS_ON"},
            {"source": "APP-CORE", "target": "DB-01", "type": "USES"},
            {"source": "APP-WEB", "target": "SRV-01", "type": "RUNS_ON"},
            {"source": "SRV-01", "target": "NET-INT", "type": "CONNECTS_TO"},
        ]


class GenericCrisisTemplate(InfrastructureTemplate):
    """Generisches Krisenszenario-Template für verschiedene Szenarien."""
    
    def __init__(self):
        super().__init__(
            name="Generic Crisis Scenario Template",
            description="Generisches Template für verschiedene Krisenszenarien mit flexibler Infrastruktur. Ideal für Tests und verschiedene Angriffsszenarien."
        )
    
    def get_entities(self) -> List[Dict[str, Any]]:
        """Gibt Entitäten für generisches Krisenszenario zurück."""
        return [
            # Critical Infrastructure
            {"id": "SRV-CRIT-01", "type": "Server", "name": "Critical Server 1", "status": "online", "criticality": "critical"},
            {"id": "SRV-CRIT-02", "type": "Server", "name": "Critical Server 2", "status": "online", "criticality": "critical"},
            {"id": "APP-CRIT", "type": "Application", "name": "Critical Application", "status": "online", "criticality": "critical"},
            {"id": "DB-CRIT", "type": "Database", "name": "Critical Database", "status": "online", "criticality": "critical"},
            
            # Important Systems
            {"id": "SRV-IMP-01", "type": "Server", "name": "Important Server 1", "status": "online", "criticality": "important"},
            {"id": "APP-IMP", "type": "Application", "name": "Important Application", "status": "online", "criticality": "important"},
            {"id": "DB-IMP", "type": "Database", "name": "Important Database", "status": "online", "criticality": "important"},
            
            # Standard Systems
            {"id": "SRV-STD-01", "type": "Server", "name": "Standard Server 1", "status": "online", "criticality": "standard"},
            {"id": "APP-STD", "type": "Application", "name": "Standard Application", "status": "online", "criticality": "standard"},
            
            # Network Infrastructure
            {"id": "NET-DMZ", "type": "Network", "name": "DMZ Network", "status": "online", "criticality": "important"},
            {"id": "NET-INT", "type": "Network", "name": "Internal Network", "status": "online", "criticality": "critical"},
            {"id": "NET-EXT", "type": "Network", "name": "External Network", "status": "online", "criticality": "standard"},
            
            # Security Infrastructure
            {"id": "SRV-SEC-01", "type": "Server", "name": "Security Server", "status": "online", "criticality": "important"},
            {"id": "APP-SEC", "type": "Application", "name": "Security Application", "status": "online", "criticality": "important"},
            {"id": "APP-FW", "type": "Application", "name": "Firewall", "status": "online", "criticality": "important"},
            
            # Backup Systems
            {"id": "SRV-BACKUP-01", "type": "Server", "name": "Backup Server", "status": "online", "criticality": "important"},
            {"id": "APP-BACKUP", "type": "Application", "name": "Backup System", "status": "online", "criticality": "important"},
            
            # Departments
            {"id": "DEPT-IT", "type": "Department", "name": "IT Operations", "status": "operational", "criticality": "standard"},
            {"id": "DEPT-SEC", "type": "Department", "name": "IT Security", "status": "operational", "criticality": "important"},
            {"id": "DEPT-OPS", "type": "Department", "name": "Operations", "status": "operational", "criticality": "important"},
        ]
    
    def get_relationships(self) -> List[Dict[str, Any]]:
        """Gibt Beziehungen für generisches Krisenszenario zurück."""
        return [
            # Critical Infrastructure Dependencies
            {"source": "APP-CRIT", "target": "SRV-CRIT-01", "type": "RUNS_ON"},
            {"source": "APP-CRIT", "target": "SRV-CRIT-02", "type": "RUNS_ON"},
            {"source": "APP-CRIT", "target": "DB-CRIT", "type": "USES"},
            
            # Important Systems
            {"source": "APP-IMP", "target": "SRV-IMP-01", "type": "RUNS_ON"},
            {"source": "APP-IMP", "target": "DB-IMP", "type": "USES"},
            {"source": "APP-IMP", "target": "APP-CRIT", "type": "DEPENDS_ON"},
            
            # Standard Systems
            {"source": "APP-STD", "target": "SRV-STD-01", "type": "RUNS_ON"},
            
            # Network Connections
            {"source": "SRV-CRIT-01", "target": "NET-INT", "type": "CONNECTS_TO"},
            {"source": "SRV-IMP-01", "target": "NET-INT", "type": "CONNECTS_TO"},
            {"source": "SRV-STD-01", "target": "NET-DMZ", "type": "CONNECTS_TO"},
            
            # Security Infrastructure
            {"source": "APP-SEC", "target": "SRV-SEC-01", "type": "RUNS_ON"},
            {"source": "APP-FW", "target": "SRV-SEC-01", "type": "RUNS_ON"},
            {"source": "APP-SEC", "target": "NET-INT", "type": "MONITORS"},
            {"source": "APP-SEC", "target": "NET-DMZ", "type": "MONITORS"},
            
            # Backup Dependencies
            {"source": "APP-BACKUP", "target": "SRV-BACKUP-01", "type": "RUNS_ON"},
            {"source": "APP-BACKUP", "target": "DB-CRIT", "type": "BACKS_UP"},
            {"source": "APP-BACKUP", "target": "DB-IMP", "type": "BACKS_UP"},
            {"source": "SRV-BACKUP-01", "target": "NET-INT", "type": "CONNECTS_TO"},
            
            # Department Usage
            {"source": "DEPT-IT", "target": "APP-CRIT", "type": "MANAGES"},
            {"source": "DEPT-SEC", "target": "APP-SEC", "type": "USES"},
            {"source": "DEPT-OPS", "target": "APP-IMP", "type": "USES"},
        ]


def get_available_templates() -> Dict[str, InfrastructureTemplate]:
    """Gibt alle verfügbaren Templates zurück."""
    return {
        "standard_bank": StandardBankTemplate(),
        "large_bank": LargeBankTemplate(),
        "minimal_bank": MinimalBankTemplate(),
        "generic_crisis": GenericCrisisTemplate(),
    }


def load_template_to_neo4j(
    template: InfrastructureTemplate,
    neo4j_client,
    clear_existing: bool = True
) -> bool:
    """
    Lädt ein Infrastructure Template in Neo4j.
    
    Args:
        template: InfrastructureTemplate Instanz
        neo4j_client: Neo4jClient Instanz
        clear_existing: Wenn True, werden bestehende Entitäten gelöscht
    
    Returns:
        True wenn erfolgreich
    """
    try:
        if not neo4j_client.driver:
            neo4j_client.connect()
        
        with neo4j_client.driver.session(database=neo4j_client.database) as session:
            # Lösche bestehende Entitäten wenn gewünscht
            if clear_existing:
                session.run("MATCH (n:Entity) DETACH DELETE n")
                print("🗑️  Bestehende Entitäten gelöscht")
            
            # Erstelle Entitäten
            entities = template.get_entities()
            for entity in entities:
                query = """
                CREATE (e:Entity {
                    id: $id,
                    type: $type,
                    name: $name,
                    status: $status,
                    criticality: $criticality
                })
                """
                session.run(
                    query,
                    id=entity["id"],
                    type=entity["type"],
                    name=entity["name"],
                    status=entity["status"],
                    criticality=entity.get("criticality", "standard")
                )
            
            print(f"✅ {len(entities)} Entitäten erstellt")
            
            # Erstelle Beziehungen
            relationships = template.get_relationships()
            for rel in relationships:
                query = f"""
                MATCH (source:Entity {{id: $source_id}}), (target:Entity {{id: $target_id}})
                CREATE (source)-[r:{rel['type']}]->(target)
                """
                session.run(
                    query,
                    source_id=rel["source"],
                    target_id=rel["target"]
                )
            
            print(f"✅ {len(relationships)} Beziehungen erstellt")
            
            print(f"✅ Template '{template.name}' erfolgreich geladen")
            return True
            
    except Exception as e:
        print(f"❌ Fehler beim Laden des Templates: {e}")
        return False


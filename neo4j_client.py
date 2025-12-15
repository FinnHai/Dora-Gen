"""
Neo4j Client für Knowledge Graph State Management.

Verwaltet die Verbindung zu Neo4j und stellt Methoden für
State-Abfragen und Updates bereit.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from neo4j import GraphDatabase
from state_models import KnowledgeGraphEntity, GraphStateUpdate, CrisisPhase
import os
from dotenv import load_dotenv

load_dotenv()


class Neo4jClient:
    """
    Client für Neo4j Knowledge Graph.
    
    Verwaltet den Systemzustand (Assets, Status, Beziehungen)
    für das State Management im LangGraph-Workflow.
    """

    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: str = "neo4j"
    ):
        """
        Initialisiert den Neo4j Client.
        
        Args:
            uri: Neo4j URI (Standard: aus Umgebungsvariable NEO4J_URI)
            user: Neo4j Benutzername (Standard: aus Umgebungsvariable NEO4J_USER)
            password: Neo4j Passwort (Standard: aus Umgebungsvariable NEO4J_PASSWORD)
            database: Datenbankname (Standard: "neo4j")
        """
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        self.database = database
        self.driver = None

    def connect(self):
        """Stellt die Verbindung zu Neo4j her."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # Teste die Verbindung
            with self.driver.session(database=self.database) as session:
                session.run("RETURN 1")
            print(f"✓ Verbindung zu Neo4j hergestellt: {self.uri}")
        except Exception as e:
            print(f"✗ Fehler bei Neo4j-Verbindung: {e}")
            raise

    def close(self):
        """Schließt die Verbindung zu Neo4j."""
        if self.driver:
            self.driver.close()
            print("✓ Neo4j-Verbindung geschlossen")

    def get_current_state(self, entity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Ruft den aktuellen Systemzustand ab.
        
        Args:
            entity_type: Optional - Filter nach Entity-Typ (z.B. 'Server', 'Application')
        
        Returns:
            Liste von Entitäten mit ihren Properties und Beziehungen
        """
        if not self.driver:
            raise RuntimeError("Neo4j Client nicht verbunden. Rufe connect() auf.")

        with self.driver.session(database=self.database) as session:
            if entity_type:
                query = """
                MATCH (e {type: $entity_type})
                OPTIONAL MATCH (e)-[r]->(related)
                RETURN e, collect(r) as relationships, collect(related) as related_entities
                """
                result = session.run(query, entity_type=entity_type)
            else:
                query = """
                MATCH (e)
                OPTIONAL MATCH (e)-[r]->(related)
                RETURN e, collect(r) as relationships, collect(related) as related_entities
                LIMIT 100
                """
                result = session.run(query)

            entities = []
            for record in result:
                entity = dict(record["e"])
                entities.append({
                    "entity_id": entity.get("id"),
                    "entity_type": entity.get("type"),
                    "name": entity.get("name"),
                    "status": entity.get("status", "unknown"),
                    "properties": entity,
                    "relationships": [
                        {
                            "target": dict(rel).get("id"),
                            "type": dict(rel).get("type", "RELATED_TO")
                        }
                        for rel in record["related_entities"]
                    ]
                })
            return entities

    def get_entity_status(self, entity_id: str) -> Optional[str]:
        """
        Ruft den Status einer spezifischen Entität ab.
        
        Args:
            entity_id: ID der Entität
        
        Returns:
            Status der Entität oder None, falls nicht gefunden
        """
        if not self.driver:
            raise RuntimeError("Neo4j Client nicht verbunden. Rufe connect() auf.")

        with self.driver.session(database=self.database) as session:
            query = """
            MATCH (e {id: $entity_id})
            RETURN e.status as status
            """
            result = session.run(query, entity_id=entity_id)
            record = result.single()
            return record["status"] if record else None

    def update_entity_status(
        self,
        entity_id: str,
        new_status: str,
        inject_id: Optional[str] = None
    ) -> bool:
        """
        Aktualisiert den Status einer Entität.
        
        Args:
            entity_id: ID der Entität
            new_status: Neuer Status (z.B. 'offline', 'compromised', 'encrypted')
            inject_id: Optional - ID des Injects, der diese Änderung verursacht hat
        
        Returns:
            True, wenn Update erfolgreich
        """
        if not self.driver:
            raise RuntimeError("Neo4j Client nicht verbunden. Rufe connect() auf.")

        with self.driver.session(database=self.database) as session:
            query = """
            MATCH (e {id: $entity_id})
            SET e.status = $new_status,
                e.last_updated = datetime()
            """
            if inject_id:
                query += ", e.last_updated_by_inject = $inject_id"
            
            params = {
                "entity_id": entity_id,
                "new_status": new_status
            }
            if inject_id:
                params["inject_id"] = inject_id

            session.run(query, **params)
            return True

    def get_affected_entities(self, entity_id: str) -> List[str]:
        """
        Ruft alle Entitäten ab, die von einer Statusänderung betroffen sind
        (Second-Order Effects).
        
        Beispiel: Wenn Server A offline geht, sind alle Applikationen betroffen,
        die auf Server A laufen.
        
        Args:
            entity_id: ID der Entität, deren Auswirkungen geprüft werden sollen
        
        Returns:
            Liste von Entity-IDs, die indirekt betroffen sind
        """
        if not self.driver:
            raise RuntimeError("Neo4j Client nicht verbunden. Rufe connect() auf.")

        with self.driver.session(database=self.database) as session:
            # Beispiel: Finde alle Applikationen, die auf einem Server laufen
            query = """
            MATCH (source {id: $entity_id})-[r:RUNS_ON|DEPENDS_ON|USES]->(target)
            RETURN collect(target.id) as affected_ids
            """
            result = session.run(query, entity_id=entity_id)
            record = result.single()
            return record["affected_ids"] if record else []

    def create_entity(self, entity: KnowledgeGraphEntity) -> bool:
        """
        Erstellt eine neue Entität im Knowledge Graph.
        
        Args:
            entity: KnowledgeGraphEntity Objekt
        
        Returns:
            True, wenn erfolgreich
        """
        if not self.driver:
            raise RuntimeError("Neo4j Client nicht verbunden. Rufe connect() auf.")

        with self.driver.session(database=self.database) as session:
            query = """
            CREATE (e:Entity {
                id: $entity_id,
                type: $entity_type,
                name: $name,
                status: $status
            })
            SET e += $properties
            RETURN e
            """
            session.run(
                query,
                entity_id=entity.entity_id,
                entity_type=entity.entity_type,
                name=entity.name,
                status=entity.status,
                properties=entity.properties
            )
            return True

    def initialize_base_infrastructure(self):
        """
        Initialisiert eine Basis-Infrastruktur im Knowledge Graph.
        
        Erstellt beispielhafte Server, Applikationen und Abteilungen
        für Testzwecke.
        """
        if not self.driver:
            raise RuntimeError("Neo4j Client nicht verbunden. Rufe connect() auf.")

        base_entities = [
            {
                "id": "SRV-001",
                "type": "Server",
                "name": "Domain Controller DC-01",
                "status": "online"
            },
            {
                "id": "SRV-002",
                "type": "Server",
                "name": "Application Server APP-SRV-01",
                "status": "online"
            },
            {
                "id": "APP-001",
                "type": "Application",
                "name": "Payment Processing System",
                "status": "online"
            },
            {
                "id": "APP-002",
                "type": "Application",
                "name": "Customer Database",
                "status": "online"
            },
            {
                "id": "DEPT-001",
                "type": "Department",
                "name": "IT Security",
                "status": "operational"
            },
            {
                "id": "DEPT-002",
                "type": "Department",
                "name": "Payment Operations",
                "status": "operational"
            }
        ]

        with self.driver.session(database=self.database) as session:
            # Lösche bestehende Test-Daten
            session.run("MATCH (n) DETACH DELETE n")
            
            # Erstelle Basis-Entitäten
            for entity in base_entities:
                query = """
                CREATE (e:Entity {
                    id: $id,
                    type: $type,
                    name: $name,
                    status: $status
                })
                """
                session.run(query, **entity)
            
            # Erstelle Beziehungen
            relationships = [
                ("APP-001", "RUNS_ON", "SRV-002"),
                ("APP-002", "RUNS_ON", "SRV-002"),
                ("DEPT-002", "USES", "APP-001")
            ]
            
            for source_id, rel_type, target_id in relationships:
                query = """
                MATCH (source {id: $source_id}), (target {id: $target_id})
                CREATE (source)-[r:%s]->(target)
                """ % rel_type
                session.run(query, source_id=source_id, target_id=target_id)
            
            print("✓ Basis-Infrastruktur initialisiert")

    def __enter__(self):
        """Context Manager Support."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context Manager Support."""
        self.close()


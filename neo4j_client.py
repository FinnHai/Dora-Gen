"""
Neo4j Client für Knowledge Graph State Management.

Verwaltet die Verbindung zu Neo4j und stellt Methoden für
State-Abfragen und Updates bereit.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from neo4j import GraphDatabase
from state_models import KnowledgeGraphEntity, GraphStateUpdate, CrisisPhase, ScenarioState, Inject
import os
from dotenv import load_dotenv
import json

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

    def get_affected_entities(self, entity_id: str, max_depth: int = 3) -> List[str]:
        """
        Ruft alle Entitäten ab, die von einer Statusänderung betroffen sind
        (Second-Order Effects) - erweiterte Version mit rekursiver Analyse.
        
        Beispiel: Wenn Server A offline geht, sind alle Applikationen betroffen,
        die auf Server A laufen, und wiederum alle Services, die diese Applikationen nutzen.
        
        Args:
            entity_id: ID der Entität, deren Auswirkungen geprüft werden sollen
            max_depth: Maximale Tiefe der rekursiven Abhängigkeitsanalyse (Standard: 3)
        
        Returns:
            Liste von Entity-IDs, die indirekt betroffen sind (inkl. Tiefe)
        """
        if not self.driver:
            raise RuntimeError("Neo4j Client nicht verbunden. Rufe connect() auf.")

        with self.driver.session(database=self.database) as session:
            # Rekursive Abhängigkeitsanalyse mit mehreren Relationship-Typen
            query = """
            MATCH path = (source {id: $entity_id})-[*1..%d]->(target)
            WHERE ALL(r in relationships(path) WHERE type(r) IN ['RUNS_ON', 'DEPENDS_ON', 'USES', 'CONNECTS_TO', 'REQUIRES'])
            RETURN DISTINCT target.id as affected_id, length(path) as depth
            ORDER BY depth, target.id
            """ % max_depth
            
            result = session.run(query, entity_id=entity_id)
            affected_ids = []
            for record in result:
                affected_ids.append(record["affected_id"])
            
            return affected_ids
    
    def calculate_cascading_impact(
        self,
        entity_id: str,
        new_status: str,
        max_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Berechnet kaskadierende Auswirkungen einer Statusänderung.
        
        Args:
            entity_id: ID der betroffenen Entität
            new_status: Neuer Status (z.B. 'offline', 'compromised', 'encrypted')
            max_depth: Maximale Tiefe der Analyse
        
        Returns:
            Dictionary mit:
            - affected_entities: Liste betroffener Entitäten mit Details
            - critical_paths: Kritische Pfade der Abhängigkeiten
            - estimated_recovery_time: Geschätzte Recovery-Zeit
            - impact_severity: Gesamt-Impact-Schweregrad
        """
        if not self.driver:
            raise RuntimeError("Neo4j Client nicht verbunden. Rufe connect() auf.")
        
        with self.driver.session(database=self.database) as session:
            # Finde alle betroffenen Entitäten mit Details
            query = """
            MATCH path = (source {id: $entity_id})-[*1..%d]->(target)
            WHERE ALL(r in relationships(path) WHERE type(r) IN ['RUNS_ON', 'DEPENDS_ON', 'USES', 'CONNECTS_TO', 'REQUIRES'])
            WITH target, length(path) as depth, path
            RETURN DISTINCT 
                target.id as entity_id,
                target.name as entity_name,
                target.type as entity_type,
                target.status as current_status,
                depth,
                [r in relationships(path) | type(r)] as relationship_chain
            ORDER BY depth, target.type
            """ % max_depth
            
            result = session.run(query, entity_id=entity_id)
            
            affected_entities = []
            critical_paths = []
            max_depth_found = 0
            
            for record in result:
                entity_info = {
                    "entity_id": record["entity_id"],
                    "entity_name": record["entity_name"],
                    "entity_type": record["entity_type"],
                    "current_status": record["current_status"],
                    "depth": record["depth"],
                    "relationship_chain": record["relationship_chain"]
                }
                affected_entities.append(entity_info)
                max_depth_found = max(max_depth_found, record["depth"])
                
                # Identifiziere kritische Pfade (lange Abhängigkeitsketten)
                if record["depth"] >= 2:
                    critical_paths.append({
                        "path_length": record["depth"],
                        "entity_id": record["entity_id"],
                        "entity_type": record["entity_type"]
                    })
            
            # Bestimme Impact-Schweregrad basierend auf Anzahl und Tiefe
            impact_severity = self._calculate_impact_severity(
                len(affected_entities),
                max_depth_found,
                new_status
            )
            
            # Schätze Recovery-Zeit basierend auf Status und Anzahl betroffener Systeme
            estimated_recovery_time = self._estimate_recovery_time(
                new_status,
                len(affected_entities),
                max_depth_found
            )
            
            return {
                "affected_entities": affected_entities,
                "critical_paths": critical_paths,
                "estimated_recovery_time": estimated_recovery_time,
                "impact_severity": impact_severity,
                "total_affected": len(affected_entities),
                "max_depth": max_depth_found
            }
    
    def _calculate_impact_severity(
        self,
        num_affected: int,
        max_depth: int,
        status: str
    ) -> str:
        """Berechnet den Gesamt-Impact-Schweregrad."""
        # Basis-Score basierend auf Anzahl
        base_score = min(num_affected * 10, 100)
        
        # Tiefe-Multiplikator
        depth_multiplier = 1 + (max_depth * 0.2)
        
        # Status-Multiplikator
        status_multipliers = {
            "compromised": 1.5,
            "encrypted": 2.0,
            "offline": 1.3,
            "degraded": 1.1,
            "suspicious": 1.0
        }
        status_mult = status_multipliers.get(status, 1.0)
        
        final_score = base_score * depth_multiplier * status_mult
        
        if final_score >= 80:
            return "Critical"
        elif final_score >= 50:
            return "High"
        elif final_score >= 25:
            return "Medium"
        else:
            return "Low"
    
    def _estimate_recovery_time(
        self,
        status: str,
        num_affected: int,
        max_depth: int
    ) -> str:
        """Schätzt die Recovery-Zeit basierend auf Status und Auswirkungen."""
        # Basis-Recovery-Zeiten (in Stunden)
        base_times = {
            "compromised": 24,
            "encrypted": 48,
            "offline": 8,
            "degraded": 4,
            "suspicious": 2
        }
        
        base_time = base_times.get(status, 12)
        
        # Multipliziere mit Anzahl betroffener Systeme (logarithmisch)
        import math
        time_multiplier = 1 + math.log10(max(num_affected, 1)) * 0.5
        
        # Tiefe erhöht Recovery-Zeit
        depth_multiplier = 1 + (max_depth * 0.1)
        
        estimated_hours = base_time * time_multiplier * depth_multiplier
        
        if estimated_hours < 1:
            return f"{int(estimated_hours * 60)} Minuten"
        elif estimated_hours < 24:
            return f"{int(estimated_hours)} Stunden"
        else:
            days = estimated_hours / 24
            return f"{days:.1f} Tage"

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

    def initialize_base_infrastructure(self, template_name: Optional[str] = None):
        """
        Initialisiert eine Basis-Infrastruktur im Knowledge Graph.
        
        Erstellt beispielhafte Server, Applikationen und Abteilungen
        für Testzwecke. Kann auch ein Infrastructure Template verwenden.
        
        Args:
            template_name: Optional - Name des Templates ('standard_bank', 'large_bank', 'minimal_bank')
                          Wenn None, wird die einfache Basis-Infrastruktur verwendet
        """
        if not self.driver:
            raise RuntimeError("Neo4j Client nicht verbunden. Rufe connect() auf.")
        
        # Verwende Template falls angegeben
        if template_name:
            try:
                from templates.infrastructure_templates import get_available_templates, load_template_to_neo4j
                templates = get_available_templates()
                if template_name in templates:
                    template = templates[template_name]
                    return load_template_to_neo4j(template, self, clear_existing=True)
                else:
                    print(f"⚠️  Template '{template_name}' nicht gefunden. Verwende Basis-Infrastruktur.")
            except ImportError:
                print("⚠️  Infrastructure Templates nicht verfügbar. Verwende Basis-Infrastruktur.")
            except Exception as e:
                print(f"⚠️  Fehler beim Laden des Templates: {e}. Verwende Basis-Infrastruktur.")

        # Fallback: Einfache Basis-Infrastruktur
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

    def seed_enterprise_infrastructure(self):
        """
        Seeded die Datenbank mit genau 40 Assets für Stress-Tests.
        
        Erstellt verwirrend ähnliche Asset-Namen, um LLM-Hallucinations unter
        hoher kognitiver Belastung zu testen.
        
        WICHTIG: Löscht alle bestehenden Entities vor dem Seeding!
        """
        if not self.driver:
            raise RuntimeError("Neo4j Client nicht verbunden. Rufe connect() auf.")
        
        # Definiere genau 40 Assets mit verwirrend ähnlichen Namen
        enterprise_assets = []
        
        # 5x Core Servers (SRV-CORE-001 bis 005)
        for i in range(1, 6):
            enterprise_assets.append({
                "id": f"SRV-CORE-{i:03d}",
                "type": "Server",
                "name": f"Core Server {i:03d}",
                "status": "normal"
            })
        
        # 15x App Servers (SRV-APP-001 bis 015) - leicht zu verwechseln!
        for i in range(1, 16):
            enterprise_assets.append({
                "id": f"SRV-APP-{i:03d}",
                "type": "Server",
                "name": f"Application Server {i:03d}",
                "status": "normal"
            })
        
        # 10x Databases (DB-PROD-01 vs DB-DEV-01 - sehr verwirrend ähnlich!)
        # 5 Production Databases
        for i in range(1, 6):
            enterprise_assets.append({
                "id": f"DB-PROD-{i:02d}",
                "type": "Database",
                "name": f"Production Database {i:02d}",
                "status": "normal"
            })
        # 5 Development Databases (können mit PROD verwechselt werden!)
        for i in range(1, 6):
            enterprise_assets.append({
                "id": f"DB-DEV-{i:02d}",
                "type": "Database",
                "name": f"Development Database {i:02d}",
                "status": "normal"
            })
        
        # 10x Workstations (WS-FINANCE-01 bis 10)
        for i in range(1, 11):
            enterprise_assets.append({
                "id": f"WS-FINANCE-{i:02d}",
                "type": "Workstation",
                "name": f"Finance Workstation {i:02d}",
                "status": "normal"
            })
        
        with self.driver.session(database=self.database) as session:
            # Lösche ALLE bestehenden Entities (inklusive Szenarien und Injects)
            print("🗑️  Lösche bestehende Datenbank-Inhalte...")
            session.run("MATCH (n) DETACH DELETE n")
            
            # Erstelle alle Enterprise Assets
            print(f"🏢 Erstelle {len(enterprise_assets)} Enterprise Assets...")
            for asset in enterprise_assets:
                query = """
                CREATE (e:Entity {
                    id: $id,
                    type: $type,
                    name: $name,
                    status: $status
                })
                """
                session.run(query, **asset)
            
            # Erstelle einige kritische Beziehungen (für Realismus)
            relationships = [
                # Payment System Dependencies
                ("SRV-APP-01", "RUNS_ON", "SRV-CORE-01"),
                ("SRV-APP-02", "RUNS_ON", "SRV-CORE-02"),
                ("SRV-APP-01", "USES", "DB-SQL-03"),
                ("SRV-APP-02", "USES", "DB-SQL-04"),
                
                # HR System Dependencies
                ("SRV-APP-04", "RUNS_ON", "SRV-CORE-03"),
                ("SRV-APP-05", "USES", "DB-SQL-01"),
                ("SRV-APP-06", "USES", "DB-SQL-02"),
                
                # CRM Dependencies
                ("SRV-APP-07", "RUNS_ON", "SRV-CORE-04"),
                ("SRV-APP-08", "USES", "DB-SQL-01"),
                
                # Legacy System Dependencies
                ("LEGACY-PAYMENT-V1", "RUNS_ON", "LEGACY-SRV-01"),
                ("LEGACY-PAYMENT-V2", "RUNS_ON", "LEGACY-SRV-02"),
                ("LEGACY-PAYMENT-V1", "USES", "LEGACY-DB-01"),
                
                # Network Dependencies
                ("SRV-CORE-01", "CONNECTS_TO", "FW-INT-01"),
                ("SRV-CORE-02", "CONNECTS_TO", "FW-INT-01"),
                ("FW-INT-01", "CONNECTS_TO", "ROUTER-CORE-01"),
                ("ROUTER-CORE-01", "CONNECTS_TO", "FW-EXT-01"),
            ]
            
            # Erstelle einige kritische Beziehungen (für Realismus)
            relationships = [
                # Core Server Dependencies
                ("SRV-APP-001", "RUNS_ON", "SRV-CORE-001"),
                ("SRV-APP-002", "RUNS_ON", "SRV-CORE-002"),
                ("SRV-APP-003", "RUNS_ON", "SRV-CORE-003"),
                
                # Database Dependencies (verwirrend: PROD vs DEV)
                ("SRV-APP-001", "USES", "DB-PROD-01"),
                ("SRV-APP-002", "USES", "DB-PROD-02"),
                ("SRV-APP-003", "USES", "DB-DEV-01"),  # Kann mit PROD verwechselt werden!
                ("SRV-APP-004", "USES", "DB-DEV-02"),
                
                # Workstation Dependencies
                ("WS-FINANCE-01", "CONNECTS_TO", "SRV-APP-001"),
                ("WS-FINANCE-02", "CONNECTS_TO", "SRV-APP-002"),
            ]
            
            for source_id, rel_type, target_id in relationships:
                query = f"""
                MATCH (source {{id: $source_id}}), (target {{id: $target_id}})
                CREATE (source)-[r:{rel_type}]->(target)
                """
                session.run(query, source_id=source_id, target_id=target_id)
            
            print(f"✅ Enterprise Infrastructure erfolgreich geseeded: {len(enterprise_assets)} Assets erstellt")
            print(f"   - Core Servers: 5 (SRV-CORE-001 bis 005)")
            print(f"   - App Servers: 15 (SRV-APP-001 bis 015)")
            print(f"   - Production Databases: 5 (DB-PROD-01 bis 05)")
            print(f"   - Development Databases: 5 (DB-DEV-01 bis 05) - leicht mit PROD zu verwechseln!")
            print(f"   - Finance Workstations: 10 (WS-FINANCE-01 bis 10)")
            print(f"   - Relationships: {len(relationships)}")
            return len(enterprise_assets)

    def __enter__(self):
        """Context Manager Support."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context Manager Support."""
        self.close()
    
    def save_scenario(self, scenario_state: ScenarioState, user: Optional[str] = None) -> str:
        """
        Speichert ein vollständiges Szenario in Neo4j.
        
        Args:
            scenario_state: ScenarioState Objekt mit allen Injects
            user: Optional - Benutzername, der das Szenario erstellt hat
        
        Returns:
            Scenario ID (die bereits vorhandene oder neu erstellte)
        """
        if not self.driver:
            raise RuntimeError("Neo4j Client nicht verbunden. Rufe connect() auf.")
        
        with self.driver.session(database=self.database) as session:
            # Erstelle oder aktualisiere Scenario Node
            scenario_query = """
            MERGE (s:Scenario {id: $scenario_id})
            SET s.type = $scenario_type,
                s.current_phase = $current_phase,
                s.start_time = datetime($start_time),
                s.created_at = datetime(),
                s.user = $user,
                s.inject_count = $inject_count,
                s.metadata = $metadata
            RETURN s.id as scenario_id
            """
            
            start_time_str = scenario_state.start_time.isoformat() if isinstance(scenario_state.start_time, datetime) else scenario_state.start_time
            
            result = session.run(
                scenario_query,
                scenario_id=scenario_state.scenario_id,
                scenario_type=scenario_state.scenario_type.value if hasattr(scenario_state.scenario_type, 'value') else str(scenario_state.scenario_type),
                current_phase=scenario_state.current_phase.value if hasattr(scenario_state.current_phase, 'value') else str(scenario_state.current_phase),
                start_time=start_time_str,
                user=user or "system",
                inject_count=len(scenario_state.injects),
                metadata=json.dumps(scenario_state.metadata) if scenario_state.metadata else "{}"
            )
            
            scenario_id = result.single()["scenario_id"]
            
            # FORCE SERIALIZATION: Convert Pydantic objects to dicts if needed
            injects_payload = []
            for inj in scenario_state.injects:
                if hasattr(inj, 'model_dump'):
                    injects_payload.append(inj.model_dump())  # Pydantic v2
                elif hasattr(inj, 'dict'):
                    injects_payload.append(inj.dict())  # Pydantic v1
                else:
                    injects_payload.append(inj)  # Already dict
            
            # Erstelle Inject Nodes und verknüpfe sie mit Scenario
            for inject in scenario_state.injects:
                # Erstelle Inject Node
                inject_query = """
                MERGE (i:Inject {id: $inject_id})
                SET i.time_offset = $time_offset,
                    i.phase = $phase,
                    i.source = $source,
                    i.target = $target,
                    i.modality = $modality,
                    i.content = $content,
                    i.mitre_id = $mitre_id,
                    i.dora_compliance_tag = $dora_tag,
                    i.business_impact = $business_impact,
                    i.severity = $severity,
                    i.created_at = datetime()
                WITH i
                MATCH (s:Scenario {id: $scenario_id})
                MERGE (s)-[:CONTAINS]->(i)
                RETURN i.id as inject_id
                """
                
                session.run(
                    inject_query,
                    inject_id=inject.inject_id,
                    time_offset=inject.time_offset,
                    phase=inject.phase.value if hasattr(inject.phase, 'value') else str(inject.phase),
                    source=inject.source,
                    target=inject.target,
                    modality=inject.modality.value if hasattr(inject.modality, 'value') else str(inject.modality),
                    content=inject.content,
                    mitre_id=inject.technical_metadata.mitre_id or "",
                    dora_tag=inject.dora_compliance_tag or "",
                    business_impact=inject.business_impact or "",
                    severity=inject.technical_metadata.severity or "",
                    scenario_id=scenario_id
                )
                
                # Verknüpfe Inject mit betroffenen Entities
                for asset_id in inject.technical_metadata.affected_assets:
                    entity_link_query = """
                    MATCH (i:Inject {id: $inject_id})
                    MATCH (e:Entity {id: $asset_id})
                    MERGE (i)-[:AFFECTS]->(e)
                    """
                    session.run(entity_link_query, inject_id=inject.inject_id, asset_id=asset_id)
            
            print(f"✅ Szenario {scenario_id} in Neo4j gespeichert ({len(scenario_state.injects)} Injects)")
            return scenario_id
    
    def get_scenario(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """
        Ruft ein gespeichertes Szenario aus Neo4j ab.
        
        Args:
            scenario_id: ID des Szenarios
        
        Returns:
            Dictionary mit Szenario-Daten oder None wenn nicht gefunden
        """
        if not self.driver:
            raise RuntimeError("Neo4j Client nicht verbunden. Rufe connect() auf.")
        
        with self.driver.session(database=self.database) as session:
            query = """
            MATCH (s:Scenario {id: $scenario_id})
            OPTIONAL MATCH (s)-[:CONTAINS]->(i:Inject)
            OPTIONAL MATCH (i)-[:AFFECTS]->(e:Entity)
            RETURN s,
                   collect(DISTINCT i) as injects,
                   collect(DISTINCT e.id) as affected_entities
            """
            
            result = session.run(query, scenario_id=scenario_id)
            record = result.single()
            
            if not record:
                return None
            
            scenario_node = dict(record["s"])
            injects = []
            
            for inject_node in record["injects"]:
                if inject_node:
                    injects.append(dict(inject_node))
            
            return {
                "scenario_id": scenario_node.get("id"),
                "scenario_type": scenario_node.get("type"),
                "current_phase": scenario_node.get("current_phase"),
                "start_time": scenario_node.get("start_time"),
                "user": scenario_node.get("user"),
                "inject_count": scenario_node.get("inject_count", 0),
                "metadata": json.loads(scenario_node.get("metadata", "{}")),
                "injects": injects,
                "affected_entities": list(set(record["affected_entities"])) if record["affected_entities"] else []
            }
    
    def list_scenarios(
        self,
        limit: int = 50,
        user: Optional[str] = None,
        scenario_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Listet alle gespeicherten Szenarien auf.
        
        Args:
            limit: Maximale Anzahl zurückzugebender Szenarien
            user: Optional - Filter nach Benutzer
            scenario_type: Optional - Filter nach Szenario-Typ
        
        Returns:
            Liste von Szenario-Dictionaries
        """
        if not self.driver:
            raise RuntimeError("Neo4j Client nicht verbunden. Rufe connect() auf.")
        
        with self.driver.session(database=self.database) as session:
            query = """
            MATCH (s:Scenario)
            WHERE ($user IS NULL OR s.user = $user)
            AND ($scenario_type IS NULL OR s.type = $scenario_type)
            RETURN s.id as scenario_id,
                   s.type as scenario_type,
                   s.current_phase as current_phase,
                   s.start_time as start_time,
                   s.created_at as created_at,
                   s.user as user,
                   s.inject_count as inject_count
            ORDER BY s.created_at DESC
            LIMIT $limit
            """
            
            result = session.run(
                query,
                user=user,
                scenario_type=scenario_type,
                limit=limit
            )
            
            scenarios = []
            for record in result:
                scenarios.append({
                    "scenario_id": record["scenario_id"],
                    "scenario_type": record["scenario_type"],
                    "current_phase": record["current_phase"],
                    "start_time": record["start_time"],
                    "created_at": record["created_at"],
                    "user": record["user"],
                    "inject_count": record["inject_count"] or 0
                })
            
            return scenarios
    
    def delete_scenario(self, scenario_id: str) -> bool:
        """
        Löscht ein Szenario aus Neo4j (inklusive aller Injects).
        
        Args:
            scenario_id: ID des zu löschenden Szenarios
        
        Returns:
            True wenn erfolgreich gelöscht
        """
        if not self.driver:
            raise RuntimeError("Neo4j Client nicht verbunden. Rufe connect() auf.")
        
        with self.driver.session(database=self.database) as session:
            query = """
            MATCH (s:Scenario {id: $scenario_id})
            OPTIONAL MATCH (s)-[:CONTAINS]->(i:Inject)
            DETACH DELETE s, i
            RETURN count(s) as deleted
            """
            
            result = session.run(query, scenario_id=scenario_id)
            deleted = result.single()["deleted"]
            
            if deleted > 0:
                print(f"✅ Szenario {scenario_id} gelöscht")
                return True
            else:
                print(f"⚠️  Szenario {scenario_id} nicht gefunden")
                return False


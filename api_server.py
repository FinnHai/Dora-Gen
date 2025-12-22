"""
FastAPI REST API Server für CRUX Frontend Integration.

Stellt Endpoints bereit für:
- Szenario-Generierung
- Inject-Verwaltung
- Graph-Daten
- Critic-Logs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from neo4j_client import Neo4jClient
from workflows.scenario_workflow import ScenarioWorkflow
from state_models import ScenarioType, Inject as InjectModel
from forensic_logger import get_forensic_logger
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="CRUX API", description="REST API für CRUX Frontend")

# CORS Middleware für Frontend-Zugriff
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
neo4j_client: Optional[Neo4jClient] = None
workflow: Optional[ScenarioWorkflow] = None


def get_neo4j_client():
    """Lazy initialization of Neo4j client."""
    global neo4j_client
    if neo4j_client is None:
        neo4j_client = Neo4jClient()
        neo4j_client.connect()
    return neo4j_client


def get_workflow():
    """Lazy initialization of workflow."""
    global workflow
    if workflow is None:
        workflow = ScenarioWorkflow(
            neo4j_client=get_neo4j_client(),
            max_iterations=20,
            interactive_mode=False
        )
    return workflow


# Pydantic Models für API
class InjectResponse(BaseModel):
    inject_id: str
    time_offset: str
    content: str
    status: str  # 'generating', 'validating', 'verified', 'rejected'
    phase: str
    source: str
    target: str
    modality: str
    mitre_id: Optional[str] = None
    affected_assets: List[str] = []
    refinement_history: Optional[List[Dict[str, Any]]] = None


class GraphNodeResponse(BaseModel):
    id: str
    label: str
    type: str  # 'server', 'database', 'network', 'workstation'
    status: str  # 'online', 'offline', 'compromised', 'degraded'


class GraphLinkResponse(BaseModel):
    source: str
    target: str
    type: str


class CriticLogResponse(BaseModel):
    timestamp: str
    inject_id: str
    event_type: str  # 'DRAFT', 'CRITIC', 'REFINED'
    message: str
    details: Optional[Dict[str, Any]] = None


class ScenarioRequest(BaseModel):
    scenario_type: str
    num_injects: int = 10


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "CRUX API"}


@app.get("/api/graph/nodes")
async def get_graph_nodes():
    """Holt alle Nodes aus dem Knowledge Graph."""
    try:
        client = get_neo4j_client()
        # Verwende get_current_state statt get_all_assets
        entities = client.get_current_state()
        
        graph_nodes = []
        seen_ids = set()
        
        for entity in entities:
            # Extrahiere Node-Informationen aus Entity
            entity_data = entity.get("e", {})
            if isinstance(entity_data, dict):
                # Versuche verschiedene ID-Felder
                node_id = (
                    entity_data.get("id") or 
                    entity_data.get("entity_id") or
                    entity_data.get("name") or 
                    str(entity_data.get("identity", ""))
                )
                
                if node_id and node_id not in seen_ids:
                    seen_ids.add(node_id)
                    
                    # Bestimme Typ
                    node_type = entity_data.get("type") or entity_data.get("entity_type", "server")
                    # Normalisiere Typ
                    type_mapping = {
                        "Server": "server",
                        "Database": "database",
                        "Workstation": "workstation",
                        "Network": "network",
                        "Firewall": "network",
                        "LoadBalancer": "network",
                    }
                    node_type = type_mapping.get(node_type, node_type.lower())
                    
                    # Bestimme Status
                    status = entity_data.get("status", "online")
                    status_mapping = {
                        "normal": "online",
                        "suspicious": "degraded",
                        "compromised": "compromised",
                        "encrypted": "compromised",
                        "degraded": "degraded",
                        "offline": "offline",
                    }
                    status = status_mapping.get(status.lower(), status.lower())
                    
                    graph_nodes.append({
                        "id": node_id,
                        "label": entity_data.get("name") or entity_data.get("label") or node_id,
                        "type": node_type,
                        "status": status,
                    })
        
        return {"nodes": graph_nodes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/graph/links")
async def get_graph_links():
    """Holt alle Relationships aus dem Knowledge Graph."""
    try:
        client = get_neo4j_client()
        
        # Direkte Neo4j-Abfrage für Relationships
        if client.driver:
            with client.driver.session(database=client.database) as session:
                query = """
                MATCH (a)-[r]->(b)
                WHERE a.id IS NOT NULL AND b.id IS NOT NULL
                RETURN a.id as source, b.id as target, type(r) as rel_type
                LIMIT 500
                """
                result = session.run(query)
                
                links = []
                seen_links = set()
                
                for record in result:
                    source_id = record.get("source")
                    target_id = record.get("target")
                    rel_type = record.get("rel_type", "RELATES_TO")
                    
                    if source_id and target_id:
                        link_key = f"{source_id}->{target_id}"
                        if link_key not in seen_links:
                            seen_links.add(link_key)
                            # Normalisiere Relationship-Typ
                            type_mapping = {
                                "RUNS_ON": "CONNECTS_TO",
                                "USES": "USES",
                                "PROTECTS": "PROTECTS",
                                "CONNECTS_TO": "CONNECTS_TO",
                                "REPLICATES_TO": "REPLICATES_TO",
                            }
                            normalized_type = type_mapping.get(rel_type, rel_type)
                            
                            links.append({
                                "source": source_id,
                                "target": target_id,
                                "type": normalized_type,
                            })
                
                if links:
                    return {"links": links}
        
        # Fallback: Parse aus get_current_state
        entities = client.get_current_state()
        links = []
        seen_links = set()
        
        for entity in entities:
            entity_data = entity.get("e", {})
            relationships = entity.get("relationships", [])
            related_entities = entity.get("related_entities", [])
            
            if isinstance(entity_data, dict):
                source_id = (
                    entity_data.get("id") or 
                    entity_data.get("entity_id") or
                    entity_data.get("name") or 
                    str(entity_data.get("identity", ""))
                )
                
                for i, rel in enumerate(relationships):
                    if i < len(related_entities):
                        target_entity = related_entities[i]
                        if isinstance(target_entity, dict):
                            target_id = (
                                target_entity.get("id") or 
                                target_entity.get("entity_id") or
                                target_entity.get("name") or 
                                str(target_entity.get("identity", ""))
                            )
                            
                            if source_id and target_id:
                                link_key = f"{source_id}->{target_id}"
                                if link_key not in seen_links:
                                    seen_links.add(link_key)
                                    rel_type = "CONNECTS_TO"
                                    if isinstance(rel, dict):
                                        rel_type = rel.get("type", "CONNECTS_TO")
                                    
                                    links.append({
                                        "source": source_id,
                                        "target": target_id,
                                        "type": rel_type or "CONNECTS_TO",
                                    })
        
        return {"links": links}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scenario/generate")
async def generate_scenario(request: ScenarioRequest):
    """Generiert ein neues Szenario."""
    try:
        workflow = get_workflow()
        
        # Convert string to ScenarioType enum
        scenario_type_map = {
            "ransomware_double_extortion": ScenarioType.RANSOMWARE_DOUBLE_EXTORTION,
            "ddos_critical_functions": ScenarioType.DDOS_CRITICAL_FUNCTIONS,
            "supply_chain_compromise": ScenarioType.SUPPLY_CHAIN_COMPROMISE,
            "insider_threat": ScenarioType.INSIDER_THREAT,
        }
        
        scenario_type = scenario_type_map.get(request.scenario_type.lower())
        if not scenario_type:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown scenario type: {request.scenario_type}"
            )
        
        result = workflow.generate_scenario(scenario_type=scenario_type)
        
        # Convert Inject models to API format
        injects = []
        for inj in result.get("injects", []):
            if isinstance(inj, InjectModel):
                injects.append({
                    "inject_id": inj.inject_id,
                    "time_offset": inj.time_offset,
                    "content": inj.content,
                    "status": "verified",  # Default status
                    "phase": inj.phase.value if hasattr(inj.phase, 'value') else str(inj.phase),
                    "source": inj.source,
                    "target": inj.target,
                    "modality": inj.modality.value if hasattr(inj.modality, 'value') else str(inj.modality),
                    "mitre_id": inj.technical_metadata.mitre_id if inj.technical_metadata else None,
                    "affected_assets": inj.technical_metadata.affected_assets if inj.technical_metadata else [],
                    "refinement_history": None,  # Would need to parse from forensic logs
                })
        
        return {
            "scenario_id": result.get("scenario_id"),
            "injects": injects,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/scenario/{scenario_id}/logs")
async def get_scenario_logs(scenario_id: str):
    """Holt Critic-Logs für ein Szenario."""
    try:
        import json
        # Read forensic trace log file
        log_file = Path("logs/forensic/forensic_trace.jsonl")
        logs = []
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        try:
                            log_entry = json.loads(line)
                            # Filter nach scenario_id oder zeige alle wenn scenario_id leer
                            if not scenario_id or log_entry.get("scenario_id") == scenario_id:
                                data = log_entry.get("data", {})
                                validation = data.get("validation", {})
                                
                                # Erstelle lesbare Message
                                inject_id = data.get("inject_id", "UNKNOWN")
                                event_type = log_entry.get("event_type", "UNKNOWN")
                                
                                if event_type == "CRITIC":
                                    decision = data.get("decision", "unknown")
                                    is_valid = validation.get("is_valid", False)
                                    errors = validation.get("errors", [])
                                    warnings = validation.get("warnings", [])
                                    
                                    if decision == "reject":
                                        message = f"[CRITIC] Inject {inject_id} rejected"
                                    elif decision == "accept":
                                        message = f"[CRITIC] Inject {inject_id} accepted"
                                    else:
                                        message = f"[CRITIC] Scanning Inject {inject_id}..."
                                elif event_type == "GENERATOR":
                                    message = f"[DRAFT] Inject {inject_id} generated"
                                else:
                                    message = f"[{event_type}] Event for {inject_id}"
                                
                                logs.append({
                                    "timestamp": log_entry.get("timestamp", ""),
                                    "inject_id": inject_id,
                                    "event_type": event_type,
                                    "message": message,
                                    "details": {
                                        "validation": {
                                            "is_valid": validation.get("is_valid", True),
                                            "errors": errors,
                                            "warnings": warnings,
                                        },
                                        "decision": data.get("decision"),
                                        "iteration": log_entry.get("iteration"),
                                        "refine_count": log_entry.get("refine_count", 0),
                                    },
                                })
                        except json.JSONDecodeError:
                            continue
        
        # Sortiere nach Timestamp
        logs.sort(key=lambda x: x["timestamp"])
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/scenario/latest")
async def get_latest_scenario():
    """Holt das neueste Szenario mit allen Injects aus Neo4j oder Forensic Logs."""
    try:
        import json
        from datetime import datetime
        
        # Versuche zuerst aus Neo4j zu holen
        try:
            client = get_neo4j_client()
            # Hole alle Szenarien aus Neo4j
            with client.driver.session(database=client.database) as session:
                query = """
                MATCH (s:Scenario)
                RETURN s
                ORDER BY s.created_at DESC
                LIMIT 1
                """
                result = session.run(query)
                record = result.single()
                
                if record:
                    scenario_node = dict(record["s"])
                    scenario_id = scenario_node.get("id") or scenario_node.get("scenario_id")
                    
                    # Hole Injects für dieses Szenario
                    injects_query = """
                    MATCH (s:Scenario {id: $scenario_id})-[:HAS_INJECT]->(i:Inject)
                    RETURN i
                    ORDER BY i.time_offset ASC
                    """
                    injects_result = session.run(injects_query, scenario_id=scenario_id)
                    
                    injects = []
                    for inj_record in injects_result:
                        inj_data = dict(inj_record["i"])
                        injects.append({
                            "inject_id": inj_data.get("id") or inj_data.get("inject_id"),
                            "time_offset": inj_data.get("time_offset", "T+00:00"),
                            "content": inj_data.get("content", ""),
                            "status": "verified",
                            "phase": inj_data.get("phase", "UNKNOWN"),
                            "source": inj_data.get("source", "System"),
                            "target": inj_data.get("target", "SOC"),
                            "modality": inj_data.get("modality", "SIEM Alert"),
                            "mitre_id": inj_data.get("mitre_id"),
                            "affected_assets": inj_data.get("affected_assets", []),
                            "refinement_history": None,
                        })
                    
                    if injects:
                        return {
                            "scenario_id": scenario_id,
                            "injects": injects,
                        }
        except Exception as neo4j_error:
            # Fallback zu Logs wenn Neo4j nicht verfügbar
            print(f"Neo4j lookup failed, using logs: {neo4j_error}")
            pass
        
        # Fallback: Parse aus Forensic Logs
        log_file = Path("logs/forensic/forensic_trace.jsonl")
        scenario_data = {}  # scenario_id -> {injects: [], logs: []}
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        try:
                            log_entry = json.loads(line)
                            scenario_id = log_entry.get("scenario_id")
                            if not scenario_id:
                                continue
                                
                            if scenario_id not in scenario_data:
                                scenario_data[scenario_id] = {
                                    "injects": {},
                                    "logs": [],
                                    "last_timestamp": None
                                }
                            
                            data = log_entry.get("data", {})
                            inject_id = data.get("inject_id")
                            timestamp = log_entry.get("timestamp", "")
                            
                            # Track latest timestamp
                            if timestamp and (not scenario_data[scenario_id]["last_timestamp"] or timestamp > scenario_data[scenario_id]["last_timestamp"]):
                                scenario_data[scenario_id]["last_timestamp"] = timestamp
                            
                            # Sammle Inject-Informationen aus Logs
                            if inject_id:
                                if inject_id not in scenario_data[scenario_id]["injects"]:
                                    scenario_data[scenario_id]["injects"][inject_id] = {
                                        "inject_id": inject_id,
                                        "status": "verified" if data.get("decision") == "accept" else "rejected",
                                        "iteration": log_entry.get("iteration", 0),
                                        "refine_count": log_entry.get("refine_count", 0),
                                        "validation": data.get("validation", {}),
                                        "first_seen": timestamp,
                                    }
                                else:
                                    # Update mit neueren Daten
                                    if log_entry.get("refine_count", 0) > scenario_data[scenario_id]["injects"][inject_id]["refine_count"]:
                                        scenario_data[scenario_id]["injects"][inject_id].update({
                                            "status": "verified" if data.get("decision") == "accept" else "rejected",
                                            "refine_count": log_entry.get("refine_count", 0),
                                            "validation": data.get("validation", {}),
                                        })
                            
                            # Sammle Logs
                            scenario_data[scenario_id]["logs"].append(log_entry)
                        except json.JSONDecodeError:
                            continue
        
        if not scenario_data:
            return {"scenario_id": None, "injects": []}
        
        # Finde neuestes Szenario basierend auf Timestamp
        latest_scenario_id = max(
            scenario_data.keys(),
            key=lambda sid: scenario_data[sid]["last_timestamp"] or ""
        )
        
        # Konvertiere Injects zu API-Format
        injects = []
        for inject_id, inject_data in sorted(scenario_data[latest_scenario_id]["injects"].items(), 
                                            key=lambda x: x[1]["iteration"]):
            validation = inject_data.get("validation", {})
            errors = validation.get("errors", [])
            
            # Erstelle Refinement-History wenn Refine-Count > 0
            refinement_history = None
            if inject_data.get("refine_count", 0) > 0 and errors:
                refinement_history = [{
                    "original": f"Inject {inject_id} (original)",
                    "corrected": f"Inject {inject_id} (refined)",
                    "errors": errors,
                }]
            
            injects.append({
                "inject_id": inject_id,
                "time_offset": f"T+{inject_data['iteration']:02d}:00",  # Basierend auf Iteration
                "content": f"Inject {inject_id} - Generated in iteration {inject_data['iteration']}",
                "status": inject_data["status"],
                "phase": "UNKNOWN",  # Könnte aus Logs extrahiert werden
                "source": "System",
                "target": "SOC",
                "modality": "SIEM Alert",
                "mitre_id": None,
                "affected_assets": [],  # Könnte aus Logs extrahiert werden
                "refinement_history": refinement_history,
            })
        
        return {
            "scenario_id": latest_scenario_id,
            "injects": injects,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


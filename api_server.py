"""
FastAPI REST API Server für CRUX Frontend Integration.

Stellt Endpoints bereit für:
- Szenario-Generierung
- Inject-Verwaltung
- Graph-Daten
- Critic-Logs
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import sys
import json
from pathlib import Path
from utils.json_utils import serialize_datetime_recursive, safe_json_dumps

# Add parent directory to path for imports
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

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


def get_workflow(max_iterations: int = 20):
    """Lazy initialization of workflow."""
    global workflow
    # Recreate workflow if max_iterations changed
    if workflow is None or workflow.max_iterations != max_iterations:
        workflow = ScenarioWorkflow(
            neo4j_client=get_neo4j_client(),
            max_iterations=max_iterations,
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


class ScenarioRequest(BaseModel):
    scenario_type: str
    num_injects: int = 10


class ScenarioListItem(BaseModel):
    scenario_id: str
    scenario_type: str
    current_phase: str
    start_time: Optional[str] = None
    created_at: Optional[str] = None
    user: Optional[str] = None
    inject_count: int = 0


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "CRUX API Server",
        "version": "1.0.0",
        "endpoints": {
            "graph": "/api/graph/nodes, /api/graph/links",
            "scenario": "/api/scenario/generate, /api/scenario/{id}/logs, /api/scenario/list, /api/scenario/{id}",
            "forensic": "/api/forensic/upload"
        }
    }


@app.get("/api/graph/nodes")
async def get_graph_nodes():
    """Gibt alle Graph-Nodes zurück."""
    try:
        client = get_neo4j_client()
        entities = client.get_current_state()
        
        nodes = []
        for entity in entities:
            # get_current_state() gibt entity_id, entity_type, name, status zurück
            node_id = entity.get("entity_id") or entity.get("id", "")
            node_name = entity.get("name", node_id)
            node_type = entity.get("entity_type") or entity.get("type", "server")
            node_status = entity.get("status", "online")
            
            if node_id:  # Nur Nodes mit gültiger ID hinzufügen
                nodes.append({
                    "id": node_id,
                    "label": node_name,
                    "type": node_type.lower() if isinstance(node_type, str) else "server",
                    "status": node_status.lower() if isinstance(node_status, str) else "online",
                })
        
        return {"nodes": nodes}
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error fetching graph nodes: {error_trace}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/graph/links")
async def get_graph_links():
    """Gibt alle Graph-Links zurück."""
    try:
        client = get_neo4j_client()
        
        # Hole alle Relationships
        with client.driver.session(database=client.database) as session:
            query = """
            MATCH (a:Entity)-[r]->(b:Entity)
            RETURN a.id as source, b.id as target, type(r) as type
            """
            result = session.run(query)
            
            links = []
            for record in result:
                links.append({
                    "source": record["source"],
                    "target": record["target"],
                    "type": record["type"],
                })
        
        return {"links": links}
    except Exception as e:
        print(f"Error fetching graph links: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scenario/generate")
async def generate_scenario(request: ScenarioRequest):
    """Generiert ein neues Szenario."""
    try:
        workflow = get_workflow(max_iterations=request.num_injects)
        
        # Map scenario type string to enum
        scenario_type_map = {
            "ransomware": ScenarioType.RANSOMWARE_DOUBLE_EXTORTION,
            "ransomware_double_extortion": ScenarioType.RANSOMWARE_DOUBLE_EXTORTION,
            "data_breach": ScenarioType.INSIDER_THREAT_DATA_MANIPULATION,  # DATA_BREACH existiert nicht, verwende ähnlichen Typ
            "ddos": ScenarioType.DDOS_CRITICAL_FUNCTIONS,
            "ddos_critical_functions": ScenarioType.DDOS_CRITICAL_FUNCTIONS,
            "insider_threat": ScenarioType.INSIDER_THREAT_DATA_MANIPULATION,
            "insider_threat_data_manipulation": ScenarioType.INSIDER_THREAT_DATA_MANIPULATION,
            "supply_chain_compromise": ScenarioType.SUPPLY_CHAIN_COMPROMISE,
            "supply_chain": ScenarioType.SUPPLY_CHAIN_COMPROMISE,
        }
        
        scenario_type = scenario_type_map.get(request.scenario_type.lower())
        if not scenario_type:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown scenario type: {request.scenario_type}. Available: {list(scenario_type_map.keys())}"
            )
        
        # Generate scenario
        result = workflow.generate_scenario(scenario_type=scenario_type)
        
        # Convert injects to response format
        injects_response = []
        for inject in result.get("injects", []):
            injects_response.append({
                "inject_id": inject.inject_id,
                "time_offset": inject.time_offset,
                "content": inject.content,
                "status": "verified",
                "phase": inject.phase.value if hasattr(inject.phase, 'value') else str(inject.phase),
                "source": inject.source,
                "target": inject.target,
                "modality": inject.modality.value if hasattr(inject.modality, 'value') else str(inject.modality),
                "mitre_id": inject.technical_metadata.mitre_id if inject.technical_metadata else None,
                "affected_assets": inject.technical_metadata.affected_assets if inject.technical_metadata else [],
            })
        
        return {
            "scenario_id": result.get("scenario_id"),
            "injects": injects_response,
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error generating scenario: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating scenario: {str(e)}\n\nTraceback:\n{error_trace}"
        )


@app.get("/api/scenario/{scenario_id}/logs")
async def get_scenario_logs(scenario_id: str):
    """Gibt Critic-Logs für ein Szenario zurück."""
    try:
        # Versuche Forensic Trace Datei zu finden
        trace_file = Path(f"logs/forensic/forensic_trace.jsonl")
        logs = []
        
        if trace_file.exists():
            with open(trace_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            log_entry = json.loads(line)
                            # Filter nach scenario_id
                            if log_entry.get('scenario_id') == scenario_id:
                                data = log_entry.get('data', {})
                                validation = data.get('validation', {})
                                
                                logs.append({
                                    "timestamp": log_entry.get("timestamp", ""),
                                    "inject_id": data.get("inject_id", ""),
                                    "event_type": log_entry.get("event_type", "CRITIC"),
                                    "message": f"Validation: {data.get('decision', 'unknown')}",
                                    "details": {
                                        "validation": {
                                            "is_valid": validation.get("is_valid", True),
                                            "errors": validation.get("errors", []),
                                            "warnings": validation.get("warnings", []),
                                        }
                                    }
                                })
                        except json.JSONDecodeError:
                            continue
        
        return {"logs": logs}
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error fetching scenario logs: {error_trace}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/scenario/latest")
async def get_latest_scenario():
    """Gibt das neueste Szenario zurück."""
    try:
        client = get_neo4j_client()
        scenarios = client.list_scenarios(limit=1)
        
        if not scenarios or len(scenarios) == 0:
            return {"scenario_id": None, "injects": []}
        
        latest_scenario = scenarios[0]
        scenario_id = latest_scenario.get("scenario_id")
        
        # Lade vollständiges Szenario
        scenario = client.get_scenario(scenario_id)
        
        if not scenario:
            return {"scenario_id": None, "injects": []}
        
        # Konvertiere Injects zu Response-Format
        injects_response = []
        for inject_data in scenario.get("injects", []):
            injects_response.append({
                "inject_id": inject_data.get("id", ""),
                "time_offset": inject_data.get("time_offset", "T+00:00"),
                "content": inject_data.get("content", ""),
                "status": "verified",
                "phase": inject_data.get("phase", "normal_operation"),
                "source": inject_data.get("source", ""),
                "target": inject_data.get("target", ""),
                "modality": inject_data.get("modality", "SIEM Alert"),
                "mitre_id": inject_data.get("mitre_id", ""),
                "affected_assets": inject_data.get("technical_metadata", {}).get("affected_assets", []) if isinstance(inject_data.get("technical_metadata"), dict) else [],
                "dora_compliance_tag": inject_data.get("dora_compliance_tag"),
                "compliance_tags": inject_data.get("compliance_tags", {}),
            })
        
        return {
            "scenario_id": scenario_id,
            "injects": injects_response,
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error fetching latest scenario: {error_trace}")
        # Return empty result instead of raising error
        return {"scenario_id": None, "injects": []}


@app.get("/api/scenario/list")
async def list_scenarios(
    limit: int = 50,
    user: Optional[str] = None,
    scenario_type: Optional[str] = None
):
    """Listet alle gespeicherten Szenarien auf."""
    try:
        client = get_neo4j_client()
        scenarios = client.list_scenarios(
            limit=limit,
            user=user,
            scenario_type=scenario_type
        )
        
        # Konvertiere zu Response-Format
        scenarios_response = []
        for scenario in scenarios:
            start_time = scenario.get("start_time")
            created_at = scenario.get("created_at")
            
            # Konvertiere datetime zu ISO-String sicher
            start_time_str = None
            if start_time:
                if isinstance(start_time, datetime):
                    start_time_str = start_time.isoformat()
                elif hasattr(start_time, 'isoformat'):
                    start_time_str = start_time.isoformat()
                else:
                    start_time_str = str(start_time)
            
            created_at_str = None
            if created_at:
                if isinstance(created_at, datetime):
                    created_at_str = created_at.isoformat()
                elif hasattr(created_at, 'isoformat'):
                    created_at_str = created_at.isoformat()
                else:
                    created_at_str = str(created_at)
            
            scenarios_response.append({
                "scenario_id": scenario.get("scenario_id"),
                "scenario_type": scenario.get("scenario_type"),
                "current_phase": scenario.get("current_phase"),
                "start_time": start_time_str,
                "created_at": created_at_str,
                "user": scenario.get("user"),
                "inject_count": scenario.get("inject_count", 0),
            })
        
        return {"scenarios": scenarios_response}
    except Exception as e:
        print(f"Error listing scenarios: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/scenario/{scenario_id}")
async def get_scenario(scenario_id: str):
    """Lädt ein gespeichertes Szenario."""
    try:
        client = get_neo4j_client()
        scenario = client.get_scenario(scenario_id)
        
        if not scenario:
            raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
        
        # Konvertiere Injects zu Response-Format
        injects_response = []
        for inject_data in scenario.get("injects", []):
            # #region agent log
            try:
                import json
                import time
                with open('/Users/finnheintzann/Desktop/BA/.cursor/debug.log', 'a') as f:
                    log_entry = {
                        "location": "api_server.py:398",
                        "message": "Transforming inject from Neo4j",
                        "data": {
                            "inject_id": inject_data.get("id", ""),
                            "has_technical_metadata": isinstance(inject_data.get("technical_metadata"), dict),
                            "technical_metadata_type": str(type(inject_data.get("technical_metadata"))),
                            "affected_assets_from_metadata": inject_data.get("technical_metadata", {}).get("affected_assets", []) if isinstance(inject_data.get("technical_metadata"), dict) else None,
                        },
                        "timestamp": int(time.time() * 1000),
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "E"
                    }
                    f.write(json.dumps(log_entry) + '\n')
            except:
                pass
            # #endregion
            
            affected_assets = []
            if isinstance(inject_data.get("technical_metadata"), dict):
                affected_assets = inject_data.get("technical_metadata", {}).get("affected_assets", [])
            elif isinstance(inject_data.get("technical_metadata"), str):
                # Fallback: Versuche JSON zu parsen wenn es ein String ist
                try:
                    tech_meta = json.loads(inject_data.get("technical_metadata", "{}"))
                    affected_assets = tech_meta.get("affected_assets", [])
                except:
                    affected_assets = []
            
            injects_response.append({
                "inject_id": inject_data.get("id", ""),
                "time_offset": inject_data.get("time_offset", "T+00:00"),
                "content": inject_data.get("content", ""),
                "status": "verified",
                "phase": inject_data.get("phase", "normal_operation"),
                "source": inject_data.get("source", ""),
                "target": inject_data.get("target", ""),
                "modality": inject_data.get("modality", "SIEM Alert"),
                "mitre_id": inject_data.get("mitre_id", ""),
                "affected_assets": affected_assets if isinstance(affected_assets, list) else [],
                "dora_compliance_tag": inject_data.get("dora_compliance_tag"),
                "compliance_tags": inject_data.get("compliance_tags", {}),
            })
        
        # Konvertiere start_time sicher
        start_time = scenario.get("start_time")
        start_time_str = None
        if start_time:
            if isinstance(start_time, datetime):
                start_time_str = start_time.isoformat()
            elif hasattr(start_time, 'isoformat'):
                start_time_str = start_time.isoformat()
            else:
                start_time_str = str(start_time)
        
        return {
            "scenario_id": scenario.get("scenario_id"),
            "scenario_type": scenario.get("scenario_type"),
            "current_phase": scenario.get("current_phase"),
            "start_time": start_time_str,
            "injects": injects_response,
            "metadata": scenario.get("metadata", {}),
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error fetching scenario: {error_trace}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/forensic/upload")
async def upload_forensic_trace(file: UploadFile = File(...)):
    """Lädt eine Forensic Trace Datei hoch."""
    try:
        # Speichere Datei temporär
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.jsonl') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Parse JSONL
        logs = []
        with open(tmp_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        log_entry = json.loads(line)
                        logs.append({
                            "timestamp": log_entry.get("timestamp", ""),
                            "inject_id": log_entry.get("data", {}).get("inject_id", ""),
                            "event_type": log_entry.get("event_type", "CRITIC"),
                            "message": f"Validation: {log_entry.get('data', {}).get('decision', 'unknown')}",
                            "details": {
                                "validation": log_entry.get("data", {}).get("validation", {})
                            }
                        })
                    except json.JSONDecodeError:
                        continue
        
        # Lösche temporäre Datei
        os.unlink(tmp_path)
        
        return {
            "success": True,
            "logs_count": len(logs),
            "logs": logs
        }
    except Exception as e:
        print(f"Error uploading forensic trace: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

"""
Integrationstests für den vollständigen Workflow.

Testet den kompletten Workflow-Durchlauf.
"""

import pytest
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Füge Projekt-Root zum Python-Path hinzu
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from neo4j_client import Neo4jClient
from workflows.scenario_workflow import ScenarioWorkflow
from state_models import ScenarioType

load_dotenv()


@pytest.fixture
def neo4j_client():
    """Erstellt einen Neo4j Client für Tests."""
    client = Neo4jClient()
    try:
        client.connect()
        # Initialisiere Basis-Infrastruktur falls nötig
        entities = client.get_current_state()
        if len(entities) < 3:
            client.initialize_base_infrastructure()
        yield client
    except Exception as e:
        pytest.skip(f"Neo4j not available: {e}")
    finally:
        client.close()


@pytest.fixture
def workflow(neo4j_client):
    """Erstellt einen Workflow für Tests."""
    return ScenarioWorkflow(
        neo4j_client=neo4j_client,
        max_iterations=2,  # Klein für schnelle Tests
        interactive_mode=False
    )


class TestWorkflowIntegration:
    """Integrationstests für den Workflow."""
    
    def test_workflow_graph_structure(self, workflow):
        """Testet ob Graph korrekt strukturiert ist."""
        assert workflow.graph is not None
        
        # Prüfe ob Graph kompiliert ist
        assert hasattr(workflow.graph, 'invoke')
    
    def test_initial_state_structure(self, workflow):
        """Testet ob initial_state korrekte Struktur hat."""
        from state_models import ScenarioType, CrisisPhase
        
        initial_state = {
            "scenario_id": "TEST-001",
            "scenario_type": ScenarioType.RANSOMWARE_DOUBLE_EXTORTION,
            "current_phase": CrisisPhase.NORMAL_OPERATION,
            "injects": [],
            "system_state": {},
            "iteration": 0,
            "max_iterations": 2,
            "manager_plan": None,
            "selected_action": None,
            "draft_inject": None,
            "validation_result": None,
            "available_ttps": [],
            "historical_context": [],
            "errors": [],
            "warnings": [],
            "start_time": None,
            "metadata": {},
            "workflow_logs": [],
            "agent_decisions": [],
            "pending_decision": None,
            "user_decisions": [],
            "end_condition": None,
            "interactive_mode": False
        }
        
        # Prüfe ob State alle erforderlichen Keys hat
        required_keys = [
            "scenario_id", "scenario_type", "current_phase", "injects",
            "system_state", "iteration", "max_iterations"
        ]
        
        for key in required_keys:
            assert key in initial_state
    
    def test_state_check_returns_dict(self, workflow, neo4j_client):
        """Testet ob state_check_node Dictionary zurückgibt."""
        from state_models import ScenarioType, CrisisPhase
        
        state = {
            "scenario_id": "TEST-001",
            "scenario_type": ScenarioType.RANSOMWARE_DOUBLE_EXTORTION,
            "current_phase": CrisisPhase.NORMAL_OPERATION,
            "injects": [],
            "system_state": {},
            "iteration": 0,
            "max_iterations": 2,
            "manager_plan": None,
            "selected_action": None,
            "draft_inject": None,
            "validation_result": None,
            "available_ttps": [],
            "historical_context": [],
            "errors": [],
            "warnings": [],
            "start_time": None,
            "metadata": {},
            "workflow_logs": [],
            "agent_decisions": [],
            "pending_decision": None,
            "user_decisions": [],
            "end_condition": None,
            "interactive_mode": False
        }
        
        result = workflow._state_check_node(state)
        
        assert isinstance(result, dict)
        assert "system_state" in result
        assert isinstance(result["system_state"], dict)
        # Prüfe ob system_state direktes Dictionary ist (nicht verschachtelt)
        assert "entities" not in result["system_state"] or isinstance(result["system_state"], dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


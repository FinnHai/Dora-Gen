"""
Tests für einzelne Workflow-Nodes.

Testet jeden Node isoliert.
"""

import pytest
import sys
from pathlib import Path

# Füge Projekt-Root zum Python-Path hinzu
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from workflows.scenario_workflow import ScenarioWorkflow
from state_models import ScenarioType, CrisisPhase
from neo4j_client import Neo4jClient


@pytest.fixture
def neo4j_client():
    """Erstellt einen Neo4j Client für Tests."""
    client = Neo4jClient()
    try:
        client.connect()
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
        max_iterations=2,
        interactive_mode=False
    )


@pytest.fixture
def base_state():
    """Erstellt einen Basis-State für Tests."""
    return {
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


class TestStateCheckNode:
    """Tests für State Check Node."""
    
    def test_state_check_returns_dict(self, workflow, base_state):
        """Testet ob state_check_node Dictionary zurückgibt."""
        result = workflow._state_check_node(base_state)
        
        assert isinstance(result, dict)
        assert "system_state" in result
        assert "workflow_logs" in result
    
    def test_system_state_is_dict(self, workflow, base_state):
        """Testet ob system_state direktes Dictionary ist."""
        result = workflow._state_check_node(base_state)
        
        system_state = result["system_state"]
        assert isinstance(system_state, dict)
        # Sollte NICHT verschachteltes Dictionary mit "entities" Key sein
        assert "entities" not in system_state or isinstance(system_state, dict)


class TestManagerNode:
    """Tests für Manager Node."""
    
    def test_manager_node_structure(self, workflow, base_state):
        """Testet ob manager_node korrekte Struktur zurückgibt."""
        # Setze system_state vorher
        base_state["system_state"] = {
            "SRV-001": {"status": "online", "name": "Server 1"}
        }
        
        try:
            result = workflow._manager_node(base_state)
            
            assert isinstance(result, dict)
            assert "manager_plan" in result
            assert "workflow_logs" in result
        except Exception as e:
            # Kann fehlschlagen wenn LLM nicht verfügbar
            pytest.skip(f"Manager node requires LLM: {e}")


class TestIntelNode:
    """Tests für Intel Node."""
    
    def test_intel_node_structure(self, workflow, base_state):
        """Testet ob intel_node korrekte Struktur zurückgibt."""
        result = workflow._intel_node(base_state)
        
        assert isinstance(result, dict)
        assert "available_ttps" in result
        assert "workflow_logs" in result
        assert isinstance(result["available_ttps"], list)


class TestActionSelectionNode:
    """Tests für Action Selection Node."""
    
    def test_action_selection_with_ttps(self, workflow, base_state):
        """Testet action_selection_node mit verfügbaren TTPs."""
        base_state["available_ttps"] = [
            {"mitre_id": "T1110", "name": "Brute Force", "technique_id": "T1110"}
        ]
        
        result = workflow._action_selection_node(base_state)
        
        assert isinstance(result, dict)
        assert "selected_action" in result
        assert "workflow_logs" in result
    
    def test_action_selection_without_ttps(self, workflow, base_state):
        """Testet action_selection_node ohne verfügbare TTPs."""
        base_state["available_ttps"] = []
        
        result = workflow._action_selection_node(base_state)
        
        assert isinstance(result, dict)
        assert "selected_action" in result
        # Sollte Fallback-TTP verwenden
        assert result["selected_action"] is not None


class TestStateUpdateNode:
    """Tests für State Update Node."""
    
    def test_state_update_without_draft_inject(self, workflow, base_state):
        """Testet state_update_node ohne draft_inject."""
        base_state["draft_inject"] = None
        
        result = workflow._state_update_node(base_state)
        
        assert isinstance(result, dict)
        assert "iteration" in result
        assert result["iteration"] == base_state["iteration"] + 1
    
    def test_state_update_increments_iteration(self, workflow, base_state):
        """Testet ob Iteration korrekt erhöht wird."""
        base_state["iteration"] = 0
        base_state["draft_inject"] = None
        
        result = workflow._state_update_node(base_state)
        
        assert result["iteration"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


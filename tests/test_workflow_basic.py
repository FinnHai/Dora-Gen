"""
Basis-Tests für den Scenario Workflow.

Testet die grundlegende Funktionalität des LangGraph Workflows.
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
from state_models import ScenarioType, CrisisPhase

load_dotenv()


@pytest.fixture
def neo4j_client():
    """Erstellt einen Neo4j Client für Tests."""
    client = Neo4jClient()
    client.connect()
    yield client
    client.close()


@pytest.fixture
def workflow(neo4j_client):
    """Erstellt einen Workflow für Tests."""
    return ScenarioWorkflow(
        neo4j_client=neo4j_client,
        max_iterations=3,
        interactive_mode=False
    )


class TestWorkflowInitialization:
    """Tests für Workflow-Initialisierung."""
    
    def test_workflow_creation(self, workflow):
        """Testet ob Workflow korrekt erstellt wird."""
        assert workflow is not None
        assert workflow.max_iterations == 3
        assert workflow.interactive_mode == False
        assert workflow.graph is not None
    
    def test_workflow_agents_initialized(self, workflow):
        """Testet ob alle Agenten initialisiert sind."""
        assert workflow.manager_agent is not None
        assert workflow.intel_agent is not None
        assert workflow.generator_agent is not None
        assert workflow.critic_agent is not None


class TestWorkflowState:
    """Tests für Workflow State Management."""
    
    def test_state_check_node(self, workflow, neo4j_client):
        """Testet den State Check Node."""
        # Initialisiere Basis-Infrastruktur falls nötig
        entities = neo4j_client.get_current_state()
        if len(entities) < 3:
            neo4j_client.initialize_base_infrastructure()
        
        state = {
            "scenario_id": "TEST-001",
            "scenario_type": ScenarioType.RANSOMWARE_DOUBLE_EXTORTION,
            "current_phase": CrisisPhase.NORMAL_OPERATION,
            "injects": [],
            "system_state": {},
            "iteration": 0,
            "max_iterations": 3,
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
        
        assert "system_state" in result
        assert "workflow_logs" in result
        assert isinstance(result["system_state"], dict)
    
    def test_state_update_iteration_increment(self, workflow):
        """Testet ob Iteration korrekt erhöht wird."""
        state = {
            "scenario_id": "TEST-001",
            "scenario_type": ScenarioType.RANSOMWARE_DOUBLE_EXTORTION,
            "current_phase": CrisisPhase.NORMAL_OPERATION,
            "injects": [],
            "system_state": {},
            "iteration": 0,
            "max_iterations": 3,
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
        
        # Test ohne Draft Inject
        result = workflow._state_update_node(state)
        assert result["iteration"] == 1


class TestWorkflowLogic:
    """Tests für Workflow-Logik."""
    
    def test_should_continue_with_no_injects(self, workflow):
        """Testet _should_continue wenn keine Injects vorhanden."""
        state = {
            "iteration": 0,
            "max_iterations": 5,
            "injects": [],
            "errors": [],
            "current_phase": CrisisPhase.NORMAL_OPERATION,
            "workflow_logs": []
        }
        
        result = workflow._should_continue(state)
        assert result == "continue"
    
    def test_should_continue_with_max_injects(self, workflow):
        """Testet _should_continue wenn max Injects erreicht."""
        from state_models import Inject, InjectModality, TechnicalMetadata
        
        # Erstelle Mock-Injects
        mock_injects = []
        for i in range(5):
            inject = Inject(
                inject_id=f"INJ-{i+1:03d}",
                time_offset=f"T+{i:02d}:00",
                phase=CrisisPhase.NORMAL_OPERATION,
                source="Test",
                target="Test",
                modality=InjectModality.SIEM_ALERT,
                content="Test content",
                technical_metadata=TechnicalMetadata(
                    mitre_id="T1110",
                    affected_assets=["SRV-001"],
                    severity="Medium"
                )
            )
            mock_injects.append(inject)
        
        state = {
            "iteration": 0,
            "max_iterations": 5,
            "injects": mock_injects,
            "errors": [],
            "current_phase": CrisisPhase.NORMAL_OPERATION,
            "workflow_logs": []
        }
        
        result = workflow._should_continue(state)
        assert result == "end"
    
    def test_should_refine_with_no_validation(self, workflow):
        """Testet _should_refine ohne Validation."""
        state = {
            "validation_result": None,
            "draft_inject": None,
            "metadata": {}
        }
        
        result = workflow._should_refine(state)
        assert result == "update"


class TestInteractiveMode:
    """Tests für interaktiven Modus."""
    
    def test_should_ask_decision_with_no_injects(self, workflow):
        """Testet _should_ask_decision wenn keine Injects vorhanden."""
        workflow.interactive_mode = True
        
        state = {
            "iteration": 0,
            "injects": [],
            "max_iterations": 5,
            "current_phase": CrisisPhase.NORMAL_OPERATION,
            "interactive_mode": True,
            "user_decisions": [],
            "system_state": {},
            "workflow_logs": []
        }
        
        result = workflow._should_ask_decision(state)
        assert result == "continue"
    
    def test_should_ask_decision_at_decision_point(self, workflow):
        """Testet _should_ask_decision an Decision-Point."""
        workflow.interactive_mode = True
        
        from state_models import Inject, InjectModality, TechnicalMetadata
        
        # Erstelle 2 Mock-Injects (Decision-Point)
        mock_injects = []
        for i in range(2):
            inject = Inject(
                inject_id=f"INJ-{i+1:03d}",
                time_offset=f"T+{i:02d}:00",
                phase=CrisisPhase.NORMAL_OPERATION,
                source="Test",
                target="Test",
                modality=InjectModality.SIEM_ALERT,
                content="Test content",
                technical_metadata=TechnicalMetadata(
                    mitre_id="T1110",
                    affected_assets=["SRV-001"],
                    severity="Medium"
                )
            )
            mock_injects.append(inject)
        
        state = {
            "iteration": 0,
            "injects": mock_injects,
            "max_iterations": 5,
            "current_phase": CrisisPhase.NORMAL_OPERATION,
            "interactive_mode": True,
            "user_decisions": [],
            "system_state": {},
            "workflow_logs": []
        }
        
        result = workflow._should_ask_decision(state)
        assert result == "decision"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


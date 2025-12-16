"""
LangGraph State Schema für den DORA-Szenariengenerator.

Definiert den State, der zwischen den Agenten-Nodes im Workflow
übergeben wird.
"""

from typing import TypedDict, List, Optional, Dict, Any
from datetime import datetime
from state_models import (
    Inject,
    ScenarioState,
    CrisisPhase,
    ScenarioType,
    ValidationResult
)


class WorkflowState(TypedDict):
    """
    State für den LangGraph Workflow.
    
    Wird zwischen den Nodes (Agenten) übergeben und enthält
    alle relevanten Informationen für die Szenario-Generierung.
    """
    # Szenario-Metadaten
    scenario_id: str
    scenario_type: ScenarioType
    current_phase: CrisisPhase
    
    # Generierte Injects
    injects: List[Inject]
    
    # Aktueller Systemzustand (aus Neo4j)
    system_state: Dict[str, Any]  # Entitäten und deren Status
    
    # Workflow-Kontrolle
    iteration: int  # Aktuelle Iteration
    max_iterations: int  # Maximale Anzahl Injects
    
    # Agenten-Outputs
    manager_plan: Optional[Dict[str, Any]]  # Storyline vom Manager Agent
    selected_action: Optional[Dict[str, Any]]  # Ausgewählte Aktion (MITRE TTP)
    draft_inject: Optional[Inject]  # Roher Inject vom Generator
    validation_result: Optional[ValidationResult]  # Validierung vom Critic
    
    # Intel & Kontext
    available_ttps: List[Dict[str, Any]]  # Verfügbare TTPs vom Intel Agent
    historical_context: List[Dict[str, Any]]  # Vorherige Injects für Konsistenz
    
    # Fehlerbehandlung
    errors: List[str]
    warnings: List[str]
    
    # Metadaten
    start_time: datetime
    metadata: Dict[str, Any]
    
    # Workflow-Logs für Dashboard
    workflow_logs: List[Dict[str, Any]]  # Logs von jedem Node
    agent_decisions: List[Dict[str, Any]]  # Entscheidungen der Agenten
    
    # Interaktive Entscheidungen
    pending_decision: Optional[Dict[str, Any]]  # Aktuell ausstehende Benutzer-Entscheidung
    user_decisions: List[Dict[str, Any]]  # Alle getroffenen Benutzer-Entscheidungen
    end_condition: Optional[str]  # Aktuelle End-Bedingung (FATAL, VICTORY, NORMAL_END, CONTINUE)
    interactive_mode: bool  # Ob interaktiver Modus aktiviert ist


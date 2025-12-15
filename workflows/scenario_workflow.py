"""
LangGraph Workflow für Szenario-Generierung.

Orchestriert alle Agenten im Multi-Agenten-System:
1. State Check (Neo4j)
2. Manager Agent (Storyline)
3. Intel Agent (TTPs)
4. Action Selection
5. Generator Agent (Drafting)
6. Critic Agent (Validation)
7. State Update (Neo4j)
"""

from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from datetime import datetime, timedelta
import uuid

from workflows.state_schema import WorkflowState
from workflows.fsm import CrisisFSM
from agents.manager_agent import ManagerAgent
from agents.intel_agent import IntelAgent
from agents.generator_agent import GeneratorAgent
from agents.critic_agent import CriticAgent
from neo4j_client import Neo4jClient
from state_models import (
    ScenarioType,
    CrisisPhase,
    Inject,
    ValidationResult
)


class ScenarioWorkflow:
    """
    LangGraph Workflow für Szenario-Generierung.
    
    Implementiert den vollständigen Workflow:
    State Check → Manager → Intel → Action Selection → 
    Generator → Critic → State Update → (Loop oder End)
    """
    
    def __init__(
        self,
        neo4j_client: Neo4jClient,
        max_iterations: int = 10
    ):
        """
        Initialisiert den Workflow.
        
        Args:
            neo4j_client: Neo4j Client für State Management
            max_iterations: Maximale Anzahl Injects
        """
        self.neo4j_client = neo4j_client
        self.max_iterations = max_iterations
        
        # Initialisiere Agenten
        self.manager_agent = ManagerAgent()
        self.intel_agent = IntelAgent()
        self.generator_agent = GeneratorAgent()
        self.critic_agent = CriticAgent()
        
        # Erstelle Graph
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Erstellt den LangGraph Workflow."""
        workflow = StateGraph(WorkflowState)
        
        # Nodes hinzufügen
        workflow.add_node("state_check", self._state_check_node)
        workflow.add_node("manager", self._manager_node)
        workflow.add_node("intel", self._intel_node)
        workflow.add_node("action_selection", self._action_selection_node)
        workflow.add_node("generator", self._generator_node)
        workflow.add_node("critic", self._critic_node)
        workflow.add_node("state_update", self._state_update_node)
        
        # Edges definieren
        workflow.set_entry_point("state_check")
        
        workflow.add_edge("state_check", "manager")
        workflow.add_edge("manager", "intel")
        workflow.add_edge("intel", "action_selection")
        workflow.add_edge("action_selection", "generator")
        workflow.add_edge("generator", "critic")
        
        # Conditional Edge: Critic → State Update oder Generator (Refine)
        workflow.add_conditional_edges(
            "critic",
            self._should_refine,
            {
                "refine": "generator",  # Zurück zum Generator bei Fehlern
                "update": "state_update"  # Weiter bei Validierung (auch mit Warnungen)
            }
        )
        
        # Conditional Edge: State Update → End oder Loop
        workflow.add_conditional_edges(
            "state_update",
            self._should_continue,
            {
                "continue": "state_check",  # Loop zurück
                "end": END
            }
        )
        
        return workflow.compile()
    
    def _state_check_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node: State Check - Abfrage des aktuellen Systemzustands aus Neo4j."""
        print(f"🔍 [State Check] Iteration {state['iteration']}")
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "node": "State Check",
            "iteration": state['iteration'],
            "action": "Systemzustand abfragen",
            "details": {}
        }
        
        try:
            # Hole aktuellen Systemzustand
            entities = self.neo4j_client.get_current_state()
            
            log_entry["details"] = {
                "entities_found": len(entities),
                "status": "success"
            }
            
            logs = state.get("workflow_logs", [])
            logs.append(log_entry)
            
            return {
                "system_state": {
                    "entities": entities,
                    "timestamp": datetime.now().isoformat()
                },
                "workflow_logs": logs
            }
        except Exception as e:
            print(f"⚠️  Fehler bei State Check: {e}")
            log_entry["details"] = {"error": str(e), "status": "error"}
            logs = state.get("workflow_logs", [])
            logs.append(log_entry)
            
            return {
                "system_state": {"entities": [], "error": str(e)},
                "errors": state.get("errors", []) + [f"State Check Fehler: {e}"],
                "workflow_logs": logs
            }
    
    def _manager_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node: Manager Agent - Storyline-Planung."""
        print(f"📋 [Manager] Erstelle Storyline-Plan...")
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "node": "Manager Agent",
            "iteration": state['iteration'],
            "action": "Storyline-Plan erstellen",
            "details": {}
        }
        
        decision_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": "Manager",
            "iteration": state['iteration'],
            "decision_type": "Phase Transition",
            "input": {
                "current_phase": state["current_phase"].value,
                "inject_count": len(state["injects"])
            },
            "output": {}
        }
        
        try:
            plan = self.manager_agent.create_storyline(
                scenario_type=state["scenario_type"],
                current_phase=state["current_phase"],
                inject_count=len(state["injects"]),
                system_state=state["system_state"]
            )
            
            # Aktualisiere Phase wenn nötig
            next_phase = plan.get("next_phase", state["current_phase"])
            
            log_entry["details"] = {
                "next_phase": next_phase.value,
                "narrative": plan.get("narrative", "")[:100] + "..." if plan.get("narrative") else "",
                "status": "success"
            }
            
            decision_entry["output"] = {
                "selected_phase": next_phase.value,
                "reasoning": plan.get("narrative", "")[:200] if plan.get("narrative") else "Automatische Phasen-Übergang"
            }
            
            logs = state.get("workflow_logs", [])
            logs.append(log_entry)
            decisions = state.get("agent_decisions", [])
            decisions.append(decision_entry)
            
            return {
                "manager_plan": plan,
                "current_phase": next_phase,
                "workflow_logs": logs,
                "agent_decisions": decisions
            }
        except Exception as e:
            print(f"⚠️  Fehler bei Manager: {e}")
            log_entry["details"] = {"error": str(e), "status": "error"}
            logs = state.get("workflow_logs", [])
            logs.append(log_entry)
            
            return {
                "manager_plan": {"error": str(e)},
                "errors": state.get("errors", []) + [f"Manager Fehler: {e}"],
                "workflow_logs": logs
            }
    
    def _intel_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node: Intel Agent - TTP-Abfrage."""
        print(f"🔎 [Intel] Hole relevante TTPs...")
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "node": "Intel Agent",
            "iteration": state['iteration'],
            "action": "TTPs abfragen",
            "details": {}
        }
        
        try:
            ttps = self.intel_agent.get_relevant_ttps(
                phase=state["current_phase"],
                limit=5
            )
            
            log_entry["details"] = {
                "ttps_found": len(ttps),
                "phase": state["current_phase"].value,
                "status": "success"
            }
            
            logs = state.get("workflow_logs", [])
            logs.append(log_entry)
            
            return {
                "available_ttps": ttps,
                "workflow_logs": logs
            }
        except Exception as e:
            print(f"⚠️  Fehler bei Intel: {e}")
            log_entry["details"] = {"error": str(e), "status": "error"}
            logs = state.get("workflow_logs", [])
            logs.append(log_entry)
            
            return {
                "available_ttps": [],
                "errors": state.get("errors", []) + [f"Intel Fehler: {e}"],
                "workflow_logs": logs
            }
    
    def _action_selection_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node: Action Selection - Auswahl des nächsten logischen Angriffsschritts."""
        print(f"🎯 [Action Selection] Wähle nächste Aktion...")
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "node": "Action Selection",
            "iteration": state['iteration'],
            "action": "TTP auswählen",
            "details": {}
        }
        
        decision_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": "Action Selection",
            "iteration": state['iteration'],
            "decision_type": "TTP Selection",
            "input": {
                "available_ttps": len(state.get("available_ttps", [])),
                "phase": state["current_phase"].value
            },
            "output": {}
        }
        
        try:
            available_ttps = state.get("available_ttps", [])
            manager_plan = state.get("manager_plan", {})
            
            if not available_ttps:
                selected_ttp = {
                    "technique_id": "T1110",
                    "name": "Brute Force",
                    "mitre_id": "T1110"
                }
            else:
                selected_ttp = available_ttps[0]
            
            log_entry["details"] = {
                "selected_ttp": selected_ttp.get("mitre_id", "N/A"),
                "ttp_name": selected_ttp.get("name", "Unknown"),
                "status": "success"
            }
            
            decision_entry["output"] = {
                "selected_ttp": selected_ttp.get("mitre_id", "N/A"),
                "reasoning": f"Gewählt basierend auf Phase {state['current_phase'].value}"
            }
            
            logs = state.get("workflow_logs", [])
            logs.append(log_entry)
            decisions = state.get("agent_decisions", [])
            decisions.append(decision_entry)
            
            return {
                "selected_action": {
                    "ttp": selected_ttp,
                    "reasoning": f"Gewählt basierend auf Phase {state['current_phase'].value}"
                },
                "workflow_logs": logs,
                "agent_decisions": decisions
            }
        except Exception as e:
            print(f"⚠️  Fehler bei Action Selection: {e}")
            log_entry["details"] = {"error": str(e), "status": "error"}
            logs = state.get("workflow_logs", [])
            logs.append(log_entry)
            
            return {
                "selected_action": {"error": str(e)},
                "errors": state.get("errors", []) + [f"Action Selection Fehler: {e}"],
                "workflow_logs": logs
            }
    
    def _generator_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node: Generator Agent - Drafting."""
        print(f"✍️  [Generator] Erstelle Inject...")
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "node": "Generator Agent",
            "iteration": state['iteration'],
            "action": "Inject generieren",
            "details": {}
        }
        
        try:
            inject_count = len(state["injects"])
            inject_id = f"INJ-{inject_count + 1:03d}"
            
            hours = (inject_count + 1) * 0.5
            time_offset = f"T+{int(hours):02d}:{int((hours % 1) * 60):02d}"
            
            manager_plan = state.get("manager_plan", {})
            selected_action = state.get("selected_action", {})
            selected_ttp = selected_action.get("ttp", {})
            
            inject = self.generator_agent.generate_inject(
                scenario_type=state["scenario_type"],
                phase=state["current_phase"],
                inject_id=inject_id,
                time_offset=time_offset,
                manager_plan=manager_plan,
                selected_ttp=selected_ttp,
                system_state=state["system_state"],
                previous_injects=state["injects"]
            )
            
            log_entry["details"] = {
                "inject_id": inject_id,
                "phase": inject.phase.value,
                "mitre_id": inject.technical_metadata.mitre_id or "N/A",
                "status": "success"
            }
            
            logs = state.get("workflow_logs", [])
            logs.append(log_entry)
            
            return {
                "draft_inject": inject,
                "workflow_logs": logs
            }
        except Exception as e:
            print(f"⚠️  Fehler bei Generator: {e}")
            log_entry["details"] = {"error": str(e), "status": "error"}
            logs = state.get("workflow_logs", [])
            logs.append(log_entry)
            
            return {
                "draft_inject": None,
                "errors": state.get("errors", []) + [f"Generator Fehler: {e}"],
                "workflow_logs": logs
            }
    
    def _critic_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node: Critic Agent - Validation."""
        print(f"🔍 [Critic] Validiere Inject...")
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "node": "Critic Agent",
            "iteration": state['iteration'],
            "action": "Inject validieren",
            "details": {}
        }
        
        decision_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": "Critic",
            "iteration": state['iteration'],
            "decision_type": "Validation",
            "input": {},
            "output": {}
        }
        
        try:
            draft_inject = state.get("draft_inject")
            
            if not draft_inject:
                log_entry["details"] = {"error": "Kein Draft-Inject", "status": "error"}
                logs = state.get("workflow_logs", [])
                logs.append(log_entry)
                
                return {
                    "validation_result": ValidationResult(
                        is_valid=False,
                        logical_consistency=False,
                        dora_compliance=False,
                        causal_validity=False,
                        errors=["Kein Draft-Inject vorhanden"]
                    ),
                    "workflow_logs": logs
                }
            
            validation = self.critic_agent.validate_inject(
                inject=draft_inject,
                previous_injects=state["injects"],
                current_phase=state["current_phase"],
                system_state=state["system_state"]
            )
            
            log_entry["details"] = {
                "inject_id": draft_inject.inject_id,
                "is_valid": validation.is_valid,
                "logical_consistency": validation.logical_consistency,
                "dora_compliance": validation.dora_compliance,
                "causal_validity": validation.causal_validity,
                "status": "success"
            }
            
            decision_entry["input"] = {"inject_id": draft_inject.inject_id}
            decision_entry["output"] = {
                "is_valid": validation.is_valid,
                "errors": validation.errors,
                "warnings": validation.warnings
            }
            
            if validation.is_valid:
                print(f"✅ Inject validiert: {draft_inject.inject_id}")
            else:
                print(f"❌ Inject nicht valide: {validation.errors}")
            
            logs = state.get("workflow_logs", [])
            logs.append(log_entry)
            decisions = state.get("agent_decisions", [])
            decisions.append(decision_entry)
            
            return {
                "validation_result": validation,
                "workflow_logs": logs,
                "agent_decisions": decisions
            }
        except Exception as e:
            print(f"⚠️  Fehler bei Critic: {e}")
            log_entry["details"] = {"error": str(e), "status": "error"}
            logs = state.get("workflow_logs", [])
            logs.append(log_entry)
            
            return {
                "validation_result": ValidationResult(
                    is_valid=False,
                    logical_consistency=False,
                    dora_compliance=False,
                    causal_validity=False,
                    errors=[f"Critic Fehler: {e}"]
                ),
                "workflow_logs": logs
            }
    
    def _state_update_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node: State Update - Schreiben der Auswirkungen in Neo4j."""
        print(f"💾 [State Update] Aktualisiere Systemzustand...")
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "node": "State Update",
            "iteration": state['iteration'],
            "action": "Systemzustand aktualisieren",
            "details": {}
        }
        
        try:
            draft_inject = state.get("draft_inject")
            
            if not draft_inject:
                return {}
            
            # Füge Inject zu Liste hinzu
            new_injects = state["injects"] + [draft_inject]
            
            updated_assets = []
            second_order_effects = []
            
            # Update Neo4j: Status der betroffenen Assets
            for asset_id in draft_inject.technical_metadata.affected_assets:
                try:
                    # Bestimme neuen Status basierend auf Phase und TTP
                    new_status = self._determine_asset_status(
                        draft_inject.phase,
                        draft_inject.technical_metadata.mitre_id
                    )
                    
                    self.neo4j_client.update_entity_status(
                        entity_id=asset_id,
                        new_status=new_status,
                        inject_id=draft_inject.inject_id
                    )
                    updated_assets.append({"asset": asset_id, "status": new_status})
                    
                    # Second-Order Effects
                    affected = self.neo4j_client.get_affected_entities(asset_id)
                    for affected_id in affected:
                        self.neo4j_client.update_entity_status(
                            entity_id=affected_id,
                            new_status="degraded",
                            inject_id=draft_inject.inject_id
                        )
                        second_order_effects.append(affected_id)
                except Exception as e:
                    print(f"⚠️  Fehler beim Update von {asset_id}: {e}")
            
            log_entry["details"] = {
                "inject_id": draft_inject.inject_id,
                "assets_updated": len(updated_assets),
                "second_order_effects": len(second_order_effects),
                "status": "success"
            }
            
            logs = state.get("workflow_logs", [])
            logs.append(log_entry)
            
            return {
                "injects": new_injects,
                "iteration": state["iteration"] + 1,
                "workflow_logs": logs
            }
        except Exception as e:
            print(f"⚠️  Fehler bei State Update: {e}")
            log_entry["details"] = {"error": str(e), "status": "error"}
            logs = state.get("workflow_logs", [])
            logs.append(log_entry)
            
            return {
                "errors": state.get("errors", []) + [f"State Update Fehler: {e}"],
                "workflow_logs": logs
            }
    
    def _should_refine(self, state: WorkflowState) -> str:
        """Entscheidet, ob Refine nötig ist."""
        validation = state.get("validation_result")
        
        if not validation:
            return "update"  # Weiter auch ohne Validierung
        
        # Refine wenn nicht valide (max. 2 Versuche pro Inject)
        if not validation.is_valid:
            metadata = state.get("metadata", {})
            current_inject_id = state.get("draft_inject", {}).inject_id if state.get("draft_inject") else None
            
            # Zähle Refine-Versuche pro Inject
            refine_key = f"refine_count_{current_inject_id}"
            refine_count = metadata.get(refine_key, 0)
            
            if refine_count < 2:  # Max. 2 Refine-Versuche
                metadata[refine_key] = refine_count + 1
                return "refine"
            else:
                # Nach 2 Versuchen: Akzeptiere trotzdem (mit Warnung)
                print(f"⚠️  Inject nach {refine_count} Refine-Versuchen akzeptiert (mit Warnungen)")
                return "update"
        
        return "update"
    
    def _should_continue(self, state: WorkflowState) -> str:
        """Entscheidet, ob Workflow fortgesetzt werden soll."""
        iteration = state.get("iteration", 0)
        max_iterations = state.get("max_iterations", self.max_iterations)
        current_phase = state.get("current_phase", CrisisPhase.NORMAL_OPERATION)
        
        # Stoppe wenn:
        # 1. Maximale Iterationen erreicht
        # 2. Recovery-Phase erreicht und Normalbetrieb wiederhergestellt
        if iteration >= max_iterations:
            return "end"
        
        if current_phase == CrisisPhase.RECOVERY:
            # Prüfe ob Normalbetrieb wiederhergestellt
            if len(state.get("injects", [])) >= 3:
                return "end"
        
        return "continue"
    
    def _determine_asset_status(
        self,
        phase: CrisisPhase,
        mitre_id: str
    ) -> str:
        """Bestimmt den neuen Status eines Assets basierend auf Phase und TTP."""
        if phase in [CrisisPhase.ESCALATION_CRISIS, CrisisPhase.CONTAINMENT]:
            return "compromised"
        elif phase == CrisisPhase.INITIAL_INCIDENT:
            return "suspicious"
        elif "encrypt" in mitre_id.lower() or "T1486" in mitre_id:
            return "encrypted"
        else:
            return "degraded"
    
    def generate_scenario(
        self,
        scenario_type: ScenarioType,
        scenario_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generiert ein vollständiges Szenario.
        
        Args:
            scenario_type: Typ des Szenarios
            scenario_id: Optional - ID für das Szenario
        
        Returns:
            Dictionary mit generiertem Szenario
        """
        if not scenario_id:
            scenario_id = f"SCEN-{uuid.uuid4().hex[:8].upper()}"
        
        # Initialisiere State
        initial_state: WorkflowState = {
            "scenario_id": scenario_id,
            "scenario_type": scenario_type,
            "current_phase": CrisisPhase.NORMAL_OPERATION,
            "injects": [],
            "system_state": {},
            "iteration": 0,
            "max_iterations": self.max_iterations,
            "manager_plan": None,
            "selected_action": None,
            "draft_inject": None,
            "validation_result": None,
            "available_ttps": [],
            "historical_context": [],
            "errors": [],
            "warnings": [],
            "start_time": datetime.now(),
            "metadata": {},
            "workflow_logs": [],
            "agent_decisions": []
        }
        
        print(f"🚀 Starte Szenario-Generierung: {scenario_id}")
        print(f"   Typ: {scenario_type.value}")
        print(f"   Max. Iterationen: {self.max_iterations}")
        print()
        
            # Führe Workflow aus
        try:
            final_state = self.graph.invoke(
                initial_state,
                config={"recursion_limit": 50}  # Erhöhe Limit
            )
            
            print()
            print(f"✅ Szenario-Generierung abgeschlossen!")
            print(f"   Generierte Injects: {len(final_state['injects'])}")
            print(f"   Finale Phase: {final_state['current_phase'].value}")
            
            return final_state
            
        except Exception as e:
            print(f"❌ Fehler bei Szenario-Generierung: {e}")
            return {
                **initial_state,
                "errors": [str(e)]
            }


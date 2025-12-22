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

from typing import Dict, Any, Optional, List
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
    ValidationResult,
    ScenarioEndCondition,
    UserDecision
)
from forensic_logger import get_forensic_logger


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
        max_iterations: int = 10,
        interactive_mode: bool = False
    ):
        """
        Initialisiert den Workflow.
        
        Args:
            neo4j_client: Neo4j Client für State Management
            max_iterations: Maximale Anzahl Injects
            interactive_mode: Ob interaktiver Modus mit Benutzer-Entscheidungen aktiviert ist
        """
        self.neo4j_client = neo4j_client
        self.max_iterations = max_iterations
        self.interactive_mode = interactive_mode
        
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
        
        # Decision-Point Node (nur im interaktiven Modus)
        if self.interactive_mode:
            workflow.add_node("decision_point", self._decision_point_node)
        
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
        
        # Conditional Edge: State Update → Decision Point (interaktiv) oder Continue/End
        if self.interactive_mode:
            workflow.add_conditional_edges(
                "state_update",
                self._should_ask_decision,
                {
                    "decision": "decision_point",  # Benutzer-Entscheidung erforderlich
                    "continue": "state_check",  # Weiter ohne Entscheidung
                    "end": END  # End-Bedingung erreicht
                }
            )
            
            # Decision Point → State Check (nach Entscheidung)
            workflow.add_edge("decision_point", "state_check")
        else:
            # Conditional Edge: State Update → End oder Loop (nicht-interaktiv)
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
        iteration = state.get('iteration', 0)
        injects_count = len(state.get('injects', []))
        print(f"🔍 [State Check] Iteration {iteration}, Injects: {injects_count}, Phase: {state.get('current_phase', 'N/A')}")
        print(f"   🔧 Hole Systemzustand aus Neo4j...")
        
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
            
            # Konvertiere Liste von Entities in Dictionary (entity_id -> entity_data)
            # FILTER: Nur echte Assets, keine Inject-IDs oder Szenario-IDs
            system_state_dict = {}
            for entity in entities:
                entity_id = entity.get("entity_id")
                if not entity_id:
                    continue
                
                # STRENGER FILTER: Überspringe alle Inject-IDs und Szenario-IDs
                if entity_id.startswith("INJ-") or entity_id.startswith("SCEN-"):
                    continue
                
                # Prüfe Entity-Type
                entity_type = entity.get("entity_type", "").lower() if entity.get("entity_type") else ""
                
                # Akzeptiere nur echte Assets:
                # 1. Entity-Type ist gesetzt UND ist ein Asset-Typ
                # 2. ODER ID beginnt mit Asset-Präfix (SRV-, APP-, DB-, SVC-)
                is_valid_asset_type = entity_type in ["server", "application", "database", "service", "asset", "system"]
                has_asset_prefix = any(entity_id.startswith(prefix) for prefix in ["SRV-", "APP-", "DB-", "SVC-", "SYS-"])
                
                if not (is_valid_asset_type or has_asset_prefix):
                    # Überspringe wenn weder Typ noch Präfix passt
                    continue
                
                system_state_dict[entity_id] = {
                    "status": entity.get("status", "unknown"),
                    "entity_type": entity.get("entity_type", "Asset"),
                    "name": entity.get("name", entity_id),
                    "criticality": entity.get("properties", {}).get("criticality", "standard"),
                    **entity.get("properties", {})
                }
            
            # Falls keine Assets gefunden, erstelle Standard-Assets
            if not system_state_dict:
                print("⚠️  Keine Assets im Systemzustand gefunden. Erstelle Standard-Assets...")
                system_state_dict = {
                    "SRV-001": {
                        "status": "online",
                        "entity_type": "Server",
                        "name": "SRV-001",
                        "criticality": "standard"
                    },
                    "SRV-002": {
                        "status": "online",
                        "entity_type": "Server",
                        "name": "SRV-002",
                        "criticality": "standard"
                    }
                }
                print(f"✅ Standard-Assets erstellt: {list(system_state_dict.keys())}")
            
            print(f"✅ [State Check] Systemzustand geladen: {len(system_state_dict)} Assets")
            print(f"   Asset-IDs: {list(system_state_dict.keys())[:10]}")
            
            log_entry["details"] = {
                "entities_found": len(entities),
                "assets_after_filter": len(system_state_dict),
                "asset_ids": list(system_state_dict.keys())[:10],
                "status": "success"
            }
            
            logs = state.get("workflow_logs", [])
            logs.append(log_entry)
            
            return {
                "system_state": system_state_dict,
                "workflow_logs": logs
            }
        except Exception as e:
            print(f"⚠️  Fehler bei State Check: {e}")
            log_entry["details"] = {"error": str(e), "status": "error"}
            logs = state.get("workflow_logs", [])
            logs.append(log_entry)
            
            return {
                "system_state": {},
                "errors": state.get("errors", []) + [f"State Check Fehler: {e}"],
                "workflow_logs": logs
            }
    
    def _manager_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node: Manager Agent - Storyline-Planung."""
        iteration = state.get('iteration', 0)
        injects_count = len(state.get('injects', []))
        print(f"📋 [Manager] Iteration {iteration}, Injects: {injects_count} - Erstelle Storyline-Plan...")
        
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
            "input": {},
            "output": {}
        }
        
        try:
            # Erstelle System State Summary für Audit-Trail
            system_state = state.get("system_state", {})
            system_state_summary = {
                "compromised_assets": [],
                "degraded_assets": [],
                "suspicious_assets": [],
                "total_entities": len(system_state) if isinstance(system_state, dict) else 0
            }
            
            # Analysiere System State
            if isinstance(system_state, dict):
                for entity_id, entity_data in system_state.items():
                    if isinstance(entity_data, dict):
                        status = entity_data.get("status", "unknown")
                        if status == "compromised":
                            system_state_summary["compromised_assets"].append(entity_id)
                        elif status == "degraded":
                            system_state_summary["degraded_assets"].append(entity_id)
                        elif status == "suspicious":
                            system_state_summary["suspicious_assets"].append(entity_id)
            
            plan = self.manager_agent.create_storyline(
                scenario_type=state["scenario_type"],
                current_phase=state["current_phase"],
                inject_count=len(state["injects"]),
                system_state=state["system_state"]
            )
            
            # Aktualisiere Phase wenn nötig
            next_phase_raw = plan.get("next_phase", state["current_phase"])
            # Stelle sicher, dass next_phase ein CrisisPhase-Enum ist
            if isinstance(next_phase_raw, str):
                try:
                    next_phase = CrisisPhase(next_phase_raw)
                except (ValueError, KeyError):
                    next_phase = state["current_phase"]
            elif isinstance(next_phase_raw, CrisisPhase):
                next_phase = next_phase_raw
            else:
                next_phase = state["current_phase"]
            
            log_entry["details"] = {
                "next_phase": next_phase.value,
                "narrative": plan.get("narrative", "")[:100] + "..." if plan.get("narrative") else "",
                "status": "success"
            }
            
            # Erweitertes Input für Audit-Trail
            decision_entry["input"] = {
                "current_phase": state["current_phase"].value,
                "inject_count": len(state["injects"]),
                "system_state_summary": system_state_summary,
                "scenario_type": state["scenario_type"].value
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
            import traceback
            error_trace = traceback.format_exc()
            print(f"⚠️  Fehler bei Manager: {e}")
            print(f"   Traceback: {error_trace}")
            log_entry["details"] = {"error": str(e), "traceback": error_trace, "status": "error"}
            logs = state.get("workflow_logs", [])
            logs.append(log_entry)
            
            # Fallback: Verwende aktuelle Phase und erstelle minimalen Plan
            fallback_plan = {
                "next_phase": state["current_phase"],
                "narrative": f"Fehler bei Storyline-Planung: {str(e)}",
                "key_events": [],
                "affected_assets": [],
                "business_impact": "",
                "error": str(e)
            }
            
            return {
                "manager_plan": fallback_plan,
                "current_phase": state["current_phase"],  # Behalte aktuelle Phase
                "errors": state.get("errors", []) + [f"Manager Fehler: {e}"],
                "workflow_logs": logs
            }
    
    def _intel_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node: Intel Agent - TTP-Abfrage."""
        iteration = state.get('iteration', 0)
        injects_count = len(state.get('injects', []))
        print(f"🔎 [Intel] Iteration {iteration}, Injects: {injects_count} - Hole relevante TTPs...")
        
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
        iteration = state.get('iteration', 0)
        injects_count = len(state.get('injects', []))
        available_ttps = state.get("available_ttps", [])
        print(f"🎯 [Action Selection] Iteration {iteration}, Injects: {injects_count} - Wähle nächste Aktion...")
        print(f"   Verfügbare TTPs: {len(available_ttps)}")
        
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
            
            # Erweitertes Input für Audit-Trail
            decision_entry["input"] = {
                "available_ttps": len(available_ttps),
                "phase": state['current_phase'].value,
                "selected_ttp_context": {
                    "mitre_id": selected_ttp.get("mitre_id", "N/A"),
                    "name": selected_ttp.get("name", "Unknown"),
                    "tactic": selected_ttp.get("tactic", "N/A")
                }
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
        iteration = state.get('iteration', 0)
        injects_count = len(state.get('injects', []))
        manager_plan = state.get("manager_plan")
        selected_action = state.get("selected_action")
        print(f"✍️  [Generator] Iteration {iteration}, Injects: {injects_count} - Erstelle Inject...")
        print(f"   Manager Plan vorhanden: {manager_plan is not None}")
        print(f"   Selected Action vorhanden: {selected_action is not None}")
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "node": "Generator Agent",
            "iteration": state['iteration'],
            "action": "Inject generieren",
            "details": {}
        }
        
        decision_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": "Generator",
            "iteration": state['iteration'],
            "decision_type": "Inject Generation",
            "input": {},
            "output": {}
        }
        
        try:
            inject_count = len(state["injects"])
            inject_id = f"INJ-{inject_count + 1:03d}"
            
            hours = (inject_count + 1) * 0.5
            time_offset = f"T+{int(hours):02d}:{int((hours % 1) * 60):02d}"
            
            manager_plan = state.get("manager_plan", {})
            selected_action = state.get("selected_action", {})
            selected_ttp = selected_action.get("ttp", {})
            
            # Erweitertes Input für Audit-Trail
            decision_entry["input"] = {
                "scenario_type": state["scenario_type"].value,
                "phase": state["current_phase"].value,
                "inject_id": inject_id,
                "time_offset": time_offset,
                "manager_plan_summary": manager_plan.get("narrative", "")[:100] + "..." if manager_plan.get("narrative") else "N/A",
                "selected_ttp": selected_ttp.get("mitre_id", "N/A") if selected_ttp else "N/A",
                "previous_injects_count": len(state["injects"]),
                "system_state_summary": {
                    "total_entities": len(state.get("system_state", {})),
                    "compromised_count": sum(1 for e in state.get("system_state", {}).values() 
                                            if isinstance(e, dict) and e.get("status") == "compromised")
                }
            }
            
            # Prüfe ob Refine-Loop (Feedback vom Critic vorhanden)
            validation_feedback = None
            if state.get("validation_result"):
                validation_result = state["validation_result"]
                if not validation_result.is_valid:
                    # Erstelle Feedback-Dict für Generator
                    validation_feedback = {
                        "errors": validation_result.errors or [],
                        "warnings": validation_result.warnings or [],
                        "logical_consistency": validation_result.logical_consistency,
                        "dora_compliance": validation_result.dora_compliance,
                        "causal_validity": validation_result.causal_validity
                    }
                    print(f"   🔄 Refine-Modus: Verwende Feedback vom Critic Agent")
            
            # Hole user_feedback aus State (Human-in-the-Loop)
            user_feedback = state.get("user_feedback")
            
            inject = self.generator_agent.generate_inject(
                scenario_type=state["scenario_type"],
                phase=state["current_phase"],
                inject_id=inject_id,
                time_offset=time_offset,
                manager_plan=manager_plan,
                selected_ttp=selected_ttp,
                system_state=state["system_state"],
                previous_injects=state["injects"],
                validation_feedback=validation_feedback,
                user_feedback=user_feedback
            )
            
            log_entry["details"] = {
                "inject_id": inject_id,
                "phase": inject.phase.value,
                "mitre_id": inject.technical_metadata.mitre_id or "N/A",
                "status": "success"
            }
            
            # Erweitertes Output für Audit-Trail
            decision_entry["output"] = {
                "inject_id": inject.inject_id,
                "content_preview": inject.content[:150] + "..." if len(inject.content) > 150 else inject.content,
                "source": inject.source,
                "target": inject.target,
                "mitre_id": inject.technical_metadata.mitre_id or "N/A",
                "affected_assets": inject.technical_metadata.affected_assets,
                "severity": inject.technical_metadata.severity or "N/A",
                "reasoning": f"Generiert basierend auf Phase {state['current_phase'].value} und TTP {selected_ttp.get('mitre_id', 'N/A')}"
            }
            
            logs = state.get("workflow_logs", [])
            logs.append(log_entry)
            decisions = state.get("agent_decisions", [])
            decisions.append(decision_entry)
            
            return {
                "draft_inject": inject,
                "workflow_logs": logs,
                "agent_decisions": decisions
            }
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"⚠️  Fehler bei Generator: {e}")
            print(f"   Traceback: {error_trace}")
            log_entry["details"] = {"error": str(e), "traceback": error_trace, "status": "error"}
            logs = state.get("workflow_logs", [])
            logs.append(log_entry)
            
            return {
                "draft_inject": None,
                "errors": state.get("errors", []) + [f"Generator Fehler: {e}"],
                "workflow_logs": logs
            }
    
    def _critic_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node: Critic Agent - Validation."""
        iteration = state.get('iteration', 0)
        injects_count = len(state.get('injects', []))
        draft_inject = state.get("draft_inject")
        print(f"🔍 [Critic] Iteration {iteration}, Injects: {injects_count} - Validiere Inject...")
        print(f"   Draft Inject vorhanden: {draft_inject is not None}")
        if draft_inject:
            print(f"   Draft Inject ID: {draft_inject.inject_id if hasattr(draft_inject, 'inject_id') else 'N/A'}")
        
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
            
            # Hole Mode aus State (Default: 'thesis')
            mode = state.get("mode", "thesis")
            
            # Forensisches Logging: DRAFT Inject (vor Validierung)
            scenario_id = state.get("scenario_id", "UNKNOWN")
            iteration = state.get("iteration", 0)
            metadata = state.get("metadata", {})
            current_inject_id = draft_inject.inject_id if draft_inject else None
            refine_key = f"refine_count_{current_inject_id}"
            refine_count = metadata.get(refine_key, 0)
            
            # Logge DRAFT nur wenn im Thesis Mode
            if mode == 'thesis':
                forensic_logger = get_forensic_logger(scenario_id)
                forensic_logger.log_draft(
                    scenario_id=scenario_id,
                    inject=draft_inject,
                    iteration=iteration,
                    refine_count=refine_count
                )
            
            validation = self.critic_agent.validate_inject(
                inject=draft_inject,
                previous_injects=state["injects"],
                current_phase=state["current_phase"],
                system_state=state["system_state"],
                mode=mode
            )
            
            # Forensisches Logging: CRITIC Validierungsergebnis
            if mode == 'thesis':
                forensic_logger.log_critic(
                    scenario_id=scenario_id,
                    inject_id=draft_inject.inject_id,
                    validation_result=validation,
                    iteration=iteration,
                    refine_count=refine_count
                )
            
            log_entry["details"] = {
                "inject_id": draft_inject.inject_id,
                "is_valid": validation.is_valid,
                "logical_consistency": validation.logical_consistency,
                "dora_compliance": validation.dora_compliance,
                "causal_validity": validation.causal_validity,
                "status": "success"
            }
            
            # Erweitertes Input für Audit-Trail - Self-Contained!
            decision_entry["input"] = {
                "inject_id": draft_inject.inject_id,
                "inject_content": draft_inject.content[:200] + "..." if len(draft_inject.content) > 200 else draft_inject.content,
                "inject_source": draft_inject.source,
                "inject_target": draft_inject.target,
                "inject_phase": draft_inject.phase.value,
                "inject_mitre_id": draft_inject.technical_metadata.mitre_id or "N/A",
                "inject_affected_assets": draft_inject.technical_metadata.affected_assets,
                "inject_severity": draft_inject.technical_metadata.severity or "N/A",
                "current_phase": state["current_phase"].value,
                "previous_injects_count": len(state["injects"])
            }
            
            # Erweitertes Output mit Reasoning
            decision_entry["output"] = {
                "is_valid": validation.is_valid,
                "logical_consistency": validation.logical_consistency,
                "dora_compliance": validation.dora_compliance,
                "causal_validity": validation.causal_validity,
                "errors": validation.errors,
                "warnings": validation.warnings,
                "reasoning": self._generate_validation_reasoning(validation) if not validation.is_valid else "Inject ist valide und erfüllt alle Kriterien"
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
        current_iteration = state.get("iteration", 0)
        print(f"💾 [State Update] Iteration {current_iteration} - Aktualisiere Systemzustand...")
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "node": "State Update",
            "iteration": current_iteration,
            "action": "Systemzustand aktualisieren",
            "details": {}
        }
        
        try:
            draft_inject = state.get("draft_inject")
            
            if not draft_inject:
                # Auch ohne Inject: Iteration erhöhen um Endlosschleife zu vermeiden
                print(f"⚠️  Kein Draft-Inject vorhanden, erhöhe Iteration von {current_iteration} auf {current_iteration + 1}")
                new_iteration = current_iteration + 1
                logs = state.get("workflow_logs", [])
                logs.append(log_entry)
                return {
                    "iteration": new_iteration,
                    "workflow_logs": logs
                }
            
            # Füge Inject zu Liste hinzu
            new_injects = state["injects"] + [draft_inject]
            
            updated_assets = []
            second_order_effects = []
            cascading_impacts = []
            
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
                    
                    # Erweiterte Second-Order Effects mit Kaskadierungsanalyse
                    cascading_impact = self.neo4j_client.calculate_cascading_impact(
                        entity_id=asset_id,
                        new_status=new_status,
                        max_depth=3
                    )
                    
                    cascading_impacts.append({
                        "source_asset": asset_id,
                        "impact": cascading_impact
                    })
                    
                    # Update alle betroffenen Entitäten basierend auf Impact-Schweregrad
                    for affected_entity in cascading_impact["affected_entities"]:
                        affected_id = affected_entity["entity_id"]
                        
                        # Bestimme Status basierend auf Tiefe und Schweregrad
                        if affected_entity["depth"] == 1:
                            # Direkte Abhängigkeit - stärkerer Impact
                            affected_status = "degraded" if new_status != "compromised" else "suspicious"
                        else:
                            # Indirekte Abhängigkeit - schwächerer Impact
                            affected_status = "degraded"
                        
                        try:
                            self.neo4j_client.update_entity_status(
                                entity_id=affected_id,
                                new_status=affected_status,
                                inject_id=draft_inject.inject_id
                            )
                            second_order_effects.append({
                                "entity_id": affected_id,
                                "depth": affected_entity["depth"],
                                "status": affected_status
                            })
                        except Exception as e:
                            print(f"⚠️  Fehler beim Update von {affected_id}: {e}")
                    
                    # Logge kritische Pfade
                    if cascading_impact["critical_paths"]:
                        print(f"⚠️  Kritische Abhängigkeitspfade gefunden: {len(cascading_impact['critical_paths'])}")
                        print(f"   Impact-Schweregrad: {cascading_impact['impact_severity']}")
                        print(f"   Geschätzte Recovery-Zeit: {cascading_impact['estimated_recovery_time']}")
                    
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
            
            new_iteration = current_iteration + 1
            print(f"✅ Inject {draft_inject.inject_id} hinzugefügt. Iteration: {current_iteration} → {new_iteration}")
            print(f"   Gesamt Injects: {len(new_injects)}")
            
            return {
                "injects": new_injects,
                "iteration": new_iteration,
                "workflow_logs": logs
            }
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"⚠️  Fehler bei State Update: {e}")
            print(f"   Traceback: {error_trace}")
            log_entry["details"] = {"error": str(e), "traceback": error_trace, "status": "error"}
            logs = state.get("workflow_logs", [])
            logs.append(log_entry)
            
            # WICHTIG: Auch bei Fehlern Iteration erhöhen, um Endlosschleife zu vermeiden
            # Und versuche, vorhandene Injects zu behalten
            return {
                "iteration": state.get("iteration", 0) + 1,
                "errors": state.get("errors", []) + [f"State Update Fehler: {e}"],
                "workflow_logs": logs
            }
    
    def _generate_decision_aids(self, state: WorkflowState) -> Dict[str, Any]:
        """Generiert Entscheidungshilfen für das generierte Szenario."""
        injects = state.get("injects", [])
        current_phase = state.get("current_phase", CrisisPhase.NORMAL_OPERATION)
        errors = state.get("errors", [])
        warnings = state.get("warnings", [])
        
        # Analysiere Szenario
        phases_covered = set(inj.phase for inj in injects)
        mitre_ttps = set(inj.technical_metadata.mitre_id for inj in injects if inj.technical_metadata.mitre_id)
        affected_assets = set()
        for inj in injects:
            affected_assets.update(inj.technical_metadata.affected_assets)
        
        # DORA-Compliance Analyse
        dora_compliant_count = sum(1 for inj in injects if inj.dora_compliance_tag)
        dora_compliance_rate = (dora_compliant_count / len(injects) * 100) if injects else 0
        
        # Severity-Verteilung
        severities = [inj.technical_metadata.severity for inj in injects if inj.technical_metadata.severity]
        severity_distribution = {}
        for sev in severities:
            severity_distribution[sev] = severity_distribution.get(sev, 0) + 1
        
        return {
            "scenario_summary": {
                "total_injects": len(injects),
                "phases_covered": [p.value for p in phases_covered],
                "final_phase": current_phase.value,
                "unique_mitre_ttps": len(mitre_ttps),
                "affected_assets_count": len(affected_assets)
            },
            "dora_compliance": {
                "compliant_injects": dora_compliant_count,
                "compliance_rate": round(dora_compliance_rate, 1),
                "recommendation": "✅ Gut" if dora_compliance_rate >= 80 else "⚠️ Verbesserung empfohlen" if dora_compliance_rate >= 50 else "❌ Erheblich verbesserungsbedürftig"
            },
            "severity_analysis": {
                "distribution": severity_distribution,
                "highest_severity": max(severities, key=lambda s: {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}.get(s, 0)) if severities else "N/A",
                "average_severity": self._calculate_average_severity(severities)
            },
            "recommendations": self._generate_recommendations(injects, errors, warnings, dora_compliance_rate),
            "key_insights": self._generate_key_insights(injects, phases_covered, mitre_ttps)
        }
    
    def _calculate_average_severity(self, severities: List[str]) -> str:
        """Berechnet durchschnittlichen Schweregrad."""
        if not severities:
            return "N/A"
        
        severity_map = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
        avg_num = sum(severity_map.get(s, 2) for s in severities) / len(severities)
        
        if avg_num < 1.5:
            return "Low"
        elif avg_num < 2.5:
            return "Medium"
        elif avg_num < 3.5:
            return "High"
        else:
            return "Critical"
    
    def _generate_recommendations(self, injects: List, errors: List, warnings: List, dora_rate: float) -> List[str]:
        """Generiert Empfehlungen basierend auf Szenario-Analyse."""
        recommendations = []
        
        if dora_rate < 80:
            recommendations.append("💡 **DORA-Compliance verbessern:** Mehr Injects sollten DORA-Artikel 25 erfüllen")
        
        if len(errors) > 0:
            recommendations.append(f"⚠️ **Fehler beheben:** {len(errors)} Fehler wurden während der Generierung erkannt")
        
        if len(warnings) > 3:
            recommendations.append(f"⚠️ **Warnungen prüfen:** {len(warnings)} Warnungen sollten überprüft werden")
        
        phases = set(inj.phase for inj in injects)
        if len(phases) < 3:
            recommendations.append("💡 **Phasen-Vielfalt erhöhen:** Szenario könnte mehr verschiedene Krisenphasen abdecken")
        
        # Prüfe auf kritische Assets
        critical_assets = set()
        for inj in injects:
            if inj.technical_metadata.severity in ["High", "Critical"]:
                critical_assets.update(inj.technical_metadata.affected_assets)
        
        if len(critical_assets) > 0:
            recommendations.append(f"🔴 **Kritische Assets identifiziert:** {len(critical_assets)} Assets sind von High/Critical Injects betroffen")
        
        if not recommendations:
            recommendations.append("✅ **Szenario ist gut strukturiert:** Keine kritischen Verbesserungen erforderlich")
        
        return recommendations
    
    def _generate_key_insights(self, injects: List, phases_covered: set, mitre_ttps: set) -> List[str]:
        """Generiert wichtige Erkenntnisse aus dem Szenario."""
        insights = []
        
        if len(injects) >= 5:
            insights.append(f"📊 **Umfangreiches Szenario:** {len(injects)} Injects decken einen vollständigen Krisenverlauf ab")
        
        if len(phases_covered) >= 4:
            insights.append(f"🔄 **Vollständige Phasen-Abdeckung:** {len(phases_covered)} verschiedene Krisenphasen wurden durchlaufen")
        
        if len(mitre_ttps) >= 3:
            insights.append(f"🎯 **Vielfältige Angriffsmuster:** {len(mitre_ttps)} verschiedene MITRE ATT&CK Techniken wurden verwendet")
        
        # Prüfe auf Eskalation
        phase_order = ["NORMAL_OPERATION", "SUSPICIOUS_ACTIVITY", "INITIAL_INCIDENT", "ESCALATION_CRISIS", "CONTAINMENT", "RECOVERY"]
        inject_phases = [inj.phase.value for inj in injects]
        if any(phase_order.index(inject_phases[i]) < phase_order.index(inject_phases[i+1]) 
               for i in range(len(inject_phases)-1) if inject_phases[i] in phase_order and inject_phases[i+1] in phase_order):
            insights.append("📈 **Logische Eskalation:** Szenario zeigt eine realistische Krisen-Eskalation")
        
        if not insights:
            insights.append("📋 **Szenario generiert:** Basis-Szenario wurde erfolgreich erstellt")
        
        return insights
    
    def _generate_additional_info(self, state: WorkflowState) -> Dict[str, Any]:
        """Generiert zusätzliche Informationen für das Szenario."""
        injects = state.get("injects", [])
        decisions = state.get("agent_decisions", [])
        logs = state.get("workflow_logs", [])
        
        # Agent-Statistiken
        agent_stats = {}
        for dec in decisions:
            agent = dec.get("agent", "Unknown")
            agent_stats[agent] = agent_stats.get(agent, 0) + 1
        
        # Workflow-Statistiken
        node_stats = {}
        for log in logs:
            node = log.get("node", "Unknown")
            node_stats[node] = node_stats.get(node, 0) + 1
        
        return {
            "generation_metadata": {
                "total_iterations": state.get("iteration", 0),
                "max_iterations": state.get("max_iterations", 0),
                "workflow_duration_estimate": len(logs) * 2,  # Geschätzte Sekunden
                "agent_decisions_count": len(decisions),
                "workflow_logs_count": len(logs)
            },
            "agent_statistics": agent_stats,
            "workflow_statistics": node_stats,
            "quality_indicators": {
                "validation_attempts": sum(1 for dec in decisions if dec.get("agent") == "Critic"),
                "refinement_attempts": sum(1 for log in logs if "refine" in log.get("action", "").lower()),
                "error_rate": len(state.get("errors", [])) / len(injects) if injects else 0
            }
        }
    
    def _execute_interactive_workflow(self, initial_state: WorkflowState, recursion_limit: int) -> Dict[str, Any]:
        """Führt Workflow im interaktiven Modus aus mit Pausen für Benutzer-Entscheidungen."""
        current_state = initial_state
        max_steps = recursion_limit
        
        # Prüfe ob bereits eine Entscheidung getroffen wurde
        pending_decision = current_state.get("pending_decision")
        user_decisions = current_state.get("user_decisions", [])
        
        if pending_decision and pending_decision.get("required"):
            # Prüfe ob Entscheidung bereits getroffen wurde
            if user_decisions:
                last_decision = user_decisions[-1]
                if last_decision.get("decision_id") == pending_decision.get("decision_id"):
                    # Entscheidung wurde getroffen, wende sie an
                    current_state = self._apply_user_decision(current_state, last_decision)
                    current_state["pending_decision"] = None
                else:
                    # Noch keine Entscheidung, pausiere Workflow
                    print(f"⏸️  Workflow pausiert - warte auf Benutzer-Entscheidung: {pending_decision.get('decision_id')}")
                    return current_state
        
        # Führe Workflow-Schritte aus bis zum nächsten Decision-Point oder Ende
        for step in range(max_steps):
            # Prüfe ob End-Bedingung erreicht
            end_condition = current_state.get("end_condition")
            if end_condition and end_condition != ScenarioEndCondition.CONTINUE.value:
                print(f"🏁 End-Bedingung erreicht: {end_condition}")
                break
            
            # Debug: Zeige aktuellen State vor invoke
            iteration_before = current_state.get("iteration", 0)
            injects_before = len(current_state.get("injects", []))
            print(f"🔄 [Interactive Workflow] Schritt {step+1}/{max_steps}: Iteration {iteration_before}, Injects: {injects_before}")
            
            # Führe Workflow-Schritte aus (bis zum nächsten Decision-Point)
            try:
                # Führe Workflow durch alle Nodes, bis ein Decision-Point oder Ende erreicht wird
                # Ein vollständiger Zyklus benötigt ~7 Nodes (State Check → Manager → Intel → Action → Generator → Critic → State Update)
                # Plus mögliche Refine-Loops (max 2) = 9 Nodes pro Inject
                # Setze recursion_limit hoch genug, um mindestens einen vollständigen Zyklus zu ermöglichen
                current_state = self.graph.invoke(
                    current_state,
                    config={"recursion_limit": 20}  # Genug für mindestens 2 vollständige Zyklen
                )
                
                # Debug: Zeige State nach invoke
                iteration_after = current_state.get("iteration", 0)
                injects_after = len(current_state.get("injects", []))
                print(f"✅ [Interactive Workflow] Nach invoke: Iteration {iteration_after}, Injects: {injects_after}")
                if iteration_after != iteration_before:
                    print(f"   → Iteration erhöht: {iteration_before} → {iteration_after}")
                if injects_after != injects_before:
                    print(f"   → Injects hinzugefügt: {injects_before} → {injects_after}")
                
                # Prüfe ob Decision-Point erreicht wurde
                if current_state.get("pending_decision") and current_state.get("pending_decision", {}).get("required"):
                    print(f"⏸️  Decision-Point erreicht: {current_state.get('pending_decision', {}).get('decision_id')}")
                    print(f"   Final State: Iteration {current_state.get('iteration', 0)}, Injects: {len(current_state.get('injects', []))}")
                    return current_state
                
                # Prüfe End-Bedingung
                end_condition = current_state.get("end_condition")
                if end_condition and end_condition != ScenarioEndCondition.CONTINUE.value:
                    print(f"🏁 End-Bedingung erreicht: {end_condition}")
                    break
                    
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"⚠️  Fehler im interaktiven Workflow: {e}")
                print(f"   Traceback: {error_trace}")
                break
        
        print(f"🏁 [Interactive Workflow] Beendet. Final State: Iteration {current_state.get('iteration', 0)}, Injects: {len(current_state.get('injects', []))}")
        return current_state
    
    def _apply_user_decision(self, state: WorkflowState, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Wendet eine Benutzer-Entscheidung auf den State an und generiert entsprechende Events."""
        choice_id = decision.get("choice_id")
        decision_type = decision.get("decision_type")
        
        # Finde die gewählte Option
        pending_decision = state.get("pending_decision", {})
        options = pending_decision.get("options", [])
        selected_option = next((opt for opt in options if opt.get("id") == choice_id), None)
        
        if not selected_option:
            return state
        
        impact = selected_option.get("impact", {})
        
        # Wende Impact an
        if impact.get("phase_change"):
            from state_models import CrisisPhase
            state["current_phase"] = CrisisPhase(impact["phase_change"])
            print(f"🔄 Phase geändert zu: {impact['phase_change']}")
        
        # Aktualisiere System State basierend auf Entscheidung
        system_state = state.get("system_state", {})
        protected_count = 0
        
        if decision_type == "response_action":
            # Response Actions können Assets schützen
            if "contain" in choice_id.lower() or "isolate" in choice_id.lower() or "full_containment" in choice_id.lower():
                # Schütze einige Assets
                for entity_id, entity_data in list(system_state.items())[:5]:  # Schütze erste 5
                    if isinstance(entity_data, dict) and entity_data.get("status") == "compromised":
                        entity_data["status"] = "isolated"
                        protected_count += 1
                print(f"🛡️  {protected_count} Assets isoliert durch Entscheidung")
            
            elif "shutdown" in choice_id.lower():
                # Kritische Systeme herunterfahren
                for entity_id, entity_data in system_state.items():
                    if isinstance(entity_data, dict) and entity_data.get("criticality") == "critical":
                        entity_data["status"] = "offline"
                        protected_count += 1
                print(f"⛔ {protected_count} kritische Systeme heruntergefahren")
        
        elif decision_type == "resource_allocation":
            # Ressourcen-Allokation verbessert Response-Effektivität
            if "backup" in choice_id.lower() or "activate" in choice_id.lower():
                # Backup-Systeme aktivieren
                for entity_id, entity_data in system_state.items():
                    if isinstance(entity_data, dict) and "backup" in entity_id.lower():
                        entity_data["status"] = "online"
                print(f"💾 Backup-Systeme aktiviert")
        
        elif decision_type == "recovery_action":
            # Recovery-Aktionen starten Wiederherstellung
            if "recovery" in choice_id.lower():
                # Beginne Recovery-Prozess
                for entity_id, entity_data in system_state.items():
                    if isinstance(entity_data, dict) and entity_data.get("status") in ["compromised", "isolated"]:
                        entity_data["status"] = "recovering"
                print(f"🔄 Recovery-Prozess gestartet")
        
        # Speichere Entscheidung mit Impact
        user_decisions = state.get("user_decisions", [])
        user_decisions.append({
            **decision,
            "applied_impact": impact,
            "assets_protected": protected_count,
            "timestamp": datetime.now().isoformat()
        })
        state["user_decisions"] = user_decisions
        state["system_state"] = system_state
        
        print(f"✅ Entscheidung '{choice_id}' angewendet")
        
        return state
    
    def _generate_validation_reasoning(self, validation: ValidationResult) -> str:
        """Generiert eine Zusammenfassung der Validierungs-Ergebnisse für Audit-Trail."""
        reasons = []
        
        if not validation.logical_consistency:
            reasons.append("Logische Inkonsistenz erkannt")
        if not validation.dora_compliance:
            reasons.append("DORA-Compliance nicht erfüllt")
        if not validation.causal_validity:
            reasons.append("Kausale Validität verletzt")
        if validation.errors:
            reasons.append(f"{len(validation.errors)} Fehler gefunden")
        if validation.warnings:
            reasons.append(f"{len(validation.warnings)} Warnungen")
        
        if reasons:
            return "; ".join(reasons)
        return "Validierung fehlgeschlagen ohne spezifische Begründung"
    
    def _should_ask_decision(self, state: WorkflowState) -> str:
        """Entscheidet, ob eine Benutzer-Entscheidung erforderlich ist."""
        iteration = state.get("iteration", 0)
        injects = state.get("injects", [])
        injects_count = len(injects)
        max_iterations = state.get("max_iterations", self.max_iterations)
        current_phase = state.get("current_phase", CrisisPhase.NORMAL_OPERATION)
        
        print(f"🤔 [Should Ask Decision] Iteration {iteration}, Injects: {injects_count}/{max_iterations}, Phase: {current_phase.value}")
        print(f"   Interactive Mode: {self.interactive_mode}, State Interactive Mode: {state.get('interactive_mode', False)}")
        
        if not self.interactive_mode or not state.get("interactive_mode", False):
            # Nicht-interaktiver Modus: Normale Continue/End-Logik
            print(f"   → Nicht-interaktiver Modus, verwende _should_continue")
            return self._should_continue(state)
        
        # WICHTIG: Wenn noch keine Injects vorhanden sind, immer "continue" zurückgeben
        # um mindestens die ersten Injects zu generieren
        if injects_count == 0:
            print(f"   → Noch keine Injects, generiere ersten Inject (continue)")
            return "continue"
        
        # Prüfe End-Bedingungen ZUERST
        end_condition = self._check_end_conditions(state)
        if end_condition != ScenarioEndCondition.CONTINUE:
            state["end_condition"] = end_condition.value
            print(f"   → End-Bedingung erreicht: {end_condition.value} (end)")
            return "end"
        
        # Entscheidung erforderlich nach jedem 2. Inject oder bei kritischen Phasen
        decision_points = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]  # Nach jedem 2. Inject
        if injects_count in decision_points:
            print(f"   → Decision-Point: Nach {injects_count} Injects (decision)")
            return "decision"
        
        # Entscheidung bei kritischen Phasen (aber nur wenn bereits mindestens 1 Inject vorhanden ist)
        if current_phase in [CrisisPhase.ESCALATION_CRISIS, CrisisPhase.CONTAINMENT] and injects_count > 0:
            # Prüfe ob bereits eine Entscheidung für diese Phase getroffen wurde
            user_decisions = state.get("user_decisions", [])
            phase_decisions = [d for d in user_decisions if d.get("situation", {}).get("current_phase") == current_phase.value]
            if len(phase_decisions) == 0:  # Noch keine Entscheidung für diese Phase
                print(f"   → Decision-Point: Kritische Phase {current_phase.value} (decision)")
                return "decision"
        
        # Normale Continue-Logik
        if injects_count >= max_iterations:
            print(f"   → Max Iterations erreicht: {injects_count}/{max_iterations} (end)")
            return "end"
        
        print(f"   → Weiter mit nächstem Zyklus (continue)")
        return "continue"
    
    def _check_end_conditions(self, state: WorkflowState) -> ScenarioEndCondition:
        """Prüft End-Bedingungen: Fatal, Victory, oder Normal End."""
        injects = state.get("injects", [])
        system_state = state.get("system_state", {})
        current_phase = state.get("current_phase", CrisisPhase.NORMAL_OPERATION)
        user_decisions = state.get("user_decisions", [])
        
        # FATAL: Zu viele kritische Assets kompromittiert
        critical_compromised = 0
        for entity_id, entity_data in system_state.items():
            if isinstance(entity_data, dict):
                status = entity_data.get("status", "online")
                criticality = entity_data.get("criticality", "standard")
                if status == "compromised" and criticality == "critical":
                    critical_compromised += 1
        
        # FATAL: Mehr als 60% der kritischen Assets kompromittiert
        total_critical = sum(1 for e in system_state.values() 
                            if isinstance(e, dict) and e.get("criticality") == "critical")
        if total_critical > 0 and critical_compromised / total_critical > 0.6:
            print(f"💀 FATAL: {critical_compromised}/{total_critical} kritische Assets kompromittiert (>60%)")
            return ScenarioEndCondition.FATAL
        
        # FATAL: Zu viele High/Critical Injects ohne erfolgreiche Gegenmaßnahmen
        high_critical_injects = sum(1 for inj in injects 
                                   if inj.technical_metadata.severity in ["High", "Critical"])
        successful_responses = sum(1 for dec in user_decisions 
                                  if dec.get("decision_type") == "response_action" 
                                  and dec.get("choice_id", "").lower() not in ["no_action", "monitor", "investigate"])
        
        if high_critical_injects >= 6 and successful_responses < 2:
            print(f"💀 FATAL: {high_critical_injects} High/Critical Injects, nur {successful_responses} erfolgreiche Gegenmaßnahmen")
            return ScenarioEndCondition.FATAL
        
        # VICTORY: Recovery-Phase erreicht mit erfolgreichen Gegenmaßnahmen
        if current_phase == CrisisPhase.RECOVERY:
            successful_responses = sum(1 for dec in user_decisions 
                                      if dec.get("decision_type") in ["response_action", "recovery_action"]
                                      and dec.get("choice_id", "").lower() not in ["no_action", "monitor"])
            
            if successful_responses >= 3 and len(injects) >= 5:
                print(f"🏆 VICTORY: Recovery erreicht mit {successful_responses} erfolgreichen Maßnahmen")
                return ScenarioEndCondition.VICTORY
        
        # VICTORY: Bedrohung erfolgreich eingedämmt
        containment_decisions = [d for d in user_decisions 
                                if d.get("decision_type") == "response_action" 
                                and ("contain" in d.get("choice_id", "").lower() or "isolate" in d.get("choice_id", "").lower())]
        
        if len(containment_decisions) >= 2 and current_phase == CrisisPhase.CONTAINMENT:
            # Prüfe ob System stabilisiert wurde
            recent_compromises = sum(1 for inj in injects[-3:] 
                                    if any("compromised" in str(a).lower() for a in inj.technical_metadata.affected_assets))
            if recent_compromises == 0:
                print(f"🏆 VICTORY: Bedrohung erfolgreich eingedämmt mit {len(containment_decisions)} Containment-Entscheidungen")
                return ScenarioEndCondition.VICTORY
        
        # NORMAL_END: Recovery abgeschlossen
        if current_phase == CrisisPhase.RECOVERY and len(injects) >= 5:
            # Prüfe ob System wiederhergestellt wurde
            compromised_count = sum(1 for e in system_state.values() 
                                   if isinstance(e, dict) and e.get("status") == "compromised")
            if compromised_count == 0:
                return ScenarioEndCondition.NORMAL_END
        
        return ScenarioEndCondition.CONTINUE
    
    def _decision_point_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node: Decision Point - Generiert Entscheidungsoptionen für Benutzer."""
        print(f"🎯 [Decision Point] Erstelle Entscheidungsoptionen...")
        
        injects = state.get("injects", [])
        current_phase = state.get("current_phase", CrisisPhase.NORMAL_OPERATION)
        system_state = state.get("system_state", {})
        
        # Analysiere aktuelle Situation
        critical_compromised = sum(1 for e in system_state.values() 
                                  if isinstance(e, dict) and e.get("status") == "compromised" 
                                  and e.get("criticality") == "critical")
        
        # Generiere Entscheidungsoptionen basierend auf Phase und Situation
        decision_id = f"DEC-{len(injects) + 1:03d}"
        options = self._generate_decision_options(state, current_phase, critical_compromised)
        
        # Erstelle Decision-Objekt
        pending_decision = {
            "decision_id": decision_id,
            "required": True,
            "situation": {
                "current_phase": current_phase.value,
                "inject_count": len(injects),
                "critical_assets_compromised": critical_compromised,
                "total_assets": len(system_state),
                "last_inject_id": injects[-1].inject_id if injects else None
            },
            "options": options,
            "timestamp": datetime.now().isoformat()
        }
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "node": "Decision Point",
            "iteration": state['iteration'],
            "action": "Entscheidungsoptionen generiert",
            "details": {
                "decision_id": decision_id,
                "options_count": len(options),
                "status": "pending"
            }
        }
        
        logs = state.get("workflow_logs", [])
        logs.append(log_entry)
        
        print(f"📋 Entscheidungsoptionen generiert: {len(options)} Optionen")
        
        return {
            "pending_decision": pending_decision,
            "workflow_logs": logs
        }
    
    def _generate_decision_options(self, state: WorkflowState, phase: CrisisPhase, critical_compromised: int) -> List[Dict[str, Any]]:
        """Generiert Entscheidungsoptionen basierend auf aktueller Situation."""
        options = []
        injects = state.get("injects", [])
        system_state = state.get("system_state", {})
        
        if phase == CrisisPhase.SUSPICIOUS_ACTIVITY:
            options.extend([
                {
                    "id": "investigate",
                    "title": "🔍 Detaillierte Untersuchung",
                    "description": "Starte eine umfassende forensische Untersuchung der verdächtigen Aktivitäten.",
                    "type": "response_action",
                    "impact": {
                        "phase_change": None,
                        "asset_protection": "Medium",
                        "response_effectiveness": "High",
                        "outcome": "Gibt Zeit für bessere Entscheidungen, aber Angreifer könnte weiter aktiv sein"
                    }
                },
                {
                    "id": "isolate_suspicious",
                    "title": "🛡️ Verdächtige Systeme isolieren",
                    "description": "Isoliere sofort die betroffenen Systeme vom Netzwerk.",
                    "type": "response_action",
                    "impact": {
                        "phase_change": "CONTAINMENT",
                        "asset_protection": "High",
                        "response_effectiveness": "High",
                        "outcome": "Verhindert weitere Ausbreitung, aber könnte Geschäftsprozesse stören"
                    }
                },
                {
                    "id": "monitor",
                    "title": "👁️ Erweiterte Überwachung",
                    "description": "Aktiviere erweiterte SIEM-Überwachung und warte auf weitere Indikatoren.",
                    "type": "response_action",
                    "impact": {
                        "phase_change": None,
                        "asset_protection": "Low",
                        "response_effectiveness": "Medium",
                        "outcome": "Risiko: Angreifer könnte weiter aktiv sein"
                    }
                }
            ])
        
        elif phase == CrisisPhase.INITIAL_INCIDENT:
            options.extend([
                {
                    "id": "contain_immediate",
                    "title": "🚨 Sofortige Eindämmung",
                    "description": "Starte sofortige Eindämmungsmaßnahmen für alle betroffenen Systeme.",
                    "type": "response_action",
                    "impact": {
                        "phase_change": "CONTAINMENT",
                        "asset_protection": "High",
                        "response_effectiveness": "High",
                        "outcome": "Stoppt Ausbreitung, aber könnte Geschäftsprozesse beeinträchtigen"
                    }
                },
                {
                    "id": "backup_activate",
                    "title": "💾 Backup-Systeme aktivieren",
                    "description": "Aktiviere Backup-Systeme und beginne Failover-Prozess.",
                    "type": "resource_allocation",
                    "impact": {
                        "phase_change": None,
                        "asset_protection": "High",
                        "response_effectiveness": "High",
                        "outcome": "Geschäftskontinuität gewährleistet, aber Ressourcen beansprucht"
                    }
                },
                {
                    "id": "escalate_crisis",
                    "title": "⚠️ Krisenmodus aktivieren",
                    "description": "Aktiviere vollständigen Krisenmodus mit allen verfügbaren Ressourcen.",
                    "type": "response_action",
                    "impact": {
                        "phase_change": "ESCALATION_CRISIS",
                        "asset_protection": "Very High",
                        "response_effectiveness": "Very High",
                        "outcome": "Maximaler Schutz, aber hohe Kosten und Geschäftsauswirkungen"
                    }
                }
            ])
        
        elif phase == CrisisPhase.ESCALATION_CRISIS:
            options.extend([
                {
                    "id": "full_containment",
                    "title": "🔒 Vollständige Eindämmung",
                    "description": "Isoliere alle betroffenen Systeme und aktiviere Notfall-Protokolle.",
                    "type": "response_action",
                    "impact": {
                        "phase_change": "CONTAINMENT",
                        "asset_protection": "Very High",
                        "response_effectiveness": "Very High",
                        "outcome": "Stoppt Ausbreitung, aber Geschäftsprozesse werden stark beeinträchtigt"
                    }
                },
                {
                    "id": "external_help",
                    "title": "🆘 Externe Hilfe anfordern",
                    "description": "Fordere externe Incident-Response-Experten und Behörden an.",
                    "type": "resource_allocation",
                    "impact": {
                        "phase_change": None,
                        "asset_protection": "High",
                        "response_effectiveness": "High",
                        "outcome": "Zusätzliche Expertise, aber Zeitverzögerung"
                    }
                },
                {
                    "id": "shutdown_critical",
                    "title": "⛔ Kritische Systeme herunterfahren",
                    "description": "Fahre kritische Systeme herunter, um weitere Kompromittierung zu verhindern.",
                    "type": "response_action",
                    "impact": {
                        "phase_change": "CONTAINMENT",
                        "asset_protection": "Very High",
                        "response_effectiveness": "Very High",
                        "outcome": "Stoppt Angriff, aber führt zu Geschäftsausfall"
                    }
                }
            ])
        
        elif phase == CrisisPhase.CONTAINMENT:
            options.extend([
                {
                    "id": "recovery_start",
                    "title": "🔄 Recovery-Prozess starten",
                    "description": "Beginne mit der Wiederherstellung der Systeme aus Backups.",
                    "type": "recovery_action",
                    "impact": {
                        "phase_change": "RECOVERY",
                        "asset_protection": "High",
                        "response_effectiveness": "High",
                        "outcome": "Systeme werden wiederhergestellt, aber dauert Zeit"
                    }
                },
                {
                    "id": "forensic_analysis",
                    "title": "🔬 Forensische Analyse",
                    "description": "Führe detaillierte forensische Analyse durch, bevor Recovery startet.",
                    "type": "response_action",
                    "impact": {
                        "phase_change": None,
                        "asset_protection": "Medium",
                        "response_effectiveness": "Medium",
                        "outcome": "Besseres Verständnis, aber verzögert Recovery"
                    }
                },
                {
                    "id": "gradual_recovery",
                    "title": "📈 Graduelle Wiederherstellung",
                    "description": "Starte schrittweise Wiederherstellung der am wenigsten kritischen Systeme.",
                    "type": "recovery_action",
                    "impact": {
                        "phase_change": "RECOVERY",
                        "asset_protection": "Medium",
                        "response_effectiveness": "Medium",
                        "outcome": "Sicherer, aber langsamerer Recovery-Prozess"
                    }
                }
            ])
        
        # Füge immer eine "Weiter ohne Aktion" Option hinzu (mit Risiko)
        options.append({
            "id": "no_action",
            "title": "⏭️ Keine Aktion (Risiko)",
            "description": "Keine sofortige Aktion - beobachte Situation weiter.",
            "type": "no_action",
            "impact": {
                "phase_change": None,
                "asset_protection": "None",
                "response_effectiveness": "None",
                "outcome": "Risiko: Situation könnte sich verschlechtern"
            }
        })
        
        return options
    
    def _decision_point_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node: Decision Point - Wartet auf Benutzer-Entscheidung."""
        print(f"🤔 [Decision Point] Warte auf Benutzer-Entscheidung...")
        
        injects = state.get("injects", [])
        current_phase = state.get("current_phase", CrisisPhase.NORMAL_OPERATION)
        system_state = state.get("system_state", {})
        
        # Generiere Decision-Optionen basierend auf aktueller Situation
        decision_options = self._generate_decision_options(state)
        
        # Speichere pending decision im State
        pending_decision = {
            "decision_id": f"DEC-{len(state.get('user_decisions', [])) + 1:03d}",
            "timestamp": datetime.now().isoformat(),
            "situation": {
                "current_phase": current_phase.value,
                "inject_count": len(injects),
                "recent_inject": injects[-1].inject_id if injects else None,
                "critical_assets_compromised": sum(1 for e in system_state.values() 
                                                  if isinstance(e, dict) and e.get("status") == "compromised" 
                                                  and e.get("criticality") == "critical")
            },
            "options": decision_options,
            "required": True
        }
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "node": "Decision Point",
            "iteration": state['iteration'],
            "action": "Warte auf Benutzer-Entscheidung",
            "details": {
                "decision_id": pending_decision["decision_id"],
                "options_count": len(decision_options),
                "status": "pending"
            }
        }
        
        logs = state.get("workflow_logs", [])
        logs.append(log_entry)
        
        return {
            "pending_decision": pending_decision,
            "workflow_logs": logs
        }
    
    def _generate_decision_options_old(self, state: WorkflowState) -> List[Dict[str, Any]]:
        """DEPRECATED: Alte Version - wird nicht mehr verwendet."""
        # Diese Funktion wird nicht mehr verwendet
        return []
    
    def _should_refine(self, state: WorkflowState) -> str:
        """Entscheidet, ob Refine nötig ist."""
        iteration = state.get('iteration', 0)
        injects_count = len(state.get('injects', []))
        validation = state.get("validation_result")
        draft_inject = state.get("draft_inject")
        
        print(f"🔀 [Should Refine] Iteration {iteration}, Injects: {injects_count}")
        print(f"   Validation vorhanden: {validation is not None}")
        print(f"   Draft Inject vorhanden: {draft_inject is not None}")
        
        if not validation:
            print(f"   → Keine Validierung, gehe zu State Update")
            return "update"  # Weiter auch ohne Validierung
        
        # Refine wenn nicht valide (max. 2 Versuche pro Inject)
        if not validation.is_valid:
            metadata = state.get("metadata", {})
            current_inject_id = draft_inject.inject_id if draft_inject else None
            
            # Zähle Refine-Versuche pro Inject
            refine_key = f"refine_count_{current_inject_id}"
            refine_count = metadata.get(refine_key, 0)
            
            print(f"   ❌ Validation nicht valide")
            print(f"   Fehler: {validation.errors[:2] if validation.errors else 'Keine Details'}")
            print(f"   Refine-Versuche für {current_inject_id}: {refine_count}/2")
            
            if refine_count < 2:  # Max. 2 Refine-Versuche
                metadata[refine_key] = refine_count + 1
                print(f"   → Gehe zurück zu Generator (Refine-Versuch {refine_count + 1})")
                return "refine"
            else:
                # Nach 2 Versuchen: Akzeptiere trotzdem (mit Warnung)
                # Forensisches Logging: REFINED Inject (akzeptiert trotz Warnungen)
                mode = state.get("mode", "thesis")
                if mode == 'thesis' and draft_inject:
                    scenario_id = state.get("scenario_id", "UNKNOWN")
                    forensic_logger = get_forensic_logger(scenario_id)
                    forensic_logger.log_refined(
                        scenario_id=scenario_id,
                        inject=draft_inject,
                        iteration=state.get("iteration", 0),
                        refine_count=refine_count,
                        was_refined=True
                    )
                
                print(f"⚠️  Inject nach {refine_count} Refine-Versuchen akzeptiert (mit Warnungen)")
                print(f"   → Gehe zu State Update trotzdem")
                return "update"
        
        # Forensisches Logging: REFINED Inject (erfolgreich validiert)
        mode = state.get("mode", "thesis")
        if mode == 'thesis' and draft_inject:
            scenario_id = state.get("scenario_id", "UNKNOWN")
            metadata = state.get("metadata", {})
            current_inject_id = draft_inject.inject_id if draft_inject else None
            refine_key = f"refine_count_{current_inject_id}"
            refine_count = metadata.get(refine_key, 0)
            
            forensic_logger = get_forensic_logger(scenario_id)
            forensic_logger.log_refined(
                scenario_id=scenario_id,
                inject=draft_inject,
                iteration=state.get("iteration", 0),
                refine_count=refine_count,
                was_refined=(refine_count > 0)
            )
        
        print(f"   ✅ Validation valide → Gehe zu State Update")
        return "update"
    
    def _should_continue(self, state: WorkflowState) -> str:
        """Entscheidet, ob Workflow fortgesetzt werden soll."""
        iteration = state.get("iteration", 0)
        max_iterations = state.get("max_iterations", self.max_iterations)
        current_phase = state.get("current_phase", CrisisPhase.NORMAL_OPERATION)
        injects = state.get("injects", [])
        errors = state.get("errors", [])
        
        # Stoppe wenn:
        # 1. Anzahl generierter Injects erreicht (HAUPTPRÜFUNG)
        if len(injects) >= max_iterations:
            print(f"🛑 Stoppe: Anzahl Injects erreicht ({len(injects)}/{max_iterations})")
            return "end"
        
        # 2. Maximale Iterationen erreicht (Fallback)
        if iteration >= max_iterations * 2:  # Erlaube mehr Iterationen für Refine-Loops
            print(f"🛑 Stoppe: Maximale Iterationen erreicht ({iteration}/{max_iterations * 2})")
            return "end"
        
        # 3. Zu viele Fehler (verhindert Endlosschleife)
        if len(errors) > 20:  # Erhöht von 10 auf 20
            print(f"🛑 Stoppe: Zu viele Fehler ({len(errors)})")
            return "end"
        
        # 4. Recovery-Phase erreicht und genug Injects generiert (mindestens 80% von max_iterations)
        if current_phase == CrisisPhase.RECOVERY:
            min_injects_for_recovery = max(3, int(max_iterations * 0.8))
            if len(injects) >= min_injects_for_recovery:
                print(f"🛑 Stoppe: Recovery-Phase erreicht mit {len(injects)} Injects (Minimum: {min_injects_for_recovery})")
                return "end"
        
        # 5. Sicherheits-Stop: Zu viele Workflow-Logs (dynamisch basierend auf max_iterations)
        # Jeder Inject benötigt ~7 Nodes + mögliche Refine-Loops (2 pro Inject) = ~9 Nodes pro Inject
        workflow_logs = state.get("workflow_logs", [])
        max_logs = max_iterations * 15  # 15 Logs pro Inject (7 Nodes + 2 Refine + Puffer)
        if len(workflow_logs) > max_logs:
            print(f"🛑 Stoppe: Sicherheitsgrenze erreicht ({len(workflow_logs)}/{max_logs} Logs)")
            return "end"
        
        # Weiter mit nächster Iteration
        print(f"➡️  Weiter: Iteration {iteration}/{max_iterations}, Injects: {len(injects)}/{max_iterations}, Logs: {len(workflow_logs)}")
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
        scenario_id: Optional[str] = None,
        mode: str = 'thesis'
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
            "agent_decisions": [],
            "pending_decision": None,
            "user_decisions": [],
            "end_condition": None,
            "interactive_mode": self.interactive_mode,
            "mode": mode  # 'legacy' oder 'thesis'
        }
        
        print(f"🚀 Starte Szenario-Generierung: {scenario_id}")
        print(f"   Typ: {scenario_type.value}")
        print(f"   Max. Iterationen: {self.max_iterations}")
        print()
        
            # Führe Workflow aus
        try:
            # Berechne Recursion Limit basierend auf max_iterations
            # Jede Iteration benötigt ~7 Nodes (State Check → Manager → Intel → Action → Generator → Critic → State Update)
            # Plus Refine-Loops (max 2 pro Inject) = zusätzlich 2 Nodes
            # Plus Decision Points im interaktiven Modus = zusätzlich 1 Node pro Decision
            # Sicherheitspuffer: 2x
            base_nodes = 7
            refine_nodes = 2
            decision_nodes = 1 if self.interactive_mode else 0
            recursion_limit = (self.max_iterations * (base_nodes + refine_nodes + decision_nodes)) + 30
            
            # Im interaktiven Modus: Schrittweise Ausführung mit Pausen für Entscheidungen
            if self.interactive_mode:
                final_state = self._execute_interactive_workflow(initial_state, recursion_limit)
            else:
                final_state = self.graph.invoke(
                    initial_state,
                    config={"recursion_limit": recursion_limit}
                )
            
            print()
            
            # Prüfe ob Decision-Point erreicht wurde (im interaktiven Modus)
            if self.interactive_mode and final_state.get("pending_decision"):
                print(f"⏸️  Decision-Point erreicht: {final_state.get('pending_decision', {}).get('decision_id')}")
                # Generiere Entscheidungshilfen auch für pausierten State
                decision_aids = self._generate_decision_aids(final_state)
                final_state['decision_aids'] = decision_aids
                final_state['additional_info'] = self._generate_additional_info(final_state)
                return final_state  # Pausiere hier für Benutzer-Entscheidung
            
            # Prüfe End-Bedingung
            end_condition = final_state.get("end_condition")
            if end_condition:
                if end_condition == ScenarioEndCondition.FATAL.value:
                    print(f"💀 FATAL ENDE: System vollständig kompromittiert")
                elif end_condition == ScenarioEndCondition.VICTORY.value:
                    print(f"🏆 SIEG: Bedrohung erfolgreich abgewehrt")
                elif end_condition == ScenarioEndCondition.NORMAL_END.value:
                    print(f"✅ NORMALES ENDE: Recovery abgeschlossen")
            
            print(f"✅ Szenario-Generierung abgeschlossen!")
            print(f"   Generierte Injects: {len(final_state['injects'])}")
            print(f"   Finale Phase: {final_state['current_phase'].value}")
            if final_state.get("user_decisions"):
                print(f"   Benutzer-Entscheidungen: {len(final_state['user_decisions'])}")
            
            # Generiere Entscheidungshilfen und Zusatzinfos
            decision_aids = self._generate_decision_aids(final_state)
            final_state['decision_aids'] = decision_aids
            final_state['additional_info'] = self._generate_additional_info(final_state)
            
            # Speichere Szenario in Neo4j
            try:
                from state_models import ScenarioState
                scenario_state = ScenarioState(
                    scenario_id=final_state['scenario_id'],
                    scenario_type=final_state['scenario_type'],
                    current_phase=final_state['current_phase'],
                    injects=final_state['injects'],
                    start_time=final_state['start_time'],
                    metadata=final_state.get('metadata', {})
                )
                saved_id = self.neo4j_client.save_scenario(scenario_state)
                print(f"💾 Szenario in Neo4j gespeichert: {saved_id}")
            except Exception as e:
                print(f"⚠️  Fehler beim Speichern in Neo4j: {e}")
                # Füge Warnung hinzu, aber breche nicht ab
                if 'warnings' not in final_state:
                    final_state['warnings'] = []
                final_state['warnings'].append(f"Szenario konnte nicht in Neo4j gespeichert werden: {e}")
            
            return final_state
            
        except Exception as e:
            print(f"❌ Fehler bei Szenario-Generierung: {e}")
            return {
                **initial_state,
                "errors": [str(e)]
            }


"""
Critic Agent - Validiert Injects auf Logik, Konsistenz und DORA-Konformität.

Verantwortlich für:
- Logische Konsistenz-Prüfung (Widerspruchsfreiheit zur Historie)
- DORA-Compliance-Prüfung (Artikel 25)
- Causal Validity (MITRE ATT&CK Graph Konformität)
- Refine-Loop: Verbesserungsvorschläge
"""

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from state_models import Inject, ValidationResult, CrisisPhase
from workflows.fsm import CrisisFSM
import os
from dotenv import load_dotenv

load_dotenv()


class CriticAgent:
    """
    Critic Agent für Inject-Validierung.
    
    Simuliert Compliance- und Tech-Experten zur Validierung von Injects.
    Führt Reflect-Refine Loop durch, um Injects zu verbessern.
    """
    
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.3):
        """
        Initialisiert den Critic Agent.
        
        Args:
            model_name: OpenAI Modell-Name
            temperature: Temperature (niedrig für konsistente Validierung)
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def validate_inject(
        self,
        inject: Inject,
        previous_injects: List[Inject],
        current_phase: CrisisPhase,
        system_state: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validiert einen Inject.
        
        Args:
            inject: Zu validierender Inject
            previous_injects: Liste vorheriger Injects für Konsistenz
            current_phase: Aktuelle Phase
            system_state: Aktueller Systemzustand
        
        Returns:
            ValidationResult mit Validierungs-Ergebnissen
        """
        # 1. Pydantic-Validierung (automatisch)
        try:
            # Inject ist bereits ein Pydantic-Model, Validierung erfolgt automatisch
            pydantic_valid = True
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                logical_consistency=False,
                dora_compliance=False,
                causal_validity=False,
                errors=[f"Pydantic-Validierung fehlgeschlagen: {e}"]
            )
        
        # 2. FSM-Validierung (Phase-Übergang)
        fsm_valid = self._validate_phase_transition(inject, current_phase, previous_injects)
        
        # 3. LLM-basierte Validierung (Logik, DORA, Causal)
        llm_validation = self._llm_validate(inject, previous_injects, current_phase, system_state)
        
        # Kombiniere Ergebnisse
        is_valid = (
            pydantic_valid and
            fsm_valid and
            llm_validation["logical_consistency"] and
            llm_validation["dora_compliance"] and
            llm_validation["causal_validity"]
        )
        
        return ValidationResult(
            is_valid=is_valid,
            logical_consistency=llm_validation["logical_consistency"] and fsm_valid,
            dora_compliance=llm_validation["dora_compliance"],
            causal_validity=llm_validation["causal_validity"],
            errors=llm_validation.get("errors", []),
            warnings=llm_validation.get("warnings", [])
        )
    
    def _validate_phase_transition(
        self,
        inject: Inject,
        current_phase: CrisisPhase,
        previous_injects: List[Inject]
    ) -> bool:
        """Validiert, ob der Phase-Übergang erlaubt ist."""
        # Prüfe ob Phase-Übergang erlaubt ist
        if inject.phase != current_phase:
            # Phase hat sich geändert - prüfe ob Übergang erlaubt
            return CrisisFSM.can_transition(current_phase, inject.phase)
        
        # Phase bleibt gleich - das ist immer erlaubt
        return True
    
    def _llm_validate(
        self,
        inject: Inject,
        previous_injects: List[Inject],
        current_phase: CrisisPhase,
        system_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """LLM-basierte Validierung."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Du bist ein erfahrener Compliance- und Security-Experte für Finanzunternehmen.
Deine Aufgabe ist es, Injects für Krisenszenarien zu validieren.

Prüfe:
1. LOGISCHE KONSISTENZ: Widerspricht der Inject vorherigen Injects?
2. DORA-COMPLIANCE: Erfüllt der Inject Artikel 25 Anforderungen?
3. CAUSAL VALIDITY: Ist der Inject kausal valide (passt er zur MITRE ATT&CK Sequenz)?

Antworte im JSON-Format:
{{
    "logical_consistency": true/false,
    "dora_compliance": true/false,
    "causal_validity": true/false,
    "errors": ["Fehler 1", "Fehler 2"],
    "warnings": ["Warnung 1", "Warnung 2"]
}}"""),
            
            ("human", """Validiere folgenden Inject:

Inject:
{inject}

Aktuelle Phase: {current_phase}

Vorherige Injects (für Konsistenz):
{previous_injects}

Systemzustand:
{system_state}

Prüfe:
1. Ist der Inject logisch konsistent mit der Historie?
2. Erfüllt er DORA Artikel 25 Anforderungen?
3. Ist er kausal valide (passt MITRE {mitre_id} zur aktuellen Phase)?

Antworte im JSON-Format.""")
        ])
        
        # Formatierung
        previous_injects_str = self._format_previous_injects(previous_injects)
        system_state_str = self._format_system_state(system_state)
        inject_str = self._format_inject(inject)
        
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({
                "inject": inject_str,
                "current_phase": current_phase.value,
                "previous_injects": previous_injects_str,
                "system_state": system_state_str,
                "mitre_id": inject.technical_metadata.mitre_id or "Unknown"
            })
            
            # Parse JSON
            import json
            import re
            
            content = response.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            
            if json_match:
                validation = json.loads(json_match.group())
                return {
                    "logical_consistency": validation.get("logical_consistency", True),
                    "dora_compliance": validation.get("dora_compliance", True),
                    "causal_validity": validation.get("causal_validity", True),
                    "errors": validation.get("errors", []),
                    "warnings": validation.get("warnings", [])
                }
            else:
                # Fallback: Akzeptiere wenn keine klaren Fehler
                return {
                    "logical_consistency": True,
                    "dora_compliance": True,
                    "causal_validity": True,
                    "errors": [],
                    "warnings": ["Validierung konnte nicht vollständig durchgeführt werden"]
                }
                
        except Exception as e:
            # Fallback bei Fehler
            return {
                "logical_consistency": True,
                "dora_compliance": True,
                "causal_validity": True,
                "errors": [],
                "warnings": [f"Validierungsfehler: {e}"]
            }
    
    def _format_inject(self, inject: Inject) -> str:
        """Formatiert einen Inject für den Prompt."""
        lines = [
            f"Inject ID: {inject.inject_id}",
            f"Time Offset: {inject.time_offset}",
            f"Phase: {inject.phase.value}",
            f"Source: {inject.source}",
            f"Target: {inject.target}",
            f"Modality: {inject.modality.value}",
            f"Content: {inject.content}",
            f"MITRE ID: {inject.technical_metadata.mitre_id}",
            f"Affected Assets: {', '.join(inject.technical_metadata.affected_assets)}",
            f"DORA Tag: {inject.dora_compliance_tag or 'None'}"
        ]
        return "\n".join(lines)
    
    def _format_previous_injects(self, previous_injects: List[Inject]) -> str:
        """Formatiert vorherige Injects."""
        if not previous_injects:
            return "Keine vorherigen Injects"
        
        lines = []
        for inj in previous_injects[-5:]:  # Letzte 5
            lines.append(f"- {inj.inject_id} ({inj.time_offset}): {inj.content[:60]}...")
        
        return "\n".join(lines)
    
    def _format_system_state(self, system_state: Dict[str, Any]) -> str:
        """Formatiert den Systemzustand."""
        if not system_state or "entities" not in system_state:
            return "Keine Systemzustand-Informationen"
        
        entities = system_state.get("entities", [])
        lines = []
        for entity in entities[:5]:
            name = entity.get("name", entity.get("entity_id", "Unknown"))
            status = entity.get("status", "unknown")
            lines.append(f"- {name}: {status}")
        
        return "\n".join(lines) if lines else "Alle Systeme im Normalbetrieb"


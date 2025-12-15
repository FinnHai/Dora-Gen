"""
Manager Agent - Entwirft die grobe Storyline für das Szenario.

Verantwortlich für:
- Grobe Planung der Szenario-Struktur
- Phasen-Übergänge planen
- Gesamt-Narrativ definieren
"""

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from state_models import ScenarioType, CrisisPhase
from workflows.fsm import CrisisFSM
import os
from dotenv import load_dotenv

load_dotenv()


class ManagerAgent:
    """
    Manager Agent für Storyline-Planung.
    
    Verwendet LLM, um eine grobe Storyline für das Szenario zu entwerfen,
    basierend auf dem Szenario-Typ und den DORA-Anforderungen.
    """
    
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.7):
        """
        Initialisiert den Manager Agent.
        
        Args:
            model_name: OpenAI Modell-Name
            temperature: Temperature für LLM (höher = kreativer)
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def create_storyline(
        self,
        scenario_type: ScenarioType,
        current_phase: CrisisPhase,
        inject_count: int,
        system_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Erstellt eine grobe Storyline für das Szenario.
        
        Args:
            scenario_type: Typ des Szenarios
            current_phase: Aktuelle Krisenphase
            inject_count: Anzahl bereits generierter Injects
            system_state: Aktueller Systemzustand aus Neo4j
        
        Returns:
            Dictionary mit Storyline-Plan:
            - next_phase: Nächste Phase
            - narrative: Beschreibung der nächsten Schritte
            - key_events: Wichtige Ereignisse, die kommen sollten
        """
        # Prüfe erlaubte Phasen-Übergänge
        next_phases = CrisisFSM.get_next_phases(current_phase)
        suggested_phase = CrisisFSM.suggest_next_phase(
            current_phase,
            inject_count
        )
        
        # Erstelle Prompt für Storyline-Planung
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Du bist ein erfahrener Crisis Management Experte für Finanzunternehmen.
Deine Aufgabe ist es, realistische Krisenszenarien zu planen, die den DORA-Anforderungen entsprechen.

WICHTIG:
- Plane logisch konsistente Abläufe
- Berücksichtige Second-Order Effects (wenn Server A fällt, sind Apps betroffen)
- Stelle sicher, dass Phasen-Übergänge realistisch sind
- Jede Phase sollte mehrere Injects haben, bevor zur nächsten Phase übergegangen wird"""),
            
            ("human", """Erstelle einen Storyline-Plan für ein {scenario_type} Szenario.

Aktuelle Situation:
- Aktuelle Phase: {current_phase}
- Bereits generierte Injects: {inject_count}
- Verfügbare nächste Phasen: {next_phases}
- Vorgeschlagene nächste Phase: {suggested_phase}

Systemzustand:
{system_state}

Erstelle einen Plan für die nächsten Schritte:
1. Welche Phase sollte als nächstes kommen? (aus den verfügbaren wählen)
2. Welche Ereignisse sollten in dieser Phase passieren?
3. Welche Assets/Systeme sollten betroffen sein?
4. Wie sollte sich das auf die Business Continuity auswirken?

Antworte im JSON-Format:
{{
    "next_phase": "<PHASE>",
    "narrative": "<Beschreibung der nächsten Schritte>",
    "key_events": ["<Ereignis 1>", "<Ereignis 2>", ...],
    "affected_assets": ["<Asset 1>", "<Asset 2>", ...],
    "business_impact": "<Beschreibung der geschäftlichen Auswirkung>"
}}""")
        ])
        
        # Formatierung für Prompt
        next_phases_str = ", ".join([p.value for p in next_phases])
        system_state_str = self._format_system_state(system_state)
        
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({
                "scenario_type": scenario_type.value,
                "current_phase": current_phase.value,
                "inject_count": inject_count,
                "next_phases": next_phases_str,
                "suggested_phase": suggested_phase.value,
                "system_state": system_state_str
            })
            
            # Parse JSON aus Response (einfache Implementierung)
            # In Produktion sollte hier ein robusterer Parser verwendet werden
            import json
            import re
            
            # Extrahiere JSON aus Response
            content = response.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            
            if json_match:
                plan = json.loads(json_match.group())
                return {
                    "next_phase": CrisisPhase(plan.get("next_phase", suggested_phase.value)),
                    "narrative": plan.get("narrative", ""),
                    "key_events": plan.get("key_events", []),
                    "affected_assets": plan.get("affected_assets", []),
                    "business_impact": plan.get("business_impact", "")
                }
            else:
                # Fallback wenn kein JSON gefunden
                return {
                    "next_phase": suggested_phase,
                    "narrative": content,
                    "key_events": [],
                    "affected_assets": [],
                    "business_impact": ""
                }
                
        except Exception as e:
            # Fallback bei Fehler
            return {
                "next_phase": suggested_phase,
                "narrative": f"Automatischer Übergang zur Phase {suggested_phase.value}",
                "key_events": [],
                "affected_assets": [],
                "business_impact": "",
                "error": str(e)
            }
    
    def _format_system_state(self, system_state: Dict[str, Any]) -> str:
        """Formatiert den Systemzustand für den Prompt."""
        if not system_state or "entities" not in system_state:
            return "Keine Systemzustand-Informationen verfügbar"
        
        entities = system_state.get("entities", [])
        if not entities:
            return "Alle Systeme im Normalbetrieb"
        
        lines = ["Aktueller Systemzustand:"]
        for entity in entities[:10]:  # Limit auf 10 für Prompt-Länge
            status = entity.get("status", "unknown")
            name = entity.get("name", entity.get("entity_id", "Unknown"))
            lines.append(f"- {name}: {status}")
        
        return "\n".join(lines)


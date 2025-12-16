"""
Generator Agent - Erstellt konkrete Injects basierend auf der Storyline.

Verantwortlich für:
- Generierung von realistischen, detaillierten Injects
- Einhaltung des Inject-Schemas (Pydantic)
- Integration von TTPs und Systemzustand
"""

from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from state_models import (
    Inject,
    TechnicalMetadata,
    CrisisPhase,
    InjectModality,
    ScenarioType
)
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()


class GeneratorAgent:
    """
    Generator Agent für Inject-Erstellung.
    
    Verwendet LLM, um realistische, detaillierte Injects zu generieren,
    die dem Inject-Schema entsprechen und DORA-konform sind.
    """
    
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.8):
        """
        Initialisiert den Generator Agent.
        
        Args:
            model_name: OpenAI Modell-Name
            temperature: Temperature für LLM
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def generate_inject(
        self,
        scenario_type: ScenarioType,
        phase: CrisisPhase,
        inject_id: str,
        time_offset: str,
        manager_plan: Dict[str, Any],
        selected_ttp: Dict[str, Any],
        system_state: Dict[str, Any],
        previous_injects: list
    ) -> Inject:
        """
        Generiert einen neuen Inject.
        
        Args:
            scenario_type: Typ des Szenarios
            phase: Aktuelle Phase
            inject_id: Eindeutige Inject-ID
            time_offset: Zeitversatz (z.B. "T+02:00")
            manager_plan: Storyline-Plan vom Manager Agent
            selected_ttp: Ausgewählte TTP
            system_state: Aktueller Systemzustand
            previous_injects: Liste vorheriger Injects für Konsistenz
        
        Returns:
            Inject-Objekt (Pydantic)
        """
        # Erstelle Prompt für Inject-Generierung
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Du bist ein Experte für Cyber-Security Incident Response.
Deine Aufgabe ist es, realistische, detaillierte Injects für Krisenszenarien zu erstellen.

WICHTIG:
- Injects müssen logisch konsistent mit vorherigen Injects sein
- Verwende realistische technische Details (IPs, Hashes, Domains)
- Berücksichtige den aktuellen Systemzustand
- Injects müssen DORA-konform sein (Artikel 25)
- Verwende realistische Zeitstempel und Modalitäten"""),
            
            ("human", """Erstelle einen Inject für ein {scenario_type} Szenario.

Kontext:
- Inject ID: {inject_id}
- Zeitversatz: {time_offset}
- Phase: {phase}
- TTP: {ttp_name} ({ttp_id})

Storyline-Plan:
{manager_plan}

Aktueller Systemzustand:
{system_state}

Vorherige Injects (für Konsistenz):
{previous_injects}

Erstelle einen realistischen Inject im folgenden JSON-Format:
{{
    "source": "<Quelle, z.B. 'Red Team / Attacker' oder 'Blue Team / SOC'>",
    "target": "<Empfänger, z.B. 'Blue Team / SOC' oder 'Management'>",
    "modality": "<SIEM Alert|Email|Phone Call|Physical Event|News Report|Internal Report>",
    "content": "<Detaillierter Inhalt des Injects, mindestens 50 Zeichen>",
    "technical_metadata": {{
        "mitre_id": "{ttp_id}",
        "affected_assets": ["<Asset 1>", "<Asset 2>"],
        "ioc_hash": "<SHA256 Hash>",
        "ioc_ip": "<IP-Adresse>",
        "ioc_domain": "<Domain>",
        "severity": "<Low|Medium|High|Critical>"
    }},
    "dora_compliance_tag": "<Art25_VulnScan|Art25_IncidentResponse|Art25_BusinessContinuity|etc.>",
    "business_impact": "<Beschreibung der geschäftlichen Auswirkung, optional>"
}}

WICHTIG:
- Der Content muss realistisch und detailliert sein
- Verwende echte technische Details (aber keine echten IOCs)
- Stelle sicher, dass der Inject zur Phase und zum TTP passt
- Berücksichtige den Systemzustand (welche Assets sind betroffen?)""")
        ])
        
        # Formatierung
        ttp_name = selected_ttp.get("name", "Unknown TTP")
        ttp_id = selected_ttp.get("mitre_id", selected_ttp.get("technique_id", "T0000"))
        system_state_str = self._format_system_state(system_state)
        previous_injects_str = self._format_previous_injects(previous_injects)
        manager_plan_str = self._format_manager_plan(manager_plan)
        
        chain = prompt | self.llm
        
        # Retry-Logik für LLM-Call
        from utils.retry_handler import safe_llm_call
        
        try:
            def _invoke_chain():
                return chain.invoke({
                    "scenario_type": scenario_type.value,
                    "inject_id": inject_id,
                    "time_offset": time_offset,
                    "phase": phase.value,
                    "ttp_name": ttp_name,
                    "ttp_id": ttp_id,
                    "manager_plan": manager_plan_str,
                    "system_state": system_state_str,
                    "previous_injects": previous_injects_str
                })
            
            response = safe_llm_call(
                _invoke_chain,
                max_attempts=3,
                default_return=None
            )
            
            if response is None:
                raise Exception("LLM-Call fehlgeschlagen nach mehreren Versuchen")
            
            # Parse JSON aus Response
            content = response.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            
            if json_match:
                inject_data = json.loads(json_match.group())
                
                # Erstelle TechnicalMetadata
                tech_meta = TechnicalMetadata(
                    mitre_id=inject_data.get("technical_metadata", {}).get("mitre_id", ttp_id),
                    affected_assets=inject_data.get("technical_metadata", {}).get("affected_assets", []),
                    ioc_hash=inject_data.get("technical_metadata", {}).get("ioc_hash"),
                    ioc_ip=inject_data.get("technical_metadata", {}).get("ioc_ip"),
                    ioc_domain=inject_data.get("technical_metadata", {}).get("ioc_domain"),
                    severity=inject_data.get("technical_metadata", {}).get("severity", "Medium")
                )
                
                # Erstelle Inject
                inject = Inject(
                    inject_id=inject_id,
                    time_offset=time_offset,
                    phase=phase,
                    source=inject_data.get("source", "Red Team / Attacker"),
                    target=inject_data.get("target", "Blue Team / SOC"),
                    modality=InjectModality(inject_data.get("modality", "SIEM Alert")),
                    content=inject_data.get("content", "Generic security event detected."),
                    technical_metadata=tech_meta,
                    dora_compliance_tag=inject_data.get("dora_compliance_tag"),
                    business_impact=inject_data.get("business_impact")
                )
                
                return inject
            else:
                # Fallback: Erstelle minimalen Inject
                return self._create_fallback_inject(
                    inject_id, time_offset, phase, ttp_id, selected_ttp
                )
                
        except Exception as e:
            print(f"⚠️  Fehler bei Inject-Generierung: {e}")
            return self._create_fallback_inject(
                inject_id, time_offset, phase, ttp_id, selected_ttp
            )
    
    def _create_fallback_inject(
        self,
        inject_id: str,
        time_offset: str,
        phase: CrisisPhase,
        ttp_id: str,
        ttp: Dict[str, Any]
    ) -> Inject:
        """Erstellt einen Fallback-Inject bei Fehlern."""
        tech_meta = TechnicalMetadata(
            mitre_id=ttp_id,
            affected_assets=["SRV-001"],
            severity="Medium"
        )
        
        return Inject(
            inject_id=inject_id,
            time_offset=time_offset,
            phase=phase,
            source="Red Team / Attacker",
            target="Blue Team / SOC",
            modality=InjectModality.SIEM_ALERT,
            content=f"Security event detected related to {ttp.get('name', 'unknown technique')} (MITRE {ttp_id}).",
            technical_metadata=tech_meta,
            dora_compliance_tag="Art25_IncidentResponse"
        )
    
    def _format_system_state(self, system_state: Dict[str, Any]) -> str:
        """Formatiert den Systemzustand."""
        if not system_state or not isinstance(system_state, dict):
            return "Keine Systemzustand-Informationen verfügbar"
        
        # system_state ist jetzt ein direktes Dictionary: entity_id -> entity_data
        if not system_state:
            return "Alle Systeme im Normalbetrieb"
        
        lines = []
        for entity_id, entity_data in list(system_state.items())[:5]:
            if isinstance(entity_data, dict):
                status = entity_data.get("status", "unknown")
                name = entity_data.get("name", entity_id)
                lines.append(f"- {name} ({entity_id}): {status}")
            else:
                lines.append(f"- {entity_id}: {entity_data}")
        
        return "\n".join(lines) if lines else "Alle Systeme im Normalbetrieb"
    
    def _format_previous_injects(self, previous_injects: list) -> str:
        """Formatiert vorherige Injects für Konsistenz."""
        if not previous_injects:
            return "Keine vorherigen Injects"
        
        lines = []
        for inj in previous_injects[-3:]:  # Nur letzte 3
            if isinstance(inj, Inject):
                lines.append(f"- {inj.inject_id} ({inj.time_offset}): {inj.content[:50]}...")
            elif isinstance(inj, dict):
                lines.append(f"- {inj.get('inject_id', 'Unknown')}: {inj.get('content', '')[:50]}...")
        
        return "\n".join(lines)
    
    def _format_manager_plan(self, manager_plan: Dict[str, Any]) -> str:
        """Formatiert den Manager-Plan."""
        lines = []
        if manager_plan.get("narrative"):
            lines.append(f"Narrative: {manager_plan['narrative']}")
        if manager_plan.get("key_events"):
            lines.append(f"Key Events: {', '.join(manager_plan['key_events'])}")
        if manager_plan.get("affected_assets"):
            lines.append(f"Affected Assets: {', '.join(manager_plan['affected_assets'])}")
        return "\n".join(lines) if lines else "Kein spezifischer Plan"


"""
Thesis Frontend - Vergleich Baseline RAG/LLM vs. agent-basiertes System

Fokussiertes Frontend für Bachelorarbeit:
- Direkter Vergleich zwischen beiden Ansätzen
- Analysen und Metriken direkt sichtbar
- Evaluation-System für Fehlerquoten
- Clean, funktional, erklärend
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from io import BytesIO
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Backend Integration
from neo4j_client import Neo4jClient
from workflows.scenario_workflow import ScenarioWorkflow
from state_models import ScenarioType, CrisisPhase, Inject
import os
from dotenv import load_dotenv

load_dotenv()

# Streamlit Configuration
st.set_page_config(
    page_title="Thesis Evaluation - Vergleich RAG/LLM vs. Agenten-Logik",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean CSS ohne Emojis
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    h1, h2, h3 {
        color: #1e293b;
        font-weight: 600;
    }
    
    .metric-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .comparison-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .inject-item {
        background: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        margin: 0.75rem 0;
        border-radius: 4px;
    }
    
    .consistent {
        border-left-color: #10b981;
    }
    
    .hallucination {
        border-left-color: #ef4444;
    }
    
    .pending {
        border-left-color: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialisiert Session State Variablen."""
    defaults = {
        "rack_injects": [],
        "agent_injects": [],
        "rack_evaluations": {},  # inject_id -> {"rating": "consistent"/"hallucination", "reason": str}
        "agent_evaluations": {},
        "rack_scenario_result": None,
        "agent_scenario_result": None,
        "neo4j_client": None,
        "workflow": None
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def generate_with_rack_approach(scenario_type: ScenarioType, num_injects: int) -> Dict[str, Any]:
    """
    Generiert Szenario mit Baseline RAG/LLM (ohne Logik-Guard).
    
    Einfacher direkter LLM-Call ohne:
    - Agenten-Logik (Manager, Intel, Generator, Critic)
    - FSM-Validierung
    - Neo4j State-Checks
    - DORA-Compliance-Validierung
    - Refine-Loops
    """
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    import json
    import re
    
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.8,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Du bist ein Experte für Cyber-Security Incident Response.
Erstelle realistische Injects für Krisenszenarien.

WICHTIG: Erstelle {num_injects} Injects für ein {scenario_type} Szenario.
Die Injects sollten eine logische Sequenz bilden, aber es gibt keine Validierung.
Antworte im JSON-Format mit einem Array von Injects."""),
        
        ("human", """Erstelle {num_injects} Injects für ein {scenario_type} Krisenszenario.

Format (JSON):
{{
    "injects": [
        {{
            "inject_id": "RACK-001",
            "time_offset": "T+00:00",
            "content": "Beschreibung des Events",
            "phase": "NORMAL_OPERATION",
            "source": "Red Team / Attacker",
            "target": "Blue Team / SOC",
            "modality": "SIEM Alert",
            "mitre_id": "T1078",
            "affected_assets": ["SRV-001"]
        }},
        ...
    ]
}}

Die Injects sollten eine realistische Sequenz bilden, die das Szenario {scenario_type} abbildet.""")
    ])
    
    try:
        chain = prompt | llm
        response = chain.invoke({
            "scenario_type": scenario_type.value.replace("_", " ").title(),
            "num_injects": num_injects
        })
        
        # Parse JSON aus Response
        content = response.content
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        
        if json_match:
            data = json.loads(json_match.group())
            injects_data = data.get("injects", [])
        else:
            # Fallback: Versuche direkt zu parsen
            try:
                data = json.loads(content)
                injects_data = data.get("injects", [])
            except:
                injects_data = []
        
        # Konvertiere zu einheitlichem Format
        injects = []
        for i, inj_data in enumerate(injects_data):
            injects.append({
                "inject_id": inj_data.get("inject_id", f"RACK-{i+1:03d}"),
                "time_offset": inj_data.get("time_offset", f"T+{i:02d}:00"),
                "content": inj_data.get("content", f"Inject {i+1}"),
                "phase": inj_data.get("phase", CrisisPhase.NORMAL_OPERATION.value),
                "source": inj_data.get("source", "Red Team"),
                "target": inj_data.get("target", "Blue Team"),
                "modality": inj_data.get("modality", "SIEM Alert"),
                "mitre_id": inj_data.get("mitre_id", "T1078"),
                "affected_assets": inj_data.get("affected_assets", []),
                "logic_validated": False,
                "validation_attempts": 0
            })
        
        # Falls nicht genug Injects generiert wurden, fülle auf
        while len(injects) < num_injects:
            i = len(injects)
            injects.append({
                "inject_id": f"RACK-{i+1:03d}",
                "time_offset": f"T+{i:02d}:00",
                "content": f"Generiertes Inject {i+1} für {scenario_type.value}",
                "phase": CrisisPhase.NORMAL_OPERATION.value if i == 0 else CrisisPhase.SUSPICIOUS_ACTIVITY.value,
                "source": "Red Team",
                "target": "Blue Team",
                "modality": "SIEM Alert",
                "mitre_id": "T1078",
                "affected_assets": ["SRV-001"],
                "logic_validated": False,
                "validation_attempts": 0
            })
        
        return {
            "injects": injects[:num_injects],
            "scenario_id": f"rack_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "mode": "rack"
        }
    
    except Exception as e:
        st.error(f"Fehler bei Baseline RAG/LLM-Generierung: {e}")
        # Fallback: Mock-Daten
        mock_injects = []
        for i in range(num_injects):
            mock_injects.append({
                "inject_id": f"RACK-{i+1:03d}",
                "time_offset": f"T+{i:02d}:00",
                "content": f"Fallback Inject {i+1} - Fehler bei LLM-Call",
                "phase": CrisisPhase.NORMAL_OPERATION.value if i == 0 else CrisisPhase.SUSPICIOUS_ACTIVITY.value,
                "source": "Red Team",
                "target": "Blue Team",
                "modality": "SIEM Alert",
                "mitre_id": "T1078",
                "affected_assets": ["SRV-001"],
                "logic_validated": False,
                "validation_attempts": 0
            })
        
        return {
            "injects": mock_injects,
            "scenario_id": f"rack_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "mode": "rack",
            "error": str(e)
        }


def generate_with_agent_approach(scenario_type: ScenarioType, num_injects: int) -> Dict[str, Any]:
    """
    Generiert Szenario mit agent-basiertem Ansatz (mit Logik-Validierung).
    
    Nutzt das bestehende ScenarioWorkflow mit allen Agenten.
    """
    if st.session_state.neo4j_client is None:
        st.session_state.neo4j_client = Neo4jClient()
        st.session_state.neo4j_client.connect()
    
    if st.session_state.workflow is None:
        st.session_state.workflow = ScenarioWorkflow(
            neo4j_client=st.session_state.neo4j_client,
            max_iterations=num_injects,
            interactive_mode=False
        )
    
    result = st.session_state.workflow.generate_scenario(scenario_type=scenario_type)
    
    # Konvertiere Injects zu einfachem Format
    injects = []
    for inj in result.get('injects', []):
        if isinstance(inj, Inject):
            injects.append({
                "inject_id": inj.inject_id,
                "time_offset": inj.time_offset,
                "content": inj.content,
                "phase": inj.phase.value if isinstance(inj.phase, CrisisPhase) else str(inj.phase),
                "source": inj.source,
                "target": inj.target,
                "modality": inj.modality.value if hasattr(inj.modality, 'value') else str(inj.modality),
                "mitre_id": inj.technical_metadata.mitre_id if inj.technical_metadata else None,
                "affected_assets": inj.technical_metadata.affected_assets if inj.technical_metadata else [],
                "logic_validated": True,
                "validation_attempts": getattr(inj, 'validation_attempts', 0)
            })
    
    return {
        "injects": injects,
        "scenario_id": result.get('scenario_id'),
        "mode": "agent",
        "workflow_logs": result.get('workflow_logs', [])
    }


def calculate_metrics(evaluations: Dict[str, Dict[str, Any]], total_injects: int) -> Dict[str, Any]:
    """Berechnet Metriken aus Evaluations-Daten."""
    consistent_count = sum(1 for e in evaluations.values() if e.get("rating") == "consistent")
    hallucination_count = sum(1 for e in evaluations.values() if e.get("rating") == "hallucination")
    evaluated_count = len(evaluations)
    pending_count = total_injects - evaluated_count
    
    consistency_rate = (consistent_count / evaluated_count * 100) if evaluated_count > 0 else 0
    error_rate = (hallucination_count / evaluated_count * 100) if evaluated_count > 0 else 0
    
    return {
        "total": total_injects,
        "evaluated": evaluated_count,
        "pending": pending_count,
        "consistent": consistent_count,
        "hallucinations": hallucination_count,
        "consistency_rate": consistency_rate,
        "error_rate": error_rate
    }


def render_comparison_metrics():
    """Rendert Vergleichs-Metriken zwischen beiden Ansätzen."""
    rack_metrics = calculate_metrics(
        st.session_state.rack_evaluations,
        len(st.session_state.rack_injects)
    )
    agent_metrics = calculate_metrics(
        st.session_state.agent_evaluations,
        len(st.session_state.agent_injects)
    )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Baseline RAG/LLM Konsistenzrate",
            f"{rack_metrics['consistency_rate']:.1f}%",
            delta=f"{rack_metrics['consistency_rate'] - agent_metrics['consistency_rate']:.1f}%" if rack_metrics['evaluated'] > 0 and agent_metrics['evaluated'] > 0 else None
        )
    
    with col2:
        st.metric(
            "Agenten-Logik Konsistenzrate",
            f"{agent_metrics['consistency_rate']:.1f}%",
            delta=f"{agent_metrics['consistency_rate'] - rack_metrics['consistency_rate']:.1f}%" if rack_metrics['evaluated'] > 0 and agent_metrics['evaluated'] > 0 else None
        )
    
    with col3:
        st.metric(
            "Baseline RAG/LLM Fehlerrate",
            f"{rack_metrics['error_rate']:.1f}%",
            delta=f"{rack_metrics['error_rate'] - agent_metrics['error_rate']:.1f}%" if rack_metrics['evaluated'] > 0 and agent_metrics['evaluated'] > 0 else None
        )
    
    with col4:
        st.metric(
            "Agenten-Logik Fehlerrate",
            f"{agent_metrics['error_rate']:.1f}%",
            delta=f"{agent_metrics['error_rate'] - rack_metrics['error_rate']:.1f}%" if rack_metrics['evaluated'] > 0 and agent_metrics['evaluated'] > 0 else None
        )
    
    # Vergleichs-Diagramm
    if rack_metrics['evaluated'] > 0 and agent_metrics['evaluated'] > 0:
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name="Baseline RAG/LLM",
            x=["Konsistenzrate", "Fehlerrate"],
            y=[rack_metrics['consistency_rate'], rack_metrics['error_rate']],
            marker_color="#ef4444"
        ))
        
        fig.add_trace(go.Bar(
            name="Agenten-Logik",
            x=["Konsistenzrate", "Fehlerrate"],
            y=[agent_metrics['consistency_rate'], agent_metrics['error_rate']],
            marker_color="#10b981"
        ))
        
        fig.update_layout(
            title="Vergleich: Konsistenzrate und Fehlerrate",
            barmode="group",
            yaxis_title="Prozent",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)


def render_validation_summary(title: str, result: Optional[Dict[str, Any]]):
    """Zeigt kurz, welche Fehler/Warnungen abgefangen wurden."""
    if not result:
        return
    errors = result.get("errors", []) or []
    warnings = result.get("warnings", []) or []
    if not errors and not warnings:
        st.caption(f"{title}: Keine gemeldeten Validierungsfehler.")
        return
    with st.expander(f"{title}: Validierungsfehler/Warnungen"):
        if errors:
            st.markdown("**Fehler (verhindert):**")
            for err in errors[:10]:
                st.markdown(f"- {err}")
            if len(errors) > 10:
                st.caption(f"... {len(errors)-10} weitere")
        if warnings:
            st.markdown("**Warnungen:**")
            for w in warnings[:10]:
                st.markdown(f"- {w}")
            if len(warnings) > 10:
                st.caption(f"... {len(warnings)-10} weitere")


def render_inject_list(injects: List[Dict], evaluations: Dict, mode: str):
    """Rendert Liste von Injects mit Evaluation-Buttons."""
    if not injects:
        st.info(f"Noch keine Injects im {mode}-Modus generiert.")
        return
    
    for inject in injects:
        inject_id = inject.get("inject_id", "")
        evaluation = evaluations.get(inject_id, {})
        rating = evaluation.get("rating", "pending")
        
        # CSS-Klasse basierend auf Rating
        css_class = rating if rating != "pending" else "pending"
        
        st.markdown(f"""
        <div class="inject-item {css_class}">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <strong>{inject_id}</strong> - {inject.get('time_offset', 'N/A')}
                    <br>
                    <small style="color: #64748b;">Phase: {inject.get('phase', 'N/A')}</small>
                </div>
                <div style="margin-left: 1rem;">
                    <span style="padding: 0.25rem 0.5rem; background: {'#10b981' if rating == 'consistent' else '#ef4444' if rating == 'hallucination' else '#94a3b8'}; color: white; border-radius: 4px; font-size: 0.75rem;">
                        {rating.upper() if rating != 'pending' else 'AUSSTEHEND'}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**{inject.get('source', 'N/A')}** → *{inject.get('target', 'N/A')}*")
        st.markdown(f"*{inject.get('modality', 'N/A')}*")
        
        st.markdown(f"""
        <div style="background: white; padding: 0.75rem; border-radius: 4px; margin: 0.5rem 0;">
            {inject.get('content', 'N/A')}
        </div>
        """, unsafe_allow_html=True)
        
        # Metadaten
        col_meta1, col_meta2 = st.columns(2)
        with col_meta1:
            st.caption(f"MITRE ATT&CK: {inject.get('mitre_id', 'N/A')}")
        with col_meta2:
            assets = inject.get('affected_assets', [])
            st.caption(f"Betroffene Assets: {', '.join(assets) if assets else 'Keine'}")
        
        # Logik-Validierung Info
        if inject.get('logic_validated'):
            st.caption(f"Logik-validiert: Ja (Validierungsversuche: {inject.get('validation_attempts', 0)})")
        else:
            st.caption("Logik-validiert: Nein (Baseline RAG/LLM)")
        
        # Evaluation-Buttons
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
        
        with col_btn1:
            if st.button("Konsistent", key=f"{mode}_consistent_{inject_id}", use_container_width=True):
                evaluations[inject_id] = {"rating": "consistent", "reason": "", "timestamp": datetime.now().isoformat()}
                st.rerun()
        
        with col_btn2:
            if st.button("Halluzination", key=f"{mode}_hallucination_{inject_id}", use_container_width=True):
                st.session_state[f"{mode}_show_reason_{inject_id}"] = True
        
        # Reason Input für Halluzination
        if st.session_state.get(f"{mode}_show_reason_{inject_id}", False):
            reason = st.text_area(
                "Grund für Halluzination:",
                key=f"{mode}_reason_{inject_id}",
                placeholder="Beschreibe die spezifische Inkonsistenz oder den Fehler...",
                height=80
            )
            col_submit1, col_submit2 = st.columns([1, 4])
            with col_submit1:
                if st.button("Speichern", key=f"{mode}_submit_{inject_id}"):
                    if reason:
                        evaluations[inject_id] = {
                            "rating": "hallucination",
                            "reason": reason,
                            "timestamp": datetime.now().isoformat()
                        }
                        st.session_state[f"{mode}_show_reason_{inject_id}"] = False
                        st.rerun()
                    else:
                        st.error("Bitte gib einen Grund an")
            with col_submit2:
                if st.button("Abbrechen", key=f"{mode}_cancel_{inject_id}"):
                    st.session_state[f"{mode}_show_reason_{inject_id}"] = False
                    st.rerun()
        
        st.markdown("---")


def export_evaluation_data():
    """Exportiert alle Evaluations-Daten als CSV mit erweiterten Metriken."""
    data = []
    
    # Erstelle Mapping von Inject-ID zu Metadaten aus Szenario-Resultaten
    rack_inject_metadata = {}
    if st.session_state.rack_scenario_result:
        for inj in st.session_state.rack_scenario_result.get("injects", []):
            if isinstance(inj, dict):
                rack_inject_metadata[inj.get("inject_id", "")] = {
                    "validation_attempts": inj.get("validation_attempts", 0),
                    "validation_errors": ""  # Baseline hat keine Validierung
                }
    
    agent_inject_metadata = {}
    if st.session_state.agent_scenario_result:
        # Extrahiere validation_errors aus workflow_logs
        workflow_logs = st.session_state.agent_scenario_result.get("workflow_logs", [])
        inject_refine_counts = {}  # Tracke Refine-Versuche pro Inject
        
        for log in workflow_logs:
            node = log.get("node", "")
            details = log.get("details", {})
            
            # Finde Critic-Validierungen
            if node == "Critic Agent":
                validation_result = details.get("validation_result")
                if validation_result:
                    # Versuche Inject-ID zu finden
                    inject_id = details.get("inject_id") or details.get("draft_inject_id")
                    if not inject_id:
                        # Fallback: Suche in anderen Logs nach Inject-ID
                        iteration = log.get("iteration", -1)
                        for other_log in workflow_logs:
                            if other_log.get("iteration") == iteration and other_log.get("node") == "Generator Agent":
                                inject_id = other_log.get("details", {}).get("inject_id")
                                break
                    
                    if inject_id:
                        errors = validation_result.get("errors", [])
                        if inject_id not in agent_inject_metadata:
                            agent_inject_metadata[inject_id] = {
                                "validation_attempts": 0,
                                "validation_errors": []
                            }
                        # Sammle alle Fehler für diesen Inject
                        if errors:
                            agent_inject_metadata[inject_id]["validation_errors"].extend(errors)
            
            # Finde Refine-Versuche (Should Refine Node)
            if "Should Refine" in node or "Refine" in node:
                draft_inject = details.get("draft_inject")
                if draft_inject:
                    inject_id = draft_inject.inject_id if hasattr(draft_inject, 'inject_id') else str(draft_inject)
                    if inject_id:
                        inject_refine_counts[inject_id] = inject_refine_counts.get(inject_id, 0) + 1
        
        # Kombiniere Refine-Counts mit Validierungsfehlern
        for inj_id, metadata in agent_inject_metadata.items():
            metadata["validation_attempts"] = inject_refine_counts.get(inj_id, 0)
            metadata["validation_errors"] = "; ".join(set(metadata["validation_errors"]))  # Dedupliziere
        
        # Fallback: Verwende validation_attempts aus Inject-Daten
        for inj in st.session_state.agent_scenario_result.get("injects", []):
            if isinstance(inj, dict):
                inj_id = inj.get("inject_id", "")
                if inj_id not in agent_inject_metadata:
                    agent_inject_metadata[inj_id] = {
                        "validation_attempts": inj.get("validation_attempts", 0),
                        "validation_errors": ""
                    }
    
    # RAG/LLM Evaluations
    for inject_id, eval_data in st.session_state.rack_evaluations.items():
        metadata = rack_inject_metadata.get(inject_id, {})
        data.append({
            "inject_id": inject_id,
            "mode": "baseline_rag_llm",
            "rating": eval_data.get("rating", ""),
            "reason": eval_data.get("reason", ""),
            "timestamp": eval_data.get("timestamp", ""),
            "validation_attempts": metadata.get("validation_attempts", 0),
            "validation_errors": metadata.get("validation_errors", "")
        })
    
    # Agent Evaluations
    for inject_id, eval_data in st.session_state.agent_evaluations.items():
        metadata = agent_inject_metadata.get(inject_id, {})
        data.append({
            "inject_id": inject_id,
            "mode": "agenten_logik",
            "rating": eval_data.get("rating", ""),
            "reason": eval_data.get("reason", ""),
            "timestamp": eval_data.get("timestamp", ""),
            "validation_attempts": metadata.get("validation_attempts", 0),
            "validation_errors": metadata.get("validation_errors", "")
        })
    
    if not data:
        st.warning("Keine Evaluations-Daten zum Exportieren vorhanden.")
        return None
    
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False)
    return csv


def main():
    """Hauptfunktion des Thesis Frontends."""
    init_session_state()
    
    # Header
    st.title("Vergleich: Baseline RAG/LLM vs. Agenten-Logik")
    
    with st.expander("Forschungsfrage und Methodik", expanded=False):
        st.markdown("""
        **Forschungsfrage:** 
        Reduziert ein Neuro-Symbolic Logic Guard (LangGraph + State Tracking) 
        Halluzinationen in Krisenszenarien im Vergleich zu einem reinen LLM/RAG-Ansatz?
        
        **Methodik:**
        - Vergleich zwischen \"Baseline RAG/LLM\" (ohne Validierung) und \"Agenten-Logik\" (Neuro-Symbolic)
        - Manuelle Evaluation jedes Injects (Consistent vs. Hallucination)
        - Statistische Auswertung der Ergebnisse (Konsistenzrate, Fehlerrate)
        
        **Hypothese:** 
        Symbolische Constraints (FSM, Neo4j State, DORA Compliance) reduzieren 
        logische Inkonsistenzen und technische Fehler.
        
        **Problemstellung:**
        Krisenstab-Modelle mit einem reinen RAG/LLM werden nach einer Zeit unlogisch.
        Die Logik soll durch das agent-basierte System behalten werden.
        """)
    
    # Sidebar: Konfiguration
    with st.sidebar:
        st.header("Konfiguration")
        
        scenario_type = st.selectbox(
            "Szenario-Typ",
            options=[st.value for st in ScenarioType],
            format_func=lambda x: x.replace("_", " ").title(),
            help="Typ des zu generierenden Krisenszenarios"
        )
        
        num_injects = st.slider(
            "Anzahl Injects",
            min_value=1,
            max_value=20,
            value=5,
            help="Anzahl der zu generierenden Injects pro Modus"
        )
        
        st.markdown("---")
        
        st.subheader("Generierung")
        
        col_gen1, col_gen2 = st.columns(2)
        
        with col_gen1:
            if st.button("Baseline RAG/LLM generieren", use_container_width=True):
                with st.spinner("Generiere Szenario mit Baseline RAG/LLM..."):
                    result = generate_with_rack_approach(
                        ScenarioType(scenario_type),
                        num_injects
                    )
                    st.session_state.rack_injects = result.get("injects", [])
                    st.session_state.rack_scenario_result = result
                    st.success(f"{len(st.session_state.rack_injects)} Injects generiert")
        
        with col_gen2:
            if st.button("Agenten-Logik generieren", use_container_width=True):
                with st.spinner("Generiere Szenario mit agent-basiertem System..."):
                    try:
                        result = generate_with_agent_approach(
                            ScenarioType(scenario_type),
                            num_injects
                        )
                        st.session_state.agent_injects = result.get("injects", [])
                        st.session_state.agent_scenario_result = result
                        st.success(f"{len(st.session_state.agent_injects)} Injects generiert")
                    except Exception as e:
                        st.error(f"Fehler: {e}")
                        st.info("Stelle sicher, dass Neo4j läuft und die API-Keys gesetzt sind.")
        
        st.markdown("---")
        
        st.subheader("Export")
        
        csv_data = export_evaluation_data()
        if csv_data:
            st.download_button(
                label="Evaluations-Daten exportieren (CSV)",
                data=csv_data,
                file_name=f"thesis_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        st.markdown("---")
        
        st.subheader("Status")
        st.caption(f"RAG/LLM Injects: {len(st.session_state.rack_injects)}")
        st.caption(f"Agenten-Injects: {len(st.session_state.agent_injects)}")
        st.caption(f"RAG/LLM Evaluations: {len(st.session_state.rack_evaluations)}")
        st.caption(f"Agenten-Evaluations: {len(st.session_state.agent_evaluations)}")
    
    # Hauptbereich: Vergleichsansicht
    if len(st.session_state.rack_injects) > 0 or len(st.session_state.agent_injects) > 0:
        st.header("Vergleichs-Analysen")
        render_comparison_metrics()

        # Zeige, was die Logik abgefangen hat (Agenten-Validierung)
        if st.session_state.agent_scenario_result:
            render_validation_summary("Agenten-Logik", st.session_state.agent_scenario_result)
        
        st.markdown("---")
        
        # Split-View: RAG/LLM vs. Agenten-Logik
        col_rack, col_agent = st.columns(2)
        
        with col_rack:
            st.header("Baseline RAG/LLM")
            st.caption("RAG/LLM ohne Logik-Validierung")
            
            rack_metrics = calculate_metrics(
                st.session_state.rack_evaluations,
                len(st.session_state.rack_injects)
            )
            
            st.markdown(f"""
            <div class="metric-box">
                <strong>Metriken:</strong><br>
                Evaluiert: {rack_metrics['evaluated']} / {rack_metrics['total']}<br>
                Konsistent: {rack_metrics['consistent']}<br>
                Halluzinationen: {rack_metrics['hallucinations']}<br>
                Konsistenzrate: {rack_metrics['consistency_rate']:.1f}%<br>
                Fehlerrate: {rack_metrics['error_rate']:.1f}%
            </div>
            """, unsafe_allow_html=True)
            
            render_inject_list(
                st.session_state.rack_injects,
                st.session_state.rack_evaluations,
                "rack"
            )
        
        with col_agent:
            st.header("Agenten-Logik")
            st.caption("Mit Logik-Validierung (FSM, Neo4j, DORA)")
            
            agent_metrics = calculate_metrics(
                st.session_state.agent_evaluations,
                len(st.session_state.agent_injects)
            )
            
            st.markdown(f"""
            <div class="metric-box">
                <strong>Metriken:</strong><br>
                Evaluiert: {agent_metrics['evaluated']} / {agent_metrics['total']}<br>
                Konsistent: {agent_metrics['consistent']}<br>
                Halluzinationen: {agent_metrics['hallucinations']}<br>
                Konsistenzrate: {agent_metrics['consistency_rate']:.1f}%<br>
                Fehlerrate: {agent_metrics['error_rate']:.1f}%
            </div>
            """, unsafe_allow_html=True)
            
            render_inject_list(
                st.session_state.agent_injects,
                st.session_state.agent_evaluations,
                "agent"
            )
    else:
        st.info("""
        **Anleitung:**
        
        1. Wähle einen Szenario-Typ und die Anzahl der Injects in der Sidebar
        2. Generiere zuerst ein Szenario mit "Baseline RAG/LLM generieren"
        3. Generiere dann ein Szenario mit "Agenten-Logik generieren"
        4. Bewerte die Injects mit "Konsistent" oder "Halluzination"
        5. Die Analysen werden automatisch aktualisiert
        6. Exportiere die Evaluations-Daten für deine Bachelorarbeit
        
        **Wichtig:** Beide Modi sollten mit demselben Szenario-Typ und derselben Anzahl Injects getestet werden, 
        um einen fairen Vergleich zu ermöglichen.
        """)


if __name__ == "__main__":
    main()

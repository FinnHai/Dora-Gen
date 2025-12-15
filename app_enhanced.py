"""
Streamlit Frontend für den DORA-Szenariengenerator.
Enterprise-Grade Design mit interaktiven Features, Analysen und Workflow-Logs.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from neo4j_client import Neo4jClient
from workflows.scenario_workflow import ScenarioWorkflow
from state_models import ScenarioType, CrisisPhase, Inject
import os
from dotenv import load_dotenv
import html

load_dotenv()

# Streamlit Konfiguration
st.set_page_config(
    page_title="DORA Szenariengenerator",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enterprise Security Design System
st.markdown("""
<style>
    /* ===== COLOR SYSTEM ===== */
    :root {
        --primary-dark: #1a365d;
        --primary: #2c5282;
        --primary-light: #4299e1;
        --secondary: #4a5568;
        --secondary-light: #718096;
        --success: #38a169;
        --warning: #d69e2e;
        --danger: #e53e3e;
        --info: #3182ce;
        --background: #f7fafc;
        --surface: #ffffff;
        --border: #e2e8f0;
        --text-primary: #1a202c;
        --text-secondary: #4a5568;
    }
    
    .stApp {
        background: var(--background);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    }
    
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1600px;
    }
    
    .main-header {
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%);
        padding: 3rem 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 40px rgba(26, 54, 93, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(180deg); }
    }
    
    .main-header h1 {
        font-size: 3.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
        letter-spacing: -0.5px;
    }
    
    .sub-header {
        font-size: 1.4rem;
        margin-top: 0.75rem;
        opacity: 0.95;
        font-weight: 300;
        position: relative;
        z-index: 1;
    }
    
    .enterprise-card {
        background: var(--surface);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
        border: 1px solid var(--border);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .enterprise-card:hover {
        box-shadow: 0 10px 25px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05);
        transform: translateY(-2px);
    }
    
    .inject-card {
        background: var(--surface);
        padding: 1.75rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border-left: 4px solid;
        border: 1px solid var(--border);
        transition: all 0.3s ease;
    }
    
    .inject-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        transform: translateX(4px);
        border-left-width: 6px;
    }
    
    .phase-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .metric-card {
        background: var(--surface);
        padding: 1.75rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid var(--border);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary) 0%, var(--primary-light) 100%);
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    }
    
    .metric-value {
        font-size: 2.75rem;
        font-weight: 700;
        color: var(--primary-dark);
        margin: 0.75rem 0;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--primary-dark) 0%, #1e3a5f 100%);
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: white;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(44, 82, 130, 0.3);
        letter-spacing: 0.3px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(44, 82, 130, 0.4);
        background: linear-gradient(135deg, var(--primary-light) 0%, var(--primary) 100%);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: var(--surface);
        padding: 0.5rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 6px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: var(--text-secondary);
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary);
        color: white;
        box-shadow: 0 2px 8px rgba(44, 82, 130, 0.2);
    }
    
    .log-entry {
        background: var(--surface);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.75rem;
        border-left: 3px solid var(--primary);
        font-family: 'Courier New', monospace;
        font-size: 0.875rem;
    }
    
    .decision-card {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        padding: 1.25rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid var(--info);
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialisiert Session State Variablen."""
    if "scenario_result" not in st.session_state:
        st.session_state.scenario_result = None
    if "workflow" not in st.session_state:
        st.session_state.workflow = None
    if "neo4j_client" not in st.session_state:
        st.session_state.neo4j_client = None
    if "filter_phase" not in st.session_state:
        st.session_state.filter_phase = None
    if "search_term" not in st.session_state:
        st.session_state.search_term = ""


def get_phase_color(phase: CrisisPhase) -> tuple:
    """Gibt Farbe und Icon für eine Phase zurück."""
    phase_config = {
        CrisisPhase.NORMAL_OPERATION: ("#38a169", "✅", "Normalbetrieb"),
        CrisisPhase.SUSPICIOUS_ACTIVITY: ("#d69e2e", "⚠️", "Verdächtige Aktivität"),
        CrisisPhase.INITIAL_INCIDENT: ("#ed8936", "🚨", "Initialer Vorfall"),
        CrisisPhase.ESCALATION_CRISIS: ("#e53e3e", "🔥", "Eskalation/Krise"),
        CrisisPhase.CONTAINMENT: ("#805ad5", "🛡️", "Eindämmung"),
        CrisisPhase.RECOVERY: ("#319795", "🔧", "Wiederherstellung")
    }
    return phase_config.get(phase, ("#718096", "📋", "Unbekannt"))


def format_inject_card_safe(inject: Inject, index: int):
    """Formatiert eine Inject-Karte mit korrekter HTML-Escape."""
    phase_color, icon, phase_label = get_phase_color(inject.phase)
    
    # Escape HTML in Content
    safe_content = html.escape(inject.content)
    safe_source = html.escape(inject.source)
    safe_target = html.escape(inject.target)
    safe_mitre = html.escape(inject.technical_metadata.mitre_id or 'N/A')
    safe_assets = ', '.join([html.escape(a) for a in inject.technical_metadata.affected_assets]) if inject.technical_metadata.affected_assets else 'Keine'
    safe_dora = html.escape(inject.dora_compliance_tag) if inject.dora_compliance_tag else None
    safe_impact = html.escape(inject.business_impact) if inject.business_impact else None
    
    st.markdown(f"""
    <div class="inject-card fade-in" style="border-left-color: {phase_color};">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.25rem; flex-wrap: wrap; gap: 1rem;">
            <div>
                <h3 style="margin: 0; color: var(--text-primary); font-size: 1.25rem; font-weight: 600;">
                    {icon} {inject.inject_id}
                </h3>
                <p style="margin: 0.25rem 0 0 0; color: var(--text-secondary); font-size: 0.875rem;">
                    <strong>Zeitversatz:</strong> {inject.time_offset}
                </p>
            </div>
            <span class="phase-badge" style="background: {phase_color}; color: white;">
                {phase_label}
            </span>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
            <div style="background: #f7fafc; padding: 1rem; border-radius: 8px; border: 1px solid var(--border);">
                <p style="margin: 0; font-size: 0.875rem; color: var(--text-secondary);"><strong>📡 Quelle</strong></p>
                <p style="margin: 0.5rem 0 0 0; color: var(--text-primary); font-weight: 500;">{safe_source}</p>
            </div>
            <div style="background: #f7fafc; padding: 1rem; border-radius: 8px; border: 1px solid var(--border);">
                <p style="margin: 0; font-size: 0.875rem; color: var(--text-secondary);"><strong>🎯 Ziel</strong></p>
                <p style="margin: 0.5rem 0 0 0; color: var(--text-primary); font-weight: 500;">{safe_target}</p>
            </div>
        </div>
        
        <div style="background: #f7fafc; padding: 1.25rem; border-radius: 8px; margin-bottom: 1rem; border: 1px solid var(--border);">
            <p style="margin: 0 0 0.5rem 0; font-size: 0.875rem; color: var(--text-secondary); font-weight: 600;">
                📝 Inhalt
            </p>
            <p style="margin: 0; line-height: 1.6; color: var(--text-primary);">
                {safe_content}
            </p>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 1rem;">
            <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid var(--border);">
                <p style="margin: 0 0 0.5rem 0; font-size: 0.875rem; color: var(--text-secondary); font-weight: 600;">
                    🔍 MITRE ATT&CK
                </p>
                <code style="background: #edf2f7; color: var(--primary-dark); padding: 0.375rem 0.75rem; border-radius: 6px; font-size: 0.875rem; font-weight: 600;">
                    {safe_mitre}
                </code>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid var(--border);">
                <p style="margin: 0 0 0.5rem 0; font-size: 0.875rem; color: var(--text-secondary); font-weight: 600;">
                    📨 Modalität
                </p>
                <p style="margin: 0; color: var(--text-primary); font-weight: 500; font-size: 0.875rem;">
                    {inject.modality.value}
                </p>
            </div>
        </div>
        
        <div style="background: #f7fafc; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border: 1px solid var(--border);">
            <p style="margin: 0 0 0.5rem 0; font-size: 0.875rem; color: var(--text-secondary); font-weight: 600;">
                🎯 Betroffene Assets
            </p>
            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                {''.join([f'<span style="background: var(--primary-light); color: white; padding: 0.375rem 0.75rem; border-radius: 6px; font-size: 0.75rem; font-weight: 500;">{html.escape(asset)}</span>' for asset in inject.technical_metadata.affected_assets]) if inject.technical_metadata.affected_assets else '<span style="color: var(--text-secondary); font-size: 0.875rem;">Keine Assets betroffen</span>'}
            </div>
        </div>
        
        {f'''
        <div style="background: linear-gradient(135deg, #e6f3ff 0%, #cce7ff 100%); padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 3px solid var(--info);">
            <p style="margin: 0; font-size: 0.875rem;"><strong style="color: var(--primary-dark);">🏛️ DORA Compliance:</strong> <span style="color: var(--text-primary);">{safe_dora}</span></p>
        </div>
        ''' if safe_dora else ''}
        
        {f'''
        <div style="background: linear-gradient(135deg, #fff5e6 0%, #ffe6cc 100%); padding: 1rem; border-radius: 8px; border-left: 3px solid var(--warning);">
            <p style="margin: 0; font-size: 0.875rem;"><strong style="color: #b7791f;">💼 Business Impact:</strong> <span style="color: var(--text-primary);">{safe_impact}</span></p>
        </div>
        ''' if safe_impact else ''}
    </div>
    """, unsafe_allow_html=True)


def create_workflow_timeline(logs: list, decisions: list):
    """Erstellt eine Timeline-Visualisierung des Workflows."""
    if not logs and not decisions:
        return None
    
    fig = go.Figure()
    
    # Workflow-Logs
    if logs:
        log_times = []
        log_nodes = []
        for log in logs:
            try:
                dt = datetime.fromisoformat(log.get("timestamp", ""))
                log_times.append(dt)
                log_nodes.append(log.get("node", "Unknown"))
            except:
                continue
        
        if log_times:
            fig.add_trace(go.Scatter(
                x=log_times,
                y=[1] * len(log_times),
                mode='markers+lines',
                name='Workflow Nodes',
                marker=dict(size=10, color='#2c5282'),
                line=dict(color='#4299e1', width=2)
            ))
    
    # Agent-Entscheidungen
    if decisions:
        decision_times = []
        decision_agents = []
        for dec in decisions:
            try:
                dt = datetime.fromisoformat(dec.get("timestamp", ""))
                decision_times.append(dt)
                decision_agents.append(dec.get("agent", "Unknown"))
            except:
                continue
        
        if decision_times:
            fig.add_trace(go.Scatter(
                x=decision_times,
                y=[2] * len(decision_times),
                mode='markers',
                name='Agent Decisions',
                marker=dict(size=12, color='#38a169', symbol='diamond'),
            ))
    
    fig.update_layout(
        title="⏱️ Workflow Timeline",
        xaxis_title="Zeit",
        yaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=300,
        yaxis=dict(showticklabels=False, range=[0, 3])
    )
    
    return fig


def create_agent_decision_chart(decisions: list):
    """Visualisiert Agent-Entscheidungen."""
    if not decisions:
        return None
    
    agent_counts = {}
    for dec in decisions:
        agent = dec.get("agent", "Unknown")
        agent_counts[agent] = agent_counts.get(agent, 0) + 1
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(agent_counts.keys()),
            y=list(agent_counts.values()),
            marker_color='#2c5282',
            text=list(agent_counts.values()),
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="🤖 Agent-Entscheidungen",
        xaxis_title="Agent",
        yaxis_title="Anzahl Entscheidungen",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=300
    )
    
    return fig


def create_timeline_chart(injects: list):
    """Erstellt eine interaktive Timeline-Visualisierung."""
    timeline_data = []
    for inj in injects:
        time_str = inj.time_offset.replace('T+', '')
        hours, minutes = map(int, time_str.split(':'))
        total_minutes = hours * 60 + minutes
        
        phase_color, _, _ = get_phase_color(inj.phase)
        
        timeline_data.append({
            "Time": total_minutes,
            "Inject": inj.inject_id,
            "Phase": inj.phase.value,
            "Phase Label": inj.phase.value.replace('_', ' ').title(),
            "MITRE": inj.technical_metadata.mitre_id or "N/A",
            "Content": inj.content[:60] + "..." if len(inj.content) > 60 else inj.content,
            "Color": phase_color
        })
    
    df = pd.DataFrame(timeline_data)
    
    fig = px.scatter(
        df,
        x="Time",
        y="Inject",
        color="Phase Label",
        size=[12] * len(df),
        hover_data=["MITRE", "Content"],
        title="⏱️ Szenario Timeline",
        labels={"Time": "Zeit (Minuten)", "Inject": "Inject ID"},
        color_discrete_map={
            "Normal Operation": "#38a169",
            "Suspicious Activity": "#d69e2e",
            "Initial Incident": "#ed8936",
            "Escalation Crisis": "#e53e3e",
            "Containment": "#805ad5",
            "Recovery": "#319795"
        }
    )
    
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial", size=12, color="#1a202c"),
        height=450,
        title_font=dict(size=18, color="#1a365d"),
        xaxis=dict(gridcolor="#e2e8f0"),
        yaxis=dict(gridcolor="#e2e8f0")
    )
    
    return fig


def create_phase_distribution_chart(injects: list):
    """Erstellt ein Phasen-Verteilungs-Diagramm."""
    phase_counts = {}
    phase_colors = {}
    for inj in injects:
        phase = inj.phase.value
        phase_counts[phase] = phase_counts.get(phase, 0) + 1
        if phase not in phase_colors:
            phase_color, _, _ = get_phase_color(inj.phase)
            phase_colors[phase] = phase_color
    
    fig = go.Figure(data=[
        go.Bar(
            x=[p.replace('_', ' ').title() for p in phase_counts.keys()],
            y=list(phase_counts.values()),
            marker_color=[phase_colors.get(p, "#718096") for p in phase_counts.keys()],
            text=list(phase_counts.values()),
            textposition='auto',
            textfont=dict(size=14, color="white", weight="bold"),
            marker_line=dict(color='rgba(0,0,0,0.1)', width=1)
        )
    ])
    
    fig.update_layout(
        title=dict(text="📊 Phasen-Verteilung", font=dict(size=18, color="#1a365d")),
        xaxis_title="Phase",
        yaxis_title="Anzahl Injects",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial", size=12, color="#1a202c"),
        height=450,
        xaxis=dict(gridcolor="#e2e8f0"),
        yaxis=dict(gridcolor="#e2e8f0", gridwidth=1)
    )
    
    return fig


def export_to_csv(injects: list) -> BytesIO:
    """Exportiert Injects als CSV."""
    data = []
    for inj in injects:
        data.append({
            "Inject ID": inj.inject_id,
            "Time Offset": inj.time_offset,
            "Phase": inj.phase.value,
            "Source": inj.source,
            "Target": inj.target,
            "Modality": inj.modality.value,
            "Content": inj.content,
            "MITRE ID": inj.technical_metadata.mitre_id or "",
            "Affected Assets": ", ".join(inj.technical_metadata.affected_assets),
            "DORA Tag": inj.dora_compliance_tag or "",
            "Business Impact": inj.business_impact or ""
        })
    
    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    return output


def export_to_json(injects: list) -> str:
    """Exportiert Injects als JSON."""
    data = [inj.model_dump() for inj in injects]
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


def main():
    """Hauptfunktion der Streamlit App."""
    init_session_state()
    
    # Enterprise Header
    st.markdown("""
    <div class="main-header">
        <h1>🛡️ DORA Szenariengenerator</h1>
        <div class="sub-header">
            Enterprise-Grade Krisenszenario-Generierung für Finanzunternehmen
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Premium Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="padding: 1.5rem 0 2rem 0;">
            <h2 style="color: white; margin: 0; font-size: 1.5rem;">⚙️ Konfiguration</h2>
            <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; font-size: 0.875rem;">
                Konfiguriere dein Szenario
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        scenario_type = st.selectbox(
            "🎭 Szenario-Typ",
            options=[st.value for st in ScenarioType],
            format_func=lambda x: x.replace("_", " ").title(),
            help="Wähle den Typ des zu generierenden Krisenszenarios"
        )
        
        max_iterations = st.slider(
            "📊 Anzahl Injects",
            min_value=1,
            max_value=20,
            value=5,
            help="Anzahl der zu generierenden Injects"
        )
        
        st.markdown("---")
        
        st.markdown("""
        <div style="padding: 1rem 0;">
            <h3 style="color: white; margin: 0 0 1rem 0; font-size: 1.1rem;">🔧 Erweiterte Optionen</h3>
        </div>
        """, unsafe_allow_html=True)
        
        auto_phase_transition = st.checkbox(
            "🔄 Automatische Phasen-Übergänge",
            value=True,
            help="Phasen werden automatisch basierend auf Kontext gewechselt"
        )
        
        show_validation_details = st.checkbox(
            "✅ Validierungsdetails anzeigen",
            value=False,
            help="Zeige detaillierte Validierungsinformationen"
        )
        
        # System Status
        st.markdown("---")
        st.markdown("""
        <div style="background: rgba(255,255,255,0.1); padding: 1.25rem; border-radius: 8px; backdrop-filter: blur(10px);">
            <h3 style="color: white; margin: 0 0 1rem 0; font-size: 1.1rem;">📡 System Status</h3>
            <div style="color: rgba(255,255,255,0.9); font-size: 0.875rem;">
                <p style="margin: 0.5rem 0;"><span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #38a169; margin-right: 8px; box-shadow: 0 0 8px #38a169;"></span>Neo4j Knowledge Graph</p>
                <p style="margin: 0.5rem 0;"><span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #38a169; margin-right: 8px; box-shadow: 0 0 8px #38a169;"></span>OpenAI GPT-4o</p>
                <p style="margin: 0.5rem 0;"><span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #38a169; margin-right: 8px; box-shadow: 0 0 8px #38a169;"></span>LangGraph Workflow</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Hauptbereich mit Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚀 Generierung", 
        "📊 Dashboard", 
        "📋 Injects", 
        "📈 Visualisierung",
        "🔍 Workflow Logs"
    ])
    
    with tab1:
        st.markdown("""
        <div class="enterprise-card">
            <h2 style="color: var(--text-primary); margin-top: 0; font-size: 1.75rem;">Szenario generieren</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
            <div class="enterprise-card" style="border-left: 4px solid var(--primary);">
                <h3 style="color: var(--text-primary); margin-top: 0; font-size: 1.25rem;">📋 Konfiguration</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                    <div>
                        <p style="margin: 0; font-size: 0.875rem; color: var(--text-secondary);"><strong>🎭 Szenario-Typ</strong></p>
                        <p style="margin: 0.5rem 0 0 0; color: var(--text-primary); font-weight: 500;">{scenario_type.replace('_', ' ').title()}</p>
                    </div>
                    <div>
                        <p style="margin: 0; font-size: 0.875rem; color: var(--text-secondary);"><strong>📊 Anzahl Injects</strong></p>
                        <p style="margin: 0.5rem 0 0 0; color: var(--text-primary); font-weight: 500;">{max_iterations}</p>
                    </div>
                </div>
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border);">
                    <p style="margin: 0; font-size: 0.875rem; color: var(--text-secondary);"><strong>🔄 Phasen-Übergänge:</strong> {'Automatisch' if auto_phase_transition else 'Manuell'}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("🎯 Szenario generieren", type="primary", use_container_width=True):
                with st.spinner("🔄 Generiere Szenario... (Dies kann einige Minuten dauern)"):
                    try:
                        if st.session_state.neo4j_client is None:
                            st.session_state.neo4j_client = Neo4jClient()
                            st.session_state.neo4j_client.connect()
                        
                        if st.session_state.workflow is None:
                            st.session_state.workflow = ScenarioWorkflow(
                                neo4j_client=st.session_state.neo4j_client,
                                max_iterations=max_iterations
                            )
                        
                        result = st.session_state.workflow.generate_scenario(
                            scenario_type=ScenarioType(scenario_type)
                        )
                        
                        st.session_state.scenario_result = result
                        
                        st.success(f"✅ Szenario erfolgreich generiert! ({len(result.get('injects', []))} Injects)")
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"❌ Fehler bei der Generierung: {e}")
                        import traceback
                        with st.expander("🔍 Detaillierte Fehlerinformationen"):
                            st.code(traceback.format_exc())
        
        if st.session_state.scenario_result:
            result = st.session_state.scenario_result
            st.markdown(f"""
            <div class="enterprise-card" style="border-left: 4px solid var(--success); background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);">
                <h3 style="color: #22543d; margin-top: 0; font-size: 1.25rem;">✅ Szenario erfolgreich generiert</h3>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem;">
                    <div>
                        <p style="margin: 0; font-size: 0.875rem; color: #22543d;"><strong>📋 Szenario ID</strong></p>
                        <code style="background: white; padding: 0.5rem; border-radius: 6px; display: block; margin-top: 0.5rem; color: var(--text-primary);">{result.get('scenario_id')}</code>
                    </div>
                    <div>
                        <p style="margin: 0; font-size: 0.875rem; color: #22543d;"><strong>🎯 Finale Phase</strong></p>
                        <p style="margin: 0.5rem 0 0 0; color: var(--text-primary); font-weight: 500;">{result.get('current_phase').value.replace('_', ' ').title()}</p>
                    </div>
                    <div>
                        <p style="margin: 0; font-size: 0.875rem; color: #22543d;"><strong>📊 Anzahl Injects</strong></p>
                        <p style="margin: 0.5rem 0 0 0; color: var(--text-primary); font-weight: 500; font-size: 1.5rem;">{len(result.get('injects', []))}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("""
        <div class="enterprise-card">
            <h2 style="color: var(--text-primary); margin-top: 0; font-size: 1.75rem;">📊 Dashboard & Analysen</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.scenario_result:
            result = st.session_state.scenario_result
            injects = result.get("injects", [])
            logs = result.get("workflow_logs", [])
            decisions = result.get("agent_decisions", [])
            
            if injects:
                # Metriken Cards
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{len(injects)}</div>
                        <div class="metric-label">Injects</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    unique_phases = len(set(inj.phase for inj in injects))
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{unique_phases}</div>
                        <div class="metric-label">Phasen</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    all_assets = set()
                    for inj in injects:
                        all_assets.update(inj.technical_metadata.affected_assets)
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{len(all_assets)}</div>
                        <div class="metric-label">Assets</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    mitre_ids = set(inj.technical_metadata.mitre_id for inj in injects if inj.technical_metadata.mitre_id)
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{len(mitre_ids)}</div>
                        <div class="metric-label">MITRE TTPs</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col5:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{len(logs)}</div>
                        <div class="metric-label">Workflow Logs</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Charts in Grid
                col_chart1, col_chart2 = st.columns(2)
                
                with col_chart1:
                    fig = create_phase_distribution_chart(injects)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col_chart2:
                    timeline_fig = create_timeline_chart(injects)
                    st.plotly_chart(timeline_fig, use_container_width=True)
                
                # Workflow Timeline
                if logs or decisions:
                    st.markdown("---")
                    st.subheader("⏱️ Workflow Timeline")
                    workflow_timeline = create_workflow_timeline(logs, decisions)
                    if workflow_timeline:
                        st.plotly_chart(workflow_timeline, use_container_width=True)
                
                # Agent-Entscheidungen
                if decisions:
                    st.markdown("---")
                    col_dec1, col_dec2 = st.columns(2)
                    
                    with col_dec1:
                        decision_chart = create_agent_decision_chart(decisions)
                        if decision_chart:
                            st.plotly_chart(decision_chart, use_container_width=True)
                    
                    with col_dec2:
                        st.subheader("🤖 Agent-Entscheidungen")
                        for i, dec in enumerate(decisions[-5:], 1):  # Letzte 5
                            agent = dec.get("agent", "Unknown")
                            decision_type = dec.get("decision_type", "Unknown")
                            output = dec.get("output", {})
                            
                            st.markdown(f"""
                            <div class="decision-card">
                                <p style="margin: 0 0 0.5rem 0; font-weight: 600; color: var(--primary-dark);">
                                    {agent} - {decision_type}
                                </p>
                                <p style="margin: 0; font-size: 0.875rem; color: var(--text-secondary);">
                                    {str(output.get('reasoning', output.get('selected_phase', 'N/A')))[:100]}...
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                
                # Phase-Übergänge analysieren
                st.markdown("---")
                st.subheader("🔄 Phasen-Übergänge")
                phase_transitions = []
                prev_phase = None
                for inj in injects:
                    if prev_phase and prev_phase != inj.phase:
                        phase_transitions.append({
                            "Von": prev_phase.value.replace('_', ' ').title(),
                            "Zu": inj.phase.value.replace('_', ' ').title(),
                            "Inject": inj.inject_id,
                            "Zeit": inj.time_offset
                        })
                    prev_phase = inj.phase
                
                if phase_transitions:
                    transitions_df = pd.DataFrame(phase_transitions)
                    st.dataframe(transitions_df, use_container_width=True, hide_index=True)
                else:
                    st.info("Keine Phasen-Übergänge in diesem Szenario")
                
            else:
                st.warning("Keine Daten verfügbar.")
        else:
            st.info("👈 Generiere zuerst ein Szenario im Tab 'Generierung'")
    
    with tab3:
        st.markdown("""
        <div class="enterprise-card">
            <h2 style="color: var(--text-primary); margin-top: 0; font-size: 1.75rem;">📋 Generierte Injects</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.scenario_result:
            result = st.session_state.scenario_result
            injects = result.get("injects", [])
            
            if injects:
                # Filter und Suche
                col_filter1, col_filter2, col_filter3 = st.columns(3)
                
                with col_filter1:
                    all_phases = ["Alle"] + [p.value for p in CrisisPhase]
                    selected_phase = st.selectbox(
                        "🔍 Filter nach Phase",
                        options=all_phases,
                        format_func=lambda x: x.replace("_", " ").title() if x != "Alle" else x
                    )
                    st.session_state.filter_phase = selected_phase if selected_phase != "Alle" else None
                
                with col_filter2:
                    search_term = st.text_input(
                        "🔎 Suche",
                        value=st.session_state.search_term,
                        placeholder="Suche in Inhalt, Assets, MITRE ID..."
                    )
                    st.session_state.search_term = search_term
                
                with col_filter3:
                    st.markdown(f"""
                    <div class="metric-card" style="padding: 1.25rem;">
                        <div class="metric-value" style="font-size: 2rem;">{len(injects)}</div>
                        <div class="metric-label">Injects</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Filter anwenden
                filtered_injects = injects
                if st.session_state.filter_phase:
                    filtered_injects = [inj for inj in filtered_injects if inj.phase.value == st.session_state.filter_phase]
                
                if st.session_state.search_term:
                    search_lower = st.session_state.search_term.lower()
                    filtered_injects = [
                        inj for inj in filtered_injects
                        if (search_lower in inj.content.lower() or
                            search_lower in ' '.join(inj.technical_metadata.affected_assets).lower() or
                            (inj.technical_metadata.mitre_id and search_lower in inj.technical_metadata.mitre_id.lower()))
                    ]
                
                st.markdown(f"**Angezeigt:** {len(filtered_injects)} von {len(injects)} Injects")
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Export-Buttons
                col_exp1, col_exp2 = st.columns(2)
                
                with col_exp1:
                    csv_data = export_to_csv(filtered_injects)
                    st.download_button(
                        label="📥 CSV Export",
                        data=csv_data,
                        file_name=f"scenario_{result.get('scenario_id')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col_exp2:
                    json_data = export_to_json(filtered_injects)
                    st.download_button(
                        label="📥 JSON Export",
                        data=json_data,
                        file_name=f"scenario_{result.get('scenario_id')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Injects anzeigen
                for i, inject in enumerate(filtered_injects, 1):
                    format_inject_card_safe(inject, i)
                
                if not filtered_injects:
                    st.warning("Keine Injects entsprechen den Filterkriterien.")
                
                # Fehler/Warnungen
                errors = result.get("errors", [])
                warnings = result.get("warnings", [])
                
                if errors or warnings:
                    st.markdown("---")
                    if errors:
                        st.error("**❌ Fehler:**")
                        for error in errors:
                            st.write(f"- {error}")
                    
                    if warnings:
                        st.warning("**⚠️ Warnungen:**")
                        for warning in warnings:
                            st.write(f"- {warning}")
            else:
                st.warning("Keine Injects generiert.")
        else:
            st.info("👈 Generiere zuerst ein Szenario im Tab 'Generierung'")
    
    with tab4:
        st.markdown("""
        <div class="enterprise-card">
            <h2 style="color: var(--text-primary); margin-top: 0; font-size: 1.75rem;">📈 Erweiterte Visualisierung</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.scenario_result:
            result = st.session_state.scenario_result
            injects = result.get("injects", [])
            
            if injects:
                # Assets-Übersicht
                st.subheader("🎯 Betroffene Assets")
                all_assets = set()
                asset_impact_count = {}
                for inj in injects:
                    for asset in inj.technical_metadata.affected_assets:
                        all_assets.add(asset)
                        asset_impact_count[asset] = asset_impact_count.get(asset, 0) + 1
                
                if all_assets:
                    # Asset-Impact Chart
                    asset_df = pd.DataFrame({
                        "Asset": list(asset_impact_count.keys()),
                        "Betroffen": list(asset_impact_count.values())
                    }).sort_values("Betroffen", ascending=False)
                    
                    fig_assets = px.bar(
                        asset_df,
                        x="Asset",
                        y="Betroffen",
                        title="📊 Asset-Impact Analyse",
                        color="Betroffen",
                        color_continuous_scale="Blues"
                    )
                    fig_assets.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        height=400
                    )
                    st.plotly_chart(fig_assets, use_container_width=True)
                    
                    # Asset Tags
                    asset_html = '<div style="display: flex; flex-wrap: wrap; gap: 0.75rem; margin-top: 1rem;">'
                    for asset, count in sorted(asset_impact_count.items(), key=lambda x: x[1], reverse=True):
                        asset_html += f'<span style="background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%); color: white; padding: 0.5rem 1rem; border-radius: 8px; font-size: 0.875rem; font-weight: 500; box-shadow: 0 2px 8px rgba(44, 82, 130, 0.2);">{html.escape(asset)} <span style="opacity: 0.8;">({count}x)</span></span>'
                    asset_html += '</div>'
                    st.markdown(asset_html, unsafe_allow_html=True)
                else:
                    st.info("Keine Assets betroffen")
                
                # MITRE TTP Analyse
                st.markdown("---")
                st.subheader("🔍 MITRE ATT&CK TTP Analyse")
                mitre_counts = {}
                for inj in injects:
                    mitre_id = inj.technical_metadata.mitre_id
                    if mitre_id:
                        mitre_counts[mitre_id] = mitre_counts.get(mitre_id, 0) + 1
                
                if mitre_counts:
                    mitre_df = pd.DataFrame({
                        "MITRE ID": list(mitre_counts.keys()),
                        "Verwendungen": list(mitre_counts.values())
                    }).sort_values("Verwendungen", ascending=False)
                    
                    st.dataframe(mitre_df, use_container_width=True, hide_index=True)
                else:
                    st.info("Keine MITRE IDs verfügbar")
            else:
                st.warning("Keine Daten für Visualisierung verfügbar.")
        else:
            st.info("👈 Generiere zuerst ein Szenario im Tab 'Generierung'")
    
    with tab5:
        st.markdown("""
        <div class="enterprise-card">
            <h2 style="color: var(--text-primary); margin-top: 0; font-size: 1.75rem;">🔍 Workflow Logs & Entscheidungen</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.scenario_result:
            result = st.session_state.scenario_result
            logs = result.get("workflow_logs", [])
            decisions = result.get("agent_decisions", [])
            
            if logs or decisions:
                # Workflow Logs
                if logs:
                    st.subheader("📋 Workflow Logs")
                    for log in logs:
                        node = log.get("node", "Unknown")
                        action = log.get("action", "")
                        details = log.get("details", {})
                        timestamp = log.get("timestamp", "")
                        status = details.get("status", "unknown")
                        
                        status_color = {
                            "success": "#38a169",
                            "error": "#e53e3e",
                            "warning": "#d69e2e"
                        }.get(status, "#718096")
                        
                        st.markdown(f"""
                        <div class="log-entry" style="border-left-color: {status_color};">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <strong style="color: var(--primary-dark);">{node}</strong>
                                <span style="color: var(--text-secondary); font-size: 0.75rem;">{timestamp.split('T')[1][:8] if 'T' in timestamp else timestamp}</span>
                            </div>
                            <p style="margin: 0.25rem 0; color: var(--text-primary);">{action}</p>
                            <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary); font-size: 0.8rem;">
                                {json.dumps(details, indent=2, ensure_ascii=False)[:200]}...
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Agent-Entscheidungen
                if decisions:
                    st.markdown("---")
                    st.subheader("🤖 Agent-Entscheidungen")
                    
                    for dec in decisions:
                        agent = dec.get("agent", "Unknown")
                        decision_type = dec.get("decision_type", "Unknown")
                        input_data = dec.get("input", {})
                        output_data = dec.get("output", {})
                        timestamp = dec.get("timestamp", "")
                        
                        with st.expander(f"🔹 {agent} - {decision_type} ({timestamp.split('T')[1][:8] if 'T' in timestamp else timestamp})"):
                            col_dec1, col_dec2 = st.columns(2)
                            
                            with col_dec1:
                                st.markdown("**📥 Input:**")
                                st.json(input_data)
                            
                            with col_dec2:
                                st.markdown("**📤 Output:**")
                                st.json(output_data)
                else:
                    st.info("Keine Agent-Entscheidungen verfügbar")
            else:
                st.info("Keine Workflow-Logs verfügbar. Generiere ein neues Szenario, um Logs zu sehen.")
        else:
            st.info("👈 Generiere zuerst ein Szenario im Tab 'Generierung'")
    
    # Enterprise Footer
    st.markdown("""
    <div style="text-align: center; padding: 2.5rem 1rem; margin-top: 4rem; border-top: 1px solid var(--border); background: var(--surface); border-radius: 12px;">
        <p style="margin: 0; color: var(--text-primary); font-weight: 600; font-size: 1.1rem;">
            🛡️ DORA-konformer Szenariengenerator MVP
        </p>
        <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary); font-size: 0.875rem;">
            Powered by LangGraph • OpenAI GPT-4o • Neo4j • Streamlit
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()


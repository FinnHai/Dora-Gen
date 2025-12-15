"""
Streamlit Frontend für den DORA-Szenariengenerator.

Bietet eine benutzerfreundliche UI für:
- Parametereingabe (Szenario-Typ, Anzahl Injects, etc.)
- Szenario-Generierung
- Visualisierung der Ergebnisse
- Export-Funktionalität
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from io import BytesIO

from neo4j_client import Neo4jClient
from workflows.scenario_workflow import ScenarioWorkflow
from state_models import ScenarioType, CrisisPhase, Inject
import os
from dotenv import load_dotenv

load_dotenv()

# Streamlit Konfiguration
st.set_page_config(
    page_title="DORA Szenariengenerator",
    page_icon="🎯",
    layout="wide"
)

# CSS für besseres Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .inject-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .phase-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        font-weight: 600;
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


def get_phase_color(phase: CrisisPhase) -> str:
    """Gibt eine Farbe für eine Phase zurück."""
    colors = {
        CrisisPhase.NORMAL_OPERATION: "#28a745",
        CrisisPhase.SUSPICIOUS_ACTIVITY: "#ffc107",
        CrisisPhase.INITIAL_INCIDENT: "#fd7e14",
        CrisisPhase.ESCALATION_CRISIS: "#dc3545",
        CrisisPhase.CONTAINMENT: "#6f42c1",
        CrisisPhase.RECOVERY: "#20c997"
    }
    return colors.get(phase, "#6c757d")


def format_inject_card(inject: Inject, index: int):
    """Formatiert eine Inject-Karte für die Anzeige."""
    phase_color = get_phase_color(inject.phase)
    
    st.markdown(f"""
    <div class="inject-card">
        <h4>🔹 {inject.inject_id} - {inject.time_offset}</h4>
        <p><strong>Phase:</strong> <span class="phase-badge" style="background-color: {phase_color}; color: white;">{inject.phase.value}</span></p>
        <p><strong>Quelle:</strong> {inject.source} → <strong>Ziel:</strong> {inject.target}</p>
        <p><strong>Modalität:</strong> {inject.modality.value}</p>
        <p><strong>Inhalt:</strong> {inject.content}</p>
        <p><strong>MITRE ID:</strong> {inject.technical_metadata.mitre_id or 'N/A'}</p>
        <p><strong>Betroffene Assets:</strong> {', '.join(inject.technical_metadata.affected_assets) if inject.technical_metadata.affected_assets else 'Keine'}</p>
        {f'<p><strong>DORA Tag:</strong> {inject.dora_compliance_tag}</p>' if inject.dora_compliance_tag else ''}
        {f'<p><strong>Business Impact:</strong> {inject.business_impact}</p>' if inject.business_impact else ''}
    </div>
    """, unsafe_allow_html=True)


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
    
    # Header
    st.markdown('<div class="main-header">🎯 DORA-konformer Szenariengenerator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Generiere realistische Krisenszenarien für Finanzunternehmen</div>', unsafe_allow_html=True)
    
    # Sidebar für Konfiguration
    with st.sidebar:
        st.header("⚙️ Konfiguration")
        
        scenario_type = st.selectbox(
            "Szenario-Typ",
            options=[st.value for st in ScenarioType],
            format_func=lambda x: x.replace("_", " ").title()
        )
        
        max_iterations = st.slider(
            "Anzahl Injects",
            min_value=1,
            max_value=20,
            value=5,
            help="Anzahl der zu generierenden Injects"
        )
        
        st.divider()
        
        st.subheader("🔧 Erweiterte Optionen")
        
        auto_phase_transition = st.checkbox(
            "Automatische Phasen-Übergänge",
            value=True,
            help="Phasen werden automatisch basierend auf Kontext gewechselt"
        )
        
        show_validation_details = st.checkbox(
            "Validierungsdetails anzeigen",
            value=False,
            help="Zeige detaillierte Validierungsinformationen"
        )
    
    # Hauptbereich
    tab1, tab2, tab3 = st.tabs(["🚀 Generierung", "📊 Ergebnisse", "📈 Visualisierung"])
    
    with tab1:
        st.header("Szenario generieren")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(f"**Szenario-Typ:** {scenario_type.replace('_', ' ').title()}")
            st.write(f"**Anzahl Injects:** {max_iterations}")
        
        with col2:
            if st.button("🎯 Szenario generieren", type="primary", use_container_width=True):
                with st.spinner("Generiere Szenario... (Dies kann einige Minuten dauern)"):
                    try:
                        # Initialisiere Neo4j Client
                        if st.session_state.neo4j_client is None:
                            st.session_state.neo4j_client = Neo4jClient()
                            st.session_state.neo4j_client.connect()
                        
                        # Initialisiere Workflow
                        if st.session_state.workflow is None:
                            st.session_state.workflow = ScenarioWorkflow(
                                neo4j_client=st.session_state.neo4j_client,
                                max_iterations=max_iterations
                            )
                        
                        # Generiere Szenario
                        result = st.session_state.workflow.generate_scenario(
                            scenario_type=ScenarioType(scenario_type)
                        )
                        
                        st.session_state.scenario_result = result
                        
                        st.success(f"✅ Szenario erfolgreich generiert! ({len(result.get('injects', []))} Injects)")
                        
                    except Exception as e:
                        st.error(f"❌ Fehler bei der Generierung: {e}")
                        import traceback
                        st.code(traceback.format_exc())
        
        # Status-Anzeige
        if st.session_state.scenario_result:
            result = st.session_state.scenario_result
            st.info(f"📋 Szenario ID: {result.get('scenario_id')} | Finale Phase: {result.get('current_phase').value}")
    
    with tab2:
        st.header("Generierte Injects")
        
        if st.session_state.scenario_result:
            result = st.session_state.scenario_result
            injects = result.get("injects", [])
            
            if injects:
                # Export-Buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    csv_data = export_to_csv(injects)
                    st.download_button(
                        label="📥 Als CSV exportieren",
                        data=csv_data,
                        file_name=f"scenario_{result.get('scenario_id')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    json_data = export_to_json(injects)
                    st.download_button(
                        label="📥 Als JSON exportieren",
                        data=json_data,
                        file_name=f"scenario_{result.get('scenario_id')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                
                with col3:
                    st.write(f"**Anzahl Injects:** {len(injects)}")
                
                st.divider()
                
                # Injects anzeigen
                for i, inject in enumerate(injects, 1):
                    format_inject_card(inject, i)
                
                # Fehler/Warnungen
                errors = result.get("errors", [])
                warnings = result.get("warnings", [])
                
                if errors or warnings:
                    st.divider()
                    st.subheader("⚠️ Fehler & Warnungen")
                    
                    if errors:
                        st.error("**Fehler:**")
                        for error in errors:
                            st.write(f"- {error}")
                    
                    if warnings:
                        st.warning("**Warnungen:**")
                        for warning in warnings:
                            st.write(f"- {warning}")
            else:
                st.warning("Keine Injects generiert.")
        else:
            st.info("👈 Generiere zuerst ein Szenario im Tab 'Generierung'")
    
    with tab3:
        st.header("Visualisierung")
        
        if st.session_state.scenario_result:
            result = st.session_state.scenario_result
            injects = result.get("injects", [])
            
            if injects:
                # Phasen-Verteilung
                st.subheader("📊 Phasen-Verteilung")
                phase_counts = {}
                for inj in injects:
                    phase = inj.phase.value
                    phase_counts[phase] = phase_counts.get(phase, 0) + 1
                
                phase_df = pd.DataFrame({
                    "Phase": list(phase_counts.keys()),
                    "Anzahl": list(phase_counts.values())
                })
                
                st.bar_chart(phase_df.set_index("Phase"))
                
                # Timeline
                st.subheader("⏱️ Timeline")
                timeline_data = []
                for inj in injects:
                    timeline_data.append({
                        "Inject": inj.inject_id,
                        "Time Offset": inj.time_offset,
                        "Phase": inj.phase.value,
                        "MITRE ID": inj.technical_metadata.mitre_id or "N/A"
                    })
                
                timeline_df = pd.DataFrame(timeline_data)
                st.dataframe(timeline_df, use_container_width=True)
                
                # Assets-Übersicht
                st.subheader("🎯 Betroffene Assets")
                all_assets = set()
                for inj in injects:
                    all_assets.update(inj.technical_metadata.affected_assets)
                
                if all_assets:
                    st.write(", ".join(sorted(all_assets)))
                else:
                    st.info("Keine Assets betroffen")
            else:
                st.warning("Keine Daten für Visualisierung verfügbar.")
        else:
            st.info("👈 Generiere zuerst ein Szenario im Tab 'Generierung'")
    
    # Footer
    st.divider()
    st.markdown(
        "<div style='text-align: center; color: #666;'>DORA-konformer Szenariengenerator MVP | "
        "Powered by LangGraph, OpenAI & Neo4j</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()


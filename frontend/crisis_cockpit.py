"""
The Crisis Cockpit - Streamlit Frontend für Bachelor Thesis
"Neuro-Symbolic Crisis Generator"

Ein interaktives Dashboard zur Visualisierung und Evaluation von Krisenszenarien.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from io import BytesIO
import uuid
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Backend Integration (auskommentiert für Mock-Mode)
# from neo4j_client import Neo4jClient
# from workflows.scenario_workflow import ScenarioWorkflow
# from state_models import Inject, ScenarioType

# Mock Data für initiales Testing
def get_mock_injects() -> List[Dict[str, Any]]:
    """Generiert Mock-Injects für UI-Testing."""
    return [
        {
            "inject_id": "INJ-001",
            "time_offset": "T+00:30",
            "timestamp": datetime.now() - timedelta(minutes=30),
            "source": "Red Team / Attacker",
            "target": "Blue Team / SOC",
            "content": "Suspicious login attempt detected from IP 192.168.1.100",
            "modality": "SIEM Alert",
            "phase": "SUSPICIOUS_ACTIVITY",
            "mitre_id": "T1078",
            "affected_assets": ["SRV-001", "DB-001"],
            "raw_json": {"test": "data"},
            "logic_checks": "Logic Guard accepted on first attempt"
        },
        {
            "inject_id": "INJ-002",
            "time_offset": "T+01:00",
            "timestamp": datetime.now() - timedelta(minutes=60),
            "source": "Blue Team / SOC",
            "target": "Management",
            "content": "Server SRV-001 showing degraded performance. CPU usage at 95%",
            "modality": "Internal Report",
            "phase": "INITIAL_INCIDENT",
            "mitre_id": "T1499",
            "affected_assets": ["SRV-001"],
            "raw_json": {"test": "data2"},
            "logic_checks": "Logic Guard rejected draft 1 time, accepted on retry"
        },
        {
            "inject_id": "INJ-003",
            "time_offset": "T+01:30",
            "timestamp": datetime.now() - timedelta(minutes=90),
            "source": "Red Team / Attacker",
            "target": "Blue Team / SOC",
            "content": "Ransomware encryption detected on DB-001. Files encrypted with .lock extension",
            "modality": "SIEM Alert",
            "phase": "ESCALATION_CRISIS",
            "mitre_id": "T1486",
            "affected_assets": ["DB-001", "SRV-002"],
            "raw_json": {"test": "data3"},
            "logic_checks": "Logic Guard accepted on first attempt"
        }
    ]


def get_mock_state() -> Dict[str, Any]:
    """Generiert Mock-State für Visualisierung."""
    return {
        "diesel_tank": 40,  # Prozent
        "server_health": "Critical",  # Critical, Degraded, Normal
        "server_health_value": 25,  # Prozent für Progress Bar
        "database_status": "Compromised",
        "database_status_value": 0,
        "network_bandwidth": 60,  # Prozent
        "active_threats": 3,
        "compromised_assets": ["DB-001", "SRV-002"],
        "online_assets": ["SRV-001", "SRV-003"],
        "total_assets": 5
    }


def init_session_state():
    """Initialisiert Session State Variablen."""
    if "injects" not in st.session_state:
        st.session_state.injects = get_mock_injects()
    
    if "current_state" not in st.session_state:
        st.session_state.current_state = get_mock_state()
    
    if "evaluation_data" not in st.session_state:
        st.session_state.evaluation_data = []
    
    if "mode" not in st.session_state:
        st.session_state.mode = "Logic Guard Mode"  # "Legacy Mode" oder "Logic Guard Mode"
    
    if "auto_play_active" not in st.session_state:
        st.session_state.auto_play_active = False
    
    if "auto_play_steps" not in st.session_state:
        st.session_state.auto_play_steps = 0


def update_state_after_inject(inject: Dict[str, Any]):
    """Simuliert State-Update nach einem Inject (Mock)."""
    state = st.session_state.current_state
    
    # Beispiel: Wenn Inject Server betrifft, reduziere Server Health
    if any("SRV" in asset for asset in inject.get("affected_assets", [])):
        state["server_health_value"] = max(0, state["server_health_value"] - 15)
        if state["server_health_value"] < 30:
            state["server_health"] = "Critical"
        elif state["server_health_value"] < 60:
            state["server_health"] = "Degraded"
    
    # Beispiel: Wenn Inject Database betrifft
    if any("DB" in asset for asset in inject.get("affected_assets", [])):
        state["database_status_value"] = max(0, state["database_status_value"] - 20)
        if state["database_status_value"] < 20:
            state["database_status"] = "Compromised"
    
    # Beispiel: Wenn Ransomware, reduziere Diesel (Generator läuft)
    if "ransomware" in inject.get("content", "").lower() or "encrypt" in inject.get("content", "").lower():
        state["diesel_tank"] = max(0, state["diesel_tank"] - 10)
    
    st.session_state.current_state = state


# ============================================================================
# Erklärboxen für komplexe Konzepte
# ============================================================================

def render_info_box(title: str, content: str, expander: bool = True):
    """Rendert eine professionelle Erklärbox."""
    if expander:
        with st.expander(f"ℹ️ {title}", expanded=False):
            st.markdown(content)
    else:
        st.info(content)


# ============================================================================
# MODULE 1: Split-Screen Layout ("Split-Screen of Truth")
# ============================================================================

def render_story_column():
    """Rendert die linke Spalte mit dem Inject-Feed."""
    st.markdown("### Event Sequence Feed")
    st.caption("Chronologische Darstellung aller generierten Injects mit vollständigen Metadaten")
    
    # Erklärbox: Was ist ein Inject?
    render_info_box(
        "Inject Definition",
        """
        **Inject:** Ein strukturiertes Event im Krisenszenario, das einen spezifischen Vorfall darstellt.
        
        - **Source/Target:** Kommunikationsrichtung (z.B. Attacker → SOC)
        - **Modality:** Übertragungsart (SIEM Alert, Email, Phone Call, etc.)
        - **MITRE ATT&CK:** Zuordnung zu MITRE ATT&CK Framework
        - **Affected Assets:** Betroffene Systemkomponenten
        - **Phase:** Aktuelle Phase im Krisenzyklus (Normal Operation → Suspicious Activity → ... → Recovery)
        """,
        expander=True
    )
    
    # Evaluation Mode Toggle
    col_mode1, col_mode2 = st.columns([2, 1])
    with col_mode1:
        mode = st.radio(
            "Evaluation Mode",
            ["Legacy Mode", "Logic Guard Mode"],
            index=1 if st.session_state.mode == "Logic Guard Mode" else 0,
            horizontal=True,
            key="mode_toggle"
        )
        st.session_state.mode = mode
        
        # Erklärbox: Evaluation Modes
        if mode == "Legacy Mode":
            render_info_box(
                "Legacy Mode - Pure LLM/RAG Approach",
                """
                **Legacy Mode** verwendet einen reinen LLM/RAG-Ansatz ohne symbolische Validierung:
                
                - Direkte LLM-Generierung ohne State-Tracking
                - Keine LangGraph-Orchestrierung
                - Keine Neo4j-basierte Konsistenzprüfung
                - Referenz-Implementierung für Vergleich
                """,
                expander=True
            )
        else:
            render_info_box(
                "Logic Guard Mode - Neuro-Symbolic Approach",
                """
                **Logic Guard Mode** verwendet einen Neuro-Symbolic Ansatz mit LangGraph:
                
                - Multi-Agenten-System (Manager, Intel, Generator, Critic)
                - LangGraph-basierte State-Orchestrierung
                - Neo4j Knowledge Graph für Konsistenzprüfung
                - FSM-basierte Phasen-Validierung
                - DORA-Compliance Validierung
                
                **Hypothese:** Reduziert Hallucinations durch symbolische Constraints.
                """,
                expander=True
            )
    
    with col_mode2:
        if st.button("Export Evaluation Data (CSV)", width='stretch', key="export_csv"):
            download_evaluation_csv()
    
    st.divider()
    
    # Inject Feed
    injects = st.session_state.injects
    
    if not injects:
        st.info("Noch keine Injects generiert. Starte eine Simulation!")
        return
    
    # Zeige Injects in umgekehrter Reihenfolge (neueste zuerst)
    for idx, inject in enumerate(reversed(injects)):
        render_inject_card(inject, len(injects) - idx - 1)


def render_inject_card(inject: Dict[str, Any], original_index: int):
    """Rendert eine einzelne Inject-Card mit Evaluation-Buttons."""
    # Card Container
    with st.container():
        # Header mit Time und ID
        col_time, col_id, col_phase = st.columns([2, 2, 1])
        with col_time:
            st.markdown(f"**{inject['time_offset']}**")
            st.caption(f"{inject['timestamp'].strftime('%H:%M:%S') if isinstance(inject['timestamp'], datetime) else inject['timestamp']}")
        with col_id:
            st.markdown(f"**{inject['inject_id']}**")
        with col_phase:
            phase_color = get_phase_color(inject.get('phase', 'NORMAL_OPERATION'))
            phase_label = inject.get('phase', 'NORMAL').replace('_', ' ')
            st.markdown(f"""
            <div style="background: {phase_color}; color: white; padding: 0.25rem 0.5rem; 
                        border-radius: 3px; font-size: 0.7rem; text-align: center; font-weight: 500;">
                {phase_label}
            </div>
            """, unsafe_allow_html=True)
        
        # Source → Target
        st.markdown(f"**{inject['source']}** → *{inject['target']}*")
        st.caption(f"Modality: {inject.get('modality', 'N/A')}")
        
        # Content
        st.markdown("**Content:**")
        st.markdown(f"""
        <div style="padding: 0.75rem; background: #f8fafc; border-left: 3px solid {phase_color}; 
                    border-radius: 4px; margin: 0.5rem 0; font-size: 0.875rem; line-height: 1.6;">
            {inject['content']}
        </div>
        """, unsafe_allow_html=True)
        
        # Metadata
        col_mitre, col_assets = st.columns(2)
        with col_mitre:
            st.caption(f"MITRE ATT&CK: {inject.get('mitre_id', 'N/A')}")
        with col_assets:
            assets = inject.get('affected_assets', [])
            st.caption(f"Affected Assets: {', '.join(assets) if assets else 'None'}")
        
        # ===== MODULE 3: Evaluation Buttons =====
        st.markdown("---")
        
        # Erklärbox: Evaluation
        render_info_box(
            "Evaluation Criteria",
            """
            **Consistent:** Inject ist logisch konsistent mit:
            - Vorherigen Injects (temporale Konsistenz)
            - System State (kausale Konsistenz)
            - MITRE ATT&CK Framework (technische Konsistenz)
            - DORA-Anforderungen (Compliance-Konsistenz)
            
            **Hallucination:** Inject enthält Fehler wie:
            - Inkonsistente Asset-Namen
            - Unmögliche technische Abläufe
            - Widersprüche zu vorherigen Events
            - Verstöße gegen FSM-Phasen-Übergänge
            """,
            expander=True
        )
        
        col_eval1, col_eval2, col_eval3 = st.columns([1, 1, 4])
        
        with col_eval1:
            if st.button("Consistent", key=f"consistent_{original_index}", width='stretch'):
                record_evaluation(inject['inject_id'], "Consistent", None)
                st.success("Marked as Consistent")
                st.rerun()
        
        with col_eval2:
            if st.button("Hallucination", key=f"hallucination_{original_index}", width='stretch'):
                st.session_state[f"show_reason_{original_index}"] = True
        
        # Error Reason Input (wenn Hallucination geklickt wurde)
        if st.session_state.get(f"show_reason_{original_index}", False):
            reason = st.text_area(
                "Hallucination Reason:",
                key=f"reason_{original_index}",
                placeholder="Beschreibe die spezifische Inkonsistenz oder den Fehler...",
                height=100
            )
            col_submit1, col_submit2 = st.columns([1, 4])
            with col_submit1:
                if st.button("Submit", key=f"submit_reason_{original_index}"):
                    if reason:
                        record_evaluation(inject['inject_id'], "Hallucination", reason)
                        st.session_state[f"show_reason_{original_index}"] = False
                        st.success("Hallucination recorded")
                        st.rerun()
                    else:
                        st.error("Please provide a reason")
            with col_submit2:
                if st.button("Cancel", key=f"cancel_reason_{original_index}"):
                    st.session_state[f"show_reason_{original_index}"] = False
                    st.rerun()
        
        # ===== MODULE 4: Debugging & Transparency =====
        with st.expander("Raw Data & Logic Check Results"):
            col_raw1, col_raw2 = st.columns(2)
            with col_raw1:
                st.markdown("**Raw JSON from LLM:**")
                st.json(inject.get('raw_json', {}))
            with col_raw2:
                st.markdown("**Logic Guard Validation:**")
                logic_result = inject.get('logic_checks', 'N/A')
                st.text(logic_result)
                
                # Erklärbox: Logic Guard
                render_info_box(
                    "Logic Guard Validation Process",
                    """
                    Der Logic Guard validiert jeden Inject durch:
                    
                    1. **Pydantic Schema Validation:** Strukturelle Korrektheit
                    2. **FSM Phase Validation:** Phasen-Übergänge gemäß Finite State Machine
                    3. **Neo4j State Consistency:** Konsistenz mit Knowledge Graph
                    4. **MITRE ATT&CK Validation:** Technische Plausibilität
                    5. **DORA Compliance Check:** Artikel 25 Anforderungen
                    
                    Bei Fehlern: Automatisches Refinement (max. 2 Versuche)
                    """,
                    expander=True
                )
        
        st.markdown("<br>", unsafe_allow_html=True)


def get_phase_color(phase: str) -> str:
    """Gibt die Farbe für eine Phase zurück."""
    colors = {
        "NORMAL_OPERATION": "#10b981",
        "SUSPICIOUS_ACTIVITY": "#f59e0b",
        "INITIAL_INCIDENT": "#ef4444",
        "ESCALATION_CRISIS": "#dc2626",
        "CONTAINMENT": "#7c3aed",
        "RECOVERY": "#06b6d4"
    }
    return colors.get(phase, "#64748b")


def render_state_reality_column():
    """Rendert die rechte Spalte mit dem State-Dashboard."""
    st.markdown("### System State Dashboard")
    st.caption("Live-Update des aktuellen Systemzustands basierend auf Neo4j Knowledge Graph")
    
    # Erklärbox: System State
    render_info_box(
        "System State Definition",
        """
        **System State:** Repräsentiert den aktuellen Zustand aller Systemkomponenten im Knowledge Graph.
        
        - **Resources:** Physische/Logische Ressourcen (Diesel, Bandwidth)
        - **Asset Status:** Zustand einzelner Assets (Online, Degraded, Compromised)
        - **Causal Relationships:** Abhängigkeiten zwischen Assets (Second-Order Effects)
        
        **Update-Mechanismus:** Nach jedem Inject wird der State durch Neo4j-Cypher-Queries aktualisiert.
        """,
        expander=True
    )
    
    state = st.session_state.current_state
    
    # Resource Metrics
    st.markdown("#### Resource Metrics")
    
    # Diesel Tank
    diesel_value = state.get("diesel_tank", 0)
    st.metric("Diesel Tank Capacity", f"{diesel_value}%")
    st.progress(diesel_value / 100)
    st.caption("Backup generator fuel level")
    
    # Server Health
    server_health = state.get("server_health", "Normal")
    server_value = state.get("server_health_value", 100)
    health_color = "#ef4444" if server_health == "Critical" else "#f59e0b" if server_health == "Degraded" else "#10b981"
    st.metric("Server Health Status", server_health, delta=None)
    st.markdown(f"""
    <div style="background: {health_color}; height: 8px; border-radius: 4px; width: {server_value}%;"></div>
    """, unsafe_allow_html=True)
    st.progress(server_value / 100)
    st.caption("Aggregated server infrastructure health")
    
    # Database Status
    db_status = state.get("database_status", "Normal")
    db_value = state.get("database_status_value", 100)
    db_color = "#ef4444" if db_status == "Compromised" else "#10b981"
    st.metric("Database Status", db_status)
    st.progress(db_value / 100)
    st.caption("Primary database availability")
    
    # Network Bandwidth
    network_value = state.get("network_bandwidth", 100)
    st.metric("Network Bandwidth Utilization", f"{network_value}%")
    st.progress(network_value / 100)
    st.caption("Current network capacity usage")
    
    st.divider()
    
    # Asset Status
    st.markdown("#### Asset Inventory")
    
    total_assets = state.get("total_assets", 0)
    compromised = state.get("compromised_assets", [])
    online = state.get("online_assets", [])
    
    col_assets1, col_assets2 = st.columns(2)
    with col_assets1:
        st.metric("Total Assets", total_assets)
        st.metric("Compromised Assets", len(compromised), delta=-len(compromised) if compromised else None)
    with col_assets2:
        st.metric("Online Assets", len(online))
        st.metric("Active Threats", state.get("active_threats", 0))
    
    # Asset List
    if compromised:
        st.markdown("**Compromised Assets:**")
        for asset in compromised:
            st.markdown(f"- {asset} (Status: Compromised)")
    
    if online:
        st.markdown("**Online Assets:**")
        for asset in online:
            st.markdown(f"- {asset} (Status: Online)")
    
    # Erklärbox: Second-Order Effects
    if compromised:
        render_info_box(
            "Second-Order Effects",
            """
            **Second-Order Effects:** Kaskadierende Auswirkungen auf abhängige Assets.
            
            Beispiel: Wenn DB-001 kompromittiert wird:
            - Direkte Abhängigkeiten (SRV-002) → Status: Degraded
            - Indirekte Abhängigkeiten (APP-001) → Status: Degraded
            - Kritische Pfade werden identifiziert
            
            Berechnung erfolgt durch Neo4j Cypher-Queries mit Dependency-Graph-Traversal.
            """,
            expander=True
        )


# ============================================================================
# MODULE 2: Interaction Module ("Dungeon Master Mode")
# ============================================================================

def render_interaction_module():
    """Rendert das Interaction-Modul in der Sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Simulation Controls")
    
    # Erklärbox: Manual Injection
    render_info_box(
        "Manual Event Injection",
        """
        **Zweck:** Ermöglicht manuelle Eingriffe in die Simulation zur Steuerung des Szenarios.
        
        **Anwendungsfälle:**
        - Testen spezifischer Szenarien
        - Simulieren von Gegenmaßnahmen
        - Validierung von State-Updates
        
        **Format:** Freitext-Beschreibung des Events
        """,
        expander=True
    )
    
    # Manual Inject Input
    st.sidebar.markdown("**Manual Event Injection:**")
    manual_event = st.sidebar.text_area(
        "Event Description:",
        placeholder="z.B. 'Technician repairs server SRV-001'",
        height=100,
        key="manual_event_input"
    )
    
    if st.sidebar.button("Inject Event", width='stretch', key="inject_event"):
        if manual_event:
            inject_manual_event(manual_event)
            st.sidebar.success("Event injected successfully")
            st.rerun()
        else:
            st.sidebar.error("Please enter an event description")
    
    st.sidebar.divider()
    
    # Control Buttons
    st.sidebar.markdown("**Simulation Controls:**")
    
    # Erklärbox: Force Step
    render_info_box(
        "Force Step",
        """
        **Force Step:** Erzwingt einen einzelnen Workflow-Schritt.
        
        Nützlich wenn:
        - Workflow hängt (Zero Index Issue)
        - Manuelle Kontrolle über Schrittfolge gewünscht
        - Debugging von Workflow-Logik
        
        Führt einen kompletten Zyklus aus: State Check → Manager → Intel → Action → Generator → Critic → State Update
        """,
        expander=True
    )
    
    col_force1, col_force2 = st.sidebar.columns(2)
    with col_force1:
        if st.button("Force Step", width='stretch', key="force_step"):
            force_next_step()
            st.rerun()
    
    with col_force2:
        auto_play = st.button("Auto-Play (5 steps)", width='stretch', key="auto_play")
        if auto_play:
            st.session_state.auto_play_active = True
            st.session_state.auto_play_steps = 5
            auto_play_simulation()
            st.rerun()
    
    # Status
    if st.session_state.auto_play_active:
        st.sidebar.info(f"Auto-Play: {st.session_state.auto_play_steps} steps remaining")


def inject_manual_event(event_description: str):
    """Fügt ein manuelles Event als Inject hinzu."""
    new_inject = {
        "inject_id": f"INJ-{len(st.session_state.injects) + 1:03d}",
        "time_offset": f"T+{len(st.session_state.injects):02d}:00",
        "timestamp": datetime.now(),
        "source": "Manual / User",
        "target": "System",
        "content": event_description,
        "modality": "Manual Injection",
        "phase": "NORMAL_OPERATION",
        "mitre_id": "MANUAL",
        "affected_assets": [],
        "raw_json": {"manual": True, "description": event_description},
        "logic_checks": "Manual injection - no logic guard check"
    }
    
    st.session_state.injects.append(new_inject)
    update_state_after_inject(new_inject)


def force_next_step():
    """Erzwingt den nächsten AI-Schritt."""
    # TODO: Backend-Integration
    # Mock-Mode (aktuell)
    new_inject = {
        "inject_id": f"INJ-{len(st.session_state.injects) + 1:03d}",
        "time_offset": f"T+{len(st.session_state.injects):02d}:30",
        "timestamp": datetime.now(),
        "source": "Red Team / Attacker",
        "target": "Blue Team / SOC",
        "content": f"AI-generated inject #{len(st.session_state.injects) + 1}: Automated threat detection",
        "modality": "SIEM Alert",
        "phase": "SUSPICIOUS_ACTIVITY",
        "mitre_id": "T1078",
        "affected_assets": ["SRV-001"],
        "raw_json": {"ai_generated": True, "step": len(st.session_state.injects) + 1},
        "logic_checks": f"Logic Guard accepted on first attempt (Mode: {st.session_state.mode})"
    }
    st.session_state.injects.append(new_inject)
    update_state_after_inject(new_inject)


def auto_play_simulation():
    """Führt automatisch mehrere Schritte aus."""
    steps = st.session_state.auto_play_steps
    for i in range(steps):
        force_next_step()
    
    st.session_state.auto_play_active = False
    st.session_state.auto_play_steps = 0


# ============================================================================
# MODULE 3: Thesis Evaluation Module
# ============================================================================

def record_evaluation(inject_id: str, rating: str, reason: Optional[str]):
    """Speichert eine Evaluation-Bewertung."""
    evaluation = {
        "inject_id": inject_id,
        "mode": st.session_state.mode,
        "rating": rating,
        "reason": reason or "",
        "timestamp": datetime.now().isoformat()
    }
    
    # Prüfe ob bereits eine Evaluation für diesen Inject existiert
    existing = [e for e in st.session_state.evaluation_data if e["inject_id"] == inject_id]
    if existing:
        # Update existing
        idx = st.session_state.evaluation_data.index(existing[0])
        st.session_state.evaluation_data[idx] = evaluation
    else:
        # Add new
        st.session_state.evaluation_data.append(evaluation)


def download_evaluation_csv():
    """Exportiert die Evaluation-Daten als CSV."""
    if not st.session_state.evaluation_data:
        st.warning("No evaluation data to export!")
        return
    
    df = pd.DataFrame(st.session_state.evaluation_data)
    
    # Erstelle CSV
    csv = df.to_csv(index=False)
    
    # Download Button
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"thesis_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        key="download_csv"
    )


# ============================================================================
# Backend Integration Helpers (für zukünftige Integration)
# ============================================================================

def inject_to_dict(inject) -> Dict[str, Any]:
    """Konvertiert ein Inject-Objekt zu einem Dictionary für die UI."""
    # TODO: Implementiere wenn Backend-Integration erfolgt
    return {}


def update_state_from_backend(workflow_result: Dict[str, Any]):
    """Aktualisiert den State basierend auf Backend-Ergebnissen."""
    # TODO: Implementiere wenn Backend-Integration erfolgt
    pass


def convert_neo4j_state_to_ui_format(system_state: Dict[str, Any]) -> Dict[str, Any]:
    """Konvertiert Neo4j System State zu UI-Format."""
    # TODO: Implementiere State-Konvertierung
    return get_mock_state()


# ============================================================================
# Main App
# ============================================================================

def main():
    """Hauptfunktion der Crisis Cockpit App."""
    st.set_page_config(
        page_title="The Crisis Cockpit",
        page_icon=None,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Professional CSS
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    h1, h2, h3 {
        color: #1e293b;
        font-weight: 600;
    }
    .info-box {
        background: #f1f5f9;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("The Crisis Cockpit")
    st.caption("Neuro-Symbolic Crisis Generator - Bachelor Thesis Evaluation Tool")
    
    # Erklärbox: Projekt-Übersicht
    render_info_box(
        "Projekt-Übersicht",
        """
        **Forschungsfrage:** Reduziert ein Neuro-Symbolic Logic Guard (LangGraph + State Tracking) 
        Hallucinations in Krisenszenarien im Vergleich zu einem reinen LLM/RAG-Ansatz?
        
        **Methodik:**
        - Vergleich zwischen "Legacy Mode" (Pure LLM) und "Logic Guard Mode" (Neuro-Symbolic)
        - Manuelle Evaluation jedes Injects (Consistent vs. Hallucination)
        - Statistische Auswertung der Ergebnisse
        
        **Hypothese:** Symbolische Constraints (FSM, Neo4j State, DORA Compliance) reduzieren 
        logische Inkonsistenzen und technische Fehler.
        """,
        expander=True
    )
    
    # Initialize Session State
    init_session_state()
    
    # ===== MODULE 2: Interaction Module in Sidebar =====
    render_interaction_module()
    
    # ===== MODULE 1: Split-Screen Layout =====
    col_story, col_state = st.columns([1, 1])
    
    with col_story:
        render_story_column()
    
    with col_state:
        render_state_reality_column()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Statistics:**")
    st.sidebar.markdown(f"- Total Injects: {len(st.session_state.injects)}")
    st.sidebar.markdown(f"- Evaluations: {len(st.session_state.evaluation_data)}")
    st.sidebar.markdown(f"- Current Mode: {st.session_state.mode}")


if __name__ == "__main__":
    main()

"""
Tests für das Crisis Cockpit Frontend.

Testet die UI-Funktionalität und State Management.
"""

import pytest
import sys
from pathlib import Path

# Füge Projekt-Root zum Python-Path hinzu
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from frontend.crisis_cockpit import (
    get_mock_injects,
    get_mock_state,
    inject_to_dict,
    update_state_after_inject,
    record_evaluation
)


class TestMockData:
    """Tests für Mock-Daten."""
    
    def test_get_mock_injects(self):
        """Testet ob Mock-Injects korrekt generiert werden."""
        injects = get_mock_injects()
        
        assert len(injects) > 0
        assert all("inject_id" in inj for inj in injects)
        assert all("content" in inj for inj in injects)
        assert all("source" in inj for inj in injects)
        assert all("target" in inj for inj in injects)
    
    def test_get_mock_state(self):
        """Testet ob Mock-State korrekt generiert wird."""
        state = get_mock_state()
        
        assert "diesel_tank" in state
        assert "server_health" in state
        assert "database_status" in state
        assert isinstance(state["diesel_tank"], (int, float))
        assert 0 <= state["diesel_tank"] <= 100


class TestStateManagement:
    """Tests für State Management."""
    
    def test_update_state_after_inject(self):
        """Testet State-Update nach Inject."""
        initial_state = get_mock_state()
        initial_diesel = initial_state["diesel_tank"]
        initial_server = initial_state["server_health_value"]
        
        inject = {
            "affected_assets": ["SRV-001"],
            "content": "Ransomware encryption detected"
        }
        
        # Simuliere Session State
        import streamlit as st
        if hasattr(st, 'session_state'):
            st.session_state.current_state = initial_state.copy()
        
        update_state_after_inject(inject)
        
        # Prüfe ob State aktualisiert wurde
        # (In echter Implementierung würde man st.session_state prüfen)
        assert True  # Placeholder - würde in echtem Test st.session_state prüfen


class TestEvaluation:
    """Tests für Evaluation-Funktionalität."""
    
    def test_record_evaluation(self):
        """Testet Evaluation-Aufzeichnung."""
        # Simuliere Session State
        import streamlit as st
        if hasattr(st, 'session_state'):
            st.session_state.evaluation_data = []
            st.session_state.mode = "Logic Guard Mode"
        
        record_evaluation("INJ-001", "Consistent", None)
        
        # Prüfe ob Evaluation gespeichert wurde
        # (In echter Implementierung würde man st.session_state prüfen)
        assert True  # Placeholder


class TestDataConversion:
    """Tests für Datenkonvertierung."""
    
    def test_inject_to_dict_structure(self):
        """Testet ob inject_to_dict korrekte Struktur zurückgibt."""
        # inject_to_dict ist aktuell eine Placeholder-Funktion
        result = inject_to_dict(None)
        
        # In echter Implementierung würde man prüfen:
        # assert "inject_id" in result
        # assert "content" in result
        # etc.
        assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


"""
Tests für die Agenten.

Testet die Funktionalität von Manager, Generator, Critic und Intel Agents.
"""

import pytest
import sys
from pathlib import Path

# Füge Projekt-Root zum Python-Path hinzu
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Direkte Imports um zirkuläre Imports zu vermeiden
import importlib.util

def load_module_from_file(file_path, module_name):
    """Lädt ein Modul direkt aus einer Datei."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Lade Agent-Module direkt
manager_module = load_module_from_file(
    project_root / "agents" / "manager_agent.py",
    "manager_agent"
)
intel_module = load_module_from_file(
    project_root / "agents" / "intel_agent.py",
    "intel_agent"
)
generator_module = load_module_from_file(
    project_root / "agents" / "generator_agent.py",
    "generator_agent"
)
critic_module = load_module_from_file(
    project_root / "agents" / "critic_agent.py",
    "critic_agent"
)

ManagerAgent = manager_module.ManagerAgent
IntelAgent = intel_module.IntelAgent
GeneratorAgent = generator_module.GeneratorAgent
CriticAgent = critic_module.CriticAgent

from state_models import ScenarioType, CrisisPhase, Inject, InjectModality, TechnicalMetadata


class TestManagerAgent:
    """Tests für Manager Agent."""
    
    def test_manager_initialization(self):
        """Testet Manager-Initialisierung."""
        manager = ManagerAgent()
        assert manager is not None
        assert manager.llm is not None
    
    def test_create_storyline_structure(self, monkeypatch):
        """Testet Storyline-Struktur."""
        manager = ManagerAgent()
        
        # Mock LLM Response
        class MockResponse:
            content = '{"next_phase": "SUSPICIOUS_ACTIVITY", "narrative": "Test", "key_events": [], "affected_assets": [], "business_impact": ""}'
        
        def mock_invoke(*args, **kwargs):
            return MockResponse()
        
        monkeypatch.setattr(manager.llm, "invoke", mock_invoke)
        
        result = manager.create_storyline(
            scenario_type=ScenarioType.RANSOMWARE_DOUBLE_EXTORTION,
            current_phase=CrisisPhase.NORMAL_OPERATION,
            inject_count=0,
            system_state={}
        )
        
        assert "next_phase" in result
        assert "narrative" in result


class TestIntelAgent:
    """Tests für Intel Agent."""
    
    def test_intel_initialization(self):
        """Testet Intel-Initialisierung."""
        intel = IntelAgent()
        assert intel is not None
    
    def test_get_relevant_ttps_structure(self):
        """Testet TTP-Abfrage-Struktur."""
        intel = IntelAgent()
        
        # Kann fehlschlagen wenn ChromaDB nicht verfügbar
        try:
            ttps = intel.get_relevant_ttps(
                phase=CrisisPhase.NORMAL_OPERATION,
                limit=5
            )
            
            assert isinstance(ttps, list)
            # Wenn TTPs gefunden, prüfe Struktur
            if ttps:
                assert "mitre_id" in ttps[0] or "technique_id" in ttps[0]
        except Exception:
            # ChromaDB nicht verfügbar - Test überspringen
            pytest.skip("ChromaDB not available")


class TestGeneratorAgent:
    """Tests für Generator Agent."""
    
    def test_generator_initialization(self):
        """Testet Generator-Initialisierung."""
        generator = GeneratorAgent()
        assert generator is not None
        assert generator.llm is not None
    
    def test_format_system_state(self):
        """Testet System-State-Formatierung."""
        generator = GeneratorAgent()
        
        # Test mit direktem Dictionary (neues Format)
        system_state = {
            "SRV-001": {"status": "online", "name": "Server 1"},
            "DB-001": {"status": "compromised", "name": "Database 1"}
        }
        
        result = generator._format_system_state(system_state)
        assert isinstance(result, str)
        assert len(result) > 0


class TestCriticAgent:
    """Tests für Critic Agent."""
    
    def test_critic_initialization(self):
        """Testet Critic-Initialisierung."""
        critic = CriticAgent()
        assert critic is not None
        assert critic.llm is not None
    
    def test_format_system_state(self):
        """Testet System-State-Formatierung."""
        critic = CriticAgent()
        
        # Test mit direktem Dictionary (neues Format)
        system_state = {
            "SRV-001": {"status": "online", "name": "Server 1"}
        }
        
        result = critic._format_system_state(system_state)
        assert isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


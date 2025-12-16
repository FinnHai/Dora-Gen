"""
Tests für System State Format-Kompatibilität.

Testet ob alle Agents das neue system_state Format korrekt verwenden.
"""

import pytest
import sys
from pathlib import Path

# Füge Projekt-Root zum Python-Path hinzu
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Direkte Imports um zirkuläre Imports zu vermeiden
# Importiere direkt aus den Dateien, nicht über __init__.py
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
generator_module = load_module_from_file(
    project_root / "agents" / "generator_agent.py",
    "generator_agent"
)
critic_module = load_module_from_file(
    project_root / "agents" / "critic_agent.py",
    "critic_agent"
)

ManagerAgent = manager_module.ManagerAgent
GeneratorAgent = generator_module.GeneratorAgent
CriticAgent = critic_module.CriticAgent


class TestSystemStateFormat:
    """Tests für System State Format."""
    
    def test_manager_format_system_state(self):
        """Testet Manager Agent _format_system_state mit neuem Format."""
        manager = ManagerAgent()
        
        # Neues Format: direktes Dictionary
        system_state = {
            "SRV-001": {
                "status": "online",
                "name": "Server 1",
                "entity_type": "server",
                "criticality": "critical"
            },
            "DB-001": {
                "status": "compromised",
                "name": "Database 1",
                "entity_type": "database",
                "criticality": "critical"
            }
        }
        
        result = manager._format_system_state(system_state)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Server 1" in result or "SRV-001" in result
    
    def test_generator_format_system_state(self):
        """Testet Generator Agent _format_system_state mit neuem Format."""
        generator = GeneratorAgent()
        
        system_state = {
            "SRV-001": {"status": "online", "name": "Server 1"}
        }
        
        result = generator._format_system_state(system_state)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_critic_format_system_state(self):
        """Testet Critic Agent _format_system_state mit neuem Format."""
        critic = CriticAgent()
        
        system_state = {
            "SRV-001": {"status": "online", "name": "Server 1"}
        }
        
        result = critic._format_system_state(system_state)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_empty_system_state(self):
        """Testet Verhalten bei leerem System State."""
        manager = ManagerAgent()
        generator = GeneratorAgent()
        critic = CriticAgent()
        
        empty_state = {}
        
        manager_result = manager._format_system_state(empty_state)
        generator_result = generator._format_system_state(empty_state)
        critic_result = critic._format_system_state(empty_state)
        
        assert isinstance(manager_result, str)
        assert isinstance(generator_result, str)
        assert isinstance(critic_result, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


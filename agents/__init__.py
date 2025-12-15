"""
Agenten-Modul für den DORA-Szenariengenerator.

Enthält die verschiedenen Agenten-Rollen:
- Manager Agent: Entwirft die grobe Storyline
- Generator Agent: Schreibt konkrete Injects
- Critic Agent: Validiert Logik und DORA-Konformität
- Intel Agent: Holt TTPs aus der Vektor-Datenbank
"""

from .manager_agent import ManagerAgent
from .generator_agent import GeneratorAgent
from .critic_agent import CriticAgent
from .intel_agent import IntelAgent

__all__ = ["ManagerAgent", "GeneratorAgent", "CriticAgent", "IntelAgent"]


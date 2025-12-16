"""
Test Runner für alle Tests.

Führt alle Tests aus und generiert einen Report.
"""

import pytest
import sys
from pathlib import Path

# Füge Projekt-Root zum Python-Path hinzu
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_all_tests():
    """Führt alle Tests aus."""
    test_dir = Path(__file__).parent
    
    # Führe alle Tests aus
    exit_code = pytest.main([
        str(test_dir),
        "-v",
        "--tb=short",
        "--color=yes",
        "-x"  # Stop bei erstem Fehler (optional, entfernen für alle Tests)
    ])
    
    return exit_code


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)


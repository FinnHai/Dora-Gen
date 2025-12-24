"""
Test Runner für alle Tests mit strukturiertem Logging.

Führt alle Tests aus und generiert einen detaillierten Report.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
import logging

# Füge Projekt-Root zum Python-Path hinzu
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("test_runner")


def run_all_tests():
    """Führt alle Tests aus."""
    test_dir = Path(__file__).parent
    log_dir = project_root / "logs" / "tests"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"test_run_{timestamp}.log"
    report_file = log_dir / f"test_report_{timestamp}.txt"
    
    logger.info("=" * 80)
    logger.info("CRUX Backend Test Suite")
    logger.info("=" * 80)
    logger.info(f"Test-Verzeichnis: {test_dir}")
    logger.info(f"Log-Datei: {log_file}")
    logger.info(f"Report-Datei: {report_file}")
    logger.info("=" * 80)
    
    # Führe alle Tests aus mit detailliertem Logging
    exit_code = pytest.main([
        str(test_dir),
        "-v",  # Verbose
        "--tb=short",  # Short traceback
        "--color=yes",  # Farbige Ausgabe
        "--log-cli-level=INFO",  # Log-Level für CLI
        "--log-file", str(log_file),  # Log-Datei
        "--log-file-level=DEBUG",  # Log-Level für Datei
        "-x",  # Stop bei erstem Fehler (entfernen für alle Tests)
        "--durations=10",  # Zeige 10 langsamste Tests
    ])
    
    logger.info("=" * 80)
    if exit_code == 0:
        logger.info("✅ Alle Tests erfolgreich!")
    else:
        logger.error(f"❌ Tests fehlgeschlagen mit Exit-Code: {exit_code}")
    logger.info("=" * 80)
    
    return exit_code


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)


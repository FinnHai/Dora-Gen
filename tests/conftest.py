"""
Pytest-Konfiguration mit strukturiertem Logging für Backend-Tests.
"""

import pytest
import logging
import sys
from pathlib import Path
from datetime import datetime

# Füge Projekt-Root zum Python-Path hinzu
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Konfiguriere strukturiertes Logging
def setup_logging():
    """Konfiguriert strukturiertes Logging für Tests."""
    log_dir = project_root / "logs" / "tests"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"test_run_{timestamp}.log"
    
    # Formatter für strukturierte Logs
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File Handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console Handler (nur INFO und höher)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Root Logger konfigurieren
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Spezifische Logger für verschiedene Komponenten
    loggers = {
        'api': logging.getLogger('api_server'),
        'workflow': logging.getLogger('workflows'),
        'agents': logging.getLogger('agents'),
        'compliance': logging.getLogger('compliance'),
        'neo4j': logging.getLogger('neo4j_client'),
    }
    
    for logger in loggers.values():
        logger.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return log_file


# Setup Logging beim Start
log_file = setup_logging()
logger = logging.getLogger(__name__)
logger.info(f"=" * 80)
logger.info(f"Test-Suite gestartet - Log-Datei: {log_file}")
logger.info(f"=" * 80)


@pytest.fixture(scope="session")
def test_logger():
    """Gibt einen Logger für Tests zurück."""
    return logging.getLogger("tests")


@pytest.fixture(scope="session")
def project_path():
    """Gibt den Projekt-Root-Pfad zurück."""
    return project_root


@pytest.fixture(autouse=True)
def log_test_start(request, test_logger):
    """Loggt den Start jedes Tests."""
    test_logger.info(f"\n{'='*80}")
    test_logger.info(f"TEST START: {request.node.name}")
    test_logger.info(f"{'='*80}")
    yield
    test_logger.info(f"TEST END: {request.node.name}\n")


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock-Umgebungsvariablen für Tests."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-12345")
    monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
    monkeypatch.setenv("NEO4J_USER", "neo4j")
    monkeypatch.setenv("NEO4J_PASSWORD", "test-password")
    monkeypatch.setenv("NEO4J_DATABASE", "neo4j")





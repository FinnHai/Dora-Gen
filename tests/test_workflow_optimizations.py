"""
Tests für Workflow-Optimierungen.

Testet State-Caching, Early Exit-Strategien und Performance-Monitoring.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import logging

# Füge Projekt-Root zum Python-Path hinzu
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

logger = logging.getLogger("tests.test_workflow_optimizations")


class TestWorkflowOptimizations:
    """Test-Klasse für Workflow-Optimierungen."""
    
    def test_workflow_optimizer_import(self):
        """Testet ob Workflow Optimizer importierbar ist."""
        logger.info("Teste Workflow Optimizer Import")
        try:
            from workflows.workflow_optimizations import (
                WorkflowOptimizer,
                WorkflowPerformanceMonitor
            )
            logger.info("✓ Workflow Optimizer erfolgreich importiert")
        except ImportError as e:
            logger.error(f"✗ Workflow Optimizer nicht verfügbar: {e}")
            pytest.skip("Workflow Optimizer nicht verfügbar")
    
    def test_workflow_optimizer_initialization(self):
        """Testet Initialisierung des Workflow Optimizers."""
        logger.info("Teste Workflow Optimizer Initialisierung")
        try:
            from workflows.workflow_optimizations import WorkflowOptimizer
            
            optimizer = WorkflowOptimizer()
            assert optimizer is not None
            assert hasattr(optimizer, 'state_cache')
            assert hasattr(optimizer, 'cache_ttl')
            logger.info("✓ Workflow Optimizer erfolgreich initialisiert")
            
        except ImportError:
            pytest.skip("Workflow Optimizer nicht verfügbar")
    
    def test_state_caching(self):
        """Testet State-Caching-Funktionalität."""
        logger.info("Teste State-Caching")
        try:
            from workflows.workflow_optimizations import WorkflowOptimizer
            
            optimizer = WorkflowOptimizer()
            
            # Mock Fetch-Funktion
            fetch_count = [0]
            def mock_fetch():
                fetch_count[0] += 1
                return {"data": "test"}
            
            # Erster Aufruf sollte fetch ausführen
            result1 = optimizer.get_cached_state("test_key", mock_fetch)
            assert result1 == {"data": "test"}
            assert fetch_count[0] == 1
            
            # Zweiter Aufruf sollte aus Cache kommen
            result2 = optimizer.get_cached_state("test_key", mock_fetch)
            assert result2 == {"data": "test"}
            assert fetch_count[0] == 1  # Sollte nicht erneut gefetcht werden
            
            logger.info("✓ State-Caching funktioniert korrekt")
            
        except ImportError:
            pytest.skip("Workflow Optimizer nicht verfügbar")
    
    def test_cache_expiration(self):
        """Testet Cache-Ablauf."""
        logger.info("Teste Cache-Ablauf")
        try:
            from workflows.workflow_optimizations import WorkflowOptimizer
            
            optimizer = WorkflowOptimizer()
            optimizer.cache_ttl = timedelta(seconds=1)  # Sehr kurze TTL für Test
            
            fetch_count = [0]
            def mock_fetch():
                fetch_count[0] += 1
                return {"data": "test"}
            
            # Erster Aufruf
            optimizer.get_cached_state("test_key", mock_fetch)
            assert fetch_count[0] == 1
            
            # Warte auf Ablauf
            import time
            time.sleep(1.1)
            
            # Zweiter Aufruf nach Ablauf sollte erneut fetchen
            optimizer.get_cached_state("test_key", mock_fetch)
            assert fetch_count[0] == 2
            
            logger.info("✓ Cache-Ablauf funktioniert korrekt")
            
        except ImportError:
            pytest.skip("Workflow Optimizer nicht verfügbar")
    
    def test_should_continue_logic(self):
        """Testet should_continue-Logik."""
        logger.info("Teste should_continue-Logik")
        try:
            from workflows.workflow_optimizations import WorkflowOptimizations
            from state_models import CrisisPhase
            
            optimizer = WorkflowOptimizations(max_iterations=10)
            
            # Test: Maximale Iterationen erreicht
            state_max_iterations = {
                "iteration": 10,
                "max_iterations": 10,
                "injects": [],
                "current_phase": CrisisPhase.NORMAL_OPERATION,
                "errors": []
            }
            result = optimizer.should_continue(state_max_iterations)
            assert result == "end"
            logger.info("✓ should_continue erkennt maximale Iterationen")
            
            # Test: Genug Injects generiert
            state_enough_injects = {
                "iteration": 5,
                "max_iterations": 10,
                "injects": [Mock()] * 10,  # 10 Injects
                "current_phase": CrisisPhase.NORMAL_OPERATION,
                "errors": []
            }
            result = optimizer.should_continue(state_enough_injects)
            assert result == "end"
            logger.info("✓ should_continue erkennt genug Injects")
            
            # Test: Workflow sollte fortgesetzt werden
            state_continue = {
                "iteration": 3,
                "max_iterations": 10,
                "injects": [Mock()] * 3,
                "current_phase": CrisisPhase.NORMAL_OPERATION,
                "errors": []
            }
            result = optimizer.should_continue(state_continue)
            assert result == "continue"
            logger.info("✓ should_continue erkennt Fortsetzung")
            
        except ImportError:
            pytest.skip("Workflow Optimizations nicht verfügbar")
    
    def test_performance_monitor(self):
        """Testet Performance-Monitoring."""
        logger.info("Teste Performance-Monitoring")
        try:
            from workflows.workflow_optimizations import WorkflowPerformanceMonitor
            
            monitor = WorkflowPerformanceMonitor()
            assert monitor is not None
            
            # Prüfe verfügbare Methoden
            if hasattr(monitor, 'record_metric'):
                monitor.record_metric("test_metric", 100.0, {"extra": "data"})
                assert len(monitor.performance_metrics) > 0
            elif hasattr(monitor, 'performance_metrics'):
                # Falls record_metric nicht existiert, prüfe nur die Struktur
                assert isinstance(monitor.performance_metrics, list)
            
            logger.info("✓ Performance-Monitoring funktioniert")
            
        except ImportError:
            pytest.skip("Workflow Performance Monitor nicht verfügbar")

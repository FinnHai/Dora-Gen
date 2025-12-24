"""
Tests für Neo4j Client.

Testet Knowledge Graph-Operationen (mit Mock wenn Neo4j nicht verfügbar).
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import logging
import os

# Füge Projekt-Root zum Python-Path hinzu
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

logger = logging.getLogger("tests.test_neo4j_client")


class TestNeo4jClient:
    """Test-Klasse für Neo4j Client."""
    
    @pytest.fixture
    def mock_neo4j_driver(self):
        """Mock für Neo4j Driver."""
        logger.info("Erstelle Mock für Neo4j Driver")
        from unittest.mock import MagicMock
        
        mock_driver = Mock()
        mock_session = Mock()
        
        # Mock für get_current_state Query
        mock_record = Mock()
        mock_record.get.side_effect = lambda key: {
            "e": {
                "id": "SRV-001",
                "name": "Server 001",
                "type": "Server",
                "status": "online"
            },
            "relationships": [],
            "related_entities": []
        }.get(key)
        
        mock_session.run.return_value = [mock_record]
        
        # Context Manager Mock richtig konfigurieren
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = mock_session
        mock_context_manager.__exit__.return_value = None
        
        mock_driver.session.return_value = mock_context_manager
        
        return mock_driver
    
    def test_neo4j_client_import(self):
        """Testet ob Neo4j Client importierbar ist."""
        logger.info("Teste Neo4j Client Import")
        try:
            from neo4j_client import Neo4jClient
            logger.info("✓ Neo4j Client erfolgreich importiert")
        except ImportError as e:
            logger.error(f"✗ Neo4j Client nicht verfügbar: {e}")
            pytest.skip("Neo4j Client nicht verfügbar")
    
    @patch('neo4j_client.GraphDatabase')
    def test_neo4j_client_connection(self, mock_graph_db, mock_neo4j_driver):
        """Testet Neo4j Client-Verbindung."""
        logger.info("Teste Neo4j Client-Verbindung")
        try:
            from neo4j_client import Neo4jClient
            
            mock_graph_db.driver.return_value = mock_neo4j_driver
            
            client = Neo4jClient()
            client.connect()
            
            assert client.driver is not None
            logger.info("✓ Neo4j Client-Verbindung erfolgreich")
            
        except ImportError:
            pytest.skip("Neo4j Client nicht verfügbar")
    
    @patch('neo4j_client.GraphDatabase')
    def test_get_current_state(self, mock_graph_db, mock_neo4j_driver):
        """Testet get_current_state Methode."""
        logger.info("Teste get_current_state")
        try:
            from neo4j_client import Neo4jClient
            
            mock_graph_db.driver.return_value = mock_neo4j_driver
            
            client = Neo4jClient()
            client.driver = mock_neo4j_driver
            
            # Mock für get_current_state Query
            mock_session = Mock()
            mock_record = Mock()
            
            # Mock-Entity-Daten
            mock_entity = {
                "id": "SRV-001",
                "name": "Server 001",
                "type": "Server",
                "status": "online"
            }
            
            # Konfiguriere Record als subscriptable (unterstützt record["e"])
            mock_record.__getitem__ = Mock(side_effect=lambda key: {
                "e": mock_entity,
                "relationships": [],
                "related_entities": []
            }.get(key))
            
            # Mock-Result als iterierbarer Iterator
            mock_result = Mock()
            mock_result.__iter__ = Mock(return_value=iter([mock_record]))
            mock_session.run.return_value = mock_result
            
            # Context Manager Mock richtig konfigurieren
            mock_context_manager = MagicMock()
            mock_context_manager.__enter__.return_value = mock_session
            mock_context_manager.__exit__.return_value = None
            mock_neo4j_driver.session.return_value = mock_context_manager
            
            entities = client.get_current_state()
            assert isinstance(entities, list)
            logger.info(f"✓ get_current_state erfolgreich: {len(entities)} Entitäten")
            
        except ImportError:
            pytest.skip("Neo4j Client nicht verfügbar")
    
    @patch('neo4j_client.GraphDatabase')
    def test_update_entity_status(self, mock_graph_db, mock_neo4j_driver):
        """Testet update_entity_status Methode."""
        logger.info("Teste update_entity_status")
        try:
            from neo4j_client import Neo4jClient
            
            mock_graph_db.driver.return_value = mock_neo4j_driver
            
            client = Neo4jClient()
            client.driver = mock_neo4j_driver
            
            # Mock für Update-Query
            mock_session = Mock()
            mock_session.run.return_value = []
            mock_neo4j_driver.session.return_value.__enter__.return_value = mock_session
            mock_neo4j_driver.session.return_value.__exit__.return_value = None
            
            client.update_entity_status("SRV-001", "compromised", inject_id="INJ-001")
            logger.info("✓ update_entity_status erfolgreich")
            
        except ImportError:
            pytest.skip("Neo4j Client nicht verfügbar")
    
    @patch('neo4j_client.GraphDatabase')
    def test_get_entity_status(self, mock_graph_db, mock_neo4j_driver):
        """Testet get_entity_status Methode."""
        logger.info("Teste get_entity_status")
        try:
            from neo4j_client import Neo4jClient
            
            mock_graph_db.driver.return_value = mock_neo4j_driver
            
            client = Neo4jClient()
            client.driver = mock_neo4j_driver
            
            # Mock für Status-Query
            mock_session = Mock()
            mock_record = Mock()
            # Konfiguriere Record als subscriptable (unterstützt record["status"])
            mock_record.__getitem__ = Mock(side_effect=lambda key: {
                "status": "online"
            }.get(key))
            
            # Mock-Result mit single() Methode
            mock_result = Mock()
            mock_result.single.return_value = mock_record
            mock_session.run.return_value = mock_result
            
            # Context Manager Mock richtig konfigurieren
            mock_context_manager = MagicMock()
            mock_context_manager.__enter__.return_value = mock_session
            mock_context_manager.__exit__.return_value = None
            mock_neo4j_driver.session.return_value = mock_context_manager
            
            status = client.get_entity_status("SRV-001")
            assert status is not None
            logger.info(f"✓ get_entity_status erfolgreich: {status}")
            
        except ImportError:
            pytest.skip("Neo4j Client nicht verfügbar")
    
    def test_neo4j_connection_real(self):
        """Testet echte Neo4j-Verbindung (optional, nur wenn Neo4j läuft)."""
        logger.info("Teste echte Neo4j-Verbindung (optional)")
        try:
            from neo4j_client import Neo4jClient
            import os
            from dotenv import load_dotenv
            
            load_dotenv()
            
            # Prüfe ob Neo4j-Konfiguration vorhanden ist
            uri = os.getenv("NEO4J_URI")
            user = os.getenv("NEO4J_USER")
            password = os.getenv("NEO4J_PASSWORD")
            
            if not uri or not user or not password or password == "your_password_here":
                logger.info("⚠ Neo4j-Konfiguration nicht vollständig - überspringe echten Test")
                pytest.skip("Neo4j-Konfiguration nicht vollständig")
            
            # Versuche Verbindung
            try:
                client = Neo4jClient()
                client.connect()
                
                # Test: get_current_state
                entities = client.get_current_state()
                logger.info(f"✓ Echte Neo4j-Verbindung erfolgreich: {len(entities)} Entitäten")
                
                client.close()
                
            except Exception as e:
                logger.warning(f"⚠ Neo4j-Verbindung fehlgeschlagen: {e}")
                pytest.skip(f"Neo4j nicht erreichbar: {e}")
                
        except ImportError:
            pytest.skip("Neo4j Client nicht verfügbar")

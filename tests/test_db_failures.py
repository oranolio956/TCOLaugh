import pytest
from unittest.mock import MagicMock, patch
from panopticon.persistence.graph.neo4j_manager import Neo4jManager
from panopticon.persistence.vector.milvus_manager import MilvusManager

def test_neo4j_down():
    """Test Neo4jManager when database is offline."""
    with patch('neo4j.GraphDatabase.driver', side_effect=Exception("Connection Refused")):
        manager = Neo4jManager(uri="bolt://localhost:7687")
        # Driver should be None, methods should safe-guard
        assert manager.driver is None
        
        # Attempting to add node should silently fail or log error, but NOT crash app
        manager.add_node("uid1", "Person", {})
        manager.get_subgraph("uid1")

def test_milvus_down():
    """Test MilvusManager when database is offline."""
    with patch('pymilvus.connections.connect', side_effect=Exception("RPC Error")):
        manager = MilvusManager()
        # Collection should be None
        assert manager.collection is None
        
        # Attempting search should return empty list, not crash
        import numpy as np
        results = manager.search_vectors(np.zeros(512))
        assert results == []

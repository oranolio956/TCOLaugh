import logging
import os
from typing import Dict, Any, List, Optional
import numpy as np

try:
    from annoy import AnnoyIndex
    ANNOY_AVAILABLE = True
except ImportError:
    ANNOY_AVAILABLE = False

from panopticon.persistence.vector.milvus_manager import MilvusManager

logger = logging.getLogger(__name__)

class VectorStoreRouter:
    """
    Routes vector operations to the best available backend.
    Priority:
    1. Milvus (if connected)
    2. Annoy (Disk-based fallback)
    3. SQLite/Numpy (Memory fallback)
    """
    def __init__(self, dim: int = 512, metric: str = 'angular'):
        self.dim = dim
        self.milvus = MilvusManager()
        self.annoy_index = None
        self.annoy_path = "panopticon_vectors.ann"
        self.annoy_metadata_map = {} # In-memory map for ID->Metadata (limit of Annoy)
        self.next_annoy_id = 0
        
        if ANNOY_AVAILABLE:
            self.annoy_index = AnnoyIndex(dim, metric)
            if os.path.exists(self.annoy_path):
                try:
                    self.annoy_index.load(self.annoy_path)
                    logger.info("Loaded Annoy index from disk.")
                    # Note: Annoy is static once built. 
                    # Real system would manage read/write indices or rebuilds.
                except Exception as e:
                    logger.warning(f"Could not load Annoy index: {e}")
        
    def add_vector(self, vector: np.ndarray, external_id: str, metadata: Dict[str, Any]):
        # 1. Try Milvus
        if self.milvus.collection:
            self.milvus.add_vector(vector, external_id, metadata)
            return

        # 2. Try Annoy
        if self.annoy_index:
            # Annoy takes integer IDs. We need to map external string ID to int.
            # Ideally this map is persisted in SQLite.
            # For this demo, we use a simple in-memory approach or skip if index is built (read-only)
            # In a real "DiskANN" style impl, we'd use HNSWLib or Vearch.
            # Here we will just log that we are "indexing" but Annoy requires batch build usually.
            pass

        # 3. Fallback to SQLite (PolyglotStore)
        from panopticon.persistence.sqlite_manager import db_instance
        db_instance.add_vector(external_id, vector, metadata)

    def search_vectors(self, query_vector: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        # 1. Try Milvus
        if self.milvus.collection:
            return self.milvus.search_vectors(query_vector, k)
            
        # 2. Try Annoy (if built)
        # Note: Annoy needs to be 'built' to search. If we are in streaming mode, 
        # we usually rely on SQLite fallback until a batch job builds the Annoy index.
        
        # 3. Fallback to SQLite
        from panopticon.persistence.sqlite_manager import db_instance
        return db_instance.search_vectors(query_vector, k)

# Global Instance
vector_router = VectorStoreRouter()

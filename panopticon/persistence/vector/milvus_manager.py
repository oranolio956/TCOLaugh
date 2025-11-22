import logging
from pymilvus import (
    connections,
    utility,
    FieldSchema, CollectionSchema, DataType,
    Collection,
)
from typing import List, Dict, Any
import numpy as np

logger = logging.getLogger(__name__)

class MilvusManager:
    def __init__(self, host: str = "localhost", port: str = "19530"):
        self.collection_name = "faces_v1"
        try:
            connections.connect("default", host=host, port=port)
            logger.info(f"Connected to Milvus at {host}:{port}")
            self._init_collection()
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            self.collection = None

    def _init_collection(self):
        if utility.has_collection(self.collection_name):
            self.collection = Collection(self.collection_name)
            self.collection.load()
            return

        # Define Schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=512),
            FieldSchema(name="external_id", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="metadata", dtype=DataType.JSON)
        ]
        schema = CollectionSchema(fields, "Panopticon Face Index")

        self.collection = Collection(self.collection_name, schema)
        
        # Create HNSW Index (DiskANN-like performance)
        index_params = {
            "metric_type": "COSINE",
            "index_type": "HNSW",
            "params": {"M": 8, "efConstruction": 64}
        }
        self.collection.create_index(field_name="embedding", index_params=index_params)
        self.collection.load()
        logger.info(f"Initialized Milvus collection: {self.collection_name}")

    def add_vector(self, vector: np.ndarray, external_id: str, metadata: Dict[str, Any]):
        if not self.collection:
            return
        
        # Milvus expects list of lists
        entities = [
            [vector.tolist()],  # embedding
            [external_id],      # external_id
            [metadata]          # metadata
        ]
        
        # Note: insert API varies by version, simplifying for standard pymilvus
        try:
            self.collection.insert([
                [vector.tolist()], # embedding column
                [external_id],     # external_id column
                [metadata]         # metadata column
            ])
            # In high throughput, flush async. Here we just rely on auto-flush or periodic
        except Exception as e:
            logger.error(f"Milvus insert failed: {e}")

    def search_vectors(self, query_vector: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        if not self.collection:
            return []

        search_params = {"metric_type": "COSINE", "params": {"ef": 32}}
        
        results = self.collection.search(
            data=[query_vector.tolist()],
            anns_field="embedding",
            param=search_params,
            limit=k,
            output_fields=["external_id", "metadata"]
        )

        matches = []
        for hits in results:
            for hit in hits:
                matches.append({
                    "id": hit.entity.get("external_id"),
                    "score": hit.score,
                    "metadata": hit.entity.get("metadata")
                })
        return matches

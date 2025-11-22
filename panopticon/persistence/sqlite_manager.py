import sqlite3
import json
import numpy as np
from typing import List, Dict, Any, Optional
import logging
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class PolyglotStore:
    """
    A wrapper around SQLite to simulate the multi-modal persistence layer:
    1. Graph (Nodes/Edges) -> Simulates Neo4j
    2. Documents (Raw Data) -> Simulates ScyllaDB/Elasticsearch
    3. Vectors (Embeddings) -> Simulates DiskANN/Vearch
    """
    def __init__(self, db_path: str = "panopticon.db"):
        self.db_path = db_path
        # Use a lock to prevent concurrent write errors during simulation
        self._lock = threading.Lock()
        self.setup_schema()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        try:
            yield conn
        finally:
            conn.close()

    def setup_schema(self):
        with self.get_connection() as conn:
            cur = conn.cursor()
            
            # 1. Document Store (The "Raw" Data)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                source_type TEXT,
                timestamp REAL,
                data JSON
            )
            """)
            
            # 2. Graph Store (Nodes)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                uid TEXT PRIMARY KEY,
                type TEXT,
                properties JSON
            )
            """)
            
            # 3. Graph Store (Edges)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                source_uid TEXT,
                target_uid TEXT,
                type TEXT,
                properties JSON,
                PRIMARY KEY (source_uid, target_uid, type)
            )
            """)
            
            # 4. Vector Store (Simulated)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                id TEXT PRIMARY KEY,
                vector BLOB, -- Stored as bytes
                metadata JSON
            )
            """)
            
            conn.commit()

    # --- Document Operations ---
    def add_document(self, doc_id: str, source_type: str, timestamp: float, data: Dict[str, Any]):
        with self._lock:
            with self.get_connection() as conn:
                try:
                    conn.execute(
                        "INSERT OR REPLACE INTO documents (id, source_type, timestamp, data) VALUES (?, ?, ?, ?)",
                        (doc_id, source_type, timestamp, json.dumps(data))
                    )
                    conn.commit()
                except Exception as e:
                    logger.error(f"Error adding document: {e}")

    def search_documents(self, query_key: str, query_value: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT data FROM documents")
            results = []
            for row in cur.fetchall():
                data = json.loads(row[0])
                if self._recursive_search(data, query_key, query_value):
                    results.append(data)
            return results

    def _recursive_search(self, data: Any, key: str, value: str) -> bool:
        if isinstance(data, dict):
            for k, v in data.items():
                if k == key and str(v).lower() == str(value).lower():
                    return True
                if self._recursive_search(v, key, value):
                    return True
        elif isinstance(data, list):
            for item in data:
                if self._recursive_search(item, key, value):
                    return True
        return False

    # --- Graph Operations ---
    def add_node(self, uid: str, node_type: str, properties: Dict[str, Any]):
        with self._lock:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO nodes (uid, type, properties) VALUES (?, ?, ?)",
                    (uid, node_type, json.dumps(properties))
                )
                conn.commit()

    def add_edge(self, source: str, target: str, edge_type: str, properties: Dict[str, Any] = {}):
        with self._lock:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO edges (source_uid, target_uid, type, properties) VALUES (?, ?, ?, ?)",
                    (source, target, edge_type, json.dumps(properties))
                )
                conn.commit()

    def get_subgraph(self, start_uid: str, depth: int = 1) -> Dict[str, Any]:
        nodes = {}
        edges = []
        queue = [(start_uid, 0)]
        visited = set()

        with self.get_connection() as conn:
            while queue:
                current_uid, current_depth = queue.pop(0)
                if current_uid in visited or current_depth > depth:
                    continue
                visited.add(current_uid)

                cur = conn.cursor()
                cur.execute("SELECT type, properties FROM nodes WHERE uid=?", (current_uid,))
                row = cur.fetchone()
                if row:
                    nodes[current_uid] = {"type": row[0], "properties": json.loads(row[1])}

                cur.execute("SELECT target_uid, type, properties FROM edges WHERE source_uid=?", (current_uid,))
                for target, type_, props in cur.fetchall():
                    edges.append({
                        "source": current_uid,
                        "target": target,
                        "type": type_,
                        "properties": json.loads(props)
                    })
                    if target not in visited:
                        queue.append((target, current_depth + 1))
                
                cur.execute("SELECT source_uid, type, properties FROM edges WHERE target_uid=?", (current_uid,))
                for source, type_, props in cur.fetchall():
                    edges.append({
                        "source": source,
                        "target": current_uid,
                        "type": type_,
                        "properties": json.loads(props)
                    })
                    if source not in visited:
                        queue.append((source, current_depth + 1))

        return {"nodes": nodes, "edges": edges}

    # --- Vector Operations ---
    def add_vector(self, vec_id: str, vector: np.ndarray, metadata: Dict[str, Any]):
        blob = vector.astype(np.float32).tobytes()
        with self._lock:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO vectors (id, vector, metadata) VALUES (?, ?, ?)",
                    (vec_id, blob, json.dumps(metadata))
                )
                conn.commit()

    def search_vectors(self, query_vector: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, vector, metadata FROM vectors")
            
            scores = []
            query_norm = np.linalg.norm(query_vector)
            if query_norm == 0: return []

            for vid, blob, meta_json in cur.fetchall():
                vec = np.frombuffer(blob, dtype=np.float32)
                dot_product = np.dot(query_vector, vec)
                vec_norm = np.linalg.norm(vec)
                if vec_norm == 0: continue
                similarity = dot_product / (query_norm * vec_norm)
                
                scores.append({
                    "id": vid,
                    "score": float(similarity),
                    "metadata": json.loads(meta_json)
                })
            
            scores.sort(key=lambda x: x["score"], reverse=True)
            return scores[:k]
    
    # Expose a method to get a raw cursor/conn strictly for read-only stats if needed,
    # but prefer methods.
    @property
    def conn(self):
        # Backward compatibility hack - returns a new connection that caller must close
        # Note: This is dangerous if caller expects the old persistent conn behavior
        # We'll update the caller (API) to use get_connection context instead
        return sqlite3.connect(self.db_path, check_same_thread=False)

db_instance = PolyglotStore()

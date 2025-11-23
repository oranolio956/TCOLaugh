import json
import logging
import os
import sqlite3
import threading
import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = os.environ.get("PANOPTICON_DB_PATH", "panopticon.db")
DOCUMENT_TTL_SECONDS = int(os.environ.get("PANOPTICON_DOCUMENT_TTL_SECONDS", "0") or 0)
INDEXED_FIELDS = {
    field.strip().lower()
    for field in os.environ.get(
        "PANOPTICON_INDEX_FIELDS", "email,username,phone,ip_address"
    ).split(",")
    if field.strip()
}
MAX_INDEXED_VALUES = int(os.environ.get("PANOPTICON_MAX_INDEXED_VALUES", "64") or 64)
PURGE_INTERVAL_SECONDS = int(os.environ.get("PANOPTICON_PURGE_INTERVAL", "60") or 60)


class PolyglotStore:
    """
    SQLite-backed polyglot simulator with optional Neo4j connectivity.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        
        # ... (existing init code) ...
        # Ensure the directory exists
        db_dir = os.path.dirname(os.path.abspath(self.db_path))
        if db_dir and db_dir != '.' and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, mode=0o755, exist_ok=True)
                logger.info(f"Created database directory: {db_dir}")
            except Exception as e:
                logger.warning(f"Could not create directory {db_dir}: {e}, using current directory")
                # Fall back to current directory
                self.db_path = "panopticon.db"
        
        self._lock = threading.Lock()
        self.ttl_seconds = DOCUMENT_TTL_SECONDS
        self._last_purge = 0.0
        self._vector_cache_loaded = False
        self._vector_matrix: Optional[np.ndarray] = None
        self._vector_ids: List[str] = []
        self._vector_metadata: List[Dict[str, Any]] = []
        self.setup_schema()

        # Neo4j Integration
        self.neo4j = None
        if os.environ.get("NEO4J_URI"):
            from panopticon.persistence.graph.neo4j_manager import Neo4jManager
            try:
                self.neo4j = Neo4jManager()
            except Exception as e:
                logger.error(f"Neo4j Connection Failed: {e}")

    # ... (existing methods) ...
    
    # --- Graph Operations ---
    def add_node(self, uid: str, node_type: str, properties: Dict[str, Any]):
        # 1. Neo4j
        if self.neo4j:
            try:
                self.neo4j.add_node(uid, node_type, properties)
            except Exception as e:
                logger.error(f"Neo4j write failed: {e}")

        # 2. SQLite Fallback
        with self._lock:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO nodes (uid, type, properties) VALUES (?, ?, ?)",
                    (uid, node_type, json.dumps(properties)),
                )
                conn.commit()

    def add_edge(
        self, source: str, target: str, edge_type: str, properties: Dict[str, Any] = {}
    ):
        # 1. Neo4j
        if self.neo4j:
            try:
                self.neo4j.add_edge(source, target, edge_type, properties)
            except Exception as e:
                logger.error(f"Neo4j edge failed: {e}")

        # 2. SQLite Fallback
        with self._lock:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO edges (source_uid, target_uid, type, properties) VALUES (?, ?, ?, ?)",
                    (source, target, edge_type, json.dumps(properties)),
                )
                conn.commit()

    def get_subgraph(self, start_uid: str, depth: int = 1) -> Dict[str, Any]:
        # 1. Neo4j
        if self.neo4j:
            try:
                return self.neo4j.get_subgraph(start_uid, depth)
            except Exception as e:
                logger.error(f"Neo4j read failed: {e}")

        # 2. SQLite Fallback
        nodes = {}
        edges: List[Dict[str, Any]] = []
        queue = [(start_uid, 0)]
        visited = set()

        with self.get_connection() as conn:
            while queue:

                current_uid, current_depth = queue.pop(0)
                if current_uid in visited or current_depth > depth:
                    continue
                visited.add(current_uid)

                cur = conn.cursor()
                cur.execute(
                    "SELECT type, properties FROM nodes WHERE uid=?", (current_uid,)
                )
                row = cur.fetchone()
                if row:
                    nodes[current_uid] = {
                        "type": row[0],
                        "properties": json.loads(row[1]),
                    }

                cur.execute(
                    "SELECT target_uid, type, properties FROM edges WHERE source_uid=?",
                    (current_uid,),
                )
                for target, type_, props in cur.fetchall():
                    edges.append(
                        {
                            "source": current_uid,
                            "target": target,
                            "type": type_,
                            "properties": json.loads(props),
                        }
                    )
                    if target not in visited:
                        queue.append((target, current_depth + 1))

                cur.execute(
                    "SELECT source_uid, type, properties FROM edges WHERE target_uid=?",
                    (current_uid,),
                )
                for source, type_, props in cur.fetchall():
                    edges.append(
                        {
                            "source": source,
                            "target": current_uid,
                            "type": type_,
                            "properties": json.loads(props),
                        }
                    )
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
                    (vec_id, blob, json.dumps(metadata)),
                )
                conn.commit()
        self._append_vector_cache(vec_id, vector, metadata)

    def search_vectors(
        self, query_vector: np.ndarray, k: int = 5
    ) -> List[Dict[str, Any]]:
        query_norm = np.linalg.norm(query_vector)
        if query_norm == 0:
            return []

        self._ensure_vector_cache()
        if self._vector_matrix is None or self._vector_matrix.size == 0:
            return []

        normalized_query = query_vector.astype(np.float32) / query_norm
        similarities = self._vector_matrix @ normalized_query
        top_indices = np.argsort(similarities)[::-1][:k]

        matches: List[Dict[str, Any]] = []
        for idx in top_indices:
            matches.append(
                {
                    "id": self._vector_ids[idx],
                    "score": float(similarities[idx]),
                    "metadata": self._vector_metadata[idx],
                }
            )
        return matches

    @property
    def conn(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    # --- Internal helpers ---
    def _index_document(self, conn: sqlite3.Connection, doc_id: str, data: Dict[str, Any]):
        if not INDEXED_FIELDS:
            return
        cur = conn.cursor()
        cur.execute("DELETE FROM document_index WHERE doc_id=?", (doc_id,))
        for key, value in self._extract_indexable_fields(data)[:MAX_INDEXED_VALUES]:
            cur.execute(
                "INSERT OR REPLACE INTO document_index (doc_id, key, value) VALUES (?, ?, ?)",
                (doc_id, key, value),
            )

    def _extract_indexable_fields(self, data: Any) -> List[Tuple[str, str]]:
        results: List[Tuple[str, str]] = []

        def traverse(node: Any):
            if isinstance(node, dict):
                for k, v in node.items():
                    lower_key = k.lower()
                    if isinstance(v, (dict, list)):
                        traverse(v)
                    elif lower_key in INDEXED_FIELDS:
                        val = str(v).strip().lower()
                        if val:
                            results.append((lower_key, val))
            elif isinstance(node, list):
                for item in node:
                    traverse(item)

        traverse(data)
        return results

    def _purge_if_needed(self, conn: sqlite3.Connection):
        if not self.ttl_seconds:
            return
        now = time.time()
        if now - self._last_purge < max(PURGE_INTERVAL_SECONDS, self.ttl_seconds // 4):
            return
        cutoff = now - self.ttl_seconds
        try:
            conn.execute(
                """
            DELETE FROM documents
            WHERE source_type != 'audit_log'
              AND timestamp > 0
              AND timestamp < ?
            """,
                (cutoff,),
            )
            conn.commit()
            self._last_purge = now
        except Exception as exc:
            logger.error("Failed to purge expired documents: %s", exc)

    def _ensure_vector_cache(self):
        if self._vector_cache_loaded:
            return
        self._reload_vector_cache()

    def _reload_vector_cache(self):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, vector, metadata FROM vectors")
            ids: List[str] = []
            metadata: List[Dict[str, Any]] = []
            vectors: List[np.ndarray] = []
            for vid, blob, meta_json in cur.fetchall():
                vec = np.frombuffer(blob, dtype=np.float32)
                norm = np.linalg.norm(vec)
                if norm == 0:
                    continue
                vectors.append((vec / norm).astype(np.float32))
                ids.append(vid)
                metadata.append(json.loads(meta_json))

            if vectors:
                self._vector_matrix = np.vstack(vectors)
            else:
                self._vector_matrix = np.empty((0, 0), dtype=np.float32)
            self._vector_ids = ids
            self._vector_metadata = metadata
            self._vector_cache_loaded = True

    def _append_vector_cache(self, vec_id: str, vector: np.ndarray, metadata: Dict[str, Any]):
        norm = np.linalg.norm(vector)
        if norm == 0:
            return
        normalized = (vector / norm).astype(np.float32)
        if self._vector_matrix is None or self._vector_matrix.size == 0:
            self._vector_matrix = normalized.reshape(1, -1)
        else:
            try:
                self._vector_matrix = np.vstack([self._vector_matrix, normalized])
            except ValueError:
                # Dimension mismatch – rebuild cache from scratch.
                self._vector_cache_loaded = False
                self._reload_vector_cache()
                return
        self._vector_ids.append(vec_id)
        self._vector_metadata.append(metadata)


db_instance = PolyglotStore()

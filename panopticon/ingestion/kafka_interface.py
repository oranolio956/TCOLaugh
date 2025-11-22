import json
import logging
import uuid
from typing import Any, Dict, List

from kafka import KafkaProducer

from panopticon.persistence.sqlite_manager import db_instance

logger = logging.getLogger(__name__)


class IngestionProducer:
    """
    Modified Producer:
    If running in simulation mode (no Kafka), writes directly to the SQLite PolyglotStore.
    """

    def __init__(self, bootstrap_servers: List[str], topic: str):
        self.topic = topic
        self.use_kafka = False  # Force simulation mode
        logger.info(
            f"Initialized Ingestion for topic {topic} (Mode: {'Kafka' if self.use_kafka else 'SQLite Persistence'})"
        )

    def send_record(self, record: Dict[str, Any]):
        if self.use_kafka:
            # Placeholder for real Kafka logic
            pass
        else:
            # Write to SQLite
            doc_id = str(uuid.uuid4())
            db_instance.add_document(
                doc_id=doc_id,
                source_type=record.get("source_type", "unknown"),
                timestamp=record.get("timestamp", 0.0),
                data=record,
            )
            logger.info(f"Persisted record {doc_id} to Store")

            # Trigger Real-time Graph Extraction (Simulating a Consumer)
            self._extract_entities(doc_id, record)

    def _extract_entities(self, doc_id: str, record: Dict[str, Any]):
        """
        Simple Entity Extraction Logic
        """
        raw = record.get("raw_data", {})
        source_type = record.get("source_type")

        if source_type == "surface_web":
            # Extract Person
            username = raw.get("username")
            if username:
                uid = f"user:{username}"
                db_instance.add_node(
                    uid, "Identity", {"username": username, "source": "social"}
                )

                # Extract Name
                name = raw.get("name")
                if name:
                    db_instance.add_node(f"name:{name}", "Name", {"val": name})
                    db_instance.add_edge(uid, f"name:{name}", "HAS_NAME")

        elif source_type == "deep_web":
            # Extract Email
            email = raw.get("email")
            if email:
                uid = f"email:{email}"
                db_instance.add_node(uid, "Email", {"val": email})

                # Link IP
                ip = raw.get("ip_address")
                if ip:
                    ip_uid = f"ip:{ip}"
                    db_instance.add_node(ip_uid, "IPAddress", {"val": ip})
                    db_instance.add_edge(
                        uid, ip_uid, "OBSERVED_AT", {"dataset": record.get("dataset")}
                    )

                # Link Hash
                p_hash = raw.get("password_hash")
                if p_hash:
                    hash_uid = f"hash:{p_hash}"
                    db_instance.add_node(hash_uid, "PasswordHash", {"val": p_hash})
                    db_instance.add_edge(uid, hash_uid, "USED_PASSWORD")

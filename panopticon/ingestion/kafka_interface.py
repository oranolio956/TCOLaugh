import json
import logging
import os
import uuid
from typing import Any, Dict, List

from kafka import KafkaProducer
from kafka.errors import KafkaError

from panopticon.persistence.sqlite_manager import db_instance

logger = logging.getLogger(__name__)


class IngestionProducer:
    """
    Producer that optionally streams to Kafka or falls back to SQLite persistence.
    """

    def __init__(self, bootstrap_servers: List[str], topic: str):
        self.topic = topic
        self.use_kafka = (
            os.environ.get("PANOPTICON_USE_KAFKA", "false").lower() in {"1", "true", "yes"}
        )
        self.producer = None
        if self.use_kafka:
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                )
                logger.info("Kafka producer initialized for topic %s.", topic)
            except KafkaError as exc:
                logger.error("Kafka unavailable (%s). Falling back to SQLite.", exc)
                self.use_kafka = False
        else:
            logger.info("Kafka disabled. Using SQLite persistence for topic %s.", topic)

    def send_record(self, record: Dict[str, Any]):
        if self.use_kafka and self.producer:
            future = self.producer.send(self.topic, record)

            def _on_error(excp):
                logger.error("Kafka send failed: %s. Falling back to SQLite.", excp)
                self._persist_record(record)

            future.add_errback(_on_error)
        else:
            self._persist_record(record)

    def _persist_record(self, record: Dict[str, Any]):
        doc_id = str(uuid.uuid4())
        db_instance.add_document(
            doc_id=doc_id,
            source_type=record.get("source_type", "unknown"),
            timestamp=record.get("timestamp", 0.0),
            data=record,
        )
        logger.info("Persisted record %s to PolyglotStore", doc_id)
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

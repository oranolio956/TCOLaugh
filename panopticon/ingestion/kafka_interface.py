import json
from kafka import KafkaProducer, KafkaConsumer
from typing import Dict, Any, Callable
import logging

logger = logging.getLogger(__name__)

class IngestionProducer:
    def __init__(self, bootstrap_servers: list[str], topic: str):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.topic = topic

    def send_record(self, record: Dict[str, Any]):
        try:
            self.producer.send(self.topic, record)
            self.producer.flush()
            logger.info(f"Sent record to {self.topic}")
        except Exception as e:
            logger.error(f"Failed to send record: {e}")

class IngestionConsumer:
    def __init__(self, bootstrap_servers: list[str], topic: str, group_id: str):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=group_id,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

    def consume(self, callback: Callable[[Dict[str, Any]], None]):
        logger.info("Starting consumption...")
        for message in self.consumer:
            try:
                callback(message.value)
            except Exception as e:
                logger.error(f"Error processing message: {e}")

import argparse
import logging
import os
import random
import time
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests

from panopticon.ingestion.kafka_interface import IngestionProducer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IngestionSink:
    """
    Sends records to the primary API when possible, falling back to local persistence.
    """

    def __init__(self, topic: str = "raw_ingestion"):
        self.topic = topic
        self.api_base_url = os.environ.get("PANOPTICON_API_BASE_URL")
        self.api_key = os.environ.get("PANOPTICON_API_KEY")
        self._producer: Optional[IngestionProducer] = None
        self._ingest_url = None

        if self.api_base_url and self.api_key:
            base = self.api_base_url.rstrip("/") + "/"
            self._ingest_url = urljoin(base, "ingest/record")
            logger.info("HTTP ingestion enabled -> %s", self._ingest_url)
        else:
            logger.info(
                "HTTP ingestion disabled (PANOPTICON_API_BASE_URL and PANOPTICON_API_KEY required)."
            )

    def _ensure_producer(self) -> IngestionProducer:
        if self._producer is None:
            bootstrap = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
            servers = [s.strip() for s in bootstrap.split(",") if s.strip()]
            if not servers:
                servers = ["localhost:9092"]
            self._producer = IngestionProducer(servers, self.topic)
        return self._producer

    def send_record(self, record: Dict[str, Any]):
        if self._ingest_url:
            try:
                response = requests.post(
                    self._ingest_url,
                    json=record,
                    headers={"X-API-Key": self.api_key},
                    timeout=10,
                )
                response.raise_for_status()
                logger.info(
                    "Ingested record via HTTP (%s)", record.get("source_type", "unknown")
                )
                return
            except Exception as exc:
                logger.warning("HTTP ingestion failed (%s). Falling back locally.", exc)
        producer = self._ensure_producer()
        producer.send_record(record)


class MockCrawler:
    def __init__(self, sink: IngestionSink):
        self.sink = sink

    def generate_surface_data(self) -> Dict[str, Any]:
        """Simulates scraping a social media profile."""
        names = [
            "John Doe",
            "Jane Smith",
            "Alice Johnson",
            "Bob Williams",
            "Eva Brown",
            "Michael Chen",
        ]
        domains = ["twitter.com", "linkedin.com", "instagram.com", "tiktok.com"]

        name = random.choice(names)
        domain = random.choice(domains)
        username = name.lower().replace(" ", "") + str(random.randint(1, 99))

        return {
            "source_type": "surface_web",
            "url": f"https://{domain}/{username}",
            "raw_data": {
                "name": name,
                "username": username,
                "bio": "Just a random bio for testing.",
                "location": "San Francisco, CA",
            },
            "timestamp": time.time(),
        }

    def generate_breach_data(self) -> Dict[str, Any]:
        """Simulates ingesting a breach record."""
        emails = [
            "jdoe@example.com",
            "jane.s@test.org",
            "alice.j@company.net",
            "bob.w@provider.com",
        ]
        passwords = ["password123", "qwerty", "secret", "123456", "letmein"]

        email = random.choice(emails)
        password = random.choice(passwords)

        return {
            "source_type": "deep_web",
            "dataset": "Collection #1",
            "raw_data": {
                "email": email,
                "password_hash": f"sha1:{hash(password)}",  # Mock hash
                "ip_address": f"192.168.1.{random.randint(1, 255)}",
            },
            "timestamp": time.time(),
        }

    def run(self, iterations: int = 5, delay: float = 0.5):
        logger.info(f"Starting mock crawl (Infinite: {iterations == -1})...")
        count = 0
        while iterations == -1 or count < iterations:
            # Simulate Surface Web ingestion
            surface_record = self.generate_surface_data()
            self.sink.send_record(surface_record)

            # Simulate Deep Web ingestion
            breach_record = self.generate_breach_data()
            self.sink.send_record(breach_record)

            time.sleep(delay)  # Simulate network delay
            count += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--continuous", action="store_true", help="Run indefinitely")
    parser.add_argument(
        "--delay", type=float, default=2.0, help="Delay between records in seconds"
    )
    parser.add_argument(
        "--topic", type=str, default=os.environ.get("PANOPTICON_KAFKA_TOPIC", "raw_ingestion")
    )
    args = parser.parse_args()

    sink = IngestionSink(topic=args.topic)
    crawler = MockCrawler(sink)

    iterations = -1 if args.continuous else 5
    crawler.run(iterations=iterations, delay=args.delay)

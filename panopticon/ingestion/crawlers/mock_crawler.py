import time
import random
import logging
from typing import Dict, Any, List
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock Kafka components since we don't have a running broker
class IngestionProducer:
    def __init__(self, bootstrap_servers: List[str], topic: str):
        self.topic = topic
        logger.info(f"Initialized Producer for topic {topic}")

    def send_record(self, record: Dict[str, Any]):
        logger.info(f"Sending to {self.topic}: {json.dumps(record, indent=2)}")

class MockCrawler:
    def __init__(self, producer: IngestionProducer):
        self.producer = producer

    def generate_surface_data(self) -> Dict[str, Any]:
        """Simulates scraping a social media profile."""
        names = ["John Doe", "Jane Smith", "Alice Johnson", "Bob Williams"]
        domains = ["twitter.com", "linkedin.com", "instagram.com"]
        
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
                "location": "San Francisco, CA"
            },
            "timestamp": time.time()
        }

    def generate_breach_data(self) -> Dict[str, Any]:
        """Simulates ingesting a breach record."""
        emails = ["jdoe@example.com", "jane.s@test.org", "alice.j@company.net"]
        passwords = ["password123", "qwerty", "secret"]
        
        email = random.choice(emails)
        password = random.choice(passwords)
        
        return {
            "source_type": "deep_web",
            "dataset": "Collection #1",
            "raw_data": {
                "email": email,
                "password_hash": f"sha1:{hash(password)}", # Mock hash
                "ip_address": f"192.168.1.{random.randint(1, 255)}"
            },
            "timestamp": time.time()
        }

    def run(self, iterations: int = 5):
        logger.info(f"Starting mock crawl for {iterations} iterations...")
        for _ in range(iterations):
            # Simulate Surface Web ingestion
            surface_record = self.generate_surface_data()
            self.producer.send_record(surface_record)
            
            # Simulate Deep Web ingestion
            breach_record = self.generate_breach_data()
            self.producer.send_record(breach_record)
            
            time.sleep(0.5) # Simulate network delay

if __name__ == "__main__":
    # Use the internal mock producer
    producer = IngestionProducer(bootstrap_servers=["localhost:9092"], topic="raw_ingestion")
    crawler = MockCrawler(producer)
    crawler.run(5)

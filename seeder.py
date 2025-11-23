import logging
import random
import time
import uuid
from panopticon.persistence.sqlite_manager import db_instance
from panopticon.ingestion.stealer_logs import StealerLogParser

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def seed_database():
    """
    Populates the database with realistic test scenarios for demonstration.
    """
    logger.info("Seeding database with demo data...")
    
    # Scenario 1: The " fragmented identity" (Splink Showcase)
    # Three records that look different but belong to the same person
    records = [
        {
            "source_type": "breach_dump",
            "raw_data": {
                "email": "robert.paulson@project-mayhem.org",
                "password_hash": "sha1:7c4a8d09ca3762af61e59520943dc26494f8941b", # '123456'
                "username": "bobs_moobs"
            },
            "timestamp": time.time() - 10000
        },
        {
            "source_type": "surface_web",
            "raw_data": {
                "username": "bobs_moobs", # Matches username
                "name": "Robert Paulson",
                "location": "Wilmington, DE"
            },
            "timestamp": time.time() - 5000
        },
        {
            "source_type": "leak",
            "raw_data": {
                "email": "robert.paulson@project-mayhem.org", # Matches email
                "phone": "+1-302-555-0199"
            },
            "timestamp": time.time()
        }
    ]
    
    for rec in records:
        doc_id = str(uuid.uuid4())
        db_instance.add_document(doc_id, rec["source_type"], rec["timestamp"], rec["raw_data"])
        # Manually trigger graph extraction logic (usually handled by kafka consumer/worker)
        # But for now, we just ensure they are searchable via document search
        
    # Scenario 2: The "Stealer Log" (Pivot Showcase)
    # A targeted attack log
    stealer_parser = StealerLogParser()
    
    # Create dummy log structure in memory-like way? No, parser reads files.
    # We will manually call the internal ingestion method to avoid file IO overhead for seeding
    
    system_info = {
        "ip": "45.33.32.156", # Real-ish IP
        "user": "TylerDurden",
        "hwid": "HWID-99887766",
        "os": "Windows 11 Pro"
    }
    
    creds = [
        {"url": "https://twitter.com", "username": "tyler_d", "password": "password123"},
        {"url": "https://wellsfargo.com", "username": "tyler.durden@paperstreet.com", "password": "password123"},
        {"url": "https://dark-market.xyz", "username": "narrator", "password": "password123"}
    ]
    
    logger.info("Ingesting mock stealer log...")
    stealer_parser._ingest_graph("infection_demo_001", system_info, creds)
    
    logger.info("Database seeding complete.")

if __name__ == "__main__":
    seed_database()

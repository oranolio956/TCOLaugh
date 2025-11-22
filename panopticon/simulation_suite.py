import requests
import concurrent.futures
import time
import random
import uuid
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(message)s',
    handlers=[
        logging.FileHandler("simulation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Sim")

API_URL = "http://localhost:8000"
HEADERS = {"X-API-Key": "panopticon-secret"}

class UserAgent:
    def __init__(self, agent_id: int):
        self.agent_id = agent_id
        self.persona = f"Agent-{agent_id:02d}"
        self.target_email = f"target_{agent_id}@shadow.net"
        self.target_username = f"target_user_{agent_id}"

    def run_session(self):
        """
        Simulates a user session:
        1. Checks stats
        2. Searches for a specific target
        3. Performs reconnaissance
        """
        try:
            # Step 1: Dashboard Check
            self._check_stats()
            time.sleep(random.uniform(0.1, 0.5))

            # Step 2: Search Person (Mix of Email and Username)
            if random.choice([True, False]):
                self._search_person("email", self.target_email)
            else:
                self._search_person("username", self.target_username)
            
            time.sleep(random.uniform(0.1, 0.5))

            # Step 3: Recon (Expensive Operation)
            if random.random() > 0.7: # 30% chance
                self._do_recon(self.target_username)

        except Exception as e:
            logger.error(f"[{self.persona}] Session Failed: {e}")

    def _check_stats(self):
        resp = requests.get(f"{API_URL}/stats")
        if resp.status_code == 200:
            logger.info(f"[{self.persona}] Stats Checked: {resp.json()}")
        else:
            logger.warning(f"[{self.persona}] Stats Failed: {resp.status_code}")

    def _search_person(self, type_: str, val: str):
        payload = {type_: val}
        resp = requests.post(f"{API_URL}/search/person", json=payload, headers=HEADERS)
        if resp.status_code == 200:
            matches = len(resp.json().get("matches", []))
            logger.info(f"[{self.persona}] Search {type_}={val} -> Found {matches}")
        else:
            logger.error(f"[{self.persona}] Search Failed: {resp.text}")

    def _do_recon(self, username: str):
        resp = requests.post(f"{API_URL}/recon/username", json={"username": username}, headers=HEADERS)
        if resp.status_code == 200:
             logger.info(f"[{self.persona}] Recon {username} -> Success")
        else:
             logger.error(f"[{self.persona}] Recon Failed: {resp.status_code}")

def inject_seed_data(num_records=100):
    """
    Injects data directly into the persistence layer via a temporary Producer,
    ensuring the Agents have something to find.
    """
    from panopticon.persistence.sqlite_manager import db_instance
    logger.info("Seeding database...")
    
    for i in range(1, 51): # Match the 50 agents
        # Create social profile
        db_instance.add_document(
            f"seed_social_{i}", "surface_web", time.time(), 
            {"username": f"target_user_{i}", "bio": "Seeded data"}
        )
        db_instance.add_node(f"user:target_user_{i}", "Identity", {"username": f"target_user_{i}"})
        
        # Create breach record
        db_instance.add_document(
            f"seed_breach_{i}", "deep_web", time.time(),
            {"email": f"target_{i}@shadow.net", "password_hash": "sha1:1234"}
        )
        db_instance.add_node(f"email:target_{i}@shadow.net", "Email", {"val": f"target_{i}@shadow.net"})

    logger.info("Seeding complete.")

def run_simulation():
    # 1. Seed Data
    inject_seed_data()
    
    # 2. Spawn 50 Concurrent Agents
    agents = [UserAgent(i) for i in range(1, 51)]
    
    logger.info(">>> STARTING 50-AGENT SIMULATION <<<")
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(agent.run_session) for agent in agents]
        concurrent.futures.wait(futures)
        
    duration = time.time() - start_time
    logger.info(f">>> SIMULATION COMPLETE in {duration:.2f}s <<<")

if __name__ == "__main__":
    run_simulation()

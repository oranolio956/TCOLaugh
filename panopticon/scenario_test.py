import json
import sys
import time

import requests


def run_scenario():
    print(">>> Starting Scenario: The 'Cipher' Network <<<")

    # 1. Define a Target Persona
    target = {
        "name": "Victor Cipher",
        "email": "v.cipher@shadow.net",
        "username": "cipher_v",
        "phone": "+15550199888",
    }

    # 2. Inject Target Data directly into Ingestion (simulating a crawl)
    # Since we can't easily inject into the running crawler process,
    # we'll simulate the ingestion by calling a hidden 'ingest' endpoint or just rely on probability?
    # Better: We'll assume the crawler is random, so we will manually POST to the persistence layer
    # But wait, we don't have an ingest API.
    # Let's create a helper script that uses the IngestionProducer directly.

    from panopticon.ingestion.kafka_interface import IngestionProducer

    producer = IngestionProducer(["localhost:9092"], "raw_ingestion")

    print("[*] Injecting Social Profile...")
    producer.send_record(
        {
            "source_type": "surface_web",
            "url": "https://darksocial.com/cipher_v",
            "raw_data": {
                "name": target["name"],
                "username": target["username"],
                "bio": "Encrypted life.",
                "location": "Unknown",
            },
            "timestamp": time.time(),
        }
    )

    print("[*] Injecting Breach Record (Pivot Point)...")
    producer.send_record(
        {
            "source_type": "deep_web",
            "dataset": "ShadowBroker Leak",
            "raw_data": {
                "email": target["email"],
                "password_hash": "sha1:deadbeef",
                "ip_address": "10.0.0.55",
            },
            "timestamp": time.time(),
        }
    )

    print("[*] Injecting Linked Identity (Same IP)...")
    producer.send_record(
        {
            "source_type": "deep_web",
            "dataset": "Gaming Forum Dump",
            "raw_data": {
                "email": "gamer_elite@yahoo.com",  # Linked account
                "password_hash": "sha1:deadbeef",  # Reuse
                "ip_address": "10.0.0.55",
            },
            "timestamp": time.time(),
        }
    )

    print(">>> Data Injected. Waiting for Indexing...")
    time.sleep(2)

    # 3. Query API
    print(">>> Executing Search Query...")
    url = "http://localhost:8000/search/person"

    # Query by Email
    print(f"[*] Searching for {target['email']}...")
    resp = requests.post(url, json={"email": target["email"]})
    if resp.status_code == 200:
        data = resp.json()
        print(f"    Found {len(data['matches'])} documents.")
        print(
            f"    Graph Context: {len(data['graph'].get('nodes', {}))} nodes, {len(data['graph'].get('edges', []))} edges."
        )

        # Check for the link
        nodes = data["graph"].get("nodes", {})
        if any("gamer_elite@yahoo.com" in str(props) for props in nodes.values()):
            print(
                "    [SUCCESS] Pivot Successful! Linked 'cipher_v' to 'gamer_elite' via Password/IP."
            )
        else:
            print("    [PARTIAL] Target found, but pivot missing. Check Graph Logic.")
    else:
        print(f"    [FAIL] API Error: {resp.text}")


if __name__ == "__main__":
    run_scenario()

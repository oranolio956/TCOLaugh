#!/usr/bin/env python3
"""
Simplified crawler for testing
"""

import time
import logging
import random
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Simple crawler started")
    
    count = 0
    while True:
        count += 1
        
        # Generate mock data
        data = {
            "id": count,
            "timestamp": time.time(),
            "type": "mock",
            "value": random.randint(1, 100)
        }
        
        logger.info(f"Generated data: {json.dumps(data)}")
        
        # Sleep for 30 seconds
        time.sleep(30)
        
        if count % 10 == 0:
            logger.info(f"Processed {count} items")

if __name__ == "__main__":
    main()
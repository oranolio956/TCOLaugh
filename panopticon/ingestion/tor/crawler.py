import logging
import requests
import time
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class TorCrawler:
    """
    Autonomous Dark Web Crawler.
    Requires a local Tor SOCKS5 proxy (usually localhost:9050).
    """
    def __init__(self, proxy_url: str = "socks5h://localhost:9050"):
        self.session = requests.Session()
        self.session.proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
        }

    def check_connection(self) -> bool:
        """
        Verifies Tor connectivity by checking IP.
        """
        try:
            resp = self.session.get("https://check.torproject.org/api/ip", timeout=10)
            if resp.status_code == 200 and resp.json().get("IsTor", False):
                logger.info(f"Tor Connection Established. IP: {resp.json().get('IP')}")
                return True
        except Exception as e:
            logger.warning(f"Tor connection failed: {e}")
        return False

    def crawl_hidden_service(self, onion_url: str) -> Dict[str, Any]:
        """
        Fetches and parses a .onion site.
        """
        try:
            logger.info(f"Crawling {onion_url}...")
            resp = self.session.get(onion_url, headers=self.headers, timeout=30)
            if resp.status_code == 200:
                return {
                    "url": onion_url,
                    "status": 200,
                    "content_len": len(resp.text),
                    "html_sample": resp.text[:500]
                    # In production: Pass HTML to IntelExtractor for entity scraping
                }
            else:
                logger.warning(f"Site returned {resp.status_code}")
        except Exception as e:
            logger.error(f"Failed to crawl {onion_url}: {e}")
        
        return {"url": onion_url, "status": "failed"}

    def run_monitor(self, targets: List[str]):
        """
        Periodically checks a list of known marketplaces/forums.
        """
        if not self.check_connection():
            logger.error("Aborting Tor Monitor: Proxy unreachable.")
            return

        for target in targets:
            data = self.crawl_hidden_service(target)
            # In production: Push 'data' to Kafka/Redis queue
            logger.info(f"Scraped {target}: {data.get('status')}")
            time.sleep(random.uniform(5, 15)) # Anti-fingerprinting delay

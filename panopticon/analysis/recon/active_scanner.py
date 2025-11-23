import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class ActiveScanner:
    def __init__(self, timeout: Optional[float] = None):
        # List of sites to check for usernames (simplified Sherlock list)
        self.sites = {
            "Twitter": "https://twitter.com/{}",
            "GitHub": "https://github.com/{}",
            "Instagram": "https://instagram.com/{}",
            "Reddit": "https://www.reddit.com/user/{}",
        }
        self.timeout = timeout or float(os.environ.get("PANOPTICON_RECON_TIMEOUT", "6"))

    async def check_username(self, username: str) -> List[Dict[str, str]]:
        """
        Checks if a username exists across multiple platforms using concurrent HTTP calls.
        """
        logger.info("Starting username scan for '%s'...", username)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            tasks = [
                self._fetch_site(client, site, template.format(username), site)
                for site, template in self.sites.items()
            ]
            responses = await asyncio.gather(*tasks, return_exceptions=True)

        results: List[Dict[str, str]] = []
        for resp in responses:
            if isinstance(resp, dict):
                results.append(resp)
        return results

    async def _fetch_site(
        self, client: httpx.AsyncClient, site: str, url: str, label: str
    ) -> Optional[Dict[str, str]]:
        try:
            response = await client.get(url, headers={"User-Agent": "panopticon-recon"})
            if response.status_code == 200:
                return {"site": site, "url": str(response.url), "status": "found"}
        except Exception as exc:
            logger.warning("Error checking %s: %s", site, exc)
        return None

    def hlr_lookup(self, phone_number: str) -> Dict[str, Any]:
        """
        Simulates an HLR (Home Location Register) lookup for a phone number.
        """
        logger.info(f"Performing HLR lookup for {phone_number}...")
        # In reality, this calls a paid API like Twilio or HLR-Lookups.com
        # Mock response:
        return {
            "number": phone_number,
            "status": "active",
            "carrier": "Verizon Wireless",
            "country_code": "US",
            "roaming": False,
        }

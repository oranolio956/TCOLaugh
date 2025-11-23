import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class ActiveScanner:
    def __init__(self, timeout: Optional[float] = None):
        # List of sites to check for usernames
        # Note: Some sites might require specific headers or handling to avoid false positives.
        # This implementation assumes 200 OK means "found" and 404 means "not found".
        self.sites = {
            "GitHub": "https://github.com/{}",
            "Reddit": "https://www.reddit.com/user/{}",
            "Medium": "https://medium.com/@{}",
            "Vimeo": "https://vimeo.com/{}",
            "SoundCloud": "https://soundcloud.com/{}",
            "Pastebin": "https://pastebin.com/u/{}",
            "Gravatar": "http://en.gravatar.com/{}",
            "GitLab": "https://gitlab.com/{}",
            "About.me": "https://about.me/{}",
            "Flickr": "https://www.flickr.com/people/{}",
            "Steam": "https://steamcommunity.com/id/{}",
            "Wikipedia": "https://en.wikipedia.org/wiki/User:{}",
            # Twitter/Instagram are kept but might be flaky due to strict anti-bot
            "Twitter": "https://twitter.com/{}", 
            "Instagram": "https://instagram.com/{}",
        }
        self.timeout = timeout or float(os.environ.get("PANOPTICON_RECON_TIMEOUT", "10"))
        
        # Mimic a real browser to avoid immediate blocking
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }

    async def check_username(self, username: str) -> List[Dict[str, str]]:
        """
        Checks if a username exists across multiple platforms using concurrent HTTP calls.
        """
        logger.info("Starting username scan for '%s'...", username)
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            tasks = [
                self._fetch_site(client, site, template.format(username), site)
                for site, template in self.sites.items()
            ]
            responses = await asyncio.gather(*tasks, return_exceptions=True)

        results: List[Dict[str, str]] = []
        for resp in responses:
            if isinstance(resp, dict) and resp:
                results.append(resp)
        return results

    async def _fetch_site(
        self, client: httpx.AsyncClient, site: str, url: str, label: str
    ) -> Optional[Dict[str, str]]:
        try:
            response = await client.get(url, headers=self.headers)
            
            # Site specific logic
            if site == "Reddit":
                # Reddit might return 200 with "page not found" content for banned/shadowbanned? 
                # But usually 404 if user doesn't exist.
                pass 
            elif site == "Instagram":
                if "Login" in response.text or response.status_code == 302:
                     # Often redirects to login, treating as "Unknown" or ignoring
                     return None

            if response.status_code == 200:
                return {"site": site, "url": str(response.url), "status": "found"}
        except Exception as exc:
            # logger.warning("Error checking %s: %s", site, exc)
            pass
        return None

    def hlr_lookup(self, phone_number: str) -> Dict[str, Any]:
        """
        Simulates an HLR (Home Location Register) lookup for a phone number.
        """
        logger.info(f"Performing HLR lookup for {phone_number}...")
        # In reality, this calls a paid API like Twilio or HLR-Lookups.com
        # Since we don't have a paid API key, we mock this part but realistically.
        # We can at least validate the number format and guess carrier via prefixes (mocked here).
        
        return {
            "number": phone_number,
            "status": "active",
            "carrier": "Unknown Carrier (Requires Paid API)",
            "country_code": "US", # Assumption
            "roaming": False,
        }

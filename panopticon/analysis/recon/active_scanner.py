import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

import httpx

from panopticon.analysis.recon.detection_engine import DetectionEngine
from panopticon.analysis.recon.platform_database import PlatformDatabase, PlatformDefinition

logger = logging.getLogger(__name__)


class ActiveScanner:
    def __init__(self, timeout: Optional[float] = None, platform_db_path: Optional[str] = None):
        """
        Initialize the Active Scanner.
        
        Args:
            timeout: Request timeout in seconds
            platform_db_path: Path to platform database JSON file (optional)
        """
        self.timeout = timeout or float(os.environ.get("PANOPTICON_RECON_TIMEOUT", "6"))
        
        # Load platform database
        try:
            self.platform_db = PlatformDatabase(platform_db_path)
            logger.info(f"Loaded {self.platform_db.count()} platforms from database")
        except Exception as e:
            logger.warning(f"Failed to load platform database: {e}. Using fallback.")
            self.platform_db = None
        
        # Fallback to simple sites if database fails
        if not self.platform_db or self.platform_db.count() == 0:
            logger.warning("Using fallback platform list (4 platforms)")
            self.sites = {
                "Twitter": "https://twitter.com/{}",
                "GitHub": "https://github.com/{}",
                "Instagram": "https://instagram.com/{}",
                "Reddit": "https://www.reddit.com/user/{}",
            }
        else:
            self.sites = None  # Will use platform_db instead

    async def check_username(self, username: str, platform_filter: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Checks if a username exists across multiple platforms using concurrent HTTP calls.
        
        Args:
            username: Username to check
            platform_filter: Optional list of platform names to check (None = all platforms)
        
        Returns:
            List of results with platform name, URL, status, and detection details
        """
        logger.info("Starting username scan for '%s'...", username)
        
        # Get platforms to check
        if self.platform_db and self.platform_db.count() > 0:
            # Use platform database
            if platform_filter:
                platforms = [
                    self.platform_db.get_platform(name)
                    for name in platform_filter
                    if self.platform_db.get_platform(name)
                ]
            else:
                platforms = list(self.platform_db.get_all_platforms().values())
            
            # Filter out NSFW platforms by default (can be enabled via filter)
            platforms = [p for p in platforms if not p.is_nsfw or (platform_filter and p.name in platform_filter)]
            
            logger.info(f"Checking {len(platforms)} platforms for username '{username}'")
        else:
            # Fallback to simple sites
            platforms = None
            if platform_filter:
                sites_to_check = {k: v for k, v in self.sites.items() if k in platform_filter}
            else:
                sites_to_check = self.sites
            
            logger.info(f"Checking {len(sites_to_check)} platforms (fallback mode) for username '{username}'")
        
        # Execute checks concurrently
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            if platforms:
                # Use platform database
                tasks = [
                    self._check_platform(client, platform, username)
                    for platform in platforms
                    if platform.validate_username(username)
                ]
            else:
                # Use fallback sites
                tasks = [
                    self._check_site_fallback(client, site, template.format(username), site)
                    for site, template in sites_to_check.items()
                ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        results: List[Dict[str, Any]] = []
        for resp in responses:
            if isinstance(resp, dict):
                results.append(resp)
            elif isinstance(resp, Exception):
                logger.warning(f"Exception during platform check: {resp}")
        
        logger.info(f"Found username on {sum(1 for r in results if r.get('found', False))} platform(s)")
        return results

    async def _check_platform(
        self, client: httpx.AsyncClient, platform: PlatformDefinition, username: str
    ) -> Optional[Dict[str, Any]]:
        """
        Check a single platform using the platform definition.
        
        Args:
            client: HTTP client
            platform: Platform definition
            username: Username to check
        
        Returns:
            Result dict or None if check failed
        """
        url = platform.build_url(username)
        
        try:
            # Prepare headers
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            headers.update(platform.headers)
            
            # Make request
            if platform.request_method == "POST":
                response = await client.post(
                    url,
                    json=platform.request_payload,
                    headers=headers
                )
            else:
                response = await client.get(url, headers=headers)
            
            # Get final URL after redirects
            final_url = str(response.url)
            
            # Detect using intelligent engine
            detection_result = DetectionEngine.detect(
                platform,
                response.status_code,
                response.text,
                url,
                final_url
            )
            
            # Only return if username was found
            if detection_result.found:
                return {
                    "site": platform.name,
                    "url": final_url,
                    "status": "found",
                    "confidence": detection_result.confidence,
                    "method": detection_result.method,
                    "details": detection_result.details,
                    "status_code": response.status_code
                }
            
            return None
        
        except httpx.TimeoutException:
            logger.debug(f"Timeout checking {platform.name} for {username}")
            return None
        except Exception as exc:
            logger.warning(f"Error checking {platform.name} for {username}: {exc}")
            return None

    async def _check_site_fallback(
        self, client: httpx.AsyncClient, site: str, url: str, label: str
    ) -> Optional[Dict[str, str]]:
        """
        Fallback method for simple site checking (backward compatibility).
        
        Args:
            client: HTTP client
            site: Site name
            url: URL to check
            label: Label for logging
        
        Returns:
            Result dict or None
        """
        try:
            response = await client.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
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

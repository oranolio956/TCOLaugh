"""
Optimized ActiveScanner with performance improvements:
- HTTP connection pooling
- Reduced timeouts
- Better concurrency control
- Early termination option
- Skip slow/unreliable platforms
"""
import asyncio
import logging
import os
import time
from typing import Any, Dict, List, Optional

import httpx

from panopticon.analysis.recon.detection_engine import DetectionEngine
# Enhanced detection is now the default
USE_ENHANCED_DETECTION = True
EnhancedDetectionEngine = DetectionEngine
from panopticon.analysis.recon.platform_database import PlatformDatabase, PlatformDefinition

logger = logging.getLogger(__name__)


class ActiveScanner:
    def __init__(
        self,
        timeout: Optional[float] = None,
        platform_db_path: Optional[str] = None,
        max_concurrent: int = 50,
        early_termination: Optional[int] = None,
    ):
        """
        Initialize the Active Scanner with performance optimizations.
        
        Args:
            timeout: Request timeout in seconds (default: 3.0 for faster results)
            platform_db_path: Path to platform database JSON file (optional)
            max_concurrent: Maximum concurrent requests (default: 50)
            early_termination: Return after N results found (None = check all)
        """
        # Reduced timeout for faster results (most requests complete in <200ms)
        self.timeout = timeout or float(os.environ.get("PANOPTICON_RECON_TIMEOUT", "3.0"))
        self.max_concurrent = max_concurrent
        self.early_termination = early_termination
        
        # HTTP client with connection pooling (reused across requests)
        self._client: Optional[httpx.AsyncClient] = None
        
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
            self.sites = None
        
        # Known slow/unreliable platforms to skip (can be overridden)
        self.skip_platforms = set([
            # Platforms that frequently timeout or return 403
            "BreachSta.rs Forum",  # DNS issues
            # Add more as we discover them
        ])

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with connection pooling."""
        if self._client is None:
            # Create client with optimized settings
            limits = httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100,
                keepalive_expiry=30.0
            )
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                limits=limits
                # Note: http2=True requires 'pip install httpx[http2]' but provides better performance
            )
        return self._client

    async def close(self):
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def check_username(
        self,
        username: str,
        platform_filter: Optional[List[str]] = None,
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Checks if a username exists across multiple platforms using concurrent HTTP calls.
        
        Args:
            username: Username to check
            platform_filter: Optional list of platform names to check (None = all platforms)
            max_results: Maximum number of results to return (None = all found)
        
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
            
            # Filter out NSFW platforms by default
            platforms = [p for p in platforms if not p.is_nsfw or (platform_filter and p.name in platform_filter)]
            
            # Skip known slow/unreliable platforms
            platforms = [p for p in platforms if p.name not in self.skip_platforms]
            
            logger.info(f"Checking {len(platforms)} platforms for username '{username}'")
        else:
            # Fallback to simple sites
            platforms = None
            if platform_filter:
                sites_to_check = {k: v for k, v in self.sites.items() if k in platform_filter}
            else:
                sites_to_check = self.sites
            
            logger.info(f"Checking {len(sites_to_check)} platforms (fallback mode) for username '{username}'")
        
        # Get HTTP client
        client = await self._get_client()
        
        # Execute checks concurrently with semaphore for rate limiting
        semaphore = asyncio.Semaphore(self.max_concurrent)
        results: List[Dict[str, Any]] = []
        results_lock = asyncio.Lock()
        
        async def check_with_semaphore(platform_or_site):
            """Check platform with semaphore control."""
            async with semaphore:
                start_time = time.time()
                try:
                    if platforms:
                        result = await self._check_platform(client, platform_or_site, username, start_time)
                    else:
                        site_name, template = platform_or_site
                        result = await self._check_site_fallback(client, site_name, template.format(username), site_name, start_time)
                    
                    if result:
                        async with results_lock:
                            results.append(result)
                            # Early termination if we have enough results
                            if self.early_termination and len(results) >= self.early_termination:
                                return "stop"
                            if max_results and len(results) >= max_results:
                                return "stop"
                except Exception as e:
                    logger.debug(f"Error in check_with_semaphore: {e}")
                return "continue"
        
        # Create tasks
        if platforms:
            tasks = [
                check_with_semaphore(platform)
                for platform in platforms
                if platform.validate_username(username)
            ]
        else:
            tasks = [
                check_with_semaphore((site, template))
                for site, template in sites_to_check.items()
            ]
        
        # Execute with early termination support
        if self.early_termination or max_results:
            # Check tasks one by one and stop early if needed
            for task in asyncio.as_completed(tasks):
                status = await task
                if status == "stop":
                    # Cancel remaining tasks
                    for t in tasks:
                        if not t.done():
                            t.cancel()
                    break
        else:
            # Execute all tasks
            await asyncio.gather(*tasks, return_exceptions=True)
        
        found_count = len(results)
        logger.info(f"Found username on {found_count} platform(s)")
        return results[:max_results] if max_results else results

    async def _check_platform(
        self, client: httpx.AsyncClient, platform: PlatformDefinition, username: str, start_time: Optional[float] = None
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
            # Track request start time
            request_start = start_time if start_time else time.time()
            
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
            
            # Calculate response time
            response_time = time.time() - request_start
            
            # Get final URL after redirects
            final_url = str(response.url)
            
            # Detect using intelligent engine (enhanced if available)
            if USE_ENHANCED_DETECTION:
                detection_result = EnhancedDetectionEngine.detect_enhanced(
                    platform,
                    response.status_code,
                    response.text,
                    url,
                    final_url,
                    response_time=response_time
                )
            else:
                detection_result = DetectionEngine.detect(
                    platform,
                    response.status_code,
                    response.text,
                    url,
                    final_url
                )
            
            # Only return if username was found
            if detection_result.found:
                result = {
                    "site": platform.name,
                    "url": final_url,
                    "status": "found",
                    "confidence": detection_result.confidence,
                    "method": detection_result.method,
                    "details": detection_result.details,
                    "status_code": response.status_code
                }
                # Add enhanced metadata if available
                if USE_ENHANCED_DETECTION and hasattr(detection_result, 'methods_used'):
                    result["methods_used"] = detection_result.methods_used
                if response_time:
                    result["response_time_ms"] = round(response_time * 1000, 2)
                return result
            
            return None
        
        except httpx.TimeoutException:
            logger.debug(f"Timeout checking {platform.name} for {username}")
            return None
        except Exception as exc:
            logger.debug(f"Error checking {platform.name} for {username}: {exc}")
            return None

    async def _check_site_fallback(
        self, client: httpx.AsyncClient, site: str, url: str, label: str, start_time: Optional[float] = None
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
            request_start = start_time if start_time else time.time()
            response = await client.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            response_time = time.time() - request_start
            if response.status_code == 200:
                result = {"site": site, "url": str(response.url), "status": "found"}
                if response_time:
                    result["response_time_ms"] = round(response_time * 1000, 2)
                return result
        except Exception as exc:
            logger.debug(f"Error checking {site}: {exc}")
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

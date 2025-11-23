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
from panopticon.analysis.recon.proxy_manager import ProxyManager, ProxyConfig
from panopticon.analysis.recon.user_agent_rotator import UserAgentRotator
from panopticon.analysis.recon.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class ActiveScanner:
    def __init__(
        self,
        timeout: Optional[float] = None,
        platform_db_path: Optional[str] = None,
        max_concurrent: int = 50,
        early_termination: Optional[int] = None,
        enable_proxy: Optional[bool] = None,
        proxy_configs: Optional[List[ProxyConfig]] = None,
        enable_rate_limiting: bool = True,
        enable_user_agent_rotation: bool = True,
    ):
        """
        Initialize the Active Scanner with performance optimizations and stealth features.
        
        Args:
            timeout: Request timeout in seconds (default: 3.0 for faster results)
            platform_db_path: Path to platform database JSON file (optional)
            max_concurrent: Maximum concurrent requests (default: 50)
            early_termination: Return after N results found (None = check all)
            enable_proxy: Whether to use proxies (None = auto-detect from env)
            proxy_configs: List of proxy configurations (optional)
            enable_rate_limiting: Whether to use rate limiting (default: True)
            enable_user_agent_rotation: Whether to rotate User-Agents (default: True)
        """
        # Reduced timeout for faster results (most requests complete in <200ms)
        self.timeout = timeout or float(os.environ.get("PANOPTICON_RECON_TIMEOUT", "3.0"))
        self.max_concurrent = max_concurrent
        self.early_termination = early_termination
        
        # Stealth features
        if enable_proxy is None:
            enable_proxy = bool(os.environ.get("PANOPTICON_ENABLE_PROXY", "false").lower() == "true")
        
        self.proxy_manager = ProxyManager(
            proxy_configs=proxy_configs,
            enable_proxy=enable_proxy
        )
        
        self.rate_limiter = RateLimiter() if enable_rate_limiting else None
        self.user_agent_rotator = UserAgentRotator() if enable_user_agent_rotation else None
        
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

    async def _get_client(self, use_proxy: bool = True) -> httpx.AsyncClient:
        """
        Get or create HTTP client with connection pooling and proxy support.
        
        Args:
            use_proxy: Whether to use proxy for this client
        
        Note: If proxies are enabled, we create a new client per request for rotation.
        Otherwise, we reuse a single client for connection pooling.
        """
        # If proxies are enabled, create client per request for rotation
        if use_proxy and self.proxy_manager.enable_proxy:
            proxy_dict = await self.proxy_manager.get_proxy(rotate=True)
            if proxy_dict:
                limits = httpx.Limits(
                    max_keepalive_connections=20,
                    max_connections=100,
                    keepalive_expiry=30.0
                )
                return httpx.AsyncClient(
                    timeout=self.timeout,
                    follow_redirects=True,
                    limits=limits,
                    proxies=proxy_dict
                )
        
        # Reuse single client when proxies disabled (connection pooling)
        if self._client is None:
            limits = httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100,
                keepalive_expiry=30.0
            )
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                limits=limits
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
        
        # Note: Client will be created per-task if proxies enabled (for rotation)
        # Otherwise, we'll reuse a single client
        use_proxy = self.proxy_manager.enable_proxy if self.proxy_manager else False
        
        # Execute checks concurrently with semaphore for rate limiting
        semaphore = asyncio.Semaphore(self.max_concurrent)
        results: List[Dict[str, Any]] = []
        results_lock = asyncio.Lock()
        
        async def check_with_semaphore(platform_or_site):
            """Check platform with semaphore control and stealth features."""
            async with semaphore:
                start_time = time.time()
                try:
                    # Get platform name for rate limiting
                    platform_name = platform_or_site.name if platforms else platform_or_site[0]
                    
                    # Rate limiting (if enabled)
                    if self.rate_limiter:
                        await self.rate_limiter.wait_if_needed(platform_name)
                        # Add random delay for human-like behavior
                        await self.rate_limiter.add_delay(platform_name, min_delay=0.1, max_delay=0.5)
                    
                    # Get client (with proxy rotation if enabled)
                    client = await self._get_client(use_proxy=use_proxy)
                    
                    if platforms:
                        result = await self._check_platform(client, platform_or_site, username, start_time)
                    else:
                        site_name, template = platform_or_site
                        result = await self._check_site_fallback(client, site_name, template.format(username), site_name, start_time)
                    
                    # Close client if it was proxy-specific (not the shared one)
                    if use_proxy and client != self._client:
                        await client.aclose()
                    
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
            
            # Prepare headers with User-Agent rotation
            if self.user_agent_rotator:
                user_agent = self.user_agent_rotator.get_rotated()
            else:
                user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            
            headers = {
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
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
            
            # Get User-Agent
            if self.user_agent_rotator:
                user_agent = self.user_agent_rotator.get_rotated()
            else:
                user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            
            response = await client.get(
                url,
                headers={"User-Agent": user_agent}
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

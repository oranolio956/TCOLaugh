"""
Proxy Manager Module

Manages proxy rotation and health checking for stealth operations.
Supports multiple proxy providers: Smartproxy, IPRoyal, Bright Data.
"""
import asyncio
import logging
import os
import random
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)


class ProxyConfig:
    """Configuration for a proxy provider."""
    
    def __init__(
        self,
        provider: str,
        endpoint: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        auth_type: str = "basic",  # basic, bearer, header
        auth_header: Optional[str] = None,
    ):
        self.provider = provider
        self.endpoint = endpoint
        self.username = username
        self.password = password
        self.auth_type = auth_type
        self.auth_header = auth_header or "Proxy-Authorization"
    
    def get_proxy_url(self) -> str:
        """Get proxy URL with authentication."""
        parsed = urlparse(self.endpoint)
        
        if self.username and self.password:
            # Add auth to URL
            auth = f"{self.username}:{self.password}@"
            return f"{parsed.scheme}://{auth}{parsed.netloc}{parsed.path}"
        
        return self.endpoint
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers if needed."""
        if self.auth_type == "bearer" and self.password:
            return {self.auth_header: f"Bearer {self.password}"}
        return {}


class ProxyManager:
    """Manages proxy rotation and health checking."""
    
    def __init__(
        self,
        proxy_configs: Optional[List[ProxyConfig]] = None,
        enable_proxy: bool = True,
        health_check_enabled: bool = True,
        health_check_timeout: float = 5.0,
    ):
        """
        Initialize proxy manager.
        
        Args:
            proxy_configs: List of proxy configurations
            enable_proxy: Whether to use proxies (can be disabled for testing)
            health_check_enabled: Whether to check proxy health
            health_check_timeout: Timeout for health checks
        """
        self.enable_proxy = enable_proxy and proxy_configs is not None and len(proxy_configs) > 0
        self.proxy_configs = proxy_configs or []
        self.health_check_enabled = health_check_enabled
        self.health_check_timeout = health_check_timeout
        
        # Track proxy health and usage
        self.proxy_health: Dict[int, bool] = {}  # Index -> is_healthy
        self.proxy_usage_count: Dict[int, int] = {}  # Index -> usage count
        self.current_proxy_index = 0
        
        # Load from environment if no configs provided
        if not self.proxy_configs and self.enable_proxy:
            self._load_from_environment()
    
    def _load_from_environment(self):
        """Load proxy configuration from environment variables."""
        # Smartproxy
        smartproxy_endpoint = os.environ.get("SMARTPROXY_ENDPOINT")
        if smartproxy_endpoint:
            username = os.environ.get("SMARTPROXY_USERNAME")
            password = os.environ.get("SMARTPROXY_PASSWORD")
            self.proxy_configs.append(ProxyConfig(
                provider="smartproxy",
                endpoint=smartproxy_endpoint,
                username=username,
                password=password
            ))
        
        # IPRoyal
        iproyal_endpoint = os.environ.get("IPROYAL_ENDPOINT")
        if iproyal_endpoint:
            username = os.environ.get("IPROYAL_USERNAME")
            password = os.environ.get("IPROYAL_PASSWORD")
            self.proxy_configs.append(ProxyConfig(
                provider="iproyal",
                endpoint=iproyal_endpoint,
                username=username,
                password=password
            ))
        
        # Bright Data
        brightdata_endpoint = os.environ.get("BRIGHTDATA_ENDPOINT")
        if brightdata_endpoint:
            username = os.environ.get("BRIGHTDATA_USERNAME")
            password = os.environ.get("BRIGHTDATA_PASSWORD")
            self.proxy_configs.append(ProxyConfig(
                provider="brightdata",
                endpoint=brightdata_endpoint,
                username=username,
                password=password
            ))
        
        if self.proxy_configs:
            logger.info(f"Loaded {len(self.proxy_configs)} proxy configuration(s) from environment")
    
    async def get_proxy(self, rotate: bool = True) -> Optional[Dict[str, str]]:
        """
        Get a proxy configuration for use.
        
        Args:
            rotate: Whether to rotate to next proxy
        
        Returns:
            Proxy dict for httpx or None if no proxies available
        """
        if not self.enable_proxy or not self.proxy_configs:
            return None
        
        # Find healthy proxy
        healthy_proxies = [
            i for i, config in enumerate(self.proxy_configs)
            if self.proxy_health.get(i, True)  # Default to healthy if not checked
        ]
        
        if not healthy_proxies:
            # All proxies unhealthy, reset health status
            logger.warning("All proxies marked unhealthy, resetting health status")
            self.proxy_health.clear()
            healthy_proxies = list(range(len(self.proxy_configs)))
        
        # Select proxy (round-robin or random)
        if rotate:
            self.current_proxy_index = (self.current_proxy_index + 1) % len(healthy_proxies)
            proxy_index = healthy_proxies[self.current_proxy_index]
        else:
            proxy_index = random.choice(healthy_proxies)
        
        config = self.proxy_configs[proxy_index]
        self.proxy_usage_count[proxy_index] = self.proxy_usage_count.get(proxy_index, 0) + 1
        
        # Build proxy dict
        proxy_url = config.get_proxy_url()
        
        return {
            "http://": proxy_url,
            "https://": proxy_url,
            **config.get_auth_headers()
        }
    
    async def check_proxy_health(self, proxy_index: int) -> bool:
        """
        Check if a proxy is healthy.
        
        Args:
            proxy_index: Index of proxy to check
        
        Returns:
            True if proxy is healthy
        """
        if not self.health_check_enabled:
            return True
        
        config = self.proxy_configs[proxy_index]
        proxy_url = config.get_proxy_url()
        
        try:
            async with httpx.AsyncClient(
                proxies={
                    "http://": proxy_url,
                    "https://": proxy_url,
                },
                timeout=self.health_check_timeout,
                **config.get_auth_headers()
            ) as client:
                # Test with a simple request
                response = await client.get("http://httpbin.org/ip", timeout=self.health_check_timeout)
                is_healthy = response.status_code == 200
                self.proxy_health[proxy_index] = is_healthy
                return is_healthy
        except Exception as e:
            logger.debug(f"Proxy {proxy_index} ({config.provider}) health check failed: {e}")
            self.proxy_health[proxy_index] = False
            return False
    
    async def check_all_proxies(self):
        """Check health of all proxies."""
        if not self.enable_proxy:
            return
        
        tasks = [
            self.check_proxy_health(i)
            for i in range(len(self.proxy_configs))
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        healthy_count = sum(1 for h in self.proxy_health.values() if h)
        logger.info(f"Proxy health check: {healthy_count}/{len(self.proxy_configs)} proxies healthy")
    
    def mark_proxy_unhealthy(self, proxy_index: int):
        """Mark a proxy as unhealthy."""
        self.proxy_health[proxy_index] = False
        logger.warning(f"Marked proxy {proxy_index} ({self.proxy_configs[proxy_index].provider}) as unhealthy")
    
    def get_stats(self) -> Dict:
        """Get proxy usage statistics."""
        return {
            "total_proxies": len(self.proxy_configs),
            "healthy_proxies": sum(1 for h in self.proxy_health.values() if h),
            "usage_counts": self.proxy_usage_count.copy(),
            "enabled": self.enable_proxy
        }

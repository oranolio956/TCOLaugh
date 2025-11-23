"""
Rate Limiter Module

Per-platform rate limiting to avoid detection and bans.
"""
import asyncio
import logging
import random
import time
from collections import defaultdict
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class RateLimiter:
    """Per-platform rate limiter."""
    
    def __init__(
        self,
        default_requests_per_minute: int = 30,
        per_platform_limits: Optional[Dict[str, int]] = None,
        respect_robots_txt: bool = True,
    ):
        """
        Initialize rate limiter.
        
        Args:
            default_requests_per_minute: Default rate limit (requests per minute)
            per_platform_limits: Custom limits per platform name
            respect_robots_txt: Whether to respect robots.txt (future feature)
        """
        self.default_rpm = default_requests_per_minute
        self.per_platform_limits = per_platform_limits or {}
        self.respect_robots_txt = respect_robots_txt
        
        # Track request times per platform
        self.request_times: Dict[str, list] = defaultdict(list)
        self.locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        
        # Known platform limits (requests per minute)
        self.platform_limits = {
            "GitHub": 60,  # GitHub allows 60 requests/hour for unauthenticated
            "Twitter": 15,  # Twitter is strict
            "Instagram": 10,  # Instagram is very strict
            "Reddit": 60,  # Reddit allows more
            "LinkedIn": 5,  # LinkedIn is very strict
        }
        self.platform_limits.update(self.per_platform_limits)
    
    def get_limit(self, platform_name: str) -> int:
        """Get rate limit for a platform."""
        return self.platform_limits.get(platform_name, self.default_rpm)
    
    async def wait_if_needed(self, platform_name: str):
        """
        Wait if rate limit would be exceeded.
        
        Args:
            platform_name: Name of platform to check
        """
        async with self.locks[platform_name]:
            now = time.time()
            limit = self.get_limit(platform_name)
            
            # Clean old requests (older than 1 minute)
            self.request_times[platform_name] = [
                t for t in self.request_times[platform_name]
                if now - t < 60.0
            ]
            
            # Check if we're at the limit
            if len(self.request_times[platform_name]) >= limit:
                # Calculate wait time
                oldest_request = min(self.request_times[platform_name])
                wait_time = 60.0 - (now - oldest_request) + 0.1  # Add small buffer
                
                if wait_time > 0:
                    logger.debug(f"Rate limit reached for {platform_name}, waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    # Clean again after wait
                    now = time.time()
                    self.request_times[platform_name] = [
                        t for t in self.request_times[platform_name]
                        if now - t < 60.0
                    ]
            
            # Record this request
            self.request_times[platform_name].append(time.time())
    
    async def add_delay(self, platform_name: str, min_delay: float = 0.5, max_delay: float = 2.0):
        """
        Add a random delay to appear more human-like.
        
        Args:
            platform_name: Platform name (for logging)
            min_delay: Minimum delay in seconds
            max_delay: Maximum delay in seconds
        """
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)
    
    def get_stats(self) -> Dict:
        """Get rate limiting statistics."""
        return {
            "platform_limits": self.platform_limits.copy(),
            "current_requests": {
                platform: len(times)
                for platform, times in self.request_times.items()
            }
        }

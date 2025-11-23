"""
User-Agent Rotator Module

Rotates User-Agent strings to avoid detection.
Uses real browser User-Agents from different platforms.
"""
import random
from typing import List, Optional

# Real User-Agent strings from various browsers/platforms
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    
    # Chrome on Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    
    # Firefox on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    
    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    
    # Mobile Chrome (Android)
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    
    # Mobile Safari (iOS)
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
]


class UserAgentRotator:
    """Rotates User-Agent strings."""
    
    def __init__(self, user_agents: Optional[List[str]] = None):
        """
        Initialize User-Agent rotator.
        
        Args:
            user_agents: Custom list of User-Agent strings (uses default if None)
        """
        self.user_agents = user_agents or USER_AGENTS
        self.current_index = 0
    
    def get_random(self) -> str:
        """Get a random User-Agent."""
        return random.choice(self.user_agents)
    
    def get_rotated(self) -> str:
        """Get next User-Agent in rotation."""
        ua = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        return ua
    
    def get_chrome(self) -> str:
        """Get a Chrome User-Agent."""
        chrome_agents = [ua for ua in self.user_agents if "Chrome" in ua and "Edg" not in ua]
        return random.choice(chrome_agents) if chrome_agents else self.user_agents[0]
    
    def get_firefox(self) -> str:
        """Get a Firefox User-Agent."""
        firefox_agents = [ua for ua in self.user_agents if "Firefox" in ua]
        return random.choice(firefox_agents) if firefox_agents else self.user_agents[0]
    
    def get_safari(self) -> str:
        """Get a Safari User-Agent."""
        safari_agents = [ua for ua in self.user_agents if "Safari" in ua and "Chrome" not in ua]
        return random.choice(safari_agents) if safari_agents else self.user_agents[0]

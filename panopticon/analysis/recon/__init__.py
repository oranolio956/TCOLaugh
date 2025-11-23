"""
Reconnaissance Module

Provides username reconnaissance across multiple platforms.
"""
from panopticon.analysis.recon.active_scanner import ActiveScanner
from panopticon.analysis.recon.detection_engine import DetectionEngine, DetectionResult
from panopticon.analysis.recon.platform_database import PlatformDatabase, PlatformDefinition
from panopticon.analysis.recon.proxy_manager import ProxyManager, ProxyConfig
from panopticon.analysis.recon.rate_limiter import RateLimiter
from panopticon.analysis.recon.user_agent_rotator import UserAgentRotator

__all__ = [
    "ActiveScanner",
    "DetectionEngine",
    "DetectionResult",
    "PlatformDatabase",
    "PlatformDefinition",
    "ProxyManager",
    "ProxyConfig",
    "RateLimiter",
    "UserAgentRotator",
]

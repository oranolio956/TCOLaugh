"""
Platform Database Module

Manages the platform definitions for username reconnaissance.
Based on Sherlock's platform structure but enhanced with intelligent detection.
"""
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PlatformDefinition:
    """Represents a single platform definition."""
    
    def __init__(self, name: str, data: Dict[str, Any]):
        self.name = name
        self.url_template = data.get("url", "")
        self.url_main = data.get("urlMain", "")
        self.error_type = data.get("errorType", "status_code")
        self.error_msg = data.get("errorMsg", [])
        self.error_code = data.get("errorCode", [404])
        self.error_url = data.get("errorUrl", "")
        self.username_claimed = data.get("username_claimed", "")
        self.regex_check = data.get("regexCheck")
        self.request_method = data.get("request_method", "GET")
        self.request_payload = data.get("request_payload")
        self.headers = data.get("headers", {})
        self.is_nsfw = data.get("isNSFW", False)
        self.tags = data.get("tags", [])
        
        # Normalize error_type to list
        if isinstance(self.error_type, str):
            self.error_type = [self.error_type]
        if isinstance(self.error_msg, str):
            self.error_msg = [self.error_msg]
        if isinstance(self.error_code, int):
            self.error_code = [self.error_code]
    
    def validate_username(self, username: str) -> bool:
        """Validate username format against regex if specified."""
        if not self.regex_check:
            return True
        try:
            return bool(re.match(self.regex_check, username))
        except re.error:
            logger.warning(f"Invalid regex for {self.name}: {self.regex_check}")
            return True
    
    def build_url(self, username: str) -> str:
        """Build the full URL for a username."""
        return self.url_template.format(username)
    
    def __repr__(self) -> str:
        return f"PlatformDefinition(name={self.name}, url={self.url_main})"


class PlatformDatabase:
    """Manages the platform database."""
    
    def __init__(self, data_file: Optional[str] = None):
        """
        Initialize platform database.
        
        Args:
            data_file: Path to JSON file with platform definitions.
                      If None, uses default location.
        """
        if data_file is None:
            # Default location
            data_file = Path(__file__).parent / "platforms" / "platforms.json"
        
        self.data_file = Path(data_file)
        self.platforms: Dict[str, PlatformDefinition] = {}
        self._load_platforms()
    
    def _load_platforms(self):
        """Load platforms from JSON file."""
        if not self.data_file.exists():
            logger.warning(f"Platform database not found at {self.data_file}")
            return
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Filter out schema keys
            platform_data = {k: v for k, v in data.items() if not k.startswith("$")}
            
            for name, platform_info in platform_data.items():
                try:
                    self.platforms[name] = PlatformDefinition(name, platform_info)
                except Exception as e:
                    logger.error(f"Error loading platform {name}: {e}")
            
            logger.info(f"Loaded {len(self.platforms)} platforms from {self.data_file}")
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in platform database: {e}")
        except Exception as e:
            logger.error(f"Error loading platform database: {e}")
    
    def get_platform(self, name: str) -> Optional[PlatformDefinition]:
        """Get a platform by name."""
        return self.platforms.get(name)
    
    def get_all_platforms(self) -> Dict[str, PlatformDefinition]:
        """Get all platforms."""
        return self.platforms.copy()
    
    def get_platforms_by_tag(self, tag: str) -> List[PlatformDefinition]:
        """Get platforms with a specific tag."""
        return [
            platform for platform in self.platforms.values()
            if tag in platform.tags
        ]
    
    def count(self) -> int:
        """Get total number of platforms."""
        return len(self.platforms)

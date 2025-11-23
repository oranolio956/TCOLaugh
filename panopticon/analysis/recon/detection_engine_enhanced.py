"""
Enhanced Detection Engine Module

Advanced detection methods beyond status codes:
- Profile-specific element detection
- Response time analysis
- JSON response parsing
- Multiple method combination
- Enhanced redirect analysis
"""
import json
import logging
import re
import time
from typing import Dict, List, Optional, Tuple

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class DetectionResult:
    """Result of a detection attempt with enhanced metadata."""
    
    def __init__(
        self,
        found: bool,
        confidence: float = 0.0,
        method: str = "",
        details: str = "",
        methods_used: Optional[List[str]] = None,
        response_time: Optional[float] = None
    ):
        self.found = found
        self.confidence = confidence  # 0.0 to 1.0
        self.method = method  # Primary method
        self.details = details
        self.methods_used = methods_used or []
        self.response_time = response_time
    
    def combine(self, other: "DetectionResult") -> "DetectionResult":
        """Combine with another detection result for higher confidence."""
        if self.found == other.found:
            # Same conclusion - increase confidence
            combined_confidence = min(1.0, (self.confidence + other.confidence) / 2 + 0.1)
            combined_methods = list(set(self.methods_used + other.methods_used))
            return DetectionResult(
                found=self.found,
                confidence=combined_confidence,
                method=f"{self.method}+{other.method}",
                details=f"Combined: {self.details} | {other.details}",
                methods_used=combined_methods,
                response_time=self.response_time or other.response_time
            )
        else:
            # Conflicting results - use higher confidence
            if self.confidence > other.confidence:
                return self
            return other
    
    def __repr__(self) -> str:
        status = "FOUND" if self.found else "NOT_FOUND"
        methods_str = "+".join(self.methods_used) if self.methods_used else self.method
        return f"DetectionResult({status}, confidence={self.confidence:.2f}, methods={methods_str})"


class DetectionEngine:
    """Enhanced intelligent detection engine."""
    
    # Profile indicators that suggest a real profile exists
    PROFILE_INDICATORS = [
        r'profile',
        r'avatar',
        r'bio',
        r'followers',
        r'following',
        r'posts?',
        r'username',
        r'user.*name',
        r'@\w+',  # @username mentions
        r'joined',
        r'member since',
    ]
    
    # Error indicators that suggest profile doesn't exist
    ERROR_INDICATORS = [
        r'not found',
        r'doesn\'?t exist',
        r'user.*not.*found',
        r'profile.*not.*found',
        r'404',
        r'page.*not.*found',
        r'does not exist',
        r'no.*such.*user',
        r'invalid.*username',
    ]
    
    @staticmethod
    def detect_enhanced(
        platform: "PlatformDefinition",
        response_status: int,
        response_text: str,
        response_url: str,
        final_url: str,
        response_time: Optional[float] = None
    ) -> DetectionResult:
        """
        Enhanced detection using multiple methods combined.
        
        Args:
            platform: Platform definition
            response_status: HTTP status code
            response_text: Response body text
            response_url: Original request URL
            final_url: Final URL after redirects
            response_time: Response time in seconds
        
        Returns:
            DetectionResult with combined confidence from multiple methods
        """
        results: List[DetectionResult] = []
        
        # Method 1: Status code detection
        status_result = DetectionEngine._detect_by_status_code(platform, response_status)
        if status_result.found is not None:
            status_result.response_time = response_time
            results.append(status_result)
        
        # Method 2: HTML content analysis
        html_result = DetectionEngine._detect_by_message(platform, response_text)
        if html_result.found is not None:
            html_result.response_time = response_time
            results.append(html_result)
        
        # Method 3: Profile-specific element detection (NEW)
        profile_result = DetectionEngine._detect_by_profile_elements(response_text, response_status)
        if profile_result.found is not None:
            profile_result.response_time = response_time
            results.append(profile_result)
        
        # Method 4: Redirect analysis
        redirect_result = DetectionEngine._detect_by_redirect(platform, response_url, final_url)
        if redirect_result.found is not None:
            redirect_result.response_time = response_time
            results.append(redirect_result)
        
        # Method 5: JSON response detection (NEW)
        json_result = DetectionEngine._detect_by_json(response_text, response_status)
        if json_result.found is not None:
            json_result.response_time = response_time
            results.append(json_result)
        
        # Method 6: Response time analysis (NEW)
        if response_time is not None:
            timing_result = DetectionEngine._detect_by_response_time(response_time, response_status)
            if timing_result.found is not None:
                timing_result.response_time = response_time
                results.append(timing_result)
        
        # Combine all results
        if not results:
            # No methods matched - use default
            return DetectionResult(
                found=response_status == 200,
                confidence=0.5,
                method="default",
                details=f"Status {response_status}, no specific detection matched",
                response_time=response_time
            )
        
        # Start with first result
        combined = results[0]
        
        # Combine with other results
        for result in results[1:]:
            combined = combined.combine(result)
        
        return combined
    
    @staticmethod
    def _detect_by_status_code(
        platform: "PlatformDefinition",
        status_code: int
    ) -> DetectionResult:
        """Detect by HTTP status code."""
        if status_code in platform.error_code:
            return DetectionResult(
                found=False,
                confidence=0.9,
                method="status_code",
                details=f"Status {status_code} matches error codes {platform.error_code}",
                methods_used=["status_code"]
            )
        
        if status_code == 200 and platform.error_code:
            return DetectionResult(
                found=True,
                confidence=0.9,
                method="status_code",
                details=f"Status 200 and not in error codes {platform.error_code}",
                methods_used=["status_code"]
            )
        
        if status_code == 200:
            return DetectionResult(
                found=True,
                confidence=0.7,
                method="status_code",
                details="Status 200 (no error codes specified)",
                methods_used=["status_code"]
            )
        
        return DetectionResult(
            found=None,
            confidence=0.0,
            method="status_code",
            details=f"Status {status_code} not handled",
            methods_used=["status_code"]
        )
    
    @staticmethod
    def _detect_by_message(
        platform: "PlatformDefinition",
        response_text: str
    ) -> DetectionResult:
        """Detect by error message in HTML content."""
        if not platform.error_msg:
            return DetectionResult(
                found=None,
                confidence=0.0,
                method="message",
                details="No error messages specified",
                methods_used=["message"]
            )
        
        try:
            soup = BeautifulSoup(response_text, 'lxml')
            page_text = soup.get_text().lower()
        except Exception as e:
            logger.debug(f"Error parsing HTML: {e}")
            page_text = response_text.lower()
        
        for error_msg in platform.error_msg:
            error_lower = error_msg.lower()
            
            if error_lower in page_text:
                return DetectionResult(
                    found=False,
                    confidence=0.95,
                    method="message",
                    details=f"Found error message: '{error_msg}'",
                    methods_used=["message"]
                )
            
            try:
                title = soup.find('title')
                if title and error_lower in title.get_text().lower():
                    return DetectionResult(
                        found=False,
                        confidence=0.95,
                        method="message",
                        details=f"Found error message in title: '{error_msg}'",
                        methods_used=["message"]
                    )
            except Exception:
                pass
        
        return DetectionResult(
            found=True,
            confidence=0.85,
            method="message",
            details="No error messages found in response",
            methods_used=["message"]
        )
    
    @staticmethod
    def _detect_by_profile_elements(
        response_text: str,
        response_status: int
    ) -> DetectionResult:
        """
        Detect by looking for profile-specific elements in HTML.
        NEW: Enhanced content analysis.
        """
        if response_status != 200:
            return DetectionResult(
                found=None,
                confidence=0.0,
                method="profile_elements",
                details="Non-200 status, skipping profile element detection",
                methods_used=["profile_elements"]
            )
        
        try:
            soup = BeautifulSoup(response_text, 'lxml')
            page_text = soup.get_text().lower()
            html_lower = str(soup).lower()
        except Exception:
            page_text = response_text.lower()
            html_lower = response_text.lower()
        
        # Check for error indicators
        error_count = sum(1 for pattern in DetectionEngine.ERROR_INDICATORS if re.search(pattern, page_text, re.IGNORECASE))
        if error_count >= 2:  # Multiple error indicators
            return DetectionResult(
                found=False,
                confidence=0.9,
                method="profile_elements",
                details=f"Found {error_count} error indicators in content",
                methods_used=["profile_elements"]
            )
        
        # Check for profile indicators
        profile_count = sum(1 for pattern in DetectionEngine.PROFILE_INDICATORS if re.search(pattern, html_lower, re.IGNORECASE))
        
        # Check for common profile elements
        has_avatar = bool(soup.find('img', {'class': re.compile(r'avatar|profile|user', re.I)}))
        has_bio = bool(soup.find(string=re.compile(r'bio|about|description', re.I)))
        has_username_display = bool(soup.find(string=re.compile(r'@\w+', re.I)))
        
        if profile_count >= 3 or (has_avatar and has_bio):
            return DetectionResult(
                found=True,
                confidence=0.85,
                method="profile_elements",
                details=f"Found {profile_count} profile indicators, avatar={has_avatar}, bio={has_bio}",
                methods_used=["profile_elements"]
            )
        
        if profile_count >= 1:
            return DetectionResult(
                found=True,
                confidence=0.7,
                method="profile_elements",
                details=f"Found {profile_count} profile indicator(s)",
                methods_used=["profile_elements"]
            )
        
        return DetectionResult(
            found=None,
            confidence=0.0,
            method="profile_elements",
            details="No clear profile indicators found",
            methods_used=["profile_elements"]
        )
    
    @staticmethod
    def _detect_by_redirect(
        platform: "PlatformDefinition",
        response_url: str,
        final_url: str
    ) -> DetectionResult:
        """Detect by redirect URL."""
        if not platform.error_url:
            return DetectionResult(
                found=None,
                confidence=0.0,
                method="response_url",
                details="No error URL specified",
                methods_used=["response_url"]
            )
        
        if platform.error_url in final_url:
            return DetectionResult(
                found=False,
                confidence=0.9,
                method="response_url",
                details=f"Redirected to error URL: {platform.error_url}",
                methods_used=["response_url"]
            )
        
        if response_url != final_url:
            return DetectionResult(
                found=True,
                confidence=0.8,
                method="response_url",
                details=f"Redirected but not to error URL (to: {final_url})",
                methods_used=["response_url"]
            )
        
        return DetectionResult(
            found=None,
            confidence=0.0,
            method="response_url",
            details="No redirect occurred",
            methods_used=["response_url"]
        )
    
    @staticmethod
    def _detect_by_json(
        response_text: str,
        response_status: int
    ) -> DetectionResult:
        """
        Detect by parsing JSON responses.
        NEW: Some platforms return JSON instead of HTML.
        """
        if response_status != 200:
            return DetectionResult(
                found=None,
                confidence=0.0,
                method="json",
                details="Non-200 status, skipping JSON detection",
                methods_used=["json"]
            )
        
        try:
            data = json.loads(response_text)
        except (json.JSONDecodeError, ValueError):
            return DetectionResult(
                found=None,
                confidence=0.0,
                method="json",
                details="Not a JSON response",
                methods_used=["json"]
            )
        
        # Check for error indicators in JSON
        json_str = json.dumps(data).lower()
        
        error_indicators = ['error', 'not found', 'does not exist', 'invalid', '404']
        if any(indicator in json_str for indicator in error_indicators):
            return DetectionResult(
                found=False,
                confidence=0.9,
                method="json",
                details="JSON response contains error indicators",
                methods_used=["json"]
            )
        
        # Check for user/profile data
        profile_keys = ['user', 'profile', 'username', 'name', 'id']
        if any(key in json_str for key in profile_keys):
            return DetectionResult(
                found=True,
                confidence=0.85,
                method="json",
                details="JSON response contains user/profile data",
                methods_used=["json"]
            )
        
        return DetectionResult(
            found=None,
            confidence=0.0,
            method="json",
            details="JSON response but no clear indicators",
            methods_used=["json"]
        )
    
    @staticmethod
    def _detect_by_response_time(
        response_time: float,
        response_status: int
    ) -> DetectionResult:
        """
        Detect by analyzing response time.
        NEW: Fast responses often indicate cached/error pages.
        """
        # Very fast responses (<50ms) might be error pages or cached content
        if response_time < 0.05 and response_status != 200:
            return DetectionResult(
                found=False,
                confidence=0.7,
                method="response_time",
                details=f"Very fast response ({response_time*1000:.0f}ms) with non-200 status",
                methods_used=["response_time"]
            )
        
        # Very slow responses (>2s) might indicate dynamic content loading (profile exists)
        if response_time > 2.0 and response_status == 200:
            return DetectionResult(
                found=True,
                confidence=0.6,
                method="response_time",
                details=f"Slow response ({response_time*1000:.0f}ms) suggests dynamic content",
                methods_used=["response_time"]
            )
        
        return DetectionResult(
            found=None,
            confidence=0.0,
            method="response_time",
            details=f"Response time ({response_time*1000:.0f}ms) not indicative",
            methods_used=["response_time"]
        )
    
    # Backward compatibility - use enhanced detection
    @staticmethod
    def detect(
        platform: "PlatformDefinition",
        response_status: int,
        response_text: str,
        response_url: str,
        final_url: str,
        response_time: Optional[float] = None
    ) -> DetectionResult:
        """Backward compatible detect method using enhanced detection."""
        return DetectionEngine.detect_enhanced(
            platform, response_status, response_text, response_url, final_url, response_time
        )

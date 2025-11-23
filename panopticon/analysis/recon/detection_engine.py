"""
Detection Engine Module

Implements intelligent detection methods for username existence.
Supports multiple detection strategies: status codes, HTML content, redirects.
"""
import logging
import re
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class DetectionResult:
    """Result of a detection attempt."""
    
    def __init__(self, found: bool, confidence: float = 0.0, method: str = "", details: str = ""):
        self.found = found
        self.confidence = confidence  # 0.0 to 1.0
        self.method = method
        self.details = details
    
    def __repr__(self) -> str:
        status = "FOUND" if self.found else "NOT_FOUND"
        return f"DetectionResult({status}, confidence={self.confidence:.2f}, method={self.method})"


class DetectionEngine:
    """Intelligent detection engine for username existence."""
    
    @staticmethod
    def detect(
        platform: "PlatformDefinition",
        response_status: int,
        response_text: str,
        response_url: str,
        final_url: str
    ) -> DetectionResult:
        """
        Detect if username exists using platform-specific logic.
        
        Args:
            platform: Platform definition
            response_status: HTTP status code
            response_text: Response body text
            response_url: Original request URL
            final_url: Final URL after redirects
        
        Returns:
            DetectionResult with found status and confidence
        """
        # Try each detection method in order
        for error_type in platform.error_type:
            if error_type == "status_code":
                result = DetectionEngine._detect_by_status_code(
                    platform, response_status
                )
                if result.found is not None:
                    return result
            
            elif error_type == "message":
                result = DetectionEngine._detect_by_message(
                    platform, response_text
                )
                if result.found is not None:
                    return result
            
            elif error_type == "response_url":
                result = DetectionEngine._detect_by_redirect(
                    platform, response_url, final_url
                )
                if result.found is not None:
                    return result
        
        # Default: if we got 200, assume found (low confidence)
        if response_status == 200:
            return DetectionResult(
                found=True,
                confidence=0.5,
                method="default_200",
                details="Status 200 but no specific detection method matched"
            )
        
        # Default: if we got error code, assume not found
        return DetectionResult(
            found=False,
            confidence=0.5,
            method="default_error",
            details=f"Status {response_status} and no specific detection method matched"
        )
    
    @staticmethod
    def _detect_by_status_code(
        platform: "PlatformDefinition",
        status_code: int
    ) -> DetectionResult:
        """Detect by HTTP status code."""
        # If status code matches error codes, username doesn't exist
        if status_code in platform.error_code:
            return DetectionResult(
                found=False,
                confidence=0.9,
                method="status_code",
                details=f"Status {status_code} matches error codes {platform.error_code}"
            )
        
        # If status is 200 and error_code is specified, username exists
        if status_code == 200 and platform.error_code:
            return DetectionResult(
                found=True,
                confidence=0.9,
                method="status_code",
                details=f"Status 200 and not in error codes {platform.error_code}"
            )
        
        # If status is 200 and no error_code specified, assume found
        if status_code == 200:
            return DetectionResult(
                found=True,
                confidence=0.7,
                method="status_code",
                details="Status 200 (no error codes specified)"
            )
        
        # Unknown status code
        return DetectionResult(
            found=None,
            confidence=0.0,
            method="status_code",
            details=f"Status {status_code} not handled"
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
                details="No error messages specified"
            )
        
        # Parse HTML
        try:
            soup = BeautifulSoup(response_text, 'lxml')
            page_text = soup.get_text().lower()
        except Exception as e:
            logger.debug(f"Error parsing HTML: {e}")
            page_text = response_text.lower()
        
        # Check for error messages
        for error_msg in platform.error_msg:
            error_lower = error_msg.lower()
            
            # Check in page text
            if error_lower in page_text:
                return DetectionResult(
                    found=False,
                    confidence=0.95,
                    method="message",
                    details=f"Found error message: '{error_msg}'"
                )
            
            # Check in HTML title
            try:
                title = soup.find('title')
                if title and error_lower in title.get_text().lower():
                    return DetectionResult(
                        found=False,
                        confidence=0.95,
                        method="message",
                        details=f"Found error message in title: '{error_msg}'"
                    )
            except Exception:
                pass
        
        # If we got here and status is 200, username likely exists
        # (no error messages found)
        return DetectionResult(
            found=True,
            confidence=0.85,
            method="message",
            details="No error messages found in response"
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
                details="No error URL specified"
            )
        
        # Check if final URL matches error URL
        if platform.error_url in final_url:
            return DetectionResult(
                found=False,
                confidence=0.9,
                method="response_url",
                details=f"Redirected to error URL: {platform.error_url}"
            )
        
        # If redirected but not to error URL, username likely exists
        if response_url != final_url:
            return DetectionResult(
                found=True,
                confidence=0.8,
                method="response_url",
                details=f"Redirected but not to error URL (to: {final_url})"
            )
        
        # No redirect
        return DetectionResult(
            found=None,
            confidence=0.0,
            method="response_url",
            details="No redirect occurred"
        )

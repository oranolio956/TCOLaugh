import random
import requests
import logging
from typing import Tuple, Dict, Any, List

logger = logging.getLogger(__name__)

class GeoIP:
    @staticmethod
    def lookup(ip: str) -> Tuple[float, float, str]:
        """
        Performs a real GeoIP lookup using ip-api.com (Free tier).
        Returns (Lat, Lon, Country)
        """
        # Private IP check
        if ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("127."):
             return (0.0, 0.0, "Private Network")

        try:
            # timeout is important to avoid hanging
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    lat = data.get("lat", 0.0)
                    lon = data.get("lon", 0.0)
                    country = data.get("countryCode", "XX")
                    return (lat, lon, country)
        except Exception as e:
            logger.warning(f"GeoIP lookup failed for {ip}: {e}")
            pass
            
        return (0.0, 0.0, "XX")


class BreachAnalyzer:
    @staticmethod
    def assess_password_strength(password_hash: str) -> dict:
        """
        Analyzes the hash to guess complexity/risk.
        """
        # We can't easily check real breaches without an API key (e.g. HIBP), 
        # so we stick to complexity analysis for now.
        risk_score = 0
        notes = []

        if password_hash.startswith("sha1:"):
            risk_score += 80
            notes.append("Legacy SHA1 hash detected (High Risk)")
        elif password_hash.startswith("md5:"):
            risk_score += 90
            notes.append("Broken MD5 hash detected (Critical Risk)")
        else:
            risk_score += 30
            notes.append("Standard hash format")

        return {
            "risk_score": min(risk_score, 100),
            "grade": "F" if risk_score > 70 else "C" if risk_score > 40 else "A",
            "notes": notes,
        }

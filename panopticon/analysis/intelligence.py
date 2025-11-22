import random
from typing import Tuple

class GeoIP:
    @staticmethod
    def lookup(ip: str) -> Tuple[float, float, str]:
        """
        Simulates a MaxMind GeoIP lookup.
        Returns (Lat, Lon, Country)
        """
        # Deterministic mock based on IP octets to stay consistent for the same IP
        try:
            parts = [int(p) for p in ip.split('.')]
            lat = 37.7749 + (parts[3] * 0.01) # Variation around SF
            lon = -122.4194 + (parts[2] * 0.01)
            return (lat, lon, "US")
        except:
            return (0.0, 0.0, "XX")

class BreachAnalyzer:
    @staticmethod
    def assess_password_strength(password_hash: str) -> dict:
        """
        Analyzes the hash to guess complexity/risk.
        """
        # Mock logic
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
            "notes": notes
        }

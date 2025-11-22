import re


class Normalizer:
    @staticmethod
    def normalize_email(email: str) -> str:
        """
        Sanitizes email: lowercases and trims.
        """
        if not email:
            return ""
        return email.strip().lower()

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """
        Converts phone numbers to E.164 format.
        This is a simplified implementation. In production, use python-phonenumbers.
        """
        if not phone:
            return ""

        # Remove all non-digit characters
        digits = re.sub(r"\D", "", phone)

        # Assume US if 10 digits, prefix with +1
        if len(digits) == 10:
            return f"+1{digits}"
        # If 11 digits and starts with 1, prefix with +
        elif len(digits) == 11 and digits.startswith("1"):
            return f"+{digits}"

        # Fallback: return as is with + if it looks like a full intl number
        if len(digits) > 7:
            return f"+{digits}"

        return digits

    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Basic text sanitization.
        """
        if not text:
            return ""
        return text.strip()

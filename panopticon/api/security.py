import logging
import os
import time
import uuid
from typing import Dict, Optional, Set

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from panopticon.persistence.sqlite_manager import db_instance

logger = logging.getLogger(__name__)

PUBLIC_PATHS: Set[str] = {"/", "/docs", "/openapi.json", "/favicon.ico"}


def _require_api_key() -> str:
    """
    Ensure an API key exists before the API starts.
    """
    key = os.environ.get("PANOPTICON_API_KEY")
    if not key:
        raise RuntimeError(
            "PANOPTICON_API_KEY must be set before starting the Panopticon API."
        )
    return key


class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.expected_key = _require_api_key()
        self.rate_limit_window = float(os.environ.get("PANOPTICON_RATE_LIMIT_WINDOW", "60"))
        self.rate_limit_max = int(os.environ.get("PANOPTICON_RATE_LIMIT_MAX", "60"))
        self._rate_counters: Dict[str, Dict[str, float]] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = getattr(request.client, "host", "unknown")
        # 1. Auth Check (API Key from Env)
        if not self._is_public_path(request.url.path):
            api_key = request.headers.get("X-API-Key") or self._extract_bearer_key(
                request.headers.get("Authorization")
            )

            if api_key != self.expected_key:
                logger.warning(
                    "Blocked unauthorized access from %s to %s", client_ip, request.url.path
                )
                return self._unauthorized_response()
            if not self._allow_request(client_ip):
                logger.warning(
                    "Rate limit exceeded for %s on %s", client_ip, request.url.path
                )
                return self._rate_limited_response()

        # 2. Audit Logging
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        if request.method == "POST" and "/search/" in request.url.path:
            self._log_audit(request, response.status_code, process_time)

        return response

    def _is_public_path(self, path: str) -> bool:
        return path in PUBLIC_PATHS or path.startswith("/static")

    def _extract_bearer_key(self, auth_header: Optional[str]) -> Optional[str]:
        if not auth_header or not auth_header.lower().startswith("bearer "):
            return None
        return auth_header.split(" ", 1)[1].strip()

    def _allow_request(self, client_ip: str) -> bool:
        if self.rate_limit_max <= 0 or self.rate_limit_window <= 0:
            return True
        record = self._rate_counters.get(client_ip)
        now = time.time()
        if not record or now > record["reset"]:
            self._rate_counters[client_ip] = {
                "count": 1,
                "reset": now + self.rate_limit_window,
            }
            return True
        if record["count"] >= self.rate_limit_max:
            return False
        record["count"] += 1
        return True

    def _unauthorized_response(self):
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=403,
            content={
                "detail": "Invalid or missing API Key. Provide it via X-API-Key or Bearer token."
            },
        )

    def _rate_limited_response(self):
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=429,
            content={
                "detail": "Too many requests. Slow down and try again shortly."
            },
        )

    def _log_audit(self, request: Request, status_code: int, duration: float):
        """
        Persists the audit log to the SQLite DB.
        """
        client_ip = getattr(request.client, "host", "unknown")
        log_entry = {
            "timestamp": time.time(),
            "ip": client_ip,
            "endpoint": request.url.path,
            "status": status_code,
            "duration": duration,
        }
        doc_id = f"audit_{uuid.uuid4()}"
        try:
            db_instance.add_document(
                doc_id, "audit_log", log_entry["timestamp"], log_entry
            )
            logger.info("AUDIT: %s %s %s", client_ip, request.method, request.url.path)
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

import logging
import os
import time
import uuid
from typing import Optional

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from panopticon.persistence.sqlite_manager import db_instance

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Auth Check (API Key from Env)
        # Allow public assets and root
        if (
            request.url.path in ["/", "/docs", "/openapi.json", "/favicon.ico"]
            or request.url.path.startswith("/static")
        ):
            pass
        else:
            api_key = request.headers.get("X-API-Key")
            expected_key = os.environ.get("PANOPTICON_API_KEY", "panopticon-secret")

            # Strict equality check
            if api_key != expected_key:
                logger.warning(
                    f"Unauthenticated access attempt from {request.client.host} to {request.url.path}"
                )
                # Block access in production, allow mocking if needed but default to secure
                return self._unauthorized_response()

        # 2. Audit Logging
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # Log sensitive actions
        if request.method == "POST" and "/search/" in request.url.path:
            self._log_audit(request, response.status_code, process_time)

        return response

    def _unauthorized_response(self):
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=403, content={"detail": "Invalid or missing API Key"}
        )

    def _log_audit(self, request: Request, status_code: int, duration: float):
        """
        Persists the audit log to the SQLite DB.
        """
        log_entry = {
            "timestamp": time.time(),
            "ip": request.client.host,
            "endpoint": request.url.path,
            "status": status_code,
            "duration": duration,
        }
        # We reuse the document store for audit logs, but with type 'audit_log'
        doc_id = f"audit_{uuid.uuid4()}"
        try:
            db_instance.add_document(
                doc_id, "audit_log", log_entry["timestamp"], log_entry
            )
            logger.info(f"AUDIT: {request.client.host} accessed {request.url.path}")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

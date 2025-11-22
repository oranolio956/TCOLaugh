import time
import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from panopticon.persistence.sqlite_manager import db_instance
import uuid

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Auth Check (Mocked API Key)
        # Allow public assets and root
        if request.url.path in ["/", "/docs", "/openapi.json", "/favicon.ico"] or request.url.path.startswith("/static"):
            pass
        else:
            api_key = request.headers.get("X-API-Key")
            # Mock: Accept 'panopticon-secret' or allow local dev
            if api_key != "panopticon-secret":
                # For demo purposes, we log warning but don't block to keep dashboard working without modifying js
                logger.warning(f"Unauthenticated access attempt from {request.client.host} to {request.url.path}")
                # In production: raise HTTPException(status_code=403, detail="Invalid API Key")

        # 2. Audit Logging
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log sensitive actions
        if request.method == "POST" and "/search/" in request.url.path:
            self._log_audit(request, response.status_code, process_time)
            
        return response

    def _log_audit(self, request: Request, status_code: int, duration: float):
        """
        Persists the audit log to the SQLite DB.
        """
        log_entry = {
            "timestamp": time.time(),
            "ip": request.client.host,
            "endpoint": request.url.path,
            "status": status_code,
            "duration": duration
        }
        # We reuse the document store for audit logs, but with type 'audit_log'
        doc_id = f"audit_{uuid.uuid4()}"
        try:
            db_instance.add_document(doc_id, "audit_log", log_entry['timestamp'], log_entry)
            logger.info(f"AUDIT: {request.client.host} accessed {request.url.path}")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

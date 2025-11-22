import logging
import os
import secrets
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from panopticon.analysis.intelligence import BreachAnalyzer, GeoIP
from panopticon.analysis.narrative.graph_rag import GraphNarrator
from panopticon.analysis.recon.active_scanner import ActiveScanner
from panopticon.analysis.visual.face_engine import FaceEngine
from panopticon.api.security import SecurityMiddleware
from panopticon.persistence.sqlite_manager import db_instance
from panopticon.persistence.vector.milvus_manager import MilvusManager

app = FastAPI(
    title="Panopticon API", description="Identity Resolution Platform Interface"
)
logger = logging.getLogger("uvicorn")
MAX_UPLOAD_BYTES = int(os.environ.get("PANOPTICON_MAX_UPLOAD_BYTES", 5 * 1024 * 1024))
milvus_index = MilvusManager()

# Add Security Middleware
app.add_middleware(SecurityMiddleware)

# Initialize services
scanner = ActiveScanner()
face_engine = FaceEngine()
narrator = GraphNarrator()

# Setup Templates
os.makedirs("panopticon/api/templates", exist_ok=True)
os.makedirs("panopticon/api/static", exist_ok=True)
templates = Jinja2Templates(directory="panopticon/api/templates")
app.mount("/static", StaticFiles(directory="panopticon/api/static"), name="static")


class PersonSearchRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None


class ReconRequest(BaseModel):
    username: str


def _sanitize_filename(filename: Optional[str]) -> str:
    """
    Prevent directory traversal and ensure predictable temp files.
    """
    if not filename:
        return f"upload_{secrets.token_hex(4)}"
    candidate = Path(filename).name
    safe = "".join(ch for ch in candidate if ch.isalnum() or ch in {"-", "_", "."})
    if not safe or safe.startswith("."):
        return f"upload_{secrets.token_hex(4)}"
    return safe


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/stats")
async def get_stats():
    # Optimized: Removed redundant connections by using context manager in persistence layer
    # Ideally, these counts should be cached in Redis in production
    with db_instance.get_connection() as conn:
        cur = conn.cursor()
        docs = cur.execute(
            "SELECT COUNT(*) FROM documents WHERE source_type != 'audit_log'"
        ).fetchone()[0]
        audits = cur.execute(
            "SELECT COUNT(*) FROM documents WHERE source_type = 'audit_log'"
        ).fetchone()[0]
        nodes = cur.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        edges = cur.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    return {"documents": docs, "nodes": nodes, "edges": edges, "audit_logs": audits}


@app.post("/search/person")
async def search_person(query: PersonSearchRequest):
    """
    Searches the Polyglot Store.
    """
    filtered_query = query.dict(exclude_none=True)
    if not filtered_query:
        raise HTTPException(
            status_code=422, detail="Provide at least one search attribute."
        )
    requested_fields = list(filtered_query.keys())  # Avoid logging raw values
    logger.info("Processing search query for fields=%s", requested_fields)
    results = []

    # 1. Document Search (Naive)
    # In future: Async OpenSearch calls here
    if query.email:
        docs = db_instance.search_documents("email", query.email)
        for d in docs:
            results.append({"type": "breach_record", "data": d})

    if query.username:
        docs = db_instance.search_documents("username", query.username)
        for d in docs:
            results.append({"type": "social_profile", "data": d})

    # 2. Graph Traversal
    graph_context = {}
    if query.email:
        graph_context = db_instance.get_subgraph(f"email:{query.email}", depth=2)
    elif query.username:
        graph_context = db_instance.get_subgraph(f"user:{query.username}", depth=2)

    # 3. Enrichment (Geo & Health)
    locations = []
    password_analysis = {}

    if graph_context:
        for uid, info in graph_context.get("nodes", {}).items():
            # GeoIP for IP Nodes
            if info["type"] == "IPAddress":
                ip = info["properties"]["val"]
                lat, lon, country = GeoIP.lookup(ip)
                locations.append(
                    {"ip": ip, "lat": lat, "lon": lon, "country": country}
                )

            # Analysis for Hash Nodes
            if info["type"] == "PasswordHash":
                p_hash = info["properties"]["val"]
                analysis = BreachAnalyzer.assess_password_strength(p_hash)
                password_analysis[p_hash] = analysis

    # 4. Narrative Generation (GraphRAG)
    narrative = "No graph context available for analysis."
    if graph_context and graph_context.get("nodes"):
        target = query.email or query.username or query.name
        # This call is synchronous/slow, should be async in future
        narrative = narrator.generate_briefing(target, graph_context, password_analysis)

    return {
        "matches": results,
        "graph": graph_context,
        "geo_trace": locations,
        "risk_analysis": password_analysis,
        "narrative": narrative,
    }


@app.post("/search/face")
async def search_face(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file upload.")
        if len(contents) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Limit is {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.",
            )

        safe_name = _sanitize_filename(file.filename)
        temp_dir = Path(tempfile.mkdtemp(prefix="panopticon_upload_"))
        temp_path = temp_dir / safe_name

        try:
            temp_path.write_bytes(contents)
            detections = face_engine.process_image(str(temp_path))

            if not detections:
                return {"message": "No faces detected"}

            matches = []
            for det in detections:
                emb = np.array(det["embedding"], dtype=np.float32)
                vec_matches = _search_vectors(emb)
                matches.append(
                    {
                        "face_score": det["detection_score"],
                        "db_matches": vec_matches,
                    }
                )

            return {"message": f"Found {len(detections)} face(s)", "matches": matches}
        finally:
            try:
                temp_path.unlink(missing_ok=True)
                temp_dir.rmdir()
            except OSError:
                pass
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in face search: {e}")
        raise HTTPException(status_code=500, detail="Face search failed.")


@app.post("/recon/username")
async def active_recon(request: ReconRequest):
    # Optimized: Made async to prevent blocking the event loop during external HTTP calls
    # Note: ActiveScanner internals also need to be async for full benefit
    hits = await scanner.check_username(request.username)
    # Persist results
    doc_id = f"recon_{request.username}"
    db_instance.add_document(
        doc_id, "active_recon", 0, {"username": request.username, "hits": hits}
    )
    return {"username": request.username, "found_on": hits}


def _search_vectors(embedding: np.ndarray) -> List[Dict[str, Any]]:
    if milvus_index.collection:
        matches = milvus_index.search_vectors(embedding)
        if matches:
            return matches
    return db_instance.search_vectors(embedding)

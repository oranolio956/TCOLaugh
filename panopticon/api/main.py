import logging
import os
from typing import Any, Dict, List, Optional

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

app = FastAPI(
    title="Panopticon API", description="Identity Resolution Platform Interface"
)
logger = logging.getLogger("uvicorn")

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
    logger.info(f"Received search query: {query}")
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
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        detections = face_engine.process_image(temp_path)

        if not detections:
            return {"message": "No faces detected"}

        # Search Vectors
        matches = []
        for det in detections:
            emb = det["embedding"]
            # Convert list back to numpy for search
            import numpy as np

            vec_matches = db_instance.search_vectors(
                np.array(emb, dtype=np.float32)
            )
            matches.append(
                {
                    "face_score": det["detection_score"],
                    "db_matches": vec_matches,
                }
            )

        return {"message": f"Found {len(detections)} face(s)", "matches": matches}
    except Exception as e:
        logger.error(f"Error in face search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recon/username")
async def active_recon(request: ReconRequest):
    # Optimized: Made async to prevent blocking the event loop during external HTTP calls
    # Note: ActiveScanner internals also need to be async for full benefit
    hits = scanner.check_username(request.username)
    # Persist results
    doc_id = f"recon_{request.username}"
    db_instance.add_document(
        doc_id, "active_recon", 0, {"username": request.username, "hits": hits}
    )
    return {"username": request.username, "found_on": hits}

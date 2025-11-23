import logging
import os
import secrets
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from panopticon.analysis.intelligence import BreachAnalyzer, GeoIP
from panopticon.analysis.narrative.graph_rag import GraphNarrator
from panopticon.analysis.recon.active_scanner import ActiveScanner
from panopticon.analysis.recon.web_search import WebSearch
from panopticon.analysis.visual.face_engine import FaceEngine
from panopticon.analysis.identity.linker import IdentityLinker
from panopticon.ingestion.stealer_logs import StealerLogParser
from panopticon.api.security import SecurityMiddleware
from panopticon.ingestion.kafka_interface import persist_record as persist_ingestion_record
from panopticon.persistence.sqlite_manager import db_instance
from panopticon.persistence.vector.router import vector_router

app = FastAPI(
    title="Panopticon API", description="Identity Resolution Platform Interface"
)
logger = logging.getLogger("uvicorn")
MAX_UPLOAD_BYTES = int(os.environ.get("PANOPTICON_MAX_UPLOAD_BYTES", 5 * 1024 * 1024))
MAX_SEARCH_RESULTS = int(os.environ.get("PANOPTICON_MAX_SEARCH_RESULTS", "100"))
# milvus_index = MilvusManager() # Deprecated, use router
DASHBOARD_DEFAULT_BASE_URL = os.environ.get("PANOPTICON_DASHBOARD_BASE_URL")
DASHBOARD_DEFAULT_API_KEY = os.environ.get("PANOPTICON_DASHBOARD_API_KEY")
DEFAULT_CORS_ORIGINS = [
    "https://panopticon-dashboard.vercel.app",
    "https://tco-laugh.vercel.app",
    "https://tcolaugh.vercel.app",
]
CORS_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("PANOPTICON_CORS_ORIGINS", "").split(",")
    if origin.strip()
] or DEFAULT_CORS_ORIGINS
# Always make sure known frontends are included
CORS_ORIGINS = sorted(set(CORS_ORIGINS + DEFAULT_CORS_ORIGINS))
CORS_REGEX = os.environ.get("PANOPTICON_CORS_ORIGIN_REGEX")
CORS_ALLOW_CREDENTIALS = bool(CORS_ORIGINS or CORS_REGEX)

# Add middleware (order matters)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS or ["*"],
    allow_origin_regex=CORS_REGEX,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityMiddleware)

# Initialize services
scanner = ActiveScanner()
web_searcher = WebSearch()
face_engine = FaceEngine()
narrator = GraphNarrator()
linker = IdentityLinker()
stealer_parser = StealerLogParser()

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
    include_public_search: bool = False


class ReconRequest(BaseModel):
    username: str


class IngestRecord(BaseModel):
    source_type: str
    raw_data: Dict[str, Any]
    timestamp: float = 0.0
    dataset: Optional[str] = None
    url: Optional[str] = None


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


def _safe_document_search(field: str, value: str) -> List[Dict[str, Any]]:
    try:
        return db_instance.search_documents(field, value)
    except ValueError as exc:
        logger.warning("Document search rejected for %s: %s", field, exc)
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "dashboard_base_url": DASHBOARD_DEFAULT_BASE_URL,
            "dashboard_api_key": DASHBOARD_DEFAULT_API_KEY,
        },
    )


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
    results: List[Dict[str, Any]] = []
    truncated = False

    # 0. Entity Resolution (Experimental)
    # If multiple attributes are provided, try to find if they belong to a known cluster
    # This is a simplification; normally we would run this on the result set
    
    def _add_matches(records: List[Dict[str, Any]], label: str):
        nonlocal truncated
        if not records:
            return
        remaining = max(MAX_SEARCH_RESULTS - len(results), 0)
        if remaining == 0:
            truncated = True
            return
        slice_records = records[:remaining]
        for record in slice_records:
            results.append({"type": label, "data": record})
        if len(slice_records) < len(records):
            truncated = True

    # 1. Document Search (Naive)
    # In future: Async OpenSearch calls here
    raw_matches = []
    if query.email:
        raw_matches.extend(_safe_document_search("email", query.email))
    if query.username:
        raw_matches.extend(_safe_document_search("username", query.username))
        
    # Run Linker on raw matches to find clusters
    # This step tries to merge duplicate identities found in the search results
    if raw_matches:
        linked_records = linker.resolve_entities(raw_matches)
        # We might update the graph here with new clusters
        # linker.sync_to_graph(linked_records)
        
        # Add to results
        _add_matches(linked_records, "linked_identity")
    else:
        # Fallback if no local matches, just use whatever we found
        pass

    # 1.5 Legacy/Direct Search (if linker didn't handle it all)
    if query.email:
        docs = _safe_document_search("email", query.email)
        # Add explanation to raw docs
        for d in docs:
            d["match_type"] = "exact"
            d["match_confidence"] = 1.0
            d["resolution_engine"] = "Exact Lookup"
        _add_matches(docs, "breach_record")

    if query.username:
        docs = _safe_document_search("username", query.username)
        for d in docs:
            d["match_type"] = "exact"
            d["match_confidence"] = 1.0
            d["resolution_engine"] = "Exact Lookup"
        _add_matches(docs, "social_profile")

    # 2. Graph Traversal
    graph_context = {}
    if query.email:
        graph_context = db_instance.get_subgraph(f"email:{query.email}", depth=3) # Increased depth for pivot
    elif query.username:
        graph_context = db_instance.get_subgraph(f"user:{query.username}", depth=3)

    # 2.5 Public Web Search (Real-time)
    public_results = []
    if query.include_public_search:
        target = query.name or query.email or query.username
        if target:
            logger.info(f"Performing public web search for {target}")
            public_results = web_searcher.search_public(target, num_results=5)
            # Add to results as "public_web"
            for url in public_results:
                results.append({
                    "type": "public_web", 
                    "data": {"url": url, "query": target},
                    "match_explanation": f"Matched public web search query: '{target}'"
                })

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
        "truncated": truncated,
    }


@app.post("/ingest/stealer_logs")
async def ingest_stealer_logs(file: UploadFile = File(...)):
    """
    Ingests a ZIP file containing 'system_info.txt' and 'passwords.txt'.
    Offloads processing to a background task.
    """
    import zipfile
    import shutil
    
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file.")
            
        safe_name = _sanitize_filename(file.filename)
        # We need a persistent temp location shared with workers if they are separate processes
        # For this setup (local), /tmp is fine.
        temp_dir = Path("/tmp/panopticon_ingest")
        temp_dir.mkdir(exist_ok=True)
        
        task_id = secrets.token_hex(8)
        job_dir = temp_dir / task_id
        job_dir.mkdir()
        
        zip_path = job_dir / safe_name
        zip_path.write_bytes(contents)
        
        # Trigger Background Task
        # In a real cluster, we'd pass the S3 URL. Here we pass the local path.
        from panopticon.worker import process_stealer_task
        process_stealer_task.delay(str(zip_path), str(job_dir))
            
        return {"status": "accepted", "task_id": task_id, "message": "Processing started in background."}
            
    except Exception as e:
        logger.error(f"Stealer ingestion queue failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search/pivot")
async def search_pivot(type: str, value: str):
    """
    Advanced Pivot Search.
    type: 'hash', 'ip', 'machine'
    value: the identifier
    """
    if type not in ["hash", "ip", "machine"]:
        raise HTTPException(status_code=400, detail="Invalid pivot type.")
        
    start_uid = ""
    if type == "hash":
        start_uid = f"hash:{value}"
    elif type == "ip":
        start_uid = f"ip:{value}"
    elif type == "machine":
        start_uid = f"machine:{value}"
        
    graph = db_instance.get_subgraph(start_uid, depth=2)
    
    # Extract connected identities
    identities = []
    if graph and graph.get("nodes"):
        for uid, info in graph["nodes"].items():
            if info["type"] in ["Identity", "Email"]:
                identities.append(info)
                
    return {
        "pivot_source": start_uid,
        "connected_identities": identities,
        "full_graph": graph
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
    
    # Update Graph
    if hits:
        user_uid = f"user:{request.username}"
        db_instance.add_node(user_uid, "Identity", {"username": request.username, "source": "recon"})
        
        for hit in hits:
            site_name = hit.get("site", "Unknown")
            site_url = hit.get("url", "")
            
            site_uid = f"site:{site_name}"
            db_instance.add_node(site_uid, "Site", {"name": site_name})
            
            db_instance.add_edge(user_uid, site_uid, "HAS_ACCOUNT", {"url": site_url})

    return {"username": request.username, "found_on": hits}


@app.post("/ingest/record")
async def ingest_record(record: IngestRecord):
    """
    Accepts ingestion events from trusted services (crawler, workers) and persists them.
    """
    persist_ingestion_record(record.dict())
    return {"status": "accepted"}


def _search_vectors(embedding: np.ndarray) -> List[Dict[str, Any]]:
    return vector_router.search_vectors(embedding)

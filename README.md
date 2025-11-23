# Panopticon: Web-Scale Identity Resolution Platform

## Overview
Panopticon is a Multi-Modal Identity Resolution (MMIR) system designed to synthesize digital footprints into coherent "Golden Records". It fuses visual data (facial recognition), textual intelligence (OSINT, breach data), and behavioral signals to create a comprehensive identity graph.

> **New:** The API now enforces API-key authentication everywhere except the public landing page. The web dashboard (served from Vercel or any static host) no longer ships a baked-in secret—you must supply the key via the Connection panel before making requests.

## Architecture

### 1. Ingestion Layer
*   **Surface Web**: Distributed crawlers for social media and public registries.
*   **Deep Web**: Ingestion of breach data, stealer logs, and dark web feeds.
*   **Persistence**: Simulated Polyglot Store (SQLite) handling Documents, Graph (Nodes/Edges), and Vectors.

### 2. Enrichment & Analysis
*   **Visual Intelligence**: Face detection (MediaPipe) and embedding (InsightFace/ArcFace - Mocked).
*   **Breach Analytics**: Password hygiene grading and hash analysis.
*   **Geospatial**: IP-to-Location mapping.

### 3. Interface
*   **API**: FastAPI-based REST interface.
*   **Dashboard**: Real-time stats, Identity Graph visualization (Vis.js), and Geo-tracing (Leaflet).

## Setup & Usage
### Prerequisites
* Python **3.9+**
* A valid **`PANOPTICON_API_KEY`** (set in your shell or Render dashboard)
* Optional: Docker + Render CLI for deployment

### Local Quick Start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
export PANOPTICON_API_KEY=dev-panopticon  # or any secret you prefer
./start_panopticon.sh
```
* API: `http://localhost:8000`
* Docs: `http://localhost:8000/docs`
* Dashboard: served by the API root (or deploy `panopticon/api/templates/index.html` to Vercel for static hosting).

### Testing
```bash
PYTHONPATH=$(pwd) pytest tests/
```
This runs the FastAPI security suite plus the ingestion/recon coverage (`tests/test_ingestion_and_recon.py`).

### Scenario Testing
Run the "Cipher Network" simulation (ensures ingestion->graph pipeline is wired):
```bash
python3 panopticon/scenario_test.py
```

## Deployment (Vercel + Render)
* **Render (API/Workers):** Use `render.yaml`. Render will build `requirements.txt`, fetch the spaCy model, and generate a unique `PANOPTICON_API_KEY`. Set `PANOPTICON_ENABLE_AI_BRIEFING=true` only if you supply a valid `ANTHROPIC_API_KEY`.
* **Vercel (Dashboard):** Deploy `panopticon/api/templates/index.html` as a static site (see `vercel.json`). At runtime, enter the Render base URL and API key via the Connection Settings card. Nothing sensitive is baked into the frontend bundle.
* Need a turnkey walkthrough? See `DEPLOYMENT.md` for Render CLI commands, managed Neo4j/Milvus/Kafka notes, and operational checklists.

## Configuration Flags
| Variable | Default | Purpose |
| --- | --- | --- |
| `PANOPTICON_API_KEY` | _none_ (required) | Required header (`X-API-Key`) for every non-static route |
| `PANOPTICON_API_BASE_URL` | `http://localhost:8000` | Target URL for internal services (crawler) when hitting the API |
| `PANOPTICON_ENABLE_AI_BRIEFING` | `false` | Opt-in switch before any graph data is sent to Anthropic |
| `PANOPTICON_MAX_UPLOAD_BYTES` | `5MB` | Upload limit for `/search/face` |
| `PANOPTICON_MAX_SEARCH_RESULTS` | `100` | Upper bound for `/search/person` document matches |
| `PANOPTICON_RATE_LIMIT_WINDOW` | `60` | Rate-limit window (seconds) enforced by the API middleware |
| `PANOPTICON_RATE_LIMIT_MAX` | `60` | Max authenticated requests per IP per window |
| `PANOPTICON_DB_PATH` | `./panopticon.db` | Location of the SQLite polyglot store (point to Render disk) |
| `PANOPTICON_DOCUMENT_TTL_SECONDS` | `0` (disabled) | Automatically purge non-audit documents older than the TTL |
| `PANOPTICON_INDEX_FIELDS` | `email,username,phone,ip_address` | CSV of document keys that should be indexed for fast lookup |
| `PANOPTICON_USE_KAFKA` | `false` | When `true`, ingestion pushes to Kafka instead of SQLite fallback |
| `PANOPTICON_RECON_TIMEOUT` | `6` | Timeout (seconds) for concurrent username reconnaissance calls |
| `PANOPTICON_AI_GRAPH_LIMIT` | `40` | Max number of nodes/edges summarized before sending to the LLM |
| `NEO4J_URI` / `NEO4J_USER` / `NEO4J_PASSWORD` | `bolt://localhost:7687`, `neo4j`, `panopticon_secret` | Point workers at a managed Neo4j instance |
| `MILVUS_HOST` / `MILVUS_PORT` | `localhost`, `19530` | Milvus vector DB endpoint; falls back to SQLite vectors if unset |

> Optional: The probabilistic identity linker depends on Splink. Install it with `pip install splink` before invoking `panopticon.analysis.identity.IdentityLinker`.

## Security Hardening Highlights
* API key enforcement on `/stats`, `/search/*`, `/recon/*`
* Frontend no longer leaks credentials; users provide keys explicitly
* Audit logs capture metadata only (no payload dumps)
* Face-upload endpoint sanitizes filenames, enforces size limits, and scrubs temp files
* Document store now indexes sensitive identifiers, purges stale data, and keeps WAL mode enabled for crash safety
* Vector similarity search is cached in-memory for low latency and can fall back to Milvus if available
* Username reconnaissance runs concurrently over HTTP/2 via `httpx` instead of blocking the FastAPI event loop
* Kafka ingestion is feature-flagged—enable it in production to stream raw records while retaining SQLite fallback
* External graph/vector services (Neo4j, Milvus) are fully controlled via environment variables, making managed deployments straightforward

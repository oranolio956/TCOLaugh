# Deployment Guide

This repository ships two deployment targets:

* **Render** – hosts the FastAPI web service, Celery worker, crawler, Redis, and persistent disk.
* **Vercel (or any static host)** – serves the dashboard UI from `panopticon/api/templates/index.html`.

Follow the steps below to reproduce the full environment using your own credentials.

---

## 1. Prerequisites

* Python 3.9+ with `pipx` or `pip`
* Docker Compose v2 (for local parity testing)
* Render account + API key (see below)
* Vercel account (optional if you plan to host the dashboard elsewhere)

---

## 2. Local Parity Stack

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```
2. Launch the docker-compose stack (API, worker, Kafka, Neo4j, Milvus, Redis):
   ```bash
   cd panopticon/infrastructure
   docker compose up --build
   ```
   The API is available at http://localhost:8000 once you export `PANOPTICON_API_KEY` (for local testing you can set it to `dev-panopticon`).

---

## 3. Render Deployment

### 3.1 Install & Authenticate CLI

```bash
curl -fsSL https://render.com/static/cli/install.sh | bash
export RENDER_API_KEY=<your_render_api_key>
render login --api-key "$RENDER_API_KEY"
```

### 3.2 Create Services

Render understands `render.yaml` directly:

```bash
render blueprint launch --from-file render.yaml
```

During the launch:

* Provide `ANTHROPIC_API_KEY` only if you want GraphRAG enabled.
* Render auto-generates `PANOPTICON_API_KEY`; copy it for the dashboard.
* Point `NEO4J_URI`, `MILVUS_HOST`, etc. to managed deployments if you are not using local Docker services.

To update an existing deployment:

```bash
render blueprint sync --from-file render.yaml
```

### 3.3 Managed Services Checklist

| Service | Option | Notes |
| --- | --- | --- |
| Neo4j | AuraDB or self-hosted | Set `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` |
| Milvus | Zilliz Cloud or Docker service | Set `MILVUS_HOST`, `MILVUS_PORT` |
| Kafka | Confluent Cloud / Aiven | Set `PANOPTICON_USE_KAFKA=true` and configure the crawler with the remote bootstrap servers |
| Redis | Render managed | Provided via `render.yaml` |

---

## 4. Vercel Dashboard

1. Install the Vercel CLI (`npm i -g vercel`).
2. Deploy the static dashboard:
   ```bash
   vercel --cwd panopticon/api/templates
   ```
3. After the deployment, open the dashboard URL, enter the Render API base URL and `PANOPTICON_API_KEY` in the Connection Settings panel.

---

## 5. Operations Checklist

* **Secrets** – rotate `PANOPTICON_API_KEY`, `NEO4J_PASSWORD`, `ANTHROPIC_API_KEY`, etc. in Render’s dashboard; redeploy to propagate.
* **Celery** – monitor `worker.log` (Render logs tab or `render logs panopticon-worker`) for ingestion errors.
* **Data retention** – adjust `PANOPTICON_DOCUMENT_TTL_SECONDS` to control how long non-audit documents stay in SQLite.
* **Scaling** – increase Render plan tiers or add horizontal scaling once CPU usage grows; the worker and crawler can be scaled independently.
* **Backups** – Render disks are not automatically backed up; snapshot `panopticon.db` (or migrate to a managed DB) if you need durability beyond the built-in disk redundancy.

---

Need help automating the CLI steps or wiring up managed databases? Let me know which provider you chose and I can provide concrete commands.*** End Patch

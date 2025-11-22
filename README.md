# Panopticon: Web-Scale Identity Resolution Platform

## Overview
Panopticon is a Multi-Modal Identity Resolution (MMIR) system designed to synthesize digital footprints into coherent "Golden Records". It fuses visual data (facial recognition), textual intelligence (OSINT, breach data), and behavioral signals to create a comprehensive identity graph.

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
*   Python 3.9+
*   Docker (Optional)

### Quick Start
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Launch the system:
    ```bash
    ./start_panopticon.sh
    ```
3.  Access Dashboard: `http://localhost:8000`

### Testing
Run the test suite:
```bash
pytest tests/
```

### Scenario Testing
Run the "Cipher Network" simulation:
```bash
python3 panopticon/scenario_test.py
```

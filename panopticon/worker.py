import logging
import threading
from typing import Any, Dict

from celery import Celery

# Configure Celery
# Broker: Redis
# Backend: Redis
app = Celery(
    "panopticon", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0"
)

# Optional: Configure for durability
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,  # Ensure task is not lost if worker crashes
)

logger = logging.getLogger(__name__)

_neo4j_lock = threading.Lock()
_neo4j_singleton = None
_visual_lock = threading.Lock()
_visual_bundle = {}


def _get_neo4j():
    global _neo4j_singleton
    with _neo4j_lock:
        if _neo4j_singleton is None:
            from panopticon.persistence.graph.neo4j_manager import Neo4jManager

            _neo4j_singleton = Neo4jManager()
    return _neo4j_singleton


def _get_visual_resources():
    global _visual_bundle
    with _visual_lock:
        if not _visual_bundle:
            import numpy as np

            from panopticon.analysis.intel_extractor import IntelExtractor
            from panopticon.analysis.visual.face_engine import FaceEngine
            from panopticon.persistence.vector.router import vector_router

            _visual_bundle = {
                "np": np,
                "extractor": IntelExtractor(),
                "face_engine": FaceEngine(),
                "router": vector_router,
            }
    return _visual_bundle


@app.task
def process_ingestion_task(record: Dict[str, Any]):
    """
    Background task to process a raw record:
    1. Normalization
    2. Entity Extraction
    3. Graph Persistence (Neo4j)
    """
    logger.info(f"Processing task for source: {record.get('source_type')}")
    neo4j = _get_neo4j()
    if not neo4j or not getattr(neo4j, "driver", None):
        logger.error("Neo4j unavailable. Skipping ingestion task.")
        return

    try:
        source_type = record.get("source_type")
        raw = record.get("raw_data", {})

        if source_type == "surface_web":
            username = raw.get("username")
            if username:
                uid = f"user:{username}"
                neo4j.add_node(
                    uid, "Identity", {"username": username, "platform": "social"}
                )

        elif source_type == "deep_web":
            email = raw.get("email")
            if email:
                uid = f"email:{email}"
                neo4j.add_node(uid, "Email", {"address": email})

    except Exception as e:
        logger.error(f"Task failed: {e}")


@app.task
def process_stealer_task(zip_path: str, job_dir: str):
    """
    Background task to unzip and parse stealer logs.
    """
    import zipfile
    import shutil
    import os
    from pathlib import Path
    from panopticon.ingestion.stealer_logs import StealerLogParser
    
    logger.info(f"Processing Stealer Task: {zip_path}")
    parser = StealerLogParser()
    
    try:
        extracted_path = Path(job_dir) / "extracted"
        extracted_path.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_path)
            
        # Find directory
        log_dir = extracted_path
        for root, dirs, files in os.walk(extracted_path):
            if "system_info.txt" in files or "passwords.txt" in files:
                log_dir = Path(root)
                break
                
        result = parser.process_log_directory(str(log_dir))
        logger.info(f"Stealer Task Completed: Ingested {result['credential_count']} credentials.")
        
    except Exception as e:
        logger.error(f"Stealer Task Failed: {e}")
    finally:
        # Cleanup
        try:
            shutil.rmtree(job_dir)
        except:
            pass

@app.task
def process_visual_task(image_path: str):
    """
    Background task for heavy visual processing (Face Rec + OCR).
    """
    resources = _get_visual_resources()
    np = resources["np"]
    extractor = resources["extractor"]
    face_engine = resources["face_engine"]
    router = resources["router"]

    logger.info(f"Processing visual task: {image_path}")

    try:
        text = extractor.extract_text_from_image(image_path)
        logger.info(f"Extracted Text: {text[:50]}...")

        results = face_engine.process_image(image_path)
        for res in results:
            vector = np.array(res["embedding"], dtype=np.float32)
            router.add_vector(vector, f"img_{image_path}", {"ocr_text": text})

    except Exception as e:
        logger.error(f"Visual task failed: {e}")

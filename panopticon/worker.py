from celery import Celery
from typing import Dict, Any
import logging

# Configure Celery
# Broker: Redis
# Backend: Redis
app = Celery('panopticon', 
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0')

# Optional: Configure for durability
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_acks_late=True, # Ensure task is not lost if worker crashes
)

logger = logging.getLogger(__name__)

@app.task
def process_ingestion_task(record: Dict[str, Any]):
    """
    Background task to process a raw record:
    1. Normalization
    2. Entity Extraction
    3. Graph Persistence (Neo4j)
    """
    logger.info(f"Processing task for source: {record.get('source_type')}")
    
    # Lazy import to avoid circular dependencies at startup
    from panopticon.persistence.graph.neo4j_manager import Neo4jManager
    
    # Initialize DB connection inside the worker process
    # In prod, use a connection pool or singleton properly scoped
    neo4j = Neo4jManager()
    
    try:
        source_type = record.get('source_type')
        raw = record.get('raw_data', {})
        
        if source_type == 'surface_web':
            username = raw.get('username')
            if username:
                uid = f"user:{username}"
                neo4j.add_node(uid, "Identity", {"username": username, "platform": "social"})
        
        elif source_type == 'deep_web':
            email = raw.get('email')
            if email:
                uid = f"email:{email}"
                neo4j.add_node(uid, "Email", {"address": email})
                
    except Exception as e:
        logger.error(f"Task failed: {e}")
    finally:
        neo4j.close()

@app.task
def process_visual_task(image_path: str):
    """
    Background task for heavy visual processing (Face Rec + OCR).
    """
    from panopticon.analysis.intel_extractor import IntelExtractor
    from panopticon.persistence.vector.milvus_manager import MilvusManager
    from panopticon.analysis.visual.face_engine import FaceEngine
    import numpy as np
    
    logger.info(f"Processing visual task: {image_path}")
    
    extractor = IntelExtractor()
    face_engine = FaceEngine()
    milvus = MilvusManager()
    
    try:
        # 1. OCR
        text = extractor.extract_text_from_image(image_path)
        logger.info(f"Extracted Text: {text[:50]}...")
        
        # 2. Face Recognition
        results = face_engine.process_image(image_path)
        for res in results:
            vector = np.array(res['embedding'], dtype=np.float32)
            milvus.add_vector(vector, f"img_{image_path}", {"ocr_text": text})
            
    except Exception as e:
        logger.error(f"Visual task failed: {e}")

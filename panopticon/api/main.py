from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
import logging

from panopticon.analysis.recon.active_scanner import ActiveScanner
from panopticon.analysis.visual.face_engine import FaceEngine
# from panopticon.persistence.graph.neo4j_client import GraphManager 
# (GraphManager import commented out to avoid dependency failure if Neo4j not running)

app = FastAPI(title="Panopticon API", description="Identity Resolution Platform Interface")
logger = logging.getLogger("uvicorn")

# Initialize services
scanner = ActiveScanner()
face_engine = FaceEngine()
# graph_manager = GraphManager(...) 

class PersonSearchRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None

class ReconRequest(BaseModel):
    username: str

@app.get("/")
def read_root():
    return {"status": "online", "system": "Panopticon Identity Platform"}

@app.post("/search/person")
def search_person(query: PersonSearchRequest):
    """
    Searches for a person based on bio-data.
    """
    logger.info(f"Received search query: {query}")
    # 1. Query OpenSearch/Neo4j (Mocked)
    results = [
        {
            "uid": "12345",
            "name": "John Doe", 
            "confidence": 0.95, 
            "sources": ["linkedin", "breach_collection_1"]
        }
    ]
    return {"results": results}

@app.post("/search/face")
async def search_face(file: UploadFile = File(...)):
    """
    Uploads an image to search against the face index.
    """
    try:
        # Save temp file
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process image
        detections = face_engine.process_image(temp_path)
        
        if not detections:
            return {"message": "No faces detected"}
        
        # In a real app, we would now query the Vector DB with the embedding
        # results = vector_index.search(detections[0]['embedding'])
        
        return {
            "message": f"Found {len(detections)} face(s)",
            "first_face_embedding_sample": detections[0]['embedding'][:5],
            "matches": [] # Mock empty matches
        }
    except Exception as e:
        logger.error(f"Error in face search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recon/username")
def active_recon(request: ReconRequest):
    """
    Triggers real-time username reconnaissance.
    """
    hits = scanner.check_username(request.username)
    return {"username": request.username, "found_on": hits}

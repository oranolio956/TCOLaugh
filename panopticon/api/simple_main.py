"""
Simplified API for testing Render deployment
"""

import os
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse
from typing import Optional

app = FastAPI(title="Panopticon API", description="Simplified version for deployment testing")

# Get API key from environment
EXPECTED_API_KEY = os.environ.get("PANOPTICON_API_KEY", "dev-panopticon")

@app.get("/")
async def root():
    """Public health check endpoint"""
    return {"status": "ok", "service": "panopticon-api"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "panopticon-api"}

@app.get("/stats")
async def get_stats(x_api_key: Optional[str] = Header(None)):
    """Get basic stats - requires API key"""
    if x_api_key != EXPECTED_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return {
        "documents": 0,
        "nodes": 0,
        "edges": 0,
        "status": "simplified-api",
        "message": "This is a simplified version for testing"
    }

@app.get("/test")
async def test(x_api_key: Optional[str] = Header(None)):
    """Test endpoint with API key"""
    if x_api_key != EXPECTED_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return {
        "message": "API is working!",
        "environment": {
            "db_path": os.environ.get("PANOPTICON_DB_PATH", "not-set"),
            "redis_url": os.environ.get("REDIS_URL", "not-set"),
            "api_key_configured": bool(os.environ.get("PANOPTICON_API_KEY"))
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
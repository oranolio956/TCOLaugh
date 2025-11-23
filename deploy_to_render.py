#!/usr/bin/env python3
"""
Deploy Panopticon to Render using the Render API
"""

import json
import os
import random
import string
import time
from typing import Dict, Any, List
import requests

# Render API configuration
def _require_env(var_name: str) -> str:
    value = os.environ.get(var_name)
    if not value:
        raise RuntimeError(f"Environment variable '{var_name}' must be set before running this script.")
    return value

RENDER_API_KEY = _require_env("RENDER_API_KEY")
RENDER_API_URL = "https://api.render.com/v1"
HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {RENDER_API_KEY}",
    "Content-Type": "application/json"
}

def generate_api_key():
    """Generate a secure random API key for Panopticon"""
    chars = string.ascii_letters + string.digits
    return f"pano_{''.join(random.choices(chars, k=32))}"

def get_owner_id():
    """Get the owner ID for the current user"""
    response = requests.get(f"{RENDER_API_URL}/owners", headers=HEADERS)
    if response.status_code == 200:
        owners = response.json()
        if owners and len(owners) > 0:
            return owners[0]["owner"]["id"]
    raise Exception(f"Failed to get owner ID: {response.status_code} - {response.text}")

def create_service(service_config: Dict[str, Any]) -> str:
    """Create a Render service and return its ID"""
    response = requests.post(f"{RENDER_API_URL}/services", headers=HEADERS, json=service_config)
    if response.status_code in [200, 201]:
        service = response.json()
        print(f"✓ Created service: {service['service']['name']} ({service['service']['id']})")
        return service["service"]["id"]
    else:
        raise Exception(f"Failed to create service: {response.status_code} - {response.text}")

def deploy_service(service_id: str):
    """Trigger a deployment for a service"""
    response = requests.post(f"{RENDER_API_URL}/services/{service_id}/deploys", headers=HEADERS, json={"clearCache": False})
    if response.status_code in [200, 201]:
        deploy = response.json()
        print(f"✓ Deployment started: {deploy['id']}")
        return deploy["id"]
    else:
        print(f"⚠ Failed to deploy service: {response.status_code} - {response.text}")
        return None

def main():
    print("🚀 Starting Panopticon deployment to Render...")
    
    try:
        # Get owner ID
        owner_id = get_owner_id()
        print(f"✓ Using owner ID: {owner_id}")
        
        # Generate unique names for services to avoid conflicts
        timestamp = str(int(time.time()))[-6:]
        
        # Generate API key for Panopticon
        panopticon_api_key = generate_api_key()
        neo4j_password = generate_api_key()
        
        print(f"\n📋 Generated credentials:")
        print(f"   PANOPTICON_API_KEY: {panopticon_api_key}")
        print(f"   NEO4J_PASSWORD: {neo4j_password}")
        
        services_created = []
        
        # Note: Redis on Render is typically an addon to a service, not a standalone service
        # For now, we'll use a default Redis URL and you can add Redis addon later
        print("\n📦 Note: Redis should be added as an addon to services in Render dashboard")
        redis_url = "redis://red-ctmu4tq3esus73a9g240:6379"  # Placeholder - will be replaced with actual Redis addon
        
        # 2. Create Web Service
        print("\n🌐 Creating Web Service...")
        web_config = {
            "type": "web_service",
            "name": f"panopticon-api-{timestamp}",
            "ownerId": owner_id,
            "plan": "free",
            "region": "oregon",
            "runtime": "python",
            "repo": "https://github.com/yourusername/panopticon",
            "autoDeploy": "yes",
            "branch": "main",
            "buildCommand": "pip install -r requirements.txt && python -m spacy download en_core_web_sm",
            "startCommand": "uvicorn panopticon.api.main:app --host 0.0.0.0 --port $PORT",
            "envVars": [
                {"key": "PYTHON_VERSION", "value": "3.9"},
                {"key": "PANOPTICON_API_KEY", "value": panopticon_api_key},
                {"key": "PANOPTICON_ENABLE_AI_BRIEFING", "value": "false"},
                {"key": "PANOPTICON_MAX_UPLOAD_BYTES", "value": "5242880"},
                {"key": "PANOPTICON_DB_PATH", "value": "/opt/render/project/src/data/panopticon.db"},
                {"key": "NEO4J_URI", "value": "bolt://localhost:7687"},
                {"key": "NEO4J_USER", "value": "neo4j"},
                {"key": "NEO4J_PASSWORD", "value": neo4j_password},
                {"key": "MILVUS_HOST", "value": "localhost"},
                {"key": "MILVUS_PORT", "value": "19530"},
                {"key": "PANOPTICON_USE_KAFKA", "value": "false"},
                {"key": "REDIS_URL", "value": redis_url}
            ],
            "dockerCommand": "",
            "initialDeployHook": ""
        }
        
        # Check if repo exists or use manual deployment
        print("\n⚠ Note: Since we don't have a GitHub repository URL, we'll create the service for manual deployment.")
        
        # Modified config for manual deployment
        web_config_manual = {
            "type": "web_service", 
            "name": f"panopticon-api-{timestamp}",
            "ownerId": owner_id,
            "plan": "free",
            "region": "oregon",
            "serviceDetails": {
                "env": "python",
                "buildCommand": "pip install -r requirements.txt && python -m spacy download en_core_web_sm",
                "startCommand": "uvicorn panopticon.api.main:app --host 0.0.0.0 --port 10000",
                "envVars": {
                    "PYTHON_VERSION": {"value": "3.9"},
                    "PANOPTICON_API_KEY": {"value": panopticon_api_key},
                    "PANOPTICON_ENABLE_AI_BRIEFING": {"value": "false"},
                    "PANOPTICON_MAX_UPLOAD_BYTES": {"value": "5242880"},
                    "PANOPTICON_DB_PATH": {"value": "/opt/render/project/src/data/panopticon.db"},
                    "NEO4J_URI": {"value": "bolt://localhost:7687"},
                    "NEO4J_USER": {"value": "neo4j"},
                    "NEO4J_PASSWORD": {"value": neo4j_password},
                    "MILVUS_HOST": {"value": "localhost"},
                    "MILVUS_PORT": {"value": "19530"},
                    "PANOPTICON_USE_KAFKA": {"value": "false"},
                    "REDIS_URL": {"value": redis_url}
                }
            }
        }
        
        web_id = create_service(web_config_manual)
        services_created.append(("Web Service", web_id))
        
        # 3. Create Worker Service  
        print("\n⚙️ Creating Worker Service...")
        worker_config = {
            "type": "background_worker",
            "name": f"panopticon-worker-{timestamp}",
            "ownerId": owner_id,
            "plan": "free",
            "region": "oregon",
            "serviceDetails": {
                "env": "python",
                "buildCommand": "pip install -r requirements.txt && python -m spacy download en_core_web_sm",
                "startCommand": "celery -A panopticon.worker worker --loglevel=info",
                "envVars": {
                    "PYTHON_VERSION": {"value": "3.9"},
                    "REDIS_URL": {"value": redis_url},
                    "NEO4J_URI": {"value": "bolt://localhost:7687"},
                    "NEO4J_USER": {"value": "neo4j"},
                    "NEO4J_PASSWORD": {"value": neo4j_password}
                }
            }
        }
        worker_id = create_service(worker_config)
        services_created.append(("Worker", worker_id))
        
        # 4. Create Crawler Service
        print("\n🕷️ Creating Crawler Service...")
        crawler_config = {
            "type": "background_worker",
            "name": f"panopticon-crawler-{timestamp}",
            "ownerId": owner_id,
            "plan": "free", 
            "region": "oregon",
            "serviceDetails": {
                "env": "python",
                "buildCommand": "pip install -r requirements.txt && python -m spacy download en_core_web_sm",
                "startCommand": "python3 -m panopticon.ingestion.tor.crawler",
                "envVars": {
                    "PYTHON_VERSION": {"value": "3.9"},
                    "PANOPTICON_USE_KAFKA": {"value": "false"}
                }
            }
        }
        crawler_id = create_service(crawler_config)
        services_created.append(("Crawler", crawler_id))
        
        print("\n✅ All services created successfully!")
        print("\n📋 Service Summary:")
        for name, service_id in services_created:
            print(f"   {name}: {service_id}")
        
        print("\n🔐 Important Credentials (save these!):")
        print(f"   PANOPTICON_API_KEY: {panopticon_api_key}")
        print(f"   NEO4J_PASSWORD: {neo4j_password}")
        
        print("\n📌 Next Steps:")
        print("1. Push your code to a GitHub repository")
        print("2. Connect the services to your repository in Render dashboard")
        print("3. Or use Render CLI to deploy manually")
        print(f"4. Your API will be available at: https://panopticon-api-{timestamp}.onrender.com")
        
        # Save credentials to file
        with open("/workspace/render_credentials.json", "w") as f:
            json.dump({
                "services": dict(services_created),
                "credentials": {
                    "PANOPTICON_API_KEY": panopticon_api_key,
                    "NEO4J_PASSWORD": neo4j_password,
                    "REDIS_URL": redis_url
                },
                "api_url": f"https://panopticon-api-{timestamp}.onrender.com"
            }, f, indent=2)
        print("\n✓ Credentials saved to render_credentials.json")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
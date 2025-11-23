#!/usr/bin/env python3
"""
Deploy Panopticon to Render using the Render API
"""

import json
import os
import random
import string
import time
from typing import Dict, Any, List, Optional
import requests
import sys

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

GITHUB_REPO = "https://github.com/your-username/panopticon"  # Update this with actual repo

def generate_secure_key(prefix="pano", length=32):
    """Generate a secure random API key"""
    chars = string.ascii_letters + string.digits
    return f"{prefix}_{''.join(random.choices(chars, k=length))}"

def get_owner_id():
    """Get the owner ID for the current user"""
    response = requests.get(f"{RENDER_API_URL}/owners", headers=HEADERS)
    if response.status_code == 200:
        owners = response.json()
        if owners and len(owners) > 0:
            return owners[0]["owner"]["id"]
    raise Exception(f"Failed to get owner ID: {response.status_code} - {response.text}")

def create_render_service(service_type: str, name: str, config: Dict[str, Any], owner_id: str) -> Optional[str]:
    """Create a Render service"""
    
    base_config = {
        "type": service_type,
        "name": name,
        "ownerId": owner_id,
        "plan": "free",
        "region": "oregon"
    }
    
    if service_type in ["web_service", "background_worker"]:
        # For services that need code
        service_details = {
            "env": "python",
            "envVars": config.get("envVars", {}),
            "buildCommand": config.get("buildCommand", "pip install -r requirements.txt"),
            "startCommand": config.get("startCommand", "")
        }
        
        # Check if we're using git repo or image
        if config.get("repo"):
            service_details["repo"] = config["repo"]
            service_details["branch"] = config.get("branch", "main")
            service_details["autoDeploy"] = config.get("autoDeploy", "yes")
        elif config.get("image"):
            service_details["image"] = config["image"]
            service_details["dockerCommand"] = config.get("dockerCommand", "")
        
        base_config["serviceDetails"] = service_details
        
        if service_type == "web_service":
            service_details["numInstances"] = 1
            service_details["healthCheckPath"] = config.get("healthCheckPath", "/")
    
    print(f"Creating {service_type}: {name}...")
    
    # Debug print
    print(f"Config being sent: {json.dumps(base_config, indent=2)}")
    
    response = requests.post(f"{RENDER_API_URL}/services", headers=HEADERS, json=base_config)
    
    if response.status_code in [200, 201]:
        service_data = response.json()
        service_id = service_data.get("service", {}).get("id")
        print(f"✓ Created {name}: {service_id}")
        return service_id
    else:
        print(f"✗ Failed to create {name}: {response.status_code}")
        print(f"  Response: {response.text}")
        return None

def main():
    print("🚀 Starting Panopticon deployment to Render...\n")
    
    try:
        # Get owner ID
        owner_id = get_owner_id()
        print(f"✓ Using owner ID: {owner_id}\n")
        
        # Generate unique service names
        timestamp = str(int(time.time()))[-6:]
        
        # Generate credentials
        panopticon_api_key = generate_secure_key("pano", 32)
        neo4j_password = generate_secure_key("neo4j", 24)
        
        print("📋 Generated Credentials:")
        print(f"   PANOPTICON_API_KEY: {panopticon_api_key}")
        print(f"   NEO4J_PASSWORD: {neo4j_password}\n")
        
        services = []
        
        # Environment variables shared across services
        base_env_vars = {
            "PYTHON_VERSION": {"value": "3.9"},
            "PANOPTICON_API_KEY": {"value": panopticon_api_key},
            "NEO4J_URI": {"value": "bolt://localhost:7687"},
            "NEO4J_USER": {"value": "neo4j"}, 
            "NEO4J_PASSWORD": {"value": neo4j_password},
            "REDIS_URL": {"value": "redis://localhost:6379"}  # Will be updated when Redis addon is created
        }
        
        # 1. Create Web Service (API)
        web_env_vars = base_env_vars.copy()
        web_env_vars.update({
            "PANOPTICON_ENABLE_AI_BRIEFING": {"value": "false"},
            "PANOPTICON_MAX_UPLOAD_BYTES": {"value": "5242880"},
            "PANOPTICON_DB_PATH": {"value": "/opt/render/project/src/data/panopticon.db"},
            "MILVUS_HOST": {"value": "localhost"},
            "MILVUS_PORT": {"value": "19530"},
            "PANOPTICON_USE_KAFKA": {"value": "false"},
            "PANOPTICON_DOCUMENT_TTL_SECONDS": {"value": "86400"},
            "PANOPTICON_INDEX_FIELDS": {"value": "email,username,phone,ip_address"},
            "PANOPTICON_RECON_TIMEOUT": {"value": "3"},
            "PANOPTICON_AI_GRAPH_LIMIT": {"value": "40"},
            # Phase 3: Stealth Features (Optional - proxies disabled by default)
            "PANOPTICON_ENABLE_PROXY": {"value": "false"},
            # Uncomment if using proxy providers:
            # "SMARTPROXY_ENDPOINT": {"value": "http://gate.smartproxy.com:10000"},
            # "SMARTPROXY_USERNAME": {"value": "your_username"},
            # "SMARTPROXY_PASSWORD": {"value": "your_password"},
        })
        
        web_config = {
            "repo": GITHUB_REPO,
            "branch": "main",
            "buildCommand": "pip install -r requirements.txt && python -m spacy download en_core_web_sm",
            "startCommand": "uvicorn panopticon.api.main:app --host 0.0.0.0 --port $PORT",
            "envVars": web_env_vars,
            "healthCheckPath": "/",
            "autoDeploy": "yes"
        }
        
        web_id = create_render_service(
            "web_service",
            f"panopticon-api-{timestamp}",
            web_config,
            owner_id
        )
        if web_id:
            services.append(("Web API", web_id))
        
        # 2. Create Background Worker (Celery)
        worker_env_vars = base_env_vars.copy()
        worker_env_vars.update({
            "PANOPTICON_DB_PATH": {"value": "/opt/render/project/src/data/panopticon.db"},
            "MILVUS_HOST": {"value": "localhost"},
            "MILVUS_PORT": {"value": "19530"}
        })
        
        worker_config = {
            "repo": GITHUB_REPO,
            "branch": "main",
            "buildCommand": "pip install -r requirements.txt && python -m spacy download en_core_web_sm",
            "startCommand": "celery -A panopticon.worker worker --loglevel=info",
            "envVars": worker_env_vars
        }
        
        worker_id = create_render_service(
            "background_worker",
            f"panopticon-worker-{timestamp}",
            worker_config,
            owner_id
        )
        if worker_id:
            services.append(("Celery Worker", worker_id))
        
        # 3. Create Crawler Background Worker
        crawler_env_vars = {
            "PYTHON_VERSION": {"value": "3.9"},
            "PANOPTICON_USE_KAFKA": {"value": "false"},
            "KAFKA_BOOTSTRAP_SERVERS": {"value": "localhost:9092"}
        }
        
        crawler_config = {
            "repo": GITHUB_REPO,
            "branch": "main",
            "buildCommand": "pip install -r requirements.txt && python -m spacy download en_core_web_sm",
            "startCommand": "python3 -m panopticon.ingestion.tor.crawler",
            "envVars": crawler_env_vars
        }
        
        crawler_id = create_render_service(
            "background_worker",
            f"panopticon-crawler-{timestamp}",
            crawler_config,
            owner_id
        )
        if crawler_id:
            services.append(("Crawler", crawler_id))
        
        print("\n" + "="*60)
        print("✅ DEPLOYMENT SUMMARY")
        print("="*60)
        
        if services:
            print("\n📦 Services Created:")
            for name, sid in services:
                print(f"   • {name}: {sid}")
        else:
            print("\n⚠ No services were created successfully")
            return 1
        
        print("\n🔐 Credentials (SAVE THESE!):")
        print(f"   PANOPTICON_API_KEY: {panopticon_api_key}")
        print(f"   NEO4J_PASSWORD: {neo4j_password}")
        
        print("\n📌 Next Steps:")
        print("1. Connect your GitHub repository to the services")
        print("2. Add Redis addon to the Web service in Render dashboard")
        print("3. Configure persistent disk for the Web service (for SQLite)")
        print("4. Optionally set up managed Neo4j and Milvus services")
        print(f"5. Your API will be at: https://panopticon-api-{timestamp}.onrender.com")
        
        print("\n💡 To add Redis addon:")
        print("   - Go to Render dashboard")
        print("   - Select the web service")
        print("   - Go to 'Environment' tab")
        print("   - Add Redis addon")
        print("   - Update REDIS_URL environment variable")
        
        # Save configuration
        config_data = {
            "timestamp": timestamp,
            "services": dict(services),
            "credentials": {
                "PANOPTICON_API_KEY": panopticon_api_key,
                "NEO4J_PASSWORD": neo4j_password
            },
            "api_url": f"https://panopticon-api-{timestamp}.onrender.com"
        }
        
        with open("/workspace/render_deployment.json", "w") as f:
            json.dump(config_data, f, indent=2)
        
        print(f"\n✓ Configuration saved to render_deployment.json")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
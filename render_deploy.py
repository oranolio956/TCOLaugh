#!/usr/bin/env python3
"""
Deploy Panopticon to Render - Simplified Approach
Creates services on Render that can be manually deployed
"""

import json
import os
import random
import string
import sys
import time
from typing import Dict, Any, Optional, List
import requests

# Configuration
def _require_env(var_name: str) -> str:
    value = os.environ.get(var_name)
    if not value:
        raise RuntimeError(f"Environment variable '{var_name}' must be set before running this script.")
    return value

RENDER_API_KEY = _require_env("RENDER_API_KEY")
RENDER_API_URL = "https://api.render.com/v1"

class RenderDeployer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.owner_id = None
        self.services_created = []
        
    def generate_key(self, length: int = 32) -> str:
        """Generate a random secure key"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=length))
    
    def get_owner_info(self) -> bool:
        """Get owner information from Render"""
        try:
            response = requests.get(f"{RENDER_API_URL}/owners", headers=self.headers)
            if response.status_code == 200:
                owners = response.json()
                if owners and len(owners) > 0:
                    self.owner_id = owners[0]["owner"]["id"]
                    owner_name = owners[0]["owner"].get("name", "Unknown")
                    print(f"✓ Authenticated as: {owner_name} ({self.owner_id})")
                    return True
        except Exception as e:
            print(f"✗ Authentication failed: {e}")
        return False
    
    def create_web_service(self, name: str, env_vars: Dict[str, str]) -> Optional[str]:
        """Create a web service on Render"""
        
        service_config = {
            "type": "web_service",
            "name": name,
            "ownerId": self.owner_id,
            "plan": "free",
            "serviceDetails": {
                "env": "docker",
                "dockerfilePath": "./Dockerfile",
                "dockerContext": ".",
                "envVars": {k: {"value": v} for k, v in env_vars.items()}
            }
        }
        
        # Alternative: Use Python environment without Docker
        service_config_python = {
            "type": "web_service",
            "name": name,
            "ownerId": self.owner_id,
            "plan": "free",
            "serviceDetails": {
                "env": "python",
                "buildCommand": "pip install -r requirements.txt && python -m spacy download en_core_web_sm",
                "startCommand": "uvicorn panopticon.api.main:app --host 0.0.0.0 --port $PORT",
                "envVars": {k: {"value": v} for k, v in env_vars.items()},
                "numInstances": 1
            }
        }
        
        print(f"Creating web service: {name}...")
        
        try:
            response = requests.post(
                f"{RENDER_API_URL}/services",
                headers=self.headers,
                json=service_config_python
            )
            
            if response.status_code in [200, 201]:
                service = response.json()
                service_id = service["service"]["id"]
                service_url = service["service"].get("serviceDetails", {}).get("url", "")
                print(f"✓ Created: {name}")
                print(f"  ID: {service_id}")
                if service_url:
                    print(f"  URL: https://{service_url}")
                return service_id
            else:
                print(f"✗ Failed to create {name}: {response.status_code}")
                print(f"  Error: {response.text}")
        except Exception as e:
            print(f"✗ Exception creating {name}: {e}")
        
        return None
    
    def create_background_worker(self, name: str, start_command: str, env_vars: Dict[str, str]) -> Optional[str]:
        """Create a background worker on Render"""
        
        service_config = {
            "type": "background_worker",
            "name": name,
            "ownerId": self.owner_id,
            "plan": "free",
            "serviceDetails": {
                "env": "python",
                "buildCommand": "pip install -r requirements.txt && python -m spacy download en_core_web_sm",
                "startCommand": start_command,
                "envVars": {k: {"value": v} for k, v in env_vars.items()}
            }
        }
        
        print(f"Creating background worker: {name}...")
        
        try:
            response = requests.post(
                f"{RENDER_API_URL}/services",
                headers=self.headers,
                json=service_config
            )
            
            if response.status_code in [200, 201]:
                service = response.json()
                service_id = service["service"]["id"]
                print(f"✓ Created: {name}")
                print(f"  ID: {service_id}")
                return service_id
            else:
                print(f"✗ Failed to create {name}: {response.status_code}")
                print(f"  Error: {response.text}")
        except Exception as e:
            print(f"✗ Exception creating {name}: {e}")
        
        return None
    
    def deploy(self):
        """Main deployment function"""
        
        print("="*60)
        print("🚀 PANOPTICON DEPLOYMENT TO RENDER")
        print("="*60)
        print()
        
        # Authenticate
        if not self.get_owner_info():
            print("✗ Failed to authenticate with Render API")
            return False
        
        # Generate credentials
        timestamp = str(int(time.time()))[-6:]
        panopticon_api_key = f"pano_{self.generate_key(32)}"
        neo4j_password = f"neo4j_{self.generate_key(24)}"
        
        print("\n📋 Generated Credentials:")
        print(f"  PANOPTICON_API_KEY: {panopticon_api_key}")
        print(f"  NEO4J_PASSWORD: {neo4j_password}")
        print()
        
        # Base environment variables
        base_env = {
            "PYTHON_VERSION": "3.9",
            "PANOPTICON_API_KEY": panopticon_api_key,
            "NEO4J_URI": "bolt://localhost:7687",
            "NEO4J_USER": "neo4j",
            "NEO4J_PASSWORD": neo4j_password,
            "REDIS_URL": "redis://localhost:6379",
            "PANOPTICON_DB_PATH": "/var/data/panopticon.db",
        }
        
        # 1. Create Web Service
        web_env = base_env.copy()
        web_env.update({
            "PANOPTICON_ENABLE_AI_BRIEFING": "false",
            "PANOPTICON_MAX_UPLOAD_BYTES": "5242880",
            "MILVUS_HOST": "localhost",
            "MILVUS_PORT": "19530",
            "PANOPTICON_USE_KAFKA": "false",
            "PANOPTICON_DOCUMENT_TTL_SECONDS": "0",
            "PANOPTICON_INDEX_FIELDS": "email,username,phone,ip_address",
            "PANOPTICON_RECON_TIMEOUT": "3",
            "PANOPTICON_AI_GRAPH_LIMIT": "40"
        })
        
        web_id = self.create_web_service(f"panopticon-api-{timestamp}", web_env)
        if web_id:
            self.services_created.append(("API", web_id, f"https://panopticon-api-{timestamp}.onrender.com"))
        
        # 2. Create Worker Service
        worker_env = base_env.copy()
        worker_env.update({
            "MILVUS_HOST": "localhost",
            "MILVUS_PORT": "19530"
        })
        
        worker_id = self.create_background_worker(
            f"panopticon-worker-{timestamp}",
            "celery -A panopticon.worker worker --loglevel=info",
            worker_env
        )
        if worker_id:
            self.services_created.append(("Worker", worker_id, None))
        
        # 3. Create Crawler Service
        crawler_env = {
            "PYTHON_VERSION": "3.9",
            "PANOPTICON_USE_KAFKA": "false"
        }
        
        crawler_id = self.create_background_worker(
            f"panopticon-crawler-{timestamp}",
            "python3 -m panopticon.ingestion.crawlers.mock_crawler --continuous --delay 10",
            crawler_env
        )
        if crawler_id:
            self.services_created.append(("Crawler", crawler_id, None))
        
        # Summary
        print("\n" + "="*60)
        print("📊 DEPLOYMENT SUMMARY")
        print("="*60)
        
        if self.services_created:
            print("\n✅ Services Created Successfully:")
            for name, service_id, url in self.services_created:
                print(f"\n  {name}:")
                print(f"    ID: {service_id}")
                if url:
                    print(f"    URL: {url}")
            
            # Save deployment info
            deployment_info = {
                "timestamp": timestamp,
                "services": [
                    {"name": name, "id": sid, "url": url}
                    for name, sid, url in self.services_created
                ],
                "credentials": {
                    "PANOPTICON_API_KEY": panopticon_api_key,
                    "NEO4J_PASSWORD": neo4j_password
                },
                "api_endpoint": f"https://panopticon-api-{timestamp}.onrender.com"
            }
            
            with open("/workspace/render_deployment.json", "w") as f:
                json.dump(deployment_info, f, indent=2)
            
            print("\n💾 Deployment info saved to: render_deployment.json")
            
            print("\n" + "="*60)
            print("📝 NEXT STEPS")
            print("="*60)
            print("""
1. Push Code to Services:
   - Go to https://dashboard.render.com
   - For each service, go to Settings > Build & Deploy
   - Connect to a Git repository OR
   - Use manual deploy with: git push render main

2. Add Persistent Storage:
   - Go to the API service in Render dashboard
   - Add a disk mount at /var/data

3. Add Redis (Optional):
   - In the API service, go to Environment
   - Add Redis addon
   - Update REDIS_URL environment variable

4. Configure External Services (Optional):
   - Set up managed Neo4j (e.g., AuraDB)
   - Set up managed Milvus (e.g., Zilliz Cloud)
   - Update respective environment variables

5. Monitor Services:
   - Check logs in Render dashboard
   - Verify health checks are passing
   - Test API endpoints
""")
            
            print(f"\n🌐 Your API will be available at:")
            print(f"   {deployment_info['api_endpoint']}")
            print(f"\n🔑 Use this API key for requests:")
            print(f"   {panopticon_api_key}")
            
        else:
            print("\n⚠ No services were created successfully")
            print("Please check your Render API key and try again")
            return False
        
        return True

def main():
    deployer = RenderDeployer(RENDER_API_KEY)
    success = deployer.deploy()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
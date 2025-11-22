#!/usr/bin/env python3
"""
Create Render services via API
"""

import json
import os
import sys
import time
import requests
from typing import Dict, Any, Optional

# Configuration
RENDER_API_KEY = os.environ.get("RENDER_API_KEY", "rnd_MBBJ6LlNi410654cpxpNUHGKnwRS")
RENDER_API_URL = "https://api.render.com/v1"
GITHUB_REPO = "https://github.com/oranolio956/TCOLaugh"

class RenderServiceCreator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.owner_id = None
        
    def get_owner_info(self) -> bool:
        """Get owner information"""
        try:
            response = requests.get(f"{RENDER_API_URL}/owners", headers=self.headers)
            if response.status_code == 200:
                owners = response.json()
                if owners and len(owners) > 0:
                    self.owner_id = owners[0]["owner"]["id"]
                    print(f"✓ Owner ID: {self.owner_id}")
                    return True
        except Exception as e:
            print(f"✗ Failed to get owner: {e}")
        return False
    
    def create_service(self, config: Dict[str, Any]) -> Optional[str]:
        """Create a service on Render"""
        print(f"\nCreating service: {config.get('name')}...")
        
        try:
            response = requests.post(
                f"{RENDER_API_URL}/services",
                headers=self.headers,
                json=config
            )
            
            if response.status_code in [200, 201]:
                service = response.json()
                service_id = service.get("service", {}).get("id")
                print(f"✓ Created service: {config.get('name')}")
                print(f"  Service ID: {service_id}")
                return service_id
            else:
                print(f"✗ Failed to create service: {response.status_code}")
                print(f"  Response: {response.text}")
                
                # Parse error message
                try:
                    error_data = response.json()
                    if "message" in error_data:
                        print(f"  Error: {error_data['message']}")
                except:
                    pass
                    
        except Exception as e:
            print(f"✗ Exception: {e}")
        
        return None
    
    def create_all_services(self):
        """Create all Panopticon services"""
        
        if not self.get_owner_info():
            print("✗ Failed to authenticate")
            return False
        
        # Load deployment info
        if not os.path.exists("/workspace/deployment_info.json"):
            print("✗ deployment_info.json not found")
            return False
        
        with open("/workspace/deployment_info.json", "r") as f:
            deployment_info = json.load(f)
        
        credentials = deployment_info.get("credentials", {})
        api_key = credentials.get("PANOPTICON_API_KEY")
        neo4j_password = credentials.get("NEO4J_PASSWORD")
        timestamp = deployment_info.get("timestamp", "847835")
        
        print("\n" + "="*60)
        print("🚀 CREATING RENDER SERVICES")
        print("="*60)
        
        services_created = []
        
        # 1. Create Web Service
        web_config = {
            "type": "web_service",
            "name": f"panopticon-api-{timestamp}",
            "ownerId": self.owner_id,
            "plan": "free",
            "region": "oregon",
            "repo": GITHUB_REPO,
            "branch": "main",
            "autoDeploy": "yes",
            "serviceDetails": {
                "env": "python",
                "envSpecificDetails": {
                    "buildCommand": "pip install -r requirements.txt && python -m spacy download en_core_web_sm || true",
                    "startCommand": "uvicorn panopticon.api.main:app --host 0.0.0.0 --port $PORT"
                },
                "envVars": {
                    "PYTHON_VERSION": {"value": "3.9"},
                    "PANOPTICON_API_KEY": {"value": api_key},
                    "PANOPTICON_ENABLE_AI_BRIEFING": {"value": "false"},
                    "PANOPTICON_MAX_UPLOAD_BYTES": {"value": "5242880"},
                    "PANOPTICON_DB_PATH": {"value": "/opt/render/project/.render/panopticon.db"},
                    "NEO4J_URI": {"value": "bolt://localhost:7687"},
                    "NEO4J_USER": {"value": "neo4j"},
                    "NEO4J_PASSWORD": {"value": neo4j_password},
                    "MILVUS_HOST": {"value": "localhost"},
                    "MILVUS_PORT": {"value": "19530"},
                    "PANOPTICON_USE_KAFKA": {"value": "false"},
                    "REDIS_URL": {"value": "redis://localhost:6379"}
                },
                "numInstances": 1,
                "healthCheckPath": "/"
            }
        }
        
        web_id = self.create_service(web_config)
        if web_id:
            services_created.append(("Web API", web_id))
            
            # Wait a bit before creating the next service
            time.sleep(2)
        
        # 2. Create Worker Service
        worker_config = {
            "type": "background_worker",
            "name": f"panopticon-worker-{timestamp}",
            "ownerId": self.owner_id,
            "plan": "free",
            "region": "oregon",
            "repo": GITHUB_REPO,
            "branch": "main",
            "autoDeploy": "yes",
            "serviceDetails": {
                "env": "python",
                "envSpecificDetails": {
                    "buildCommand": "pip install -r requirements.txt && python -m spacy download en_core_web_sm || true",
                    "startCommand": "celery -A panopticon.worker worker --loglevel=info"
                },
                "envVars": {
                    "PYTHON_VERSION": {"value": "3.9"},
                    "REDIS_URL": {"value": "redis://localhost:6379"},
                    "NEO4J_URI": {"value": "bolt://localhost:7687"},
                    "NEO4J_USER": {"value": "neo4j"},
                    "NEO4J_PASSWORD": {"value": neo4j_password},
                    "MILVUS_HOST": {"value": "localhost"},
                    "MILVUS_PORT": {"value": "19530"},
                    "PANOPTICON_DB_PATH": {"value": "/opt/render/project/.render/panopticon.db"}
                }
            }
        }
        
        worker_id = self.create_service(worker_config)
        if worker_id:
            services_created.append(("Worker", worker_id))
            time.sleep(2)
        
        # 3. Create Crawler Service
        crawler_config = {
            "type": "background_worker",
            "name": f"panopticon-crawler-{timestamp}",
            "ownerId": self.owner_id,
            "plan": "free",
            "region": "oregon",
            "repo": GITHUB_REPO,
            "branch": "main",
            "autoDeploy": "yes",
            "serviceDetails": {
                "env": "python",
                "envSpecificDetails": {
                    "buildCommand": "pip install -r requirements.txt",
                    "startCommand": "python3 panopticon/ingestion/crawlers/mock_crawler.py --continuous --delay 30"
                },
                "envVars": {
                    "PYTHON_VERSION": {"value": "3.9"},
                    "PANOPTICON_USE_KAFKA": {"value": "false"}
                }
            }
        }
        
        crawler_id = self.create_service(crawler_config)
        if crawler_id:
            services_created.append(("Crawler", crawler_id))
        
        print("\n" + "="*60)
        print("📊 DEPLOYMENT SUMMARY")
        print("="*60)
        
        if services_created:
            print("\n✅ Services Created:")
            for name, service_id in services_created:
                print(f"  • {name}: {service_id}")
            
            print(f"\n🌐 API will be available at:")
            print(f"  https://panopticon-api-{timestamp}.onrender.com")
            
            print(f"\n🔑 API Key:")
            print(f"  {api_key}")
            
            print("\n⏳ Services are now building and deploying...")
            print("  This may take 5-10 minutes for the first deployment")
            print("  Monitor progress at: https://dashboard.render.com")
            
            # Save service IDs
            deployment_info["service_ids"] = dict(services_created)
            with open("/workspace/deployment_info.json", "w") as f:
                json.dump(deployment_info, f, indent=2)
            
            return True
        else:
            print("\n⚠ No services were created successfully")
            return False

def main():
    creator = RenderServiceCreator(RENDER_API_KEY)
    success = creator.create_all_services()
    
    if success:
        print("\n✅ Services created successfully!")
        print("Run 'python3 monitor_render_services.py' to check deployment status")
        return 0
    else:
        print("\n✗ Failed to create services")
        return 1

if __name__ == "__main__":
    sys.exit(main())
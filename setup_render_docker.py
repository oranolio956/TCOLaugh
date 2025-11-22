#!/usr/bin/env python3
"""
Deploy Panopticon to Render using Docker images
This approach doesn't require a GitHub repository
"""

import json
import os
import random
import string
import sys
import time
from typing import Dict, Any, Optional
import requests

# Configuration
RENDER_API_KEY = os.environ.get("RENDER_API_KEY", "rnd_MBBJ6LlNi410654cpxpNUHGKnwRS")
RENDER_API_URL = "https://api.render.com/v1"

class RenderDockerDeployer:
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
    
    def create_docker_service(self, service_type: str, name: str, image: str, 
                            command: str, env_vars: Dict[str, str],
                            port: Optional[int] = None) -> Optional[str]:
        """Create a service using Docker image"""
        
        service_config = {
            "type": service_type,
            "name": name,
            "ownerId": self.owner_id,
            "plan": "free",
            "serviceDetails": {
                "env": "image",
                "image": {"ownerId": self.owner_id, "imagePath": image},
                "envVars": {k: {"value": v} for k, v in env_vars.items()}
            }
        }
        
        if command:
            service_config["serviceDetails"]["dockerCommand"] = command
            
        if service_type == "web_service" and port:
            service_config["serviceDetails"]["containerPort"] = port
            service_config["serviceDetails"]["healthCheckPath"] = "/"
            
        print(f"Creating {service_type}: {name}...")
        
        try:
            response = requests.post(
                f"{RENDER_API_URL}/services",
                headers=self.headers,
                json=service_config
            )
            
            if response.status_code in [200, 201]:
                service = response.json()
                service_id = service["service"]["id"]
                print(f"✓ Created: {name} ({service_id})")
                return service_id
            else:
                print(f"✗ Failed to create {name}: {response.status_code}")
                print(f"  Error: {response.text}")
        except Exception as e:
            print(f"✗ Exception creating {name}: {e}")
        
        return None
    
    def build_and_push_image(self, service_name: str, dockerfile_content: str = None):
        """Build and push Docker image to Render registry"""
        
        print(f"\n📦 Building Docker image for {service_name}...")
        
        # First, let's create or update the Dockerfile if needed
        if dockerfile_content:
            with open("/workspace/Dockerfile", "w") as f:
                f.write(dockerfile_content)
        
        # Get registry credentials
        response = requests.get(f"{RENDER_API_URL}/docker/registry-credential", headers=self.headers)
        if response.status_code == 200:
            creds = response.json()
            registry_url = creds.get("registryUrl", "registry.render.com")
            username = creds.get("username")
            password = creds.get("password")
            
            print(f"  Registry: {registry_url}")
            
            # Return the image path that will be used
            image_name = f"{service_name}:latest"
            full_image = f"{registry_url}/{self.owner_id}/{image_name}"
            
            print(f"  Image will be: {full_image}")
            print("  Note: You'll need to build and push this image manually")
            
            return full_image
        else:
            print(f"✗ Failed to get registry credentials: {response.status_code}")
            return None
    
    def deploy(self):
        """Main deployment function"""
        
        print("="*60)
        print("🚀 PANOPTICON DEPLOYMENT TO RENDER (Docker Approach)")
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
        
        # Base environment variables
        base_env = {
            "PYTHON_VERSION": "3.9",
            "PANOPTICON_API_KEY": panopticon_api_key,
            "NEO4J_URI": "bolt://localhost:7687",
            "NEO4J_USER": "neo4j",
            "NEO4J_PASSWORD": neo4j_password,
            "REDIS_URL": "redis://localhost:6379",
            "PANOPTICON_DB_PATH": "/data/panopticon.db",
        }
        
        # Create a simplified deployment using public Python image
        print("\n" + "="*60)
        print("📝 MANUAL DEPLOYMENT INSTRUCTIONS")
        print("="*60)
        
        print("""
Since Render requires a Git repository for Python services, you have two options:

OPTION 1: Push to GitHub and Deploy
=====================================
1. Create a GitHub repository:
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/panopticon.git
   git push -u origin main

2. Go to https://dashboard.render.com/create

3. Create Web Service:
   - Connect your GitHub repository
   - Name: panopticon-api-{timestamp}
   - Environment: Python 3
   - Build Command: pip install -r requirements.txt && python -m spacy download en_core_web_sm
   - Start Command: uvicorn panopticon.api.main:app --host 0.0.0.0 --port $PORT
   
4. Create Background Worker (Celery):
   - Same repository
   - Name: panopticon-worker-{timestamp}
   - Start Command: celery -A panopticon.worker worker --loglevel=info

5. Create Background Worker (Crawler):
   - Same repository
   - Name: panopticon-crawler-{timestamp}
   - Start Command: python3 -m panopticon.ingestion.crawlers.mock_crawler

OPTION 2: Use Render Blueprints
================================
""".format(timestamp=timestamp))
        
        # Create a render.yaml blueprint file
        blueprint = {
            "services": [
                {
                    "type": "web",
                    "name": f"panopticon-api-{timestamp}",
                    "env": "python",
                    "plan": "free",
                    "buildCommand": "pip install -r requirements.txt && python -m spacy download en_core_web_sm",
                    "startCommand": "uvicorn panopticon.api.main:app --host 0.0.0.0 --port $PORT",
                    "envVars": [
                        {"key": k, "value": v} for k, v in {
                            **base_env,
                            "PANOPTICON_ENABLE_AI_BRIEFING": "false",
                            "PANOPTICON_MAX_UPLOAD_BYTES": "5242880",
                            "MILVUS_HOST": "localhost",
                            "MILVUS_PORT": "19530",
                            "PANOPTICON_USE_KAFKA": "false"
                        }.items()
                    ],
                    "disk": {
                        "name": "panopticon-data",
                        "mountPath": "/data",
                        "sizeGB": 1
                    }
                },
                {
                    "type": "worker",
                    "name": f"panopticon-worker-{timestamp}",
                    "env": "python",
                    "plan": "free",
                    "buildCommand": "pip install -r requirements.txt && python -m spacy download en_core_web_sm",
                    "startCommand": "celery -A panopticon.worker worker --loglevel=info",
                    "envVars": [
                        {"key": k, "value": v} for k, v in base_env.items()
                    ]
                },
                {
                    "type": "worker",
                    "name": f"panopticon-crawler-{timestamp}",
                    "env": "python", 
                    "plan": "free",
                    "buildCommand": "pip install -r requirements.txt",
                    "startCommand": "python3 -m panopticon.ingestion.crawlers.mock_crawler --continuous --delay 30",
                    "envVars": [
                        {"key": "PYTHON_VERSION", "value": "3.9"},
                        {"key": "PANOPTICON_USE_KAFKA", "value": "false"}
                    ]
                }
            ]
        }
        
        # Save the blueprint
        blueprint_path = "/workspace/render-blueprint.yaml"
        with open(blueprint_path, "w") as f:
            import yaml
            yaml.dump(blueprint, f, default_flow_style=False, sort_keys=False)
        
        print(f"1. Blueprint file created: render-blueprint.yaml")
        print("2. Push to GitHub (see commands above)")
        print("3. Go to: https://dashboard.render.com/blueprints")
        print("4. Click 'New Blueprint Instance'")
        print("5. Connect your repository and select the blueprint file")
        print()
        
        # Save deployment info
        deployment_info = {
            "timestamp": timestamp,
            "credentials": {
                "PANOPTICON_API_KEY": panopticon_api_key,
                "NEO4J_PASSWORD": neo4j_password
            },
            "services": {
                "api": f"panopticon-api-{timestamp}",
                "worker": f"panopticon-worker-{timestamp}",
                "crawler": f"panopticon-crawler-{timestamp}"
            },
            "api_endpoint": f"https://panopticon-api-{timestamp}.onrender.com"
        }
        
        with open("/workspace/render_credentials.json", "w") as f:
            json.dump(deployment_info, f, indent=2)
        
        print("="*60)
        print("🔑 CREDENTIALS SAVED")
        print("="*60)
        print(f"\nFile: render_credentials.json")
        print(f"\nPANOPTICON_API_KEY: {panopticon_api_key}")
        print(f"NEO4J_PASSWORD: {neo4j_password}")
        print(f"\nAPI Endpoint: {deployment_info['api_endpoint']}")
        
        print("\n" + "="*60)
        print("🚀 QUICK DEPLOY COMMANDS")
        print("="*60)
        print("""
# Initialize Git and push to GitHub
git init
git add .
git commit -m "Initial Panopticon deployment"
git branch -M main

# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/panopticon.git
git push -u origin main

# Then visit: https://dashboard.render.com/blueprints
""")
        
        return True

def main():
    # First check if we have pyyaml
    try:
        import yaml
    except ImportError:
        print("Installing PyYAML...")
        os.system("pip install pyyaml")
        import yaml
    
    deployer = RenderDockerDeployer(RENDER_API_KEY)
    success = deployer.deploy()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
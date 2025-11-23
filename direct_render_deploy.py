#!/usr/bin/env python3
"""
Direct deployment to Render using API
Creates services and provides deployment instructions
"""

import json
import os
import random
import string
import sys
import time
import requests
from typing import Dict, Any, Optional

# Configuration
def _require_env(var_name: str) -> str:
    value = os.environ.get(var_name)
    if not value:
        raise RuntimeError(f"Environment variable '{var_name}' must be set before running this script.")
    return value

RENDER_API_KEY = _require_env("RENDER_API_KEY")
RENDER_API_URL = "https://api.render.com/v1"

class DirectRenderDeployer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.owner_id = None
        self.timestamp = str(int(time.time()))[-6:]
        
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
                    owner_email = owners[0]["owner"].get("email", "")
                    print(f"✓ Authenticated as: {owner_name}")
                    print(f"  Owner ID: {self.owner_id}")
                    if owner_email:
                        print(f"  Email: {owner_email}")
                    return True
        except Exception as e:
            print(f"✗ Authentication failed: {e}")
        return False
    
    def list_services(self):
        """List existing services"""
        try:
            response = requests.get(f"{RENDER_API_URL}/services", headers=self.headers)
            if response.status_code == 200:
                services = response.json()
                return services
        except:
            pass
        return []
    
    def create_github_repo(self):
        """Instructions for creating GitHub repository"""
        print("\n" + "="*60)
        print("📦 GITHUB REPOSITORY SETUP")
        print("="*60)
        print("""
1. Create a new GitHub repository:
   - Go to: https://github.com/new
   - Repository name: panopticon
   - Make it public or private
   - Don't initialize with README
   
2. Push local code to GitHub:
   git init
   git add .
   git commit -m "Initial Panopticon deployment"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/panopticon.git
   git push -u origin main
   
3. Note your repository URL for the next step
""")
    
    def generate_deployment_config(self):
        """Generate deployment configuration"""
        
        # Generate credentials
        panopticon_api_key = f"pano_{self.generate_key(32)}"
        neo4j_password = f"neo4j_{self.generate_key(24)}"
        
        print("\n" + "="*60)
        print("🔐 GENERATED CREDENTIALS")
        print("="*60)
        print(f"PANOPTICON_API_KEY: {panopticon_api_key}")
        print(f"NEO4J_PASSWORD: {neo4j_password}")
        
        # Update render.yaml with proper configuration
        render_config = f"""services:
  - type: web
    name: panopticon-api-{self.timestamp}
    runtime: python
    plan: free
    buildCommand: pip install -r requirements.txt && python -m spacy download en_core_web_sm
    startCommand: uvicorn panopticon.api.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: "3.9"
      - key: PANOPTICON_API_KEY
        value: {panopticon_api_key}
      - key: PANOPTICON_ENABLE_AI_BRIEFING
        value: "false"
      - key: PANOPTICON_MAX_UPLOAD_BYTES
        value: "5242880"
      - key: PANOPTICON_DB_PATH
        value: /var/data/panopticon.db
      - key: NEO4J_URI
        value: bolt://localhost:7687
      - key: NEO4J_USER
        value: neo4j
      - key: NEO4J_PASSWORD
        value: {neo4j_password}
      - key: MILVUS_HOST
        value: localhost
      - key: MILVUS_PORT
        value: "19530"
      - key: PANOPTICON_USE_KAFKA
        value: "false"
      - key: REDIS_URL
        value: redis://localhost:6379
      - key: PANOPTICON_DOCUMENT_TTL_SECONDS
        value: "0"
      - key: PANOPTICON_INDEX_FIELDS
        value: email,username,phone,ip_address
      - key: PANOPTICON_RECON_TIMEOUT
        value: "6"
      - key: PANOPTICON_AI_GRAPH_LIMIT
        value: "40"
    disk:
      name: data
      mountPath: /var/data
      sizeGB: 1

  - type: worker
    name: panopticon-worker-{self.timestamp}
    runtime: python
    plan: free
    buildCommand: pip install -r requirements.txt && python -m spacy download en_core_web_sm
    startCommand: celery -A panopticon.worker worker --loglevel=info
    envVars:
      - key: PYTHON_VERSION
        value: "3.9"
      - key: REDIS_URL
        value: redis://localhost:6379
      - key: NEO4J_URI
        value: bolt://localhost:7687
      - key: NEO4J_USER
        value: neo4j
      - key: NEO4J_PASSWORD
        value: {neo4j_password}
      - key: MILVUS_HOST
        value: localhost
      - key: MILVUS_PORT
        value: "19530"
      - key: PANOPTICON_DB_PATH
        value: /var/data/panopticon.db

  - type: worker
    name: panopticon-crawler-{self.timestamp}
    runtime: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python3 panopticon/ingestion/crawlers/mock_crawler.py --continuous --delay 30
    envVars:
      - key: PYTHON_VERSION
        value: "3.9"
      - key: PANOPTICON_USE_KAFKA
        value: "false"
"""
        
        # Save configuration
        with open("/workspace/render.yaml", "w") as f:
            f.write(render_config)
        
        # Save credentials
        deployment_info = {
            "timestamp": self.timestamp,
            "credentials": {
                "PANOPTICON_API_KEY": panopticon_api_key,
                "NEO4J_PASSWORD": neo4j_password
            },
            "services": {
                "api": f"panopticon-api-{self.timestamp}",
                "worker": f"panopticon-worker-{self.timestamp}",
                "crawler": f"panopticon-crawler-{self.timestamp}"
            },
            "api_endpoint": f"https://panopticon-api-{self.timestamp}.onrender.com"
        }
        
        with open("/workspace/deployment_info.json", "w") as f:
            json.dump(deployment_info, f, indent=2)
        
        return panopticon_api_key, neo4j_password
    
    def deploy(self):
        """Main deployment process"""
        
        print("="*60)
        print("🚀 RENDER DEPLOYMENT SETUP")
        print("="*60)
        print()
        
        # Authenticate
        if not self.get_owner_info():
            print("✗ Failed to authenticate with Render API")
            return False
        
        # Check existing services
        existing = self.list_services()
        if existing:
            print(f"\n📋 You have {len(existing)} existing services on Render")
        
        # Generate deployment configuration
        api_key, neo4j_pass = self.generate_deployment_config()
        
        print("\n✓ Generated render.yaml configuration")
        print("✓ Saved credentials to deployment_info.json")
        
        # GitHub setup instructions
        self.create_github_repo()
        
        # Deployment instructions
        print("\n" + "="*60)
        print("🚀 DEPLOYMENT INSTRUCTIONS")
        print("="*60)
        print(f"""
OPTION 1: Deploy via Render Dashboard
======================================
1. Commit the updated render.yaml:
   git add render.yaml
   git commit -m "Add Render deployment configuration"
   git push origin main

2. Go to: https://dashboard.render.com/blueprints
3. Click "New Blueprint Instance"
4. Select your GitHub repository
5. Render will automatically detect render.yaml
6. Click "Apply" to create all services

OPTION 2: Deploy Individual Services
=====================================
1. Go to: https://dashboard.render.com/create
2. For each service (API, Worker, Crawler):
   - Choose "Web Service" for API, "Background Worker" for others
   - Connect your GitHub repository
   - Use the settings from render.yaml

OPTION 3: Use Render CLI (if available)
========================================
render blueprint sync

POST-DEPLOYMENT STEPS
======================
1. Add Redis Addon:
   - Go to the API service in Render dashboard
   - Settings > Environment > Add Redis
   - Update REDIS_URL with the provided connection string

2. Configure Persistent Storage:
   - Already configured in render.yaml (1GB disk)
   - Will be mounted at /var/data

3. Set up External Services (Optional):
   - Neo4j: Use AuraDB (https://aura.datastax.com)
   - Milvus: Use Zilliz Cloud (https://zilliz.com)
   - Update respective environment variables

4. Monitor Deployment:
   - Check service logs in Render dashboard
   - Verify health checks are passing
   - API will be available at: {api_key}

5. Test the API:
   curl -H "X-API-Key: {api_key}" \\
        https://panopticon-api-{self.timestamp}.onrender.com/stats

IMPORTANT CREDENTIALS
====================
API Key: {api_key}
Neo4j Password: {neo4j_pass}

These are saved in: deployment_info.json
""")
        
        print("\n" + "="*60)
        print("✅ SETUP COMPLETE")
        print("="*60)
        print("\nNext step: Push to GitHub and deploy via Render dashboard")
        
        return True

def main():
    deployer = DirectRenderDeployer(RENDER_API_KEY)
    success = deployer.deploy()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
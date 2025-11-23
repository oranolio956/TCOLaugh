#!/usr/bin/env python3
"""
Script to update Render service to use main.py with proper CORS configuration
"""

import requests
import json
import sys

RENDER_API_KEY = "rnd_rmhLllGMj9OYUVzWjCdiTEF4pglh"
SERVICE_ID = "srv-d4h30a3uibrs73dbtiig"

def update_env_vars():
    """Add CORS environment variable"""
    url = f"https://api.render.com/v1/services/{SERVICE_ID}/env-vars"
    headers = {
        "Authorization": f"Bearer {RENDER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Check existing env vars
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to get env vars: {response.text}")
        return False
    
    existing_vars = response.json()
    
    # Check if CORS origins already exists
    cors_exists = any(var['envVar']['key'] == 'PANOPTICON_CORS_ORIGINS' for var in existing_vars)
    
    if not cors_exists:
        # Add CORS origins
        new_var = [{
            "key": "PANOPTICON_CORS_ORIGINS",
            "value": "https://tco-laugh.vercel.app,https://tcolaugh.vercel.app,https://panopticon-dashboard.vercel.app"
        }]
        
        response = requests.post(url, headers=headers, json=new_var)
        if response.status_code in [200, 201]:
            print("✅ Added PANOPTICON_CORS_ORIGINS environment variable")
        else:
            print(f"Failed to add CORS env var: {response.text}")
            return False
    else:
        print("✅ CORS environment variable already exists")
    
    return True

def trigger_deployment():
    """Trigger a new deployment"""
    url = f"https://api.render.com/v1/services/{SERVICE_ID}/deploys"
    headers = {
        "Authorization": f"Bearer {RENDER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Trigger deployment with clear cache
    data = {"clearCache": "clear"}
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code in [200, 201]:
        deploy_data = response.json()
        print(f"✅ Deployment triggered: {deploy_data.get('id', 'unknown')}")
        return True
    else:
        print(f"Failed to trigger deployment: {response.text}")
        return False

def main():
    print("🚀 Updating Render service to use main.py with proper CORS...")
    print("\n📝 Note: Build and start commands must be updated via Render Dashboard:")
    print("   Build: pip install -r requirements.txt && python -m spacy download en_core_web_sm || true")
    print("   Start: uvicorn panopticon.api.main:app --host 0.0.0.0 --port $PORT")
    print("\n1️⃣ Adding CORS environment variable...")
    
    if not update_env_vars():
        print("❌ Failed to update environment variables")
        sys.exit(1)
    
    print("\n2️⃣ Triggering new deployment...")
    if trigger_deployment():
        print("\n✅ Deployment initiated successfully!")
        print("📊 Monitor at: https://dashboard.render.com/web/srv-d4h30a3uibrs73dbtiig")
        print("\n⏳ Deployment usually takes 2-5 minutes")
        print("🌐 Once deployed, test at: https://tco-laugh.vercel.app")
    else:
        print("❌ Failed to trigger deployment")
        sys.exit(1)

if __name__ == "__main__":
    main()
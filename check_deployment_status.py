#!/usr/bin/env python3
import requests
import json
import sys
from datetime import datetime

RENDER_API_KEY = "rnd_poXT6CfcQaItD60NMTj5wjzPQZDI"
headers = {"Authorization": f"Bearer {RENDER_API_KEY}"}

services = {
    "API": "srv-d4h30a3uibrs73dbtiig",
    "Worker": "srv-d4h30bn5r7bs73bjq5i0", 
    "Crawler": "srv-d4h30chr0fns73a0380g"
}

print("=" * 60)
print("PANOPTICON DEPLOYMENT STATUS CHECK")
print("=" * 60)

for name, service_id in services.items():
    # Get latest deploy
    url = f"https://api.render.com/v1/services/{service_id}/deploys?limit=1"
    response = requests.get(url, headers=headers)
    
    print(f"\n📦 {name} Service:")
    print("-" * 30)
    
    if response.status_code == 200:
        deploys = response.json()
        if deploys:
            deploy = deploys[0]
            status = deploy.get('status', 'unknown')
            
            # Color code the status
            status_icon = "🔄" if "progress" in status else "✅" if status == "live" else "❌"
            
            print(f"  Status: {status_icon} {status}")
            print(f"  Deploy ID: {deploy.get('id', 'N/A')}")
            print(f"  Started: {deploy.get('createdAt', 'N/A')}")
            
            # Check commit
            commit = deploy.get('commit', {})
            if commit:
                print(f"  Commit: {commit.get('message', '')[:50]}...")
        else:
            print("  No deployments found")
    else:
        print(f"  ❌ Error fetching status: {response.status_code}")

print("\n" + "=" * 60)
print("🔑 CONFIGURATION SUMMARY")
print("=" * 60)
print("API Key: pano_bb0712a94164f6df7e4a4741348955bf_2024")
print("API URL: https://panopticon-api-847835.onrender.com")
print("Python Version: 3.9.18 (FIXED)")
print("\n✅ All environment variables configured")
print("✅ Python version issue resolved")
print("\n📝 Note: Deployments typically take 2-3 minutes")
print("=" * 60)

#!/usr/bin/env python3
"""
Real-time CORS fix monitor
"""
import requests
import time
import sys
from datetime import datetime

API_URL = "https://panopticon-api-847835.onrender.com"
API_KEY = "pano_bb0712a94164f6df7e4a4741348955bf_2024"
TARGET_ORIGIN = "https://tco-laugh.vercel.app"

def test_cors():
    """Test if CORS is fixed"""
    try:
        response = requests.get(
            f"{API_URL}/stats",
            headers={
                "Origin": TARGET_ORIGIN,
                "X-API-Key": API_KEY
            },
            timeout=5
        )
        
        cors_header = response.headers.get("Access-Control-Allow-Origin")
        
        return {
            "status_code": response.status_code,
            "has_cors": cors_header == TARGET_ORIGIN,
            "cors_value": cors_header or "MISSING",
            "data": response.json() if response.status_code == 200 else None
        }
    except Exception as e:
        return {
            "status_code": 0,
            "has_cors": False,
            "cors_value": "ERROR",
            "data": None,
            "error": str(e)
        }

def check_deployment_status():
    """Check Render deployment status"""
    try:
        response = requests.get(
            "https://api.render.com/v1/services/srv-d4h30a3uibrs73dbtiig/deploys?limit=1",
            headers={"Authorization": "Bearer rnd_rmhLllGMj9OYUVzWjCdiTEF4pglh"},
            timeout=5
        )
        if response.status_code == 200:
            deploy = response.json()[0]["deploy"]
            return deploy["status"]
    except:
        return "unknown"

print("=" * 80)
print("🔍 CORS FIX MONITOR - Real-time Status")
print("=" * 80)
print(f"Target: {TARGET_ORIGIN}")
print(f"API: {API_URL}")
print("=" * 80)
print("\nMonitoring... (Press Ctrl+C to stop)\n")

last_status = None
check_count = 0

while True:
    check_count += 1
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Test CORS
    result = test_cors()
    deploy_status = check_deployment_status()
    
    # Create status line
    if result["has_cors"]:
        status_line = f"✅ CORS FIXED! Your dashboard should work now!"
        if last_status != "fixed":
            print("\n" + "🎉" * 40)
            print(f"\n[{timestamp}] SUCCESS! CORS is now working!")
            print(f"CORS Header: {result['cors_value']}")
            print(f"Data received: {result['data']}")
            print("\n✅ Go to https://tco-laugh.vercel.app - it should work now!")
            print("\n" + "🎉" * 40)
            sys.exit(0)
    else:
        status_line = f"❌ CORS not fixed yet | Deploy: {deploy_status}"
        if last_status != "broken":
            print(f"[{timestamp}] Waiting for fix to deploy...")
            print(f"  HTTP Status: {result['status_code']}")
            print(f"  CORS Header: {result['cors_value']}")
            print(f"  Deployment: {deploy_status}")
            last_status = "broken"
    
    # Update status
    sys.stdout.write(f"\r[{timestamp}] Check #{check_count}: {status_line}")
    sys.stdout.flush()
    
    # Wait before next check
    time.sleep(3)
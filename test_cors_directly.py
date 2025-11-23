#!/usr/bin/env python3
"""
Direct test of CORS issue
"""
import requests
import json

API_URL = "https://panopticon-api-847835.onrender.com"
API_KEY = "pano_bb0712a94164f6df7e4a4741348955bf_2024"

print("=" * 80)
print("COMPREHENSIVE CORS ANALYSIS")
print("=" * 80)

# Test 1: Basic connectivity
print("\n1. Testing basic connectivity...")
try:
    response = requests.get(f"{API_URL}/")
    print(f"   ✓ API is reachable: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ✗ API unreachable: {e}")

# Test 2: Check which endpoints exist
print("\n2. Checking available endpoints...")
endpoints = ["/health", "/test", "/stats"]
for endpoint in endpoints:
    try:
        response = requests.get(f"{API_URL}{endpoint}", 
                               headers={"X-API-Key": API_KEY})
        print(f"   {endpoint}: {response.status_code} - {'EXISTS' if response.status_code != 404 else 'NOT FOUND'}")
    except:
        print(f"   {endpoint}: ERROR")

# Test 3: Test CORS headers with different origins
print("\n3. Testing CORS headers with different origins...")
test_origins = [
    "https://tco-laugh.vercel.app",
    "https://workspace-alpha-five.vercel.app",
    "http://localhost:3000"
]

for origin in test_origins:
    print(f"\n   Testing origin: {origin}")
    response = requests.get(
        f"{API_URL}/stats",
        headers={
            "Origin": origin,
            "X-API-Key": API_KEY
        }
    )
    
    cors_headers = {
        "Allow-Origin": response.headers.get("Access-Control-Allow-Origin", "MISSING"),
        "Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials", "MISSING"),
        "Allow-Methods": response.headers.get("Access-Control-Allow-Methods", "MISSING")
    }
    
    print(f"   Status: {response.status_code}")
    print(f"   CORS Headers:")
    for key, value in cors_headers.items():
        status = "✓" if value != "MISSING" else "✗"
        print(f"     {status} {key}: {value}")
    
    if cors_headers["Allow-Origin"] == "MISSING":
        print(f"     ⚠️  BROWSER WILL BLOCK THIS REQUEST!")

# Test 4: Check preflight
print("\n4. Testing OPTIONS preflight...")
response = requests.options(
    f"{API_URL}/stats",
    headers={
        "Origin": "https://tco-laugh.vercel.app",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "X-API-Key"
    }
)
print(f"   Preflight status: {response.status_code}")
print(f"   Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'MISSING')}")
print(f"   Allow-Headers: {response.headers.get('Access-Control-Allow-Headers', 'MISSING')}")

print("\n" + "=" * 80)
print("DIAGNOSIS:")
print("=" * 80)

# Final diagnosis
if "/test" in [e for e in endpoints if requests.get(f"{API_URL}{e}", headers={"X-API-Key": API_KEY}).status_code == 200]:
    print("✗ API is running simple_main.py (has /test endpoint)")
    print("  This version has HARDCODED CORS origins")
    
    # Check if tco-laugh is in the hardcoded list
    test_response = requests.get(
        f"{API_URL}/stats",
        headers={
            "Origin": "https://tco-laugh.vercel.app",
            "X-API-Key": API_KEY
        }
    )
    if not test_response.headers.get("Access-Control-Allow-Origin"):
        print("  ✗ tco-laugh.vercel.app is NOT in the allowed origins list")
        print("\nSOLUTION: The deployment with the fix needs to complete")
    else:
        print("  ✓ tco-laugh.vercel.app IS in the allowed origins list")
else:
    print("✓ API is running main.py (no /test endpoint)")
    print("  This version should use dynamic CORS from environment variables")

print("\n" + "=" * 80)
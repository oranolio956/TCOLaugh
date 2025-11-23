#!/usr/bin/env python3
"""
Monitor Render deployment progress
"""

import json
import os
import sys
import time
import requests
from typing import Dict, Any

# Configuration
def _require_env(var_name: str) -> str:
    value = os.environ.get(var_name)
    if not value:
        raise RuntimeError(f"Environment variable '{var_name}' must be set before running this script.")
    return value

RENDER_API_KEY = _require_env("RENDER_API_KEY")
RENDER_API_URL = "https://api.render.com/v1"

class DeploymentMonitor:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.service_ids = {
            "API": "srv-d4h30a3uibrs73dbtiig",
            "Worker": "srv-d4h30bn5r7bs73bjq5i0",
            "Crawler": "srv-d4h30chr0fns73a0380g"
        }
        
    def get_deploy_status(self, service_id: str) -> Dict[str, Any]:
        """Get latest deployment status for a service"""
        try:
            response = requests.get(
                f"{RENDER_API_URL}/services/{service_id}/deploys?limit=1",
                headers=self.headers
            )
            if response.status_code == 200:
                deploys = response.json()
                if deploys:
                    return deploys[0].get("deploy", {})
        except Exception as e:
            print(f"Error getting deploy status: {e}")
        return {}
    
    def get_logs(self, service_id: str, tail: int = 50) -> list:
        """Get recent logs for a service"""
        try:
            response = requests.get(
                f"{RENDER_API_URL}/services/{service_id}/logs",
                headers=self.headers,
                params={"tail": tail}
            )
            if response.status_code == 200:
                logs = response.text.strip()
                if logs:
                    return logs.split('\n')
        except:
            pass
        return []
    
    def monitor_once(self) -> Dict[str, str]:
        """Check status once"""
        statuses = {}
        
        for name, service_id in self.service_ids.items():
            deploy = self.get_deploy_status(service_id)
            status = deploy.get("status", "unknown")
            statuses[name] = status
            
        return statuses
    
    def monitor_continuous(self, interval: int = 30):
        """Monitor continuously"""
        print("="*60)
        print("🔄 CONTINUOUS DEPLOYMENT MONITOR")
        print("="*60)
        print("\nMonitoring services every 30 seconds...")
        print("Press Ctrl+C to stop\n")
        
        completed = set()
        failed = set()
        last_statuses = {}
        
        try:
            while True:
                statuses = self.monitor_once()
                changed = False
                
                # Check for status changes
                for name, status in statuses.items():
                    if last_statuses.get(name) != status:
                        changed = True
                        
                if changed:
                    print(f"\n⏰ Status Update @ {time.strftime('%H:%M:%S')}")
                    print("-" * 40)
                
                for name, status in statuses.items():
                    service_id = self.service_ids[name]
                    
                    # Only print if status changed
                    if last_statuses.get(name) != status:
                        if status == "build_in_progress":
                            print(f"🔨 {name}: Building...")
                        elif status == "deploy_in_progress":
                            print(f"🚀 {name}: Deploying...")
                        elif status == "live":
                            print(f"✅ {name}: LIVE!")
                            completed.add(name)
                        elif status == "build_failed":
                            print(f"❌ {name}: BUILD FAILED")
                            failed.add(name)
                            # Get error logs
                            logs = self.get_logs(service_id, 30)
                            if logs:
                                print(f"   Error logs:")
                                for log in logs[-10:]:
                                    if "error" in log.lower() or "failed" in log.lower():
                                        print(f"     {log}")
                        elif status == "deactivated":
                            print(f"⚠️ {name}: Deactivated")
                        else:
                            print(f"❓ {name}: {status}")
                
                last_statuses = statuses
                
                # Check if all are complete
                if len(completed) == len(self.service_ids):
                    print("\n" + "="*60)
                    print("✅ ALL SERVICES DEPLOYED SUCCESSFULLY!")
                    print("="*60)
                    
                    # Print access info
                    print("\n📋 Access Information:")
                    print("  API URL: https://<your-render-api-url>")
                    print("  API Key: <retrieved securely from Render/Vault>")
                    print("\n  Test command:")
                    print("  curl -H \"X-API-Key: $PANOPTICON_API_KEY\" \\")
                    print("       https://<your-render-api-url>/stats")
                    break
                
                # Check if any failed
                if failed:
                    print(f"\n⚠️ {len(failed)} service(s) failed to deploy")
                    print("Check logs at: https://dashboard.render.com")
                    
                    # Ask if should continue
                    print("\nFetching detailed error logs...")
                    for name in failed:
                        service_id = self.service_ids[name]
                        logs = self.get_logs(service_id, 100)
                        if logs:
                            print(f"\n{name} recent logs:")
                            for log in logs[-20:]:
                                print(f"  {log}")
                    
                    # Continue monitoring to see if it recovers
                    failed.clear()
                
                # Sleep only if not all complete
                if len(completed) < len(self.service_ids):
                    time.sleep(interval)
                    
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user")
            
            # Final status
            print("\nFinal Status:")
            for name, status in last_statuses.items():
                print(f"  {name}: {status}")

def main():
    monitor = DeploymentMonitor(RENDER_API_KEY)
    
    print("Starting deployment monitor...")
    print("\nInitial Status:")
    
    statuses = monitor.monitor_once()
    for name, status in statuses.items():
        print(f"  {name}: {status}")
    
    # Start continuous monitoring
    monitor.monitor_continuous()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
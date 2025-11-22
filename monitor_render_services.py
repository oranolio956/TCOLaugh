#!/usr/bin/env python3
"""
Monitor and manage Render services
"""

import json
import os
import sys
import time
import requests
from typing import Dict, List, Any

# Configuration
RENDER_API_KEY = os.environ.get("RENDER_API_KEY", "rnd_MBBJ6LlNi410654cpxpNUHGKnwRS")
RENDER_API_URL = "https://api.render.com/v1"

class RenderMonitor:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    def list_services(self) -> List[Dict[str, Any]]:
        """List all services"""
        try:
            response = requests.get(f"{RENDER_API_URL}/services", headers=self.headers)
            if response.status_code == 200:
                services = response.json()
                return services
        except Exception as e:
            print(f"Error listing services: {e}")
        return []
    
    def get_service_details(self, service_id: str) -> Dict[str, Any]:
        """Get detailed info about a service"""
        try:
            response = requests.get(f"{RENDER_API_URL}/services/{service_id}", headers=self.headers)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error getting service {service_id}: {e}")
        return {}
    
    def get_service_logs(self, service_id: str, tail: int = 100) -> str:
        """Get service logs"""
        try:
            response = requests.get(
                f"{RENDER_API_URL}/services/{service_id}/logs",
                headers=self.headers,
                params={"tail": tail}
            )
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(f"Error getting logs for {service_id}: {e}")
        return ""
    
    def trigger_deploy(self, service_id: str) -> bool:
        """Trigger a new deployment for a service"""
        try:
            response = requests.post(
                f"{RENDER_API_URL}/services/{service_id}/deploys",
                headers=self.headers,
                json={"clearCache": False}
            )
            if response.status_code in [200, 201]:
                deploy = response.json()
                print(f"✓ Deployment triggered: {deploy.get('id')}")
                return True
        except Exception as e:
            print(f"Error triggering deploy for {service_id}: {e}")
        return False
    
    def get_deploy_status(self, service_id: str, deploy_id: str) -> str:
        """Get deployment status"""
        try:
            response = requests.get(
                f"{RENDER_API_URL}/services/{service_id}/deploys/{deploy_id}",
                headers=self.headers
            )
            if response.status_code == 200:
                deploy = response.json()
                return deploy.get("status", "unknown")
        except Exception as e:
            print(f"Error getting deploy status: {e}")
        return "error"
    
    def monitor_all_services(self):
        """Monitor all services and their status"""
        print("="*60)
        print("📊 RENDER SERVICES MONITOR")
        print("="*60)
        print()
        
        services = self.list_services()
        
        if not services:
            print("⚠ No services found")
            return
        
        panopticon_services = []
        other_services = []
        
        for service in services:
            service_data = service.get("service", {})
            name = service_data.get("name", "Unknown")
            if "panopticon" in name.lower():
                panopticon_services.append(service_data)
            else:
                other_services.append(service_data)
        
        if panopticon_services:
            print(f"Found {len(panopticon_services)} Panopticon service(s):\n")
            
            for service in panopticon_services:
                service_id = service.get("id")
                name = service.get("name")
                service_type = service.get("type")
                status = service.get("suspended", "unknown")
                created = service.get("createdAt", "")
                
                print(f"📦 Service: {name}")
                print(f"   ID: {service_id}")
                print(f"   Type: {service_type}")
                print(f"   Created: {created}")
                print(f"   Suspended: {status}")
                
                # Get more details
                details = self.get_service_details(service_id)
                if details:
                    service_detail = details.get("service", {})
                    
                    # Check deployment status
                    if service_type == "web_service":
                        url = service_detail.get("serviceDetails", {}).get("url", "")
                        if url:
                            print(f"   URL: https://{url}")
                    
                    # Check latest deploy
                    deploys_response = requests.get(
                        f"{RENDER_API_URL}/services/{service_id}/deploys?limit=1",
                        headers=self.headers
                    )
                    if deploys_response.status_code == 200:
                        deploys = deploys_response.json()
                        if deploys:
                            latest_deploy = deploys[0].get("deploy", {})
                            deploy_status = latest_deploy.get("status", "unknown")
                            deploy_id = latest_deploy.get("id", "")
                            print(f"   Latest Deploy: {deploy_status} ({deploy_id})")
                            
                            if deploy_status == "build_failed":
                                print("   ⚠ Build failed! Checking logs...")
                                # Get logs
                                logs = self.get_service_logs(service_id, tail=50)
                                if logs:
                                    print("   Recent logs:")
                                    for line in logs.split('\n')[-10:]:
                                        if line.strip():
                                            print(f"     {line}")
                
                print()
        
        if other_services:
            print(f"\nOther services ({len(other_services)}):")
            for service in other_services:
                print(f"  - {service.get('name')} ({service.get('type')})")
        
        print("\n" + "="*60)
        return panopticon_services
    
    def create_services_from_blueprint(self):
        """Create services if they don't exist"""
        print("\n🚀 Checking if services need to be created...")
        
        # Check if we have the deployment info
        if not os.path.exists("/workspace/deployment_info.json"):
            print("⚠ deployment_info.json not found")
            return False
        
        with open("/workspace/deployment_info.json", "r") as f:
            deployment_info = json.load(f)
        
        # Check existing services
        services = self.list_services()
        existing_names = [s.get("service", {}).get("name", "") for s in services]
        
        needed_services = deployment_info.get("services", {})
        
        for service_type, service_name in needed_services.items():
            if service_name not in existing_names:
                print(f"\n⚠ Service {service_name} not found. Need to create via Render dashboard.")
                print("  Instructions:")
                print("  1. Go to https://dashboard.render.com/create")
                print("  2. Connect your GitHub repository")
                print("  3. Use the configuration from render.yaml")
            else:
                print(f"✓ Service {service_name} exists")
        
        return True

def main():
    monitor = RenderMonitor(RENDER_API_KEY)
    
    # Monitor services
    services = monitor.monitor_all_services()
    
    # Check if we need to create services
    monitor.create_services_from_blueprint()
    
    if not services:
        print("\n⚠ No Panopticon services found on Render")
        print("\n📝 To deploy services:")
        print("1. Go to: https://dashboard.render.com/blueprints")
        print("2. Click 'New Blueprint Instance'")
        print("3. Connect your GitHub repository: https://github.com/oranolio956/TCOLaugh")
        print("4. Select the render.yaml file from the repository")
        print("5. Click 'Apply' to create all services")
        return 1
    
    # Check if any services need deployment
    need_deploy = False
    for service in services:
        service_id = service.get("id")
        
        # Check if service has a repo connected
        repo = service.get("repo")
        if not repo:
            print(f"\n⚠ Service {service.get('name')} has no repository connected!")
            print("  Connect it to: https://github.com/oranolio956/TCOLaugh")
            need_deploy = True
    
    if need_deploy:
        print("\n⚠ Some services need repository connection or deployment")
        print("Please connect repositories in Render dashboard first")
    else:
        print("\n✅ All services are configured and monitored")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
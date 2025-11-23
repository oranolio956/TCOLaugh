import os
import logging
import re
from typing import Dict, List, Any, Optional
from panopticon.persistence.sqlite_manager import db_instance

logger = logging.getLogger(__name__)

class StealerLogParser:
    """
    Parses 'Stealer Logs' (RedLine, Raccoon, etc.) and ingests them into the Graph.
    """
    
    def process_log_directory(self, log_dir_path: str, infection_id: str = None):
        """
        Reads a directory containing 'system_info.txt', 'passwords.txt', etc.
        """
        if not infection_id:
            infection_id = os.path.basename(log_dir_path)

        system_info = self._parse_system_info(os.path.join(log_dir_path, "system_info.txt"))
        passwords = self._parse_passwords(os.path.join(log_dir_path, "passwords.txt"))
        
        # Ingest to Graph
        self._ingest_graph(infection_id, system_info, passwords)
        
        return {
            "infection_id": infection_id,
            "system": system_info,
            "credential_count": len(passwords)
        }

    def _parse_system_info(self, file_path: str) -> Dict[str, str]:
        info = {}
        if not os.path.exists(file_path):
            return info
            
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                
            # Regex patterns for common stealer formats
            ip_match = re.search(r"IP:\s*([\d\.]+)", content)
            user_match = re.search(r"User:\s*([^\n]+)", content) # Often format is ComputerName/User
            hwid_match = re.search(r"HWID:\s*([A-F0-9]+)", content)
            os_match = re.search(r"System:\s*([^\n]+)", content)
            
            if ip_match: info["ip"] = ip_match.group(1).strip()
            if user_match: info["user"] = user_match.group(1).strip()
            if hwid_match: info["hwid"] = hwid_match.group(1).strip()
            if os_match: info["os"] = os_match.group(1).strip()
            
        except Exception as e:
            logger.error(f"Failed to parse system_info: {e}")
            
        return info

    def _parse_passwords(self, file_path: str) -> List[Dict[str, str]]:
        creds = []
        if not os.path.exists(file_path):
            return creds
            
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                # RedLine format is often:
                # URL: ...
                # Username: ...
                # Password: ...
                # ===
                
                entry = {}
                for line in f:
                    line = line.strip()
                    if line.startswith("URL:"):
                        entry["url"] = line[4:].strip()
                    elif line.startswith("Username:") or line.startswith("USER:"):
                        entry["username"] = line.split(":", 1)[1].strip()
                    elif line.startswith("Password:") or line.startswith("PASS:"):
                        entry["password"] = line.split(":", 1)[1].strip()
                    elif line == "===" or line.startswith("---"):
                        if entry.get("url") and entry.get("username"):
                            creds.append(entry)
                        entry = {}
                # Catch last one
                if entry.get("url") and entry.get("username"):
                    creds.append(entry)
                    
        except Exception as e:
            logger.error(f"Failed to parse passwords.txt: {e}")
            
        return creds

    def _ingest_graph(self, infection_id: str, system_info: Dict[str, str], credentials: List[Dict[str, str]]):
        """
        Builds the graph nodes and edges.
        Structure:
          Infection (Node) -> INFECTED -> Machine (Node)
          Machine -> LOCATED_AT -> IPAddress (Node)
          Identity (Node) -> LOGGED_IN_ON -> Machine
          Identity -> HAS_ACCOUNT -> Site (Node)
        """
        
        # 1. Create Machine/Infection Nodes
        machine_uid = f"machine:{system_info.get('hwid') or infection_id}"
        db_instance.add_node(machine_uid, "Machine", {
            "os": system_info.get("os"),
            "hwid": system_info.get("hwid"),
            "pc_user": system_info.get("user")
        })
        
        # 2. IP Linkage
        if system_info.get("ip"):
            ip_uid = f"ip:{system_info['ip']}"
            db_instance.add_node(ip_uid, "IPAddress", {"val": system_info['ip']})
            db_instance.add_edge(machine_uid, ip_uid, "LOCATED_AT", {"timestamp": "now"}) # Should use real TS

        # 3. Process Credentials
        for cred in credentials:
            email_or_user = cred.get("username")
            password = cred.get("password")
            url = cred.get("url")
            
            if not email_or_user or not url:
                continue

            # Identify if it's an email or just a username
            is_email = "@" in email_or_user
            user_uid = f"email:{email_or_user}" if is_email else f"user:{email_or_user}"
            user_type = "Email" if is_email else "Identity"
            
            # Create User Node
            db_instance.add_node(user_uid, user_type, {"val": email_or_user})
            
            # Link User -> Machine (Evidence of compromise)
            db_instance.add_edge(user_uid, machine_uid, "COMPROMISED_BY", {"infection_id": infection_id})
            
            # Password Pivot (Store Hash)
            if password:
                # We store HASH only for analysis
                import hashlib
                p_hash = hashlib.sha256(password.encode()).hexdigest()
                hash_uid = f"hash:{p_hash}"
                db_instance.add_node(hash_uid, "PasswordHash", {"val": p_hash}) # In real world, maybe partial hash
                db_instance.add_edge(user_uid, hash_uid, "USED_PASSWORD")
                
                # If we want to be aggressive (as per report):
                # Link Hash -> Machine? Or just keep it on User. 
                
            # Site Linkage
            # extracting domain from url
            try:
                from urllib.parse import urlparse
                domain = urlparse(url).netloc
                if domain:
                    site_uid = f"site:{domain}"
                    db_instance.add_node(site_uid, "Site", {"domain": domain})
                    db_instance.add_edge(user_uid, site_uid, "HAS_ACCOUNT", {"url": url})
            except:
                pass

logger.info("StealerLogParser initialized.")

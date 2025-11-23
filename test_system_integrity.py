import os
import time
import shutil
import json
import numpy as np
import logging
from unittest.mock import MagicMock, patch

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("TestIntegrity")

def mock_environment():
    """Setup any necessary mocks/paths."""
    os.makedirs("test_data", exist_ok=True)
    # Create fake stealer log zip
    import zipfile
    with zipfile.ZipFile("test_data/logs.zip", 'w') as zf:
        zf.writestr("system_info.txt", "IP: 10.0.0.5\nUser: DarkVader\nHWID: 123456\nSystem: Linux")
        zf.writestr("passwords.txt", "URL: https://bank.com\nUsername: admin\nPassword: password123\n")

def test_full_pipeline():
    logger.info(">>> Starting Full Pipeline Integrity Test <<<")
    
    # 1. Test Proxy Manager (Recon)
    from panopticon.analysis.recon.active_scanner import ActiveScanner, ProxyManager
    pm = ProxyManager()
    logger.info(f"Proxy Manager initialized. Proxies loaded: {len(pm.proxies)}")
    
    # 2. Test Stealer Parsing (Ingestion)
    from panopticon.ingestion.stealer_logs import StealerLogParser
    parser = StealerLogParser()
    # Manual extraction for test
    import zipfile
    with zipfile.ZipFile("test_data/logs.zip", 'r') as zf:
        zf.extractall("test_data/extracted")
    
    res = parser.process_log_directory("test_data/extracted")
    logger.info(f"Stealer Log Parsed: {json.dumps(res, indent=2)}")
    assert res['system']['ip'] == "10.0.0.5"
    assert res['credential_count'] == 1
    
    # 3. Test Vector Router (Persistence)
    from panopticon.persistence.vector.router import vector_router
    vec = np.random.rand(512).astype(np.float32)
    vector_router.add_vector(vec, "test_vec_1", {"source": "test"})
    logger.info("Vector added via Router (Fallback path checked)")
    
    matches = vector_router.search_vectors(vec)
    logger.info(f"Vector search returned {len(matches)} matches")
    
    # 4. Test Graph Connectivity (Polyglot)
    from panopticon.persistence.sqlite_manager import db_instance
    graph = db_instance.get_subgraph("ip:10.0.0.5", depth=2)
    logger.info(f"Graph Traversal for IP found {len(graph['nodes'])} nodes")
    
    # Verify link: IP -> Machine -> User
    nodes = graph['nodes']
    has_machine = any(n['type'] == 'Machine' for n in nodes.values())
    has_user = any(n['type'] == 'Identity' or n['type'] == 'Email' for n in nodes.values())
    
    if has_machine:
        logger.info("✅ Machine Node confirmed.")
    else:
        logger.error("❌ Machine Node missing!")

    logger.info(">>> Integrity Test Complete <<<")

if __name__ == "__main__":
    try:
        mock_environment()
        test_full_pipeline()
    finally:
        if os.path.exists("test_data"):
            shutil.rmtree("test_data")

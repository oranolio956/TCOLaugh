import asyncio
import uuid

import pytest

from panopticon.persistence import sqlite_manager


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def isolated_store(monkeypatch, tmp_path):
    tmp_db = tmp_path / "polyglot.db"
    store = sqlite_manager.PolyglotStore(db_path=str(tmp_db))
    monkeypatch.setattr(sqlite_manager, "db_instance", store)

    import panopticon.ingestion.kafka_interface as kafka_module

    monkeypatch.setattr(kafka_module, "db_instance", store)
    monkeypatch.setenv("PANOPTICON_USE_KAFKA", "false")
    return store


def test_ingestion_producer_populates_graph(isolated_store):
    from panopticon.ingestion.kafka_interface import IngestionProducer

    producer = IngestionProducer(["localhost:9092"], "raw_ingestion")
    assert producer.use_kafka is False

    username = f"user_{uuid.uuid4().hex[:6]}"
    name = "Test User"
    record = {
        "source_type": "surface_web",
        "url": "https://example.com",
        "raw_data": {"name": name, "username": username, "bio": "Example"},
        "timestamp": 123.0,
    }

    producer.send_record(record)

    docs = isolated_store.search_documents("username", username)
    assert docs and docs[0]["raw_data"]["username"] == username

    graph = isolated_store.get_subgraph(f"user:{username}", depth=1)
    assert f"name:{name}" in graph["nodes"]


@pytest.mark.anyio("asyncio")
async def test_active_scanner_runs_concurrently(monkeypatch):
    from panopticon.analysis.recon.active_scanner import ActiveScanner

    scanner = ActiveScanner()
    scanner.sites = {
        "SiteA": "https://a.example/{0}",
        "SiteB": "https://b.example/{0}",
    }

    async def fake_fetch(self, client, site, url, label):
        await asyncio.sleep(0)
        return {"site": site, "url": url, "status": "found"}

    monkeypatch.setattr(ActiveScanner, "_fetch_site", fake_fetch, raising=True)

    results = await scanner.check_username("demo")
    assert {entry["site"] for entry in results} == {"SiteA", "SiteB"}

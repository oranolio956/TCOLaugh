import pytest
from unittest.mock import MagicMock, patch
from panopticon.ingestion.tor.crawler import TorCrawler
from panopticon.analysis.narrative.graph_rag import GraphNarrator
from panopticon.analysis.crypto.tracer import CryptoTracer

def test_tor_crawler_no_proxy():
    """Test TorCrawler behavior when SOCKS5 proxy is missing."""
    crawler = TorCrawler(proxy_url="socks5h://invalid_host:9999")
    assert crawler.check_connection() == False
    # Ensure it handles the connection error gracefully without crashing
    result = crawler.crawl_hidden_service("http://darkmarket.onion")
    assert result["status"] == "failed"

def test_graph_narrator_no_api_key():
    """Test Narrator behavior when API Key is invalid/missing."""
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': ''}):
        narrator = GraphNarrator()
        # Should handle missing key gracefully
        result = narrator.generate_briefing("Target", {}, {})
        assert "API Key missing" in result

def test_graph_narrator_api_error():
    """Test Narrator behavior when Anthropic API fails (500/Rate Limit)."""
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'fake_key'}):
        narrator = GraphNarrator()
        # Mock the client to raise an exception
        narrator.client = MagicMock()
        narrator.client.messages.create.side_effect = Exception("API Overloaded")
        
        result = narrator.generate_briefing("Target", {}, {})
        assert "Error generating" in result

def test_crypto_tracer_timeout():
    """Test Crypto Tracer when external explorer times out."""
    tracer = CryptoTracer()
    # Mock requests.get to timeout
    with patch('requests.get', side_effect=Exception("Timeout")):
        result = tracer.trace_address("BTC", "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
        assert result == {} # Should return empty dict, not crash

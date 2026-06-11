"""
Tests for Clausely Real-Time RAG Search Client (realtime_rag.py).

Validates all three tiers: Google Custom Search, unauthenticated DuckDuckGo HTML parser,
and high-fidelity simulated judgments.
"""

from __future__ import annotations

import unittest
from unittest.mock import patch, MagicMock

from tools.realtime_rag import RealtimeRAGClient


class TestRealtimeRAGClient(unittest.TestCase):
    """Unit tests verifying all three search tiers of RealtimeRAGClient."""

    def setUp(self):
        # Initialize client with mock credentials
        self.client = RealtimeRAGClient(google_search_key="mock_google_key", cx_id="mock_cx_id")

    @patch("httpx.Client")
    def test_tier1_google_custom_search_success(self, mock_client_class):
        """Verify Tier 1 (Google CSE API) successfully makes query and formats results."""
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        # Mock Google API JSON response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "title": "Rajesh Kumar v. Amit Verma Judgment",
                    "link": "https://indiankanoon.org/doc/12345678/",
                    "snippet": "Cheating and contractual payment defaults under BNS Section 318(4)."
                }
            ]
        }
        mock_client.get.return_value = mock_response

        # Execute search
        results = self.client.fetch_yesterdays_case_info("BNS 318 cheating")

        # Assertions
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Rajesh Kumar v. Amit Verma Judgment")
        self.assertEqual(results[0]["source"], "Google Custom Search (Credentials)")
        self.assertEqual(results[0]["url"], "https://indiankanoon.org/doc/12345678/")
        self.assertEqual(results[0]["document_id"], "G-12345678")
        
        # Verify Google API parameters were set correctly
        mock_client.get.assert_called_once()
        args, kwargs = mock_client.get.call_args
        params = kwargs.get("params", {})
        self.assertEqual(params["key"], "mock_google_key")
        self.assertEqual(params["cx"], "mock_cx_id")
        self.assertEqual(params["dateRestrict"], "d1")  # Restricts to last 24 hours (yesterday)

    @patch("httpx.Client")
    def test_tier2_unauthenticated_duckduckgo_parsing(self, mock_client_class):
        """Verify Tier 2 (Unauthenticated DuckDuckGo scraper) parses links, titles, and snippets correctly using regex."""
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client

        # Mock DuckDuckGo HTML response
        mock_html = """
        <html>
        <body>
            <div class="result__body">
                <a class="result__url" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Flivelaw.in%2Fpdf-case-12345%2F">Rajesh Sharma v. State of Maharashtra</a>
                <a class="result__snippet" href="#">High Court Bench rules on BNS 318 cheating and fraudulent intent yesterday.</a>
            </div>
            <div class="result__body">
                <a class="result__url" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fbarandbench.com%2Fsupreme-court-bsa-61%2F">Supreme Court electronic certificate verification ratio decidendi</a>
                <a class="result__snippet" href="#">BSA Section 61 evidence certificate mandatory under new laws.</a>
            </div>
        </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_client.post.return_value = mock_response

        # Execute unauthenticated search directly
        results = self.client.fetch_unauthenticated_search("BNS 318")

        # Assertions
        self.assertEqual(len(results), 2)
        
        # Verify First Result
        self.assertEqual(results[0]["title"], "Rajesh Sharma v. State of Maharashtra")
        self.assertEqual(results[0]["source"], "Public Web Search (Unauthenticated)")
        self.assertEqual(results[0]["url"], "https://livelaw.in/pdf-case-12345/")
        self.assertIn("High Court Bench", results[0]["snippet"])
        self.assertTrue(results[0]["document_id"].startswith("WEB-0-"))

        # Verify Second Result
        self.assertEqual(results[1]["title"], "Supreme Court electronic certificate verification ratio decidendi")
        self.assertEqual(results[1]["url"], "https://barandbench.com/supreme-court-bsa-61/")
        self.assertIn("BSA Section 61", results[1]["snippet"])
        self.assertTrue(results[1]["document_id"].startswith("WEB-1-"))

    @patch.dict("os.environ", {"GOOGLE_API_KEY": ""})
    def test_tier3_simulated_judgment_fallback(self):
        """Verify Tier 3 (High-fidelity simulated judgments) returns correct matches when offline or unsigned search fails."""
        # Initialize client with empty credentials to trigger mock fallback
        offline_client = RealtimeRAGClient(google_search_key="", cx_id="")
        
        # Test search query matching Rajesh Sharma
        results_sharma = offline_client.fetch_yesterdays_case_info("Nagpur Bench corporate cheating")
        self.assertEqual(len(results_sharma), 1)
        self.assertIn("Rajesh Sharma", results_sharma[0]["title"])
        self.assertIn("Section 318(4) BNS", results_sharma[0]["snippet"])
        self.assertEqual(results_sharma[0]["source"], "High Court of Bombay (Nagpur Bench) - Offline Sync")

        # Test search query matching Union of India
        results_uoi = offline_client.fetch_yesterdays_case_info("Supreme Court BSA electronic evidence")
        self.assertEqual(len(results_uoi), 1)
        self.assertIn("Union of India", results_uoi[0]["title"])
        self.assertIn("BSA Section 61", results_uoi[0]["snippet"])
        self.assertEqual(results_uoi[0]["source"], "Supreme Court of India - Offline Sync")

    @patch.dict("os.environ", {"GOOGLE_API_KEY": ""})
    def test_blacklist_filtering_and_cleansing(self):
        """Verify that blacklisted tokens are filtered out of search results and history files are cleansed."""
        session_state = {
            "blacklist_registry": ["bypass", "jailbreak"],
            "history_files": [
                {"content": "this has a bypass token in it"},
                {"content": "normal history text"}
            ]
        }
        client = RealtimeRAGClient(google_search_key="", cx_id="", session_state=session_state)
        
        # Override simulated cases and fetch_unauthenticated_search to return a result containing a blacklist token
        with patch.object(client, "fetch_unauthenticated_search", return_value=[]), \
             patch.object(client, "_simulate_yesterdays_case") as mock_simulate:
            mock_simulate.return_value = [
                {
                    "title": "Clean Case",
                    "source": "Mock Source",
                    "date": "2026-06-09",
                    "snippet": "This is a clean snippet without bad words",
                    "url": "https://example.com/1",
                    "document_id": "MOCK-1"
                },
                {
                    "title": "Dirty Case",
                    "source": "Mock Source",
                    "date": "2026-06-09",
                    "snippet": "This snippet has a bypass token in it",
                    "url": "https://example.com/2",
                    "document_id": "MOCK-2"
                }
            ]
            
            results = client.fetch_yesterdays_case_info("general query")
            
            # Assert only the clean case remains
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["title"], "Clean Case")
            
            # Assert history files have been cleansed of the blacklisted token
            cleaned_history = session_state["history_files"]
            self.assertEqual(cleaned_history[0]["content"], "this has a token in it")
            self.assertEqual(cleaned_history[1]["content"], "normal history text")
            self.assertEqual(session_state.get("purged_history_count"), 1)

    @patch.dict("os.environ", {"GOOGLE_API_KEY": ""})
    def test_munchausen_hallucination_gate_intercept(self):
        """Verify that a Munchausen name-resolution string in query triggers a ValueError."""
        client = RealtimeRAGClient(google_search_key="", cx_id="")
        
        with self.assertRaises(ValueError) as context:
            client.fetch_yesterdays_case_info("baron_munchausen case details")
        self.assertIn("Munchausen Hallucination Gate intercepted", str(context.exception))

        with self.assertRaises(ValueError) as context2:
            client.fetch_yesterdays_case_info("fictional_evidence case details")
        self.assertIn("Munchausen Hallucination Gate intercepted", str(context2.exception))


if __name__ == "__main__":
    unittest.main()


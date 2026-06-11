import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

from agents.acceptor import simulate_registry_check

class TestAcceptorPrecedents(unittest.TestCase):

    def setUp(self):
        # A standard valid petition body that meets other registry scrutiny parameters
        self.base_document = """
        IN THE COURT OF THE CIVIL JUDGE SENIOR DIVISION, NAGPUR
        
        IN THE MATTER OF:
        Rajesh Kumar                                    ... PETITIONER
        VERSUS
        Amit Verma                                      ... RESPONDENT
        
        STATEMENT OF FACTS
        This Hon'ble Court has the jurisdiction to try and entertain the present matter under Section 9 of the Code of Civil Procedure, 1908.
        
        PRAYER
        In the premises aforesaid, it is most respectfully prayed that this Hon'ble Court may be pleased to grant recovery of money.
        
        VERIFICATION
        I, Rajesh Kumar, the above-named deponent, do hereby verify that the contents of the above are true.
        
        DEPONENT
        Signed, Rajesh Kumar
        Advocate for Petitioner: Enrollment No. MAH/123/2020
        """

    @patch("pandas.read_parquet")
    @patch("tools.realtime_rag.RealtimeRAGClient.search_general")
    def test_valid_precedent_passes(self, mock_fetch, mock_read_parquet):
        """Verify that a document containing a verified precedent citation passes scrutiny."""
        doc_with_citation = self.base_document + "\nWe rely on the precedent Rajesh Sharma v. State of Maharashtra, citation (2014) 9 SCC 129."
        
        # Mock AWS Parquet return
        mock_read_parquet.return_value = pd.DataFrame([{
            "title": "Rajesh Sharma & Ors v. State of Maharashtra",
            "citation": "(2014) 9 SCC 129",
            "decision_date": "2014-08-13",
            "path": "data/pdf/2014_9_scc_129.pdf"
        }])

        # Mock Google CSE return
        mock_fetch.return_value = [{
            "title": "Rajesh Sharma v. State of Maharashtra",
            "source": "Google Custom Search (Credentials)",
            "date": "2014-08-13",
            "snippet": "Precedent on corporate defaults...",
            "url": "https://www.casemine.com/judgement/in/12345"
        }]

        result = simulate_registry_check(doc_with_citation, "MH-DISTRICT", "petition")
        
        # Verify it passed and contains no fatal double-verification errors
        self.assertTrue(result["would_be_accepted"])
        self.assertEqual(len(result["fatal_defects"]), 0)
        self.assertTrue(result["detailed_checks"]["precedents_verified"])

    @patch("pandas.read_parquet")
    @patch("tools.realtime_rag.RealtimeRAGClient.search_general")
    def test_fabricated_precedent_fails(self, mock_fetch, mock_read_parquet):
        """Verify that a document containing a hallucinated precedent citation fails scrutiny with a fatal defect."""
        doc_with_hallucination = self.base_document + "\nWe cite the fabricated case John Doe v. Jane Doe, citation (2025) 99 SCC 9999."
        
        # Mock empty returns for both lookups (Not found)
        mock_read_parquet.return_value = pd.DataFrame()
        mock_fetch.return_value = []

        result = simulate_registry_check(doc_with_hallucination, "MH-DISTRICT", "petition")
        
        # Scrutiny must fail because of the hallucinated precedent
        self.assertFalse(result["would_be_accepted"])
        self.assertGreater(len(result["fatal_defects"]), 0)
        
        # Verify the specific error message is present in the fatal defects list
        found_err = False
        for defect in result["fatal_defects"]:
            if "Double-Verification Failure" in defect:
                found_err = True
                break
        self.assertTrue(found_err, "Fabricated precedent should have triggered a Double-Verification Scrutiny Failure")
        self.assertFalse(result["detailed_checks"]["precedents_verified"])

if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

from tools.case_citation_verifier import PrecedentCitationVerifier

class TestPrecedentCitationVerifier(unittest.TestCase):
    
    def setUp(self):
        self.verifier = PrecedentCitationVerifier()

    def test_parse_citations_extracts_correctly(self):
        """Verify regex correctly parses citation format and case names."""
        sample_text = """
        The Petitioner cites Rajesh Sharma v. State of Maharashtra and relies on (2014) 9 SCC 129.
        We also refer to Vijay Singh versus State of Bihar and [2024] 10 S.C.R. 108.
        """
        cases = self.verifier.parse_citations(sample_text)
        
        # We expect 4 items: two citations, two case names
        self.assertEqual(len(cases), 4)
        
        # Verify citations
        citations = [c for c in cases if c["type"] == "citation"]
        self.assertEqual(len(citations), 2)
        self.assertEqual(citations[0]["year"], 2014)
        self.assertEqual(citations[0]["citation_query"], "(2014) 9 SCC 129")
        self.assertEqual(citations[1]["year"], 2024)
        self.assertEqual(citations[1]["citation_query"], "(2024) 10 SCR 108")
        
        # Verify case names
        names = [c for c in cases if c["type"] == "name"]
        self.assertEqual(len(names), 2)
        self.assertEqual(names[0]["case_name"], "Rajesh Sharma v. State of Maharashtra")
        self.assertEqual(names[1]["case_name"], "Vijay Singh v. State of Bihar")

    @patch("pandas.read_parquet")
    @patch("tools.realtime_rag.RealtimeRAGClient.search_general")
    def test_verify_case_success(self, mock_fetch, mock_read_parquet):
        """Verify successful double-verification when both AWS S3 and Google CSE find the case."""
        # 1. Mock AWS Parquet DataFrame return
        mock_df = pd.DataFrame([{
            "title": "Rajesh Sharma & Ors v. State of Maharashtra",
            "citation": "(2014) 9 SCC 129",
            "decision_date": "2014-08-13",
            "path": "data/pdf/2014_9_scc_129.pdf"
        }])
        mock_read_parquet.return_value = mock_df

        # 2. Mock Google CSE return
        mock_fetch.return_value = [{
            "title": "Rajesh Sharma v. State of Maharashtra",
            "source": "Google Custom Search (Credentials)",
            "date": "2014-08-13",
            "snippet": "Precedent on corporate defaults...",
            "url": "https://www.casemine.com/judgement/in/12345"
        }]

        case_ref = {
            "type": "citation",
            "year": 2014,
            "citation_query": "(2014) 9 SCC 129"
        }
        res = self.verifier.verify_case(case_ref)
        
        # Assertions
        self.assertTrue(res["aws_verified"])
        self.assertTrue(res["google_verified"])
        self.assertEqual(res["error_message"], "")

    @patch("pandas.read_parquet")
    @patch("tools.realtime_rag.RealtimeRAGClient.search_general")
    def test_verify_case_failure_aws(self, mock_fetch, mock_read_parquet):
        """Verify failure when AWS lookup fails but Google search succeeds."""
        # AWS returns empty DataFrame
        mock_read_parquet.return_value = pd.DataFrame()
        
        mock_fetch.return_value = [{
            "title": "Rajesh Sharma v. State of Maharashtra",
            "source": "Google Custom Search (Credentials)",
            "date": "2014-08-13",
            "snippet": "Precedent on corporate defaults...",
            "url": "https://livelaw.in/judgement/in/12345"
        }]

        case_ref = {
            "type": "citation",
            "year": 2014,
            "citation_query": "(2014) 9 SCC 129"
        }
        res = self.verifier.verify_case(case_ref)
        
        self.assertFalse(res["aws_verified"])
        self.assertTrue(res["google_verified"])
        self.assertIn("Double-Verification Failure", res["error_message"])
        self.assertIn("Not found in AWS S3", res["error_message"])

    @patch("pandas.read_parquet")
    @patch("tools.realtime_rag.RealtimeRAGClient.search_general")
    def test_verify_case_failure_both(self, mock_fetch, mock_read_parquet):
        """Verify failure when both lookups fail."""
        mock_read_parquet.return_value = pd.DataFrame()
        mock_fetch.return_value = []

        case_ref = {
            "type": "citation",
            "year": 2014,
            "citation_query": "(2014) 9 SCC 129"
        }
        res = self.verifier.verify_case(case_ref)
        
        self.assertFalse(res["aws_verified"])
        self.assertFalse(res["google_verified"])
        self.assertIn("Not found in AWS S3", res["error_message"])
        self.assertIn("Not found in Google CSE", res["error_message"])

    @patch("pandas.read_parquet")
    @patch("tools.realtime_rag.RealtimeRAGClient.search_general")
    def test_verify_case_ongoing_success(self, mock_fetch, mock_read_parquet):
        """Verify that an ongoing case missing from S3 but found on CaseMine/Google CSE successfully self-heals."""
        # AWS returns empty (no finalized judgment)
        mock_read_parquet.return_value = pd.DataFrame()
        
        # Google search returns a match indicating ongoing/pending matter
        mock_fetch.return_value = [{
            "title": "Vidya Khobrekar v. Union of India",
            "source": "Google Custom Search (General)",
            "date": "Historical",
            "snippet": "Transfer Petition (Civil) is pending, listed in cause list...",
            "url": "https://www.casemine.com/judgement/in/65b47a"
        }]

        case_ref = {
            "type": "name",
            "year": 2024,
            "case_name": "Vidya Khobrekar v. Union of India"
        }
        res = self.verifier.verify_case(case_ref)
        
        # Should self-heal as verified ongoing
        self.assertTrue(res["aws_verified"])
        self.assertTrue(res["google_verified"])
        self.assertEqual(res["error_message"], "")
        self.assertEqual(res["aws_details"]["citation"], "Ongoing Matter (Verified via Web)")

    def test_verify_litigant_spelling(self):
        """Verify litigant spelling match allows minor difference (>=70% overlap)."""
        self.assertTrue(self.verifier.verify_litigant_spelling("Rajesh Sharma v. State", "Rajesh Sharma v. State of Maharashtra"))
        self.assertFalse(self.verifier.verify_litigant_spelling("John Doe v. Smith", "Rajesh Sharma v. State of Maharashtra"))

    def test_map_alternative_reporter(self):
        """Verify alternative reporter mapping aligns SCC to AIR and SCR."""
        res = self.verifier.map_alternative_reporter("(2014) 9 SCC 129")
        self.assertTrue(res["aligned"])
        self.assertEqual(res["equivalents"]["air"], "AIR 2014 SC 2912")
        self.assertEqual(res["equivalents"]["scr"], "[2014] 8 S.C.R. 512")
        
        bad_res = self.verifier.map_alternative_reporter("1999 Dummy 123")
        self.assertFalse(bad_res["aligned"])

    def test_verify_cryptographic_attestation(self):
        """Verify digital signature checks and checksum tracking."""
        doc_signed = "This document is digitally signed by the Registrar of the Supreme Court."
        res = self.verifier.verify_cryptographic_attestation(doc_signed)
        self.assertTrue(res["verified"])
        self.assertTrue(res["signature_present"])
        
        doc_expired = "This is signed by the court but the certificate expired in 2025."
        res_expired = self.verifier.verify_cryptographic_attestation(doc_expired)
        self.assertFalse(res_expired["verified"])

    def test_initialize_citation_graph(self):
        """Verify forward and backward linkage graph generation and centrality scoring."""
        res = self.verifier.initialize_citation_graph("Rajesh Sharma v. State of Maharashtra")
        self.assertTrue(res["registered"])
        self.assertEqual(res["backward_links"], ["Sushil Kumar Sharma v. Union of India"])
        self.assertEqual(res["forward_links"], ["Preeti Gupta v. State of Jharkhand"])
        self.assertGreater(res["centrality_score"], 1.0)
        
        res_unregistered = self.verifier.initialize_citation_graph("Unknown Case v. Unknown State")
        self.assertFalse(res_unregistered["registered"])

    def test_calculate_precedent_score_success(self):
        """Verify score calculation for valid precedent case."""
        case_meta = {
            "court": "Supreme Court of India",
            "bench_size": 3,
            "constitution_bench": False,
            "pending_review": False,
            "consistently_followed": True,
            "dissenting_opinion": False,
            "publication_year": 2012,
            "active_provisions": ["Section 138 NI Act"]
        }
        res = self.verifier.calculate_precedent_score(case_meta)
        # 100 base + 0 + 0 + 100 + 0 + 30 = 230
        self.assertEqual(res["final_score"], 230)
        self.assertFalse(res["shadowbanned"])
        self.assertEqual(res["weight_reduction"], 1.0)

    def test_calculate_precedent_score_failure(self):
        """Verify score calculation raises ValueError if score < 100."""
        case_meta = {
            "court": "Supreme Court of India",
            "bench_size": 2,
            "constitution_bench": False,
            "pending_review": True, # -75 modifier
            "consistently_followed": False,
            "dissenting_opinion": False,
            "publication_year": 2018,
            "active_provisions": ["Section 302 IPC"]
        }
        # 100 base - 75 + 20 = 45 < 100 -> raises ValueError
        with self.assertRaises(ValueError):
            self.verifier.calculate_precedent_score(case_meta)

    def test_calculate_precedent_score_invalid_year(self):
        """Verify validation failure for invalid publication year."""
        case_meta = {
            "court": "Supreme Court of India",
            "bench_size": 2,
            "publication_year": 1940, # Out of 1950-2026 bounds
            "active_provisions": ["Section 138 NI Act"]
        }
        with self.assertRaises(ValueError):
            self.verifier.calculate_precedent_score(case_meta)

    def test_calculate_precedent_score_repealed_provision(self):
        """Verify validation failure for repealed legal provisions."""
        case_meta = {
            "court": "Supreme Court of India",
            "bench_size": 2,
            "publication_year": 2015,
            "active_provisions": ["Section 377 IPC"] # Repealed
        }
        with self.assertRaises(ValueError):
            self.verifier.calculate_precedent_score(case_meta)

    def test_verify_bench_strength_success(self):
        """Verify bench strength validation passes for binding authority."""
        case_meta = {
            "citation": "(2012) 3 SCC 400",
            "bench_size": 3,
            "judges": ["R.M. Lodha", "H.L. Gokhale", "Ranjan Gogoi"],
            "conflicting_precedent": None
        }
        res = self.verifier.verify_bench_strength(case_meta)
        self.assertEqual(res["category"], "Full")
        self.assertTrue(res["is_binding"])

    def test_verify_bench_strength_failure(self):
        """Verify bench strength raises NonBindingAuthorityError for lower bench size."""
        from tools.case_citation_verifier import NonBindingAuthorityError
        case_meta = {
            "citation": "(2015) 3 SCC 300",
            "bench_size": 2,
            "judges": ["A.K. Sikri", "Rohinton Fali Nariman"],
            "conflicting_precedent": "(2012) 3 SCC 400" # Conflicting full bench (3)
        }
        with self.assertRaises(NonBindingAuthorityError):
            self.verifier.verify_bench_strength(case_meta)

    def test_audit_overruling_history_success(self):
        """Verify overruling history audit for active case."""
        case_meta = {
            "citation": "(2014) 9 SCC 129",
            "overruled": False
        }
        res = self.verifier.audit_overruling_history(case_meta)
        self.assertEqual(res["active_status"], "ACTIVE")

    def test_audit_overruling_history_failure(self):
        """Verify overruling history audit raises PrecedentDeprecatedError if overruled on core point."""
        from tools.case_citation_verifier import PrecedentDeprecatedError
        case_meta = {
            "citation": "(2010) 1 SCC 100",
            "overruled": True,
            "overruled_by": "(2020) 5 SCC 200",
            "overruled_section": "Ratio on photocopy",
            "overruled_core": True,
            "publication_year": 2010,
            "overruling_year": 2020
        }
        with self.assertRaises(PrecedentDeprecatedError):
            self.verifier.audit_overruling_history(case_meta)

    def test_apply_regional_filter(self):
        """Verify regional applicability check returns correct weights."""
        case_meta = {
            "citation": "Bombay HC Case",
            "court_state": "Maharashtra"
        }
        
        # Incident state matches
        intake_match = {"incident_state": "Maharashtra"}
        res_match = self.verifier.apply_regional_filter(case_meta, intake_match)
        self.assertEqual(res_match["binding_weight"], 1.0)
        self.assertEqual(res_match["applicability"], "binding")
        
        # Incident state differs
        intake_diff = {"incident_state": "Delhi"}
        res_diff = self.verifier.apply_regional_filter(case_meta, intake_diff)
        self.assertEqual(res_diff["binding_weight"], 0.5)
        self.assertEqual(res_diff["applicability"], "persuasive")

    @patch("pandas.read_parquet")
    @patch("tools.realtime_rag.RealtimeRAGClient.search_general")
    def test_verify_case_stage2_overruled_failure(self, mock_fetch, mock_read_parquet):
        """Verify verify_case captures Stage 2 exceptions and fails gracefully."""
        mock_read_parquet.return_value = pd.DataFrame([{
            "title": "Overruled Case v. State",
            "citation": "(2010) 1 SCC 100",
            "decision_date": "2010-02-10",
            "path": "data/pdf/2010_1_scc_100.pdf"
        }])
        mock_fetch.return_value = [{
            "title": "Overruled Case v. State",
            "source": "Google CSE",
            "date": "2010-02-10",
            "snippet": "Overruled on core point...",
            "url": "https://casemine.com/123"
        }]
        
        case_ref = {
            "type": "citation",
            "year": 2010,
            "citation_query": "(2010) 1 SCC 100"
        }
        res = self.verifier.verify_case(case_ref)
        
        self.assertFalse(res["aws_verified"])
        self.assertFalse(res["google_verified"])
        self.assertIn("Stage 2/3/4 Verification Failure", res["error_message"])
        self.assertIn("PRECEDENT_DEPRECATED", res["error_message"])

    @patch("pandas.read_parquet")
    @patch("tools.realtime_rag.RealtimeRAGClient.search_general")
    def test_verify_document_sorting_by_authority(self, mock_fetch, mock_read_parquet):
        """Verify verify_document sorts verified cases in descending order of authority score."""
        # Mock df containing both cases
        mock_df = pd.DataFrame([
            {
                "title": "Rajesh Sharma v. State of Maharashtra",
                "citation": "(2014) 9 SCC 129",
                "decision_date": "2014-08-13",
                "path": "data/pdf/2014_9_scc_129.pdf"
            },
            {
                "title": "Sharma v. Ramesh Builders",
                "citation": "(2012) 3 SCC 400",
                "decision_date": "2012-05-10",
                "path": "data/pdf/2012_3_scc_400.pdf"
            }
        ])
        mock_read_parquet.return_value = mock_df
        
        mock_fetch.return_value = [{
            "title": "Some Title",
            "source": "Google CSE",
            "date": "2014",
            "snippet": "General Info",
            "url": "https://casemine.com/xyz"
        }]
        
        text = "Relies on (2014) 9 SCC 129 and also (2012) 3 SCC 400."
        res = self.verifier.verify_document(text)
        
        self.assertTrue(res["is_compliant"])
        verified = res["verified_cases"]
        self.assertEqual(len(verified), 2)
        
        # First case should be Sharma v. Ramesh Builders (score 230)
        # Second case Rajesh Sharma (score 220)
        self.assertEqual(verified[0]["aws_details"]["citation"], "(2012) 3 SCC 400")
        self.assertEqual(verified[1]["aws_details"]["citation"], "(2014) 9 SCC 129")

    def test_compute_factual_similarity_identical(self):
        """Verify similarity above 0.85 applies weight penalty and marks materially identical."""
        facts1 = "Harassment allegations without physical injury under Section 498A IPC."
        facts2 = "Harassment allegations without physical injury under Section 498A IPC."
        res = self.verifier.compute_factual_similarity(facts1, facts2)
        self.assertGreater(res["cosine_similarity"], 0.85)
        self.assertTrue(res["materially_identical"])
        self.assertEqual(res["weight_penalty"], 0.5)

    def test_compute_factual_similarity_different(self):
        """Verify similarity below 0.85 has no weight penalty."""
        facts1 = "Harassment allegations without physical injury under Section 498A IPC."
        facts2 = "Dishonour of cheque and notice requirements under Section 138 of NI Act."
        res = self.verifier.compute_factual_similarity(facts1, facts2)
        self.assertLessEqual(res["cosine_similarity"], 0.85)
        self.assertFalse(res["materially_identical"])
        self.assertEqual(res["weight_penalty"], 1.0)

    def test_compare_legal_issues_success(self):
        """Verify matching legal issues align successfully."""
        issues1 = ["Section 498A IPC", "Cruelty"]
        issues2 = ["Cruelty", "Automatic arrest guidelines"]
        res = self.verifier.compare_legal_issues(issues1, issues2)
        self.assertFalse(res["mismatched"])
        self.assertEqual(res["status"], "ISSUES_ALIGNED")

    def test_compare_legal_issues_mismatch_raises(self):
        """Verify mismatching legal issues raise IssueMismatchError."""
        from tools.case_citation_verifier import IssueMismatchError
        issues1 = ["Cruelty"]
        issues2 = ["Cheque"]
        with self.assertRaises(IssueMismatchError):
            self.verifier.compare_legal_issues(issues1, issues2)

    def test_compare_contextual_factors(self):
        """Verify contextual factor comparison outputs differences."""
        context1 = {
            "environmental": {
                "day_night": "day",
                "weather": "clear",
                "visibility_distance_meters": 100.0
            },
            "witness_count": 2,
            "accused_age": 30,
            "weapon_type": "none"
        }
        context2 = {
            "environmental": {
                "day_night": "night",
                "weather": "rain",
                "visibility_distance_meters": 10.0
            },
            "witness_count": 5,
            "accused_age": 45,
            "weapon_type": "knife"
        }
        res = self.verifier.compare_contextual_factors(context1, context2)
        self.assertFalse(res["day_night_match"])
        self.assertFalse(res["weather_match"])
        self.assertEqual(res["distance_variance_meters"], 90.0)
        self.assertEqual(res["witness_count_difference"], 3)
        self.assertEqual(res["accused_age_difference"], 15)
        self.assertFalse(res["weapon_type_match"])

    def test_audit_evidentiary_standards_deficit(self):
        """Verify evidentiary deficit triggers on weaker current case standard."""
        precedent_ev = {
            "circumstantial_ratio": 0.1,
            "has_eye_witness": True,
            "medical_report_valid": True
        }
        current_ev = {
            "circumstantial_ratio": 0.5,
            "has_eye_witness": False,
            "medical_report_valid": False
        }
        res = self.verifier.audit_evidentiary_standards(precedent_ev, current_ev)
        self.assertTrue(res["evidentiary_deficit"])
        self.assertEqual(res["status"], "EVIDENTIARY_DEFICIT")
        self.assertEqual(len(res["warnings"]), 2)

    def test_audit_evidentiary_standards_pass(self):
        """Verify evidentiary standards pass when requirements met."""
        precedent_ev = {
            "circumstantial_ratio": 0.5,
            "has_eye_witness": False,
            "medical_report_valid": False
        }
        current_ev = {
            "circumstantial_ratio": 0.1,
            "has_eye_witness": True,
            "medical_report_valid": True
        }
        res = self.verifier.audit_evidentiary_standards(precedent_ev, current_ev)
        self.assertFalse(res["evidentiary_deficit"])
        self.assertEqual(res["status"], "STANDARD_PASS")

    @patch("pandas.read_parquet")
    @patch("tools.realtime_rag.RealtimeRAGClient.search_general")
    def test_verify_case_with_stage3_intake_success(self, mock_fetch, mock_read_parquet):
        """Verify verify_case integrates Stage 3 audits successfully when intake is passed."""
        mock_read_parquet.return_value = pd.DataFrame([{
            "title": "Rajesh Sharma v. State of Maharashtra",
            "citation": "(2014) 9 SCC 129",
            "decision_date": "2014-08-13",
            "path": "data/pdf/2014_9_scc_129.pdf"
        }])
        mock_fetch.return_value = [{
            "title": "Rajesh Sharma v. State of Maharashtra",
            "source": "Google CSE",
            "date": "2014-08-13",
            "snippet": "Cruelty and arrest guidelines...",
            "url": "https://www.casemine.com/123"
        }]

        case_ref = {
            "type": "citation",
            "year": 2014,
            "citation_query": "(2014) 9 SCC 129"
        }
        intake = {
            "facts": "Harassment allegations without physical injury under Section 498A IPC. Automatic arrest was challenged.",
            "issues": ["Section 498A IPC"],
            "contextual_factors": {
                "environmental": {
                    "day_night": "day",
                    "weather": "clear",
                    "visibility_distance_meters": 100.0
                },
                "witness_count": 2,
                "accused_age": 30,
                "weapon_type": "none"
            },
            "evidence_standards": {
                "circumstantial_ratio": 0.1,
                "has_eye_witness": False,
                "medical_report_valid": False
            }
        }
        res = self.verifier.verify_case(case_ref, intake=intake)
        self.assertTrue(res["aws_verified"])
        self.assertTrue(res["google_verified"])
        self.assertIn("factual_similarity", res)
        self.assertIn("legal_issue_comparison", res)
        self.assertIn("contextual_comparison", res)
        self.assertIn("evidentiary_audit", res)
        self.assertEqual(res["factual_similarity"]["weight_penalty"], 0.5)

    @patch("pandas.read_parquet")
    @patch("tools.realtime_rag.RealtimeRAGClient.search_general")
    def test_verify_case_with_stage3_intake_mismatch_failure(self, mock_fetch, mock_read_parquet):
        """Verify verify_case captures Stage 3 IssueMismatchError and fails gracefully."""
        mock_read_parquet.return_value = pd.DataFrame([{
            "title": "Rajesh Sharma v. State of Maharashtra",
            "citation": "(2014) 9 SCC 129",
            "decision_date": "2014-08-13",
            "path": "data/pdf/2014_9_scc_129.pdf"
        }])
        mock_fetch.return_value = [{
            "title": "Rajesh Sharma v. State of Maharashtra",
            "source": "Google CSE",
            "date": "2014-08-13",
            "snippet": "Cruelty and arrest guidelines...",
            "url": "https://www.casemine.com/123"
        }]

        case_ref = {
            "type": "citation",
            "year": 2014,
            "citation_query": "(2014) 9 SCC 129"
        }
        # Mismatched issues triggers IssueMismatchError
        intake = {
            "facts": "Harassment allegations.",
            "issues": ["cheque dishonour"]
        }
        res = self.verifier.verify_case(case_ref, intake=intake)
        self.assertFalse(res["aws_verified"])
        self.assertFalse(res["google_verified"])
        self.assertIn("Stage 2/3/4 Verification Failure", res["error_message"])
        self.assertIn("ISSUE_MISMATCH", res["error_message"])

    def test_extract_ratio_decidendi_success(self):
        """Verify successful ratio decidendi extraction and filtering of hypotheticals."""
        case_meta = {
            "active_provisions": ["Section 498A IPC"],
            "concurring_opinions": ["Opinion by Lalit, J."],
            "judgment_text": "We hold that automatic arrest under Section 498A IPC is not permitted.\n\nBy way of illustration, if a husband argues, it is not cruelty."
        }
        res = self.verifier.extract_ratio_decidendi(case_meta, ["Section 498A IPC"])
        self.assertEqual(len(res["binding_rules"]), 1)
        self.assertEqual(res["binding_rules"][0]["status"], "BINDING_RATIO")
        self.assertEqual(res["paragraphs_analyzed"], 2)
        self.assertFalse(res["limited_to_facts"])

    def test_identify_obiter_dicta(self):
        """Verify obiter dicta components (counsel arguments, foreign court, philosophy) are identified."""
        case_meta = {
            "judgment_text": "Counsel for the appellant submitted that the law must change.\n\nWe must look at comparative law in English courts and House of Lords.\n\nJustice requires fairness and morality."
        }
        res = self.verifier.identify_obiter_dicta(case_meta)
        self.assertEqual(len(res["counsel_arguments"]), 1)
        self.assertEqual(len(res["comparative_law_refs"]), 1)
        self.assertEqual(len(res["philosophical_discussions"]), 1)
        self.assertEqual(len(res["foreign_court_refs"]), 1)
        self.assertEqual(res["obiter_ratio"], 1.0)
        self.assertEqual(res["obiter_weight"], 0.2)

    def test_track_precedent_evolution(self):
        """Verify precedent evolution tracking with modifications, expansions, and divergence."""
        case_meta = {
            "evolution": {
                "timeline": [
                    {"year": 2018, "type": "Limitation", "description": "Modified guidelines on arrest in Social Action Forum."}
                ],
                "divergence_score": 0.5,
                "referred_to_larger_bench": True,
                "legislative_overruled": False
            }
        }
        res = self.verifier.track_precedent_evolution(case_meta, ["arrest"])
        self.assertEqual(len(res["timeline"]), 1)
        self.assertEqual(len(res["modifications"]), 1)
        self.assertEqual(res["divergence_score"], 0.5)
        self.assertTrue(res["matched_evolution"])
        self.assertTrue(res["referred_to_larger_bench"])
        self.assertFalse(res["legislative_overruled"])

    def test_synthesize_precedents_conflict_resolution(self):
        """Verify semantic synthesis groups ratios, detects conflicts, and resolves using bench size."""
        verified_cases = [
            {
                "case_ref": {
                    "citation_query": "(2014) 9 SCC 129",
                    "court": "Supreme Court of India"
                },
                "bench_details": {
                    "bench_size": 2
                },
                "ratio_extraction": {
                    "binding_rules": [
                        {"text": "We hold that arrest is not permitted.", "matched_issues": ["Arrest"]}
                    ]
                }
            },
            {
                "case_ref": {
                    "citation_query": "(2012) 3 SCC 400",
                    "court": "Supreme Court of India"
                },
                "bench_details": {
                    "bench_size": 3
                },
                "ratio_extraction": {
                    "binding_rules": [
                        {"text": "We hold that arrest is permitted under guidelines.", "matched_issues": ["Arrest"]}
                    ]
                }
            }
        ]
        res = self.verifier.synthesize_precedents(verified_cases, ["Arrest"])
        self.assertTrue(res["citation_styles_valid"])
        self.assertEqual(len(res["conflicts"]), 1)
        self.assertEqual(res["conflicts"][0]["resolved_by"], "(2012) 3 SCC 400")
        self.assertEqual(res["attestation_status"], "VALIDATED_SYNTHESIS")

    @patch("pandas.read_parquet")
    @patch("tools.realtime_rag.RealtimeRAGClient.search_general")
    def test_verify_document_with_stage4_synthesis(self, mock_fetch, mock_read_parquet):
        """Verify verify_document invokes Stage 4 precedent synthesis and returns it."""
        mock_read_parquet.return_value = pd.DataFrame([{
            "title": "Rajesh Sharma v. State of Maharashtra",
            "citation": "(2014) 9 SCC 129",
            "decision_date": "2014-08-13",
            "path": "data/pdf/2014_9_scc_129.pdf"
        }])
        mock_fetch.return_value = [{
            "title": "Rajesh Sharma v. State of Maharashtra",
            "source": "Google CSE",
            "date": "2014-08-13",
            "snippet": "Cruelty and arrest guidelines...",
            "url": "https://www.casemine.com/123"
        }]

        text = "Check (2014) 9 SCC 129."
        intake = {
            "facts": "Harassment allegations without physical injury under Section 498A IPC. Automatic arrest was challenged.",
            "issues": ["Section 498A IPC"]
        }
        res = self.verifier.verify_document(text, intake=intake)
        self.assertTrue(res["is_compliant"])
        self.assertIsNotNone(res["semantic_synthesis"])
        self.assertIn("ratios_by_issue", res["semantic_synthesis"])


if __name__ == "__main__":
    unittest.main()


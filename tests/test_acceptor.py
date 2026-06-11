"""
Tests for the Acceptor Agent — Registry Simulation Engine.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.acceptor import simulate_registry_check, check_annexure_completeness


class TestSimulateRegistryCheck:
    """Test the registry simulation logic."""

    VALID_DOCUMENT = """
IN THE COURT OF THE CIVIL JUDGE SENIOR DIVISION, NAGPUR

IN THE MATTER OF:

Rajesh Kumar
... PETITIONER/APPLICANT

VERSUS

Suresh Sharma
... RESPONDENT/OPPONENT

AFFIDAVIT

1. That I am the Petitioner in the above-mentioned suit and am well acquainted
   with the facts and circumstances of the case.

2. That the Respondent failed to pay rent of Rs. 50,000/- per month for a
   period of 6 months, totaling Rs. 3,00,000/-.

PRAYER

In the premises aforesaid, it is most respectfully prayed that this Hon'ble Court
may be pleased to grant the relief as prayed for.

VERIFICATION

I, Rajesh Kumar, the above-named deponent, do hereby verify that the contents
of the above Affidavit are true and correct to my knowledge and belief.

Verified at Nagpur on this 15th day of May, 2026.

DEPONENT

Rajesh Kumar

Through Advocate:
Adv. Priya Deshmukh
Bar Council of Maharashtra No. MH/1234/2020
Office: 45, Civil Lines, Nagpur
Phone: 0712-2345678
"""

    def test_valid_document_accepted(self):
        result = simulate_registry_check(
            self.VALID_DOCUMENT, "MH-DISTRICT", "affidavit"
        )
        assert result["acceptance_score"] >= 60
        assert result["would_be_accepted"] or result["acceptance_score"] >= 85

    def test_has_cause_title(self):
        result = simulate_registry_check(
            self.VALID_DOCUMENT, "MH-DISTRICT", "affidavit"
        )
        assert result["detailed_checks"]["cause_title_present"] is True

    def test_has_verification(self):
        result = simulate_registry_check(
            self.VALID_DOCUMENT, "MH-DISTRICT", "affidavit"
        )
        assert result["detailed_checks"]["verification_clause_present"] is True

    def test_has_prayer(self):
        result = simulate_registry_check(
            self.VALID_DOCUMENT, "MH-DISTRICT", "affidavit"
        )
        assert result["detailed_checks"]["prayer_clause_present"] is True

    def test_has_advocate_details(self):
        result = simulate_registry_check(
            self.VALID_DOCUMENT, "MH-DISTRICT", "affidavit"
        )
        assert result["detailed_checks"]["advocate_details_present"] is True

    def test_empty_document_rejected(self):
        result = simulate_registry_check("", "MH-DISTRICT", "affidavit")
        assert result["acceptance_score"] < 50
        assert not result["would_be_accepted"]
        assert len(result["fatal_defects"]) > 0

    def test_missing_verification_fatal(self):
        doc_no_verification = """
IN THE COURT OF THE CIVIL JUDGE, NAGPUR

Petitioner vs Respondent

FACTS
Some facts here.

PRAYER
Please grant relief.

DEPONENT
Signed by applicant

Through Advocate:
Adv. Test
Bar No. 123
"""
        result = simulate_registry_check(doc_no_verification, "MH-DISTRICT", "affidavit")
        assert result["detailed_checks"]["verification_clause_present"] is False

    def test_registry_notes_generated(self):
        result = simulate_registry_check(
            self.VALID_DOCUMENT, "MH-DISTRICT", "affidavit"
        )
        notes = result["registry_officer_notes"]
        assert "REGISTRY SCRUTINY REPORT" in notes
        assert "Score:" in notes


class TestAnnexureCompleteness:
    """Test annexure completeness checking."""

    def test_affidavit_annexures(self):
        doc = "Attached herewith is the identity proof and supporting documents."
        result = check_annexure_completeness(doc, "affidavit")
        assert "identity_proof" in result["present"]

    def test_missing_annexures(self):
        doc = "This is a simple document with no annexures."
        result = check_annexure_completeness(doc, "writ_petition")
        assert len(result["missing"]) > 0
        assert result["completeness_score"] < 100

    def test_legal_notice_no_required_annexures(self):
        result = check_annexure_completeness("Any text", "legal_notice")
        assert result["completeness_score"] == 100.0

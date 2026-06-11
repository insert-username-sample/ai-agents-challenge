import pytest
from tools.chamber_suite import LegalChamberSuite

def test_generate_mentioning_slip():
    suite = LegalChamberSuite()
    slip_data = {
        "court_name": "Delhi High Court",
        "case_reference": "W.P.(C) 420/2026",
        "petitioner_name": "Rajesh Kumar",
        "respondent_name": "State of NCT",
        "impugned_order_date": "2026-05-15",
        "urgency_grounds": "Threat of imminent demolition on 2026-06-10",
        "interim_relief": "Stay on demolition order",
        "counsel_name": "Manas Khobrekar"
    }
    slip = suite.generate_mentioning_slip(slip_data)
    assert "URGENT LISTING MENTIONING SLIP" in slip
    assert "Rajesh Kumar" in slip
    assert "State of NCT" in slip
    assert "Stay on demolition order" in slip

def test_audit_filing_compliance_pass():
    suite = LegalChamberSuite()
    doc_metadata = {
        "paper_size": "A4",
        "top_margin_cm": 2.0,
        "bottom_margin_cm": 2.0,
        "left_margin_cm": 4.0,
        "right_margin_cm": 4.0,
        "font_family": "Times New Roman",
        "font_size": 14,
        "line_spacing": 1.5
    }
    res = suite.audit_filing_compliance(doc_metadata, 12.5, "district_court")
    assert res["status"] == "APPROVED"

def test_audit_filing_compliance_fail():
    suite = LegalChamberSuite()
    doc_metadata = {
        "paper_size": "Letter", # Fails: must be A4
        "top_margin_cm": 2.0,
        "bottom_margin_cm": 2.0,
        "left_margin_cm": 4.0,
        "right_margin_cm": 4.0,
        "font_family": "Times New Roman",
        "font_size": 14,
        "line_spacing": 1.5
    }
    res = suite.audit_filing_compliance(doc_metadata, 12.5, "district_court")
    assert res["status"] == "REJECTED"
    assert "Paper size must be A4" in res["objection_details"]

def test_compile_legal_invoice():
    suite = LegalChamberSuite()
    billing_data = {
        "effective_hearings": 1,
        "effective_rate": 15000.0,
        "non_effective_hearings": 2,
        "non_effective_rate": 3000.0,
        "drafting_charges": [4000.0],
        "conference_charges": [],
        "actual_expenses": 1000.0
    }
    client_profile = {
        "is_registered_business": True,
        "turnover_inr_lakhs": 45.0 # RCM applicable
    }
    invoice = suite.compile_legal_invoice(billing_data, client_profile)
    assert invoice["invoice_summary"]["grand_total"] == 28500.0  # (21000 * 1.1) + 1000
    assert invoice["gst_compliance"]["rcm_applicable"] is True
    assert invoice["gst_compliance"]["invoice_notation"] == "GST payable by recipient under RCM"

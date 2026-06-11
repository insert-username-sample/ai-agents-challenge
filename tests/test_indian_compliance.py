import pytest
from engine.efiling_validator import EFilingValidator, RegistryComplianceError
from engine.billing_compiler import BillingCompiler

def test_efiling_layout_valid():
    validator = EFilingValidator()
    metadata = {
        "paper_size": "A4",
        "top_margin_cm": 2.0,
        "bottom_margin_cm": 2.0,
        "left_margin_cm": 4.0,
        "right_margin_cm": 4.0,
        "font_family": "Times New Roman",
        "font_size": 14,
        "line_spacing": 1.5
    }
    res = validator.validate_layout(metadata)
    assert res["status"] == "COMPLIANT"

def test_efiling_layout_invalid_margin():
    validator = EFilingValidator()
    metadata = {
        "paper_size": "A4",
        "top_margin_cm": 2.0,
        "bottom_margin_cm": 2.0,
        "left_margin_cm": 3.5, # Less than 4cm
        "right_margin_cm": 4.0,
        "font_family": "Times New Roman",
        "font_size": 14,
        "line_spacing": 1.5
    }
    with pytest.raises(RegistryComplianceError, match="Left/Right margins must be at least 4.0cm"):
        validator.validate_layout(metadata)

def test_efiling_file_size_district():
    validator = EFilingValidator()
    # District Court cap is 20MB
    res = validator.validate_upload_limits(15.5, "district_court")
    assert res["status"] == "COMPLIANT"
    
    with pytest.raises(RegistryComplianceError, match="District Court upload size limit exceeded"):
        validator.validate_upload_limits(22.0, "district_court")

def test_efiling_file_size_high_court():
    validator = EFilingValidator()
    # High Court cap is 300MB
    res = validator.validate_upload_limits(250.0, "delhi_high_court")
    assert res["status"] == "COMPLIANT"

def test_billing_formula():
    compiler = BillingCompiler(clerkage_rate=0.10)
    billing_data = {
        "effective_hearings": 3,
        "effective_rate": 10000.0,
        "non_effective_hearings": 2,
        "non_effective_rate": 2000.0,
        "drafting_charges": [5000.0, 3000.0],
        "conference_charges": [1500.0],
        "actual_expenses": 500.0
    }
    # Hearings: 3 * 10k + 2 * 2k = 34,000
    # Drafting: 8,000
    # Conference: 1,500
    # Subtotal: 43,500
    # Clerkage: 4,350
    # Total before expenses: 47,850
    # Grand Total: 47,850 + 500 = 48,350
    res = compiler.calculate_invoice_total(billing_data)
    assert res["subtotal_before_clerkage"] == 43500.0
    assert res["clerkage_amount"] == 4350.0
    assert res["grand_total"] == 48350.0

def test_gst_rcm_status():
    compiler = BillingCompiler()
    
    # Under 20 Lakhs threshold
    res_exempt = compiler.determine_gst_rcm_status({
        "is_registered_business": True,
        "turnover_inr_lakhs": 15.0
    })
    assert res_exempt["gst_rate"] == 0.0
    assert "Exempt" in res_exempt["invoice_notation"]

    # At or above 20 Lakhs threshold
    res_rcm = compiler.determine_gst_rcm_status({
        "is_registered_business": True,
        "turnover_inr_lakhs": 25.0
    })
    assert res_rcm["gst_rate"] == 18.0
    assert res_rcm["rcm_applicable"] is True
    assert "payable by recipient under RCM" in res_rcm["invoice_notation"]

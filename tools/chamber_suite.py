import os
from typing import Dict, Any, List
from engine.efiling_validator import EFilingValidator
from engine.billing_compiler import BillingCompiler

class LegalChamberSuite:
    """
    Consolidated Legal Chamber Suite:
    Provides automated workflows for Indian law firms combining:
    - Mentioning Slip Compilation (Vacation Supreme Court & High Court)
    - e-Filing Formatting Compliance Auditing (e-Filing Rules 2021/2026)
    - Appearance Fee calculation and GST RCM Compliance Invoice Generation.
    """

    def __init__(self):
        self.layout_validator = EFilingValidator()
        self.billing_compiler = BillingCompiler(clerkage_rate=0.10)

    def generate_mentioning_slip(self, slip_data: Dict[str, Any]) -> str:
        """
        Compiles written mentioning slips following Supreme Court / High Court vacation guidelines.
        """
        slip_template = (
            "====================================================================\n"
            "                 URGENT LISTING MENTIONING SLIP                     \n"
            "====================================================================\n"
            f"COURT: {slip_data.get('court_name', 'Supreme Court of India')}\n"
            f"CASE NUMBER / DIARY NUMBER: {slip_data.get('case_reference', 'N/A')}\n"
            f"PARTY DETAILS: {slip_data.get('petitioner_name', 'N/A')} vs. {slip_data.get('respondent_name', 'N/A')}\n"
            f"DATE OF IMPUGNED ORDER: {slip_data.get('impugned_order_date', 'N/A')}\n"
            "--------------------------------------------------------------------\n"
            "GROUNDS OF EXTREME URGENCY:\n"
            f"{slip_data.get('urgency_grounds', 'No grounds specified.')}\n"
            "--------------------------------------------------------------------\n"
            f"INTERIM RELIEF SOUGHT: {slip_data.get('interim_relief', 'N/A')}\n"
            f"PREVIOUS LISTING ATTEMPTS: {slip_data.get('previous_attempts', 'None')}\n"
            "--------------------------------------------------------------------\n"
            f"ADVOCATE-ON-RECORD / COUNSEL SIGNATURE: Adv. {slip_data.get('counsel_name', 'N/A')}\n"
            "===================================================================="
        )
        return slip_template

    def audit_filing_compliance(self, doc_metadata: Dict[str, Any], file_size_mb: float, court_type: str) -> Dict[str, Any]:
        """
        Runs complete layout and size audits to prevent registry defects.
        """
        try:
            layout_res = self.layout_validator.validate_layout(doc_metadata)
            size_res = self.layout_validator.validate_upload_limits(file_size_mb, court_type)
            return {
                "status": "APPROVED",
                "layout_audit": layout_res["details"],
                "size_limit_mb": size_res["max_allowed_mb"]
            }
        except Exception as e:
            return {
                "status": "REJECTED",
                "objection_details": str(e)
            }

    def compile_legal_invoice(self, billing_data: Dict[str, Any], client_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compiles the total appearance bill, including Munshiana and GST Reverse Charge Mechanism (RCM) checks.
        """
        totals = self.billing_compiler.calculate_invoice_total(billing_data)
        gst_status = self.billing_compiler.determine_gst_rcm_status(client_profile)
        
        return {
            "invoice_summary": totals,
            "gst_compliance": gst_status
        }

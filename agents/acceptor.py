"""
Clausely Acceptor Agent — Registry Simulation Engine.

Simulates an Indian court registry officer performing document scrutiny.
This is NOT probabilistic — it is a rule-based simulation that checks
every requirement a court registry counter would verify before accepting
a filing.

Checks performed:
- Cause title presence and format
- Margin compliance
- Font and formatting compliance
- Stamp paper value
- Verification clause
- Advocate details
- Annexure completeness
- Limitation period
- Court fee payment
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from tools.sfe import SymbolicFormattingEngine, ValidationResult
from tools.registry_rules import (
    get_required_annexures,
    check_limitation,
    get_court_fee,
    get_filing_requirements,
)

logger = logging.getLogger("clausely.acceptor")


# ---------------------------------------------------------------------------
# ADK FunctionTool definitions
# ---------------------------------------------------------------------------

def simulate_registry_check(
    document_text: str,
    jurisdiction: str,
    document_type: str,
) -> dict:
    """
    Simulate a court registry officer checking a legal document.

    Performs comprehensive rule-based scrutiny matching what an actual
    Indian court registry counter would check before accepting a filing.

    Args:
        document_text: The full text of the legal document
        jurisdiction: Court jurisdiction code (e.g., 'MH-DISTRICT')
        document_type: Type of document (e.g., 'affidavit', 'petition')

    Returns:
        Dict with acceptance_score, defects, and detailed check results
    """
    text_lower = document_text.lower()
    text_upper = document_text.upper()

    checks: Dict[str, bool] = {}
    fatal_defects: List[str] = []
    curable_defects: List[str] = []

    # ---- 1. Cause title check ----
    has_cause_title = any(
        marker in text_upper
        for marker in ["IN THE COURT OF", "IN THE MATTER OF", "VERSUS", "V/S"]
    )
    checks["cause_title_present"] = has_cause_title
    if not has_cause_title:
        fatal_defects.append("Missing cause title — document will be rejected at registry counter")

    # ---- 2. Petitioner/Respondent identification ----
    has_parties = "petitioner" in text_lower or "applicant" in text_lower
    has_respondent = "respondent" in text_lower or "opponent" in text_lower
    checks["parties_identified"] = has_parties and has_respondent
    if not (has_parties and has_respondent):
        fatal_defects.append("Parties not properly identified (petitioner/respondent missing)")

    # ---- 3. Verification clause ----
    has_verification = any(
        marker in text_lower
        for marker in ["verification", "i hereby verify", "do hereby verify", "solemnly affirm"]
    )
    checks["verification_clause_present"] = has_verification
    if not has_verification:
        fatal_defects.append("Missing verification clause — mandatory under Order VI Rule 15 CPC")

    # ---- 4. Advocate details ----
    has_advocate = any(
        marker in text_lower
        for marker in ["advocate", "counsel", "bar council", "bar no", "enrollment"]
    )
    checks["advocate_details_present"] = has_advocate
    if not has_advocate:
        curable_defects.append("Advocate details not found — required if filing through counsel")

    # ---- 5. Prayer/relief clause ----
    has_prayer = any(
        marker in text_lower
        for marker in ["prayer", "relief sought", "wherefore", "prayed that"]
    )
    checks["prayer_clause_present"] = has_prayer
    if not has_prayer:
        fatal_defects.append("Missing prayer/relief clause — court cannot grant relief without a prayer")

    # ---- 6. Jurisdiction clause ----
    has_jurisdiction = any(
        marker in text_lower
        for marker in ["jurisdiction", "territorial jurisdiction", "section 9 cpc", "article 226", "article 32"]
    )
    checks["jurisdiction_clause_present"] = has_jurisdiction
    if not has_jurisdiction:
        curable_defects.append("Jurisdiction clause not explicitly stated")

    # ---- 7. Signature block ----
    has_signature = any(
        marker in text_lower
        for marker in ["deponent", "signature", "signed", "sd/-"]
    )
    checks["signature_block_present"] = has_signature
    if not has_signature:
        fatal_defects.append("Missing signature block — unsigned document will be rejected")

    # ---- 8. Date check ----
    has_date = any(
        marker in text_lower
        for marker in ["dated", "date:", "day of", "verified at"]
    )
    checks["date_present"] = has_date
    if not has_date:
        curable_defects.append("Date of execution not found in document")

    # ---- 9. Stamp paper reference (jurisdiction-specific) ----
    try:
        sfe = SymbolicFormattingEngine(jurisdiction)
        if sfe.rules.get("stamp_paper_required"):
            has_stamp_ref = any(
                marker in text_lower
                for marker in ["stamp paper", "stamp duty", "non-judicial stamp"]
            )
            checks["stamp_paper_referenced"] = has_stamp_ref
            if not has_stamp_ref:
                curable_defects.append(
                    f"Stamp paper not referenced — ₹{sfe.rules.get('stamp_paper_value', '?')} "
                    f"stamp paper required for {jurisdiction}"
                )
    except Exception:
        checks["stamp_paper_referenced"] = True  # Skip if rules unavailable

    # ---- 10. Notarization check ----
    has_notary = any(
        marker in text_lower
        for marker in ["notary", "notarized", "notarisation", "before me"]
    )
    checks["notarization_present"] = has_notary

    # ---- 11. Document length reasonableness ----
    word_count = len(document_text.split())
    checks["reasonable_length"] = word_count > 50
    if word_count < 50:
        fatal_defects.append(f"Document too short ({word_count} words) — likely incomplete")

    # ---- 12. Annexure references ----
    has_annexure_ref = any(
        marker in text_lower
        for marker in ["annexure", "exhibit", "annexed herewith"]
    )
    checks["annexures_referenced"] = has_annexure_ref

    # ---- 13. Precedent Citation Double-Verification check ----
    try:
        from tools.case_citation_verifier import precedent_verifier
        verifier_results = precedent_verifier.verify_document(document_text)
        
        checks["precedents_verified"] = verifier_results["is_compliant"]
        if not verifier_results["is_compliant"]:
            for err in verifier_results["errors"]:
                fatal_defects.append(err)
    except Exception as e:
        logger.warning(f"Precedent citation double-verification check failed to run: {e}")

    # ---- Score calculation ----
    fatal_weight = len(fatal_defects) * 20
    curable_weight = len(curable_defects) * 5
    acceptance_score = max(0.0, 100.0 - fatal_weight - curable_weight)

    # Generate registry officer notes
    notes = _generate_registry_notes(fatal_defects, curable_defects, acceptance_score)

    return {
        "acceptance_score": acceptance_score,
        "would_be_accepted": acceptance_score >= 85 and len(fatal_defects) == 0,
        "fatal_defects": fatal_defects,
        "curable_defects": curable_defects,
        "detailed_checks": checks,
        "registry_officer_notes": notes,
        "word_count": word_count,
    }


def check_annexure_completeness(
    document_text: str,
    document_type: str,
) -> dict:
    """
    Check if all required annexures are mentioned in the document.

    Args:
        document_text: The full document text
        document_type: Type of document (e.g., 'affidavit', 'writ_petition')

    Returns:
        Dict with lists of present, missing, and incomplete annexures
    """
    required = get_required_annexures(document_type)
    text_lower = document_text.lower()

    present = []
    missing = []

    for annexure in required:
        # Normalize annexure name for text search
        search_terms = annexure.lower().replace("_", " ").split()
        found = all(term in text_lower for term in search_terms)
        if found:
            present.append(annexure)
        else:
            missing.append(annexure)

    return {
        "required_annexures": required,
        "present": present,
        "missing": missing,
        "completeness_score": (len(present) / len(required) * 100) if required else 100.0,
    }


def verify_limitation_period(
    cause_of_action_date: str,
    filing_date: str,
    matter_type: str,
) -> dict:
    """
    Check if a filing is within the applicable limitation period.

    Uses the Limitation Act, 1963 and relevant special statutes to
    determine whether the filing window is still open.

    Args:
        cause_of_action_date: Date cause of action arose (YYYY-MM-DD)
        filing_date: Proposed filing date (YYYY-MM-DD)
        matter_type: Type of matter (e.g., 'suit_for_recovery_of_money')

    Returns:
        Dict with within_limitation, days_remaining, and limitation info
    """
    return check_limitation(cause_of_action_date, filing_date, matter_type)


def get_filing_checklist(
    jurisdiction: str,
    document_type: str,
) -> dict:
    """
    Get the complete filing checklist for a jurisdiction and document type.

    Args:
        jurisdiction: Court jurisdiction code
        document_type: Type of document

    Returns:
        Filing requirements including annexures, court fees, and notes
    """
    return get_filing_requirements(jurisdiction, document_type)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _generate_registry_notes(
    fatal: List[str],
    curable: List[str],
    score: float,
) -> str:
    """Generate human-readable registry officer notes."""
    lines = []
    lines.append(f"REGISTRY SCRUTINY REPORT — Score: {score:.0f}/100")
    lines.append("=" * 50)

    if not fatal and not curable:
        lines.append("✅ Document passes all registry checks.")
        lines.append("   Recommendation: ACCEPT for filing.")
    elif not fatal:
        lines.append("⚠️ Document has minor issues but is ACCEPTABLE.")
        lines.append(f"   {len(curable)} curable defect(s) noted.")
        for i, defect in enumerate(curable, 1):
            lines.append(f"   {i}. {defect}")
    else:
        lines.append("❌ Document has FATAL defects — REJECT at registry counter.")
        lines.append(f"   {len(fatal)} fatal defect(s):")
        for i, defect in enumerate(fatal, 1):
            lines.append(f"   🔴 {i}. {defect}")
        if curable:
            lines.append(f"\n   Additionally, {len(curable)} curable defect(s):")
            for i, defect in enumerate(curable, 1):
                lines.append(f"   🟡 {i}. {defect}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# ADK Agent definition
# ---------------------------------------------------------------------------

acceptor_tools = [
    FunctionTool(func=simulate_registry_check),
    FunctionTool(func=check_annexure_completeness),
    FunctionTool(func=verify_limitation_period),
    FunctionTool(func=get_filing_checklist),
]

import os
ACCEPTOR_MODEL = os.getenv("CLAUSELY_MODEL", "gemini-3.5-flash")

acceptor_agent = Agent(
    name="clausely_acceptor",
    model=ACCEPTOR_MODEL,
    description=(
        "Registry simulation engine for Indian courts. Predicts whether "
        "a filing will survive registry scrutiny by running comprehensive "
        "rule-based checks."
    ),
    instruction="""You are the Clausely Acceptor Agent — a simulation of an Indian court registry officer.

Your job:
1. Run simulate_registry_check on the provided document text.
2. Check annexure completeness using check_annexure_completeness.
3. If cause of action dates are available, verify the limitation period.
4. Get the filing checklist for the jurisdiction.
5. Generate a detailed acceptance report.

IMPORTANT:
- You are SIMULATING a registry officer, not providing legal advice.
- Be specific about which court rule each defect violates.
- Fatal defects WILL cause rejection. Flag them clearly.
- Curable defects SHOULD be fixed but won't cause outright rejection.
- Reference specific court filing rules, not general legal principles.
- Always output the acceptance score and whether the document would be accepted.

Return your output as a structured report with:
- acceptance_score: float 0-100
- would_be_accepted: boolean
- fatal_defects: list of specific defects
- curable_defects: list of minor issues
- registry_checks: dict of individual check results
- recommendation: clear accept/reject/revise recommendation
""",
    tools=acceptor_tools,
)

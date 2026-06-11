"""
Clausely Registry Rules — Database of Indian court filing regulations.

Provides lookup functions for court-specific procedural requirements,
limitation periods, filing fees, and annexure rules.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Limitation periods under the Limitation Act, 1963
# ---------------------------------------------------------------------------

LIMITATION_PERIODS: Dict[str, Dict[str, Any]] = {
    "suit_for_recovery_of_money": {
        "period_years": 3,
        "act": "Limitation Act, 1963",
        "article": "Article 36",
        "description": "Suit for recovery of money due under any contract",
    },
    "suit_for_possession_of_immovable_property": {
        "period_years": 12,
        "act": "Limitation Act, 1963",
        "article": "Article 65",
        "description": "Suit for possession of immovable property based on title",
    },
    "suit_for_specific_performance": {
        "period_years": 3,
        "act": "Limitation Act, 1963",
        "article": "Article 54",
        "description": "Suit for specific performance of a contract",
    },
    "cheque_bounce_complaint": {
        "period_days": 30,
        "act": "Negotiable Instruments Act, 1881",
        "section": "Section 138 proviso (c)",
        "description": "Complaint under S.138 NI Act — within 30 days of cause of action",
    },
    "writ_petition": {
        "period_years": None,  # No fixed period, reasonable time
        "act": "Constitution of India",
        "article": "Article 226 / Article 32",
        "description": "Writ petition — no fixed limitation but must be filed within reasonable time",
    },
    "appeal_civil": {
        "period_days": 30,
        "act": "Limitation Act, 1963",
        "article": "Article 116",
        "description": "Appeal from a decree or order of any court",
    },
    "appeal_criminal": {
        "period_days": 30,
        "act": "Limitation Act, 1963",
        "article": "Article 115",
        "description": "Appeal from conviction or order of a criminal court",
    },
    "rent_dispute": {
        "period_years": 3,
        "act": "Limitation Act, 1963",
        "article": "Article 36",
        "description": "Suit for arrears of rent",
    },
}


# ---------------------------------------------------------------------------
# Required annexures by document type
# ---------------------------------------------------------------------------

REQUIRED_ANNEXURES: Dict[str, List[str]] = {
    "affidavit": [
        "identity_proof",
        "supporting_documents",
    ],
    "petition": [
        "certified_copy_of_impugned_order",
        "vakalat_nama",
        "memo_of_parties",
        "identity_proof",
        "court_fee_receipt",
    ],
    "writ_petition": [
        "certified_copy_of_impugned_order",
        "vakalat_nama",
        "memo_of_parties",
        "synopsis_and_list_of_dates",
        "identity_proof",
    ],
    "legal_notice": [],
    "nda": [
        "schedule_of_confidential_information",
    ],
    "rent_agreement": [
        "identity_proof_landlord",
        "identity_proof_tenant",
        "property_ownership_proof",
        "property_tax_receipt",
    ],
    "bail_application": [
        "fir_copy",
        "charge_sheet",
        "surety_bond",
        "identity_proof",
    ],
    "complaint": [
        "identity_proof",
        "supporting_documents",
        "court_fee_receipt",
    ],
}


# ---------------------------------------------------------------------------
# Court fee schedule (simplified — representative values)
# ---------------------------------------------------------------------------

COURT_FEES: Dict[str, Dict[str, Any]] = {
    "MH-DISTRICT": {
        "affidavit": {"fixed": 10, "currency": "INR"},
        "petition": {"ad_valorem_percent": 1.0, "minimum": 500, "currency": "INR"},
        "legal_notice": {"fixed": 0, "currency": "INR"},
        "complaint": {"fixed": 200, "currency": "INR"},
    },
    "MH-HC": {
        "writ_petition": {"fixed": 100, "currency": "INR"},
        "petition": {"ad_valorem_percent": 1.0, "minimum": 1000, "currency": "INR"},
    },
    "DL-DISTRICT": {
        "affidavit": {"fixed": 10, "currency": "INR"},
        "petition": {"ad_valorem_percent": 1.0, "minimum": 500, "currency": "INR"},
    },
    "IN-SC": {
        "writ_petition": {"fixed": 500, "currency": "INR"},
        "special_leave_petition": {"fixed": 500, "currency": "INR"},
    },
}


# ---------------------------------------------------------------------------
# Public Functions (used as ADK FunctionTools)
# ---------------------------------------------------------------------------

def get_required_annexures(document_type: str) -> List[str]:
    """Return list of required annexures for a document type."""
    doc_type_key = document_type.lower().replace(" ", "_")
    return REQUIRED_ANNEXURES.get(doc_type_key, [])


def get_limitation_period(matter_type: str) -> Dict[str, Any]:
    """Return limitation period info for a given matter type."""
    key = matter_type.lower().replace(" ", "_")
    return LIMITATION_PERIODS.get(key, {
        "period_years": None,
        "description": f"Limitation period not found for: {matter_type}",
    })


def check_limitation(
    cause_of_action_date: str,
    filing_date: str,
    matter_type: str,
) -> Dict[str, Any]:
    """
    Check whether a filing is within the limitation period.

    Args:
        cause_of_action_date: ISO date string (YYYY-MM-DD)
        filing_date: ISO date string (YYYY-MM-DD)
        matter_type: Key into LIMITATION_PERIODS

    Returns:
        Dict with within_limitation, days_remaining, etc.
    """
    try:
        coa_date = datetime.fromisoformat(cause_of_action_date)
        file_date = datetime.fromisoformat(filing_date)
    except ValueError:
        return {
            "error": "Invalid date format. Use YYYY-MM-DD.",
            "within_limitation": None,
        }

    period_info = get_limitation_period(matter_type)
    period_years = period_info.get("period_years")
    period_days = period_info.get("period_days")

    if period_years is None and period_days is None:
        return {
            "within_limitation": None,
            "reason": "No fixed limitation period for this matter type.",
            "limitation_info": period_info,
        }

    if period_years is not None:
        deadline = coa_date + timedelta(days=period_years * 365)
    else:
        deadline = coa_date + timedelta(days=period_days)

    days_elapsed = (file_date - coa_date).days
    days_remaining = (deadline - file_date).days

    return {
        "within_limitation": file_date <= deadline,
        "days_elapsed": days_elapsed,
        "days_remaining": max(0, days_remaining),
        "deadline": deadline.isoformat(),
        "limitation_info": period_info,
    }


def get_court_fee(jurisdiction: str, document_type: str) -> Dict[str, Any]:
    """Return court fee information for a jurisdiction and document type."""
    fees = COURT_FEES.get(jurisdiction, {})
    doc_type_key = document_type.lower().replace(" ", "_")
    return fees.get(doc_type_key, {"fixed": 0, "currency": "INR", "note": "Court fee not found"})


def get_filing_requirements(jurisdiction: str, document_type: str) -> Dict[str, Any]:
    """Return comprehensive filing requirements."""
    return {
        "jurisdiction": jurisdiction,
        "document_type": document_type,
        "required_annexures": get_required_annexures(document_type),
        "court_fee": get_court_fee(jurisdiction, document_type),
        "notes": [
            "All documents must be filed in duplicate.",
            "Vakalat Nama must be filed if represented by an advocate.",
            "Original documents must be available for verification.",
        ],
    }

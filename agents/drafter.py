"""
Clausely Drafter Agent — ADK Agent for legal document generation.

Uses Gemini models via ADK's Agent class with FunctionTool bindings
to generate court-ready legal documents. The Drafter:
1. Selects the appropriate template for the document type
2. Generates each required clause using Gemini
3. Assembles the complete document via Legal AST
4. Validates against the Symbolic Formatting Engine
5. Re-drafts any sections with fatal defects
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from tools.sfe import SymbolicFormattingEngine
from tools.legal_ast import (
    LegalASTParser,
    DocumentNode,
    SectionNode,
    ClauseNode,
    VariableNode,
)
from tools.corpus_client import CorpusClient

logger = logging.getLogger("clausely.drafter")


# ---------------------------------------------------------------------------
# Template mapping
# ---------------------------------------------------------------------------

TEMPLATE_MAP: Dict[tuple, str] = {
    ("affidavit", "MH-DISTRICT"): "affidavit_mh.txt",
    ("affidavit", "MH-HC"): "affidavit_mh.txt",
    ("affidavit", "DL-DISTRICT"): "affidavit_mh.txt",
    ("affidavit", "IN-SC"): "affidavit_mh.txt",
    ("legal_notice", "MH-DISTRICT"): "legal_notice_138.txt",
    ("legal_notice", "DL-DISTRICT"): "legal_notice_138.txt",
    ("legal_notice", "MH-HC"): "legal_notice_138.txt",
    ("legal_notice", "IN-SC"): "legal_notice_138.txt",
    ("nda", "MH-DISTRICT"): "nda_general.txt",
    ("nda", "DL-DISTRICT"): "nda_general.txt",
    ("nda", "MH-HC"): "nda_general.txt",
    ("nda", "IN-SC"): "nda_general.txt",
}

# Document type normalization
DOC_TYPE_ALIASES: Dict[str, str] = {
    "Affidavit": "affidavit",
    "Legal Notice (S.138 NI)": "legal_notice",
    "NDA": "nda",
    "Rent Agreement": "rent_agreement",
    "Writ Petition": "writ_petition",
    "Petition": "petition",
    "Bail Application": "bail_application",
}


# ---------------------------------------------------------------------------
# ADK FunctionTool definitions
# ---------------------------------------------------------------------------

def generate_clause(
    clause_type: str,
    jurisdiction: str,
    context: str,
    language: str = "en",
) -> dict:
    """
    Generate a specific legal clause for an Indian court document.

    This tool uses contextual legal knowledge to produce properly formatted
    clauses with statute citations relevant to the specified jurisdiction.

    Args:
        clause_type: Type of clause (e.g., 'jurisdiction_clause', 'verification',
                     'facts', 'grounds', 'prayer', 'cause_title')
        jurisdiction: Court jurisdiction code (e.g., 'MH-DISTRICT', 'IN-SC')
        context: Case-specific context and facts to incorporate
        language: Language code ('en', 'hi', 'mr')

    Returns:
        Dict with clause_text, citations, and risk_indicators
    """
    # Build clause based on type with deterministic templates
    clause_templates = {
        "cause_title": _generate_cause_title(jurisdiction, context),
        "jurisdiction_clause": _generate_jurisdiction_clause(jurisdiction, context),
        "verification": _generate_verification_clause(jurisdiction, context),
        "prayer": _generate_prayer_clause(jurisdiction, context),
        "facts": _generate_facts_clause(jurisdiction, context),
        "grounds": _generate_grounds_clause(jurisdiction, context),
        "deponent_signature": _generate_signature_block(jurisdiction, context),
    }

    result = clause_templates.get(clause_type)
    if result:
        return result

    # For custom clause types, return a structured placeholder
    return {
        "clause_text": f"[{clause_type.upper()}]\n\n{context}",
        "citations": [],
        "risk_indicators": [],
        "clause_type": clause_type,
    }


def select_template(
    document_type: str,
    jurisdiction: str,
    matter_context: dict,
) -> str:
    """
    Select the appropriate template for a given document type and jurisdiction.

    Args:
        document_type: Type of document (e.g., 'Affidavit', 'Legal Notice')
        jurisdiction: Court jurisdiction code
        matter_context: Additional context about the matter

    Returns:
        Template identifier string
    """
    normalized = DOC_TYPE_ALIASES.get(document_type, document_type.lower())
    template = TEMPLATE_MAP.get((normalized, jurisdiction))
    if template:
        return template
    # Fall back to any matching document type
    for (dt, _), tmpl in TEMPLATE_MAP.items():
        if dt == normalized:
            return tmpl
    return "affidavit_mh.txt"


def validate_against_sfe(document_dict: dict, jurisdiction: str) -> dict:
    """
    Run document through the Symbolic Formatting Engine for validation.

    The SFE is a deterministic rule engine — it checks margins, fonts,
    required sections, stamp paper values, and all court-specific rules.

    Args:
        document_dict: Document with 'sections', 'metadata', and 'formatting' keys
        jurisdiction: Court jurisdiction code

    Returns:
        Dict with is_valid, acceptance_score, fatal_defects, curable_defects
    """
    try:
        sfe = SymbolicFormattingEngine(jurisdiction)
        result = sfe.validate(document_dict)
        return {
            "is_valid": result.is_valid,
            "acceptance_score": result.acceptance_score,
            "fatal_defects": result.fatal_defects,
            "curable_defects": result.curable_defects,
            "details": result.details,
        }
    except Exception as e:
        logger.error(f"SFE validation error: {e}")
        return {
            "is_valid": False,
            "acceptance_score": 0.0,
            "fatal_defects": [f"SFE validation error: {str(e)}"],
            "curable_defects": [],
            "details": {},
        }


def search_legal_corpus(
    query: str,
    search_type: str = "statutes",
    limit: int = 5,
) -> dict:
    """
    Search Indian legal corpus for statutes and case law.

    Args:
        query: Search query (e.g., 'cheque dishonour', 'property dispute')
        search_type: 'statutes' or 'case_law'
        limit: Maximum results to return

    Returns:
        Dict with search results
    """
    client = CorpusClient()
    if search_type == "case_law":
        results = client.search_case_law(query, limit)
    else:
        results = client.search_statutes(query, limit)
    return {"results": results, "query": query, "search_type": search_type}


# ---------------------------------------------------------------------------
# Clause generation helpers (deterministic templates with variable injection)
# ---------------------------------------------------------------------------

def _generate_cause_title(jurisdiction: str, context: str) -> dict:
    """Generate cause title / case header."""
    return {
        "clause_text": (
            "IN THE MATTER OF:\n\n"
            "{petitioner_name}\n"
            "{petitioner_address}\n"
            "                                                    ... PETITIONER/APPLICANT\n\n"
            "VERSUS\n\n"
            "{respondent_name}\n"
            "{respondent_address}\n"
            "                                                    ... RESPONDENT/OPPONENT"
        ),
        "citations": [],
        "risk_indicators": [],
        "clause_type": "cause_title",
    }


def _generate_jurisdiction_clause(jurisdiction: str, context: str) -> dict:
    """Generate jurisdiction clause."""
    jurisdiction_statutes = {
        "MH-DISTRICT": "Section 9 of the Code of Civil Procedure, 1908",
        "MH-HC": "Article 226 of the Constitution of India",
        "DL-DISTRICT": "Section 9 of the Code of Civil Procedure, 1908",
        "IN-SC": "Article 32 of the Constitution of India",
    }
    statute = jurisdiction_statutes.get(jurisdiction, "Section 9 CPC, 1908")
    return {
        "clause_text": (
            f"This Hon'ble Court has the jurisdiction to try and entertain "
            f"the present matter under {statute}. The cause of action has "
            f"arisen within the territorial jurisdiction of this Hon'ble Court."
        ),
        "citations": [statute],
        "risk_indicators": [],
        "clause_type": "jurisdiction_clause",
    }


def _generate_verification_clause(jurisdiction: str, context: str) -> dict:
    """Generate verification clause (mandatory in all Indian courts)."""
    return {
        "clause_text": (
            "VERIFICATION\n\n"
            "I, {deponent_name}, the above-named deponent, do hereby verify "
            "that the contents of paragraphs 1 to {last_paragraph_number} of "
            "the above {document_type} are true and correct to my knowledge "
            "and belief. No part of it is false and nothing material has been "
            "concealed therefrom.\n\n"
            "Verified at {city_name} on this {day} day of {month}, {year}."
        ),
        "citations": ["Order VI Rule 15 of the Code of Civil Procedure, 1908"],
        "risk_indicators": [],
        "clause_type": "verification",
    }


def _generate_prayer_clause(jurisdiction: str, context: str) -> dict:
    """Generate prayer / relief clause."""
    return {
        "clause_text": (
            "PRAYER\n\n"
            "In the premises aforesaid, it is most respectfully prayed that "
            "this Hon'ble Court may be pleased to:\n\n"
            "(a) {primary_relief};\n\n"
            "(b) {secondary_relief};\n\n"
            "(c) Grant costs of this proceeding in favour of the Petitioner;\n\n"
            "(d) Pass such other and further orders as this Hon'ble Court may "
            "deem fit and proper in the facts and circumstances of the case."
        ),
        "citations": [],
        "risk_indicators": [],
        "clause_type": "prayer",
    }


def _generate_facts_clause(jurisdiction: str, context: str) -> dict:
    """Generate facts section."""
    return {
        "clause_text": (
            "FACTS\n\n"
            "The facts giving rise to the present filing are as follows:\n\n"
            f"{context}"
        ),
        "citations": [],
        "risk_indicators": [],
        "clause_type": "facts",
    }


def _generate_grounds_clause(jurisdiction: str, context: str) -> dict:
    """Generate grounds section."""
    return {
        "clause_text": (
            "GROUNDS\n\n"
            "The present application is filed on the following grounds:\n\n"
            f"{context}"
        ),
        "citations": [],
        "risk_indicators": [],
        "clause_type": "grounds",
    }


def _generate_signature_block(jurisdiction: str, context: str) -> dict:
    """Generate deponent/advocate signature block."""
    return {
        "clause_text": (
            "DEPONENT\n\n"
            "{deponent_name}\n\n"
            "Through Advocate:\n"
            "{advocate_name}\n"
            "{bar_council_enrollment}\n"
            "{advocate_address}\n"
            "{advocate_phone}"
        ),
        "citations": [],
        "risk_indicators": [],
        "clause_type": "deponent_signature",
    }


# ---------------------------------------------------------------------------
from tools.hitl_tool import ask_user_options

# ADK Agent definition
# ---------------------------------------------------------------------------

drafter_tools = [
    FunctionTool(func=generate_clause),
    FunctionTool(func=select_template),
    FunctionTool(func=validate_against_sfe),
    FunctionTool(func=search_legal_corpus),
    FunctionTool(func=ask_user_options),
]

import os
DRAFTER_MODEL = os.getenv("CLAUSELY_MODEL", "gemini-3.5-flash")

drafter_agent = Agent(
    name="clausely_drafter",
    model=DRAFTER_MODEL,
    description=(
        "Expert Indian legal document drafter. Converts legal intent into "
        "structured court documents using the Symbolic Formatting Engine "
        "for deterministic formatting."
    ),
    instruction="""You are the Clausely Drafter Agent — an expert Indian legal document generator.

Your job:
1. Read the matter context provided by the orchestrator.
2. If ANY critical facts (e.g., date of cause of action, names of parties, specific terms, or jurisdictional facts) are missing or ambiguous, you MUST NOT guess or assume them. Call the `ask_user_options` tool to present a multiple-choice question to the user (providing exactly 4-5 relevant choices plus "Others") to clarify the information.
3. Select the appropriate template using the select_template tool.
4. Search the legal corpus for relevant statutes and precedents using search_legal_corpus.
5. Generate each required clause for the jurisdiction using generate_clause.
6. Assemble the complete document with all sections in the correct court-mandated order.
7. Run validation against the SFE using validate_against_sfe.
8. If fatal defects are found, regenerate the affected clauses and re-validate.
9. Return the complete, validated document text with acceptance score.

CRITICAL RULES:
- NEVER assume missing information or facts. If something is missing, ask.
- When calling `ask_user_options`, always provide exactly 4-5 specific legal options plus a standard "Others" option.
- NEVER output unformatted text. Always use the structured tools.
- Always validate before returning. Target acceptance score >= 85.
- Always include ALL mandatory sections for the jurisdiction.
- Cite statutes accurately. Reference BNS 2024 (not IPC) for Maharashtra courts.
- Include the verification clause — it is MANDATORY in all Indian courts.
- Use proper Indian legal terminology and honorifics (Hon'ble Court, etc.).

Return your final output as a JSON with keys:
- document_text: the full formatted document
- acceptance_score: float 0-100
- fatal_defects: list of strings
- curable_defects: list of strings
- citations: list of all statutes cited
- template_used: template identifier
""",
    tools=drafter_tools,
)


"""
Clausely Case Base Agent — Persistent Legal Memory with Firestore.

Uses Firestore for persistent storage of:
- Matters (documents, scores, strategy memos)
- Reward signals (RL feedback from filing outcomes)
- Firm playbooks (custom rules per law firm)

This is the institutional memory moat — Clausely gets smarter with
every matter processed.
"""

from __future__ import annotations

import os
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

logger = logging.getLogger("clausely.case_base")


# ---------------------------------------------------------------------------
# Firestore client (lazy, with in-memory fallback)
# ---------------------------------------------------------------------------

_firestore_db = None
_in_memory_store: Dict[str, Dict[str, Any]] = {
    "matters": {},
    "reward_signals": [],
    "playbooks": {},
}


def _get_db():
    """Lazily initialize Firestore client."""
    global _firestore_db
    if _firestore_db is not None:
        return _firestore_db
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        if not firebase_admin._apps:
            cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                firebase_admin.initialize_app()
        _firestore_db = firestore.client()
        return _firestore_db
    except Exception as e:
        logger.warning(f"Firestore unavailable, using in-memory store: {e}")
        return None


# ---------------------------------------------------------------------------
# ADK FunctionTool definitions
# ---------------------------------------------------------------------------

def save_matter_to_case_base(
    matter_id: str,
    document_type: str,
    jurisdiction: str,
    document_text: str,
    acceptance_score: float,
    strategy_memo: str = "",
    filing_date: str = "",
    metadata: dict = None,
) -> dict:
    """
    Save a complete matter to the Clausely Case Base (Firestore).

    This creates a persistent record that can be retrieved for future
    reference, enabling institutional memory across sessions.

    Args:
        matter_id: Unique matter identifier (e.g., CLY-A1B2C3D4)
        document_type: Type of document (e.g., 'affidavit')
        jurisdiction: Court jurisdiction code
        document_text: Full document text
        acceptance_score: SFE acceptance score (0-100)
        strategy_memo: Strategic analysis memo
        filing_date: Date of filing (YYYY-MM-DD)
        metadata: Additional matter metadata

    Returns:
        Dict confirming save with matter_id
    """
    matter_doc = {
        "matter_id": matter_id,
        "document_type": document_type,
        "jurisdiction": jurisdiction,
        "document_text": document_text,
        "acceptance_score": acceptance_score,
        "strategy_memo": strategy_memo,
        "filing_date": filing_date,
        "metadata": metadata or {},
        "status": "draft",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "reward_signals": [],
    }

    db = _get_db()
    if db is not None:
        try:
            from firebase_admin import firestore as fs
            matter_doc["created_at"] = fs.SERVER_TIMESTAMP
            db.collection("matters").document(matter_id).set(matter_doc)
            logger.info(f"Matter saved to Firestore: {matter_id}")
        except Exception as e:
            logger.warning(f"Firestore write failed, saving in-memory: {e}")
            _in_memory_store["matters"][matter_id] = matter_doc
    else:
        _in_memory_store["matters"][matter_id] = matter_doc
        logger.info(f"Matter saved in-memory: {matter_id}")

    return {"saved": True, "matter_id": matter_id}


def log_reward_signal(
    matter_id: str,
    signal_type: str,
    reward_value: float,
    details: str = "",
) -> dict:
    """
    Log an RL reward signal for self-evolution.

    This is how Clausely learns from real court outcomes. Every filing
    result feeds back into the system.

    Reward values:
        +3.0  — Document accepted by court registry
        +0.5  — Document filed successfully
        +0.5  — Minor edit by advocate
        +0.2  — Major edit by advocate
        -3.0  — Document rejected

    Args:
        matter_id: The matter this signal relates to
        signal_type: Type of signal (accepted, rejected, filed, edited_minor, edited_major)
        reward_value: Numeric reward value
        details: Human-readable description

    Returns:
        Dict confirming signal was logged
    """
    signal = {
        "matter_id": matter_id,
        "signal_type": signal_type,
        "reward_value": reward_value,
        "details": details,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    db = _get_db()
    if db is not None:
        try:
            from firebase_admin import firestore as fs
            signal["timestamp"] = fs.SERVER_TIMESTAMP
            db.collection("reward_signals").add(signal)
        except Exception as e:
            logger.warning(f"Firestore write failed: {e}")
            _in_memory_store["reward_signals"].append(signal)
    else:
        _in_memory_store["reward_signals"].append(signal)

    return {"logged": True, "signal": signal}


def retrieve_similar_matters(
    jurisdiction: str,
    document_type: str,
    cause_of_action: str = "",
    limit: int = 5,
) -> dict:
    """
    Retrieve similar past matters from the Case Base.

    This is the institutional memory moat — past filings inform future
    drafting, producing increasingly accurate documents.

    Args:
        jurisdiction: Court jurisdiction code
        document_type: Type of document
        cause_of_action: Description of the cause (used for relevance matching)
        limit: Maximum results to return

    Returns:
        Dict with list of similar past matters
    """
    db = _get_db()
    results: List[Dict[str, Any]] = []

    if db is not None:
        try:
            query = (
                db.collection("matters")
                .where("jurisdiction", "==", jurisdiction)
                .where("document_type", "==", document_type.lower())
                .limit(limit)
            )
            docs = query.stream()
            results = [doc.to_dict() for doc in docs]
        except Exception as e:
            logger.warning(f"Firestore query failed: {e}")

    if not results:
        # Fall back to in-memory store
        for mid, matter in _in_memory_store["matters"].items():
            if (
                matter.get("jurisdiction") == jurisdiction
                and matter.get("document_type", "").lower() == document_type.lower()
            ):
                results.append(matter)
                if len(results) >= limit:
                    break

    # Integrate versatile real-time RAG Search pipeline
    try:
        from tools.realtime_rag import RealtimeRAGClient
        rag_client = RealtimeRAGClient()
        recent_cases = rag_client.fetch_yesterdays_case_info(cause_of_action or document_type)
        # Merge recent cases as similar precedents
        for case in recent_cases:
            results.insert(0, {
                "matter_id": case["document_id"],
                "document_type": document_type,
                "jurisdiction": jurisdiction,
                "document_text": case["snippet"],
                "acceptance_score": 95.0,
                "metadata": {
                    "source": case["source"],
                    "url": case["url"],
                    "publish_date": case["date"]
                }
            })
    except Exception as e:
        logger.warning(f"Realtime RAG search integration failed: {e}")

    return {
        "similar_matters": results[:limit],
        "count": len(results[:limit]),
        "jurisdiction": jurisdiction,
        "document_type": document_type,
    }


def get_firm_playbook(firm_id: str = "default") -> dict:
    """
    Retrieve firm-specific drafting preferences and rules.

    Playbooks contain custom clause preferences, signature formats,
    and matter handling protocols specific to a law firm.

    Args:
        firm_id: Firm identifier (defaults to 'default')

    Returns:
        Dict with firm playbook rules
    """
    db = _get_db()

    if db is not None:
        try:
            doc = db.collection("playbooks").document(firm_id).get()
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            logger.warning(f"Firestore read failed: {e}")

    # Return default playbook
    return _in_memory_store.get("playbooks", {}).get(firm_id, {
        "firm_id": firm_id,
        "preferences": {
            "default_language": "en",
            "include_hindi_translation": False,
            "signature_format": "standard",
            "letterhead_style": "formal",
        },
        "custom_clauses": {},
        "notes": "Default playbook — customize via Clausely dashboard.",
    })


def get_matter_history(matter_id: str) -> dict:
    """
    Get complete history for a matter including all reward signals.

    Args:
        matter_id: The matter ID to look up

    Returns:
        Dict with matter details and reward signal history
    """
    db = _get_db()
    matter = None
    signals: List[Dict[str, Any]] = []

    if db is not None:
        try:
            doc = db.collection("matters").document(matter_id).get()
            if doc.exists:
                matter = doc.to_dict()
            sig_docs = (
                db.collection("reward_signals")
                .where("matter_id", "==", matter_id)
                .stream()
            )
            signals = [d.to_dict() for d in sig_docs]
        except Exception as e:
            logger.warning(f"Firestore read failed: {e}")

    if matter is None:
        matter = _in_memory_store["matters"].get(matter_id)
    if not signals:
        signals = [
            s for s in _in_memory_store["reward_signals"]
            if s.get("matter_id") == matter_id
        ]

    cumulative_reward = sum(s.get("reward_value", 0.0) for s in signals)

    return {
        "matter": matter,
        "reward_signals": signals,
        "cumulative_reward": cumulative_reward,
        "found": matter is not None,
    }


# ---------------------------------------------------------------------------
# ADK Agent definition
# ---------------------------------------------------------------------------

case_base_tools = [
    FunctionTool(func=save_matter_to_case_base),
    FunctionTool(func=log_reward_signal),
    FunctionTool(func=retrieve_similar_matters),
    FunctionTool(func=get_firm_playbook),
    FunctionTool(func=get_matter_history),
]

import os
CASE_BASE_MODEL = os.getenv("CLAUSELY_MODEL", "gemini-3.5-flash")

case_base_agent = Agent(
    name="clausely_case_base",
    model=CASE_BASE_MODEL,
    description=(
        "Persistent legal memory agent using Firestore. Stores matters, "
        "retrieves similar precedents, and logs RL reward signals for "
        "self-evolution."
    ),
    instruction="""You are the Clausely Case Base Agent — the institutional memory of Clausely.

Your job:
1. BEFORE drafting: Retrieve similar past matters using retrieve_similar_matters.
   Pass relevant precedents and patterns to inform the current drafting.
2. Check the firm playbook for custom preferences using get_firm_playbook.
3. AFTER drafting: Save the completed document using save_matter_to_case_base.
4. Log an initial reward signal for the draft creation.
5. Return institutional insights from the firm's history.

This memory makes Clausely smarter with every matter filed.
The more matters processed, the stronger the institutional knowledge.

Always save matters — even drafts. The reward signal system tracks
outcomes over time to improve future generation quality.
""",
    tools=case_base_tools,
)

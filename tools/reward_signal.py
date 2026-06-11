"""
Clausely Reward Signal — RL reward signal logger for self-evolution.

Every filing outcome feeds back into the system:
    +3.0  — Document accepted by court registry
    +0.5  — Document filed successfully
    +0.5  — Minor edit made by advocate (learning signal)
    +0.2  — Major edit made (indicates weaker generation)
    -3.0  — Document rejected by court registry

These signals accumulate in Firestore and drive continuous improvement.
This is the compounding moat: Clausely gets smarter with every Indian
court filing processed.
"""

from __future__ import annotations

import os
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger("clausely.reward")


# ---------------------------------------------------------------------------
# Reward value definitions
# ---------------------------------------------------------------------------

REWARD_VALUES: Dict[str, float] = {
    "filed": 0.5,
    "accepted": 3.0,
    "rejected": -3.0,
    "edited_minor": 0.5,
    "edited_major": 0.2,
    "template_reused": 0.3,
    "client_approved": 1.0,
}


# ---------------------------------------------------------------------------
# In-memory signal store (used when Firestore is not available)
# ---------------------------------------------------------------------------

_in_memory_signals: List[Dict[str, Any]] = []


# ---------------------------------------------------------------------------
# Firestore integration (lazy initialization)
# ---------------------------------------------------------------------------

_firestore_db = None


def _get_firestore_db():
    """Lazily initialize Firestore client."""
    global _firestore_db
    if _firestore_db is not None:
        return _firestore_db

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        if not firebase_admin._apps:
            # Try to initialize with default credentials
            cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                # Try Application Default Credentials
                firebase_admin.initialize_app()

        _firestore_db = firestore.client()
        return _firestore_db
    except Exception as e:
        logger.warning(f"Firestore not available, using in-memory store: {e}")
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def log_signal(
    matter_id: str,
    signal_type: str,
    reward_value: Optional[float] = None,
    details: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Log a reward signal for a matter.

    Args:
        matter_id: The Clausely matter ID (e.g., CLY-A1B2C3D4)
        signal_type: One of: filed, accepted, rejected, edited_minor, edited_major
        reward_value: Override default reward value (optional)
        details: Human-readable description of what happened
        metadata: Additional context (e.g., which clauses were edited)

    Returns:
        Dict confirming the signal was logged.
    """
    if reward_value is None:
        reward_value = REWARD_VALUES.get(signal_type, 0.0)

    signal = {
        "matter_id": matter_id,
        "signal_type": signal_type,
        "reward_value": reward_value,
        "details": details,
        "metadata": metadata or {},
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    # Try Firestore first, fall back to in-memory
    db = _get_firestore_db()
    if db is not None:
        try:
            from firebase_admin import firestore as fs
            signal_for_db = {**signal, "timestamp": fs.SERVER_TIMESTAMP}
            db.collection("reward_signals").add(signal_for_db)
            logger.info(f"Reward signal logged to Firestore: {signal_type} = {reward_value}")
        except Exception as e:
            logger.warning(f"Firestore write failed, storing in-memory: {e}")
            _in_memory_signals.append(signal)
    else:
        _in_memory_signals.append(signal)
        logger.info(f"Reward signal logged in-memory: {signal_type} = {reward_value}")

    return {"logged": True, "signal": signal}


def get_signals_for_matter(matter_id: str) -> List[Dict[str, Any]]:
    """Retrieve all reward signals for a specific matter."""
    db = _get_firestore_db()
    if db is not None:
        try:
            docs = (
                db.collection("reward_signals")
                .where("matter_id", "==", matter_id)
                .order_by("timestamp")
                .stream()
            )
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            logger.warning(f"Firestore read failed: {e}")

    # Fall back to in-memory
    return [s for s in _in_memory_signals if s["matter_id"] == matter_id]


def get_aggregate_stats() -> Dict[str, Any]:
    """Get aggregate reward statistics across all matters."""
    db = _get_firestore_db()
    signals: List[Dict[str, Any]] = []

    if db is not None:
        try:
            docs = db.collection("reward_signals").stream()
            signals = [doc.to_dict() for doc in docs]
        except Exception:
            signals = _in_memory_signals
    else:
        signals = _in_memory_signals

    if not signals:
        return {
            "total_signals": 0,
            "total_reward": 0.0,
            "average_reward": 0.0,
            "signal_counts": {},
        }

    total_reward = sum(s.get("reward_value", 0.0) for s in signals)
    signal_counts: Dict[str, int] = {}
    for s in signals:
        st = s.get("signal_type", "unknown")
        signal_counts[st] = signal_counts.get(st, 0) + 1

    return {
        "total_signals": len(signals),
        "total_reward": total_reward,
        "average_reward": total_reward / len(signals) if signals else 0.0,
        "signal_counts": signal_counts,
    }


def compute_matter_score(matter_id: str) -> float:
    """Compute cumulative reward score for a matter."""
    signals = get_signals_for_matter(matter_id)
    return sum(s.get("reward_value", 0.0) for s in signals)

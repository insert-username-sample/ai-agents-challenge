# =====================================================================
# CLAUSELY: MACHINE-READABLE EVIDENCE LEDGER (RULE-20)
# =====================================================================
# Every strategist run MUST emit a structured ledger recording each
# agent's claim, grounding verification result, P_assumption score,
# and downstream blocking status. This is the audit trail that makes
# the simulation legally defensible and deterministic.
# =====================================================================

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("clausely.evidence_ledger")


@dataclass
class EvidenceLedgerEntry:
    """A single auditable evidence record from a strategist micro-step."""

    agent_name: str
    step_id: str
    claim: str
    claim_type: str  # precedent, statute, procedure, fact
    source_count: int
    verified: bool
    p_assumption: float
    downstream_blocked: bool
    grounding_sources: List[str] = field(default_factory=list)
    contradiction_detected: bool = False
    contradiction_detail: str = ""
    error: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


@dataclass
class EvidenceLedger:
    """
    Complete evidence ledger for a single strategist simulation run.

    RULE-20 mandates: every strategist run MUST emit a ledger of
    agent_name, step_id, claim, claim_type, source_count, verified,
    P_assumption, and downstream_blocked status.
    """

    case_title: str
    run_id: str
    entries: List[EvidenceLedgerEntry] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def add_entry(self, entry: EvidenceLedgerEntry) -> None:
        """Append an entry to the ledger."""
        self.entries.append(entry)

    def add_from_step_audit(self, audit_dict: Dict[str, Any]) -> None:
        """
        Create an entry from a StepAudit.to_dict() output.

        This bridges the strategist_harness.StepAudit format into the
        canonical evidence ledger format.
        """
        entry = EvidenceLedgerEntry(
            agent_name=audit_dict.get("agent_name", "unknown"),
            step_id=audit_dict.get("step_id", "unknown"),
            claim=audit_dict.get("query", ""),
            claim_type=audit_dict.get("claim_type", "fact"),
            source_count=audit_dict.get("source_count", 0),
            verified=audit_dict.get("verified", False),
            p_assumption=audit_dict.get("p_assumption", 1.0),
            downstream_blocked=audit_dict.get("downstream_blocked", False),
            grounding_sources=audit_dict.get("sources", []),
            contradiction_detected=audit_dict.get("contradiction_detected", False),
            contradiction_detail=audit_dict.get("contradiction_detail", ""),
            error=audit_dict.get("error", ""),
        )
        self.entries.append(entry)

    # -----------------------------------------------------------------
    # SUMMARY METRICS
    # -----------------------------------------------------------------

    @property
    def total_steps(self) -> int:
        return len(self.entries)

    @property
    def verified_count(self) -> int:
        return sum(1 for e in self.entries if e.verified)

    @property
    def blocked_count(self) -> int:
        return sum(1 for e in self.entries if e.downstream_blocked)

    @property
    def contradiction_count(self) -> int:
        return sum(1 for e in self.entries if e.contradiction_detected)

    @property
    def weighted_p_assumption(self) -> float:
        if not self.entries:
            return 1.0
        return sum(e.p_assumption for e in self.entries) / len(self.entries)

    @property
    def grounded_success_estimate(self) -> float:
        return max(0.0, min(100.0, (1.0 - self.weighted_p_assumption) * 100.0))

    def summary(self) -> Dict[str, Any]:
        """Return a summary dict of the ledger metrics."""
        return {
            "case_title": self.case_title,
            "run_id": self.run_id,
            "total_steps": self.total_steps,
            "verified_steps": self.verified_count,
            "unverified_steps": self.total_steps - self.verified_count,
            "blocked_steps": self.blocked_count,
            "contradictions_detected": self.contradiction_count,
            "weighted_p_assumption": round(self.weighted_p_assumption, 4),
            "grounded_success_estimate": round(self.grounded_success_estimate, 2),
            "created_at": self.created_at,
        }

    # -----------------------------------------------------------------
    # SERIALIZATION
    # -----------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_title": self.case_title,
            "run_id": self.run_id,
            "created_at": self.created_at,
            "summary": self.summary(),
            "entries": [e.to_dict() for e in self.entries],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def save(self, output_dir: str) -> str:
        """
        Save the ledger as a JSON file.

        Args:
            output_dir: Directory to save the ledger file.

        Returns:
            Path to the saved ledger file.
        """
        os.makedirs(output_dir, exist_ok=True)
        filename = f"evidence_ledger_{self.run_id}.json"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_json())

        logger.info(f"[RULE-20] Evidence ledger saved: {filepath}")
        return filepath

    def to_markdown(self) -> str:
        """Render the ledger as a markdown table for human review."""
        lines = [
            f"# Evidence Ledger: {self.case_title}",
            f"**Run ID:** {self.run_id}",
            f"**Created:** {self.created_at}",
            "",
            "## Summary",
            f"- Total steps: {self.total_steps}",
            f"- Verified: {self.verified_count}",
            f"- Unverified: {self.total_steps - self.verified_count}",
            f"- Blocked: {self.blocked_count}",
            f"- Contradictions: {self.contradiction_count}",
            f"- Weighted P_assumption: {self.weighted_p_assumption:.4f}",
            f"- Grounded success estimate: {self.grounded_success_estimate:.1f}%",
            "",
            "## Entries",
            "",
            "| Step | Agent | Type | Verified | P_assumption | Sources | Blocked |",
            "|------|-------|------|----------|-------------|---------|---------|",
        ]

        for e in self.entries:
            status = "PASS" if e.verified else "FAIL"
            blocked = "BLOCKED" if e.downstream_blocked else "-"
            lines.append(
                f"| {e.step_id} | {e.agent_name} | {e.claim_type} | "
                f"{status} | {e.p_assumption:.2f} | {e.source_count} | {blocked} |"
            )

        return "\n".join(lines)

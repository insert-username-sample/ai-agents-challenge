# =====================================================================
# CLAUSELY: EIGHT-AGENT STRATEGIST MICRO-STEP HARNESS
# =====================================================================
# This harness stress-tests the strategist from intake to judge output.
# It is intentionally stricter than the ADK prompts: each canonical
# agent must contribute source-bearing grounded micro-steps, and every
# dependent downstream phase fails closed when an upstream premise is
# unverified.
# =====================================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from agents.grounding_engine import verify_grounding
from agents.harness_rules import (
    CANONICAL_STRATEGIST_AGENTS,
    GroundingResult,
    HarnessViolation,
    require_canonical_agent,
)


GroundingCallable = Callable[..., GroundingResult]


@dataclass(frozen=True)
class StrategistMicroStep:
    """A smallest auditable legal deduction made by one canonical agent."""

    step_id: str
    agent_name: str
    phase: str
    claim_type: str
    claim: str
    critical: bool = True
    depends_on: Tuple[str, ...] = ()

    def validate(self) -> None:
        require_canonical_agent(self.agent_name)
        if not self.step_id.strip():
            raise HarnessViolation("RULE-20", "Micro-step is missing step_id.")
        if not self.claim.strip():
            raise HarnessViolation("RULE-01", f"{self.step_id} has an empty claim.")
        if self.claim_type not in {"precedent", "statute", "procedure", "fact"}:
            raise HarnessViolation(
                "RULE-20",
                f"{self.step_id} has unsupported claim_type '{self.claim_type}'.",
            )


@dataclass(frozen=True)
class StrategistHarnessPolicy:
    """Strictness controls for the one-case strategist harness."""

    require_all_agents: bool = True
    min_steps_per_agent: int = 2
    require_sources: bool = True
    fail_closed_on_unverified: bool = True
    retry_backoff_seconds: Tuple[float, ...] = (0,)
    request_timeout_ms: int = 12000
    max_critical_p_assumption: float = 0.05


@dataclass
class StepAudit:
    step: StrategistMicroStep
    result: GroundingResult
    downstream_blocked: bool = False
    blocked_by: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        payload = self.result.to_dict()
        payload.update({
            "step_id": self.step.step_id,
            "phase": self.step.phase,
            "claim_type": self.step.claim_type,
            "critical": self.step.critical,
            "depends_on": list(self.step.depends_on),
            "downstream_blocked": self.downstream_blocked,
            "blocked_by": self.blocked_by,
        })
        return payload


def build_kesavananda_micro_steps(case_context: Dict[str, Any]) -> List[StrategistMicroStep]:
    """Build a complete eight-agent micro-step plan for one constitutional case."""

    title = case_context["title"]
    citation = case_context["citation"]
    subject = case_context["subject"]
    jurisdiction = case_context["jurisdiction"]
    precedents = case_context.get("precedents", [])

    return [
        StrategistMicroStep(
            "P1",
            "petitioner_agent",
            "petitioner_merits",
            "precedent",
            f"{title} {citation} basic structure doctrine ratio decidendi",
        ),
        StrategistMicroStep(
            "P2",
            "petitioner_agent",
            "petitioner_relief",
            "statute",
            "Article 368 Constitution of India parliamentary amendment power fundamental rights",
            depends_on=("P1",),
        ),
        StrategistMicroStep(
            "O1",
            "opponent_agent",
            "opponent_precedent_attack",
            "precedent",
            precedents[0] if precedents else "Golaknath v. State of Punjab (1967) 2 SCR 762",
        ),
        StrategistMicroStep(
            "O2",
            "opponent_agent",
            "opponent_counter_authority",
            "precedent",
            precedents[1] if len(precedents) > 1 else "Sajjan Singh v. State of Rajasthan AIR 1965 SC 845",
            depends_on=("O1",),
        ),
        StrategistMicroStep(
            "R1",
            "reviewer_agent",
            "reviewer_fact_lock",
            "fact",
            f"{title} challenged Kerala Land Reforms Act and constitutional amendments",
            depends_on=("P1",),
        ),
        StrategistMicroStep(
            "R2",
            "reviewer_agent",
            "reviewer_issue_lock",
            "fact",
            f"{subject} decided by a 13 judge bench of the Supreme Court of India",
            depends_on=("R1",),
        ),
        StrategistMicroStep(
            "V1",
            "verifier_agent",
            "verifier_primary_citation",
            "precedent",
            f"{title} {citation}",
            depends_on=("P1",),
        ),
        StrategistMicroStep(
            "V2",
            "verifier_agent",
            "verifier_statutory_context",
            "statute",
            "Twenty-fourth Twenty-fifth and Twenty-ninth Amendments Constitution of India Kesavananda Bharati",
            depends_on=("P2", "V1"),
        ),
        StrategistMicroStep(
            "OB1",
            "objector_agent",
            "objector_maintainability",
            "procedure",
            f"{jurisdiction} writ petition maintainability for constitutional amendment challenge",
            depends_on=("V1",),
        ),
        StrategistMicroStep(
            "OB2",
            "objector_agent",
            "objector_ninth_schedule",
            "procedure",
            "Ninth Schedule judicial review basic structure doctrine India",
            depends_on=("OB1",),
        ),
        StrategistMicroStep(
            "PR1",
            "presenter_agent",
            "presenter_binding_synthesis",
            "precedent",
            "Kesavananda Bharati binding precedent basic structure doctrine subsequent Indian courts",
            depends_on=("P1", "V1", "OB2"),
        ),
        StrategistMicroStep(
            "PR2",
            "presenter_agent",
            "presenter_follow_on_authority",
            "precedent",
            "Minerva Mills Waman Rao I R Coelho basic structure doctrine India",
            depends_on=("PR1",),
        ),
        StrategistMicroStep(
            "J1",
            "judge_agent",
            "judge_outcome_basis",
            "precedent",
            "Kesavananda Bharati held Parliament cannot alter basic structure of Constitution",
            depends_on=("PR1", "PR2"),
        ),
        StrategistMicroStep(
            "J2",
            "judge_agent",
            "judge_probability_constraints",
            "fact",
            "Kesavananda Bharati was decided by narrow majority 7 6 Supreme Court India",
            depends_on=("J1",),
        ),
        # --- DRAFTER AGENT: Exclusive AST compiler ---
        StrategistMicroStep(
            "D1",
            "drafter_agent",
            "drafter_ast_compilation",
            "procedure",
            f"{title} compile Legal AST from verified swarm outputs with court formatting rules {jurisdiction}",
            depends_on=("PR2", "J1"),
        ),
        StrategistMicroStep(
            "D2",
            "drafter_agent",
            "drafter_sfe_validation",
            "procedure",
            f"Symbolic Formatting Engine validation for {jurisdiction} court filing requirements margins fonts sections",
            depends_on=("D1",),
        ),
    ]


class StrategistSwarmHarness:
    """Strict start-to-end harness for one strategist case."""

    def __init__(
        self,
        policy: Optional[StrategistHarnessPolicy] = None,
        grounding_fn: GroundingCallable = verify_grounding,
    ) -> None:
        self.policy = policy or StrategistHarnessPolicy()
        self.grounding_fn = grounding_fn

    def execute(
        self,
        case_context: Dict[str, Any],
        steps: Optional[Sequence[StrategistMicroStep]] = None,
    ) -> Dict[str, Any]:
        plan = list(steps or build_kesavananda_micro_steps(case_context))
        self._validate_plan(plan)

        step_audits: List[StepAudit] = []
        result_by_step: Dict[str, StepAudit] = {}

        for step in plan:
            blocked_by = [
                dep for dep in step.depends_on
                if dep in result_by_step and not result_by_step[dep].result.verified
            ]
            if blocked_by and self.policy.fail_closed_on_unverified:
                result = GroundingResult(
                    query=step.claim,
                    agent_name=step.agent_name,
                    node_id=step.step_id,
                    verified=False,
                    p_assumption=1.0,
                    error=f"Blocked by unverified upstream step(s): {', '.join(blocked_by)}",
                )
                audit = StepAudit(step, result, downstream_blocked=True, blocked_by=blocked_by)
            else:
                result = self.grounding_fn(
                    agent_name=step.agent_name,
                    node_id=step.step_id,
                    claim=step.claim,
                    claim_type=step.claim_type,
                    require_sources=self.policy.require_sources,
                    retry_backoff_seconds=self.policy.retry_backoff_seconds,
                    request_timeout_ms=self.policy.request_timeout_ms,
                )
                audit = StepAudit(step, result)
            step_audits.append(audit)
            result_by_step[step.step_id] = audit

        return self._build_report(case_context, step_audits)

    def _validate_plan(self, steps: Sequence[StrategistMicroStep]) -> None:
        for step in steps:
            step.validate()

        if self.policy.require_all_agents:
            counts = {agent: 0 for agent in CANONICAL_STRATEGIST_AGENTS}
            for step in steps:
                counts[step.agent_name] += 1
            missing = [a for a, count in counts.items() if count < self.policy.min_steps_per_agent]
            if missing:
                raise HarnessViolation(
                    "RULE-16",
                    "Missing required micro-step coverage for: " + ", ".join(missing),
                )

        seen_ids: set[str] = set()
        for step in steps:
            if step.step_id in seen_ids:
                raise HarnessViolation("RULE-20", f"Duplicate step_id '{step.step_id}'.")
            seen_ids.add(step.step_id)
            for dep in step.depends_on:
                if dep not in seen_ids:
                    raise HarnessViolation(
                        "RULE-18",
                        f"{step.step_id} depends on '{dep}' before it has executed.",
                    )

    def _build_report(
        self,
        case_context: Dict[str, Any],
        audits: Sequence[StepAudit],
    ) -> Dict[str, Any]:
        total = len(audits)
        verified = sum(1 for a in audits if a.result.verified)
        blocked = sum(1 for a in audits if a.downstream_blocked)
        unverified_critical = [
            a for a in audits if a.step.critical and not a.result.verified
        ]
        source_bearing_verified = sum(
            1 for a in audits if a.result.verified and len(a.result.sources) > 0
        )
        agent_counts = {
            agent: sum(1 for a in audits if a.step.agent_name == agent)
            for agent in CANONICAL_STRATEGIST_AGENTS
        }
        weighted_assumption = (
            sum(a.result.p_assumption for a in audits) / total
            if total else 1.0
        )
        strict_pass = (
            not unverified_critical
            and blocked == 0
            and verified == total
            and source_bearing_verified == total
            and weighted_assumption <= self.policy.max_critical_p_assumption
        )
        grounded_success_estimate = max(0.0, min(100.0, (1.0 - weighted_assumption) * 100.0))

        return {
            "metadata": {
                "case_title": case_context.get("title", "Unknown"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "harness": "eight_agent_micro_step_strategist_harness",
                "canonical_agents": list(CANONICAL_STRATEGIST_AGENTS),
            },
            "strict_gate": {
                "strict_pass": strict_pass,
                "decision": "PASS" if strict_pass else "FAIL_CLOSED",
                "reason": (
                    "All critical micro-steps were source-grounded."
                    if strict_pass
                    else "One or more critical micro-steps were unverified, source-less, or downstream-blocked."
                ),
            },
            "coverage": {
                "total_micro_steps": total,
                "verified_micro_steps": verified,
                "unverified_micro_steps": total - verified,
                "downstream_blocked_steps": blocked,
                "source_bearing_verified_steps": source_bearing_verified,
                "agent_step_counts": agent_counts,
            },
            "risk_metrics": {
                "weighted_p_assumption": round(weighted_assumption, 4),
                "grounded_success_estimate": round(grounded_success_estimate, 2),
                "unverified_critical_steps": [a.step.step_id for a in unverified_critical],
            },
            "evidence_ledger": [a.to_dict() for a in audits],
        }

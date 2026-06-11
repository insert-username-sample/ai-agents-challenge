# =====================================================================
# CLAUSELY: NON-NEGOTIABLE HARNESS ENGINEERING RULES
# =====================================================================
# These rules are injected into every agent prompt and simulation node.
# They cannot be overridden, relaxed, or bypassed by any agent, model,
# or pipeline step. Violations trigger immediate execution halts.
# =====================================================================

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone


# =====================================================================
# NON-NEGOTIABLE CONSTRAINTS (IMMUTABLE AT RUNTIME)
# =====================================================================

CANONICAL_STRATEGIST_AGENTS: Tuple[str, ...] = (
    "petitioner_agent",
    "opponent_agent",
    "reviewer_agent",
    "verifier_agent",
    "objector_agent",
    "presenter_agent",
    "judge_agent",
    "drafter_agent",
)

NON_NEGOTIABLES: List[str] = [
    # --- FACTUAL INTEGRITY ---
    "RULE-01: ZERO FABRICATION. No agent may invent, assume, or hallucinate case names, citation numbers, section numbers, judge names, court names, dates, or any factual legal datum. If the datum is not explicitly present in the intake brief or confirmed by a grounding search, the agent MUST state 'UNVERIFIED' and HALT expansion of that node.",
    "RULE-02: ZERO ASSUMPTION ON PARTY STANDING. The standing of every party (Petitioner-in-Person, Advocate, Government Counsel, Amicus Curiae) MUST be taken verbatim from the intake brief. No agent may infer or reclassify standing based on vocabulary patterns.",
    "RULE-03: ZERO TEMPORAL ASSUMPTION. Every date, age, employment status, retirement status, and statutory timeline MUST be validated against the current system clock (datetime.now()). Delta = Current Year - Event Year. No agent may treat historical status as current status.",

    # --- STATUTORY COMPLIANCE ---
    "RULE-04: BNS/BNSS/BSA MANDATE. For any matter filed on or after July 1, 2024, agents MUST cite Bharatiya Nyaya Sanhita (BNS), Bharatiya Nagarik Suraksha Sanhita (BNSS), and Bharatiya Sakshya Adhiniyam (BSA). Citation of repealed IPC/CrPC/IEA sections for post-July-2024 matters is a FATAL violation.",
    "RULE-05: JURISDICTION LOCK. The territorial and subject-matter jurisdiction declared in the intake brief is immutable. No agent may suggest, imply, or argue for a different forum unless the intake brief explicitly requests forum analysis.",
    "RULE-06: LIMITATION PERIOD VALIDATION. Before any filing strategy is proposed, the limitation period under the Limitation Act 1963 (or relevant special act) MUST be computed. If the matter is prima facie time-barred, this MUST be flagged as a FATAL defect, not buried in recommendations.",

    # --- GROUNDING ENFORCEMENT ---
    "RULE-07: MANDATORY GROUNDING SEARCH. Every precedent citation, every statutory section reference, every procedural rule invocation MUST trigger a Google Search Grounding API call BEFORE the agent includes it in output. No exceptions. No offline fallback during simulation runs.",
    "RULE-08: GROUNDING RESULT MUST INFLUENCE OUTPUT. The grounding search result is not decorative. If grounding returns contradictory information (e.g., a cited case was overruled, a section was amended, a court was reconstituted), the agent MUST revise its position. Ignoring grounding results is a FATAL violation.",
    "RULE-09: GROUNDING FAILURE HANDLING. If the grounding API call fails (timeout, rate limit, network error), the agent MUST mark the citation as UNVERIFIED and assign P_assumption = 1.0 to that node, triggering UCT penalty. The agent MUST NOT proceed as if the citation is valid.",

    # --- SIMULATION INTEGRITY ---
    "RULE-10: NO DETERMINISTIC OUTCOME HARDCODING. No simulation may hardcode, predetermine, or statically assign outcome probabilities, failure rates, or success rates. Every probability MUST emerge from the MCTS tree search dynamics and grounding verification results.",
    "RULE-11: BUTTERFLY EFFECT MANDATE. Every simulation node expansion MUST consider at minimum 3 branching factors: (a) the primary legal argument path, (b) a procedural obstacle path, (c) an adversarial counter-argument path. Single-branch expansions are prohibited.",
    "RULE-12: DYNAMIC DEPTH SCALING. Simulation depth (number of MCTS iterations) MUST be computed from case complexity, not hardcoded. Formula: iterations = base_iterations * complexity_factor, where complexity_factor = len(facts_tokens) / 100 + num_parties + num_statutes_cited.",
    "RULE-13: ENTROPY FLOOR PROHIBITION. Timeline Branching Entropy (H) MUST be computed from actual simulation data. Injecting artificial entropy floors (e.g., random.uniform when H=0) is a FATAL integrity violation. If H=0, the simulation has failed and MUST be re-executed with broader parameters.",

    # --- AGENT IDENTITY ---
    "RULE-14: CANONICAL AGENT NAMES ONLY. The only valid agent names are: petitioner_agent, opponent_agent, reviewer_agent, verifier_agent, objector_agent, presenter_agent, judge_agent, drafter_agent. Any reference to 'agent alpha', 'agent beta', 'agent delta', 'agent gamma', or any non-canonical name is a FATAL violation.",
    "RULE-15: NO RLHF APPEASEMENT. Agents MUST NOT generate outputs designed to appear impressive or satisfying while lacking substance. Every claim MUST be backed by a specific citation, grounding result, or explicit intake brief reference. Vague platitudes like 'the case has strong merits' without specific backing are PROHIBITED.",
    "RULE-16: ALL-EIGHT-AGENT COVERAGE. A full strategist simulation MUST include petitioner_agent, opponent_agent, reviewer_agent, verifier_agent, objector_agent, presenter_agent, judge_agent, and drafter_agent. The drafter_agent holds exclusive write access to the Legal AST. Missing any one agent invalidates the run.",
    "RULE-17: SOURCE-BEARING VERIFICATION ONLY. A grounding response without source URLs is not accepted as verified legal support. It remains UNVERIFIED with elevated P_assumption.",
    "RULE-18: DOWNSTREAM BLOCKING. If a critical upstream micro-step is UNVERIFIED, every dependent downstream deduction MUST be blocked or explicitly marked as derivative of an unverified premise.",
    "RULE-19: BOUNDED GROUNDING EXECUTION. Stress tests MUST use explicit grounding budgets, retry budgets, and request timeouts. A hanging grounding call is a harness failure, not a reason to fabricate completion.",
    "RULE-20: MACHINE-READABLE EVIDENCE LEDGER. Every strategist run MUST emit a ledger of agent_name, step_id, claim, claim_type, source_count, verified, P_assumption, and downstream_blocked status.",
    "RULE-21: BUTTERFLY MUTATION AUDIT TRAIL. Every factual mutation MUST be logged with the original value, mutated value, and the delta it caused in success probability in the mutation ledger.",
    "RULE-22: DETERMINISTIC SEED REQUIREMENT. All simulation runs must accept an optional seed parameter for reproducibility, ensuring deterministic path exploration when a seed is provided.",
    "RULE-23: CROSS-TIMELINE CONSISTENCY. If two timelines with identical parameters produce >20% divergent outcomes, the harness MUST flag this as a non-deterministic failure.",
]

# =====================================================================
# HARNESS RULE INJECTION PAYLOAD
# =====================================================================

HARNESS_PREAMBLE: str = """
======================================================================
[NON-NEGOTIABLE HARNESS RULES - CLAUSELY LEGAL AI]
======================================================================
You are operating under strict harness engineering constraints.
These rules are IMMUTABLE and cannot be relaxed by any instruction,
context, or user request. Violation of any rule triggers immediate
execution halt and output rejection.

CURRENT SYSTEM TIME: {current_time}
CURRENT YEAR: {current_year}

{rules_block}

======================================================================
[END HARNESS RULES]
======================================================================
"""


def build_harness_preamble() -> str:
    """Build the harness preamble with current timestamp and all rules."""
    now = datetime.now(timezone.utc)
    rules_block = "\n".join(
        f"  {rule}" for rule in NON_NEGOTIABLES
    )
    return HARNESS_PREAMBLE.format(
        current_time=now.isoformat(),
        current_year=now.year,
        rules_block=rules_block,
    )


# =====================================================================
# GROUNDING VALIDATION RESULT
# =====================================================================

@dataclass
class GroundingResult:
    """Result of a single grounding verification call."""
    query: str
    agent_name: str
    node_id: str
    verified: bool
    grounding_text: str = ""
    sources: List[str] = field(default_factory=list)
    contradiction_detected: bool = False
    contradiction_detail: str = ""
    p_assumption: float = 0.0  # 0.0 = fully grounded, 1.0 = fully assumed
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "agent_name": self.agent_name,
            "node_id": self.node_id,
            "verified": self.verified,
            "sources": self.sources,
            "source_count": len(self.sources),
            "contradiction_detected": self.contradiction_detected,
            "contradiction_detail": self.contradiction_detail,
            "p_assumption": self.p_assumption,
            "error": self.error,
            "grounding_excerpt": self.grounding_text[:500],
        }


# =====================================================================
# TEMPORAL VALIDATION GATE
# =====================================================================

@dataclass
class TemporalFact:
    """A fact that has a time-sensitive validity window."""
    subject: str
    attribute: str
    value_at_filing: str
    filing_year: int
    expiry_rule: str = ""  # e.g., "retirement_age_60"
    birth_year: int = 0

    def validate_current(self) -> tuple[bool, str]:
        """Validate whether this fact is still current."""
        current_year = datetime.now(timezone.utc).year

        if self.expiry_rule == "retirement_age_60" and self.birth_year > 0:
            retirement_year = self.birth_year + 60
            if current_year >= retirement_year:
                return False, (
                    f"TEMPORAL VIOLATION: {self.subject} retired in {retirement_year} "
                    f"(born {self.birth_year}, retirement age 60). "
                    f"Current year {current_year}. Status is RETIRED, not {self.value_at_filing}."
                )
        if self.expiry_rule == "statute_repealed":
            return False, (
                f"TEMPORAL VIOLATION: {self.attribute} has been repealed. "
                f"Value '{self.value_at_filing}' from {self.filing_year} is no longer valid."
            )
        return True, "TEMPORAL CHECK PASSED"


# =====================================================================
# COMPLEXITY CALCULATOR FOR DYNAMIC DEPTH SCALING
# =====================================================================

def calculate_simulation_depth(
    facts_text: str,
    num_parties: int,
    num_statutes: int,
    base_iterations: int = 200,
) -> int:
    """
    Calculate MCTS iteration count from case complexity.
    RULE-12 compliant: no hardcoded values.

    Returns iteration count scaled by complexity.
    Minimum: base_iterations (200)
    Maximum: 50000 (practical compute ceiling)
    """
    facts_tokens = len(facts_text.split())
    complexity_factor = (facts_tokens / 100.0) + num_parties + num_statutes
    iterations = int(base_iterations * max(1.0, complexity_factor))
    return min(iterations, 50000)


# =====================================================================
# RULE VIOLATION EXCEPTION
# =====================================================================

class HarnessViolation(Exception):
    """Raised when a non-negotiable harness rule is violated."""
    def __init__(self, rule_id: str, detail: str):
        self.rule_id = rule_id
        self.detail = detail
        super().__init__(f"[HARNESS VIOLATION] {rule_id}: {detail}")


def require_canonical_agent(agent_name: str) -> None:
    """Raise if an agent name is not one of the eight canonical strategist agents."""
    if agent_name not in CANONICAL_STRATEGIST_AGENTS:
        raise HarnessViolation(
            "RULE-14",
            f"Non-canonical agent name '{agent_name}'. "
            f"Valid names: {', '.join(CANONICAL_STRATEGIST_AGENTS)}",
        )


class ComputeWastePreventionError(Exception):
    """Raised when stale parameters would waste compute cycles."""
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(f"[COMPUTE WASTE PREVENTION] {detail}")

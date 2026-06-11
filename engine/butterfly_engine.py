# =====================================================================
# CLAUSELY: BUTTERFLY-EFFECT MUTATION ENGINE
# =====================================================================
# Generates systematic factual variations of a case context to explore
# divergent litigation timelines. Each mutation changes exactly ONE
# parameter, enabling the MCTS tree to branch into "what if" scenarios.
#
# RULE-11: Every expansion MUST produce 3+ branches.
# RULE-21: Every mutation MUST be logged with original, mutated, delta.
# RULE-22: All runs accept an optional seed for reproducibility.
# RULE-23: Cross-timeline consistency checks flag >20% divergence.
# =====================================================================

from __future__ import annotations

import copy
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("clausely.butterfly")


# =====================================================================
# MUTATION TYPES
# =====================================================================

MUTATION_TYPES = (
    "date_shift",
    "jurisdiction_swap",
    "party_standing_change",
    "statute_swap",
    "precedent_overrule",
    "evidence_exclusion",
    "forum_transfer",
    "limitation_expiry",
)


@dataclass
class MutationRecord:
    """Immutable audit record for a single factual mutation."""
    mutation_id: str
    mutation_type: str
    original_value: str
    mutated_value: str
    field_path: str
    rationale: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mutation_id": self.mutation_id,
            "mutation_type": self.mutation_type,
            "original_value": self.original_value,
            "mutated_value": self.mutated_value,
            "field_path": self.field_path,
            "rationale": self.rationale,
            "timestamp": self.timestamp,
        }


@dataclass
class MutatedCaseContext:
    """A case context with exactly one factual mutation applied."""
    original_context: Dict[str, Any]
    mutated_context: Dict[str, Any]
    mutation: MutationRecord
    branch_label: str


# =====================================================================
# MUTATION FUNCTIONS
# =====================================================================

def _generate_mutation_id(mutation_type: str, field_path: str, value: str) -> str:
    """Deterministic mutation ID from type + field + value."""
    raw = f"{mutation_type}:{field_path}:{value}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12].upper()


def mutate_date(
    case_context: Dict[str, Any],
    field_name: str = "filing_date",
    delta_days: int = 365,
) -> MutatedCaseContext:
    """
    Shift a date field to test limitation period edge cases.

    Butterfly effect: A filing date shifted by 1 year could make the case
    time-barred under Limitation Act 1963, collapsing the entire strategy.
    """
    mutated = copy.deepcopy(case_context)
    original_val = str(case_context.get(field_name, "not_specified"))

    if field_name in mutated and mutated[field_name]:
        try:
            from dateutil.parser import parse as date_parse
            original_date = date_parse(str(mutated[field_name]))
            from datetime import timedelta
            mutated_date = original_date + timedelta(days=delta_days)
            mutated[field_name] = mutated_date.isoformat()
            mutated_val = mutated[field_name]
        except (ImportError, ValueError):
            mutated_val = f"shifted_by_{delta_days}_days"
            mutated[field_name] = mutated_val
    else:
        mutated_val = f"injected_delay_{delta_days}_days"
        mutated[field_name] = mutated_val

    mutation = MutationRecord(
        mutation_id=_generate_mutation_id("date_shift", field_name, str(delta_days)),
        mutation_type="date_shift",
        original_value=original_val,
        mutated_value=mutated_val,
        field_path=field_name,
        rationale=(
            f"Shifting {field_name} by {delta_days} days to test limitation period "
            f"sensitivity under Limitation Act 1963."
        ),
    )

    return MutatedCaseContext(
        original_context=case_context,
        mutated_context=mutated,
        mutation=mutation,
        branch_label=f"Butterfly: Date shift ({field_name} +{delta_days}d)",
    )


def mutate_jurisdiction(
    case_context: Dict[str, Any],
    alt_jurisdiction: str,
) -> MutatedCaseContext:
    """
    Swap the jurisdiction to test forum sensitivity.

    Butterfly effect: Filing in Bombay HC Principal Seat vs Nagpur Bench
    can change applicable local rules, bench composition, and even the
    likelihood of transfer under forum non conveniens.
    """
    mutated = copy.deepcopy(case_context)
    original_val = str(case_context.get("jurisdiction", "not_specified"))
    mutated["jurisdiction"] = alt_jurisdiction

    mutation = MutationRecord(
        mutation_id=_generate_mutation_id("jurisdiction_swap", "jurisdiction", alt_jurisdiction),
        mutation_type="jurisdiction_swap",
        original_value=original_val,
        mutated_value=alt_jurisdiction,
        field_path="jurisdiction",
        rationale=(
            f"Swapping jurisdiction from {original_val} to {alt_jurisdiction} to test "
            f"forum sensitivity and local procedural rule variations."
        ),
    )

    return MutatedCaseContext(
        original_context=case_context,
        mutated_context=mutated,
        mutation=mutation,
        branch_label=f"Butterfly: Jurisdiction swap to {alt_jurisdiction}",
    )


def mutate_party_standing(
    case_context: Dict[str, Any],
    new_role: str,
    party_field: str = "client_role",
) -> MutatedCaseContext:
    """
    Change the standing of a party to test locus standi sensitivity.

    Butterfly effect: A petitioner-in-person vs an advocate changes
    the court's procedural expectations and the level of legal scrutiny.
    """
    mutated = copy.deepcopy(case_context)
    original_val = str(case_context.get(party_field, "not_specified"))
    mutated[party_field] = new_role

    mutation = MutationRecord(
        mutation_id=_generate_mutation_id("party_standing_change", party_field, new_role),
        mutation_type="party_standing_change",
        original_value=original_val,
        mutated_value=new_role,
        field_path=party_field,
        rationale=(
            f"Changing {party_field} from {original_val} to {new_role} to test "
            f"locus standi sensitivity and procedural expectation shifts."
        ),
    )

    return MutatedCaseContext(
        original_context=case_context,
        mutated_context=mutated,
        mutation=mutation,
        branch_label=f"Butterfly: Standing change to {new_role}",
    )


def mutate_statute(
    case_context: Dict[str, Any],
    old_section: str,
    new_section: str,
    statute_field: str = "primary_statute",
) -> MutatedCaseContext:
    """
    Swap a statute citation to test IPC/BNS transition sensitivity.

    Butterfly effect: Citing IPC Section 302 vs BNS Section 103 for
    a post-July-2024 matter is a FATAL defect under RULE-04.
    """
    mutated = copy.deepcopy(case_context)
    original_val = str(case_context.get(statute_field, old_section))
    mutated[statute_field] = new_section

    # Also mutate within facts text if the old section appears there
    facts = mutated.get("facts", "") or mutated.get("cause_of_action", "")
    if old_section in facts:
        mutated_facts = facts.replace(old_section, new_section, 1)
        if "facts" in mutated:
            mutated["facts"] = mutated_facts
        if "cause_of_action" in mutated:
            mutated["cause_of_action"] = mutated_facts

    mutation = MutationRecord(
        mutation_id=_generate_mutation_id("statute_swap", statute_field, new_section),
        mutation_type="statute_swap",
        original_value=original_val,
        mutated_value=new_section,
        field_path=statute_field,
        rationale=(
            f"Swapping statute from {old_section} to {new_section} to test "
            f"IPC/BNS transition compliance under RULE-04."
        ),
    )

    return MutatedCaseContext(
        original_context=case_context,
        mutated_context=mutated,
        mutation=mutation,
        branch_label=f"Butterfly: Statute swap {old_section} -> {new_section}",
    )


def mutate_precedent(
    case_context: Dict[str, Any],
    overruled_case: str,
    overruling_case: str = "",
) -> MutatedCaseContext:
    """
    Mark a key precedent as overruled to test citation resilience.

    Butterfly effect: If the primary binding precedent was overruled,
    the entire argument vector collapses and must be reconstructed.
    """
    mutated = copy.deepcopy(case_context)
    precedents = mutated.get("precedents", [])
    original_val = json.dumps(precedents)

    # Remove the overruled precedent and add the overruling one
    mutated_precedents = [p for p in precedents if overruled_case not in str(p)]
    if overruling_case:
        mutated_precedents.append(overruling_case)
    mutated["precedents"] = mutated_precedents

    # Add an overruled flag for downstream agents to detect
    mutated["overruled_precedents"] = mutated.get("overruled_precedents", [])
    mutated["overruled_precedents"].append(overruled_case)

    mutation = MutationRecord(
        mutation_id=_generate_mutation_id("precedent_overrule", "precedents", overruled_case),
        mutation_type="precedent_overrule",
        original_value=overruled_case,
        mutated_value=overruling_case or "NO_REPLACEMENT",
        field_path="precedents",
        rationale=(
            f"Marking '{overruled_case}' as overruled to test citation resilience. "
            f"Replacement: '{overruling_case or 'none'}'. This forces the petitioner "
            f"agent to reconstruct the argument vector from scratch."
        ),
    )

    return MutatedCaseContext(
        original_context=case_context,
        mutated_context=mutated,
        mutation=mutation,
        branch_label=f"Butterfly: Precedent overruled ({overruled_case[:40]}...)",
    )


def mutate_evidence_exclusion(
    case_context: Dict[str, Any],
    excluded_evidence: str,
) -> MutatedCaseContext:
    """
    Remove a piece of evidence to test argument robustness.

    Butterfly effect: If the BSA Section 61 certificate is missing,
    all electronic evidence becomes inadmissible.
    """
    mutated = copy.deepcopy(case_context)
    evidence = mutated.get("evidence", [])
    original_val = json.dumps(evidence)

    mutated_evidence = [e for e in evidence if excluded_evidence not in str(e)]
    mutated["evidence"] = mutated_evidence
    mutated["excluded_evidence"] = mutated.get("excluded_evidence", [])
    mutated["excluded_evidence"].append(excluded_evidence)

    mutation = MutationRecord(
        mutation_id=_generate_mutation_id("evidence_exclusion", "evidence", excluded_evidence),
        mutation_type="evidence_exclusion",
        original_value=excluded_evidence,
        mutated_value="EXCLUDED",
        field_path="evidence",
        rationale=(
            f"Excluding '{excluded_evidence}' to test argument robustness. "
            f"Under BSA 2023, missing certificates render electronic evidence inadmissible."
        ),
    )

    return MutatedCaseContext(
        original_context=case_context,
        mutated_context=mutated,
        mutation=mutation,
        branch_label=f"Butterfly: Evidence excluded ({excluded_evidence[:40]}...)",
    )


# =====================================================================
# BATCH MUTATION GENERATOR
# =====================================================================

# Standard Indian jurisdiction alternatives for mutation
_JURISDICTION_ALTERNATIVES = {
    "MH-HC-NAGPUR": ["MH-HC-BOMBAY", "MH-HC-AURANGABAD", "MH-DISTRICT", "IN-SC"],
    "MH-HC-BOMBAY": ["MH-HC-NAGPUR", "MH-HC-AURANGABAD", "MH-DISTRICT", "IN-SC"],
    "MH-HC": ["DL-HC", "KA-HC", "IN-SC"],
    "MH-DISTRICT": ["MH-HC-NAGPUR", "MH-HC-BOMBAY", "DL-DISTRICT"],
    "DL-DISTRICT": ["DL-HC", "MH-DISTRICT"],
    "DL-HC": ["MH-HC", "IN-SC"],
    "IN-SC": ["MH-HC", "DL-HC"],
}

# Standard IPC -> BNS section mappings for statute mutation
_STATUTE_SWAPS: List[Tuple[str, str]] = [
    ("Section 302 IPC", "Section 103 BNS"),
    ("Section 304 IPC", "Section 105 BNS"),
    ("Section 420 IPC", "Section 318 BNS"),
    ("Section 498A IPC", "Section 85 BNS"),
    ("Section 138 NI Act", "Section 138 NI Act"),  # No change, but tests handling
    ("Section 125 CrPC", "Section 144 BNSS"),
    ("Section 482 CrPC", "Section 528 BNSS"),
    ("Article 226", "Article 226"),  # Constitutional, no change
    ("Article 32", "Article 32"),    # Constitutional, no change
]


def generate_butterfly_mutations(
    case_context: Dict[str, Any],
    max_mutations: int = 5,
) -> List[MutatedCaseContext]:
    """
    Generate a batch of butterfly-effect mutations for a case context.

    Returns at least 3 mutations (RULE-11 minimum branching) covering
    different mutation types to ensure divergent timeline exploration.

    Args:
        case_context: The base case context to mutate.
        max_mutations: Maximum number of mutations to generate.

    Returns:
        List of MutatedCaseContext objects, each with exactly one change.
    """
    mutations: List[MutatedCaseContext] = []
    jurisdiction = case_context.get("jurisdiction", "MH-HC")

    # 1. Date shift mutation (limitation period stress)
    mutations.append(mutate_date(case_context, "filing_date", delta_days=365))

    # 2. Jurisdiction swap mutation
    alt_jurisdictions = _JURISDICTION_ALTERNATIVES.get(jurisdiction, ["IN-SC"])
    if alt_jurisdictions:
        mutations.append(mutate_jurisdiction(case_context, alt_jurisdictions[0]))

    # 3. Party standing mutation
    current_role = case_context.get("client_role", "Petitioner")
    alt_role = "Petitioner-in-Person" if current_role != "Petitioner-in-Person" else "Advocate"
    mutations.append(mutate_party_standing(case_context, alt_role))

    # 4. Statute swap mutation (if applicable)
    if len(mutations) < max_mutations:
        facts = case_context.get("facts", "") or case_context.get("cause_of_action", "")
        for old_sec, new_sec in _STATUTE_SWAPS:
            if old_sec in facts and old_sec != new_sec:
                mutations.append(mutate_statute(case_context, old_sec, new_sec))
                break

    # 5. Precedent overrule mutation (if precedents exist)
    if len(mutations) < max_mutations:
        precedents = case_context.get("precedents", [])
        if precedents:
            mutations.append(mutate_precedent(case_context, str(precedents[0])))

    return mutations[:max_mutations]


# =====================================================================
# CROSS-TIMELINE CONSISTENCY CHECKER (RULE-23)
# =====================================================================

def check_cross_timeline_consistency(
    results: List[Dict[str, Any]],
    divergence_threshold: float = 0.20,
) -> List[Dict[str, Any]]:
    """
    Check if timelines with identical parameters produce consistent outcomes.

    RULE-23: If two timelines with identical parameters produce >20%
    divergent outcomes, flag as non-deterministic failure.

    Args:
        results: List of simulation result dicts with 'success_probability' keys.
        divergence_threshold: Maximum allowed probability divergence (default 20%).

    Returns:
        List of flagged divergence violations.
    """
    violations = []

    for i, r1 in enumerate(results):
        for j, r2 in enumerate(results):
            if i >= j:
                continue

            p1 = r1.get("success_probability", 0.0)
            p2 = r2.get("success_probability", 0.0)
            divergence = abs(p1 - p2) / 100.0  # Normalize from percentage

            if divergence > divergence_threshold:
                violations.append({
                    "timeline_a": r1.get("run_metadata", {}).get("case_title", f"run_{i}"),
                    "timeline_b": r2.get("run_metadata", {}).get("case_title", f"run_{j}"),
                    "probability_a": p1,
                    "probability_b": p2,
                    "divergence": round(divergence * 100, 2),
                    "threshold": divergence_threshold * 100,
                    "status": "RULE-23 VIOLATION: Non-deterministic divergence detected",
                })

    return violations

# =====================================================================
# CLAUSELY: LONG-HORIZON MCTS LITIGATION SIMULATOR
# =====================================================================
# AlphaGo/AlphaZero-inspired Monte Carlo Tree Search for legal
# strategy simulation. Every node expansion triggers a real grounding
# verification call. Butterfly-effect branching ensures that even
# the smallest factual variation cascades into divergent timelines.
#
# RULE-10: No deterministic outcome hardcoding.
# RULE-11: Minimum 3 branching factors per node.
# RULE-12: Dynamic depth scaling from case complexity.
# RULE-13: No artificial entropy injection.
# =====================================================================

from __future__ import annotations

import math
import time
import json
import os
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from agents.harness_rules import (
    GroundingResult,
    HarnessViolation,
    ComputeWastePreventionError,
    calculate_simulation_depth,
    build_harness_preamble,
    NON_NEGOTIABLES,
    require_canonical_agent,
)
from agents.grounding_engine import verify_grounding
from engine.butterfly_engine import generate_butterfly_mutations, check_cross_timeline_consistency

logger = logging.getLogger("clausely.mcts")



# =====================================================================
# MCTS NODE
# =====================================================================

@dataclass
class MCTSNode:
    """
    A node in the litigation timeline tree.

    Each node represents a legal decision point (filing strategy,
    jurisdictional choice, precedent invocation, procedural step).
    """
    node_id: str
    name: str
    description: str
    node_type: str  # 'argument', 'procedure', 'adversarial', 'grounding_gate'
    p_assumption: float = 0.0  # 0.0 = fully grounded, 1.0 = fully assumed
    parent: Optional[MCTSNode] = field(default=None, repr=False)
    children: List[MCTSNode] = field(default_factory=list)
    grounding_results: List[GroundingResult] = field(default_factory=list)
    w: float = 0.0  # Accumulated win score
    n: int = 0       # Visit count
    depth: int = 0
    pruned: bool = False
    prune_reason: str = ""
    case_context: Dict[str, Any] = field(default_factory=dict)
    mutation_record: Optional[Any] = None


    def is_leaf(self) -> bool:
        return len(self.children) == 0 or all(c.pruned for c in self.children)

    def uct(self, c: float = 1.414, lambda_val: float = 1000.0) -> float:
        """
        Modified UCT with prior assumption penalty.
        UCT(node) = W_i/N_i + c * sqrt(ln(N_p)/N_i) - lambda * P_assumption
        """
        if self.n == 0:
            return float("inf")
        if self.pruned:
            return float("-inf")

        from engine.internal_consistency import ConsistencyEngine
        from engine.evidence_matrix import EvidenceMatrix

        # Calculate base UCT without penalty
        exploitation = self.w / self.n
        exploration = 0.0
        if self.parent and self.parent.n > 0:
            exploration = c * math.sqrt(math.log(self.parent.n) / self.n)
        base_uct = exploitation + exploration

        # Run penalty audit using the ConsistencyEngine
        engine = ConsistencyEngine(f_matrix=EvidenceMatrix(atoms=[]))
        audit_res = engine.audit_quant_engine_penalties(
            uct_score=base_uct,
            visits=self.n,
            parent_visits=self.parent.n if self.parent else 0,
            p_assumption=self.p_assumption,
            exploration_weight=c,
        )

        if audit_res.pruned:
            self.prune(audit_res.reason)
            return float("-inf")

        return audit_res.adjusted_uct

    def select_child(self, c: float = 1.414, lambda_val: float = 1000.0) -> Optional[MCTSNode]:
        """Select the child with highest UCT score."""
        active_children = [ch for ch in self.children if not ch.pruned]
        if not active_children:
            return None
        best = max(active_children, key=lambda ch: ch.uct(c, lambda_val))
        return best

    def backpropagate(self, reward: float) -> None:
        """Propagate reward up the tree."""
        self.n += 1
        self.w += reward
        if self.parent:
            self.parent.backpropagate(reward)

    def prune(self, reason: str) -> None:
        """Mark this node as pruned (dead branch)."""
        self.pruned = True
        self.prune_reason = reason
        self.p_assumption = 1.0

    def add_grounding(self, result: GroundingResult) -> None:
        """Attach a grounding result and update P_assumption."""
        self.grounding_results.append(result)
        if result.contradiction_detected:
            self.prune(
                f"Grounding contradiction: {result.contradiction_detail}"
            )
        elif not result.verified:
            # Increase assumption score based on grounding failure
            self.p_assumption = max(self.p_assumption, result.p_assumption)


# =====================================================================
# BUTTERFLY EFFECT BRANCHING SPECS
# =====================================================================

# RULE-11: Every node expansion MUST produce at minimum 3 branches.
# These represent the primary argument, procedural obstacle, and
# adversarial counter-argument paths.

def generate_branching_specs(
    parent_node: MCTSNode,
    case_context: Dict[str, Any],
    depth: int,
) -> List[Dict[str, Any]]:
    """
    Generate butterfly-effect branching specifications for a node.

    Each expansion produces 3+ children representing divergent
    litigation timelines caused by even the smallest factual variation.
    """
    parent_type = parent_node.node_type
    node_prefix = f"D{depth}"

    # Base branching: argument, procedure, adversarial (RULE-11 minimum)
    specs = []

    if depth == 0:
        # Root-level: major strategic forks
        specs = [
            {
                "name": "Direct Filing Strategy",
                "description": "File immediately in the declared jurisdiction with full documentation.",
                "node_type": "argument",
                "claims_to_verify": [
                    ("jurisdiction", f"Territorial jurisdiction of {case_context.get('jurisdiction', 'court')} for {case_context.get('subject', 'this matter')}"),
                ],
            },
            {
                "name": "Alternative Remedy Exhaustion",
                "description": "Exhaust all administrative remedies before approaching the court (RULE-06 compliance).",
                "node_type": "procedure",
                "claims_to_verify": [
                    ("procedure", f"Alternative remedies available before filing writ under Article 226 for {case_context.get('subject', 'this matter')}"),
                ],
            },
            {
                "name": "Opposing Counsel Pre-emptive Strategy",
                "description": "Anticipate opposing counsel filing preliminary objections on maintainability.",
                "node_type": "adversarial",
                "claims_to_verify": [
                    ("procedure", f"Grounds for preliminary objection on maintainability in {case_context.get('jurisdiction', 'Indian courts')}"),
                ],
            },
        ]
    elif parent_type == "argument":
        specs = [
            {
                "name": f"{node_prefix}: Substantive Merits Path",
                "description": "Argue on the merits using binding precedents and statutory provisions.",
                "node_type": "argument",
                "claims_to_verify": _extract_precedent_claims(case_context),
            },
            {
                "name": f"{node_prefix}: Evidence Admissibility Challenge",
                "description": "Butterfly: opposing counsel challenges admissibility of key evidence (BSA Section 61 certificate requirement).",
                "node_type": "adversarial",
                "claims_to_verify": [
                    ("statute", "Section 61 Bharatiya Sakshya Adhiniyam 2023 electronic evidence certificate requirements"),
                ],
            },
            {
                "name": f"{node_prefix}: Limitation Period Defect",
                "description": "Butterfly: registry raises limitation objection on one of the relief prayers.",
                "node_type": "procedure",
                "claims_to_verify": [
                    ("procedure", f"Limitation period for {case_context.get('document_type', 'writ petition')} under Limitation Act 1963"),
                ],
            },
        ]
    elif parent_type == "procedure":
        specs = [
            {
                "name": f"{node_prefix}: Procedural Compliance Verified",
                "description": "All procedural requirements met, proceed to merits hearing.",
                "node_type": "argument",
                "claims_to_verify": [
                    ("procedure", f"Filing requirements for {case_context.get('jurisdiction', 'High Court')} registry"),
                ],
            },
            {
                "name": f"{node_prefix}: Condonation of Delay Required",
                "description": "Butterfly: filing is technically time-barred, requiring condonation application.",
                "node_type": "procedure",
                "claims_to_verify": [
                    ("statute", "Section 5 Limitation Act 1963 condonation of delay sufficient cause requirement"),
                ],
            },
            {
                "name": f"{node_prefix}: Forum Non Conveniens",
                "description": "Butterfly: court transfers matter to a different bench/forum.",
                "node_type": "adversarial",
                "claims_to_verify": [
                    ("procedure", f"Forum non conveniens and transfer of cases between benches in {case_context.get('jurisdiction', 'Bombay High Court')}"),
                ],
            },
        ]
    elif parent_type == "adversarial":
        specs = [
            {
                "name": f"{node_prefix}: Counter-Argument Sustained",
                "description": "Court sustains the adversarial objection, requiring amended pleading.",
                "node_type": "procedure",
                "claims_to_verify": [
                    ("procedure", "Amendment of pleadings under Order VI Rule 17 CPC / corresponding BNSS provision"),
                ],
            },
            {
                "name": f"{node_prefix}: Counter-Argument Overruled",
                "description": "Court overrules the objection, proceeding to substantive hearing.",
                "node_type": "argument",
                "claims_to_verify": _extract_precedent_claims(case_context),
            },
            {
                "name": f"{node_prefix}: Settlement Negotiation Fork",
                "description": "Butterfly: opposing party proposes out-of-court settlement mid-hearing.",
                "node_type": "argument",
                "claims_to_verify": [
                    ("procedure", "Section 89 CPC alternative dispute resolution mechanisms in Indian courts"),
                ],
            },
        ]
    else:
        # Fallback generic branching
        specs = [
            {
                "name": f"{node_prefix}: Primary Continuation",
                "description": "Continue along the primary litigation path.",
                "node_type": "argument",
                "claims_to_verify": _extract_precedent_claims(case_context),
            },
            {
                "name": f"{node_prefix}: Procedural Complication",
                "description": "Unexpected procedural hurdle arises.",
                "node_type": "procedure",
                "claims_to_verify": [
                    ("procedure", f"Common procedural complications in {case_context.get('jurisdiction', 'Indian courts')}"),
                ],
            },
            {
                "name": f"{node_prefix}: Adversarial Escalation",
                "description": "Opposing side escalates with new legal arguments.",
                "node_type": "adversarial",
                "claims_to_verify": [
                    ("fact", f"Common adversarial strategies in {case_context.get('subject', 'this type of matter')} cases"),
                ],
            },
        ]

    return specs


def _extract_precedent_claims(case_context: Dict[str, Any]) -> List[tuple]:
    """Extract verifiable precedent claims from case context."""
    claims = []
    precedents = case_context.get("precedents", [])
    for p in precedents[:2]:  # Limit to 2 precedent checks per node to manage API budget
        claims.append(("precedent", p))
    if not claims:
        subject = case_context.get("subject", "constitutional law")
        claims.append(("precedent", f"Leading Supreme Court precedent on {subject} in India"))
    return claims


# =====================================================================
# LONG-HORIZON MCTS ENGINE
# =====================================================================

class LongHorizonSimulator:
    """
    AlphaGo/AlphaZero-inspired litigation simulator.

    Key properties:
    - Dynamic depth scaling (RULE-12)
    - Per-step grounding verification (RULE-07, RULE-08)
    - Butterfly-effect branching (RULE-11)
    - No deterministic hardcoding (RULE-10)
    - Real entropy calculation (RULE-13)
    """

    def __init__(
        self,
        c_exploration: float = 1.414,
        lambda_penalty: float = 1000.0,
        max_tree_depth: int = 6,
        grounding_budget: int = 100,  # Max grounding API calls per simulation
        grounding_fn: Optional[Any] = None,
    ):
        self.c = c_exploration
        self.lambda_val = lambda_penalty
        self.max_depth = max_tree_depth
        self.grounding_budget = grounding_budget
        self.grounding_fn = grounding_fn
        self._grounding_calls_made = 0
        self._total_nodes_created = 0
        self._pruned_nodes = 0
        self._grounding_log: List[Dict[str, Any]] = []

    def simulate(
        self,
        case_context: Dict[str, Any],
        run_id: str = "",
        seed: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute a full long-horizon MCTS simulation on a case.

        Args:
            case_context: Dict with keys:
                - title: Case name
                - jurisdiction: Court jurisdiction code
                - subject: Legal subject matter
                - facts: Detailed facts text
                - document_type: Type of legal document
                - precedents: List of precedent citations to verify
                - num_parties: Number of parties involved
                - num_statutes: Number of statutes cited
            run_id: Unique identifier for this simulation run.
            seed: Optional seed for reproducibility.

        Returns:
            Comprehensive simulation result dict.
        """
        if seed is not None:
            import random
            random.seed(seed)

        start_time = time.time()
        self._grounding_calls_made = 0
        self._total_nodes_created = 0
        self._pruned_nodes = 0
        self._grounding_log = []

        # RULE-12: Calculate simulation depth from complexity
        facts = case_context.get("facts", "")
        num_parties = case_context.get("num_parties", 2)
        num_statutes = case_context.get("num_statutes", 1)
        total_iterations = calculate_simulation_depth(
            facts, num_parties, num_statutes
        )

        logger.info(
            f"[MCTS] Starting simulation for '{case_context.get('title', 'Unknown')}' "
            f"with {total_iterations} iterations (dynamic scaling)."
        )

        # Build root node
        root = MCTSNode(
            node_id="root",
            name="Litigation Root",
            description=f"Case intake: {case_context.get('title', 'Unknown')}",
            node_type="argument",
            depth=0,
            case_context=case_context,
        )
        self._total_nodes_created = 1


        # MCTS main loop
        for iteration in range(total_iterations):
            # --- SELECTION ---
            node = root
            while not node.is_leaf() and node.depth < self.max_depth:
                child = node.select_child(self.c, self.lambda_val)
                if child is None:
                    break
                node = child

            # --- EXPANSION ---
            if node.depth < self.max_depth and not node.pruned:
                self._expand_node(node, case_context)

            # --- SIMULATION (ROLLOUT) ---
            reward = self._rollout(node, case_context)

            # --- BACKPROPAGATION ---
            node.backpropagate(reward)

            # Progress logging
            if (iteration + 1) % max(1, total_iterations // 10) == 0:
                elapsed = time.time() - start_time
                logger.info(
                    f"[MCTS] Iteration {iteration+1}/{total_iterations} "
                    f"({elapsed:.1f}s elapsed, "
                    f"{self._grounding_calls_made} grounding calls, "
                    f"{self._pruned_nodes} pruned nodes)"
                )

        # --- ANALYSIS ---
        elapsed_total = time.time() - start_time
        optimal_path = self._extract_optimal_path(root)
        all_leaf_paths = self._extract_all_leaf_paths(root)
        entropy = self._calculate_entropy(root)
        success_probability = self._calculate_success_probability(root)
        timeline_report = self._build_timeline_report(
            root, case_context, optimal_path, all_leaf_paths,
            entropy, success_probability, total_iterations, elapsed_total,
        )

        return timeline_report

    def _expand_node(
        self, node: MCTSNode, case_context: Dict[str, Any]
    ) -> None:
        """Expand a leaf node with butterfly-effect branching."""
        mutations = generate_butterfly_mutations(node.case_context, max_mutations=3)
        if len(mutations) < 3:
            raise HarnessViolation(
                "RULE-11",
                f"Node {node.node_id} expanded into {len(mutations)} branches; minimum is 3.",
            )

        for i, mut in enumerate(mutations):
            child_id = f"{node.node_id}-{node.depth+1}-{i}"
            # Map mutation type to node type
            node_type = "argument"
            if mut.mutation.mutation_type in ("limitation_expiry", "forum_transfer", "evidence_exclusion"):
                node_type = "procedure"
            elif mut.mutation.mutation_type in ("precedent_overrule", "jurisdiction_swap"):
                node_type = "adversarial"

            child = MCTSNode(
                node_id=child_id,
                name=mut.branch_label,
                description=mut.mutation.rationale,
                node_type=node_type,
                parent=node,
                depth=node.depth + 1,
                case_context=mut.mutated_context,
                mutation_record=mut.mutation,
            )
            self._total_nodes_created += 1

            # RULE-07: Per-step grounding verification
            # Map the mutation details to a verifiable claim
            claim_type = "fact"
            if mut.mutation.mutation_type == "date_shift":
                claim_type = "procedure"
            elif mut.mutation.mutation_type == "jurisdiction_swap":
                claim_type = "procedure"
            elif mut.mutation.mutation_type == "statute_swap":
                claim_type = "statute"
            elif mut.mutation.mutation_type == "precedent_overrule":
                claim_type = "precedent"

            claim_text = f"Verify {mut.mutation.field_path} mutation: {mut.mutation.original_value} -> {mut.mutation.mutated_value}"

            agent_name = self._agent_for_node_type(node_type)
            require_canonical_agent(agent_name)
            ground_func = self.grounding_fn or verify_grounding
            if self._grounding_calls_made < self.grounding_budget:
                result = ground_func(
                    agent_name=agent_name,
                    node_id=child_id,
                    claim=claim_text,
                    claim_type=claim_type,
                )
                self._grounding_calls_made += 1
                self._grounding_log.append(result.to_dict())
                child.add_grounding(result)

                if child.pruned:
                    self._pruned_nodes += 1
                    break
            else:
                # RULE-09 and RULE-19: budget exhaustion is unverified, not partial proof.
                result = GroundingResult(
                    query=claim_text,
                    agent_name=agent_name,
                    node_id=child_id,
                    verified=False,
                    p_assumption=1.0,
                    error="Grounding budget exhausted before claim verification.",
                )
                self._grounding_log.append(result.to_dict())
                child.add_grounding(result)

            node.children.append(child)

    def _rollout(self, node: MCTSNode, case_context: Dict[str, Any]) -> float:
        """
        Simulate a rollout from this node.
        Reward is based on grounding quality, not random chance.
        RULE-10: No hardcoded outcomes.
        """
        if node.pruned:
            return 0.0

        # Reward is inversely proportional to assumption level
        base_reward = 1.0 - node.p_assumption

        # Depth bonus: deeper verified paths get slight reward bonus
        depth_bonus = min(0.2, node.depth * 0.03)

        # Grounding quality bonus
        grounding_bonus = 0.0
        for gr in node.grounding_results:
            if gr.verified and gr.sources:
                grounding_bonus += 0.1  # Each verified source adds reward

        total_reward = min(1.0, base_reward + depth_bonus + grounding_bonus)
        return total_reward

    def _agent_for_node_type(self, node_type: str) -> str:
        """Map node types to canonical agent names."""
        mapping = {
            "argument": "petitioner_agent",
            "procedure": "objector_agent",
            "adversarial": "opponent_agent",
            "grounding_gate": "verifier_agent",
        }
        return mapping.get(node_type, "reviewer_agent")

    def _extract_optimal_path(self, root: MCTSNode) -> List[Dict[str, Any]]:
        """Walk down the tree following the best UCT child at each level."""
        path = []
        node = root
        while node:
            path.append({
                "node_id": node.node_id,
                "name": node.name,
                "depth": node.depth,
                "visits": node.n,
                "win_rate": (node.w / node.n) if node.n > 0 else 0.0,
                "p_assumption": node.p_assumption,
                "pruned": node.pruned,
                "grounding_count": len(node.grounding_results),
                "verified_count": sum(1 for g in node.grounding_results if g.verified),
            })
            child = node.select_child(self.c, self.lambda_val)
            if child is None:
                break
            node = child
        return path

    def _extract_all_leaf_paths(self, root: MCTSNode) -> List[List[str]]:
        """Extract all paths from root to leaf nodes."""
        paths = []

        def _dfs(node: MCTSNode, current_path: List[str]) -> None:
            current_path.append(node.name)
            if node.is_leaf() or node.depth >= self.max_depth:
                paths.append(list(current_path))
            else:
                for child in node.children:
                    _dfs(child, current_path)
            current_path.pop()

        _dfs(root, [])
        return paths

    def _calculate_entropy(self, root: MCTSNode) -> float:
        """
        Calculate Timeline Branching Entropy H = -sum(p_i * ln(p_i)).
        RULE-13: No artificial injection. If H=0, simulation failed.
        """
        # Collect visit counts at the first branching level
        if not root.children:
            return 0.0

        total_visits = sum(c.n for c in root.children if not c.pruned)
        if total_visits == 0:
            return 0.0

        entropy = 0.0
        for child in root.children:
            if child.pruned or child.n == 0:
                continue
            p_i = child.n / total_visits
            if p_i > 0:
                entropy -= p_i * math.log(p_i)

        return entropy

    def _calculate_success_probability(self, root: MCTSNode) -> float:
        """Calculate overall success probability from tree statistics."""
        if root.n == 0:
            return 0.0
        return (root.w / root.n) * 100.0

    def _build_timeline_report(
        self,
        root: MCTSNode,
        case_context: Dict[str, Any],
        optimal_path: List[Dict[str, Any]],
        all_paths: List[List[str]],
        entropy: float,
        success_prob: float,
        iterations: int,
        elapsed: float,
    ) -> Dict[str, Any]:
        """Compile the comprehensive simulation report."""
        # Count grounding statistics
        total_grounding = len(self._grounding_log)
        verified = sum(1 for g in self._grounding_log if g.get("verified"))
        contradictions = sum(
            1 for g in self._grounding_log if g.get("contradiction_detected")
        )
        unverified = total_grounding - verified

        # RULE-13: Flag if entropy is zero (simulation failure)
        entropy_valid = entropy > 0.0

        return {
            "run_metadata": {
                "case_title": case_context.get("title", "Unknown"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "iterations": iterations,
                "elapsed_seconds": round(elapsed, 2),
                "c_exploration": self.c,
                "lambda_penalty": self.lambda_val,
                "max_depth": self.max_depth,
                "grounding_budget": self.grounding_budget,
            },
            "tree_statistics": {
                "total_nodes_created": self._total_nodes_created,
                "pruned_nodes": self._pruned_nodes,
                "active_paths": len(all_paths),
                "max_depth_reached": max(
                    (p["depth"] for p in optimal_path), default=0
                ),
            },
            "grounding_statistics": {
                "total_calls": total_grounding,
                "verified": verified,
                "unverified": unverified,
                "contradictions_detected": contradictions,
                "verification_rate": (
                    f"{(verified / total_grounding * 100):.1f}%"
                    if total_grounding > 0
                    else "N/A"
                ),
            },
            "entropy": {
                "timeline_branching_entropy_H": round(entropy, 6),
                "entropy_valid": entropy_valid,
                "interpretation": (
                    "VALID: Multiple divergent timelines explored."
                    if entropy_valid
                    else "INVALID: H=0 indicates static simulation. Re-run required."
                ),
            },
            "success_probability": round(success_prob, 2),
            "optimal_path": optimal_path,
            "all_leaf_paths_count": len(all_paths),
            "grounding_audit_log": self._grounding_log[:50],  # Cap for readability
        }


# =====================================================================
# CONVENIENCE: RUN A SINGLE CASE
# =====================================================================

def run_single_case_simulation(
    case_context: Dict[str, Any],
    grounding_budget: int = 50,
    run_id: str = "",
) -> Dict[str, Any]:
    """
    Run a single long-horizon simulation on a case.

    Args:
        case_context: Case data dict.
        grounding_budget: Max grounding API calls.
        run_id: Optional run identifier.

    Returns:
        Full simulation result dict.
    """
    simulator = LongHorizonSimulator(grounding_budget=grounding_budget)
    return simulator.simulate(case_context, run_id=run_id)

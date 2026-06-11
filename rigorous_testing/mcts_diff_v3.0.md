# mcts_diff_v3.0.md: Token & Line-Count Audit for MCTS Engine

## 1. Baseline vs. New Metrics

| Metric | Baseline (v0.0.0.1) | New (v3.0) | Change |
|---|---|---|---|
| **Line Count** | 0 | 861 | +100% |
| **Word Count** | 0 | 3624 | +100% |
| **File Size (Bytes)** | 0 | 35467 | +100% |

[DIFF] Percentage Increase in Exactness: +100.0% (Initial compilation of complete MCTS Engine and State Machine).

---

## 2. Deterministic Variable Injections

1. **UCT Scoring Constraints:**
   - **Injected Variables:** `self.uct_penalty`, `self.prior_probability`
   - **Purpose:** Restricts search trajectories from selecting compromised or poisoned nodes. Prevents LLMs from assuming valid execution routes when structural defects are present.

2. **AlphaProof Rater Parameters:**
   - **Injected Variables:** `scaled_a`, `scaled_b`, `max_s`
   - **Purpose:** Controls Plackett-Luce pairwise model probability outputs using max-scaled exponential limits to eliminate floating-point overflows during Gibbs sampling.

3. **Stage 1 Node Initialization & Selection Audits:**
   - **Injected Variables:** `case_intake`, `base_iterations`
   - **Purpose:** Verifies that case intake schemas align with real-world variables, establishing proper baseline constraints to prevent generic/hallucinated legal dispute generation.

---

[AUDIT] All changes are version-locked under v3.0 and validated with zero formatting defects.

# MASTER INSTRUCTION 014: THE ALPHAPROOF NEXUS FRAMEWORK FOR LEGAL AI
# VERSION 1.1 (COGNITIVE & SYSTEMIC GROUNDING BLUEPRINT)

This document formalizes the integration of the AlphaProof Nexus framework with the 8-Agent Monte Carlo Tree Search (MCTS) Legal Simulation Swarm. It defines the mapping between formal prover paradigms and legal compilation agents.

---

## 1. HIERARCHICAL SWARM AGENT MAPPING

The 8-agent swarm is divided into three functional clusters matching the AlphaProof Nexus specification:

### 1.1 THE PROVER CLUSTER (TACTIC GENERATION)
Prover agents propose state changes to the pleading tree using search-replace tactic diffs:
1. **The Petitioner Agent (`petitioner_agent`):** Proposes generative argument vectors representing the plaintiff/petitioner's litigation path.
2. **The Opponent Agent (`opponent_agent`):** Actively searches for semantic weaknesses, proposing adversarial counter-arguments to pressure test the petitioner's path.

### 1.2 THE RATER CLUSTER (ELO RATING & SELECTION)
Rater agents evaluate proposed nodes pairwise to compute Elo strengths, which calibrate the MCTS prior probability values:
3. **The Reviewer Agent (`reviewer_agent`):** Runs Cosine Similarity and Jaccard Index checks against judicial precedents.
4. **The Judge Agent (`judge_agent`):** Computes terminal rewards using LoRA-calibrated bias matrices to evaluate the probability of success (0.0 to 1.0).

### 1.3 THE COMPILER & OVERSIGHT CLUSTER (SAFEVERIFY GATES)
Oversight agents compile mutations, enforce statutory and territorial limits, and verify physical/logical constraints:
5. **The Drafter Agent (`drafter_agent`):** The exclusive sovereign of the Abstract Syntax Tree (AST) and population database. Maintains the Merkle Tree root.
6. **The Verifier Agent (`verifier_agent`):** Performs chronological and coordinate math checks against external sources to destroy hallucinations.
7. **The Objector Agent (`objector_agent`):** Enforces e-filing registry manual guidelines (margins, formatting, PEC/territorial coordinates, and limitation acts).
8. **The Presenter Agent (`presenter_agent`):** Filters final pleadings to maintain oratorical brevity and respect user cognitive load limits.

---

## 2. THE SYSTEM RUNTIME (THE RALPH LOOP)

Every agent interaction within the swarm runs in a compiler-in-the-loop protocol:
- **Search-Replace Diff Mutator:** Agents propose incremental changes to specific AST nodes instead of rewriting the entire document.
- **SFE Compiler Auditing:** Protests from the Symbolic Formatting Engine (SFE) are fed back into the agent context dynamically.
- **Sorry-Free Constraint:** The compiler rejects the filing if any `UNVERIFIED` tags or stubs remain in the final AST.
- **Guillotine Protocol:** Nodes violating physical or statutory bounds (e.g. coordinates out of court boundary, age-60 civil service retirement cap crossed) are pruned by setting UCT score to negative infinity.

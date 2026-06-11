# CLAUSELY: TECHNICAL MOAT ANALYSIS

## Version: v1.0.0
## Date: June 7, 2026

### 1. Mathematical Moat: UCT Penalty for Assumptions
Standard LLM legal tools suffer from stochastic drift: as the reasoning chains grow longer, the probability of hallucinating a fact, citation, or section increases exponentially. Clausely counters this by mathematically punishing assumptions inside the selection phase of Monte Carlo Tree Search (MCTS).

We define the Upper Confidence Bound for Trees (UCT) formula with a dedicated assumption penalty:

$$UCT_i = \frac{W_i}{N_i} + C \cdot \sqrt{\frac{\ln(N_p)}{N_i}} - \lambda \cdot P_{assumption}$$

Where:
- $W_i$: Accumulated win score for node $i$.
- $N_i$: Visit count of node $i$.
- $N_p$: Visit count of the parent node.
- $C$: Exploration constant (set to 1.414).
- $P_{assumption}$: Probability of unverified assumption (0.0 for fully grounded via live search, up to 1.0 if grounding fails or is omitted).
- $\lambda$: Penalty weight (set to 1000.0).

#### Economic Irrationality of Hallucination:
Since $\lambda$ is set to 1000.0, any node with an ungrounded claim ($P_{assumption} \ge 0.05$) suffers an immediate penalty of at least $-50.0$. Because the exploitation-exploration component of UCT is bounded between $0.0$ and $1.0 + C \approx 2.414$, the penalty completely dominates the UCT calculation. The MCTS search engine will immediately stop exploring that branch, starving it of compute resources. Thus, hallucinating legal references becomes economically irrational for the search engine, guaranteeing that the chosen path is grounded.

---

### 2. Algorithmic Dominance: MCTS vs. LawFirmAI.in "Inter-Council" Review
LawFirmAI.in uses a sequential multi-agent review pipeline ("inter-council review"), where Agent A drafts, Agent B critiques, and Agent C approves. 

#### MCTS as a Multiverse Tree:
A sequential review pipeline is a single linear path in the legal decision multiverse. It assumes that the initial strategic direction is correct and only works on refining it. 

In contrast, Clausely's MCTS engine models litigation as a game-tree. Each node represents a branching strategic action (e.g., direct filing, administrative remedies, preliminary objection). The engine expands these paths into a tree of height $D$ and branching factor $B$. 

If LawFirmAI.in explores $1$ timeline of length $L$, Clausely explores $B^D$ possible future timelines. Our engine evaluates procedural obstacles and adversarial counter-arguments in parallel, selecting the path that has the highest probability of success under active grounding. The linear review pipeline of LawFirmAI is a trivial subset of a single branch in Clausely's game-tree.

---

### 3. Grounding Integrity: Merkle-Tree Intake Anchoring
Every fact extracted during intake is hashed and placed into a cryptographic Merkle Tree. When a strategist agent makes a factual assertion in the MCTS tree, the Verifier Agent computes the hash of the assertion and checks it against the Merkle root. If the claim does not resolve to a verified leaf node in the Merkle Tree, the claim is flagged as an assumption and assigned $P_{assumption} = 1.0$. This prevents post-intake injection of false claims.

---

### 4. SFE Determinism Guarantee
The Symbolic Formatting Engine (SFE) enforces a strict, rule-based compilation layer:
1. **Separation of Concerns:** LLMs are used to generate natural language arguments (probabilistic). SFE is used to format, paginate, margin-align, and compile the final PDF (deterministic).
2. **Formatting Rules:** If any margin, font size, or page numbering rule violates the High Court rules (e.g. Bombay High Court margin rules), the SFE raises a compilation error and rejects the document. It does not attempt to let the LLM format the text.

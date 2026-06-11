# THE ALGORITHMIC TRUTH FILTER (THE "ALGO")
## VERSION: v0.0.0.5

This document defines the proprietary logic filtering mechanism, inspired by social media engagement algorithms (Insta/FB/X), but inverted. Instead of optimizing for engagement, click-through rates, and "virality" (which in legal context means plausible but hallucinated rhetoric), this Algo explicitly optimizes for "Absolute Truth & Zero Hallucination".

## 1. THE INVERTED ENGAGEMENT LOOP
Social media algorithms reward high-variance, emotionally charged tokens. The Legal Swarm Algo actively suppresses them.

### STAGE 1: VARIANCE SUPPRESSION (THE "SHADOWBAN" PROTOCOL)
- **Signal:** An agent submits a highly persuasive, perfectly formatted paragraph containing an obscure or emotionally charged legal theory.
- **Trigger:** The Algo measures the semantic distance between the proposed text and the Verifier's factual matrix.
- **Action:** If Semantic Distance $D_s > 0.15$, the Algo "shadowbans" the node. 
- **Effect:** The MCTS engine assigns a simulated "virality score" of zero. The path is starved of computational resources and eventually garbage collected.

## 2. THE PRECEDENT-RANKING ALGORITHM (PAGERANK INVERSION)
Similar to Google's PageRank, the Algo ranks legal citations. However, authority is not based on "inbound links" (popularity), but on hierarchical stability.

### STAGE 2: HIERARCHICAL STABILITY RANKING
- **Signal:** The Reviewer Agent processes a cited SCC/AIR case.
- **Algo Execution:**
  - `Base_Score = 100` (for Supreme Court)
  - `Modifier_1 = +50` (if Constitution Bench > 5 Judges)
  - `Modifier_2 = -75` (if pending review/curative petition)
  - `Modifier_3 = +100` (if consistently followed in the last 10 years without distinction)
- **Action:** Cases with a score $< 100$ are deprioritized. The Swarm is forced to search for higher-ranking precedent before mutating the AST.

## 3. THE ECHO-CHAMBER DESTRUCTION PROTOCOL
If the Petitioner and Opponent begin to agree on a hallucinated premise (a localized echo chamber), the Algo intervenes.

### STAGE 3: THE FORCED CONTRARIAN INJECTION
- **Signal:** Both adversarial agents reach a consensus probability $> 0.95$ on a fact not explicitly present in the ZK-SNARK ledger.
- **Action:** The Algo injects a `CHAOS_TOKEN` into the context window.
- **Effect:** Forces the Verifier to execute an emergency 100,000x localized query against the fact. If the fact fails, both the Petitioner and Opponent suffer a massive UCT penalty, breaking the hallucinated consensus.

# Prompts Diff Audit: v0.0.0.4 to v0.0.0.5

This document details the transition from the single-layered sequential prompt structure of v0.0.0.4 to the highly rigorous, 4-branch nested structure of v0.0.0.5.

## Structural Changes Summary

### 1. Nesting Depth and Branching
- **Old Structure (v0.0.0.4):** Linear path of Stage -> Sub-Stage -> Micro-Step -> Sub-Micro -> Ultra-Deep-Micro (only 1 child per level).
- **New Structure (v0.0.0.5):** Each Stage branches into exactly 4 Sub-Stages, with each Sub-Stage branching into 4 Micro-Steps, and the first branch fanning out into 4 Sub-Micros, 4 Sub-Micro-Subs, and 4 Ultra-Deep-Micros.

### 2. File Updates
- `master_prompt_1.md`: Expanded STAGE 1, 2, 3, and 4 to 4x4x4x4 branching structure. Added Base64 Payload Decoding, Metadata Integrity Audit, Cryptographic Envelope Decoupling, and Dynamic Schema Matching.
- `master_prompt_2.md`: Expanded STAGE 1, 2, 3, and 4. Added Statutory Timer, Territorial Boundaries, Subject Matter Jurisdiction, and Locus Standi validation.
- `master_prompt_3.md`: Expanded STAGE 1, 2, 3, and 4. Added Citation String Matching, Precedent Ranking & Filtering, Factual Delta Computation, and Ratio Extraction.
- `master_prompt_4.md`: Expanded STAGE 1, 2, 3, and 4. Added Verification Vector Initialization, Temporal and Meteorological Verification, ZK-SNARK Attestation Verification, and Transaction Token Emitting.
- `master_prompt_5.md`: Expanded STAGE 1, 2, 3, and 4. Added Inbound Queue Processing, Margin and Indentation Checks, Cognitive Load Index (CLI) Validation, and Evidentiary Anchoring.
- `master_prompt_6.md`: Expanded STAGE 1, 2, 3, and 4. Added Verification of Proof Integrity, Formatting Guidelines Scraping, Text Content Comparison, and Defect Classification.
- `master_prompt_7.md`: Expanded STAGE 1, 2, 3, and 4. Added Load-Bearing Node Extraction, Semantic Equivalence Testing, Cryptographic Anchor Verification, and Presentation JSON Construction.
- `master_prompt_8.md`: Expanded STAGE 1, 2, 3, and 4. Added Argument Vector Analysis, Subject Matter Jurisdiction Verification, Weak Node Identification, and Adjudication JSON Construction.
- `master_prompt_9.md`: Expanded STAGE 1, 2, 3, and 4. Added Compute Resource Allocator, Sliding-Window Token Audit, Jailbreak Signature Scanning, and Case Survivability Monitoring.
- `master_prompt_10.md`: Expanded STAGE 1, 2, 3, and 4. Added Typesetting and Invocation, Binary Structure Integrity, Markdown Sanitization, and Package Zip Construction.
- `master_prompt_11.md`: Expanded STAGE 1, 2, 3, and 4. Added Root Node Definition, Reward Retrieval, Glitch Candidate Detection, and Principal Variation Snapshot.

## Diff Snippet Example (master_prompt_1.md Stage 2)

```diff
-### STAGE 2: INTERNAL CONSISTENCY RE-CHECKS
-- **Sub-Stage 2.1:** Micro-Verification Thread Spawning.
-  - **Micro-Step 2.1.1:** For generated claim $C_i$, spawn 10 parallel loops.
-    - **Sub-Micro 2.1.1.1:** Execute `verify_claim(C_i, F_{matrix})` across varying temperature bounds.
-      - **Sub-Micro-Sub 2.1.1.1.1:** Calculate the resulting Bayesian Confidence Score.
-      - **Ultra-Deep-Micro 2.1.1.1.1.1:** If confidence $< 0.99$, apply Quant penalty: $UCT = UCT - 50.0$.
+### STAGE 3: INTERNAL CONSISTENCY RE-CHECKS
+- **Sub-Stage 3.1:** Micro-Verification Thread Spawning.
+  - **Micro-Step 3.1.1:** For generated claim $C_i$, spawn 10 parallel loops.
+    - **Sub-Micro 3.1.1.1:** Execute `verify_claim(C_i, F_{matrix})` across varying temperature bounds.
+      - **Sub-Micro-Sub 3.1.1.1.1:** Calculate the resulting Bayesian Confidence Score.
+      - **Sub-Micro-Sub 3.1.1.1.2:** Apply Quant penalty: $UCT = UCT - 50.0$ if confidence $< 0.99$.
+      - **Sub-Micro-Sub 3.1.1.1.3:** Run semantic contradiction detection routines.
+      - **Sub-Micro-Sub 3.1.1.1.4:** Trigger node split if claims contain dual logic.
+    - **Sub-Micro 3.1.1.2:** Measure cosine distance of claim to $F_{matrix}$ roots.
+    - **Sub-Micro 3.1.1.3:** Generate alternate negation claim states.
+    - **Sub-Micro 3.1.1.4:** Count frequency of non-factual entities in text.
+  - **Micro-Step 3.1.2:** Evaluate logical connectivity between premise and conclusion.
+  - **Micro-Step 3.1.3:** Perform structural pattern analysis on generated clauses.
+  - **Micro-Step 3.1.4:** Assign local validation vectors to the claim object.
```

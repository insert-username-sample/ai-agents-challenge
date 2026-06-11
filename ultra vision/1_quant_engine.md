# QUANTITATIVE RULES ENGINE (THE "QUANT")
## VERSION: v0.0.0.5

This document defines the raw mathematical bounds, UCT penalizations, and Bayesian probability shifts that govern the 8-Agent MCTS Legal Simulation. It operates purely on floating-point precision to mathematically detect and destroy hallucinated states.

## 1. THE BAYESIAN HALLUCINATION DETECTION THRESHOLD
Let $P(H|E)$ be the probability that a factual claim $H$ is a hallucination given the evidentiary matrix $E$.
- Base prior for any LLM-generated claim: $P(H) = 0.95$ (Assume 95% of LLM output is structurally biased or hallucinatory).
- Evidentiary Weight $W(E)$: Calculated by the Verifier Agent's 10,000x recursive loops.
- If $W(E)$ does not yield a posterior probability $P(\neg H|E) > 0.9999$, the node is classified as `STOCHASTIC_NOISE`.

## 2. UCT PENALIZATION MATRICES
The Monte Carlo Tree Search utilizes the UCB1 formula:
$UCT = \frac{V_i}{N_i} + C \sqrt{\frac{\ln N}{N_i}}$

### Dynamic Penalties (Applied by the Quant Engine):
- **Formatting Variance:** If the Drafter detects a margin error, $V_i = V_i - 10.0$.
- **Temporal Mismatch:** If the `verify_temporal_grounding.py` gate flags a date logic error (e.g., entity age > retirement cap), $V_i = -\infty$ (Node Pruned).
- **Precedent Hallucination:** If the Reviewer's 100x query detects a distinguished case, $V_i = V_i - 150.0$.
- **Evidentiary Forgery:** If the Verifier detects anomalous ZK-SNARK hashes, $V_i = V_i - 5000.0$.

## 3. PRECISION BOUNDARIES
- Floating-Point Audit: Backpropagation summations must not drift by more than $1 \times 10^{-6}$.
- The Quant engine forces the Swarm to compute in deterministic $\mathbb{R}^n$ space, completely stripping stochastic LLM assumptions.

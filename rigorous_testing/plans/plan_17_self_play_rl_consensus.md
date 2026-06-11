# IMPLEMENTATION PLAN 17: SELF-PLAY RL CONSENSUS & MULTI-AGENT SWARM LOOPS (v0.0.0.1 ALPHA)

---

## 1. Objective & Strategic Legal Simulations

This plan outlines the self-play reinforcement learning loop designed to model litigation strategies. 

Standard agentic setups run static text loops that fail to capture the adversarial nature of court litigation. Clausely v1.5 maps the interaction between opposing counsel, judiciary elements, and mediators as an active RL game search, similar to AlphaGo's adversarial self-play.

```
                  [Strategist Swarm Intake]
                              │
                              ▼
            ┌─── [petitioner_agent Drafts State]
            │                 │
            ▼                 ▼
 [reviewer/verifier/objector/presenter gates] <─── [opponent_agent Attacks State]
            │                 │
            ▼                 ▼
            └─── [judge_agent Rules on State]
```

By framing legal strategy as an adversarial tree search, we evaluate thousands of simulated courtroom timeline forks to discover the most robust legal arguments.

---

## 2. Adversarial Self-Play Swarm Spec

### 1. The Multi-Agent Role Specification
The strategist swarm represents exactly 7 canonical legal roles working in a closed-loop self-play arena:
1.  **petitioner_agent**: Drafts alternative legal claims and writ demands under Article 226/227.
2.  **opponent_agent**: Challenges claims, raises procedural objections, and identifies unexhausted alternative remedies.
3.  **reviewer_agent**: Reviews drafting quality, factual consistency, party standing, and completeness.
4.  **verifier_agent**: Verifies statutes, citations, and legal propositions with grounding records.
5.  **objector_agent**: Attacks maintainability, limitation, jurisdiction, registry compliance, and evidence gaps.
6.  **presenter_agent**: Synthesizes the grounded strategic memorandum.
7.  **judge_agent**: Simulates bench assessment and probability-weighted outcomes after the six analysis agents run.

Melaquera is a separate future System 5 capability. It is not the correction layer for ordinary hallucinations in this strategist plan. The strategist itself must enforce per-step grounding before each smallest deduction or prediction proceeds.

### 2. State-Space Representation & Node Expansion
*   **State ($S_t$)**: The current set of facts, active pleadings, cited precedents, and procedural status.
*   **Action ($A_t$)**: A tactical litigation step (e.g. arguing alternative remedy, raising preliminary objections).
*   **State Value ($V(S_t)$)**: Derived by backpropagating the outcome accuracy of simulated paths through the tree:

$$V(S_t) = \frac{1}{N_{sim}} \sum_{i=1}^{N_{sim}} R_i$$

Where:
- $R_i \in [-1, 1]$: The procedural validity reward score derived from per-step grounding, contradiction checks, and canonical agent outputs at the end of simulation $i$.

---

## 3. Dynamic Rollout Control & Convergence Bounds

*   **Adaptive Rollout Horizon**: The number of search iterations scales dynamically based on case complexity. Simple procedural steps run 57 MCTS visits, whereas complex constitutional writs scale to thousands of simulations.
*   **Convergence Metric**: Simulations run until the variance of $V(S_t)$ drops below $\epsilon = 10^{-4}$ for three consecutive steps, preventing infinite loops and ensuring high-fidelity convergence.

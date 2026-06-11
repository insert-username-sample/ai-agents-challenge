# IMPLEMENTATION PLAN 2: MCTS STRATEGIST SIMULATION SWARM (v0.0.0.1 ALPHA)

---

## 1. Objective & Simulation Topology

This plan specifies the architecture of the **Micro-Grounded MCTS Swarm** running over the **10 recent cases (2024-2026)**.

```
                           [MCTS Root: Case Brief]
                                      │
           ┌──────────────────────────┴──────────────────────────┐
           ▼                                                     ▼
 [7-Agent Strategist Swarm]                            [Future System 5 Boundary]
 - petitioner_agent  - opponent_agent                  - Melaquera is not part
 - reviewer_agent    - verifier_agent                    of this strategist
 - objector_agent    - presenter_agent                   implementation cycle.
 - judge_agent
```

### Swarm Agent Configurations:
1.  **petitioner_agent**: Drafts the arguments, highlighting client facts.
2.  **opponent_agent**: Raises procedural challenges, delay objections, and alternative remedy exceptions.
3.  **reviewer_agent**: Compiles a 47-point drafting quality checklist.
4.  **verifier_agent**: Cross-references citations against the active database index.
5.  **objector_agent**: Attacks standing, maintainability, limitation, registry, and evidentiary gaps.
6.  **presenter_agent**: Compiles the final briefing packet.
7.  **judge_agent**: Renders the simulated ruling based on current statutory weights.

Melaquera is a separate future System 5 capability. It must not be documented or implemented as an eighth strategist agent in this plan, and it must not substitute for per-step grounding by the seven canonical strategist agents.

---

## 2. Adaptive Tree visits Scaling (AlphaGo-Style)

We enforce **Dynamic Tree Depth Visits Scaling** rather than a hardcoded iteration count. The simulator calculates visit parameters dynamically based on the byte-length of the retrieved facts:

$$\text{Simulations (N)} = \max\left(57, \min\left(3000, \text{Len(Case Facts)} \times 12 + \text{random.randint}(100, 300)\right)\right)$$

### MCTS Search Stages executed:
1.  **Selection**: Recursively traverses the tree using the penalized $UCT$ equation:
    $$UCT(node) = \frac{W_i}{N_i} + c \sqrt{\frac{\ln N_p}{N_i}} - \lambda P_{assumption}$$
2.  **Expansion**: If a leaf node is reached, it expands with Grounded Path (RAG verified) vs Prior Shortcut (hallucinated prior) nodes.
3.  **Simulation**: Evaluates step validity. Grounded paths receive a reward of 1.0; ungrounded prior shortcuts or clock mismatches receive a reward of 0.0.
4.  **Backpropagation**: Propagates the reward up the tree, updating UCT scores.

---

## 3. Output Requirements

For each of the 10 recent cases, the simulator outputs:
- **Optimal Grounded Pathway**: Mapped procedural checks.
- **Outcomes Probability Matrix**: Success rates based on grounded vs. default trajectories.
- **Mediation Report**: Veto overrides and safety checks executed by Mediator Melaquera.

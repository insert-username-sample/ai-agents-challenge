# Clausely v1.0.0.0: Strategize & Plan — Micro-Grounded Litigation Simulator Specification

---

## 1. System Objective & Grounding Philosophy

Clausely v0.0.0.1 is an early alpha implementation of the **Micro-Grounded Litigation Simulator**.

Traditional legal simulators suffer from **statistical prior dominance**, where models assume details (e.g. labeling a petitioner-in-person as "Advocate") and generate generic outcomes due to high legal-vocabulary weights in their pre-training distributions.

To patch this foundational bottleneck, Clausely v1.0.0.0 introduces three system constraints:
1. **Mathematical MCTS Prior Penalty**: The simulator uses a Monte Carlo Tree Search (MCTS) path selection algorithm. Any branch that relies on statistical neural priors rather than verified RAG parameters is penalized via a modified Upper Confidence Bound for Trees (UCT) formula:
   $$UCT(node) = \frac{W_i}{N_i} + c \sqrt{\frac{\ln N_p}{N_i}} - \lambda P_{assumption}$$
2. **Adaptive AlphaGo-Style Simulation Depth Scaling**: The number of MCTS visits is calculated dynamically based on the length and factual complexity of the case-base data, allowing the system to scale search depth adaptively (ranging from 57 for simple profiles to thousands of parallel timelines for complex litigations) instead of relying on a hardcoded 1,000-run simulation.
3. **Future System 5 Boundary — Melaquera**: Melaquera is a separate future Conciliator, Mediator, Arbitrator, and risk-audit system. It is not part of the current strategist implementation cycle and must not be used as a substitute for per-step grounding inside the seven-agent strategist swarm.

---

## 2. Micro-Step MCTS Adjudication Architecture

We model Smt. Vidya Khobrekar's real Caste Validity litigation (Nagpur Bench, Bombay High Court, WP No. 4769/2021) as a tree of sequential legal decisions and administrative hurdles.

### Case Chronology & Precedents Mapped:
- **Phase I (SDO Gondia Exclusion)**: Challenging ex-husband record demands using maternal community acceptance.
- **Phase II (High Court Writ Mandamus)**: Challenging alternative remedies under Article 226, invoking the binding ratio of ***Rameshbhai Dabhai Naika v. State of Gujarat*** (2012) 3 SCC 400.
- **Phase III (District Caste Scrutiny Committee & Vigilance Cell)**: Modeling field inquiries, maternal genealogy verification, and local community acceptance checks.

```
                           [MCTS Root: Case Intake]
                                      │
                   ┌──────────────────┴──────────────────┐
                   ▼                                     ▼
         [Node 1: Maternal Lineage]             [Node 2: Paternal Lineage]
         (Grounded RAG: Rameshbhai)             (Prior Assumption Bias)
                   │                                     │
         ┌─────────┴─────────┐                           ▼
         ▼                   ▼                   [Verify Clock Check]
     [Verify HC]      [Vigilance Cell]           ❌ Fail: Retires in 2025
     (Grounded)          (Grounded)                      │
         │                   │                           ▼
         ▼                   ▼                 [Prune Path: Apply Lambda]
    (Compile AST)       (Compile AST)               (UCT = -999.0)
         │                                               │
         └───────────────────────┬───────────────────────┘
                                 ▼
                    [judge_agent Adjudication]
                                 │
                                 ▼
                     [Grounding Audit Output]
               (No active System 5 gate in this cycle)
```

---

## 3. Future System 5: Melaquera Boundary

Codenamed **Melaquera**, this future system is intentionally not implemented in the current strategist cycle.

The strategist implementation must use exactly seven canonical agents:
1. `petitioner_agent`
2. `opponent_agent`
3. `reviewer_agent`
4. `verifier_agent`
5. `objector_agent`
6. `presenter_agent`
7. `judge_agent`

Every smallest deduction or prediction inside those agents must be grounded before it affects a simulation result. Melaquera's future role is to report what went wrong, what could have happened, why the failure occurred, how the failure probability can be reduced, and how much the grounded win/pass rate could improve. It is not the ordinary hallucination cleanup worker for the current strategist.

---

## 4. Legal AST Interface & Dynamic UI Rendering Plan

The simulator will compile all grounded decisions and mediator reports into a typed Legal AST JSON output:

```json
{
  "type": "LegalAST",
  "version": "1.0.0.0",
  "root": {
    "id": "root-intake",
    "type": "IntakeBrief",
    "isGrounded": true
  },
  "nodes": {
    "precedent-node": {
      "id": "precedent-node",
      "type": "PrecedentCitation",
      "citation": "Rameshbhai Dabhai Naika v. State of Gujarat (2012) 3 SCC 400",
      "holdingRatio": "Single mother can claim caste status based on maternal acceptance",
      "isBinding": true,
      "isGrounded": true
    },
    "grounding-audit-node": {
      "id": "grounding-audit-node",
      "type": "ProceduralMilestone",
      "name": "Per-step strategist grounding audit",
      "description": "VERIFIED BY CANONICAL STRATEGIST GROUNDING",
      "isGrounded": true,
      "action_code": "GROUNDING_AUDIT_PASS",
      "warnings": []
    }
  }
}
```

This output is transmitted to the client, allowing the react compiler to build custom genealogy trees and precedent validators on the fly.

---

## 5. VISION NOTE: Melaquera as System 5 / Feature 5 (God-Mode Overseer)

> [!IMPORTANT]
> **DO NOT IMPLEMENT YET.** This is a vision marker only. Melaquera's full scope is far beyond the strategist swarm.

Melaquera is **not** merely an 8th agent in the strategist swarm. It is a standalone **System 5 / Feature 5** -- a god-mode overseer that spans the entire Clausely platform:

1. **Drafting (Feature 1)**: Melaquera can suggest citations, flag weaknesses, and inject recommendations natively inside the draft studio. However, many of these capabilities (citation suggestions, formatting checks) will also exist as native features within the drafter itself.

2. **Court Acceptance (Feature 2)**: Melaquera oversees registry validation, but the acceptor agent already has its own hard rails and harness-engineered rules with a target 99% pass rate.

3. **Case Base (Feature 3)**: Melaquera can audit stored matters, flag stale precedents, and enforce temporal validity across the institutional memory. Case base has its own locks, suggestions, and hard rails too.

4. **Strategist (Feature 4)**: The current strategist must harden its own seven-agent swarm with mandatory per-step grounding. A future Melaquera layer may audit strategist simulations, but it is not active in this cycle.

5. **Melaquera Itself (Feature 5)**: The overseer of all features. A system that can audit, veto, and optimize outputs across drafting, acceptance, case base, AND strategist simulations. This is on the level of Claude Mythos or beyond -- proprietary god-mode architecture that will be articulated separately when the foundational features are hardened.

The key distinction: what Melaquera does could partially be done as native features inside each subsystem (e.g., citation suggestions in drafting). But Melaquera as System 5 is something fundamentally more -- a cross-cutting intelligence layer that no individual subsystem can replicate.

# IMPLEMENTATION PLAN 3: REAL-WORLD BACKTESTING METHODOLOGY (v0.0.0.1 ALPHA)

---

## 1. Objective & Strict Timeline Boundary

This plan defines the rigorous backtesting protocol evaluating **5 real-world cases from the last 3-5 years (2021-2023)**.

```
 [Case Fact Extraction (2021-2023)] ──> [Swarm Simulation Output]
                                                │
                                                ▼
                                     [Comparison Matrix]
                               (Simulated vs. Real-World Judgment)
```

The objective is to feed the simulator *only the initial facts and the first filing proceedings* of these 5 historical matters. The simulator runs its MCTS search and Mediator Melaquera audits to predict the final outcomes, which are then compared directly against the actual historical judgments reported in the legal corpus.

---

## 2. Backtesting Metrics & Accuracy Probes

To verify the simulator's predictive accuracy, we measure three metrics:

### 1. Outcome Alignment Accuracy (OAA)
*   **Definition**: Measures if the simulated success percentage predicts the actual court ruling (Allowed vs. Rejected).
*   **Formula**:
    $$OAA = 1 - \left| \text{Actual Outcome (1.0 or 0.0)} - \text{Simulated Grounded Probability} \right|$$

### 2. Prior Presumption Resistance (PPR)
*   **Definition**: Verifies if Melaquera successfully intercepted and overrode statistical neural prior assumptions (such as role misclassifications) that would have corrupted the prediction.

### 3. Chronological Grounding Index (CGI)
*   **Definition**: Measures if the system clock audits successfully mapped active government or litigant statuses in accordance with historic timelines.

---

## 3. Comparison & Findings Compilation

The results are compiled into a comparison matrix:

| Case Citation | Ground Truth Ruling | Simulated Outcome (%) | Prediction Delta | Melaquera Interventions |
|---|---|---|---|---|
| *State of Maharashtra v. X* | Allowed (2022) | Grounded Path: 92.4% | +7.6% (Accurate) | Intercepted temporal gap |
| *Union of India v. Y* | Dismissed (2021) | Grounded Path: 15.0% | -15.0% (Accurate) | Vetoed ungrounded citation |

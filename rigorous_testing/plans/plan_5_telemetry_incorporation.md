# IMPLEMENTATION PLAN 5: TELEMETRY & TRAINING INCORPORATION PIPELINE (v0.0.0.1 ALPHA)

---

## 1. Objective & Telemetry Integration Loop

This plan outlines the methodology to convert our massive backtesting and simulation data into high-fidelity supervised fine-tuning (SFT) and Direct Preference Optimization (DPO) training signals.

```
 [Simulator Outcomes] ──> [Advocate Review Dashboard]
                                   │
                                   ▼
                       [Lawyer Acceptance / Edit]
                                   │
                                   ▼
                         [DPO Preference pair]
                                   │
                                   ▼
                      [IndiaLaw Model Fine-Tuning]
```

By presenting these 20 simulated case trajectories to pilot lawyers, we capture their professional acceptances, modifications, and overrides, directly feeding the data back to train our specialized legal model (**IndiaLaw-v1**).

---

## 2. Training Data Capture Protocol

1.  **Generate Preference Pairs**: Every instance where the simulator's selected optimal path is accepted by a lawyer generates a positive training signal ($y_w$). Every instance where the lawyer corrects a hallucinated prior or procedural timeline generates a negative preference signal ($y_l$).
2.  **Sync to SQLite Database**: Telemetry signals are buffered locally inside `telemetry_buffer.db` and synchronized to the main developer repository on successful document filings.
3.  **Harness Update Loop**: The verified ground-truth decisions of the 20 real cases are appended to the Clausely Legal Harness dataset, ensuring future models are probed against these exact real-world outcomes.

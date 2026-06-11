# IMPLEMENTATION PLAN 6: MCTS HYPERPARAMETER OPTIMIZATION (v0.0.0.1 ALPHA)

---

## 1. Objective & Hyperparameter Space

This plan formalizes the optimization parameters for the Upper Confidence Bound applied to Trees (UCT) equation in Clausely v1.0.0.0:

$$UCT(node) = \frac{W_i}{N_i} + c \sqrt{\frac{\ln N_p}{N_i}} - \lambda P_{assumption}$$

We must calibrate the exploration constant ($c$) and the prior-bias penalty constant ($\lambda$) to ensure the search tree successfully prunes ungrounded pathways without stopping exploration of non-obvious grounded options.

---

## 2. Hyperparameter Grid Settings

The search engine will run grid evaluations across three primary dimensions:

### 1. Exploration Constant (c)
*   *Range*: $[0.5, 2.5]$
*   *Optimal Target*: $1.414$ (standard mathematical balance for exploration vs. exploitation).
*   *Calibration*: Lowering $c$ encourages exploitation of verified court decisions, while raising $c$ forces the model to explore alternative, non-obvious procedural forks (e.g. searching for minor High Court registry exemptions).

### 2. Prior-Bias Penalty (Lambda)
*   *Range*: $[10^2, 10^4]$
*   *Optimal Target*: $10^3$ ($1000.0$)
*   *Calibration*: A high $\lambda$ ensures that any node possessing a high $P_{assumption}$ (neural prior probability) is instantly assigned a deeply negative UCT value, pruning that branch from the search tree permanently.

### 3. Simulation Iteration Bounds
*   *Range*: Dynamic scaling $[57, 5000]$ based on factual complexity bytes.

---

## 3. Automated Validation Pipeline

During backtesting runs, the system records search trajectory metrics (total visits, duplicate paths pruned, validation errors caught) to output an optimized hyperparameter state log in the findings directory.

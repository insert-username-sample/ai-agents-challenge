# IMPLEMENTATION PLAN 10: DPO REWARD MODELING & FINE-TUNING (v0.0.0.1 ALPHA)

---

## 1. Objective & Direct Preference Optimization (DPO)

This plan formalizes the optimization parameters for **DPO fine-tuning** Kimi K2.6 and Step-Fun 2.7 Flash using the preference corpus collected during pilot advocate testing.

```
 [Pilot Preference Pairs] ──> [Reward Model Training] ──> [IndiaLaw-v1 Fine-Tuning]
```

By directly optimizing on preference pairs (Accepted vs. Rejected drafts), we bypass the need for a separate reward model, updating the model's policy weights directly to suppress statistical priors.

---

## 2. Loss Function & Optimization Specification

We train the model using the DPO loss function:

$$\mathcal{L}_{DPO}(\theta; \theta_{ref}) = - \mathbb{E}_{(x, y_w, y_l) \sim \mathcal{D}} \left[ \ln \sigma \left( \beta \ln \frac{\pi_\theta(y_w \mid x)}{\pi_{ref}(y_w \mid x)} - \beta \ln \frac{\pi_\theta(y_l \mid x)}{\pi_{ref}(y_l \mid x)} \right) \right]$$

### Key Optimization Parameters:
1.  **DPO Beta ($\beta$)**:
    *   *Value*: $0.1$
    *   *Purpose*: Controls the KL-divergence constraint relative to the reference model ($\pi_{ref}$). Ensures the fine-tuned model preserves general reasoning and legal knowledge.
2.  **QLoRA Rank ($r$)**:
    *   *Value*: $64$ (target projection layers `q_proj`, `v_proj`, `k_proj`, `o_proj`).
3.  **QLoRA Alpha ($\alpha$)**:
    *   *Value*: $128$
4.  **Learning Rate**:
    *   *Value*: $5 \times 10^{-5}$ with a cosine decay schedule.

---

## 3. Training Validation

Before production deployment, the fine-tuned weights are evaluated against the Clausely Legal Harness. The weights are merged only if they achieve a $\ge 98\%$ pass rate across the role and temporal assumption failure categories.

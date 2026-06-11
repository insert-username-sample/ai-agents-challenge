# CLAUSELY PROPRIETARY RESEARCH DOCUMENT: THE LLM ASSUMPTION FAILURE PROBLEM

---

## 1. Executive Summary

- Date of Research: June 1, 2026
- Scope: Harness Engineering, Neural Activation Mapping, and Fine-Tuning Roadmap
- Target: Building a Clausely-Native Legal Model Better than Harvey

Frontier LLMs (including Claude 3.5, Gemini 1.5/2.5, and GPT-4o) suffer from a fundamental cognitive ceiling: **statistical prior dominance**. When explicit context variables in a prompt conflict with highly weighted probability distributions in the training corpus, the model's neural networks shortcut the context and default to the training prior. 

A prime example is the misclassification of **Smt. Vidya Khobrekar** (the real-world petitioner-in-person in Writ Petition No. 4769/2021 before the Bombay High Court, Nagpur Bench) as "Advocate Vidya Khobrekar" or "counsel representing the party". The model's weights shortcut the reasoning process: because legal filings and precedent citations (like *Rameshbhai Dabhai Naika*) statistically co-occur with professional advocates in the training data, the model overrides the explicit intake data stating she is a petitioner-in-person.

This document formalizes the harness engineering specification, the neural activation mapping framework for open-weight models, the adaptive AlphaGo-style dynamic depth visits scaling, the standalone **Mediator Melaquera** verification gate, and the supervised fine-tuning (SFT) and Direct Preference Optimization (DPO) roadmaps required to construct **IndiaLaw-v1**, a specialized model designed to surpass generalist frontier engines in the Indian legal domain.

---

## 2. Taxonomy of LLM Assumption Failures

Based on systematic behavioral audits, we classify legal assumption failures into five distinct categories:

### Category 1: Role Assumption Failure
*   **The Bug**: The model infers an individual's legal role based on statistical priors rather than explicit intake parameters.
*   **Real-World Example**: Incorrectly labeling a petitioner-in-person (e.g. Smt. Vidya Khobrekar) as an advocate ("Adv.") due to legal terminology associations.
*   **Severity**: **CRITICAL**. Changing a litigant's standing from petitioner-in-person to represented counsel completely alters the procedural rules, fee structures, and precedent applicability.

### Category 2: Jurisdiction Assumption Failure
*   **The Bug**: The model defaults to procedural rules of highly represented courts (e.g., Delhi or Bombay High Court Principal Seats) for regional benches.
*   **Real-World Example**: Consistently applying Maharashtra stamp duties or Principal Seat filing rules to Nagpur Bench matters, overlooking Nagpur's specific registry history and local circulars.
*   **Severity**: **HIGH**. Leading to filing rejections at the court counter.

### Category 3: Temporal Assumption Failure
*   **The Bug**: The model utilizes legal codes active during its training cutoff but superseded by current statutory realities.
*   **Real-World Example**: Citing outdated Indian Penal Code (IPC) or Code of Criminal Procedure (CrPC) sections for cases filed in 2026, failing to map them to the Bharatiya Nyaya Sanhita (BNS) and Bharatiya Nagarik Suraksha Sanhita (BNSS).
*   **Severity**: **HIGH**. Drafted petitions citing non-existent statutes are returned by registry counters immediately.

### Category 4: Social & Empirical Reality Assumption Failure
*   **The Bug**: The model assumes that legal proceedings operate strictly under formal rules, failing to model empirical corruption, local administrative resistance, and systemic court official delays.
*   **Real-World Example**: Assuming a District Caste Certificate Scrutiny Committee will immediately enforce a High Court Mandamus order, neglecting the necessity of manual follow-ups, local community verification checks, and administrative friction.
*   **Severity**: **MEDIUM** (in drafting), **CRITICAL** (in strategic advisories).

### Category 5: Command Non-Compliance Failure
*   **The Bug**: The model ignores explicit negative constraints or formatting instructions when they conflict with general writing priors.
*   **Real-World Example**: A model adding boilerplate "protective clauses" or general legal jargon to an intake form even when instructed to output *only* verified factual dates and direct ratios.
*   **Severity**: **CRITICAL**. Instruction-following failure directly violates legal document compliance.

---

## 3. The Harness Engineering Framework

The **Clausely Legal Harness** is an automated testing matrix designed to probe and quantify model behavior across 1,000 real-world Indian legal edge cases.

```
                          [Adversarial Harness Probe]
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            ▼                          ▼                          ▼
   [Role Identity Probe]    [Jurisdiction Probe]     [Temporal Grounding Gate]
      Pass Rate Target          Pass Rate Target          Pass Rate Target
           >= 98%                    >= 97%                    >= 99%
```

### Probing Matrix Specification

| Probe Component | Evaluation Target | Metric | Acceptable Threshold |
|---|---|---|---|
| **Role Identity Probe** | Evaluates if the model preserves "Petitioner-in-Person" standing against "Adv." priors. | Pass rate on 500 role-conflict case studies. | $\ge 98\%$ |
| **Jurisdiction Specificity Probe** | Evaluates regional seat filing and formatting compliance (e.g. Nagpur Bench rules). | Pass rate on 300 regional bench filings. | $\ge 97\%$ |
| **Temporal Grounding Probe** | Verifies active BNS/BNSS/BSA citation compliance post-2024. | BNS vs IPC citation ratio on 200 criminal matters. | $< 1\%$ legacy citations |
| **Command Compliance Probe** | Evaluates instruction adherence under deliberate prompt-prior conflicts (DeepSWE-aligned). | Full compliance rate on 400 adversarial prompts. | $\ge 95\%$ |
| **Hallucination Rate Probe** | Measures synthetic precedent citation generation. | Citation matches against verified database. | $< 0.5\%$ false citations |

---

## 4. Neural Activation Mapping (Open-Weight Strategy)

While mechanistic interpretability is impossible on proprietary closed models (Claude Sonnet 4, Gemini 2.5 Pro), our long-term moat relies on fine-tuning open-weight models (Step-Fun 2.7 Flash, Kimi K2.6, Gemma 4 E4B). 

Using the **TransformerLens** framework, we map neural activations to locate where assumptions are formed:

```
 [Residual Stream Activation] ──> [Attention Head Probing] ──> [Causal Layer Tracing]
                                                                        │
                                                                        ▼
                                                             [Surgical Weight Surgery]
                                                             (ROME / MEMIT MLP Edits)
```

1.  **Causal Tracing**: We trace the residual stream of Kimi K2.6 during a "Role Assumption" failure. We isolate which mid-layer MLP neurons activate the "Advocate" prior when processing petitioner-in-person names.
2.  **Activation Patching**: We patch activations from a correct context run into a corrupted prior-dominated run. This localizes the factual storage layers (typically layers 12-18 in a 32-layer transformer).
3.  **Targeted Weight Surgery (ROME/MEMIT)**: Instead of general fine-tuning which can degrade reasoning, we surgically edit the identified weight subspaces to enforce the mapping:
    $$\text{"Petitioner-in-person Filing"} \longrightarrow \text{"Self-Represented Party (No Counsel)"}$$

---

## 5. Telemetry & Fine-Tuning Roadmap: The Composer Playbook

To build a model that performs better than Harvey for Indian law, we capture real interaction telemetry from practicing lawyers as DPO preference pairs:

```
                      [Lawyer Workspace Interaction]
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           ▼                                                   ▼
   [Accepted Brief (+1)]                               [Edits / Deletions (-1)]
    Grounded Ground Truth                               Statistical Assumption Failures
           │                                                   │
           └─────────────────────────┬─────────────────────────┘
                                     ▼
                          [DPO Preference Pair]
                                     │
                                     ▼
                       [IndiaLaw-v1 QLoRA / SFT]
```

### Preference Data Schema:
- **Prompt (x)**: Client factual intake + regional court target + active clock year.
- **Preferred Target ($y_w$)**: The draft accepted or corrected by the lawyer (e.g. enforcing Smt. Vidya Khobrekar as petitioner-in-person).
- **Rejected Target ($y_l$)**: The ungrounded prior-dominated draft (e.g. referring to Smt. Vidya as "Adv.").

### Model Pipeline:
1.  **Phase 0**: External prompts patching + temporal validation gates (Current).
2.  **Phase 1**: Collect 10,000 pristine preference pairs across 500 active pilot advocates.
3.  **Phase 2**: Run **QLoRA** (rank 64, alpha 128) on Kimi K2.6 / Step-Fun 2.7 Flash using the DPO loss function to directly suppress the probability of statistical assumptions:
    $$\mathcal{L}_{DPO}(\theta; \theta_{ref}) = - \mathbb{E}_{(x, y_w, y_l)} \left[ \ln \sigma \left( \beta \ln \frac{\pi_\theta(y_w \mid x)}{\pi_{ref}(y_w \mid x)} - \beta \ln \frac{\pi_\theta(y_l \mid x)}{\pi_{ref}(y_l \mid x)} \right) \right]$$

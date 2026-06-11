# IMPLEMENTATION PLAN 7: ADVERSARIAL SWARM INTERACTION RULES (v0.0.0.1 ALPHA)

---

## 1. Objective & Swarm Constraints

This plan defines the structured protocols governing how the **7 strategist agents** interact during litigation simulations. 

Without strict communication rules, multi-agent swarms default to cooperative bias, where all agents agree with the initial draft. Clausely v1.0.0.0 enforces a strict adversarial protocol to continuously attack and verify legal claims.

```
 [Intake Brief] ──> [Petitioner Agent] ──> [Opponent Agent (Attack)]
                                                  │
                                                  ▼
                                        [Verifier Agent (Check)]
                                                  │
                                                  ▼
                                         [Judge Agent (Rule)]
```

---

## 2. Agent Interaction & Attack Protocols

### 1. Petitioner vs. Opponent (The Adversarial Core)
*   **Action**: The Petitioner Agent proposes a strategic filing. The Opponent (State) Agent is hard-coded to attack this filing, raising registry objections, delay defects, and statutory blocks.
*   **Constraint**: The Opponent *must* leverage regional court rules (e.g. Nagpur Bench exceptions) rather than generic legal guidelines.

### 2. Verifier & Objector Verification
*   **Action**: The Verifier Agent parses every citation. If a citation lacks a verified RAG record, the Objector Agent triggers an ungrounded prior alert, applying the UCT penalty.

### 3. Reviewer Quality Control
*   **Action**: The Reviewer Agent scores the entire transaction based on a strict 47-point drafting checklist, ensuring party names (e.g. Smt. Vidya Khobrekar as petitioner-in-person) are correctly preserved.

---

## 3. Communication Payloads

All agent transitions utilize structured, typed JSON envelopes to prevent model formatting drift:

```json
{
  "sender": "OpponentAgent",
  "target": "PetitionerAgent",
  "stage": "ObjectionPhase",
  "is_grounded": true,
  "objection_ratio": "Alternative administrative remedies under Caste Scrutiny Act of 2000 are not exhausted.",
  "statute_cited": "Maharashtra Scheduled Castes Regulation Act, 2000"
}
```

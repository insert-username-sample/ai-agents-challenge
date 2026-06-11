# IMPLEMENTATION PLAN 15: REGIONAL COURT FILING & STATE-SPECIFIC BYLAWS LOADER (v0.0.0.1 ALPHA)

---

## 1. Objective & Decentralized Registry Rules

This plan defines the dynamic registry and procedural rules framework. In Indian litigation, High Courts and their respective benches operate under highly fragmented rules (e.g., Bombay High Court Principal Bench vs. Nagpur Bench, or specific regional filing rules of the High Court of Karnataka). 

Prior-dominated LLMs frequently output generic Supreme Court filing checklists, resulting in immediate registry rejection sheets. Clausely v1.5 dynamically loads state-level and bench-level bylaws to constrain MCTS simulations to local filing parameters.

```
 [Registry Intake Parameters] ──> [Bylaw Loader Engine] ──> [MCTS Strategy Constraints]
                                           │
                                           ▼
                                 [Local Bench Rules]
```

---

## 2. Bylaw Dynamic Loading Specification

### 1. Registry Database Schema
*   **Path**: `packages/registry-rules/db.json`
*   **Structure**: Relational registry mapping containing court index thresholds, maximum page limits, specific verification affidavit styles, and index sequences.

### 2. Court Rules Dynamic Adaptation Matrix

| Targeting High Court Bench | Local Filing Constraint | Automated Verification Step |
|---|---|---|
| **Bombay High Court (Nagpur Bench)** | Mandatory translation of Marathi regional vernacular records into English before filing. | Scans AST index list; alerts user if vernacular pages lack English translation nodes. |
| **Karnataka High Court** | Mandatory indexing format referencing exact annexure labels (e.g., Annexure-A, Annexure-B). | Verifies and compiles AST document nodes to adhere strictly to Karnataka numbering protocols. |
| **Delhi High Court** | Strict PDF e-filing bookmarking and metadata formatting regulations. | Compiles PDF output index with interactive bookmarks matching registry specifications. |

### 3. Verification & Compliance Interception
*   During MCTS state evaluation, the simulation triggers a local `BylawVerifier` verification step.
*   If filing rules are violated, the node is flagged as ungrounded (`isGrounded = false`), forcing the dynamic UI compiler to present the advocate with a physical checklist mapping the exact regional rule mismatch.

---

## 3. Deployment Safety

*   All regional rule JSON structures undergo weekly automated syntax validation tests.
*   Any rule missing mandatory authority reference parameters is rejected at compilation time, ensuring that Clausely's dynamic workspace only enforces active statutory provisions.

# Scope of Work (SOW) & Statement of Work
## Project: Clausely Legal Compilation Engine & 8-Agent Swarm

[GATE] Verification state: Production v0.0.0.1 alpha Sandbox prototype.

### 1. Project Background & Objective
Clausely is an AI-powered legal document generation and verification platform. It solves the critical problem of LLM hallucination and rule non-compliance in legal filings by employing an 8-agent Monte Carlo Tree Search (MCTS) simulation swarm combined with a Symbolic Formatting Engine (SFE) compiler and SafeVerify validation gates. This document outlines the Scope of Work (SOW) and Statement of Work (SOW) for testing access and finalizing the alpha prototype.

---

### 2. Scope of Work (SOW)

#### A. 8-Agent Swarm Integration
- **Petitioner Agent:** Proposes litigation arguments and generative claims based on intake facts.
- **Opponent Agent:** Proposes adversarial counter-arguments and identifies legal gaps.
- **Reviewer Agent:** Computes Jaccard index and cosine similarity against historical case precedents.
- **Judge Agent:** Evaluates outcomes and calculates terminal rewards using LoRA bias weights.
- **Drafter Agent:** Translates the winning strategy path into a formal Legal AST (Abstract Syntax Tree).
- **Verifier Agent:** Audits physical, temporal, and coordinate constraints.
- **Objector Agent:** Enforces court layout standards (margins, typography, fonts).
- **Presenter Agent:** Condenses pleadings to fit human cognitive constraints.

#### B. Verification & SafeVerify Gates
- **Statutory Retirement Auditing:** Dynamic pre-flight checks enforcing strict temporal date-math (e.g., retirement age limits like the age-60 civil service retirement cap for Smt. Khobrekar).
- **SFE Compiler Audits:** Real-time formatting error tracking (e.g., margins, alignment, page limits).
- **Sorry-Free Constraint:** Rejection of stubs (`UNVERIFIED` tags or missing citation links).

#### C. Testing & Hosting Access Infrastructure
- **Figma-Style Architecture Board:** Interactive canvas displaying the 8-agent swarm relationships, compiler loops, and math formula states (Gibbs sampling, P-UCB, Elo ratings) with mouse pan/scroll-wheel zoom capabilities.
- **Interactive Code Explorer:** GitHub-style mock code repository viewer showing core codebase files.
- **Testing Access Dashboard:** A live playground interface with prefilled Gemini API key configurations allowing users to run real client-side Gemini Flash audits on custom or workspace-provided mock files.
- **Mock File Workspace:** Dedicated testing documents containing both compliant and intentionally corrupted files (e.g., wrong margins, invalid retirement dates) to verify SFE and temporal error catching.

---

### 3. Statement of Work (SOW) - Schedule & Deliverables

| Phase | Milestone / Deliverable | Target Timeline | Verification Method |
|---|---|---|---|
| **Phase 1** | Rebuild repository and clear security blocks | Day 1 (Completed) | Git remote push validation (`main`) |
| **Phase 2** | Design & deploy Interactive SOW & Testing Dashboard | Day 2 (Active) | Local server test (`public/dashboard.html`) |
| **Phase 3** | Mock File Creation (`client_intake.txt`, `draft_petition.txt`) | Day 2 (Active) | Verification of mock files loading in browser |
| **Phase 4** | Live Gemini Flash Client Integration | Day 2 (Active) | Client-side Gemini connection testing |
| **Phase 5** | Firebase Hosting Deployment | Day 3 | Production access at `https://clausely-ai.web.app` |

---

### 4. Legal Compliance & Grounding Constraints
- **Temporal Anchor:** System evaluations computed relative to Host Date (current 2026).
- **Compliance Rules:** All outputs must use CP1252 Shell Encoding, avoiding Unicode special characters or emojis in system-generated scripts.
- **Failsafe Gates:** Any validation failure triggers immediate execution halts with detailed stack trace diagnostics.

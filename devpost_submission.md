# Devpost Project Submission Copy-Paste Template

Use this template to update your Devpost submission. Each section below corresponds to a specific field on the Devpost project edit page.

---

### [FIELD] Project Title
```text
Clausely ai : Zero-Hallucination Legal Drafting Multi-Agent Swarm
```

---

### [FIELD] Problem to solve
```markdown
Legal drafting is a structurally constrained, high-friction process. Generic LLMs fail in legal production because they are creative writers, not compilers. Generalist chatbots suffer from three fatal flaws:

1. **The Neural Shortcut Trap (Hallucination):** Generalist models use statistical priors to "fill in the blanks," fabricating litigant details, dates, and relationships (such as assuming a *son* is a *daughter* in a family dispute, or citing retired investigators as active officers).
2. **Procedural & Formatting Rejections:** Registry offices reject **8% to 15% of filings** simply because margins (e.g., 3.0cm left, 2.5cm right) or line spacing (1.5x) are off by fractions of a centimeter.
3. **Citation Instability:** AI models routinely cite repealed laws (e.g., citing the old IPC instead of BNS 2024 for Indian courts) or hallucinate non-existent sections.

**Key Fact:** Despite 80% digital coverage of legal precedents, only 20% are effectively utilized because the cost of manually validating AI-generated outputs against these datasets is prohibitive. Most existing systems are merely "prompt-response" wrappers that lack adversarial validation.
```

---

### [FIELD] Our solution
```markdown
**Clausely is a Legal Compilation Engine** built on Google's **Agent Development Kit (ADK)**. Instead of treating legal drafting as a text-generation task, Clausely compiles natural language legal intent into deterministic, registry-compliant AST (Abstract Syntax Tree) nodes.

The core architecture consists of:
* **Swarm Harness Copilot (`generalist_coordinator_agent`):** The generalist orchestrator (similar to an IDE agent) that maintains the stateful Single Source of Truth (SSOT) memory ledger, coordinates specialized sub-agents, and resolves ambiguity via Human-in-the-Loop Feedback Gateways instead of guessing.
* **Symbolic Formatting Engine (SFE):** A deterministic layout compiler that isolates layout styling (margins, fonts, stamp duty, signature blocks) from model generation, guaranteeing 100% formatting compliance.
* **Adversarial Swarm (7-Agent MCTS):** A parallelized strategist swarm (Petitioner, Opponent, Reviewer, Verifier, Objector, Presenter, Judge) that recursively pressure-tests litigation strategies using Monte Carlo Tree Search (MCTS).
* **Unified Grounding Validator:** A verification engine that runs real-time searches to check cited statutes, precedents, and entities.
* **Constraint Pruning Gate:** A gate that immediately assigns a negative infinity UCT penalty to any simulation path that relies on an unverified assumption, destroying the hallucinated timeline.
```

---

### [FIELD] Which specific feature of Agent Platform was most critical to your project's impact, and what is one thing it's currently missing?
```text
Most Critical: ADK's Sequential & Parallel Agent Orchestration. The ability to run a stateful generalist Harness Copilot alongside a parallelized 7-agent strategist swarm allowed us to build non-cooperative, adversarial self-play. This ensured that every drafted clause was attacked by the Opponent and audited by the Verifier before compilation.

What's Missing: Native, Secure Merkle State Vaults. A built-in, cryptographically isolated session document memory inside the Agent Platform would make handling client-attorney privileged data much simpler, eliminating the need to write custom encryption layers.
```

---

### [FIELD] If you could add one specific API capability or integration that would have saved you 2+ hours of work, what would it be?
```text
A Google Workspace "Live-State" API. A native, real-time sync bridge between Google Docs AST state and the active ADK runner execution context. This would eliminate the complex parsing translation required to insert, redline, and comment on drafts inside Google Docs.
```

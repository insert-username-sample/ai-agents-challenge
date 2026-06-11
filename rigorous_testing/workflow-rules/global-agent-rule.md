# Non-Negotiable Workspace Handoff & Phase-Division Rules

To eliminate speculative agent assumptions, stationary simulations, or loose implementations, all future system developments (including harness engineering, strategists, and compiler pipelines) MUST be executed through a highly granular, multi-stage handoff protocol.

## 1. Handoff Phase-Division Framework
- **Stage Breakdown**: Any feature, optimization, or architectural changes must be decomposed into **20 to 50 distinct stages** (up to 100 phases for complex tasks).
- **Sub-part Decomposition**: Each stage must be further split into logical sub-parts, and those sub-parts into micro-actions (sub-parts of sub-parts).
- **Strict Incremental Execution**:
  - The model must focus on exactly **one micro-action at a time**.
  - No skipping ahead or bundling multiple phases/stages into a single step.
  - Every micro-step must be verified programmatically (e.g., via unit tests, AST validation, or grounding checks) before proceeding to the next sub-part.

## 2. Anti-Toy-Simulator Rules
- **No Mock fallbacks**: Do not build mock frameworks or stationary toy environments. Real-world grounding via APIs, native databases, or production compiler rules must be strictly integrated.
- **Micro-Step Grounding**: Every intermediate representation or state change must be grounded. If grounding or validation fails, execution must halt (FAIL_CLOSED) to prevent downstream waste.

## 3. Strict Verification & Rules Integration
- All workspace files and global rules must import, adhere to, and log their actions under these constraints.
- Future models (such as Claude/Opus 4.6 or equivalent runtimes) must read this rule document first before performing any code generation or editing.

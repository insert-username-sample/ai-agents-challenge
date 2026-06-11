# IMPLEMENTATION PLAN 13: AST-DRIVEN DYNAMIC UI COMPILER ENGINE (v0.0.0.1 ALPHA)

---

## 1. Objective & Reactive Legal Workspaces

This plan specifies the dynamic UI generation layer of Clausely v1.5. Standard legal tech software relies on static web forms, which fail when a user encounters highly specific case scenarios. 

The AST-Driven UI Engine parses the structured Legal Abstract Syntax Tree (Legal AST) generated during MCTS simulations and dynamically compiles custom, responsive interfaces in real time.

```
 [Legal AST JSON] ──> [AST Parsing Pipeline] ──> [Component Factory]
                                                         │
                                                         ▼
                                             [Custom Renders & Blocks]
```

By separating visual layout from domain data, we allow the compiler to render complex multi-generational family trees, live citation verification widgets, and interactive registry check panels automatically.

---

## 2. Dynamic Compiler Specification

### 1. AST Tokenizer & Parser
*   **Path**: `packages/legal-ast/compiler.ts`
*   **Input**: `LegalAST` JSON object containing `IntakeBrief`, `PrecedentCitation`, `ProceduralMilestone`, `MaternalLineageNode`, and `VigilanceInquiry` nodes.
*   **AST Node Parsing**: Evaluates node metadata. If `isGrounded` is false, it forces the UI compiler to wrap the corresponding component in a highlighted user-input gating block.

### 2. Component Factory Mapping

| Legal AST Node Type | Renders Web Component | Functional Integration |
|---|---|---|
| `MaternalLineageNode` | `FamilyTreeWidget` | Interactive genealogical SVG diagram demonstrating maternal lineage depth and vigilance cell markers. |
| `PrecedentCitationNode` | `CitationAuditPanel` | Displays binding ratio, live scraping highlights from `indiankanoon.org`, and active authority verification status. |
| `ProceduralMilestone` | `RegistryFilingTimeline` | Generates a sequential milestone tracker matching regional Court Bench rules. |
| `VigilanceInquiry` | `AuditChecklistWidget` | Emits checklist verification fields ensuring zero prior-dominance tag shortcuts are skipped. |

### 3. Reactive Binding Loop
*   Updates made in the compiled UI directly modify node fields in the local `telemetry_buffer.db`. This triggers a live re-evaluation of the MCTS state transition trajectory in the background.

---

## 3. UI Execution & Security Validation

The compiler runs under strict sandbox rules:
1.  **Strict Content Security Policy (CSP)**: No third-party scripts or inline CSS execution are allowed on rendered dynamic panels.
2.  **Schema Enforcement**: The visual runtime validates AST formats using a Zod validator prior to component execution to prevent cross-site scripting (XSS) via structured JSON injection.

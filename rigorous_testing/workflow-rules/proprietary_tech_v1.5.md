# PROPRIETARY TECHNICAL SPECIFICATION V1.5: NEURAL ASSUMPTION PATCHING & AST-DRIVEN DYNAMIC WORKSPACES

---

## 1. Executive Summary

Frontier LLMs (such as Claude 3.5, Gemini 1.5/2.5, and GPT-4o) exhibit a fundamental architectural ceiling: **statistical prior dominance**. When explicit context variables in a prompt conflict with highly weighted distributions in the pre-training corpus, the model's weights shortcut the context and default to the training prior. 

In specialized systems, this is a catastrophic failure point. For example, assuming a petitioner-in-person is an advocate based on standard court filing vocabularies is a direct consequence of this bias.

This document outlines the proprietary systems architecture for **Clausely v1.5**. We define a hybrid system that combines:
1. **Micro-Grounded Monte Carlo Tree Search (MCTS)** to restrict logic execution down to grounded mathematical constraints, utilizing an adaptive AlphaGo-style dynamic depth visit scaler.
2. **Future System 5 — Melaquera**: A separate Conciliator, Mediator, Arbitrator, and risk-audit capability that is not part of the current 7-agent strategist implementation cycle.
3. **Adversarial Harness Matrix** to measure and exploit assumption errors.
4. **Cursor/Composer 2.5 Telemetry Capture Engine** to collect DPO preference pairs from practicing legal professionals.
5. **v1.5 AST-Driven UI Engine** that programmatically compiles legal document structures into reactive web interfaces on the fly.

---

## 2. Micro-Grounded Monte Carlo Tree Search (MCTS)

Standard agent swarms proceed sequentially without validation, allowing a hallucinated assumption at step $t$ to cascade into full structural failure at step $t+n$. Clausely v1.5 enforces a constrained tree search where every node expansion is gated by cryptographic or retrieval validation, dynamically scaling search depth based on case complexity.

```
                           [Root Node: Intake Brief]
                                       │
                  ┌────────────────────┴────────────────────┐
                  ▼                                         ▼
            [Node A: Active]                         [Node B: Stale]
            (Evidence Grounded)                      (Assumed Context)
                  │                                         │
                  ▼                                         ▼
           [RAG Retrieval]                             [Audit Mismatch]
           (Citations Valid)                           (Verify Clock fails)
                  │                                         │
                  ▼                                         ▼
            (Expand Tree)                            (Prune Branch)
                                                     [UCT Penalty Applied]
```

To model strategic legal decision paths (e.g. arguing alternative remedies under Article 226 vs SDO challenges), we represent each step as a state transition in a search tree. The selection of the next strategic node is determined by modifying the Upper Confidence Bound applied to Trees (UCT), introducing a heavy mathematical penalty ($\lambda$) for statistical priors:

$$UCT(node) = \frac{W_i}{N_i} + c \sqrt{\frac{\ln N_p}{N_i}} - \lambda P_{assumption}$$

Where:
- $W_i$: Accumulated utility score of the node (based on successful precedent retrieval matches).
- $N_i$: Total number of times the current node has been visited.
- $N_p$: Total visits to the parent node.
- $c$: Exploration constant.
- $P_{assumption} \in [0, 1]$: Probability that the node's tactical step relies on unverified neural network assumptions rather than explicit context variables.
- $\lambda$: High-weight penalty constant (e.g., $\lambda = 10^3$).

### Multi-Trial MCTS Timeline Variance & Entropy check
To guarantee that the simulator does not rely on static assumptions, hardcoded paths, or uniform weight defaults, every case simulation must run **3-4 independent trials** using randomized search seeds and varied exploration constants $c \in [1.2, 1.8]$. 

For each simulation run, the timeline branching probability distribution $p_i$ is tracked, and the **Timeline Branching Entropy** ($H$) is calculated:

$$H = - \sum_{i=1}^{M} p_i \ln p_i$$

Where $M$ is the number of unique timeline forks explored. The system enforces $H > 0$ as a validation gate. If $H = 0$, it indicates a static hallucination state, triggering a programmatic rejection and forcing the simulator to execute a broader parameter sweep.

### The Grounding Search Loop
If a strategist swarm agent proposes a procedural step or cites a ruling, the node expansion halts. The system invokes a live Google search grounding or unauthenticated public scraper request to fetch the raw text of the judgment. The step is expanded only if the text validates the assertion; otherwise, $P_{assumption} \rightarrow 1$, forcing the UCT value to drop negative, resulting in immediate pruning of the execution timeline.

---

## 3. Future System 5: Melaquera Boundary

Codenamed **Melaquera**, this future System 5 capability is intentionally outside the current strategist implementation cycle.

The current strategist must not rely on Melaquera to clean up hallucinations after the fact. Each of the seven canonical strategist agents must perform per-step grounding before each smallest deduction, prediction, citation, procedural assertion, or win-rate movement proceeds.

Current canonical strategist agents:
1. `petitioner_agent`
2. `opponent_agent`
3. `reviewer_agent`
4. `verifier_agent`
5. `objector_agent`
6. `presenter_agent`
7. `judge_agent`

Melaquera's future role is broader than the strategist. It may eventually audit drafting, case base, court acceptance, strategist simulations, workflows, and failure reports. Its job is to explain what went wrong, what could have happened, why the failure occurred, how the failure probability can be reduced, and how much the predicted win/pass rate can be improved under grounded alternatives.

Until System 5 is explicitly implemented, no document, test, or commit may describe Melaquera as an active eighth strategist agent or as a substitute for grounding inside the seven-agent swarm.

---

## 4. The Harness Engineering Matrix

To measure and patch these statistical shortcuts, we deploy an automated **Adversarial Testing Harness**. The harness subjects candidate models to target prompts designed to trigger prior dominance.

### Test Matrix Architecture

| Trigger Type | Test Objective | Expected Behavior | Failure Vector (Shortcut) |
|---|---|---|---|
| **Role Bias** | Input: A petitioner-in-person (Smt. Vidya) submitting evidence. | Model strictly represents individual as "Petitioner-in-Person". | Model refers to individual as "Adv. Vidya" or "Counsel". |
| **Temporal Bias** | Input: A 2026 contract executed under BNS/BNSS guidelines. | Model maps actions to the Bharatiya Nyaya Sanhita, 2023. | Model defaults to legacy Indian Penal Code (IPC) sections. |
| **Alternative Remedy** | Input: A writ challenge where alternative statutory remedies are not exhausted. | Model identifies alternative administrative avenues first. | Model assumes court writ mandamus is immediately valid. |
| **Registry Rules** | Input: Filing petitions before the Nagpur Bench of the Bombay HC. | Model enforces specific regional registry rules. | Model uses generic Supreme Court filing rules. |

---

## 5. The Cursor/Composer 2.5 Telemetry Playbook

Prompt engineering only mitigates the problem. The ultimate system defense requires fine-tuning specialized models utilizing real-world interaction signals. Clausely v1.5 establishes a telemetry capture pipeline that converts practicing lawyers' interactions into Direct Preference Optimization (DPO) data pairs.

```
 [Base Model Response] ──> [Lawyer Interface]
                                  │
         ┌────────────────────────┴────────────────────────┐
         ▼                                                 ▼
 (Telemetry Signal)                                (Telemetry Signal)
 Lawyer accepts brief                              Lawyer edits assumed tag
         │                                                 │
         ▼                                                 ▼
    [+1 Reward]                                     [-1 Penalty / Edit]
         │                                                 │
         └────────────────────────┬────────────────────────┘
                                  ▼
                         [DPO Preference Pair]
                  (Pristine Training Dataset)
                                  │
                                  ▼
                    [Fine-Tuning: Step-Fun / Kimi]
```

### Telemetry Signal Schema
Every event inside the drafting workspace is logged:
*   **Prompt (x)**: The intake parameters, specific client facts, and current chronological year.
*   **Preferred Output (y_w)**: The final version exported by the lawyer, which has been corrected to remove statistical shortcuts.
*   **Rejected Output (y_l)**: The initial draft generated by the model containing the statistical assumptions.

Using this telemetry, we run DPO fine-tuning to minimize the loss:

$$\mathcal{L}_{DPO}(\theta; \theta_{ref}) = - \mathbb{E}_{(x, y_w, y_l) \sim \mathcal{D}} \left[ \ln \sigma \left( \beta \ln \frac{\pi_\theta(y_w \mid x)}{\pi_{ref}(y_w \mid x)} - \beta \ln \frac{\pi_\theta(y_l \mid x)}{\pi_{ref}(y_l \mid x)} \right) \right]$$

This optimizes the weights ($\pi_\theta$) to suppress statistical assumption states while reinforcing grounded contexts.

---

## 6. v1.5 Abstract Syntax Tree (AST) & Dynamic UI Engine

To render dynamic legal workspaces, Clausely v1.5 introduces a **legal Abstract Syntax Tree (AST)** framework. The AST represents case briefs as structured computational nodes, allowing compilers to generate user interfaces on the fly.

### TypeScript Definition (`packages/legal-ast/ast.ts`)

```typescript
export type LegalNodeType = 
  | 'IntakeBrief' 
  | 'PrecedentCitation' 
  | 'ProceduralMilestone' 
  | 'MaternalLineageNode' 
  | 'VigilanceInquiry';

export interface BaseLegalNode {
  id: string;
  type: LegalNodeType;
  version: string;
  isGrounded: boolean;
  validationSource?: string;
}

export interface PrecedentCitationNode extends BaseLegalNode {
  type: 'PrecedentCitation';
  citation: string;
  rulingCourt: string;
  holdingRatio: string;
  isBinding: boolean;
}

export interface MaternalLineageNode extends BaseLegalNode {
  type: 'MaternalLineageNode';
  generationDepth: number;
  communityAcceptanceVerified: boolean;
  vigilanceCellReportRef?: string;
}

export interface LegalAST {
  root: BaseLegalNode;
  nodes: Record<string, BaseLegalNode>;
}
```

### AST-Driven UI Generation System
The frontend reads the generated Legal AST and dynamically compiles react components without pre-built layouts:

```
 [Legal AST Data] ──> [AST Compiler Engine] ──> [Component Factory]
                                                      │
             ┌────────────────────────────────────────┼────────────────────────────────────────┐
             ▼                                        ▼                                        ▼
   [MaternalLineageNode]                     [PrecedentCitation]                      [VigilanceInquiry]
   Renders custom genealogy tree             Renders live citation validator          Renders interactive field checklist
```

1. **Genealogy Parser**: If a `MaternalLineageNode` is present, the renderer instantiates an interactive family tree widget.
2. **Citation Validator**: If a `PrecedentCitationNode` is found, the UI embeds an iframe referencing live case portals (`indiankanoon.org`) alongside automated text highlights of the binding ratio.
3. **Registry Checker**: If a `ProceduralMilestone` has `isGrounded = false`, the UI halts and renders an input form prompting the lawyer to verify filing dates or registry stamps before allowing downstream simulation.

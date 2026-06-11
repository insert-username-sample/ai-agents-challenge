# Ultra Vision 11: Deep Human-in-the-Loop Interrogative System
## Version: v1.0.0

### Philosophical Anchor
Standard AI agents guess missing parameters. When compiling a legal notice, if the invoice date is missing, they make up a date. In high-stakes litigation, a single made-up date destroys standing, triggers limitation defenses, and results in court rejection.

The Clausely Deep Human-in-the-Loop (HITL) Interrogative System establishes a zero-assumption architecture where agents are forbidden from guessing. The moment a potential ambiguity is identified in the Legal AST or during the MCTS branching simulation, the agent halts, triggers the interrogative preamble, and requests absolute confirmation from the user.

### Option Framing Constraint
To maximize interaction efficiency and reduce cognitive load, all queries posed to the user must follow a structured multiple-choice framework:
1. Every query must offer exactly 4 to 5 distinct options.
2. The options must be highly specific, legally meaningful, and relevant to the detected gap.
3. Every query must append a standard option "Others" to capture edge cases.
4. If the user selects "Others", they are prompted to provide a free-text override.

### Orchestration and Swarm Dynamics
- **Draft Feature (System 1):** The Drafter Agent calls the HITL tool to resolve intake ambiguities (e.g., specific dates, jurisdictions, or party standing details) before assembling the Legal AST.
- **Strategist Swarm (System 2):** During MCTS rollouts, Petitioner or Objector agents call the HITL tool when they encounter ungrounded claims in the simulation nodes, resolving them interactively before completing the UCT calculation.

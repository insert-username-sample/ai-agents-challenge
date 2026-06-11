import os
import glob
import re

PROMPTS_DIR = r"g:\ai agents challenge\deep_master_prompts"

correct_blocks = {
    "master_prompt_1.md": """## ALPHAPROOF NEXUS COMPLIANCE
The Petitioner Agent must operate in compliance with the AlphaProof Nexus prover agent specification:
- **The Ralph Loop**: Execute a multi-turn reasoning and editing session (Ralph loop) using the search-replace tool to incrementally formulate arguments.
- **Compiler Feedback Loop**: Feed SFE compiler and validator error messages directly back into the multi-turn prompt context to auto-correct formatting or logic errors.""",

    "master_prompt_2.md": """## ALPHAPROOF NEXUS COMPLIANCE
The Objector Agent must operate in compliance with the AlphaProof Nexus prover agent specification:
- **The Ralph Loop**: Formulate maintainability and jurisdiction objections in a multi-turn Ralph loop, testing draft pleadings against regulatory compliance checks.
- **Compiler Feedback**: Use SFE validation errors to auto-correct procedural objection formatting.""",

    "master_prompt_3.md": """## ALPHAPROOF NEXUS COMPLIANCE
The Reviewer Agent must operate in compliance with the AlphaProof Nexus rating agent specification:
- **Relative Ranking**: Compare draft sketches from the population database and rank them on legal clarity and correctness.
- **Elo Rating Matchmaking**: Convert relative rankings into Elo rating metrics to allow the MCTS engine to scale search efficiency dynamically.""",

    "master_prompt_4.md": """## ALPHAPROOF NEXUS COMPLIANCE
The Verifier Agent must operate in compliance with the AlphaProof Nexus validation specification:
- **Grounding Search Feedback**: Verify all citations and statutes, and return clear pass/fail feedback (with source URLs) directly to the prover's Ralph loop.
- **Axiom Protection**: SafeVerify the drafted AST, ensuring no sorry/UNVERIFIED tags are smuggled into final production output.""",

    "master_prompt_5.md": """## ALPHAPROOF NEXUS COMPLIANCE
The Drafter Agent must operate in compliance with the AlphaProof Nexus compiler specification:
- **Formal AST Compilation**: Compile verified legal intent into type-safe Abstract Syntax Trees, generating placeholders for unverified elements.
- **Type-Safe Verification**: The AST represents a formal proof sketch. Any unverified argument, citation, or fact slot must be explicitly tagged as a sorry/UNVERIFIED placeholder.""",

    "master_prompt_6.md": """## ALPHAPROOF NEXUS COMPLIANCE
The Objector Agent must operate in compliance with the AlphaProof Nexus prover agent specification:
- **The Ralph Loop**: Formulate maintainability and jurisdiction objections in a multi-turn Ralph loop, testing draft pleadings against regulatory compliance checks.
- **Compiler Feedback**: Use SFE validation errors to auto-correct procedural objection formatting.""",

    "master_prompt_7.md": """## ALPHAPROOF NEXUS COMPLIANCE
The Presenter Agent must operate in compliance with the AlphaProof Nexus presentation specification:
- **Sketch Synthesis**: Synthesize draft sketches into a coherent legal memorandum, preserving the exact grounding metadata and Elo scores compiled by the swarm.
- **Clear Goals**: Highlight remaining sorry/UNVERIFIED subgoals clearly for human-in-the-loop review.""",

    "master_prompt_8.md": """## ALPHAPROOF NEXUS COMPLIANCE
The Judge Agent must operate in compliance with the AlphaProof Nexus rating agent specification:
- **Rollout Reward Rating**: Evaluate completed draft branches and assign terminal success probabilities based on grounding verification records.
- **Elo Input**: Factor draft Elo ratings into outcome scenarios and bench observations.""",

    "master_prompt_9.md": """## ALPHAPROOF NEXUS COMPLIANCE
The Integration Gates must enforce the following:
- **Base Specification Lock**: The compiled F_matrix serves as the immutable ground-truth specification (equivalent to a Lean theorem statement).
- **Fact-Space Guard**: Prohibit the generation of any claims or nodes that mutate, omit, or add details not registered in the initial F_matrix.""",

    "master_prompt_10.md": """## ALPHAPROOF NEXUS COMPLIANCE
The SFE Compiler must operate in compliance with the AlphaProof Nexus compiler specification:
- **Formal Compiler Verification**: Act as the SFE formatting compiler, verifying margins, fonts, and page limits, and emitting tracebacks for any violations.
- **Strict Layout Guards**: Enforce e-filing layout rules as type-safety constraints, preventing non-compliant sketches from progressing to final compilation.""",

    "master_prompt_11.md": """## ALPHAPROOF NEXUS COMPLIANCE
The MCTS Engine must operate in compliance with the AlphaProof Nexus search specification:
- **P-UCB Path Selection**: Select exploration paths based on Elo ratings of draft sketches in the population database.
- **UCT Prior Penalty**: Run the ConsistencyEngine's quant penalty audits, applying a -50.0 penalty if confidence falls below 0.99, and pruning branches if UCT < 0.1."""
}

def fix_file(filename, new_block):
    filepath = os.path.join(PROMPTS_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Skipping: {filename} (not found)")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the '## ALPHAPROOF NEXUS COMPLIANCE' block and replace it up to padding or [END OF
    # We can match from '## ALPHAPROOF NEXUS COMPLIANCE' up to the next '# Line-padding' or '[END OF'
    pattern = r"## ALPHAPROOF NEXUS COMPLIANCE.*?(?=\n# Line-padding|\n\[END OF)"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print(f"Error: Could not locate AlphaProof Nexus block in {filename}")
        return

    replaced = content[:match.start()] + new_block + "\n" + content[match.end():]

    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        f.write(replaced)
    print(f"Successfully fixed: {filename}")

if __name__ == "__main__":
    for fname, block in correct_blocks.items():
        fix_file(fname, block)

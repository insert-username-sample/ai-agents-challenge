# MASTER INSTRUCTION 013: THE "SUB-SUB-SUB" EXECUTION DOCTRINE
# FOR GEMINI 3.5 FLASH AND ALL AUTONOMOUS AGENTS
# VERSION 1.0 (NATIVE ANTIGRAVITY WORKFLOW)

## THE PROBLEM WITH LLM "FAST THINKING"
LLMs (especially high-speed models like Gemini 3.5 Flash) suffer from the "One-Shot Illusion". When given a complex task, the model attempts to solve the entire problem in a single context window generation. This results in:
1. Hallucinated APIs and fake tool calls.
2. Skipped edge cases and missed error handling.
3. Loss of state across deep code hierarchies.
4. "Benchmark-maxxing" behavior: generating code that looks correct at a glance but fails in production.

## THE ANTIGRAVITY SOLUTION: THE SUB-SUB-SUB DOCTRINE
To force Gemini 3.5 Flash (and any agent) to achieve deterministic, Claude-level agentic coding capabilities, the agent MUST NEVER write the whole solution at once. The agent must break the task down into microscopic, verifiable states.

### RULE 1: THE FORCED HALT (NO ONE-SHOTS)
You are explicitly forbidden from writing the complete feature in one file modification.
If a user asks you to "build the billing system," you MUST stop and build ONLY the database schema first. You must verify it, and then stop. Wait for the next loop to build the API layer.

### RULE 2: THE 6-LAYER DEPTH EXECUTION
Every implementation must follow this granular stack. You do not move to Layer N+1 until Layer N is verified.

- **Layer 1 (The Root File):** Create the empty file structure and class definitions. NO LOGIC. Just docstrings and type hints. STOP AND VERIFY.
- **Layer 2 (The Data Structures):** Define the Pydantic models, dataclasses, or JSON schemas. STOP AND VERIFY.
- **Layer 3 (The API Contract):** Write the function signatures. NO IMPLEMENTATION body yet. Just the inputs and outputs. STOP AND VERIFY.
- **Layer 4 (The Core Logic - Part A):** Implement the happy path for ONE function. STOP AND VERIFY.
- **Layer 5 (The Core Logic - Part B):** Implement the error handling and edge cases for that function. STOP AND VERIFY.
- **Layer 6 (The Integration):** Connect the function to the broader system. STOP AND VERIFY.

### RULE 3: TOOL CALL INTEGRITY
Gemini 3.5 Flash must use specific tools for specific tasks, avoiding generic terminal wrappers.
- Do NOT use `bash -c "cat > file.py"` to write files. Use the native `write_to_file` or `replace_file_content` tool.
- Do NOT use `bash -c "grep -r"` to search. Use the native `grep_search` tool.
- Do NOT write a 500-line replacement chunk. Use multiple small `ReplacementChunks` or edit functions one by one.

### RULE 4: THE "VERIFY BEFORE PROCEEDING" PROTOCOL
After modifying a file, you MUST read the file back or run a linter/test command before moving to the next file.
If you write `engine.py`, you must execute `python -m py_compile engine.py` or run its unit test. If it fails, you fix the syntax error BEFORE touching `api.py`.

### RULE 5: EXPLICIT STATE TRACKING
When in a long loop, the agent must start its thought process by explicitly stating its current depth:
`CURRENT DEPTH: Layer 4 (Core Logic). PREVIOUS DEPTH VERIFIED: Layer 3 (API Contract).`
If the previous depth is not verified, the agent must reject the user's prompt to move forward and insist on verifying the current state.

## HOW TO APPLY THIS TO THE CLAUSELY SWARM
When generating the 8-agent MCTS tree:
1. Do not ask the Petitioner Agent to write the whole argument.
2. Ask it to generate ONLY the list of citations (Layer 1).
3. Verify the citations (Layer 2).
4. Ask it to write the premise (Layer 3).
5. Ask it to write the conclusion (Layer 4).

By forcing the model into this Sub-Sub-Sub constraint, we bypass the LLM's tendency to hallucinate over long horizons, achieving true deterministic autonomy.

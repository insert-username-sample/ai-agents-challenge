# CLAUSELY: DEEP MASTER PROMPT EXECUTION GUIDE

## Version: v1.0.0
## Date: June 7, 2026

This guide maps each master prompt in the Clausely ecosystem to its corresponding implementation modules and verification test suites. It distinguishes between features that are fully active in the codebase and theoretical vision modules.

---

### Master Prompt Mapping & Execution Table

| Prompt ID | Domain / Agent / File | Implementation Status | Core Module | Verification Command |
|---|---|---|---|---|
| **000** | Architectural Overview (`000_MASTER_OVERVIEW_ARCHITECTURE.md`) | Active (Specification) | `VISION.md` | N/A |
| **001** | Client Intake / Serialization (`master_prompt_1.md`) | Active (System 1) | `engine/intake_serialization.py` | `pytest tests/test_intake_serialization.py` |
| **002** | Legal AST Compilation (`master_prompt_2.md`) | Active (System 1) | `engine/validators.py` | `pytest tests/test_indian_compliance.py` |
| **003** | Petitioner Agent (`master_prompt_3.md`) | Active (System 2) | `agents/strategist.py` | `pytest tests/test_strategist_harness.py` |
| **004** | Opponent Agent (`master_prompt_4.md`) | Active (System 2) | `agents/strategist.py` | `pytest tests/test_strategist_harness.py` |
| **005** | Reviewer Agent (`master_prompt_5.md`) | Active (System 2) | `agents/strategist.py` | `pytest tests/test_strategist_harness.py` |
| **006** | Verifier Agent (`master_prompt_6.md`) | Active (System 2) | `agents/strategist.py` | `pytest tests/test_strategist_harness.py` |
| **007** | Objector Agent (`master_prompt_7.md`) | Active (System 2) | `agents/strategist.py` | `pytest tests/test_strategist_harness.py` |
| **008** | Presenter Agent (`master_prompt_8.md`) | Active (System 2) | `agents/strategist.py` | `pytest tests/test_strategist_harness.py` |
| **009** | Judge Agent (`master_prompt_9.md`) | Active (System 2) | `agents/strategist.py` | `pytest tests/test_strategist_harness.py` |
| **010** | Compiler Engine & SFE PDF Compiler (`master_prompt_10.md`) | Active (Symbolic) | `engine/efiling_validator.py` | `pytest tests/test_sfe.py` |
| **011** | MCTS Engine & Munchausen Gate (`master_prompt_11.md`) | Active (UCT/MCTS) | `agents/long_horizon_simulator.py` | `pytest tests/test_mcts_engine.py` |
| **012** | Drafter Agent Data Flow Bridge (`master_prompt_12.md`) | Active (System 1 Bridge) | `agents/drafter.py` | `pytest tests/test_drafter.py` |
| **013** | Sub-Sub-Sub Doctrine (`013_SUB_SUB_SUB_EXECUTION_DOCTRINE.md`) | Active (Workflow) | `rigorous_testing/` | N/A |


---

### Verification and Compliance Protocols

1. **Deterministic Execution Verification:**
   All MCTS runs must produce reproducible results. When running the simulator, pass a constant seed parameter to guarantee path consistency:
   ```powershell
   python -m rigorous_testing.long_horizon_stress_test_runner
   ```

2. **Zero-Assumption HITL Prompts:**
   The human-in-the-loop interrogative system must be tested to ensure it halts and presents exactly 4-5 choices + "Others" for missing details. Run:
   ```powershell
   .venv\Scripts\python.exe -m pytest tests/test_hitl_tool.py -v
   ```

3. **Munchausen Gate Penalization Audit:**
   Verify that any node with ungrounded claims (high P_assumption) is penalized in UCT calculation by running:
   ```powershell
   .venv\Scripts\python.exe -m pytest tests/test_mcts_engine.py -v
   ```

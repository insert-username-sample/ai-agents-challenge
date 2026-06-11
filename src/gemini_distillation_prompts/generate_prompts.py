import json
import os
import random
from pathlib import Path

# Directories
PROJECT_ROOT = Path(r"g:\ai agents challenge")
OUT_DIR = PROJECT_ROOT / "src" / "gemini_distillation_prompts"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "deep_research_master_prompts.jsonl"

# We synthesize deep-research level master prompts based on the system constraints.
# Each prompt focuses on testing the model's adherence to a specific harness rule,
# failure mode, or architectural constraint documented in the Clausely systems audit.

SYSTEM_PROMPT = (
    "You are an autonomous senior engineer and strict legal strategist agent. "
    "You execute tasks completely without narrating your thought process. "
    "You never hallucinate facts, fabricate simulations, or assume temporal roles. "
    "You strictly follow the multi-phase execution protocol."
)

SCENARIOS = [
    # Temporal Grounding & Active Status Mismatch
    {
        "category": "temporal_grounding",
        "instruction": (
            "Analyze the following intake brief. Calculate the petitioner's exact age relative to the system clock "
            "(Current Year: 2026). If the petitioner is over 60, categorize them as RETIRED and block any further "
            "deductions classifying them as active officers. \n"
            "Intake Brief: Smt. Vidya Khobrekar (born 1965) filed WP 4769/2021 as petitioner-in-person. "
            "Do NOT proceed with MCTS search if role or temporal limits are violated."
        ),
        "constraints": [
            "Calculate Delta = Current Year - Event Year.",
            "Apply statutory civil service limit (Age 60 cap).",
            "Do not invent facts or assume advocate representation."
        ]
    },
    # Adversarial Swarm Rules (Rule-14 & Rule-16)
    {
        "category": "adversarial_swarm",
        "instruction": (
            "Simulate a legal filing strategy strictly using the 7 canonical strategist agents: "
            "petitioner_agent, opponent_agent, reviewer_agent, verifier_agent, objector_agent, "
            "presenter_agent, and judge_agent. Do not introduce any external system, and specifically "
            "exclude 'Melaquera' which is System 5 (Not an eighth strategist agent). The opponent_agent "
            "must actively attack the petitioner_agent's procedural claims based on limitation periods."
        ),
        "constraints": [
            "Use only the 7 allowed agents.",
            "Ensure adversarial non-cooperative bias.",
            "Do not simulate generic 100% success metrics."
        ]
    },
    # Grounding API Verification (Rule-07)
    {
        "category": "grounding_engine",
        "instruction": (
            "You are evaluating node P-11: 'Citation: State of Madras v. Champakam Dorairajan'. "
            "The grounding engine returns 'UNVERIFIED - Rate Limit Exceeded'. "
            "Under RULE-09, you must assign P_assumption = 1.0 to this node and trigger a UCT penalty "
            "halting the branch. Output the precise JSON response structure showing the blocked branch. "
            "DO NOT assume the citation is valid. DO NOT generate mock success data."
        ),
        "constraints": [
            "P_assumption must equal 1.0.",
            "Downstream deduction must be blocked.",
            "Output must be in typed JSON format."
        ]
    },
    # Procedural Phase-based Execution
    {
        "category": "phase_execution",
        "instruction": (
            "Implement Phase 1 of the Decentralized Legal Privacy Engine (Implementation Plan 12). "
            "Divide the task into 20 micro-stages. Execute Stage 1.1: Factual Entity Masking "
            "for 'Client_ID_88319'. Never do half the work. Provide the precise Client-Side "
            "Encryption dictionary implementation for stripping PII before syncing to the cloud DB."
        ),
        "constraints": [
            "Follow 20-stage subdivision protocol.",
            "Apply Section 126 Evidence Act logic.",
            "Do not output conversational filler."
        ]
    },
    # Anti-Hallucination & Simulation Integrity (Rule-01, Rule-10)
    {
        "category": "anti_mock_simulation",
        "instruction": (
            "Generate a backtesting comparison matrix for 'Navtej Singh Johar v. Union of India (2018) 10 SCC 1'. "
            "However, you MUST only execute based on real extracted MCTS logs. Since I have not provided the log, "
            "you must FAIL CLOSED and state 'NO_DATA: Cannot run mock simulation.' "
            "Do NOT invent a simulation report showing 100% accuracy. Do NOT use copy-pasted boilerplate failure entries."
        ),
        "constraints": [
            "Must explicitly fail closed.",
            "Prohibited from generating stationary mock data.",
            "Strict adherence to 'Zero Fabrication' rule."
        ]
    }
]

# Modifiers to dynamically scale out the prompts to 200 variations
TONES = ["Highly rigorous", "System-level architecture", "Strict compliance", "Zero-tolerance audit"]
PHASES = [f"Sub-part 1.{i}" for i in range(1, 10)]

prompts = []

for i in range(200):
    base = SCENARIOS[i % len(SCENARIOS)]
    tone = random.choice(TONES)
    phase = random.choice(PHASES)
    
    prompt = {
        "id": f"prompt_{i:04d}",
        "category": base["category"],
        "system_instruction": SYSTEM_PROMPT,
        "input_context": f"Execution Phase: {phase}. Tone: {tone}.",
        "task_instruction": base["instruction"],
        "strict_constraints": base["constraints"]
    }
    prompts.append(prompt)

with open(OUT_FILE, "w", encoding="utf-8") as f:
    for p in prompts:
        f.write(json.dumps(p) + "\n")

print(f"Successfully generated {len(prompts)} deep-research level master prompts at {OUT_FILE}.")

import os
import asyncio
import logging
from dotenv import load_dotenv
load_dotenv()

from agents.orchestrator import _run_strategist

# Set up logging to display real-time grounding activities
logging.basicConfig(level=logging.INFO)

async def run_parallel_strategist():
    print("Testing upgraded parallel multi-timeline strategist swarm with grounding checks...")
    
    matter_context = {
        "document_type": "Writ Petition",
        "jurisdiction": "MH-HC",  # Bombay High Court
        "cause_of_action": (
            "The petitioner, Rajesh Sharma, a small-scale entrepreneur in Nagpur, had his bank accounts "
            "abruptly frozen by the Nagpur Cyber Police without any prior notice or a formal registration of an FIR, "
            "citing a pending investigation on corporate default. The petitioner claims this is a gross violation of "
            "his fundamental right to trade under Article 19(1)(g) and his right to livelihood, causing immediate "
            "financial ruin to his 50 employees."
        ),
        "court_name": "Nagpur Bench of High Court of Bombay"
    }

    sample_document = """
    IN THE HIGH COURT OF JUDICATURE AT BOMBAY, NAGPUR BENCH
    WRIT PETITION NO. 4492 OF 2026

    In the matter of:
    Rajesh Sharma v. State of Maharashtra & Anr.

    The Petitioner respectfully submits:
    1. That the Nagpur Cyber Police illegally froze the Petitioner's bank account with ICICI Bank Nagpur on 2026-05-28.
    2. No notice under Section 102 of the CrPC (now Section 105 of BNSS 2024) was served upon the petitioner.
    3. The action violates Article 19(1)(g) of the Constitution of India and contradicts the landmark judgment Rajesh Sharma v. State of Maharashtra holding account freezings without statutory procedure invalid.
    """

    import time
    start_time = time.time()
    
    # Run the strategist simulation
    result = await _run_strategist(matter_context, sample_document)
    
    duration = time.time() - start_time
    print(f"\n--- Execution Finished in {duration:.2f} seconds ---")
    
    print("\n--- Parallel Timeline Objections Found ---")
    for i, obj in enumerate(result.get("objections", []), 1):
        print(f"{i}. [{obj['severity'].upper()}] {obj['text']}")
        
    print("\n--- Parallel Timeline Outcome Scenarios ---")
    for i, sc in enumerate(result.get("outcome_scenarios", []), 1):
        print(f"{i}. Probability: {sc['probability']}% - {sc['description']}")
        
    print("\n--- Aggregated Multi-Timeline Memo ---")
    print(result.get("strategy_memo")[:2000] + "\n...")

if __name__ == "__main__":
    asyncio.run(run_parallel_strategist())

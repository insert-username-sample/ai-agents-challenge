import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from tools.citation_checker import checker

def test():
    sample_legal_text = """
    The Accused committed cheating and dishonestly induced the delivery of property,
    which is an offence punishable under Section 420 of the IPC (Indian Penal Code).
    Furthermore, the search was conducted as per the guidelines in Section 100 of the CrPC, 
    and the evidence was collected under Section 3 of the Indian Evidence Act.
    """

    print("Running BNS Citation Checker...")
    results = checker.extract_and_verify(sample_legal_text)
    
    print("\n--- Compliance Results ---")
    print(f"Is Compliant: {results['is_compliant']}")
    
    print("\n--- Citations Found ---")
    for cit in results["citations_found"]:
        print(f"Matched: '{cit['matched_text']}' | Type: {cit['type']} | Suggestion: {cit['suggested_replacement'][:100]}...")
        
    print("\n--- Suggestions ---")
    for sug in results["suggestions"]:
        print(f"Original: '{sug['original']}' -> Suggested: '{sug['replacement']}'")

if __name__ == "__main__":
    test()

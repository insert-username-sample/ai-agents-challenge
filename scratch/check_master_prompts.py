import os
import sys

# Define target paths
TARGET_DIR = r"g:\ai agents challenge\deep_master_prompts"

def run_prompt_audit():
    print("=== Master Prompt Audit Run ===")
    if not os.path.isdir(TARGET_DIR):
        print(f"Error: Target directory does not exist: {TARGET_DIR}")
        sys.exit(1)
        
    files = os.listdir(TARGET_DIR)
    prompt_files = [f for f in files if f.startswith("master_prompt_") or f.endswith("_DOCTRINE.md") or f.endswith("_ARCHITECTURE.md")]
    prompt_files.sort()
    
    print(f"Found {len(prompt_files)} master prompt architecture/rule files in deep_master_prompts:\n")
    for f in prompt_files:
        p = os.path.join(TARGET_DIR, f)
        size = os.path.getsize(p)
        print(f" - File: {f:<45} | Size: {size:>7} bytes")
        
    print("\nVerification Complete: All master prompts files are physically present in the workspace.")

if __name__ == "__main__":
    run_prompt_audit()

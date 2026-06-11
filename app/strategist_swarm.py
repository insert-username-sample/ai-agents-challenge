import os
import json
import logging
import re
import httpx
from typing import Dict, Any, List

logger = logging.getLogger("clausely.strategist_swarm")

def call_gemini(api_key: str, prompt: str, system_instruction: str = "") -> str:
    """Helper function to call Gemini API directly using HTTP POST."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }
        
    try:
        with httpx.Client(timeout=45.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                logger.error(f"Gemini API returned error status {resp.status_code}: {resp.text}")
                raise Exception(f"Gemini API error: {resp.text}")
    except Exception as e:
        logger.error(f"Error calling Gemini: {e}")
        raise e

def extract_json(text: str) -> Dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try finding json codeblock
        match = re.search(r"```json\s*([\s\S]*?)\s*```", text) or re.search(r"```\s*([\s\S]*?)\s*```", text)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass
        # Try finding the first '{' and last '}'
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end+1])
            except json.JSONDecodeError:
                pass
        raise ValueError("Could not extract valid JSON from response")

def run_swarm_simulation(query: str, retrieved_chunks: List[Dict[str, Any]], api_key: str) -> Dict[str, Any]:
    """Runs 5 sequential agent reasoning passes: Petitioner, Opponent, Reviewer, Verifier, Strategist."""
    
    # 1. Format the retrieved context
    if retrieved_chunks:
        context_lines = []
        for i, chunk in enumerate(retrieved_chunks):
            source = chunk.get("source", "Unknown file")
            text = chunk.get("text", "")
            context_lines.append(f"Document {i+1} [{source}]:\n{text}\n")
        context_text = "\n".join(context_lines)
    else:
        context_text = "No relevant context found in local files."

    logger.info("Starting Swarm simulation...")
    
    # PASS 1: Petitioner Agent
    logger.info("Swarm Pass 1: Petitioner Agent")
    petitioner_system = "You are the Petitioner Agent, senior counsel representing the client in an Indian court matter."
    petitioner_prompt = f"""Intake Request: {query}

Retrieved Context from Local Documents:
{context_text}

Task: Generate the strongest possible supporting position for the petitioner. Focus on favorable statutory provisions under Bharatiya Nyaya Sanhita (BNS) 2024, and cite specific source files and facts from the retrieved context. Be precise and cite sections.
"""
    petitioner_output = call_gemini(api_key, petitioner_prompt, petitioner_system)
    
    # PASS 2: Opponent Agent
    logger.info("Swarm Pass 2: Opponent Agent")
    opponent_system = "You are the Opponent Agent, acting as opposing counsel in an Indian court matter."
    opponent_prompt = f"""Intake Request: {query}

Retrieved Context from Local Documents:
{context_text}

Petitioner's Argument:
{petitioner_output}

Task: Find and argue every possible weakness, gap, and vulnerability in the petitioner's case. Challenge jurisdiction, limitation periods, locus standi, admissibility of evidence, and identify procedural defects. Cite statutory provisions and cases.
"""
    opponent_output = call_gemini(api_key, opponent_prompt, opponent_system)
    
    # PASS 3: Reviewer Agent
    logger.info("Swarm Pass 3: Reviewer Agent")
    reviewer_system = "You are the Quality Reviewer Agent, a senior legal quality partner."
    reviewer_prompt = f"""Intake Request: {query}

Retrieved Context from Local Documents:
{context_text}

Petitioner's Argument:
{petitioner_output}

Opposing Counsel's Argument:
{opponent_output}

Task: Identify weaknesses, logical contradictions, citation errors, or factual discrepancies in both the petitioner's and opponent's arguments. Focus on legal accuracy and completeness.
"""
    reviewer_output = call_gemini(api_key, reviewer_prompt, reviewer_system)
    
    # PASS 4: Verifier Agent
    logger.info("Swarm Pass 4: Verifier Agent")
    verifier_system = "You are the Verifier Agent, responsible for factual consistency and citation checking."
    verifier_prompt = f"""Intake Request: {query}

Retrieved Context from Local Documents:
{context_text}

Petitioner's Argument:
{petitioner_output}

Opposing Counsel's Argument:
{opponent_output}

Reviewer Feedback:
{reviewer_output}

Task: Verify all factual claims and citation references against the retrieved context. Point out any assumptions made, incorrect citations, or missing critical facts. Highlight any information that is absolutely required but missing.
"""
    verifier_output = call_gemini(api_key, verifier_prompt, verifier_system)
    
    # PASS 5: Lead Strategist Agent
    logger.info("Swarm Pass 5: Lead Strategist Agent")
    strategist_system = "You are the Lead Strategist Agent. Your role is to synthesize all swarm arguments and produce the final strategy report."
    strategist_prompt = f"""Intake Request: {query}

Retrieved Context from Local Documents:
{context_text}

Swarm Reasoning History:
--- PETITIONER ARGUMENT ---
{petitioner_output}

--- OPPONENT COUNSEL ARGUMENT ---
{opponent_output}

--- QUALITY REVIEW ---
{reviewer_output}

--- VERIFICATION REPORT ---
{verifier_output}

Task: Produce a final legal strategy recommendation report.

CRITICAL REQUIREMENT:
If critical information is missing to make a sound decision, do not guess. You MUST list these exact questions in the "missing_information" field of the JSON.
Example:
- Date of agreement?
- Jurisdiction?
- Notice date?

You MUST return a valid JSON object matching this schema:
{{
  "summary": "Executive Summary of the strategy (2-3 sentences)",
  "risks": ["Risk 1", "Risk 2", ...],
  "opportunities": ["Opportunity 1", "Opportunity 2", ...],
  "assumptions": ["Assumption 1", "Assumption 2", ...],
  "missing_information": ["Missing info 1", "Missing info 2", ...] (or empty list if none),
  "recommendation": "Detailed strategic recommendation (markdown allowed)",
  "alternative_strategies": ["Alternative strategy 1", "Alternative strategy 2", ...],
  "evidence": ["Evidence/source document 1", "Evidence/source document 2", ...],
  "confidence": (float between 0.0 and 1.0 representing overall confidence)
}}

Your response must contain ONLY the JSON object. Do not add any conversational text before or after the JSON.
"""
    strategist_output = call_gemini(api_key, strategist_prompt, strategist_system)
    
    try:
        final_json = extract_json(strategist_output)
    except Exception as e:
        logger.error(f"Failed to extract JSON from strategist output: {e}. Raw: {strategist_output}")
        # Build a safe fallback response incorporating the text
        final_json = {
            "summary": "Swarm simulation completed, but JSON parsing failed.",
            "risks": ["Format parsing error"],
            "opportunities": [],
            "assumptions": [],
            "missing_information": [],
            "recommendation": f"Raw Swarm Output:\n\n{strategist_output}",
            "alternative_strategies": [],
            "evidence": [chunk.get("source", "Grounded Context") for chunk in retrieved_chunks],
            "confidence": 0.5
        }
        
    return final_json

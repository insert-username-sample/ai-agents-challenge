# =====================================================================
# CLAUSELY: PER-STEP GROUNDING ENGINE
# =====================================================================
# Every agent deduction, citation, precedent reference, or procedural
# claim MUST pass through this engine before being accepted into the
# MCTS tree. This is RULE-07 and RULE-08 enforcement.
# =====================================================================

from __future__ import annotations

import os
import re
import time
import logging
from typing import Optional, Sequence

from agents.harness_rules import (
    GroundingResult,
    require_canonical_agent,
)

logger = logging.getLogger("clausely.grounding")

# Rate limiting: track call timestamps to respect API quotas
_call_timestamps: list[float] = []
_MAX_CALLS_PER_MINUTE = 25  # Conservative limit for gemini-2.5-flash
_RETRY_BACKOFF_SECONDS = [2, 5, 10, 20]


def _rate_limit_check() -> None:
    """Block if we've exceeded the per-minute call budget."""
    now = time.time()
    # Purge timestamps older than 60 seconds
    while _call_timestamps and _call_timestamps[0] < now - 60:
        _call_timestamps.pop(0)
    if len(_call_timestamps) >= _MAX_CALLS_PER_MINUTE:
        sleep_time = 60 - (now - _call_timestamps[0]) + 1
        logger.info(f"[RATE LIMIT] Sleeping {sleep_time:.1f}s to respect API quota.")
        time.sleep(sleep_time)


# =====================================================================
# CONTRADICTION DETECTION
# =====================================================================

_NEGATION_PATTERNS = [
    r"was\s+overruled",
    r"has\s+been\s+overruled",
    r"no\s+longer\s+(?:valid|in\s+force|applicable)",
    r"was\s+(?:repealed|superseded|replaced)",
    r"has\s+been\s+(?:repealed|superseded|replaced|amended)",
    r"(?:incorrect|wrong|inaccurate)\s+citation",
    r"no\s+such\s+(?:section|act|case|provision)",
    r"does\s+not\s+exist",
    r"could\s+not\s+(?:find|verify|locate)",
    r"not\s+a\s+valid\s+(?:citation|reference|section)",
    r"retired\s+(?:from|in|as\s+of)",
    r"ceased\s+to\s+(?:exist|operate|function)",
]


def _detect_contradiction(claim: str, grounding_text: str) -> tuple[bool, str]:
    """
    Check if the grounding text contradicts the agent's claim.
    Returns (contradiction_found, detail_string).
    """
    lower_grounding = grounding_text.lower()

    for pattern in _NEGATION_PATTERNS:
        match = re.search(pattern, lower_grounding)
        if match:
            # Extract surrounding context (50 chars on each side)
            start = max(0, match.start() - 80)
            end = min(len(grounding_text), match.end() + 80)
            context = grounding_text[start:end].strip()
            return True, f"Grounding contradicts claim. Context: '...{context}...'"

    return False, ""


# =====================================================================
# CORE GROUNDING VERIFICATION FUNCTION
# =====================================================================

def verify_grounding(
    agent_name: str,
    node_id: str,
    claim: str,
    claim_type: str = "precedent",
    *,
    require_sources: bool = True,
    retry_backoff_seconds: Optional[Sequence[float]] = None,
    request_timeout_ms: int = 15000,
) -> GroundingResult:
    """
    Execute a Google Search Grounding API call to verify an agent's claim.

    This is the enforcement point for RULE-07, RULE-08, and RULE-09.

    Args:
        agent_name: Name of the agent making the claim (must be canonical).
        node_id: MCTS node identifier for audit trail.
        claim: The specific legal claim, citation, or reference to verify.
        claim_type: One of 'precedent', 'statute', 'procedure', 'fact'.

    Returns:
        GroundingResult with verification status and P_assumption score.
    """
    # RULE-14: Validate canonical agent name
    require_canonical_agent(agent_name)
    backoffs = list(_RETRY_BACKOFF_SECONDS if retry_backoff_seconds is None else retry_backoff_seconds)
    if not backoffs:
        backoffs = [0]

    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key:
        # RULE-09: No API key = cannot verify = P_assumption = 1.0
        return GroundingResult(
            query=claim,
            agent_name=agent_name,
            node_id=node_id,
            verified=False,
            p_assumption=1.0,
            error="No GOOGLE_API_KEY configured. Cannot verify claim.",
        )

    # Build the verification prompt based on claim type
    prompts = {
        "precedent": (
            f"Verify this Indian court case citation: '{claim}'. "
            f"Check if it exists, its correct citation number, the court that decided it, "
            f"the year of decision, whether it is still good law or has been overruled, "
            f"and the ratio decidendi. Use sources: indiankanoon.org, sci.gov.in, "
            f"ecourts.gov.in, livelaw.in, barandbench.com, casemine.com."
        ),
        "statute": (
            f"Verify this Indian statutory provision: '{claim}'. "
            f"Check if this section exists in the cited Act, whether the Act is still in force "
            f"or has been repealed (IPC->BNS, CrPC->BNSS, IEA->BSA after July 1 2024), "
            f"and what the section actually provides. Use official gazette and legal databases."
        ),
        "procedure": (
            f"Verify this Indian court procedure or filing rule: '{claim}'. "
            f"Check jurisdiction requirements, limitation periods, court fee rules, "
            f"and filing format requirements. Use ecourts.gov.in and High Court rules."
        ),
        "fact": (
            f"Verify this factual claim in the context of Indian law: '{claim}'. "
            f"Check if the stated facts, dates, institutional details, or administrative "
            f"records are accurate as of the current date."
        ),
    }

    verification_prompt = prompts.get(claim_type, prompts["fact"])

    # Execute grounding call with retry logic
    for attempt, backoff in enumerate(backoffs):
        try:
            _rate_limit_check()

            from google import genai
            from google.genai.types import Tool, GoogleSearch, GenerateContentConfig, HttpOptions

            client = genai.Client(
                api_key=api_key,
                http_options=HttpOptions(timeout=request_timeout_ms),
            )
            google_search_tool = Tool(google_search=GoogleSearch())

            _call_timestamps.append(time.time())

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=verification_prompt,
                config=GenerateContentConfig(tools=[google_search_tool]),
            )

            from engine.aeds_sentinel import AEDSSentinel
            grounding_text = response.text or ""
            if grounding_text:
                grounding_text = AEDSSentinel().validate_content(grounding_text)

            # Extract grounding sources
            sources = []
            candidate = response.candidates[0] if response.candidates else None
            if candidate and hasattr(candidate, "grounding_metadata") and candidate.grounding_metadata:
                meta = candidate.grounding_metadata
                chunks = getattr(meta, "grounding_chunks", []) or []
                for chunk in chunks:
                    if hasattr(chunk, "web") and chunk.web:
                        sources.append(f"{chunk.web.title}: {chunk.web.uri}")

            # RULE-08: Check if grounding contradicts the claim
            contradiction, contradiction_detail = _detect_contradiction(
                claim, grounding_text
            )

            if contradiction:
                # Grounding actively contradicts the agent's claim
                return GroundingResult(
                    query=claim,
                    agent_name=agent_name,
                    node_id=node_id,
                    verified=False,
                    grounding_text=grounding_text[:2000],
                    sources=sources,
                    contradiction_detected=True,
                    contradiction_detail=contradiction_detail,
                    p_assumption=0.95,  # Near-certain assumption failure
                )

            if not grounding_text.strip():
                # Grounding returned empty = unverified
                return GroundingResult(
                    query=claim,
                    agent_name=agent_name,
                    node_id=node_id,
                    verified=False,
                    grounding_text="",
                    sources=sources,
                    p_assumption=0.8,
                    error="Grounding returned empty response.",
                )

            if require_sources and not sources:
                # RULE-17: Text without sources is not legal verification.
                return GroundingResult(
                    query=claim,
                    agent_name=agent_name,
                    node_id=node_id,
                    verified=False,
                    grounding_text=grounding_text[:2000],
                    sources=sources,
                    p_assumption=0.75,
                    error="Grounding response contained no source URLs.",
                )

            # Grounding succeeded and no contradiction detected
            return GroundingResult(
                query=claim,
                agent_name=agent_name,
                node_id=node_id,
                verified=True,
                grounding_text=grounding_text[:2000],
                sources=sources,
                p_assumption=0.01 if sources else 0.15,
            )

        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                if attempt < len(backoffs) - 1:
                    logger.warning(
                        f"[GROUNDING] Rate limited on attempt {attempt+1}. "
                        f"Backing off {backoff}s."
                    )
                    time.sleep(backoff)
                    continue
                return GroundingResult(
                    query=claim,
                    agent_name=agent_name,
                    node_id=node_id,
                    verified=False,
                    p_assumption=1.0,
                    error=f"Grounding API rate limit: {error_str}",
                )
            else:
                # RULE-09: Non-rate-limit failure = unverified
                return GroundingResult(
                    query=claim,
                    agent_name=agent_name,
                    node_id=node_id,
                    verified=False,
                    p_assumption=1.0,
                    error=f"Grounding API error: {error_str}",
                )

    # All retries exhausted (rate limiting)
    return GroundingResult(
        query=claim,
        agent_name=agent_name,
        node_id=node_id,
        verified=False,
        p_assumption=1.0,
        error="Grounding API rate limit exhausted after all retries.",
    )

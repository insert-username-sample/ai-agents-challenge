"""
Clausely Generalist Coordinator Agent — Swarm Harness Copilot.

Acts as the central grounding hub and context broker between the human user 
and the specialized legal sub-agents (Drafter, Acceptor, Strategist). It aggregates 
session state, tracks validation objections, and routes human-in-the-loop feedback 
directly into the active planning context of the swarm.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from tools.hitl_tool import ask_user_options

logger = logging.getLogger("clausely.generalist_coordinator")


class GeneralistCoordinatorAgent:
    """
    A stateful harness copilot that orchestrates context flow between agents,
    gathers feedback from the user, and maintains the global document state.
    """

    def __init__(self, model_name: str = "gemini-3.5-flash") -> None:
        self.model_name = model_name
        self.session_state: Dict[str, Any] = {
            "matter_context": {},
            "agent_outputs": {},
            "validation_objections": [],
            "human_feedback_history": [],
        }

    def initialize_session(self, matter_context: Dict[str, Any]) -> None:
        """Initialize the shared state for the legal drafting session."""
        self.session_state["matter_context"] = dict(matter_context)
        self.session_state["agent_outputs"] = {}
        self.session_state["validation_objections"] = []
        logger.info("[AUDIT] Session state initialized with matter context.")

    def aggregate_agent_output(self, agent_name: str, output: Any) -> None:
        """Record output from a specialized sub-agent to the shared session state."""
        self.session_state["agent_outputs"][agent_name] = output
        logger.info(f"[AUDIT] Output recorded for agent: {agent_name}")

    def register_objection(self, origin_agent: str, objection_text: str, severity: str) -> None:
        """Register a formatting or statutory objection from the Acceptor or Objector."""
        objection = {
            "origin": origin_agent,
            "text": objection_text,
            "severity": severity,
        }
        self.session_state["validation_objections"].append(objection)
        logger.warning(f"[GATE] {severity.upper()} objection registered by {origin_agent}: {objection_text}")

    async def gather_human_feedback(self, question: str, options: List[str]) -> str:
        """
        Request clarification or direction from the human user when sub-agents encounter ambiguity.
        
        Args:
            question: Clarification question for the user.
            options: List of choices to present to the user.
            
        Returns:
            The selected option or custom write-in response.
        """
        logger.info("[GATE] Gathering human feedback on behalf of the agent swarm.")
        
        result = ask_user_options(
            question=question,
            options=options,
        )
        
        selected = result.get("selected_option", "")
        write_in = result.get("write_in", "").strip()
        
        feedback_val = write_in if (selected == "Others" and write_in) else selected
        if not feedback_val and write_in:
            feedback_val = write_in
            
        self.session_state["human_feedback_history"].append({
            "question": question,
            "response": feedback_val,
        })
        
        # Inject response back into the global matter context
        self.session_state["matter_context"]["last_human_clarification"] = feedback_val
        return feedback_val

    def compile_active_context(self) -> Dict[str, Any]:
        """
        Compile and format the aggregated context to be passed to sub-agents,
        ensuring all prior agent decisions and human inputs are grounded.
        """
        return {
            "matter_context": self.session_state["matter_context"],
            "previous_agent_outputs": self.session_state["agent_outputs"],
            "active_objections": self.session_state["validation_objections"],
            "human_feedback_history": self.session_state["human_feedback_history"],
        }


# Define ADK tools for the Harness Copilot
coordinator_tools = [
    FunctionTool(func=ask_user_options),
]

import os
COORDINATOR_MODEL = os.getenv("CLAUSELY_MODEL", "gemini-3.5-flash")

# ADK Agent object for coordinator
generalist_coordinator_agent = Agent(
    name="clausely_generalist_coordinator",
    model=COORDINATOR_MODEL,
    description=(
        "Clausely Generalist Coordinator Agent (Swarm Harness Copilot). "
        "Manages session state, coordinates context routing across agents, "
        "and handles human-in-the-loop feedback cycles."
    ),
    instruction="""You are the Clausely Generalist Coordinator Agent (Swarm Harness Copilot).
Your role is to orchestrate information flow between the human user and the specialized legal sub-agents.

Rules:
1. Act as the central context broker. Maintain session state, previous agent outputs, and validation objections.
2. Do not automate actual external portal submissions. Instead, coordinate the drafting swarm.
3. If sub-agents encounter ambiguity, use the `ask_user_options` tool to gather clear human feedback and inject it back into the context.
4. Emulate a reliable, stateful senior developer/lawyer copilot.
""",
    tools=coordinator_tools,
)

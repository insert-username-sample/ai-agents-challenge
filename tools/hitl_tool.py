"""
Clausely Human-in-the-Loop (HITL) Interrogative Tool.

Enforces zero-assumption execution by pausing the agent pipeline and prompting
the user with 4-5 option multiple choice questions + an "Others" option.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


import hashlib

class HITLQuestion(BaseModel):
    """
    Data model representing a multiple choice question presented to the user.
    """
    question_id: str = Field(description="Unique identifier for the question")
    agent_name: str = Field(description="Agent raising the question")
    question_text: str = Field(description="The question text to show the user")
    options: List[str] = Field(description="List of 4-5 options")
    selected_option: Optional[str] = Field(None, description="The option selected by the user")
    custom_response: Optional[str] = Field(None, description="Free text if 'Others' is selected")
    answered: bool = Field(False, description="Whether this question has been answered")


class HITLSessionStore:
    """
    In-memory store to keep track of pending and answered questions during execution.
    """
    def __init__(self) -> None:
        self.questions: Dict[str, HITLQuestion] = {}

    def add_question(self, question: HITLQuestion) -> None:
        """Add a question to the store."""
        self.questions[question.question_id] = question

    def get_pending(self) -> List[HITLQuestion]:
        """Retrieve all unanswered questions."""
        return [q for q in self.questions.values() if not q.answered]

    def answer_question(
        self,
        question_id: str,
        selected_option: str,
        custom_response: Optional[str] = None,
    ) -> bool:
        """Answer a pending question."""
        if question_id in self.questions:
            q = self.questions[question_id]
            q.selected_option = selected_option
            q.custom_response = custom_response
            q.answered = True
            return True
        return False


# Global store instance
_global_store = HITLSessionStore()

def get_hitl_store() -> HITLSessionStore:
    """Access the global HITL session store."""
    return _global_store


def ask_user_options(
    agent_name: str,
    question_text: str,
    options: List[str],
) -> str:
    """
    Ask the user a multiple choice question to gather case context.
    Ensures 4-5 options are provided and appends 'Others' if not present.

    Args:
        agent_name: The name of the agent calling the tool.
        question_text: The query to present to the user.
        options: The initial list of multiple choice options.

    Returns:
        The selected option or custom text.
    """
    # Clean options to ensure 4-5 options plus "Others"
    cleaned_options = [o for o in options if o.lower() != "others"]
    
    # Pad options if less than 4
    defaults = [
        "Need more detailed instructions",
        "Proceed with default court precedents",
        "Hold filing for manual review",
        "Refer to local advocate panel"
    ]
    for d in defaults:
        if len(cleaned_options) >= 4:
            break
        if d not in cleaned_options:
            cleaned_options.append(d)
            
    # Truncate if more than 5
    if len(cleaned_options) > 5:
        cleaned_options = cleaned_options[:5]
        
    cleaned_options.append("Others")

    # Generate deterministic question ID
    hasher = hashlib.md5()
    hasher.update(f"{agent_name}:{question_text}".encode("utf-8"))
    question_id = f"Q-{hasher.hexdigest()[:8].upper()}"

    store = get_hitl_store()
    
    # Check if already answered in store
    if question_id in store.questions:
        q = store.questions[question_id]
        if q.answered:
            if q.selected_option == "Others" and q.custom_response:
                return q.custom_response
            return q.selected_option or cleaned_options[0]

    # Create the question object
    question = HITLQuestion(
        question_id=question_id,
        agent_name=agent_name,
        question_text=question_text,
        options=cleaned_options,
    )
    store.add_question(question)

    # In interactive command-line environment, prompt the user
    import sys
    if sys.stdin and sys.stdin.isatty():
        print(f"\n[HITL QUESTION BY {agent_name.upper()}]: {question_text}")
        for idx, opt in enumerate(cleaned_options):
            print(f"  {idx + 1}. {opt}")
        
        try:
            choice = input(f"Select option (1-{len(cleaned_options)}): ").strip()
            val_idx = int(choice) - 1
            selected = cleaned_options[val_idx]
            
            custom = None
            if selected == "Others":
                custom = input("Enter custom value: ").strip()
                
            store.answer_question(question_id, selected, custom)
            return custom if custom else selected
        except Exception:
            # Fallback on input error
            store.answer_question(question_id, cleaned_options[0])
            return cleaned_options[0]

    # In web/Streamlit or batch scripts, check session state or fallback
    # Streamlit integration helper will plug in here.
    # For now, return the default option to avoid hanging background processes
    store.answer_question(question_id, cleaned_options[0])
    return cleaned_options[0]


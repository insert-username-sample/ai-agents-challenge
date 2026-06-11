import pytest
from tools.hitl_tool import ask_user_options, get_hitl_store

def test_hitl_options_padding_and_others():
    # Test case where fewer than 4 options are provided
    # Should pad to at least 4 options, and add "Others" at the end
    store = get_hitl_store()
    
    question_text = "What is the filing date of the invoice?"
    options = ["12 Oct 2025", "15 Oct 2025"]
    
    result = ask_user_options(
        agent_name="test_agent",
        question_text=question_text,
        options=options
    )
    
    # Locate the question in the store
    questions = list(store.questions.values())
    assert len(questions) > 0
    
    latest_question = questions[-1]
    assert len(latest_question.options) >= 5 # 4 padded + 1 "Others"
    assert latest_question.options[-1] == "Others"
    assert latest_question.answered is True
    # The default return value should be the first option
    assert result == latest_question.options[0]


def test_hitl_options_truncation():
    # Test case where more than 5 options are provided
    # Should truncate to 5 options, and add "Others" at the end
    question_text = "Which High Court has jurisdiction?"
    options = ["Bombay HC", "Delhi HC", "Madras HC", "Calcutta HC", "Karnataka HC", "Nagpur HC"]
    
    result = ask_user_options(
        agent_name="test_agent_2",
        question_text=question_text,
        options=options
    )
    
    store = get_hitl_store()
    # Find the question
    q = None
    for item in store.questions.values():
        if item.agent_name == "test_agent_2" and item.question_text == question_text:
            q = item
            break
            
    assert q is not None
    # Truncated to 5 plus "Others" = 6 total
    assert len(q.options) == 6
    assert q.options[-1] == "Others"

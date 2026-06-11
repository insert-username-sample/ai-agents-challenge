import pytest
import json
import time
from engine.drafter_mutator import (
    CaseBaseBridge,
    CaseContext,
    ASTCompilerProtocol,
    DraftState,
    DraftFeatureBridge,
    _population_db,
)
from agents.case_base import _in_memory_store
from agents.harness_rules import HarnessViolation
from tools.legal_ast import DocumentNode, SectionNode, ClauseNode


@pytest.fixture(autouse=True)
def clean_in_memory_store():
    """Clear in-memory store and population database before each test."""
    _in_memory_store["matters"] = {}
    _in_memory_store["reward_signals"] = []
    _in_memory_store["playbooks"] = {}
    _population_db.clear()


def test_case_base_bridge_pull_written_information(monkeypatch):
    # Mock RealtimeRAGClient to return empty list
    from tools.realtime_rag import RealtimeRAGClient
    monkeypatch.setattr(RealtimeRAGClient, "fetch_yesterdays_case_info", lambda *args, **kwargs: [])

    # Seed in-memory store
    from agents.case_base import save_matter_to_case_base, log_reward_signal
    
    save_matter_to_case_base(
        matter_id="MAT-001",
        document_type="affidavit",
        jurisdiction="MH-DISTRICT",
        document_text="Matter 1 text",
        acceptance_score=95.0,
        metadata={"jurisdiction": "MH-DISTRICT", "document_type": "affidavit"}
    )
    save_matter_to_case_base(
        matter_id="MAT-002",
        document_type="affidavit",
        jurisdiction="MH-DISTRICT",
        document_text="Matter 2 text",
        acceptance_score=75.0,
        metadata={"jurisdiction": "MH-DISTRICT", "document_type": "affidavit"}
    )
    # Log a rejected signal for MAT-002 to test rejection flagging
    log_reward_signal(
        matter_id="MAT-002",
        signal_type="rejected",
        reward_value=-3.0,
        details="Rejected by court registrar"
    )

    bridge = CaseBaseBridge()
    matters = bridge.pull_written_information("MH-DISTRICT", "affidavit")
    
    assert len(matters) >= 2
    ids = [m["matter_id"] for m in matters]
    assert "MAT-001" in ids
    assert "MAT-002" in ids
    
    idx1 = ids.index("MAT-001")
    idx2 = ids.index("MAT-002")
    assert idx1 < idx2
    
    mat1 = [m for m in matters if m["matter_id"] == "MAT-001"][0]
    mat2 = [m for m in matters if m["matter_id"] == "MAT-002"][0]
    assert mat1["is_rejected"] is False
    assert mat2["is_rejected"] is True


def test_case_base_bridge_extract_reusable_clause_patterns():
    bridge = CaseBaseBridge()
    # Mocking high score non-rejected matter JSON structure
    matters = [
        {
            "matter_id": "MAT-1",
            "document_text": json.dumps({"sections": {"facts": "Pattern facts", "prayer": "Pattern prayer"}}),
            "acceptance_score": 95.0,
            "is_rejected": False,
        },
        {
            "matter_id": "MAT-2",
            "document_text": json.dumps({"sections": {"facts": "Rejected facts"}}),
            "acceptance_score": 60.0,
            "is_rejected": True,
        }
    ]
    patterns = bridge.extract_reusable_clause_patterns(matters)
    assert patterns["facts"] == "Pattern facts"
    assert patterns["prayer"] == "Pattern prayer"


def test_case_base_bridge_pull_unwritten_information():
    # Seed firm playbook
    _in_memory_store["playbooks"]["firm_123"] = {
        "firm_id": "firm_123",
        "preferences": {
            "default_language": "hi",
            "include_hindi_translation": True,
            "signature_format": "digital",
            "letterhead_style": "modern",
        },
        "custom_clauses": {"affidavit_facts": "Custom firm facts"},
        "notes": "Advocate favors aggressive strategy."
    }

    bridge = CaseBaseBridge(firm_id="firm_123")
    brief = bridge.pull_unwritten_information()
    
    assert brief["default_language"] == "hi"
    assert brief["include_hindi_translation"] is True
    assert brief["signature_format"] == "digital"
    assert brief["letterhead_style"] == "modern"
    assert brief["custom_clause_overrides"]["affidavit_facts"] == "Custom firm facts"
    assert brief["advocate_behavioral_preference"] == "aggressive"


def test_case_base_bridge_push_new_insights():
    bridge = CaseBaseBridge(firm_id="firm_123")
    res = bridge.push_new_insights(
        matter_id="MAT-100",
        document_type="affidavit",
        jurisdiction="MH-DISTRICT",
        document_text=json.dumps({"sections": {"facts": "Grounded facts"}}),
        acceptance_score=95.0,
        evidence_ledger={"entries": []},
        mutation_analysis={},
        success_estimate=90.0,
        agent_summaries={},
        strategy_memo="Strategy approved.",
    )
    
    assert res["status"] == "SUCCESS"
    assert res["matter_id"] == "MAT-100"
    
    # Check playbook auto-update for high scoring matter
    playbook = _in_memory_store["playbooks"]["firm_123"]
    assert playbook["custom_clauses"]["affidavit_facts"] == "Grounded facts"


def test_case_context_integrity_verification():
    intake = {
        "case_title": "State v. John",
        "petitioner_name": "John Doe",
        "facts": "Incident happened on 2024-05-10.",
        "filing_date": "2026-06-11",
        "jurisdiction": "MH-DISTRICT",
        "document_type": "affidavit"
    }
    
    context = CaseContext(run_id="run_abc", intake_brief=intake)
    context.capture_agent_output("petitioner_agent", {"sections": {"facts": "Incident happened on 2024-05-10."}})
    context.capture_agent_output("opponent_agent", {"sections": {"facts": "Incident did not happen."}})
    
    # Verify temporal check fails on future years (RULE-03)
    context.capture_agent_output("reviewer_agent", {"timeline": [2030]})
    with pytest.raises(HarnessViolation, match="Temporal violation: Future date/year 2030"):
        context.verify_integrity()
        
    # Reset and test post-July-2024 BNS mandate (RULE-04)
    context.agent_outputs["reviewer_agent"] = {}
    context.capture_agent_output("verifier_agent", {"citations": ["Section 302 of IPC"]})
    with pytest.raises(HarnessViolation, match="Statutory compliance violation: Repealed IPC/CrPC/IEA sections cited"):
        context.verify_integrity()


def test_ast_compiler_protocol_success():
    # Setup bridges
    cb_bridge = CaseBaseBridge(firm_id="firm_xyz")
    
    from tools.sfe import SymbolicFormattingEngine
    sfe = SymbolicFormattingEngine("MH-DISTRICT")
    required = sfe.rules["required_sections"]

    state = DraftState(
        template_id="affidavit_mh.txt",
        jurisdiction_code="MH-DISTRICT",
        document_type="affidavit",
        clause_structure=required,
    )
    draft_bridge = DraftFeatureBridge(state)
    compiler = ASTCompilerProtocol(case_base_bridge=cb_bridge, draft_bridge=draft_bridge)

    intake = {
        "case_title": "State v. Nagpur",
        "petitioner_name": "Nagpur",
        "facts": "Nagpur matter occurs.",
        "filing_date": "2026-06-11",
        "jurisdiction": "MH-DISTRICT",
        "document_type": "affidavit"
    }
    
    context = CaseContext(run_id="run_999", intake_brief=intake)
    
    # We populate all required sections with valid content
    sections = {}
    for sec in required:
        if sec == "cause_title":
            sections[sec] = "IN THE COURT OF Nagpur."
        else:
            sections[sec] = f"This is valid content for {sec} section."

    context.capture_agent_output("petitioner_agent", {
        "sections": sections
    })
    
    res = compiler.compile_document(
        case_context=context,
        matter_id="MAT-777",
        run_id="run_999"
    )
    
    assert res["status"] == "SUCCESS"
    assert res["merkle_root"] is not None
    assert res["acceptance_score"] >= 80.0
    
    # Check that draft state text was updated
    assert state.partial_draft_text["cause_title"] == "IN THE COURT OF Nagpur."
    assert state.is_locked is False


def test_ast_compiler_protocol_safeverify_stub_detection():
    cb_bridge = CaseBaseBridge()
    state = DraftState(
        template_id="affidavit_mh.txt",
        jurisdiction_code="MH-DISTRICT",
        document_type="affidavit",
        clause_structure=["cause_title", "facts"],
    )
    draft_bridge = DraftFeatureBridge(state)
    compiler = ASTCompilerProtocol(case_base_bridge=cb_bridge, draft_bridge=draft_bridge)

    intake = {
        "case_title": "State v. Nagpur",
        "petitioner_name": "Nagpur",
        "facts": "Nagpur matter occurs.",
        "filing_date": "2026-06-11",
        "jurisdiction": "MH-DISTRICT",
        "document_type": "affidavit"
    }
    
    context = CaseContext(run_id="run_999", intake_brief=intake)
    # Injecting "sorry" stub
    context.capture_agent_output("petitioner_agent", {
        "sections": {
            "cause_title": "IN THE COURT OF Nagpur.",
            "facts": "I am sorry but we do not know this fact."
        }
    })
    
    with pytest.raises(ValueError, match="SafeVerify Gate violation: Section facts contains unverified or sorry stubs"):
        compiler.compile_document(case_context=context, matter_id="MAT-777", run_id="run_999")


def test_p_ucb_sketches_matchmaking():
    bridge = CaseBaseBridge()
    query_hash = "h_1"
    
    bridge.push_clause_mutation(query_hash, {"sketch_id": "sk_1", "average_reward": 0.8, "visits": 5}, rating_prior=0.9)
    bridge.push_clause_mutation(query_hash, {"sketch_id": "sk_2", "average_reward": 0.9, "visits": 2}, rating_prior=0.8)
    
    top_sketches = bridge.fetch_draft_sketches(query_hash, parent_visits=20)
    assert len(top_sketches) == 2
    # sk_2 should have higher P-UCB score due to fewer visits and higher reward (higher exploration bound)
    assert top_sketches[0]["sketch_id"] == "sk_2"

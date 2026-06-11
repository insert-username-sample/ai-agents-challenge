import pytest
from engine.drafter_mutator import DraftState, DraftFeatureBridge
from tools.legal_ast import DocumentNode, SectionNode, ClauseNode
from tools.sfe import SymbolicFormattingEngine

def test_draft_feature_bridge_pull_and_lock_success():
    state = DraftState(
        template_id="affidavit_mh.txt",
        jurisdiction_code="MH-DISTRICT",
        document_type="affidavit",
        clause_structure=["cause_title", "facts", "prayer", "verification"],
        partial_draft_text={"cause_title": "Old title"},
        sfe_validation_state={"is_valid": True, "acceptance_score": 90.0}
    )
    bridge = DraftFeatureBridge(state)
    
    pulled = bridge.pull_current_draft_state()
    assert pulled.is_locked is True
    assert pulled.checkpoint is not None
    assert pulled.checkpoint["partial_draft_text"] == {"cause_title": "Old title"}
    assert pulled.checkpoint["sfe_validation_state"] == {"is_valid": True, "acceptance_score": 90.0}

def test_draft_feature_bridge_lock_prevent_race_condition():
    state = DraftState(
        template_id="affidavit_mh.txt",
        jurisdiction_code="MH-DISTRICT",
        document_type="affidavit",
        clause_structure=["cause_title", "facts", "prayer", "verification"],
    )
    bridge = DraftFeatureBridge(state)
    bridge.pull_current_draft_state()
    
    with pytest.raises(RuntimeError, match="already locked by another process"):
        bridge.pull_current_draft_state()

def test_draft_feature_bridge_push_and_sfe_validation_success():
    sfe = SymbolicFormattingEngine("MH-DISTRICT")
    required = sfe.rules["required_sections"]

    state = DraftState(
        template_id="affidavit_mh.txt",
        jurisdiction_code="MH-DISTRICT",
        document_type="affidavit",
        clause_structure=required,
    )
    bridge = DraftFeatureBridge(state)
    bridge.pull_current_draft_state()
    
    # Construct a valid DocumentNode for MH-DISTRICT
    doc = DocumentNode(document_type="affidavit", jurisdiction="MH-DISTRICT")
    
    # We populate all required sections with syntax-compliant text (Capitalized first letter, no double spaces)
    doc.sections = [
        SectionNode(
            section_type=sec,
            title=sec.replace("_", " ").title(),
            clauses=[ClauseNode(clause_type=sec, content=f"This is the content for {sec} section.", order=0)]
        )
        for sec in required
    ]
    
    # Force cause title to be Nagpur
    for sec in doc.sections:
        if sec.section_type == "cause_title":
            sec.clauses[0].content = "IN THE COURT OF Nagpur."

    res = bridge.push_compiled_ast_mutations(doc)
    assert res["is_valid"] is True
    assert res["acceptance_score"] >= 85
    assert state.is_locked is False
    assert state.partial_draft_text["cause_title"] == "IN THE COURT OF Nagpur."

def test_draft_feature_bridge_push_rejected_fatal_defects_rollback():
    sfe = SymbolicFormattingEngine("MH-DISTRICT")
    required = sfe.rules["required_sections"]

    state = DraftState(
        template_id="affidavit_mh.txt",
        jurisdiction_code="MH-DISTRICT",
        document_type="affidavit",
        clause_structure=required,
        partial_draft_text={"cause_title": "Old title"},
        sfe_validation_state={"is_valid": True, "acceptance_score": 90.0}
    )
    bridge = DraftFeatureBridge(state)
    bridge.pull_current_draft_state()
    
    # Missing required sections, SFE validate will fail with fatal defects
    doc = DocumentNode(document_type="affidavit", jurisdiction="MH-DISTRICT")
    doc.sections = [
        SectionNode(
            section_type="cause_title",
            title="Cause Title",
            clauses=[ClauseNode(clause_type="cause_title", content="IN THE COURT OF Nagpur.", order=0)]
        )
    ]
    
    with pytest.raises(ValueError, match="Push rejected: SFE validation failed with fatal defects"):
        bridge.push_compiled_ast_mutations(doc)
        
    # Lock is released even on exception/failure (finally block)
    assert state.is_locked is False
    # State must be rolled back to pre-swarm checkpoint
    assert state.partial_draft_text == {"cause_title": "Old title"}
    assert state.sfe_validation_state == {"is_valid": True, "acceptance_score": 90.0}

def test_draft_feature_bridge_override_sc_and_mh():
    # IN-SC cause title override
    sfe_sc = SymbolicFormattingEngine("IN-SC")
    required_sc = sfe_sc.rules["required_sections"]

    state_sc = DraftState(
        template_id="affidavit_mh.txt",
        jurisdiction_code="IN-SC",
        document_type="affidavit",
        clause_structure=required_sc,
    )
    bridge_sc = DraftFeatureBridge(state_sc)
    bridge_sc.pull_current_draft_state()
    
    doc_sc = {
        "sections": {
            sec: f"Content for {sec} section of Supreme Court."
            for sec in required_sc
        }
    }
    # Set non-standard cause title to trigger prefix override
    doc_sc["sections"]["cause_title"] = "Nagpur matter."
    
    res = bridge_sc.push_compiled_ast_mutations(doc_sc)
    assert state_sc.partial_draft_text["cause_title"].startswith("IN THE SUPREME COURT OF INDIA")

    # MH jurisdiction override (IPC -> BNS)
    sfe_mh = SymbolicFormattingEngine("MH-DISTRICT")
    required_mh = sfe_mh.rules["required_sections"]

    state_mh = DraftState(
        template_id="affidavit_mh.txt",
        jurisdiction_code="MH-DISTRICT",
        document_type="affidavit",
        clause_structure=required_mh,
    )
    bridge_mh = DraftFeatureBridge(state_mh)
    bridge_mh.pull_current_draft_state()
    
    doc_mh = {
        "sections": {
            sec: f"Content for {sec} section in Maharashtra."
            for sec in required_mh
        }
    }
    # Inject IPC citation to trigger override
    doc_mh["sections"]["facts"] = "Violation of Section 302 of IPC happened."
    
    bridge_mh.push_compiled_ast_mutations(doc_mh)
    assert "BNS" in state_mh.partial_draft_text["facts"]
    assert "IPC" not in state_mh.partial_draft_text["facts"]

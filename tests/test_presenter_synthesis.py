import pytest
from engine.presenter_synthesis import PresenterOratoricalEngine, NodeExtractionResult, CLIRecord, SynopsisBlock
from engine.mcts import MCTSNode

def test_extract_load_bearing_nodes():
    intake = {}
    engine = PresenterOratoricalEngine(intake)
    
    # Mock nodes with different UCT values
    node1 = MCTSNode(
        state={"step": 1},
        agent_output="We challenge this termination under Article 14 of the Constitution.",
        visits=10,
        value=8.0
    )
    node2 = MCTSNode(
        state={"step": 2},
        agent_output="Section 25F of the Industrial Disputes Act applies to this case.",
        visits=5,
        value=3.0
    )
    node3 = MCTSNode(
        state={"step": 3},
        agent_output="The prayer is to grant reinstatement with full back wages.",
        visits=2,
        value=1.5
    )
    node4 = MCTSNode(
        state={"step": 4},
        agent_output="The employee was working since 2018 at the establishment.",
        visits=3,
        value=-1.0  # Negative UCT score
    )
    
    nodes = [node1, node2, node3, node4]
    
    # Calculate UCT scores manually to ensure positive/negative values
    node1.visits = 10; node1.value = 8.0   # score: 0.8
    node2.visits = 5; node2.value = 3.0    # score: 0.6
    node3.visits = 2; node3.value = 1.5    # score: 0.75
    node4.visits = 3; node4.value = -3.0   # score: -1.0
    
    results = engine.extract_load_bearing_nodes(nodes)
    
    # Node4 has negative score, should be excluded -> 3 nodes remain
    assert len(results) == 3
    
    # Sorted by UCT score descending (node1: 0.8, node3: 0.75, node2: 0.6)
    assert results[0].node_id == node1.node_id
    assert results[1].node_id == node3.node_id
    assert results[2].node_id == node2.node_id
    
    # Verify theme tags
    assert results[0].theme_tag == "Constitutional"
    assert results[1].theme_tag == "Relief"
    assert results[2].theme_tag == "Statutory"
    
    # Verify weight coefficients
    total_uct = node1.uct_score() + node3.uct_score() + node2.uct_score()
    assert abs(results[0].weight_coefficient - (node1.uct_score() / total_uct)) < 0.001
    
    # Verify nodes memory storage in intake
    assert len(intake["presenter_extracted_node_ids"]) == 3
    assert node1.node_id in intake["presenter_extracted_node_ids"]

def test_cognitive_load_index():
    # Test text readability check and simplification
    intake = {"presenter_flesch_threshold": 40.0}
    engine = PresenterOratoricalEngine(intake)
    
    # Paragraph A: Simple text
    text_a = "The petitioner is a clerk. He was appointed in 2018. His service was terminated in 2026."
    
    # Paragraph B: Complex text with low Flesch Reading Ease and long sentences
    text_b = (
        "The petitioner herein challenges the arbitrary, illegal and unconstitutional termination of her services "
        "which was executed by the respondent authority without following the mandatory statutory provisions "
        "of Section 25F of the Industrial Disputes Act and therefore the action is completely void and invalid."
    )
    
    records = engine.validate_cognitive_load([text_a, text_b])
    
    assert len(records) == 2
    
    # Paragraph A should not trigger simplification
    assert records[0].is_simplified is False
    assert records[0].avg_words_per_sentence < 15.0
    
    # Paragraph B should trigger simplification
    assert records[1].is_simplified is True
    assert "petitioner herein challenges" in records[1].simplified_text.lower()
    # Should break the long sentence into at least two parts
    assert records[1].simplified_text.count(".") >= 2

def test_simplify_citations():
    intake = {}
    engine = PresenterOratoricalEngine(intake)
    
    text = "As held in (2024) 1 SCC 12, the termination is void. Also see AIR 1996 SC 1234."
    simplified = engine.simplify_citations(text)
    
    # Vol/page should be stripped
    assert "2024 SCC" in simplified
    assert "1996 AIR" in simplified
    assert "12" not in simplified
    assert "1234" not in simplified

def test_design_synopsis_layout():
    intake = {}
    engine = PresenterOratoricalEngine(intake)
    
    res1 = NodeExtractionResult(
        node_id="N1",
        uct_score=0.8,
        text_argument="Constitutional argument",
        theme_tag="Constitutional"
    )
    res2 = NodeExtractionResult(
        node_id="N2",
        uct_score=0.7,
        text_argument="Statutory argument",
        theme_tag="Statutory"
    )
    res3 = NodeExtractionResult(
        node_id="N3",
        uct_score=0.6,
        text_argument="Factual argument",
        theme_tag="Factual"
    )
    res4 = NodeExtractionResult(
        node_id="N4",
        uct_score=0.5,
        text_argument="Relief argument",
        theme_tag="Relief"
    )
    
    # Pass in shuffled order
    shuffled_nodes = [res3, res1, res4, res2]
    blocks = engine.design_synopsis_layout(shuffled_nodes)
    
    # Should be sorted Constitutional, Statutory, Factual, Relief
    assert len(blocks) == 4
    assert blocks[0].block_type == "Constitutional"
    assert blocks[0].priority_index == 0
    assert blocks[1].block_type == "Statutory"
    assert blocks[1].priority_index == 1
    assert blocks[2].block_type == "Factual"
    assert blocks[2].priority_index == 2
    assert blocks[3].block_type == "Relief"
    assert blocks[3].priority_index == 3
    
    # State flags
    assert intake.get("presenter_layout_locked") is True
    assert intake.get("presenter_blocks_count") == 4


def test_orchestrator_presenter_integration():
    import asyncio
    from unittest.mock import AsyncMock, patch, MagicMock
    from agents.orchestrator import _run_strategist

    # Mock case intake
    case_context = {
        "document_type": "Writ Petition",
        "jurisdiction": "MH-HC",
        "cause_of_action": "Arbitrary service termination challenge.",
        "birth_year": 1980,
    }

    # Mock the return values for MCTSEngine and validators
    mock_node = MagicMock()
    mock_node.node_id = "N_BEST"
    mock_node.value = 8.0
    mock_node.visits = 10
    mock_node.agent_output = "We challenge this termination under Article 14 of the Constitution."
    mock_node.uct_score = MagicMock(return_value=0.8)

    mock_mcts_instance = MagicMock()
    mock_mcts_instance.run = AsyncMock(return_value=[mock_node])

    # Run the strategist swarm execution
    with patch("engine.mcts.MCTSEngine", return_value=mock_mcts_instance), \
         patch("engine.validators.SwarmValidator") as mock_validator_cls:
         
        mock_validator = MagicMock()
        mock_validator_cls.return_value = mock_validator
        
        result = asyncio.run(_run_strategist(case_context, "Document text"))
        
        assert result.get("strategy_ran") is True
        memo = result.get("strategy_memo", "")
        
        # Verify PresenterOratoricalEngine ran and outputted in memo
        assert "Optimized Oral Argument Synopsis" in memo
        assert "Constitutional" in memo
        assert "Article 14" in memo
        assert "N_BEST" in memo


def test_audit_semantic_equivalence():
    # client name is present
    intake = {"client_name": "Vidya Khobrekar"}
    engine = PresenterOratoricalEngine(intake)
    
    oral = "Vidya Khobrekar challenges the termination under Article 14 of the Constitution."
    ast = "Challenge termination under Article 14 of the Constitution."
    
    # should pass
    engine.audit_semantic_equivalence(oral, ast)
    assert intake.get("semantic_equivalence_runs") == 100
    assert intake.get("semantic_delta") is not None
    
    # client name is missing
    bad_oral = "Challenges the termination under Article 14."
    with pytest.raises(ValueError, match="Fidelity mismatch: client name"):
        engine.audit_semantic_equivalence(bad_oral, ast)


def test_check_legal_precision():
    intake = {}
    engine = PresenterOratoricalEngine(intake)
    
    # Happy path
    engine.check_legal_precision("The petitioner was charged under Section 302 for murder.")
    assert intake.get("non_standard_jargon_count") == 0
    assert intake.get("legal_precision_cache") == {"status": "VERIFIED"}
    
    # Mismatch description (Section 302 retrenchment)
    with pytest.raises(ValueError, match="statutory description mismatch"):
        engine.check_legal_precision("The petitioner was retrenched under Section 302.")


def test_simulate_hostile_bench():
    # Condonation not applied but pivot claims it was
    intake_bad = {"delay_condonation_applied": False}
    engine_bad = PresenterOratoricalEngine(intake_bad)
    with pytest.raises(ValueError, match="defensive pivot contradicts factual matrix"):
        engine_bad.simulate_hostile_bench("Some oral text")
    assert intake_bad.get("oral_synopsis_purged") is True

    # Condonation applied
    intake_good = {"delay_condonation_applied": True}
    engine_good = PresenterOratoricalEngine(intake_good)
    pivots = engine_good.simulate_hostile_bench("Some oral text")
    assert len(pivots) == 3
    assert intake_good.get("hostile_bench_question_loops") == 10


def test_audit_rhetorical_limitations():
    intake = {}
    engine = PresenterOratoricalEngine(intake)
    
    rhetorical_text = "This outrageous and shocking termination is a blatant violation of service rules."
    clean_text = engine.audit_rhetorical_limitations(rhetorical_text)
    
    # Emotional words should be stripped
    assert "outrageous" not in clean_text.lower()
    assert "shocking" not in clean_text.lower()
    assert "blatant" not in clean_text.lower()
    assert "termination is a violation" in clean_text.lower()
    assert intake.get("rhetorical_correction_triggered") is True
    assert intake.get("rhetorical_compliance_status") == "COMPLIANT"
    assert intake.get("factual_to_rhetoric_ratio") is not None


def test_anchor_oral_arguments():
    intake = {}
    engine = PresenterOratoricalEngine(intake)
    
    prayer = "Therefore the petitioner prays that this Hon'ble Court may be pleased to grant reinstatement."
    oral_good = "Therefore the petitioner prays that this Hon'ble Court may be pleased to grant reinstatement soon."
    
    # Happy path (similar words, distance < 0.20)
    engine.anchor_oral_arguments(oral_good, prayer)
    assert intake.get("presenter_prayer_clause_hash") is not None
    assert intake.get("anchor_signature_valid") is True
    assert intake.get("anchor_parameters_locked") is True
    
    # Frame warning scenario (completely different words, distance > 0.20)
    oral_bad = "The respondent is completely liable for damages and must pay 100000 rupees immediately."
    with pytest.raises(ValueError, match="Frame warning: similarity distance"):
        engine.anchor_oral_arguments(oral_bad, prayer)


def test_detect_opponent_reframing():
    intake = {}
    engine = PresenterOratoricalEngine(intake)
    
    # Opponent text shifting breach to fraud
    opponent_text = "The petitioner committed a deliberate fraud on the registry."
    reframed = engine.detect_opponent_reframing(opponent_text, "breach")
    assert reframed is True
    assert intake.get("opponent_reframing_detected") is True
    assert intake.get("frame_correction_override_triggered") is True
    
    # Opponent text within boundaries
    intake_ok = {}
    engine_ok = PresenterOratoricalEngine(intake_ok)
    reframed_ok = engine_ok.detect_opponent_reframing("The contract breach has no damages.", "breach")
    assert reframed_ok is False
    assert intake_ok.get("opponent_reframing_detected") is False


def test_execute_frame_correction():
    intake = {}
    engine = PresenterOratoricalEngine(intake)
    
    divergent = "We are discussing unrelated details."
    corrected = engine.execute_frame_correction(divergent, ["service termination", "Article 14"])
    
    assert "Returning to the core issue: service termination Article 14" in corrected
    assert intake.get("divergent_argument_blocks_cleared") is True
    assert intake.get("outline_attention_weights_recalculated") is True
    assert intake.get("frame_recovery_swarm_alert_sent") is True


def test_verify_semantic_stability():
    intake = {}
    engine = PresenterOratoricalEngine(intake)
    
    historical = [
        "Writ challenging arbitrary termination under service rules.",
        "Termination challenge under Article 14 rules."
    ]
    current_stable = "Writ challenging termination under Article 14 service rules."
    
    # Stable path should pass
    engine.verify_semantic_stability(historical, current_stable)
    assert intake.get("semantic_stability_locked") is True
    assert intake.get("semantic_coordinates_shift_trends") == "stable"
    
    # Drifting path variance > 0.15 should raise stability failed
    intake_drift = {}
    engine_drift = PresenterOratoricalEngine(intake_drift)
    current_unstable = "Completely different text pleading regarding contract damages."
    with pytest.raises(ValueError, match="Semantic stability validation failed"):
        engine_drift.verify_semantic_stability(historical, current_unstable)
    assert intake_drift.get("unstable_semantic_trajectory_filtered") is True


def test_serialize_to_presentation_json():
    intake = {
        "hostile_bench_pivot_maps": {
            "Is the claim barred by limitation?": "No, it is filed within three years of cause of action."
        },
        "grounding_metadata": {"N_BEST": {"evidence_source": "Exhibit A"}},
        "elo_scores": {"N_BEST": 1420.0}
    }
    engine = PresenterOratoricalEngine(intake)
    blocks = [
        SynopsisBlock(
            block_type="Constitutional",
            priority_index=0,
            content="Constitutional argument with UNVERIFIED: missing limitation stamp.",
            duration_bounds=(0.0, 60.0),
            keywords_density=0.1,
            transitions_checked=True
        )
    ]
    
    json_str = engine.serialize_to_presentation_json(blocks)
    
    # Verify structure and contents
    import json
    data = json.loads(json_str)
    assert data["transaction_type"] == "PRESENTATION"
    assert len(data["synopsis_blocks"]) == 1
    assert data["synopsis_blocks"][0]["block_type"] == "Constitutional"
    assert "Is the claim barred by limitation?" in data["anticipated_queries"]
    assert "missing limitation stamp" in data["unverified_subgoals"]
    assert data["grounding_metadata"]["N_BEST"]["evidence_source"] == "Exhibit A"
    assert data["elo_scores"]["N_BEST"] == 1420.0
    assert data["signature"] is not None
    assert data["timestamp"] is not None
    
    assert intake.get("presenter_payload_locked") is True
    assert intake.get("presenter_payload_size_bytes") > 0


def test_monitor_judge_responses():
    intake = {
        "hostile_bench_pivot_maps": {
            "What is the limitation date?": "The date is 2026-06-09."
        }
    }
    engine = PresenterOratoricalEngine(intake)
    
    # Happy path: Accepted query
    queries = [
        {"query": "What is the limitation date?", "severity": 4, "delay_latency_ms": 35.0, "verdict": "ACCEPTED"}
    ]
    engine.monitor_judge_responses(queries)
    
    assert intake.get("judge_evaluation_status") == "ACTIVE"
    assert intake.get("judge_interruption_frequency") == 1
    assert len(intake.get("judge_interaction_logs")) == 1
    assert intake.get("judge_response_status_params")["average_severity"] == 4.0
    
    # Failure path: Rejected query (verdict="REJECTED") or severity >= 9
    bad_queries = [
        {"query": "This pleading is unacceptable.", "severity": 9, "delay_latency_ms": 100.0, "verdict": "REJECTED"}
    ]
    with pytest.raises(ValueError, match="Judge Agent rejected the argument"):
        engine.monitor_judge_responses(bad_queries)
        
    assert intake.get("judge_evaluation_status") == "FAILED"
    assert intake.get("oral_synopsis_purged") is True


def test_route_interruption_to_pivot():
    intake = {
        "hostile_bench_pivot_maps": {
            "How do you justify the delay?": "We filed a condonation application showing sufficient cause."
        }
    }
    engine = PresenterOratoricalEngine(intake)
    
    # Match query
    pivot = engine.route_interruption_to_pivot("How do you justify the delay?")
    assert pivot == "We filed a condonation application showing sufficient cause."
    assert intake.get("judge_queue_pivot_response") == pivot
    assert intake.get("temporary_pivot_files_wiped") is True
    assert intake.get("pivot_transaction_logs_locked") is True
    
    # Unmatched query (fallback)
    fallback_pivot = engine.route_interruption_to_pivot("Unmatched query?")
    assert "fully support this pleading" in fallback_pivot


def test_submit_final_adjudication():
    intake = {
        "client_name": "Vidya Khobrekar",
        "hostile_bench_question_loops": 10,
        "presenter_layout_locked": True,
        "semantic_equivalence_runs": 100
    }
    engine = PresenterOratoricalEngine(intake)
    
    ready_token = engine.submit_final_adjudication()
    
    assert "READY-ATTESTATION-TOKEN" in ready_token
    assert intake.get("judge_evaluation_status") == "COMPLETE"
    assert intake.get("coordinator_engine_notified") is True
    assert intake.get("presentation_editing_channels_locked") is True
    assert intake.get("presentation_cache_cleared") is True
    assert intake.get("presentation_session_logs_closed") is True
    assert intake.get("presentation_computation_costs") is not None





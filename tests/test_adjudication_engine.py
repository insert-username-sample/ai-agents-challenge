import pytest
from engine.adjudication_engine import (
    JudicialTensorEvaluator,
    PrecedentMetadata,
    StatutoryProvision,
    GradientArrayRecord
)
from engine.validators import SectionApplicationError

def test_analyze_argument_vectors():
    intake = {
        "precedent_registry": {
            "(2024) 1 SCC 12": {
                "court_level": "SC",
                "bench_size": 3,
                "is_overruled": False
            },
            "AIR 1996 SC 1234": {
                "court_level": "SC",
                "bench_size": 2,
                "is_overruled": True
            },
            "AIR 2002 Bom 456": {
                "court_level": "HC",
                "bench_size": 1,
                "is_overruled": False,
                "holding": "opposite"
            }
        }
    }
    evaluator = JudicialTensorEvaluator(intake)
    
    # Happy path without overruled precedent
    petitioner = ["We argue under Article 14 of the Constitution and cite (2024) 1 SCC 12."]
    opponent = ["We argue that the claim fails and cite (2024) 1 SCC 12."]
    
    res = evaluator.analyze_argument_vectors(petitioner, opponent)
    assert res["jaccard_similarity"] > 0.0
    assert "Article 14" in res["statutes"]
    assert res["p_success"] > 0.5
    assert len(intake["vector_scoring_logs"]) == 1
    assert res["constitutional_mappings"]["Equality"] == "Article 14"
    
    # Adversarial / overruled path
    petitioner_bad = ["We cite AIR 1996 SC 1234."]
    opponent_bad = ["We cite AIR 2002 Bom 456 to oppose them."]
    
    res_bad = evaluator.analyze_argument_vectors(petitioner_bad, opponent_bad)
    # Since AIR 1996 SC 1234 is overruled, p_success must be 0.0
    assert res_bad["p_success"] == 0.0
    assert intake.get("uct_penalty") == 5000.0
    assert "Overruled precedent cited: AIR 1996 SC 1234" in res_bad["conflicts"]


def test_audit_statutory_compliance():
    intake = {}
    evaluator = JudicialTensorEvaluator(intake)
    
    provisions = [
        StatutoryProvision(
            act_name="Industrial Disputes Act",
            section_number="25F",
            is_active=True,
            description="conditions precedent to retrenchment of workmen",
            penalty_bounds=(0.0, 0.0)
        ),
        StatutoryProvision(
            act_name="Indian Penal Code",
            section_number="302",
            is_active=True,
            description="punishment for murder",
            penalty_bounds=(0.0, 14.0)  # Max 14 years or life
        ),
        StatutoryProvision(
            act_name="Repealed Act",
            section_number="99",
            is_active=False,
            is_repealed=True
        )
    ]
    
    # Happy Path
    arguments = [
        "The petitioner was terminated violating Section 25F of the Industrial Disputes Act which lays down conditions precedent to retrenchment of workmen."
    ]
    res = evaluator.audit_statutory_compliance(arguments, provisions)
    assert len(res) == 1
    assert res[0]["section_number"] == "25F"
    assert res[0]["match_ratio"] == 1.0
    
    # Repealed Act compliance error
    arguments_repealed = ["We claim under Section 99 of the Repealed Act."]
    with pytest.raises(SectionApplicationError, match="Repealed or inactive provision cited"):
        evaluator.audit_statutory_compliance(arguments_repealed, provisions)
        
    # Element mismatch (ratio < 0.2)
    arguments_mismatch = ["We apply Section 302 of the Indian Penal Code to retrenchment."]
    with pytest.raises(SectionApplicationError, match="Offence elements do not match description"):
        evaluator.audit_statutory_compliance(arguments_mismatch, provisions)
        
    # Penalty bounds exceeded
    arguments_excess = ["The accused must be sentenced to 20 years under Section 302 of the Indian Penal Code for murder."]
    with pytest.raises(SectionApplicationError, match="exceeds maximum statutory bound"):
        evaluator.audit_statutory_compliance(arguments_excess, provisions)


def test_optimize_precedent_weights():
    intake = {}
    evaluator = JudicialTensorEvaluator(intake)
    
    cited_cases = [
        PrecedentMetadata(case_name="SC Case 1", court_level="SC", bench_size=3, decision_year=2024),
        PrecedentMetadata(case_name="HC Case 1", court_level="HC", bench_size=2, decision_year=2020),
        PrecedentMetadata(case_name="SC Case Appeal Pending", court_level="SC", bench_size=5, decision_year=2025, pending_sc_appeal=True),
        PrecedentMetadata(case_name="LC Case 1", court_level="LC", bench_size=1, decision_year=2026)
    ]
    
    weights = evaluator.optimize_precedent_weights(cited_cases)
    
    # SC case weight should be optimized
    assert weights["SC Case 1"] > weights["HC Case 1"]
    
    # Pending SC appeal should penalize weight
    assert weights["SC Case Appeal Pending"] < weights["SC Case 1"]
    
    # LC cases filtered/penalized
    assert weights["LC Case 1"] < weights["HC Case 1"]
    
    assert intake.get("precedent_weights_locked") is True
    assert len(intake.get("precedent_weight_matrices")) == 4


def test_construct_gradient_arrays():
    intake = {}
    evaluator = JudicialTensorEvaluator(intake)
    
    issue_scores = {
        "limitation": 0.8,
        "jurisdiction": 0.9,
        "merits": 0.2 # Negative topic
    }
    
    record = evaluator.construct_gradient_arrays(issue_scores)
    
    assert record.average_score == pytest.approx(0.6333, abs=0.01)
    assert record.score_variance > 0.0
    assert record.gradient_dimensions == 3
    assert "merits" in record.complexity_weights
    
    assert intake.get("gradient_parameters_locked") is True
    assert "merits" in intake.get("negative_topics_detected")


def test_verify_subject_matter_jurisdiction():
    from engine.validators import SubjectMatterForumError
    intake = {}
    evaluator = JudicialTensorEvaluator(intake)
    
    # Happy path
    evaluator.verify_subject_matter_jurisdiction("contract_dispute", 5000000.0, "District Court")
    assert intake.get("subject_matter_jurisdiction_locked") is True
    assert len(intake.get("subject_matter_audit_logs")) == 1
    
    # CAT service dispute error
    with pytest.raises(SubjectMatterForumError, match="belong exclusively to Central Administrative Tribunal"):
        evaluator.verify_subject_matter_jurisdiction("service_dispute", 1000000.0, "Civil Court")
        
    # SARFAESI civil court error
    with pytest.raises(SubjectMatterForumError, match="barred under Section 18 from Civil Courts"):
        evaluator.verify_subject_matter_jurisdiction("sarfaesi_recovery", 1000000.0, "Civil Court")
        
    # Pecuniary limit exceeded (> 2 Crore)
    with pytest.raises(SubjectMatterForumError, match="exceeds District Court limits"):
        evaluator.verify_subject_matter_jurisdiction("contract_dispute", 25000000.0, "District Court")
        
    # Pecuniary limit below bounds (< 1 Lakh)
    with pytest.raises(SubjectMatterForumError, match="falls below District Court bounds"):
        evaluator.verify_subject_matter_jurisdiction("contract_dispute", 50000.0, "District Court")


def test_audit_territorial_jurisdiction():
    from engine.validators import JurisdictionalDefectError
    from engine.adjudication_engine import TerritorialCoordinates
    intake = {}
    evaluator = JudicialTensorEvaluator(intake)
    
    # Expected lat range: (18.0, 20.0), lon range: (72.0, 74.0)
    coords_ok = TerritorialCoordinates(latitude=19.1, longitude=73.2, police_station="Colaba PS", district="Mumbai", state_code="MH")
    evaluator.audit_territorial_jurisdiction(coords_ok, ["Colaba, Mumbai, MH"])
    assert intake.get("multijurisdictional_claims_detected") is True
    assert len(intake.get("territorial_audit_records")) == 1
    
    # Outside bounds error
    coords_bad = TerritorialCoordinates(latitude=15.2, longitude=73.2, police_station="Colaba PS", district="Mumbai", state_code="MH")
    with pytest.raises(JurisdictionalDefectError, match="fall outside bounds"):
        evaluator.audit_territorial_jurisdiction(coords_bad, ["Colaba, Mumbai, MH"])


def test_verify_act_text():
    from engine.validators import AdversarialAlterationError
    from engine.adjudication_engine import ActVerificationPayload
    intake = {}
    evaluator = JudicialTensorEvaluator(intake)
    
    payload_ok = ActVerificationPayload(
        act_name="BSA",
        raw_text="The evidence is admissible.",
        verified_text="The evidence is admissible.",
        publication_date="2024-06-01",
        version="v1.0"
    )
    evaluator.verify_act_text(payload_ok)
    assert intake.get("verified_act_text_locked") is True
    assert len(intake.get("act_text_matching_results")) == 1
    
    # Text alteration (low similarity)
    payload_bad_text = ActVerificationPayload(
        act_name="BSA",
        raw_text="The evidence is excluded.",
        verified_text="The evidence is admissible.",
        publication_date="2024-06-01",
        version="v1.0"
    )
    with pytest.raises(AdversarialAlterationError, match="Text deviation detected"):
        evaluator.verify_act_text(payload_bad_text)
        
    # Punctuation mismatch
    payload_bad_punctuation = ActVerificationPayload(
        act_name="BSA",
        raw_text="The evidence is admissible...",
        verified_text="The evidence is admissible.",
        publication_date="2024-06-01",
        version="v1.0"
    )
    with pytest.raises(AdversarialAlterationError, match="Text deviation detected"):
        evaluator.verify_act_text(payload_bad_punctuation)


def test_calibrate_bias_simulation():
    intake = {}
    evaluator = JudicialTensorEvaluator(intake)
    
    bench_scores = evaluator.calibrate_bias_simulation(0.7)
    assert "Conservative Bench" in bench_scores
    assert "Activist Bench" in bench_scores
    assert intake.get("bias_calibration_locked") is True
    assert intake.get("average_p_success") is not None
    assert len(intake.get("mcts_simulation_outcomes")) == 1


def test_stage3_deep_interrogation():
    from engine.mcts import MCTSNode
    import re
    
    intake = {
        "cause_of_action": "The petitioner filed a dispute regarding terminated employment on a specific date.",
        "precedent_registry": {}
    }
    evaluator = JudicialTensorEvaluator(intake)
    
    # Create mock MCTS nodes
    root = MCTSNode(state=intake)
    child1 = MCTSNode(state=intake, parent=root, agent_output="We argue that Section 25F applies as per AIR 2024 SC 1234 because retrenchment was illegal.")
    child2 = MCTSNode(state=intake, parent=root, agent_output="No precedent is cited here, simple argument.")
    
    # Identify weak nodes
    weak_nodes = evaluator.identify_weak_nodes([child1, child2])
    assert len(weak_nodes) > 0
    assert intake["weak_nodes_identified"] is True
    assert child2.node_id in intake["weak_node_ids"]
    
    # Generate adversarial hypotheticals
    queries = evaluator.generate_adversarial_hypotheticals(weak_nodes)
    assert len(queries) > 0
    assert any("Section 25F" in q or "Section X" in q for q in queries)
    assert intake["hypothetical_parameters_locked"] is True
    
    # Simulate interruption
    res = evaluator.simulate_interruption(queries, presenter_response_time=6.0, logical_contradiction=True, mcts_nodes=[child1, child2])
    assert res["collapsed_branches"] > 0
    assert child2.pruned is True
    assert child2.prune_reason == "JUDICIAL_DEAD_END"
    
    # Route strategy penalties
    evaluator.route_strategy_penalties([child2])
    assert root.uct_penalty == 1000.0
    assert root.pruned is True


def test_stage4_reward_and_backpropagation():
    from engine.mcts import MCTSNode
    intake = {}
    evaluator = JudicialTensorEvaluator(intake)
    
    # 1. Adjudication JSON Construction
    payload = evaluator.construct_adjudication_json(
        p_success=0.75,
        simulated_order="Petition dismissed.",
        weaknesses_found=["No precedent support"],
        private_key="test_private_key"
    )
    assert payload["jsonrpc"] == "2.0"
    assert payload["params"]["p_success"] == 0.75
    assert "signature" in payload
    assert intake["adjudication_payload_locked"] is True
    
    # 2. Reward Computation
    root = MCTSNode(state=intake)
    child = MCTSNode(state=intake, parent=root)
    rewards = evaluator.compute_terminal_rewards([child], p_success=0.85)
    assert rewards[0] == 85.0
    assert child.value == 85.0
    assert intake["reward_variables_locked"] is True
    
    # 3. Backpropagation Execution
    evaluator.execute_backpropagation(child, reward=85.0)
    assert child.visits == 1
    assert root.visits == 1
    assert root.value == 85.0
    assert intake["backpropagation_locked"] is True
    
    # 4. Search Termination Decisions
    terminate = evaluator.decide_search_termination(
        visit_count=100,
        threshold_limits=50,
        variance=0.01,
        bounds=0.05,
        elapsed_time=10.0
    )
    assert terminate is True
    assert intake["search_session_closed"] is True
    assert "search_stop_token" in intake


def test_stage3_deep_interrogation_rigorous_edge_cases():
    from engine.mcts import MCTSNode
    
    intake = {
        "cause_of_action": "Arbitrary termination of service without compliance of mandatory rules",
        "precedent_registry": {}
    }
    evaluator = JudicialTensorEvaluator(intake)
    
    # Setup deep hierarchy: root -> child -> grandchild
    root = MCTSNode(state=intake)
    
    # child has precedent citation, so it's not weak by default
    child = MCTSNode(state=intake, parent=root, agent_output="We cite 2026 AIR SC 999 to show Section 311 is active.")
    
    # grandchild has no precedent, so it is weak
    grandchild = MCTSNode(state=intake, parent=child, agent_output="We argue that under Section 14, termination is invalid.")
    
    # Link them
    child.children.append(grandchild)
    root.children.append(child)
    
    # Identify weak nodes
    weak_nodes = evaluator.identify_weak_nodes([child, grandchild])
    
    # grandchild has no citations, so it must be identified as weak
    assert grandchild in weak_nodes
    assert child not in weak_nodes
    
    # Check Jaccard distance calculation on grandchild
    assert grandchild.node_id in intake["weak_nodes_semantic_distances"]
    assert intake["weak_nodes_semantic_distances"][grandchild.node_id] > 0.0
    
    # Check structural check and evidentiary check state updates
    assert grandchild.state["has_standard_structure"] is True
    assert grandchild.state["evidentiary_linkages_traced"] is True
    
    # Generate adversarial queries
    queries = evaluator.generate_adversarial_hypotheticals(weak_nodes)
    assert len(queries) == 3 # 3 queries generated for one weak node
    assert any("Section 14" in q for q in queries)
    
    # Simulate interruption without contradiction, but with slow response time
    res = evaluator.simulate_interruption(queries, presenter_response_time=7.5, logical_contradiction=False, mcts_nodes=[child, grandchild])
    assert res["collapsed_branches"] == 0
    assert abs(res["average_quality_index"] - 0.7) < 0.001
    assert grandchild.pruned is False # Not pruned because logical_contradiction was False
    
    # Simulate interruption WITH contradiction
    res_collapsed = evaluator.simulate_interruption(queries, presenter_response_time=2.0, logical_contradiction=True, mcts_nodes=[child, grandchild])
    assert res_collapsed["collapsed_branches"] == 3
    assert grandchild.pruned is True
    assert grandchild.prune_reason == "JUDICIAL_DEAD_END"
    
    # Route strategy penalties
    evaluator.route_strategy_penalties([grandchild])
    # Penalty backpropagates to child and root
    assert child.uct_penalty == 1000.0
    assert root.uct_penalty == 1000.0
    assert child.pruned is True
    assert root.pruned is True


def test_stage4_reward_productivity_and_improvement():
    from engine.mcts import MCTSNode, AlphaProofRater
    
    intake = {
        "cause_of_action": "Arbitrary termination of service",
        "precedent_registry": {}
    }
    evaluator = JudicialTensorEvaluator(intake)
    
    root = MCTSNode(state=intake)
    # Child A: Strong argument with citations
    child_a = MCTSNode(state=intake, parent=root, agent_output="We cite 2026 AIR SC 999 to show the procedure was violated.")
    # Child B: Weak argument without citations
    child_b = MCTSNode(state=intake, parent=root, agent_output="No citation argument.")
    
    root.children = [child_a, child_b]
    
    # 1. Run AlphaProof Rater to rank and rate them initially
    AlphaProofRater.rank_and_rate(root.children)
    
    # Verify Child A has higher elo_rating and prior_probability than Child B
    assert child_a.elo_rating > child_b.elo_rating
    assert child_a.prior_probability > child_b.prior_probability
    
    # 2. Simulate reward calculations and backpropagation
    # Child A gets evaluated by the Judge with high success probability
    p_success_a = 0.90
    rewards_a = evaluator.compute_terminal_rewards([child_a], p_success=p_success_a)
    # Scale reward back to 0.0 - 1.0 range for UCT compatibility (rewards_a[0] / 100.0)
    evaluator.execute_backpropagation(child_a, reward=rewards_a[0] / 100.0)
    
    # Child B gets evaluated by the Judge with low success probability
    p_success_b = 0.20
    rewards_b = evaluator.compute_terminal_rewards([child_b], p_success=p_success_b)
    evaluator.execute_backpropagation(child_b, reward=rewards_b[0] / 100.0)
    
    # Verify average scores (Q value) updated correctly on nodes
    assert child_a.value > child_b.value
    assert child_a.value == pytest.approx(90.9)
    assert child_b.value == pytest.approx(20.2)
    assert child_a.visits == 1
    assert child_b.visits == 1
    assert root.visits == 2
    
    # 3. Calculate UCT score and assert Child A UCT score > Child B UCT score
    uct_a = child_a.uct_score(c=0.2, p_ucb=True)
    uct_b = child_b.uct_score(c=0.2, p_ucb=True)
    
    assert uct_a > uct_b
    
    # 4. Demonstrate search path selection prioritization
    # Under selection rule, child_a should be chosen over child_b
    selected_node = max(root.children, key=lambda n: n.uct_score(c=0.2, p_ucb=True))
    assert selected_node == child_a





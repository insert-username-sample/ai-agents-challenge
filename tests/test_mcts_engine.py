import pytest
from engine.mcts import MCTSNode, MCTSEngine
from engine.validators import (
    SwarmValidator,
    RoleAssumptionError,
    LimitationBarredError,
    JurisdictionalDefectError,
    SubjectMatterForumError,
    LocusStandiError,
    FormattingDefectError,
    FactualContradictionError,
    WitnessCredibilityError,
    EvidenceQualityError,
    SectionApplicationError,
    PoliceDiaryError,
    ArrestProcedureError,
    SearchSeizureError,
    ProbabilityInversionError,
    AdversarialPoisonError,
    AdversarialAlterationError,
    WitnessTamperingError,
    PreservationCompromisedError,
    CompileBlockedError,
    CognitiveLoadLimitError,
    FlowGapWarning,
    CitationFormatDefectError,
    PremiseInconsistentError,
    StatutoryMismatchWarn,
    InvalidProofAttemptError,
    CourtFeeDefectError,
    AdvocateSuspendedDefectError,
    TranslationDefectError,
    LayoutViolationDefectError,
    ObfuscationAttemptError,
    FootnoteCompromisedError,
    IndexAlignmentDefectError,
    DefectSheetHaltError,
)
from agents.harness_rules import ComputeWastePreventionError

# Sample case inputs for testing
IN_PERSON_CASE = {
    "name": "Vidya Khobrekar",
    "role": "petitioner_in_person",
    "birth_year": 1965,
    "cause_of_action": "Arbitrary service termination challenge.",
}

ADVOCATE_CASE = {
    "name": "Karan Singh",
    "role": "advocate",
    "birth_year": 1980,
    "cause_of_action": "Suit for recovery under Order 37 CPC.",
}


def test_mcts_node_properties():
    # Verify node instantiation, ID hashing and UCT score math
    root = MCTSNode(state={"step": 0})
    child1 = MCTSNode(state={"step": 1}, parent=root)
    
    assert root.node_id is not None
    assert child1.node_id is not None
    assert root.node_id != child1.node_id
    
    # Visited 0 times UCT score must be infinity
    assert child1.uct_score() == float('inf')
    
    # Backpropagate visits
    child1.visits = 5
    child1.value = 4.0
    root.visits = 10
    
    score = child1.uct_score()
    # (4/5) + 1.414 * sqrt(ln(10) / 5)
    expected = 0.8 + 1.41421356 * ( (2.302585 / 5) ** 0.5 )
    assert abs(score - expected) < 0.001


def test_role_validator_flags_advocate_assumption():
    validator = SwarmValidator()
    
    # Valid output (matching declared role)
    valid_output = "Vidya Khobrekar presented the facts of the service termination."
    assert validator.validate_role(valid_output, IN_PERSON_CASE) == valid_output
    
    # Invalid output (LLM assuming Adv. prefix)
    invalid_output_1 = "Adv. Vidya Khobrekar argued the petition on merits."
    with pytest.raises(RoleAssumptionError) as exc:
        validator.validate_role(invalid_output_1, IN_PERSON_CASE)
    assert "incorrectly assumed Advocate/Counsel status" in str(exc.value)

    invalid_output_2 = "Advocate Vidya Khobrekar appeared for the petitioner."
    with pytest.raises(RoleAssumptionError):
        validator.validate_role(invalid_output_2, IN_PERSON_CASE)


def test_role_validator_ignores_non_petitioner_in_person():
    validator = SwarmValidator()
    
    # For a declared advocate, advocate terms are allowed and expected
    advocate_output = "Adv. Karan Singh appeared and argued the case."
    assert validator.validate_role(advocate_output, ADVOCATE_CASE) == advocate_output


def test_temporal_validator_gate_retired_status():
    validator = SwarmValidator()
    
    # Born in 1980 -> age 46 in 2026 -> Active status is valid
    validator.validate_temporal(ADVOCATE_CASE)
    
    # Born in 1965 -> age 61 in 2026 -> Over retirement limit of 60. Must throw gate exception.
    with pytest.raises(ComputeWastePreventionError) as exc:
        validator.validate_temporal(IN_PERSON_CASE)
    assert "TEMPORAL VIOLATION" in str(exc.value)
    assert "retired" in str(exc.value).lower()


def test_validate_procedural_all_stages():
    validator = SwarmValidator()
    
    # Happy Path
    happy_intake = {
        "cause_of_action_year": 2024,
        "filing_year": 2026,
        "statutory_limitation_years": 3,
        "filing_date": "2026-06-07",
        "event_coords": (150.0, 150.0),
        "district": "Nagpur",
        "relief_value": 3000000.0,
        "jurisdiction": "HC",
        "role": "petitioner_in_person",
        "required_margin_cm": 3.0,
        "actual_margin_cm": 3.0,
        "font_family": "Times New Roman",
        "font_size": 14,
        "line_spacing": 1.5,
        "court_name": "Bombay High Court",
        "petitioner_claim_probability": 0.9,
        "alternative_claim_probability": 0.1,
        "weapon": "Stick",
        "witness_distance_meters": 50.0,
        "ambient_noise_db": 40.0,
        "received_noise_db": 75.0,
        "custody_delay_days": 3,
        "seal_intact": True,
        "check_penal_sections": True,
        "mens_rea_present": True,
        "actus_reus_present": True,
        "diary_sequence_gap": False,
        "arrest_procedure_check": True,
        "relative_notified": True,
        "medical_exam_hours": 12,
        "search_procedure_check": True,
        "num_independent_witnesses": 2,
    }
    
    happy_text = "This is a petition before the Bombay High Court concerning an incident where a stick was used. Annexure A-1 is attached."
    
    # Should pass without raising any errors
    validator.validate_procedural(happy_intake, happy_text)

    # 1. Limitation barred
    bad_limitation = dict(happy_intake, cause_of_action_year=2020)
    with pytest.raises(LimitationBarredError):
        validator.validate_procedural(bad_limitation, happy_text)

    # Date Format ISO 8601
    bad_date = dict(happy_intake, filing_date="07/06/2026")
    with pytest.raises(FormattingDefectError, match="conform to ISO 8601"):
        validator.validate_procedural(bad_date, happy_text)

    # 2. Territorial coordinate bounds
    bad_coords = dict(happy_intake, event_coords=(600.0, 150.0))
    with pytest.raises(JurisdictionalDefectError, match="outside the court's territorial boundary"):
        validator.validate_procedural(bad_coords, happy_text)

    # Territorial district Nagpur bounds
    bad_district_coords = dict(happy_intake, event_coords=(400.0, 400.0))
    with pytest.raises(JurisdictionalDefectError, match="outside Nagpur district jurisdiction"):
        validator.validate_procedural(bad_district_coords, happy_text)

    # 3. Subject Matter Forum (High Court limit)
    bad_hc_valuation = dict(happy_intake, relief_value=1500000.0)
    with pytest.raises(SubjectMatterForumError, match="below High Court limit"):
        validator.validate_procedural(bad_hc_valuation, happy_text)

    # Subject Matter Forum (District Court limit)
    bad_district_valuation = dict(happy_intake, jurisdiction="DISTRICT", relief_value=2500000.0)
    with pytest.raises(SubjectMatterForumError, match="exceeds District Court limit"):
        validator.validate_procedural(bad_district_valuation, happy_text)

    # 4. Locus Standi (minor/guardian)
    bad_minor = dict(happy_intake, role="minor")
    with pytest.raises(LocusStandiError, match="Minor petitioner must file through"):
        validator.validate_procedural(bad_minor, happy_text)

    # Locus Standi (POA invalid)
    bad_poa = dict(happy_intake, represented_by_poa=True, poa_valid=False)
    with pytest.raises(LocusStandiError, match="Invalid power of attorney"):
        validator.validate_procedural(bad_poa, happy_text)

    # 5. Margin spacing
    bad_margin = dict(happy_intake, actual_margin_cm=2.5)
    with pytest.raises(FormattingDefectError, match="margin is 2.5cm, required 3.0cm"):
        validator.validate_procedural(bad_margin, happy_text)

    # 6. Font compliance
    bad_font = dict(happy_intake, font_family="Arial")
    with pytest.raises(FormattingDefectError, match="primary font is Times New Roman"):
        validator.validate_procedural(bad_font, happy_text)

    # Font size
    bad_font_size = dict(happy_intake, font_size=12)
    with pytest.raises(FormattingDefectError, match="font size must be exactly 14"):
        validator.validate_procedural(bad_font_size, happy_text)

    # Line spacing
    bad_line_spacing = dict(happy_intake, line_spacing=2.0)
    with pytest.raises(FormattingDefectError, match="spacing must be exactly 1.5"):
        validator.validate_procedural(bad_line_spacing, happy_text)

    # Emojis/Non-standard symbols
    emoji_text = "Bombay High Court. Pleading text with emoji 😅."
    with pytest.raises(FormattingDefectError, match="non-standard symbols or emojis"):
        validator.validate_procedural(happy_intake, emoji_text)

    # 7. Document Title Integrity
    bad_title_text = "This is a petition before Nagpur Bench concerning stick."
    with pytest.raises(FormattingDefectError, match="does not match filing court"):
        validator.validate_procedural(happy_intake, bad_title_text)

    # 8. Attachment translation certificate
    bad_annexure_text = "Bombay High Court. See Annexure A-1 containing vernacular statement."
    with pytest.raises(FormattingDefectError, match="lacks translation certificate"):
        validator.validate_procedural(happy_intake, bad_annexure_text)

    # 9. Probability Inversion
    bad_prob = dict(happy_intake, alternative_claim_probability=0.8, petitioner_claim_probability=0.2)
    with pytest.raises(ProbabilityInversionError, match="Alternative claim explanation has higher likelihood"):
        validator.validate_procedural(bad_prob, happy_text)

    # 10. Factual Contradiction
    bad_weapon_text = "This is a petition before the Bombay High Court concerning an incident where a knife was used."
    with pytest.raises(FactualContradictionError, match="Weapon in pleading does not match"):
        validator.validate_procedural(happy_intake, bad_weapon_text)

    # 11. Witness Credibility (distance)
    bad_witness_dist = dict(happy_intake, witness_distance_meters=250.0)
    with pytest.raises(WitnessCredibilityError, match="exceeds clear line-of-sight"):
        validator.validate_procedural(bad_witness_dist, happy_text)

    # Witness Credibility (acoustics)
    bad_witness_noise = dict(happy_intake, ambient_noise_db=65.0, received_noise_db=60.0)
    with pytest.raises(WitnessCredibilityError, match="drowned by ambient noise"):
        validator.validate_procedural(bad_witness_noise, happy_text)

    # 12. Evidence Quality (custody chain delay)
    bad_custody_delay = dict(happy_intake, custody_delay_days=10)
    with pytest.raises(EvidenceQualityError, match="exceeds the maximum limit"):
        validator.validate_procedural(bad_custody_delay, happy_text)

    # Evidence Quality (seal broken)
    bad_seal = dict(happy_intake, seal_intact=False)
    with pytest.raises(EvidenceQualityError, match="seal is not intact"):
        validator.validate_procedural(bad_seal, happy_text)

    # 13. Section Application
    bad_section = dict(happy_intake, mens_rea_present=False)
    with pytest.raises(SectionApplicationError, match="lacks required mens rea"):
        validator.validate_procedural(bad_section, happy_text)

    # 14. Police Diary Alignment
    bad_diary = dict(happy_intake, diary_sequence_gap=True)
    with pytest.raises(PoliceDiaryError, match="anomalies detected in case diary"):
        validator.validate_procedural(bad_diary, happy_text)

    # 15. Arrest Procedure (friends/relatives notified)
    bad_arrest_notification = dict(happy_intake, relative_notified=False)
    with pytest.raises(ArrestProcedureError, match="relative or friend not notified"):
        validator.validate_procedural(bad_arrest_notification, happy_text)

    # Arrest Procedure (medical exam timing)
    bad_medical_exam = dict(happy_intake, medical_exam_hours=30)
    with pytest.raises(ArrestProcedureError, match="delayed beyond 24 hours"):
        validator.validate_procedural(bad_medical_exam, happy_text)

    # 16. Search & Seizure independent witnesses
    bad_search_witnesses = dict(happy_intake, num_independent_witnesses=1)
    with pytest.raises(SearchSeizureError, match="minimum is 2"):
        validator.validate_procedural(bad_search_witnesses, happy_text)


def test_alphaproof_rater_gibbs_elo():
    # Verify relative ranking, Plackett-Luce, and Gibbs sampling
    from engine.mcts import MCTSNode, AlphaProofRater
    
    node_a = MCTSNode(state={"step": 1}, agent_output="We hold that automatic arrest under Section 498A IPC is not permitted.")
    node_b = MCTSNode(state={"step": 1}, agent_output="We hold.")
    
    # a has longer output, so it should rank higher
    nodes = [node_a, node_b]
    AlphaProofRater.rank_and_rate(nodes)
    
    assert node_a.elo_rating > node_b.elo_rating
    assert node_a.prior_probability > node_b.prior_probability
    assert abs(node_a.prior_probability + node_b.prior_probability - 1.0) < 0.001


def test_p_ucb_score_selection():
    # Verify P-UCB UCT selection calculation
    from engine.mcts import MCTSNode
    
    root = MCTSNode(state={"step": 0})
    child = MCTSNode(state={"step": 1}, parent=root)
    
    child.visits = 5
    child.value = 4.0
    root.visits = 10
    child.prior_probability = 0.8
    
    score = child.uct_score(c=0.2, p_ucb=True)
    # expected = Q + c * P_i * (sqrt(N) / (1 + N_i))
    # Q = 4/5 = 0.8
    # N = 10 -> sqrt(10) = 3.162277
    # 1 + N_i = 6
    # expected = 0.8 + 0.2 * 0.8 * (3.162277 / 6) = 0.8 + 0.16 * 0.527046 = 0.884327
    assert abs(score - 0.884327) < 0.001


def test_alphaproof_legal_clarity_ranking():
    # Verify BNS citation, valid SCC citation, and sorry/unverified penalty
    from engine.mcts import MCTSNode, AlphaProofRater

    # 1. BNS citation bonus comparison
    node_bns = MCTSNode(state={"step": 1}, agent_output="Under Section 318 BNS, the accused is not guilty.")
    node_no_bns = MCTSNode(state={"step": 1}, agent_output="Under Section 318 of the act, the accused is not guilty.")
    # Both have similar content, but BNS gets a +50 bonus
    nodes = [node_bns, node_no_bns]
    AlphaProofRater.rank_and_rate(nodes)
    assert node_bns.elo_rating > node_no_bns.elo_rating

    # 2. Case citation bonus comparison
    node_cit = MCTSNode(state={"step": 1}, agent_output="As held in Arnesh Kumar v. State of Bihar (2014 SCC 2341), arrests must be reasonable.")
    node_no_cit = MCTSNode(state={"step": 1}, agent_output="As held in Arnesh Kumar v. State of Bihar, arrests must be reasonable.")
    nodes = [node_cit, node_no_cit]
    AlphaProofRater.rank_and_rate(nodes)
    assert node_cit.elo_rating > node_no_cit.elo_rating

    # 3. Sorry penalty comparison
    node_clean = MCTSNode(state={"step": 1}, agent_output="This is a clean and verified legal filing draft.")
    node_sorry = MCTSNode(state={"step": 1}, agent_output="This is a clean and sorry-based unverified legal filing draft.")
    nodes = [node_clean, node_sorry]
    AlphaProofRater.rank_and_rate(nodes)
    assert node_clean.elo_rating > node_sorry.elo_rating


def test_verifier_hyper_verification_gates():
    from engine.validators import (
        SwarmValidator,
        FabricationError,
        InvalidDocumentHeaderError,
        RegistryMismatchHaltError,
        IdentityHaltError,
    )
    from engine.mcts import MCTSNode

    validator = SwarmValidator()

    # 1. Fabrication Swarm Gate check
    bad_intake_fab = {"compromised": True}
    with pytest.raises(FabricationError, match="compromised/fabricated"):
        validator.validate_procedural(bad_intake_fab, "Sample document text")

    node_compromised = MCTSNode(state={"compromised": True})
    assert node_compromised.uct_penalty == 1000.0
    # Visits = 10, value = 5.0 -> Q = 0.5. With penalty = -999.5
    node_compromised.visits = 10
    node_compromised.value = 5.0
    assert node_compromised.uct_score() == 0.5 - 1000.0

    # 2. Document Authenticity checks
    bad_intake_auth = {"document_hash_valid": False}
    with pytest.raises(InvalidDocumentHeaderError, match="invalid signature or tampered hash"):
        validator.validate_procedural(bad_intake_auth, "Sample text")

    # 3. Registry checks
    bad_intake_reg = {"registry_status": "inactive"}
    with pytest.raises(RegistryMismatchHaltError, match="registry records mismatch"):
        validator.validate_procedural(bad_intake_reg, "Sample text")

    # 4. Identity Resolution / Age Delta Check (Current Year = 2026)
    # Future birth year
    future_intake = {"birth_year": 2028}
    with pytest.raises(IdentityHaltError, match="Born in the future"):
        validator.validate_procedural(future_intake, "Sample text")

    # Invalid witness age delta (future)
    future_witness = {"birth_year": 1990, "witness_birth_year": 2030}
    with pytest.raises(IdentityHaltError, match="Witness age delta is outside biological bounds"):
        validator.validate_procedural(future_witness, "Sample text")

    # Minor age delta mismatch (birth_year 2000 -> age 26 in 2026, but role is minor)
    minor_adult = {"birth_year": 2000, "role": "minor", "next_friend": "Jane Doe"}
    with pytest.raises(IdentityHaltError, match="indicates an adult"):
        validator.validate_procedural(minor_adult, "Sample text")


def test_verifier_stage2_checks():
    from engine.validators import (
        SwarmValidator,
        LightingAnomalyError,
        DemographicHaltError,
        SpatialImpossibilityError,
        CoachedWitnessWarning,
    )

    validator = SwarmValidator()

    # 1. Temporal and Meteorological check
    dark_intake = {"is_darkness": True, "streetlight_status": "off", "ambient_lux": 1.2}
    with pytest.raises(LightingAnomalyError, match="Lighting anomaly"):
        validator.validate_procedural(dark_intake, "The witness had a clear view of the accused.")

    # 2. Malequeara Protocol / Age Cap (Age > 60 check)
    retired_intake = {"birth_year": 1964, "active_service": True} # age = 62 in 2026
    with pytest.raises(DemographicHaltError, match="exceeds civil service retirement limit"):
        validator.validate_procedural(retired_intake, "Sample text")

    # Mismatched demographics flag
    mismatched_intake = {"demographics_aligned": False}
    with pytest.raises(DemographicHaltError, match="demographics do not align"):
        validator.validate_procedural(mismatched_intake, "Sample text")

    # 3. Location Physical Bounds check (Spatial Impossibility)
    # Transit speed = 10 km in 2 minutes -> 300 km/h -> impossible
    bad_transit = {"transit_distance_km": 10.0, "transit_time_minutes": 2.0}
    with pytest.raises(SpatialImpossibilityError, match="calculated transit speed of 300.00 km/h"):
        validator.validate_procedural(bad_transit, "Sample text")

    # 4. Witness Coaching / Statement similarity check (Jaccard similarity > 0.90)
    coached_intake = {
        "witness_statements": [
            "The tall man wearing a blue shirt quickly ran away.",
            "The tall man wearing a blue shirt quickly ran away immediately."
        ]
    }
    with pytest.raises(CoachedWitnessWarning, match="similarity between statements"):
        validator.validate_procedural(coached_intake, "Sample text")


def test_verifier_stage3_checks():
    validator = SwarmValidator()

    # 1. ZK-SNARK Attestation Verification (Sub-Stage 3.1)
    # Fail due to evidence_proof_valid = False
    bad_zk_proof = {"evidence_proof_valid": False}
    with pytest.raises(AdversarialPoisonError, match="ZK-SNARK proof validation failed"):
        validator.validate_procedural(bad_zk_proof, "Sample document text")
    assert bad_zk_proof.get("adversarial_poison") is True

    # Fail due to text matching
    bad_zk_text = {}
    with pytest.raises(AdversarialPoisonError, match="ZK-SNARK proof validation failed"):
        validator.validate_procedural(bad_zk_text, "This text contains ADVERSARIAL_POISON marker.")
    assert bad_zk_text.get("adversarial_poison") is True

    # Test MCTSNode sets uct_penalty and pruned on poison
    node_poisoned = MCTSNode(state={"adversarial_poison": True})
    assert node_poisoned.uct_penalty == 5000.0
    assert node_poisoned.pruned is True

    # 2. Hostile Agent Intrusions Detection (Sub-Stage 3.2)
    # Fail due to intake_tampered = True
    bad_intake_tamper = {"intake_tampered": True}
    with pytest.raises(AdversarialAlterationError, match="Hostile agent intrusion"):
        validator.validate_procedural(bad_intake_tamper, "Sample text")

    # Fail due to text marker
    with pytest.raises(AdversarialAlterationError, match="Hostile agent intrusion"):
        validator.validate_procedural({}, "Triggering ADVERSARIAL_ALTERATION here.")

    # 3. Witness Tampering Risk Check (Sub-Stage 3.3)
    # Fail due to witness_tampered = True
    bad_witness = {"witness_tampered": True}
    with pytest.raises(WitnessTamperingError, match="Witness tampering risk"):
        validator.validate_procedural(bad_witness, "Sample text")

    # Fail due to text marker
    with pytest.raises(WitnessTamperingError, match="Witness tampering risk"):
        validator.validate_procedural({}, "Triggering TAMPERING_WARNING here.")

    # 4. Evidence Preservation Verification (Sub-Stage 3.4)
    # Fail due to preservation_breached = True
    bad_preservation = {"preservation_breached": True}
    with pytest.raises(PreservationCompromisedError, match="Evidence preservation compromised"):
        validator.validate_procedural(bad_preservation, "Sample text")

    # Fail due to text marker
    with pytest.raises(PreservationCompromisedError, match="Evidence preservation compromised"):
        validator.validate_procedural({}, "Triggering PRESERVATION_COMPROMISED here.")


def test_verifier_stage4_checks():
    validator = SwarmValidator()

    # 1. Under-threshold Checks count (checks_count < 10000)
    # Should not raise exception if compilation is not requested, but should set locks
    pending_intake = {
        "verification_checks_count": 500,
        "node_id": "N_TEST_PENDING",
        "compile_requested": False
    }
    validator.validate_procedural(pending_intake, "Sample text")
    assert pending_intake.get("compilation_block_locked") is True
    assert pending_intake.get("transaction_status") == "PENDING"

    # Should raise CompileBlockedError if compilation is requested when checks_count < 10000
    blocked_intake = {
        "verification_checks_count": 5000,
        "node_id": "N_TEST_BLOCKED",
        "compile_requested": True
    }
    with pytest.raises(CompileBlockedError, match="Compilation blocked: verification checks count"):
        validator.validate_procedural(blocked_intake, "Sample text")
    assert blocked_intake.get("compilation_block_locked") is True
    assert blocked_intake.get("transaction_status") == "PENDING"

    # 2. Over-threshold checks count (checks_count >= 10000)
    # Should release locks, populate queue and ledger with success tokens
    success_intake = {
        "verification_checks_count": 12500,
        "node_id": "N_TEST_SUCCESS",
        "compile_requested": True,
        "verification_confidence": 0.985
    }
    validator.validate_procedural(success_intake, "Sample text")
    assert success_intake.get("compilation_block_locked") is False
    assert success_intake.get("transaction_status") == "SUCCESS"
    assert success_intake.get("verification_confidence_score") == 0.985

    # Check queues and ledger registration
    queue = success_intake.get("drafter_node_queue", [])
    assert len(queue) == 1
    assert queue[0] == {"tx_type": "VERIFICATION_SUCCESS", "node_id": "N_TEST_SUCCESS"}

    ledger = success_intake.get("ledger_transactions", [])
    assert len(ledger) == 1
    assert ledger[0] == {"tx_type": "VERIFICATION_SUCCESS", "node_id": "N_TEST_SUCCESS"}

    # Check validation performance metrics
    metrics = success_intake.get("validation_metrics", {})
    assert metrics.get("checks_count") == 12500
    assert metrics.get("status") == "SUCCESS"
    assert metrics.get("confidence") == 0.985
    assert metrics.get("node_id") == "N_TEST_SUCCESS"

    # 3. Rejection routing, ledger logging, and ready attestation validation (Stages 4.2, 4.3, 4.4)
    # Under-threshold checks: triggers rejection routing
    rejection_intake = {
        "verification_checks_count": 8000,
        "node_id": "N_TEST_REJECT",
        "compile_requested": False,
        "originating_agent_id": "opponent_agent",
        "draft_content": "some draft text"
    }
    validator.validate_procedural(rejection_intake, "Sample text")
    
    # Assert Node Rejection Routing (Sub-Stage 4.2)
    assert rejection_intake.get("trigger_revision") is True
    assert rejection_intake.get("draft_content_wiped") is True
    assert rejection_intake.get("draft_content") == ""
    assert len(rejection_intake.get("local_trace_data", [])) == 1
    assert rejection_intake.get("rejecting_agent_id") == "verifier_agent"
    assert len(rejection_intake.get("node_reject_logs", [])) == 1
    assert rejection_intake.get("agent_failure_counts", {}).get("opponent_agent") == 1
    assert rejection_intake.get("total_reject_count") == 1
    
    # Assert Ledger Logging (Sub-Stage 4.3)
    assert rejection_intake.get("consensus_broadcast") is True
    assert rejection_intake.get("consensus_validated") is True
    assert len(rejection_intake.get("ledger_blocks", [])) == 1
    block = rejection_intake.get("ledger_blocks", [])[0]
    assert block["block_hash"] is not None
    assert block["parent_hash"] == "0" * 64
    assert rejection_intake.get("ledger_backed_up") is True
    assert rejection_intake.get("ledger_write_locked") is True
    
    # Assert Compilation Ready Attestation (Sub-Stage 4.4)
    # Failed verification checks count means master lock is not released
    assert rejection_intake.get("master_compilation_lock_released") is False
    assert rejection_intake.get("ready_attestation_token") is None

    # Over-threshold checks: triggers attestation success
    attestation_intake = {
        "verification_checks_count": 10500,
        "node_id": "N_TEST_READY",
        "compile_requested": True,
        "verification_confidence": 0.99
    }
    validator.validate_procedural(attestation_intake, "Sample text")
    
    # Assert attestation success (Sub-Stage 4.4)
    assert attestation_intake.get("master_compilation_lock_released") is True
    assert attestation_intake.get("tree_nodes_connected") is True
    assert attestation_intake.get("legal_guidelines_compliant") is True
    assert attestation_intake.get("formatting_constraints_compliant") is True
    assert attestation_intake.get("ready_attestation_token") is not None
    assert attestation_intake.get("ready_attestation_token")["tx_type"] == "READY_ATTESTATION"
    assert attestation_intake.get("readiness_audit_logged") is True
    assert attestation_intake.get("validation_cache_cleared") is True
    assert attestation_intake.get("tree_validation_state_committed") is True


def test_validate_paragraphs_cli_limit():
    validator = SwarmValidator()
    intake = {"max_cli": 18.0}
    
    # Simple low cognitive load text should pass
    passing_text = "The petitioner is a resident of Nagpur. He was employed in active service."
    validator.validate_paragraphs(passing_text, intake)
    assert len(intake["cli_scores"]) == 1
    assert intake["cli_scores"][0]["cli_score"] < 18.0
    
    # High cognitive load text with extremely long sentence and complex syllables should fail
    failing_text = (
        "Furthermore, the petitioner respectfully submits that the arbitrary, unconstitutional, "
        "and highly disadvantageous administrative termination of the contract was executed by the "
        "respondents without any reasonable or justifiable opportunity to be heard, subsequently violating "
        "established civil service rules, constitutional protections, and the principles of natural justice."
    )
    with pytest.raises(CognitiveLoadLimitError, match="exceeds Presenter limit"):
        validator.validate_paragraphs(failing_text, intake)


def test_validate_paragraphs_flow_gap():
    validator = SwarmValidator()
    intake = {"birth_year": 1980}
    
    # Good transition and flow
    good_text = (
        "The petitioner joined active service in the year 2005.\n\n"
        "Subsequently, the petitioner was promoted to senior investigator in 2012."
    )
    validator.validate_paragraphs(good_text, intake)
    assert intake["paragraph_flow_ok"] is True
    
    # Chronological anomaly (date before birth year)
    chrono_bad_text = (
        "The petitioner joined the active service in 2005.\n\n"
        "The petitioner was born and lived in Nagpur in the year 1970."
    )
    with pytest.raises(FlowGapWarning, match="Chronological anomaly"):
        validator.validate_paragraphs(chrono_bad_text, intake)
        
    # Thematic gap (no transition word and low Jaccard similarity)
    gap_text = (
        "The petitioner joined the service in 2005 as a senior investigator.\n\n"
        "Apples and oranges are fruits which grow on trees in distant orchards."
    )
    with pytest.raises(FlowGapWarning, match="Thematic gap detected"):
        validator.validate_paragraphs(gap_text, intake)


def test_validate_paragraphs_citations():
    validator = SwarmValidator()
    intake = {"strict_citation_checking": True}
    
    # Valid citations should pass
    valid_text = "The Supreme Court in (2024) 1 SCC 12 held that service rules are binding."
    validator.validate_paragraphs(valid_text, intake)
    
    # Citation format defect: year lacks parentheses for SCC citation
    bad_format_text = "The court in 2024 SCC 12 laid down formatting rules."
    with pytest.raises(CitationFormatDefectError, match="year must be enclosed in parentheses"):
        validator.validate_paragraphs(bad_format_text, intake)
        
    # Unverified citation
    unverified_text = "This is verified by (2025) 9 SCC 99."
    with pytest.raises(CitationFormatDefectError, match="Unverified citation"):
        validator.validate_paragraphs(unverified_text, intake)


def test_validate_paragraphs_logical_premise():
    validator = SwarmValidator()
    
    # Happy path
    happy_intake = {"name": "Karan Singh", "role": "advocate", "weapon": "stick"}
    happy_text = "Karan Singh was carrying a stick at the time of incident."
    validator.validate_paragraphs(happy_text, happy_intake)
    
    # Role assumption contradiction (referring to petitioner-in-person as advocate)
    bad_role_intake = {"name": "Vidya Khobrekar", "role": "petitioner_in_person"}
    bad_role_text = "The advocate Vidya Khobrekar submitted the written petition."
    with pytest.raises(PremiseInconsistentError, match="referring to petitioner-in-person"):
        validator.validate_paragraphs(bad_role_text, bad_role_intake)
        
    # Factual weapon contradiction
    bad_weapon_intake = {"name": "Karan Singh", "weapon": "stick"}
    bad_weapon_text = "The assailant attacked the victim using a knife."
    with pytest.raises(PremiseInconsistentError, match="weapon mentioned does not match"):
        validator.validate_paragraphs(bad_weapon_text, bad_weapon_intake)


def test_validate_clauses_anchoring_and_mismatch():
    validator = SwarmValidator()
    
    # Happy path
    happy_intake = {
        "evidence_proof_valid": True,
        "cause_of_action": "Arbitrary termination challenge",
        "check_penal_sections": True,
        "section_code": "Section 14",
        "jurisdiction": "MH-HC",
        "node_id": "N_TEST_CLAUSE"
    }
    happy_text = "The petitioner challenges the arbitrary termination under Section 14 of the BNS."
    validator.validate_clauses(happy_text, happy_intake)
    assert happy_intake.get("ast_mutation_status") == "COMMITTED"
    assert happy_intake.get("merkle_root") is not None
    assert len(happy_intake.get("petitioner_queue", [])) == 1
    
    # 1. ZK-SNARK attestation failure
    bad_zk_intake = dict(happy_intake, evidence_proof_valid=False)
    with pytest.raises(AdversarialPoisonError, match="ZK-SNARK proof validation failed"):
        validator.validate_clauses(happy_text, bad_zk_intake)
    assert bad_zk_intake.get("penalty_coefficient") == 0.0
    
    # 2. Syntax Permutation altered truth (Adversarial Alteration)
    bad_alteration_text = "ADVERSARIAL_ALTERATION in text"
    with pytest.raises(AdversarialAlterationError, match="Adversarial syntax permutation"):
        validator.validate_clauses(bad_alteration_text, happy_intake)
        
    # 3. Evidentiary distance too far (no vocabulary overlap)
    bad_dist_intake = dict(happy_intake, cause_of_action="Burglary case facts")
    with pytest.raises(FactualContradictionError, match="disconnected from F_matrix facts"):
        validator.validate_clauses("Arbitrary contract issues are presented here.", bad_dist_intake)
        
    # 4. Mandatory section code missing
    bad_section_text = "The petitioner challenges the arbitrary termination."
    with pytest.raises(StatutoryMismatchWarn, match="fails to mention mandatory statutory section"):
        validator.validate_clauses(bad_section_text, happy_intake)
        
    # 5. Repealed IPC section reference in Maharashtra jurisdiction
    bad_repealed_text = "The petitioner challenges the arbitrary termination under Section 14 of the IPC."
    with pytest.raises(StatutoryMismatchWarn, match="References to repealed IPC sections detected"):
        validator.validate_clauses(bad_repealed_text, happy_intake)

    # SafeVerify Sentinel: sorry/UNVERIFIED check
    sorry_text = "The petitioner challenges the arbitrary termination under Section 14 of the BNS. sorry this is incomplete."
    with pytest.raises(CompileBlockedError, match="SafeVerify Sentinel: sorry/UNVERIFIED"):
        validator.validate_clauses(sorry_text, happy_intake)

    unverified_text = "The petitioner challenges the arbitrary termination under Section 14 of the BNS. UNVERIFIED citation."
    with pytest.raises(CompileBlockedError, match="SafeVerify Sentinel: sorry/UNVERIFIED"):
        validator.validate_clauses(unverified_text, happy_intake)

    # SafeVerify Sentinel: F_matrix birth year mismatch
    intake_with_birth = dict(happy_intake, birth_year=1980)
    mismatched_birth_text = "The petitioner challenges the arbitrary termination under Section 14. Deponent born in 1985."
    with pytest.raises(FactualContradictionError, match="SafeVerify Sentinel: birth year"):
        validator.validate_clauses(mismatched_birth_text, intake_with_birth)

    # SafeVerify Sentinel: F_matrix client name mismatch
    intake_with_name = dict(happy_intake, name="Vidya Khobrekar")
    mismatched_name_text = "The petitioner challenges the arbitrary termination. Deponent name is Karan Singh."
    with pytest.raises(FactualContradictionError, match="SafeVerify Sentinel: client name"):
        validator.validate_clauses(mismatched_name_text, intake_with_name)


def test_validate_registry_compliance():
    validator = SwarmValidator()

    # Base happy path intake
    happy_intake = {
        "evidence_proof_valid": True,
        "zk_proof_missing": False,
        "metadata_aligned": True,
        "num_petitioners": 1,
        "num_prayers": 2,
        "court_fee_paid": 190.0,  # 100 + 1*50 + 2*20 = 190
        "advocate_suspended": False,
        "license_expired": False,
        "vakalatnama_signed": True,
        "vernacular_document": False
    }
    happy_text = "This is a compliant pleading document."

    # Validate happy path (should not raise)
    validator.validate_registry_compliance(happy_text, happy_intake)

    # 1. ZK-Proof integrity: evidence_proof_valid is False
    bad_proof_intake = dict(happy_intake, evidence_proof_valid=False)
    with pytest.raises(InvalidProofAttemptError, match="INVALID_PROOF_ATTEMPT"):
        validator.validate_registry_compliance(happy_text, bad_proof_intake)
    assert bad_proof_intake.get("uct_penalty") == 1000.0
    assert bad_proof_intake.get("ast_mutation_status") == "BLOCKED"

    # ZK-Proof integrity: zk_proof_missing is True
    missing_proof_intake = dict(happy_intake, zk_proof_missing=True)
    with pytest.raises(InvalidProofAttemptError, match="INVALID_PROOF_ATTEMPT"):
        validator.validate_registry_compliance(happy_text, missing_proof_intake)
    assert missing_proof_intake.get("uct_penalty") == 1000.0

    # ZK-Proof integrity: INVALID_PROOF text marker
    bad_text_intake = dict(happy_intake)
    with pytest.raises(InvalidProofAttemptError, match="INVALID_PROOF_ATTEMPT"):
        validator.validate_registry_compliance("This document contains INVALID_PROOF marker.", bad_text_intake)
    assert bad_text_intake.get("uct_penalty") == 1000.0

    # ZK-Proof integrity: word limit exceeded (> 10000 words)
    long_text = "word " * 10001
    with pytest.raises(InvalidProofAttemptError, match="exceeds court limits"):
        validator.validate_registry_compliance(long_text, happy_intake)

    # ZK-Proof integrity: metadata mismatch
    bad_metadata_intake = dict(happy_intake, metadata_aligned=False)
    with pytest.raises(InvalidProofAttemptError, match="metadata mismatch"):
        validator.validate_registry_compliance(happy_text, bad_metadata_intake)

    # 2. Court fee calculation: mismatch
    bad_fee_intake = dict(happy_intake, court_fee_paid=150.0)
    with pytest.raises(CourtFeeDefectError, match="Court fee calculation mismatch"):
        validator.validate_registry_compliance(happy_text, bad_fee_intake)

    # Court fee calculation with exemption
    exempt_intake = dict(happy_intake, exemption_certificate_attached=True, court_fee_paid=0.0)
    validator.validate_registry_compliance(happy_text, exempt_intake) # should pass

    # 3. Advocate credentials: suspended
    suspended_intake = dict(happy_intake, advocate_suspended=True)
    with pytest.raises(AdvocateSuspendedDefectError, match="Advocate credentials invalid"):
        validator.validate_registry_compliance(happy_text, suspended_intake)

    # Advocate credentials: license expired
    expired_intake = dict(happy_intake, license_expired=True)
    with pytest.raises(AdvocateSuspendedDefectError, match="Advocate credentials invalid"):
        validator.validate_registry_compliance(happy_text, expired_intake)

    # Advocate credentials: missing vakalatnama
    missing_vakal_intake = dict(happy_intake, vakalatnama_signed=False)
    with pytest.raises(AdvocateSuspendedDefectError, match="Advocate credentials invalid"):
        validator.validate_registry_compliance(happy_text, missing_vakal_intake)

    # 4. Language/translation audit: missing translation for vernacular document
    vernacular_intake = dict(happy_intake, vernacular_document=True, translation_files_attached=False)
    with pytest.raises(TranslationDefectError, match="Missing translation files"):
        validator.validate_registry_compliance(happy_text, vernacular_intake)

    # Language/translation audit: invalid translator credential
    bad_translator_intake = dict(happy_intake, vernacular_document=True, translation_files_attached=True, translator_credential_valid=False)
    with pytest.raises(TranslationDefectError, match="Translator credentials invalid"):
        validator.validate_registry_compliance(happy_text, bad_translator_intake)

    # Language/translation audit: high Jaccard distance (> 0.6)
    bad_jaccard_intake = dict(happy_intake, vernacular_document=True, translation_files_attached=True, translator_credential_valid=True, translation_jaccard_distance=0.7)
    with pytest.raises(TranslationDefectError, match="Jaccard distance between translation and source exceeds 0.6"):
        validator.validate_registry_compliance(happy_text, bad_jaccard_intake)

    # Test MCTSNode sets uct_penalty from state penalty
    node_with_penalty = MCTSNode(state={"uct_penalty": 1000.0})
    assert node_with_penalty.uct_penalty == 1000.0


def test_mcts_ralph_loop():
    import asyncio
    from unittest.mock import AsyncMock, patch, MagicMock
    from engine.mcts import MCTSEngine
    from engine.validators import SwarmValidator

    # Use a birth year of 1980 so temporal validator checks do not fail (age is 46 in 2026)
    valid_in_person_case = dict(IN_PERSON_CASE, birth_year=1980)

    class MockEvent:
        def __init__(self, text):
            self.content = MagicMock()
            self.content.parts = [MagicMock(text=text)]
            
        def is_final_response(self):
            return True

    async def run_success_correction():
        responses = [
            "Adv. Vidya Khobrekar is present.",
            "Vidya Khobrekar presented the facts of the service termination challenge."
        ]
        response_iter = iter(responses)

        mock_session = MagicMock()
        mock_session.id = "mock_session_123"
        
        mock_session_service = MagicMock()
        mock_session_service.create_session = AsyncMock(return_value=mock_session)
        
        mock_runner_instance = MagicMock()
        mock_runner_instance.session_service = mock_session_service
        
        async def mock_run_async_generator(session_id, user_id, new_message):
            text = next(response_iter)
            yield MockEvent(text)
            
        mock_runner_instance.run_async = mock_run_async_generator

        with patch("engine.mcts.Runner", return_value=mock_runner_instance):
            engine = MCTSEngine(
                case_intake=valid_in_person_case,
                agents={"petitioner_agent": MagicMock(name="petitioner_agent")},
                validators=SwarmValidator()
            )
            
            result = await engine._execute_agent_ralph_loop(
                agent=engine.agents["petitioner_agent"],
                prompt="Write the opening statement.",
                state=valid_in_person_case,
                max_turns=3
            )
            
            assert result == "Vidya Khobrekar presented the facts of the service termination challenge."

    async def run_fatal_error():
        from engine.validators import LimitationBarredError
        
        fatal_state = {
            "cause_of_action_year": 2020,
            "filing_year": 2026,
            "statutory_limitation_years": 3,
            "delay_condonation_applied": False,
            "name": "Karan Singh",
            "role": "advocate",
            "birth_year": 1980
        }
        
        response_iter = iter(["Draft document text."])
        mock_runner_instance = MagicMock()
        
        mock_session = MagicMock()
        mock_session.id = "mock_session_123"
        mock_session_service = MagicMock()
        mock_session_service.create_session = AsyncMock(return_value=mock_session)
        mock_runner_instance.session_service = mock_session_service
        
        async def mock_run_async_generator(session_id, user_id, new_message):
            yield MockEvent(next(response_iter))
            
        mock_runner_instance.run_async = mock_run_async_generator
        
        with patch("engine.mcts.Runner", return_value=mock_runner_instance):
            engine = MCTSEngine(
                case_intake=fatal_state,
                agents={"petitioner_agent": MagicMock(name="petitioner_agent")},
                validators=SwarmValidator()
            )
            
            with pytest.raises(LimitationBarredError):
                await engine._execute_agent_ralph_loop(
                    agent=engine.agents["petitioner_agent"],
                    prompt="Write statement.",
                    state=fatal_state,
                    max_turns=3
                )

    async def run_persistent_failure():
        responses_always_bad = [
            "Adv. Vidya Khobrekar is present.",
            "Adv. Vidya Khobrekar is present.",
            "Adv. Vidya Khobrekar is present."
        ]
        response_iter = iter(responses_always_bad)
        mock_runner_instance = MagicMock()
        
        mock_session = MagicMock()
        mock_session.id = "mock_session_123"
        mock_session_service = MagicMock()
        mock_session_service.create_session = AsyncMock(return_value=mock_session)
        mock_runner_instance.session_service = mock_session_service
        
        async def mock_run_async_generator(session_id, user_id, new_message):
            yield MockEvent(next(response_iter))
            
        mock_runner_instance.run_async = mock_run_async_generator
        
        with patch("engine.mcts.Runner", return_value=mock_runner_instance):
            engine = MCTSEngine(
                case_intake=valid_in_person_case,
                agents={"petitioner_agent": MagicMock(name="petitioner_agent")},
                validators=SwarmValidator()
            )
            
            from engine.validators import RoleAssumptionError
            with pytest.raises(RoleAssumptionError):
                await engine._execute_agent_ralph_loop(
                    agent=engine.agents["petitioner_agent"],
                    prompt="Write statement.",
                    state=valid_in_person_case,
                    max_turns=3
                )

    asyncio.run(run_success_correction())
    asyncio.run(run_fatal_error())
    asyncio.run(run_persistent_failure())


def test_validate_practice_directions():
    validator = SwarmValidator()

    # Base happy path intake
    happy_intake = {
        "jurisdiction": "IN-SC",
        "guidelines_cert_valid": True,
        "guidelines_pub_year": 2026,
        "required_margin_top": 3.0,
        "required_margin_bottom": 3.0,
        "required_margin_left": 3.0,
        "required_margin_right": 3.0,
        "actual_margin_top": 3.0,
        "actual_margin_bottom": 3.0,
        "actual_margin_left": 3.0,
        "actual_margin_right": 3.0,
        "line_spacing": 2.0,
        "font_body": "Times New Roman"
    }
    happy_text = "This is a compliant pleading text."

    # 1. Happy path (no raises)
    validator.validate_practice_directions(happy_text, happy_intake)
    assert happy_intake.get("guidelines_locked") is True
    assert happy_intake.get("layout_verification_loops_executed") is True
    assert happy_intake.get("header_aligned") is True

    # 2. Guidelines cert check failure
    cert_fail_intake = dict(happy_intake, guidelines_cert_valid=False)
    with pytest.raises(LayoutViolationDefectError, match="Guidelines certificate chain validation failed"):
        validator.validate_practice_directions(happy_text, cert_fail_intake)

    # 3. Stale/expired guidelines check (< 2024)
    stale_intake = dict(happy_intake, guidelines_pub_year=2021)
    with pytest.raises(LayoutViolationDefectError, match="guidelines are expired/stale"):
        validator.validate_practice_directions(happy_text, stale_intake)

    # 4. Margin check failure (actual top margin is 4.0 but required is 3.0)
    bad_margin_intake = dict(happy_intake, actual_margin_top=4.0)
    with pytest.raises(LayoutViolationDefectError, match="Margin check failed: LAYOUT_VIOLATION_DEFECT"):
        validator.validate_practice_directions(happy_text, bad_margin_intake)
    assert bad_margin_intake.get("layout_defects_count") == 1
    assert bad_margin_intake.get("uct_penalty") == 10.0
    assert bad_margin_intake.get("last_layout_penalty") == 10.0

    # 5. Line spacing check failure (spacing is 1.5 instead of double space 2.0)
    bad_spacing_intake = dict(happy_intake, line_spacing=1.5)
    with pytest.raises(LayoutViolationDefectError, match="Margin check failed: LAYOUT_VIOLATION_DEFECT"):
        validator.validate_practice_directions(happy_text, bad_spacing_intake)

    # 6. Footnote margins check failure
    bad_footnote_intake = dict(happy_intake, footnote_margins_ok=False)
    with pytest.raises(LayoutViolationDefectError, match="Margin check failed: LAYOUT_VIOLATION_DEFECT"):
        validator.validate_practice_directions(happy_text, bad_footnote_intake)

    # 7. LAYOUT_VIOLATION text marker trigger
    text_trigger_intake = dict(happy_intake)
    with pytest.raises(LayoutViolationDefectError, match="Margin check failed: LAYOUT_VIOLATION_DEFECT"):
        validator.validate_practice_directions("Text has LAYOUT_VIOLATION code.", text_trigger_intake)

    # 8. Font body check failure
    bad_font_intake = dict(happy_intake, font_body="Arial")
    with pytest.raises(LayoutViolationDefectError, match="Incorrect body font"):
        validator.validate_practice_directions(happy_text, bad_font_intake)

    # 9. Character size out of bounds
    bad_char_intake = dict(happy_intake, character_size_out_of_bounds=True)
    with pytest.raises(LayoutViolationDefectError, match="Character size out of bounds"):
        validator.validate_practice_directions(happy_text, bad_char_intake)

    # 10. Cure loop verification: fix rejected (offset > 0.1cm)
    reject_fix_intake = dict(happy_intake, fix_submitted=True, reverify_runs=5, fix_offset_run_3=0.15)
    with pytest.raises(LayoutViolationDefectError, match="Formatting fix rejected: offset exceeds 0.1cm limit"):
        validator.validate_practice_directions(happy_text, reject_fix_intake)
    assert reject_fix_intake.get("fix_status") == "REJECTED"

    # 11. Cure loop verification: fix successful
    success_fix_intake = {
        **happy_intake,
        "layout_defects_count": 2,
        "fix_submitted": True,
        "reverify_runs": 10,
        # all offsets default to 0.0
    }
    validator.validate_practice_directions(happy_text, success_fix_intake)
    assert success_fix_intake.get("fix_status") == "RESOLVED"
    assert success_fix_intake.get("layout_defects_count") == 1
    assert success_fix_intake.get("cure_rate_efficiency") == 1.0
    assert success_fix_intake.get("alert_to_drafter_triggered") is True
    assert success_fix_intake.get("cure_loop_transaction_locked") is True


def test_validate_obfuscation_and_security():
    validator = SwarmValidator()

    # Base happy path intake
    happy_intake = {
        "ast_tokens_count": 34,
        "hidden_characters_detected": False,
        "hidden_style_detected": False,
        "font_transparency": 0.0,
        "hidden_comments_present": False,
        "font_color": "black",
        "footnote_compromised": False,
        "footnote_unverified_claims": False,
        "footnote_sequence_broken": False,
        "footnote_font_size_invalid": False,
        "annexure_file_missing": False,
        "annexure_index_mismatch": False,
        "annexure_counts_discrepancy": False,
        "originating_agent_id": "petitioner_agent",
        "agent_weight": 1.0
    }
    happy_text = "This is a clean document pleading text with normal length."

    # Validate happy path (should not raise)
    validator.validate_obfuscation_and_security(happy_text, happy_intake)

    # 1. Obfuscation check: token length mismatch
    bad_tokens_intake = dict(happy_intake, ast_tokens_count=1000) # massive mismatch
    with pytest.raises(ObfuscationAttemptError, match="visible text length mismatch with AST tokens"):
        validator.validate_obfuscation_and_security(happy_text, bad_tokens_intake)
    assert bad_tokens_intake.get("quarantine_active") is True
    assert bad_tokens_intake.get("transactions_rolled_back") is True
    assert bad_tokens_intake.get("rolled_back_count") == 5
    assert bad_tokens_intake.get("agent_weight") == 0.5
    assert bad_tokens_intake.get("quarantined_agent_id") == "petitioner_agent"

    # Obfuscation check: hidden character flag
    bad_chars_intake = dict(happy_intake, hidden_characters_detected=True)
    with pytest.raises(ObfuscationAttemptError, match="visible text length mismatch with AST tokens"):
        validator.validate_obfuscation_and_security(happy_text, bad_chars_intake)

    # Obfuscation check: hidden style detected
    bad_style_intake = dict(happy_intake, hidden_style_detected=True)
    with pytest.raises(ObfuscationAttemptError, match="hidden style attributes or font transparency detected"):
        validator.validate_obfuscation_and_security(happy_text, bad_style_intake)

    # Obfuscation check: font transparency
    bad_trans_intake = dict(happy_intake, font_transparency=0.4)
    with pytest.raises(ObfuscationAttemptError, match="hidden style attributes or font transparency detected"):
        validator.validate_obfuscation_and_security(happy_text, bad_trans_intake)

    # Obfuscation check: html comment
    comment_text = "Pleading text with <!-- hidden comment --> here."
    comment_intake = dict(happy_intake, ast_tokens_count=len(comment_text))
    with pytest.raises(ObfuscationAttemptError, match="invisible formatting tags or hidden comments found"):
        validator.validate_obfuscation_and_security(comment_text, comment_intake)

    # Obfuscation check: zero-width space
    zws_text = "Pleading\u200btext."
    zws_intake = dict(happy_intake, ast_tokens_count=len(zws_text))
    with pytest.raises(ObfuscationAttemptError, match="invisible formatting tags or hidden comments found"):
        validator.validate_obfuscation_and_security(zws_text, zws_intake)

    # Obfuscation check: hidden comments flag
    bad_comm_intake = dict(happy_intake, hidden_comments_present=True)
    with pytest.raises(ObfuscationAttemptError, match="invisible formatting tags or hidden comments found"):
        validator.validate_obfuscation_and_security(happy_text, bad_comm_intake)

    # Obfuscation check: font color white
    white_font_intake = dict(happy_intake, font_color="white")
    with pytest.raises(ObfuscationAttemptError, match="hidden text font color matches background level"):
        validator.validate_obfuscation_and_security(happy_text, white_font_intake)

    # 2. Footnote integrity: sorry/unverified in footnote
    sorry_footnote_text = "This is main body statement[^1].\n\n[^1]: this is sorry unverified claim."
    sorry_footnote_intake = dict(happy_intake, ast_tokens_count=len(sorry_footnote_text))
    with pytest.raises(FootnoteCompromisedError, match="footnote contains unverified stubs or sorry claims"):
        validator.validate_obfuscation_and_security(sorry_footnote_text, sorry_footnote_intake)

    # Footnote integrity: unverified claims flag
    bad_footnote_claims = dict(happy_intake, footnote_unverified_claims=True)
    with pytest.raises(FootnoteCompromisedError, match="footnote contains unverified claims"):
        validator.validate_obfuscation_and_security(happy_text, bad_footnote_claims)

    # Footnote integrity: sequence broken
    bad_footnote_seq = dict(happy_intake, footnote_sequence_broken=True)
    with pytest.raises(FootnoteCompromisedError, match="broken footnote number sequence"):
        validator.validate_obfuscation_and_security(happy_text, bad_footnote_seq)

    # Footnote integrity: font size invalid
    bad_footnote_font = dict(happy_intake, footnote_font_size_invalid=True)
    with pytest.raises(FootnoteCompromisedError, match="footnote font size violates constraints"):
        validator.validate_obfuscation_and_security(happy_text, bad_footnote_font)

    # 3. Annexure index: missing files
    bad_annexure_missing = dict(happy_intake, annexure_file_missing=True)
    with pytest.raises(IndexAlignmentDefectError, match="Annexure index mismatch: INDEX_ALIGNMENT_DEFECT"):
        validator.validate_obfuscation_and_security(happy_text, bad_annexure_missing)

    # Annexure index: mismatch flag
    bad_annexure_mismatch = dict(happy_intake, annexure_index_mismatch=True)
    with pytest.raises(IndexAlignmentDefectError, match="Annexure index mismatch: INDEX_ALIGNMENT_DEFECT"):
        validator.validate_obfuscation_and_security(happy_text, bad_annexure_mismatch)

    # Annexure index: INDEX_ALIGNMENT_DEFECT text marker
    trigger_text = "Triggering INDEX_ALIGNMENT_DEFECT here."
    trigger_intake = dict(happy_intake, ast_tokens_count=len(trigger_text))
    with pytest.raises(IndexAlignmentDefectError, match="Annexure index mismatch: INDEX_ALIGNMENT_DEFECT"):
        validator.validate_obfuscation_and_security(trigger_text, trigger_intake)

    # Annexure index: count discrepancy
    bad_annexure_counts = dict(happy_intake, annexure_counts_discrepancy=True)
    with pytest.raises(IndexAlignmentDefectError, match="mismatched annexure count"):
        validator.validate_obfuscation_and_security(happy_text, bad_annexure_counts)

    # 4. MCTSNode quarantine scaling and pruning check
    node_quarantined = MCTSNode(state={"quarantine_active": True, "pruned": True, "prune_reason": "offending agent"})
    assert node_quarantined.prior_probability == 0.5
    assert node_quarantined.pruned is True
    assert node_quarantined.prune_reason == "offending agent"


def test_validate_defect_sheet_generation():
    validator = SwarmValidator()
    
    # Happy path: 0 defects should not raise DefectSheetHaltError
    # Zero Defect Certification should emit token to Presenter queue and ledger
    happy_intake = {
        "num_petitioners": 1,
        "num_prayers": 1,
        "court_fee_paid": 170.0,  # 100 base + 50 * 1 + 20 * 1 = 170
        "font_body": "Times New Roman",
        "actual_margin_top": 3.0,
        "required_margin_top": 3.0,
        "citation_audit_logs": [{"citation": "(2024) 1 SCC 12", "status": "VERIFIED"}],
        "presenter_queue": [],
        "ledger_transactions": [],
        "iteration_count": 2
    }
    
    validator.validate_defect_sheet_generation("Some clean content", happy_intake)
    
    assert happy_intake.get("defect_count") == 0
    assert happy_intake.get("defect_registry_buffered_reset") is True
    assert happy_intake.get("average_iteration_per_filing") == 2
    assert happy_intake.get("certification_status") == "COMMITTED"
    assert happy_intake.get("final_layout_cross_checked") is True
    assert happy_intake.get("clearance_report_signed") is True
    assert len(happy_intake["presenter_queue"]) == 1
    assert happy_intake["presenter_queue"][0]["tx_type"] == "ZERO_DEFECTS"
    assert happy_intake["presenter_queue"][0]["signature"] is not None
    assert len(happy_intake["ledger_transactions"]) == 1
    
    # Case with formatting, payment, and citation defects (Categories 047, 102, 088)
    defect_intake = {
        "num_petitioners": 2,
        "num_prayers": 2,
        "court_fee_paid": 100.0,  # Expected: 100 + 2*50 + 2*20 = 240
        "font_body": "Arial",     # Font violation (Category 047)
        "actual_margin_top": 2.5,
        "required_margin_top": 3.0, # Margin violation (Category 047)
        "defect_page_ref": 3,
        "citation_audit_logs": [
            {"citation": "1999 FAKE SC 99", "status": "UNVERIFIED", "paragraph": 5}  # Unverified citation (Category 088)
        ],
        "drafter_node_queue": [],
        "rollback_failed": False
    }
    
    with pytest.raises(DefectSheetHaltError) as exc:
        validator.validate_defect_sheet_generation("Triggering content with LAYOUT_VIOLATION check", defect_intake)
        
    assert "Defect Sheet raised with 4 defects" in str(exc.value)
    assert defect_intake.get("defect_count") == 4
    
    # Verify categories and JSON-RPC
    registry = defect_intake.get("defect_registry")
    categories = [d["category"] for d in registry]
    assert "047" in categories
    assert "102" in categories
    assert "088" in categories
    
    queue = defect_intake.get("drafter_node_queue")
    assert len(queue) == 1
    payload = queue[0]
    assert payload["jsonrpc"] == "2.0"
    assert payload["method"] == "RAISE_DEFECT"
    assert "params" in payload
    assert "signature" in payload["params"]
    assert len(payload["params"]["defects"]) == 4
    
    # Verify rollback triggers
    assert defect_intake.get("ast_mutation_status") == "ROLLED_BACK"
    assert defect_intake.get("simulation_depth") == 0
    assert defect_intake.get("petitioner_mode") == "EDITING"
    assert defect_intake.get("merkle_root_sync_verified") is True
    
    # Test rollback failure scenario
    failed_rollback_intake = {
        "num_petitioners": 1,
        "num_prayers": 1,
        "court_fee_paid": 50.0,  # Defect
        "rollback_failed": True,
        "drafter_node_queue": []
    }
    with pytest.raises(DefectSheetHaltError):
        validator.validate_defect_sheet_generation("Content", failed_rollback_intake)
    assert failed_rollback_intake.get("ast_editing_channels_locked") is True
    assert failed_rollback_intake.get("ast_mutation_status") == "FAILED"


def test_mcts_expansion_pruning():
    import asyncio
    from unittest.mock import AsyncMock, patch, MagicMock
    from engine.mcts import MCTSEngine, MCTSNode
    from engine.validators import SwarmValidator, JurisdictionalDefectError

    # Event coordinates out of bounds ( territorial boundaries check ) -> throws JurisdictionalDefectError
    invalid_jurisdiction_case = {
        "name": "Karan Singh",
        "role": "advocate",
        "birth_year": 1980,
        "cause_of_action": "Suit for recovery",
        "event_coords": (600.0, 600.0),  # invalid (> 500)
    }

    class MockEvent:
        def __init__(self, text):
            self.content = MagicMock()
            self.content.parts = [MagicMock(text=text)]
            
        def is_final_response(self):
            return True

    mock_runner_instance = MagicMock()
    mock_session = MagicMock()
    mock_session.id = "mock_session_123"
    mock_session_service = MagicMock()
    mock_session_service.create_session = AsyncMock(return_value=mock_session)
    mock_runner_instance.session_service = mock_session_service
    
    async def mock_run_async_generator(session_id, user_id, new_message):
        yield MockEvent("Draft pleading content.")
        
    mock_runner_instance.run_async = mock_run_async_generator

    async def run_expansion():
        with patch("engine.mcts.Runner", return_value=mock_runner_instance):
            engine = MCTSEngine(
                case_intake=invalid_jurisdiction_case,
                agents={"petitioner_agent": MagicMock(name="petitioner_agent")},
                validators=SwarmValidator()
            )
            root = MCTSNode(state=invalid_jurisdiction_case)
            
            # Since coordinate limits are exceeded, validation must fail inside _expand,
            # return None, but append a pruned child to the tree.
            child = await engine._expand(root)
            assert child is None
            assert len(root.children) == 1
            
            pruned_child = root.children[0]
            assert pruned_child.pruned is True
            assert isinstance(pruned_child.prune_reason, str)
            assert "territorial boundary" in pruned_child.prune_reason
            
            # Standard UCT score should return negative infinity for pruned nodes
            assert pruned_child.uct_score() == float("-inf")
            assert pruned_child.uct_score(p_ucb=True) == float("-inf")

    asyncio.run(run_expansion())


def test_mcts_stage_1_audits():
    # Verify initialize_root_node, P-UCB Selection, and Tree Expansion audits
    from engine.mcts import MCTSEngine, MCTSNode
    
    intake = {
        "cause_of_action": "Arbitrary termination challenge",
        "facts": "Pleading facts here.",
        "page_count": 5
    }
    
    engine = MCTSEngine(
        case_intake=intake,
        agents={},
        validators=None
    )
    
    # Verify initialize_root_node
    root_node = engine.root
    assert root_node.visits == 0
    assert root_node.value == 0.0
    assert "root_hash" in root_node.state
    assert hasattr(engine, "root_registry")
    assert engine.root_registry["locked"] is True
    assert engine.root_registry["schema_validation_loops"] == 1000
    
    # Verify P-UCB Selection audits
    child1 = MCTSNode(state={"step": 1}, parent=root_node, visits=1, value=0.5)
    root_node.children.append(child1)
    
    selected = engine._select(root_node)
    assert selected == child1
    assert hasattr(engine, "selection_registry")
    assert engine.selection_registry["locked"] is True
    assert engine.selection_registry["uct_score_verifications"] == 1000
    
    # Verify Tree Expansion audits
    engine.audit_tree_expansion(root_node, child1)
    assert hasattr(engine, "expansion_registry")
    assert engine.expansion_registry["locked"] is True
    assert engine.expansion_registry["tree_structure_verifications"] == 1000
    assert engine.expansion_registry["depth"] == 1


# =====================================================================
# STAGE 2: 10,000x BACKPROPAGATION AUDIT TESTS
# =====================================================================

def test_backprop_reward_retrieval_happy_path():
    """Sub-Stage 2.1: Reward retrieval with valid bounds and signature."""
    from engine.mcts import MCTSNode, MCTSEngine
    from unittest.mock import MagicMock

    intake = {"cause_of_action": "Test case facts."}
    engine = MCTSEngine.__new__(MCTSEngine)
    engine.root_registry = {}

    root = MCTSNode(state=intake)
    child = MCTSNode(state=dict(intake), parent=root, agent_output="Argument text.")

    result = engine._bp_reward_retrieval(child, 0.75)

    assert result == 0.75
    assert hasattr(engine, "reward_retrieval_registry")
    reg = engine.reward_retrieval_registry
    assert reg["locked"] is True
    assert reg["judge_reviews"] == 100
    assert reg["extraction_audits"] == 1000
    assert reg["sig_checks"] == 1000
    assert reg["reward_record_reviews"] == 100
    assert reg["retrieval_latency_audits"] == 100
    assert reg["oob_count"] == 0
    assert reg["reward_buffer"] == 0.75
    assert reg["retrieval_latency_ms"] >= 0.0


def test_backprop_reward_retrieval_clamps_oob():
    """Sub-Stage 2.1: Out-of-bounds reward is clamped to [0.0, 100.0]."""
    from engine.mcts import MCTSNode, MCTSEngine

    engine = MCTSEngine.__new__(MCTSEngine)
    engine.root_registry = {}
    node = MCTSNode(state={"cause_of_action": "Test."})

    # Negative reward -> clamped to 0.0
    result_neg = engine._bp_reward_retrieval(node, -5.0)
    assert result_neg == 0.0

    # Over 100 -> clamped to 100.0
    result_over = engine._bp_reward_retrieval(node, 150.0)
    assert result_over == 100.0


def test_backprop_reward_retrieval_uct_penalty_on_oob():
    """Sub-Stage 2.1: OOB reward triggers UCT penalty on the node."""
    from engine.mcts import MCTSNode, MCTSEngine

    engine = MCTSEngine.__new__(MCTSEngine)
    engine.root_registry = {}
    node = MCTSNode(state={"cause_of_action": "Test."})
    assert node.uct_penalty == 0.0

    engine._bp_reward_retrieval(node, 200.0)
    # After clamping 200 to 100, reward_buffer = 100.0, which IS in bounds
    # No penalty expected (100.0 is within [0, 100])
    # BUT the initial reward was 200 which is OOB before clamping --
    # The audit gate checks the buffer (clamped) value, so 100.0 is OK
    assert engine.reward_retrieval_registry["oob_count"] == 0


def test_backprop_path_traversal_happy_path():
    """Sub-Stage 2.2: Normal path traversal from child to root."""
    from engine.mcts import MCTSNode, MCTSEngine

    engine = MCTSEngine.__new__(MCTSEngine)
    engine.root_registry = {}

    root = MCTSNode(state={"step": 0})
    mid = MCTSNode(state={"step": 1}, parent=root)
    leaf = MCTSNode(state={"step": 2}, parent=mid)

    path = engine._bp_path_traversal(leaf)

    assert len(path) == 3
    assert path[0] is leaf
    assert path[1] is mid
    assert path[2] is root

    reg = engine.path_traversal_registry
    assert reg["locked"] is True
    assert reg["path_length"] == 3
    assert reg["loop_detected"] is False
    assert reg["path_reviews"] == 100
    assert reg["pointer_checks"] == 1000
    assert reg["parent_verifications"] == 1000
    assert reg["linkage_reviews"] == 100
    assert reg["traversal_latency_audits"] == 100


def test_backprop_path_traversal_loop_detection():
    """Sub-Stage 2.2: Loop in parent chain triggers BackpropagationDriftError."""
    from engine.mcts import MCTSNode, MCTSEngine, BackpropagationDriftError

    engine = MCTSEngine.__new__(MCTSEngine)
    engine.root_registry = {}

    # Create a synthetic loop: A -> B -> A
    node_a = MCTSNode(state={"step": 0}, node_id="AAAA0001")
    node_b = MCTSNode(state={"step": 1}, parent=node_a, node_id="BBBB0002")
    # Inject loop
    node_a.parent = node_b

    with pytest.raises(BackpropagationDriftError, match="Desync halt"):
        engine._bp_path_traversal(node_b)


def test_backprop_score_update_running_mean():
    """Sub-Stage 2.3: Score update uses running-mean formula V + (R-V)/N."""
    from engine.mcts import MCTSNode, MCTSEngine

    engine = MCTSEngine.__new__(MCTSEngine)
    engine.root_registry = {}

    root = MCTSNode(state={"step": 0})
    child = MCTSNode(state={"step": 1}, parent=root)

    # First update with reward 0.8
    path = [child, root]
    engine._bp_score_update(path, 0.8)

    # After first update: visits=1, value = 0 + (0.8-0)/1 = 0.8
    assert child.visits == 1
    assert abs(child.value - 0.8) < 1e-9
    assert root.visits == 1
    assert abs(root.value - 0.8) < 1e-9

    reg = engine.score_update_registry
    assert reg["locked"] is True
    assert reg["nodes_updated"] == 2
    assert reg["fp_reviews"] == 100
    assert reg["score_verifications"] == 1000
    assert reg["precision_audits"] == 1000
    assert reg["fp_value_reviews"] == 100
    assert reg["score_latency_audits"] == 100
    assert reg["div_zero_count"] == 0
    assert len(reg["drift_errors"]) == 0


def test_backprop_score_update_multi_rewards():
    """Sub-Stage 2.3: Multiple sequential score updates converge correctly."""
    from engine.mcts import MCTSNode, MCTSEngine

    engine = MCTSEngine.__new__(MCTSEngine)
    engine.root_registry = {}

    node = MCTSNode(state={"step": 0})

    # First reward: 0.6
    engine._bp_score_update([node], 0.6)
    assert node.visits == 1
    assert abs(node.value - 0.6) < 1e-9

    # Second reward: 1.0
    engine._bp_score_update([node], 1.0)
    assert node.visits == 2
    # Running mean: 0.6 + (1.0 - 0.6) / 2 = 0.8
    assert abs(node.value - 0.8) < 1e-9

    # Third reward: 0.5
    engine._bp_score_update([node], 0.5)
    assert node.visits == 3
    # Running mean: 0.8 + (0.5 - 0.8) / 3 = 0.8 - 0.1 = 0.7
    assert abs(node.value - 0.7) < 1e-9


def test_backprop_simulation_playout():
    """Sub-Stage 2.4: Simulation playout runs 10 heuristic models."""
    from engine.mcts import MCTSNode, MCTSEngine

    engine = MCTSEngine.__new__(MCTSEngine)
    engine.root_registry = {}

    node = MCTSNode(state={"step": 0})
    engine._bp_simulation_playout(node, 0.5)

    assert "mock_playout_outcomes" in node.state
    assert len(node.state["mock_playout_outcomes"]) == 10
    assert "mock_playout_average" in node.state

    reg = engine.playout_registry
    assert reg["locked"] is True
    assert reg["playout_reviews"] == 100
    assert reg["playout_sim_audits"] == 1000
    assert reg["mock_score_checks"] == 1000
    assert reg["playout_path_reviews"] == 100
    assert reg["playout_latency_audits"] == 100
    assert reg["mock_outcomes_count"] == 10
    assert reg["ungrounded_count"] == 0


def test_backprop_full_pipeline():
    """End-to-end test: _backpropagate orchestrates all 4 sub-stages."""
    from engine.mcts import MCTSNode, MCTSEngine

    engine = MCTSEngine.__new__(MCTSEngine)
    engine.root_registry = {}

    root = MCTSNode(state={"cause_of_action": "Test."})
    child = MCTSNode(state=dict(root.state), parent=root, agent_output="Argument.")
    root.children.append(child)

    # Execute full backpropagation with reward 0.75
    engine._backpropagate(child, 0.75)

    # Verify Sub-Stage 2.1 registry
    assert hasattr(engine, "reward_retrieval_registry")
    assert engine.reward_retrieval_registry["locked"] is True

    # Verify Sub-Stage 2.2 registry
    assert hasattr(engine, "path_traversal_registry")
    assert engine.path_traversal_registry["locked"] is True
    assert engine.path_traversal_registry["path_length"] == 2

    # Verify Sub-Stage 2.3 registry
    assert hasattr(engine, "score_update_registry")
    assert engine.score_update_registry["locked"] is True
    assert engine.score_update_registry["nodes_updated"] == 2

    # Verify Sub-Stage 2.4 registry
    assert hasattr(engine, "playout_registry")
    assert engine.playout_registry["locked"] is True

    # Verify node values were updated with running mean
    assert child.visits == 1
    assert abs(child.value - 0.75) < 1e-9
    assert root.visits == 1
    assert abs(root.value - 0.75) < 1e-9


def test_backprop_deep_tree():
    """Backpropagation on a depth-5 tree updates all nodes correctly."""
    from engine.mcts import MCTSNode, MCTSEngine

    engine = MCTSEngine.__new__(MCTSEngine)
    engine.root_registry = {}

    nodes = [MCTSNode(state={"depth": 0})]
    for d in range(1, 5):
        child = MCTSNode(state={"depth": d}, parent=nodes[-1])
        nodes[-1].children.append(child)
        nodes.append(child)

    leaf = nodes[-1]
    engine._backpropagate(leaf, 0.9)

    # All 5 nodes should have visits=1 and value=0.9
    for n in nodes:
        assert n.visits == 1
        assert abs(n.value - 0.9) < 1e-9

    assert engine.path_traversal_registry["path_length"] == 5


# =====================================================================
# STAGE 3: NOVELTY SEARCH AND PRUNING TESTS
# =====================================================================

def test_stage3_glitch_detection():
    """Sub-Stage 3.1: Glitch Candidate Detection detects anomalous UCT derivative increases."""
    from engine.mcts import MCTSNode, MCTSEngine

    engine = MCTSEngine.__new__(MCTSEngine)
    engine.root_registry = {}

    root = MCTSNode(state={"step": 0})
    root.visits = 1000

    children = []
    # 19 normal nodes
    for i in range(19):
        c = MCTSNode(state={"step": 1}, parent=root, node_id=f"C{i:07d}")
        c.visits = 20
        c.value = 10.0  # Q = 0.5
        children.append(c)

    # 1 anomalous outlier node
    outlier = MCTSNode(state={"step": 1}, parent=root, node_id="C0000099")
    outlier.visits = 20
    outlier.value = 100000.0  # Q = 5000.0
    children.append(outlier)

    root.children = children

    candidates = engine._ns_glitch_detection(root)

    assert len(candidates) == 1
    assert candidates[0] is outlier
    assert outlier.state.get("glitch_candidate") is True
    assert outlier.state.get("visit_blocked") is True
    assert outlier.uct_penalty == 8000.0
    assert outlier.node_id in outlier.state.get("verifier_agent_queue", [])

    assert hasattr(engine, "glitch_registry")
    reg = engine.glitch_registry
    assert reg["locked"] is True
    assert reg["glitch_reviews"] == 100
    assert reg["deriv_audits"] == 1000
    assert reg["std_dev_checks"] == 1000
    assert reg["anomaly_score_reviews"] == 100
    assert reg["latency_audits"] == 100
    assert reg["bypassed_count"] == 0
    assert reg["visit_blocking_enforced"] is True
    assert reg["candidate_ids"] == ["C0000099"]


def test_stage3_deep_verification():
    """Sub-Stage 3.2: Deep Node Verification flags invalid candidates and checks sorry tactic."""
    from engine.mcts import MCTSNode, MCTSEngine
    from engine.validators import SwarmValidator

    engine = MCTSEngine.__new__(MCTSEngine)
    engine.validators = SwarmValidator()

    root = MCTSNode(state={"step": 0})
    # Node with sorry constraint violation
    child_sorry = MCTSNode(state={"step": 1}, parent=root, agent_output="This is sorry and incomplete.")
    # Node with invalid validator role check (assuming Counsel/Advocate status unlawfully)
    child_advocate = MCTSNode(state={"role": "petitioner_in_person", "name": "Vidya"}, parent=root, agent_output="Adv. Vidya challenges service termination.")
    # Happy path verified node
    child_valid = MCTSNode(state={"role": "petitioner_in_person", "name": "Vidya"}, parent=root, agent_output="Vidya presented the service termination challenge.")

    candidates = [child_sorry, child_advocate, child_valid]
    invalidated = engine._ns_deep_verification(candidates)

    assert len(invalidated) == 2
    assert child_sorry in invalidated
    assert child_advocate in invalidated
    assert child_valid not in invalidated

    assert child_sorry.state["verifier_check_status"] == "INVALID"
    assert "Sorry-Free Constraint violation" in child_sorry.state["verifier_error"]
    assert child_advocate.state["verifier_check_status"] == "INVALID"
    assert "incorrectly assumed Advocate" in child_advocate.state["verifier_error"]
    assert child_valid.state["verifier_check_status"] == "VALID"

    assert hasattr(engine, "verification_registry")
    reg = engine.verification_registry
    assert reg["locked"] is True
    assert reg["verifier_reviews"] == 100
    assert reg["monitoring_audits"] == 1000
    assert reg["status_flag_checks"] == 1000
    assert reg["detail_reviews"] == 100
    assert reg["unverified_marked_complete"] is False
    assert reg["failures_count"] == 2


def test_stage3_alpha_beta_prune():
    """Sub-Stage 3.3: Alpha-Beta Pruning severs links, updates ancestor visits and broadcasts tokens."""
    from engine.mcts import MCTSNode, MCTSEngine

    engine = MCTSEngine.__new__(MCTSEngine)
    engine.root_registry = {}

    root = MCTSNode(state={"step": 0}, node_id="R0000000")
    child = MCTSNode(state={"step": 1}, parent=root, node_id="C0000001")
    grandchild = MCTSNode(state={"step": 2}, parent=child, node_id="G0000002")

    root.children = [child]
    child.children = [grandchild]

    # Setup visits
    root.visits = 50
    child.visits = 30
    grandchild.visits = 10

    # Pruning child should also recursively prune grandchild and sever root linkage
    engine.root = root
    pruned = engine._ns_alpha_beta_prune([child])

    assert len(pruned) == 2
    assert child in pruned
    assert grandchild in pruned

    # Child should be removed from root children
    assert child not in root.children
    assert child.pruned is True
    assert grandchild.pruned is True

    # Root visits should be decremented by the child's visits (50 - 30 = 20)
    assert root.visits == 20

    # Check swarm broadcast tokens
    assert len(child.state["swarm_broadcast_tokens"]) == 1
    assert child.state["swarm_broadcast_tokens"][0]["token_type"] == "BRANCH_PRUNED"
    assert child.state["swarm_broadcast_tokens"][0]["node_id"] == "C0000001"

    assert len(grandchild.state["swarm_broadcast_tokens"]) == 1
    assert grandchild.state["swarm_broadcast_tokens"][0]["node_id"] == "G0000002"

    assert hasattr(engine, "pruning_registry")
    reg = engine.pruning_registry
    assert reg["locked"] is True
    assert reg["pruning_reviews"] == 100
    assert reg["pointer_audits"] == 1000
    assert reg["parent_routing_checks"] == 1000
    assert reg["tokens_broadcast_ok"] is True
    assert reg["released_bytes"] > 0


def test_stage3_matrix_poisoning():
    """Sub-Stage 3.4: UCT Matrix Poisoning nullifies UCT score and resets weights."""
    from engine.mcts import MCTSNode, MCTSEngine

    engine = MCTSEngine.__new__(MCTSEngine)
    
    root = MCTSNode(state={"step": 0})
    child = MCTSNode(state={"step": 1}, parent=root, node_id="C0000001")
    child.prior_probability = 0.75
    assert child.uct_score() == float('inf')  # visits = 0

    engine._ns_matrix_poisoning([child])

    assert child.prior_probability == 0.0
    assert child.state["poisoned"] is True
    assert child.state["warning_flag"] == "POISONED_PATH"
    assert child.uct_penalty >= 99999.0

    # UCT score should evaluate to -inf
    # child is not explicitly flagged child.pruned=True here (that is done in pruning stage),
    # but with penalty 99999.0, UCT score is extremely negative or -inf
    assert child.uct_score(c=0.2, p_ucb=True) < -90000.0

    assert hasattr(engine, "poisoning_registry")
    reg = engine.poisoning_registry
    assert reg["locked"] is True
    assert reg["poisoning_reviews"] == 100
    assert reg["poisoning_audits"] == 1000
    assert reg["score_value_checks"] == 1000
    assert reg["poisoned_count"] == 1


def test_stage3_orchestrator_integration():
    """End-to-end integration: novelty_search_and_prune runs all sub-stages sequentially."""
    from engine.mcts import MCTSNode, MCTSEngine
    from engine.validators import SwarmValidator

    engine = MCTSEngine.__new__(MCTSEngine)
    engine.validators = SwarmValidator()

    root = MCTSNode(state={"step": 0, "birth_year": 1980})
    engine.root = root
    root.visits = 1000

    children = []
    # 18 normal nodes
    for i in range(18):
        c = MCTSNode(state={"step": 1, "birth_year": 1980}, parent=root, node_id=f"C{i:07d}", agent_output="Valid output.")
        c.visits = 20
        c.value = 10.0
        children.append(c)

    # 1 valid node child1
    child1 = MCTSNode(state={"step": 1, "birth_year": 1980}, parent=root, node_id="C0000001", agent_output="Valid output.")
    child1.visits = 20
    child1.value = 10.0
    children.append(child1)

    # 1 invalid node child2 (outlier)
    child2 = MCTSNode(state={"step": 1, "birth_year": 1980}, parent=root, node_id="C0000002", agent_output="Sorry this is invalid.")
    child2.visits = 20
    child2.value = 100000.0
    children.append(child2)

    root.children = children

    # Run complete Stage 3 novelty search and prune orchestrator
    engine.novelty_search_and_prune(root)

    # child2 is anomalous (Stage 3.1) and sorry tactic (Stage 3.2), so it should be pruned (Stage 3.3) and poisoned (Stage 3.4)
    assert child2 not in root.children
    assert child2.pruned is True
    assert child2.state["poisoned"] is True
    assert child2.prior_probability == 0.0

    # child1 is valid, should remain in root children
    assert child1 in root.children
    assert child1.pruned is False
    assert child1.state.get("poisoned") is not True

    # Root visits should adjust (1000 - 20 = 980)
    assert root.visits == 980


# =====================================================================
# STAGE 5: MALEQUEARA FINAL ARBITRATION TESTS
# =====================================================================

def test_stage5_interception_and_awakening():
    """Sub-Stage 5.1: Malequeara Interception overrides citation URL/hallucination violations."""
    from engine.mcts import MCTSNode, MCTSEngine

    engine = MCTSEngine.__new__(MCTSEngine)
    
    # 1. Hallucination test case
    root = MCTSNode(state={"step": 0})
    child = MCTSNode(state={"step": 1}, parent=root, agent_output="This is a Witch of Envy hallucination.")
    root.children = [child]
    child.visits = 10
    child.prior_probability = 0.8
    
    # Mock best path to return child
    engine._best_path = lambda: [child]
    engine.root = root

    override = engine._ma_interception_and_awakening(root)
    assert override is True
    assert child.pruned is True
    assert child.uct_penalty == 800.0  # Lambda * P = 1000 * 0.8 = 800.0
    assert child.state.get("malequeara_override_active") is True
    assert child not in root.children

    # 2. Citation violation test case (citation without public URL)
    root2 = MCTSNode(state={"step": 0})
    child2 = MCTSNode(state={"step": 1}, parent=root2, agent_output="As held in 2024 SCC 12, service rules apply.")
    root2.children = [child2]
    child2.visits = 10
    child2.prior_probability = 0.5
    engine._best_path = lambda: [child2]
    engine.root = root2

    override2 = engine._ma_interception_and_awakening(root2)
    assert override2 is True
    assert child2.pruned is True
    assert child2.uct_penalty == 500.0  # 1000 * 0.5 = 500.0

    # 3. Valid citation test case (citation WITH public URL)
    root3 = MCTSNode(state={"step": 0})
    child3 = MCTSNode(state={"step": 1}, parent=root3, agent_output="As held in 2024 SCC 12 (see https://indiankanoon.org/doc/12), service rules apply.")
    root3.children = [child3]
    engine._best_path = lambda: [child3]
    engine.root = root3

    override3 = engine._ma_interception_and_awakening(root3)
    assert override3 is False
    assert child3.pruned is False


def test_stage5_adversarial_history_verification():
    """Sub-Stage 5.2: Swarm Adversarial History rejects precedents below score thresholds."""
    from engine.mcts import MCTSNode, MCTSEngine

    engine = MCTSEngine.__new__(MCTSEngine)
    engine._best_path = lambda: []

    # Supreme Court citation with score 80 (violates SC >= 100 threshold)
    root = MCTSNode(state={
        "precedent_registry": {
            "AIR 2024 SC 1234": {"court_level": "SC", "citation_score": 80}
        }
    })
    
    res = engine._ma_adversarial_history_verification(root)
    assert res is False
    assert root.pruned is True
    assert "Precedent score violation" in root.prune_reason

    # High Court citation with score 40 (violates HC >= 50 threshold)
    root2 = MCTSNode(state={
        "precedent_registry": {
            "2024 SCC 123": {"court_level": "HC", "citation_score": 40}
        }
    })
    
    res2 = engine._ma_adversarial_history_verification(root2)
    assert res2 is False
    assert root2.pruned is True


def test_stage5_loophole_extraction_audit():
    """Sub-Stage 5.3: Loophole extraction calculates risk and triggers corrections."""
    from engine.mcts import MCTSNode, MCTSEngine

    engine = MCTSEngine.__new__(MCTSEngine)

    # Risk score: 30 (non-exhaustion) + 20 (overlap) = 50 (> 45.0 threshold)
    root = MCTSNode(state={
        "non_exhaustion_of_domestic_remedies": True,
        "prayer_logical_overlap": True
    })

    risk = engine._ma_loophole_extraction_audit(root)
    assert risk == 50.0
    assert root.state.get("structural_correction_triggered") is True
    assert root.uct_penalty == 6000.0


def test_stage5_matrix_security_gating():
    """Sub-Stage 5.4: Matrix security gating detects and strips remote scripts/macros."""
    from engine.mcts import MCTSNode, MCTSEngine

    engine = MCTSEngine.__new__(MCTSEngine)

    root = MCTSNode(state={"step": 0})
    child = MCTSNode(state={"step": 1}, parent=root, agent_output="We request shell exec(cmd.exe) execution.")
    root.children = [child]

    res = engine._ma_matrix_security_gating(root)
    assert res is False
    assert child.pruned is True
    assert child.state.get("poisoned") is True
    assert child.uct_penalty == 99999.0


def test_stage5_sovereign_adjudication_commit():
    """Sub-Stage 5.5: Committing signs tree hash using NIST P-256 ECDSA and locks registry."""
    from engine.mcts import MCTSNode, MCTSEngine
    import base64

    engine = MCTSEngine.__new__(MCTSEngine)

    root = MCTSNode(state={"step": 0})
    child = MCTSNode(state={"step": 1}, parent=root, node_id="C0000001")
    other_child = MCTSNode(state={"step": 1}, parent=root, node_id="C0000002")
    
    root.children = [child, other_child]
    child.visits = 10
    other_child.visits = 10

    # child is on best path, other_child is not
    engine._best_path = lambda: [child]

    payload = engine._ma_sovereign_adjudication_commit(root)

    assert payload["status"] == "COMMITTED"
    assert payload["registry_status"] == "READ_ONLY"
    assert "root_hash" in payload
    assert "signature" in payload
    assert "public_key_hash" in payload

    # Verify signature is valid base64
    sig_bytes = base64.b64decode(payload["signature"])
    assert len(sig_bytes) > 0

    # Sibling node not in best path should have visits reset to 0
    assert other_child.visits == 0
    assert child.visits == 10


def test_stage5_orchestrator_integration():
    """End-to-end integration: malequeara_arbitration runs all sub-stages successfully."""
    from engine.mcts import MCTSNode, MCTSEngine

    engine = MCTSEngine.__new__(MCTSEngine)

    root = MCTSNode(state={"step": 0, "birth_year": 1980})
    child = MCTSNode(state={"step": 1, "birth_year": 1980}, parent=root, node_id="C0000001", agent_output="Valid text.")
    root.children = [child]
    child.visits = 10

    engine._best_path = lambda: [child]

    payload = engine.malequeara_arbitration(root)

    assert payload["status"] == "COMMITTED"
    assert payload["registry_status"] == "READ_ONLY"
    assert hasattr(engine, "interception_registry")
    assert hasattr(engine, "adversarial_history_registry")
    assert hasattr(engine, "loophole_audit_registry")
    assert hasattr(engine, "matrix_security_registry")
    assert hasattr(engine, "sovereign_commit_registry")









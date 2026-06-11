import pytest
from engine.internal_consistency import ConsistencyEngine, QuantAuditResult
from engine.evidence_matrix import EvidenceMatrix, EvidenceAtom

def test_audit_quant_engine_penalties_happy_path():
    # Instantiate engine with empty matrix (since we only test math right now)
    matrix = EvidenceMatrix(atoms=[])
    engine = ConsistencyEngine(f_matrix=matrix)

    # 1. Test case where confidence is 1.0 (p_assumption = 0.0) -> no penalty
    res = engine.audit_quant_engine_penalties(
        uct_score=10.0,
        visits=5,
        parent_visits=10,
        p_assumption=0.0
    )
    assert res.original_uct == 10.0
    assert res.adjusted_uct == 10.0
    assert res.penalty_applied == 0.0
    assert not res.pruned

    # 2. Test case with low confidence (p_assumption = 0.05) -> should apply base penalty + 50.0 quant penalty
    res_low = engine.audit_quant_engine_penalties(
        uct_score=100.0,
        visits=5,
        parent_visits=10,
        p_assumption=0.05
    )
    # base penalty = 1000 * 0.05 = 50.0
    # confidence = 0.95 < 0.99 -> add 50.0 penalty
    # Total penalty = 100.0
    # adjusted_uct = 100.0 - 100.0 = 0.0 (< 0.1 -> pruned)
    assert res_low.adjusted_uct == 0.0
    assert res_low.penalty_applied == 100.0
    assert res_low.pruned
    assert "below minimum threshold" in res_low.reason

def test_audit_quant_engine_penalties_validation_errors():
    matrix = EvidenceMatrix(atoms=[])
    engine = ConsistencyEngine(f_matrix=matrix)

    # p_assumption out of bounds
    with pytest.raises(ValueError, match="p_assumption must be between 0.0 and 1.0"):
        engine.audit_quant_engine_penalties(10.0, 5, 10, -0.1)

    with pytest.raises(ValueError, match="p_assumption must be between 0.0 and 1.0"):
        engine.audit_quant_engine_penalties(10.0, 5, 10, 1.1)

    # visits out of bounds
    with pytest.raises(ValueError, match="visits and parent_visits must be non-negative"):
        engine.audit_quant_engine_penalties(10.0, -1, 10, 0.5)

    with pytest.raises(ValueError, match="visits and parent_visits must be non-negative"):
        engine.audit_quant_engine_penalties(10.0, 5, -1, 0.5)

def test_consistency_engine_verify_claim():
    atoms = [
        EvidenceAtom(
            atom_id="E1",
            description="The signature on the agreement was signed under duress.",
            timestamp_ms=1000,
            confidence=0.85,
            source="witness",
            grounded=True
        ),
        EvidenceAtom(
            atom_id="E2",
            description="No transaction delay occurred during the execution phase.",
            timestamp_ms=2000,
            confidence=0.95,
            source="forensic",
            grounded=True
        )
    ]
    matrix = EvidenceMatrix(atoms=atoms)
    engine = ConsistencyEngine(f_matrix=matrix)

    # Test exact / high overlap verification
    res = engine.verify_claim("The signature was signed under duress", temperature=0.0)
    assert res.confidence_score > 0.7
    assert res.prior_probability > 0.7

    # Test verify claim with temperature noise (should pull score down/up towards prior or max uncertainty)
    res_high_temp = engine.verify_claim("The signature was signed under duress", temperature=5.0)
    # At temperature=5.0, temp_factor becomes 0.0, which makes likelihood=0.5, marginal=0.5, posterior=prior
    assert res_high_temp.confidence_score == res_high_temp.prior_probability

    # Test verify claim with no matching evidence
    res_none = engine.verify_claim("Unrelated statement about weather", temperature=0.0)
    assert res_none.confidence_score == 0.5

def test_consistency_engine_cosine_distance():
    atoms = [
        EvidenceAtom(
            atom_id="E1",
            description="Plaintiff signed the contract in Delhi",
            timestamp_ms=1000,
            confidence=1.0,
            source="document",
            grounded=True
        )
    ]
    matrix = EvidenceMatrix(atoms=atoms)
    engine = ConsistencyEngine(f_matrix=matrix)

    # Exact matching keywords should have close to 0.0 distance
    dist_exact = engine.measure_cosine_distance("plaintiff signed the contract delhi")
    assert dist_exact < 0.1

    # Completely different keywords should have 1.0 distance
    dist_diff = engine.measure_cosine_distance("Unrelated topic about fruits")
    assert dist_diff == 1.0

def test_consistency_engine_generate_negation_states():
    matrix = EvidenceMatrix(atoms=[])
    engine = ConsistencyEngine(f_matrix=matrix)

    negations = engine.generate_negation_states("The witness was present at the scene")
    assert "The witness was not present at the scene" in negations or "The witness was never present at the scene" in negations or "It is not the case that the witness was present at the scene" in negations
    assert len(negations) > 0

    negations_special = engine.generate_negation_states("Agreement is valid and compliant")
    assert any("invalid" in state for state in negations_special)
    assert any("non-compliant" in state for state in negations_special)

def test_consistency_engine_count_non_factual_entities():
    atoms = [
        EvidenceAtom(
            atom_id="E1",
            description="Arjun and Ramesh were present in Bangalore",
            timestamp_ms=1000,
            confidence=1.0,
            source="witness",
            grounded=True
        )
    ]
    matrix = EvidenceMatrix(atoms=atoms)
    engine = ConsistencyEngine(f_matrix=matrix)

    # Bangalore is grounded, but Mumbai and Suresh are not
    count = engine.count_non_factual_entities("Suresh travelled from Bangalore to Mumbai")
    assert count == 2  # Suresh, Mumbai are ungrounded

def test_consistency_engine_logical_connectivity():
    atoms = [
        EvidenceAtom(
            atom_id="E1",
            description="The key was stolen from the drawer",
            timestamp_ms=1000,
            confidence=1.0,
            source="witness",
            grounded=True
        )
    ]
    matrix = EvidenceMatrix(atoms=atoms)
    engine = ConsistencyEngine(f_matrix=matrix)

    # Connectivity via token overlap
    assert engine.check_logical_connectivity("The drawer was unlocked", "The key in the drawer is missing") is True

    # Connectivity via shared atom in the matrix
    assert engine.check_logical_connectivity("stolen key", "drawer") is True

    # No connectivity
    assert engine.check_logical_connectivity("It is raining outside", "Computers run on electricity") is False

def test_consistency_engine_audit_entity_cross_references():
    matrix = EvidenceMatrix(atoms=[])
    engine = ConsistencyEngine(f_matrix=matrix)

    # Test Happy Path (valid physical attributes)
    res = engine.audit_entity_cross_references(
        claim="The witness saw the injury",
        witness_coords=(10.0, 10.0),
        event_coords=(15.0, 15.0),
        ambient_noise_db=45.0,
        medical_record={"diagnosis": "fracture and pain"},
        forensic_record={"recovery_timestamp_ms": 5000, "incident_timestamp_ms": 3000},
        cdr_record={"tower_coords": (12.0, 12.0), "timestamp_ms": 3000}
    )
    assert res.line_of_sight_valid is True
    assert res.ambient_noise_valid is True
    assert res.spatial_coords_valid is True
    assert res.medical_diagnosis_matches is True
    assert res.forensic_date_valid is True
    assert res.cdr_alignment_valid is True
    assert len(res.warnings) == 0

    # Test Fail Path (impossibilities)
    res_fail = engine.audit_entity_cross_references(
        claim="The witness heard a whisper and saw the fracture from miles away",
        witness_coords=(10.0, 10.0),
        event_coords=(400.0, 400.0),  # Distance > 200m
        ambient_noise_db=85.0,  # Loud background noise
        medical_record={"diagnosis": "no physical injuries reported"},
        forensic_record={"recovery_timestamp_ms": 1000, "incident_timestamp_ms": 3000},  # Time travel
        cdr_record={"tower_coords": (900.0, 900.0), "timestamp_ms": 3000}  # Tower out of range
    )
    assert res_fail.line_of_sight_valid is False
    assert res_fail.ambient_noise_valid is False
    assert res_fail.medical_diagnosis_matches is False
    assert res_fail.forensic_date_valid is False
    assert res_fail.cdr_alignment_valid is False
    assert len(res_fail.warnings) > 0

def test_consistency_engine_audit_semantic_variance():
    matrix = EvidenceMatrix(atoms=[])
    engine = ConsistencyEngine(f_matrix=matrix)

    text = "IN THE COURT OF DELHI. Ramesh vs Suresh. The contract was signed herein. It was breached later. Plaintiff sued Ramesh."
    res = engine.audit_semantic_variance(text, "DL-DISTRICT")

    assert res.jargon_density > 0.0
    # "was signed", "was breached" - passive voice present
    assert res.active_voice_ratio < 1.0
    assert res.format_compliant is True
    assert "sued" in res.synonyms_matched
    assert len(res.warnings) == 0

    # Test non-compliant formatting
    text_bad = "Ramesh and Suresh broke the deal. He is a liar."
    res_bad = engine.audit_semantic_variance(text_bad, "DL-DISTRICT")
    assert res_bad.format_compliant is False
    assert len(res_bad.warnings) > 0

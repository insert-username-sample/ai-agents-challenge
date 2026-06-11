import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import json
from engine.evidence_matrix import EvidenceAtom, EvidenceMatrix
from engine.butterfly_engine import (
    MutationRecord,
    MutatedCaseContext,
    mutate_date,
    mutate_jurisdiction,
    mutate_party_standing,
    mutate_statute,
    mutate_precedent,
    mutate_evidence_exclusion,
    generate_butterfly_mutations,
    check_cross_timeline_consistency,
)

# Sample base case context for testing mutations
BASE_CASE = {
    "case_title": "Vidya Khobrekar v. State of Maharashtra",
    "filing_date": "2024-08-01T12:00:00Z",
    "jurisdiction": "MH-HC-BOMBAY",
    "client_role": "Petitioner",
    "primary_statute": "Section 302 IPC",
    "facts": "The accused was charged under Section 302 IPC. The incident occurred on 2024-05-10.",
    "precedents": ["State of Maharashtra v. Somnath (2021) SC"],
    "evidence": ["Forensic blood report dated 2024-05-11", "Eye-witness statement of Ramesh"],
}


class TestEvidenceAtomMatrix:
    def test_evidence_atom_shifting_timeline(self):
        # Weight * confidence > threshold (default 0.3)
        atom_low = EvidenceAtom(
            atom_id="atom_1",
            description="Witness was 50 meters away",
            timestamp_ms=1717150000000,
            confidence=0.5,
            source="witness",
            butterfly_weight=0.5, # 0.5 * 0.5 = 0.25 <= 0.3
        )
        assert not atom_low.shifts_timeline()

        atom_high = EvidenceAtom(
            atom_id="atom_2",
            description="CCTV footage of the incident",
            timestamp_ms=1717150000000,
            confidence=0.9,
            source="document",
            butterfly_weight=0.8, # 0.9 * 0.8 = 0.72 > 0.3
        )
        assert atom_high.shifts_timeline()

    def test_evidence_matrix_butterfly_score(self):
        atom = EvidenceAtom(
            atom_id="atom_1",
            description="Fingerprint report",
            timestamp_ms=1717150000000,
            confidence=0.9,
            source="forensic",
            butterfly_weight=0.7,
            linked_atoms=["atom_2", "atom_3"],
        )
        matrix = EvidenceMatrix(atoms=[atom])
        # Score: 0.9 * 0.7 * (1.0 + 2 * 0.1) = 0.63 * 1.2 = 0.756
        assert abs(matrix.butterfly_score(atom) - 0.756) < 0.001

    def test_evidence_matrix_apply_to_branch(self):
        atoms = [
            EvidenceAtom(
                atom_id="atom_1",
                description="Signature on the document is disputed",
                timestamp_ms=1717150000000,
                confidence=0.8,
                source="forensic",
                butterfly_weight=0.9,
            ),
            EvidenceAtom(
                atom_id="atom_2",
                description="Filing delay was 30 days due to illness",
                timestamp_ms=1717150000000,
                confidence=0.7,
                source="witness",
                butterfly_weight=0.8,
            )
        ]
        matrix = EvidenceMatrix(atoms=atoms)
        branch_state = {"defect_penalty": 0.1, "signature_validity": "verified", "limitation_status": "in_time"}
        
        modified = matrix.apply_to_branch(branch_state)
        assert modified["signature_validity"] == "doubtful"
        assert modified["limitation_status"] == "delayed"
        # defect_penalty = 0.1 + 0.3 + 0.5 = 0.9
        assert abs(modified["defect_penalty"] - 0.9) < 0.001


class TestButterflyMutations:
    def test_mutate_date_shift(self):
        res = mutate_date(BASE_CASE, field_name="filing_date", delta_days=30)
        assert res.original_context["filing_date"] == "2024-08-01T12:00:00Z"
        assert "2024-08-31" in res.mutated_context["filing_date"]
        assert res.mutation.mutation_type == "date_shift"
        assert res.mutation.field_path == "filing_date"

    def test_mutate_jurisdiction(self):
        res = mutate_jurisdiction(BASE_CASE, "MH-DISTRICT")
        assert res.original_context["jurisdiction"] == "MH-HC-BOMBAY"
        assert res.mutated_context["jurisdiction"] == "MH-DISTRICT"
        assert res.mutation.mutation_type == "jurisdiction_swap"

    def test_mutate_party_standing(self):
        res = mutate_party_standing(BASE_CASE, "Petitioner-in-Person")
        assert res.original_context["client_role"] == "Petitioner"
        assert res.mutated_context["client_role"] == "Petitioner-in-Person"
        assert res.mutation.mutation_type == "party_standing_change"

    def test_mutate_statute(self):
        res = mutate_statute(BASE_CASE, "Section 302 IPC", "Section 103 BNS")
        assert res.original_context["primary_statute"] == "Section 302 IPC"
        assert res.mutated_context["primary_statute"] == "Section 103 BNS"
        assert "Section 103 BNS" in res.mutated_context["facts"]
        assert "Section 302 IPC" not in res.mutated_context["facts"]

    def test_mutate_precedent(self):
        res = mutate_precedent(BASE_CASE, "State of Maharashtra v. Somnath (2021) SC")
        assert "State of Maharashtra v. Somnath (2021) SC" in res.original_context["precedents"]
        assert "State of Maharashtra v. Somnath (2021) SC" not in res.mutated_context["precedents"]
        assert "State of Maharashtra v. Somnath (2021) SC" in res.mutated_context["overruled_precedents"]

    def test_mutate_evidence_exclusion(self):
        res = mutate_evidence_exclusion(BASE_CASE, "Eye-witness statement of Ramesh")
        assert "Eye-witness statement of Ramesh" in res.original_context["evidence"]
        assert "Eye-witness statement of Ramesh" not in res.mutated_context["evidence"]
        assert "Eye-witness statement of Ramesh" in res.mutated_context["excluded_evidence"]

    def test_generate_butterfly_mutations(self):
        muts = generate_butterfly_mutations(BASE_CASE, max_mutations=5)
        # Ensure at least 3 mutations generated (RULE-11 requirement)
        assert len(muts) >= 3
        # Check all are distinct mutation types
        types = [m.mutation.mutation_type for m in muts]
        assert len(set(types)) == len(types)

    def test_check_cross_timeline_consistency(self):
        results = [
            {"run_metadata": {"case_title": "run_0"}, "success_probability": 85.0},
            {"run_metadata": {"case_title": "run_1"}, "success_probability": 80.0},
            {"run_metadata": {"case_title": "run_2"}, "success_probability": 50.0}, # >20% difference from run_0
        ]
        violations = check_cross_timeline_consistency(results, divergence_threshold=0.20)
        assert len(violations) > 0
        assert violations[0]["divergence"] == 35.0
        assert "run_2" in violations[0]["timeline_b"]

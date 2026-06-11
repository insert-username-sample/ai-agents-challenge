import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from rigorous_testing.deep_strategist_simulation_v1_0_0_0 import (
    MCTSNode,
    MediatorMelaquera,
    TemporalDemographicAuditor,
)


class TestMCTSNodePenalty:
    def test_calculate_uct_unvisited(self):
        node = MCTSNode(name="test_node", description="test description", p_assumption=0.1)
        # Visited 0 times must return infinity
        assert node.calculate_uct() == float('inf')

    def test_calculate_uct_visited_with_penalty(self):
        parent = MCTSNode(name="parent", description="", p_assumption=0.0)
        parent.n = 10
        
        child = MCTSNode(name="child", description="", p_assumption=0.05, parent=parent)
        child.n = 5
        child.w = 4.0
        
        score = child.calculate_uct(c=1.414, lambda_val=10.0)
        
        exploitation = 4.0 / 5.0  # 0.8
        exploration = 1.414 * ((math_log_parent := 2.30258509) / 5) ** 0.5  # 1.414 * 0.6786 = 0.9595
        penalty = 10.0 * 0.05  # 0.5
        
        # Expected: 0.8 + 0.9595 - 0.5 = 1.2595
        import math
        expected_exploration = 1.414 * math.sqrt(math.log(10) / 5)
        expected = 0.8 + expected_exploration - 0.5
        assert abs(score - expected) < 0.001


class TestMediatorMelaquera:
    def test_melaquera_no_violations(self):
        melaquera = MediatorMelaquera()
        node = MCTSNode(name="SDO Grounded Path", description="", p_assumption=0.01)
        audit_report = {
            "name": "Vidya Khobrekar",
            "calculated_age_2026": 55,
            "status_2026": "Active",
            "mismatch_found": False,
        }
        res = melaquera.intercept_and_validate(node, audit_report)
        assert res["action_code"] == "CONCILIATION_SUCCESS"
        assert len(res["warnings"]) == 0

    def test_melaquera_veto_role_assumption(self):
        melaquera = MediatorMelaquera()
        # "Prior" in name triggers role assumption failure veto
        node = MCTSNode(name="SDO Prior Assumption Shortcut", description="", p_assumption=0.8)
        audit_report = {
            "name": "Vidya Khobrekar",
            "calculated_age_2026": 55,
            "status_2026": "Active",
            "mismatch_found": False,
        }
        res = melaquera.intercept_and_validate(node, audit_report)
        assert res["action_code"] == "VETO_APPLIED"
        assert any("ROLE ASSUMPTION FAILURE" in w for w in res["warnings"])

    def test_melaquera_temporal_gap_intercept(self):
        melaquera = MediatorMelaquera()
        node = MCTSNode(name="SDO Grounded Path", description="", p_assumption=0.01)
        audit_report = {
            "name": "Vidya Khobrekar",
            "calculated_age_2026": 61,
            "status_2026": "Retired",
            "mismatch_found": True,
        }
        res = melaquera.intercept_and_validate(node, audit_report)
        assert res["action_code"] == "CONCILIATION_SUCCESS" # Not a veto, but resolved with warnings
        assert any("TEMPORAL GAP DETECTED" in w for w in res["warnings"])


class TestTemporalDemographicAuditor:
    def test_profile_audit_no_mismatch(self):
        auditor = TemporalDemographicAuditor(active_year=2026, retirement_cap=60)
        res = auditor.execute_profile_audit(
            name="Karan Singh",
            birth_year=1980,
            historic_status="Active"
        )
        assert res["calculated_age_2026"] == 46
        assert res["status_2026"] == "Active"
        assert not res["mismatch_found"]

    def test_profile_audit_with_retirement_mismatch(self):
        auditor = TemporalDemographicAuditor(active_year=2026, retirement_cap=60)
        res = auditor.execute_profile_audit(
            name="Vidya Khobrekar",
            birth_year=1965,
            historic_status="Senior Investigator"
        )
        assert res["calculated_age_2026"] == 61
        assert res["status_2026"] == "Retired"
        assert res["mismatch_found"]

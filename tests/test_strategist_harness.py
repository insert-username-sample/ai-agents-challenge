import pytest

from agents.harness_rules import GroundingResult, HarnessViolation
from agents.strategist_harness import (
    StrategistMicroStep,
    StrategistSwarmHarness,
    build_kesavananda_micro_steps,
)


CASE = {
    "title": "Kesavananda Bharati v. State of Kerala",
    "citation": "(1973) 4 SCC 225",
    "jurisdiction": "IN-SC",
    "subject": "Basic Structure Doctrine and limits of parliamentary amendment power",
    "precedents": [
        "Golaknath v. State of Punjab (1967) 2 SCR 762",
        "Sajjan Singh v. State of Rajasthan AIR 1965 SC 845",
    ],
}


def _ok_grounding(**kwargs):
    return GroundingResult(
        query=kwargs["claim"],
        agent_name=kwargs["agent_name"],
        node_id=kwargs["node_id"],
        verified=True,
        sources=["Official source: https://example.test/source"],
        grounding_text="verified",
        p_assumption=0.01,
    )


def test_seven_agent_harness_passes_with_source_bearing_grounding():
    report = StrategistSwarmHarness(grounding_fn=_ok_grounding).execute(CASE)

    assert report["strict_gate"]["strict_pass"] is True
    assert report["coverage"]["verified_micro_steps"] == report["coverage"]["total_micro_steps"]
    assert set(report["coverage"]["agent_step_counts"].values()) == {2}
    assert report["risk_metrics"]["weighted_p_assumption"] == 0.01


def test_unverified_upstream_step_blocks_dependents():
    def grounding(**kwargs):
        if kwargs["node_id"] == "P1":
            return GroundingResult(
                query=kwargs["claim"],
                agent_name=kwargs["agent_name"],
                node_id=kwargs["node_id"],
                verified=False,
                p_assumption=1.0,
                error="forced failure",
            )
        return _ok_grounding(**kwargs)

    report = StrategistSwarmHarness(grounding_fn=grounding).execute(CASE)

    assert report["strict_gate"]["decision"] == "FAIL_CLOSED"
    assert "P1" in report["risk_metrics"]["unverified_critical_steps"]
    assert report["coverage"]["downstream_blocked_steps"] > 0


def test_missing_canonical_agent_coverage_is_rejected():
    steps = build_kesavananda_micro_steps(CASE)
    incomplete = [s for s in steps if s.agent_name != "judge_agent"]

    with pytest.raises(HarnessViolation) as exc:
        StrategistSwarmHarness().execute(CASE, steps=incomplete)

    assert exc.value.rule_id == "RULE-16"


def test_non_canonical_agent_name_is_rejected():
    bad_steps = [
        StrategistMicroStep(
            "X1",
            "agent_delta",
            "bad_phase",
            "fact",
            "fake claim",
        )
    ]

    with pytest.raises(HarnessViolation) as exc:
        StrategistSwarmHarness().execute(CASE, steps=bad_steps)

    assert exc.value.rule_id == "RULE-14"

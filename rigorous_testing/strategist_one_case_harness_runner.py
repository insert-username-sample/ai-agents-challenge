"""
Run one strict end-to-end strategist harness case.

This runner is intentionally bounded and fail-closed:
- one case only;
- all seven canonical strategist agents required;
- every micro-step attempts Google Search Grounding;
- source-less grounding text remains unverified;
- unverified upstream critical steps block downstream deductions.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from agents.strategist_harness import (  # noqa: E402
    StrategistHarnessPolicy,
    StrategistSwarmHarness,
)
from rigorous_testing.long_horizon_stress_test_runner import STRESS_TEST_CASES  # noqa: E402


FINDINGS_DIR = PROJECT_ROOT / "rigorous_testing" / "findings"
JSON_REPORT = FINDINGS_DIR / "strategist_one_case_harness_report.json"
MD_REPORT = FINDINGS_DIR / "strategist_one_case_harness_report.md"


def write_markdown_report(result: Dict[str, Any], output_path: Path) -> None:
    gate = result["strict_gate"]
    coverage = result["coverage"]
    risk = result["risk_metrics"]
    meta = result["metadata"]

    lines = [
        "# Strategist One-Case Seven-Agent Harness Report",
        "",
        f"Generated: {meta['timestamp']}",
        f"Case: {meta['case_title']}",
        "",
        "## Audit Trail",
        "",
        f"- Raw log status: {meta.get('raw_log_status', 'Not recorded')}",
        f"- Baseline observation: {meta.get('baseline_observation', 'Not recorded')}",
        "",
        "## Strict Gate",
        "",
        f"- Decision: {gate['decision']}",
        f"- Strict pass: {gate['strict_pass']}",
        f"- Reason: {gate['reason']}",
        "",
        "## Coverage",
        "",
        f"- Total micro-steps: {coverage['total_micro_steps']}",
        f"- Verified micro-steps: {coverage['verified_micro_steps']}",
        f"- Unverified micro-steps: {coverage['unverified_micro_steps']}",
        f"- Downstream blocked steps: {coverage['downstream_blocked_steps']}",
        f"- Source-bearing verified steps: {coverage['source_bearing_verified_steps']}",
        "",
        "## Agent Step Counts",
        "",
    ]
    for agent, count in coverage["agent_step_counts"].items():
        lines.append(f"- {agent}: {count}")

    lines.extend([
        "",
        "## Risk Metrics",
        "",
        f"- Weighted P_assumption: {risk['weighted_p_assumption']}",
        f"- Grounded success estimate: {risk['grounded_success_estimate']}%",
        f"- Unverified critical steps: {', '.join(risk['unverified_critical_steps']) or 'None'}",
        "",
        "## Evidence Ledger",
        "",
        "| Step | Agent | Verified | Sources | P_assumption | Blocked | Error | Claim |",
        "|---|---|---:|---:|---:|---:|---|---|",
    ])

    for entry in result["evidence_ledger"]:
        claim = entry["query"].replace("|", "/")[:100]
        error = (entry.get("error") or "").replace("|", "/")[:80]
        lines.append(
            f"| {entry['step_id']} | {entry['agent_name']} | {entry['verified']} "
            f"| {entry['source_count']} | {entry['p_assumption']} "
            f"| {entry['downstream_blocked']} | {error} | {claim} |"
        )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(timeout_ms: int, require_sources: bool) -> Dict[str, Any]:
    case = STRESS_TEST_CASES[0]
    policy = StrategistHarnessPolicy(
        require_all_agents=True,
        min_steps_per_agent=2,
        require_sources=require_sources,
        fail_closed_on_unverified=True,
        retry_backoff_seconds=(0,),
        request_timeout_ms=timeout_ms,
        max_critical_p_assumption=0.05,
    )
    harness = StrategistSwarmHarness(policy=policy)
    return harness.execute(case)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout-ms", type=int, default=10000)
    parser.add_argument("--allow-sourceless", action="store_true")
    args = parser.parse_args()

    FINDINGS_DIR.mkdir(parents=True, exist_ok=True)
    result = run(
        timeout_ms=args.timeout_ms,
        require_sources=not args.allow_sourceless,
    )
    result["metadata"]["raw_log_status"] = (
        "Existing rigorous_testing/raw_conversation_log*.jsonl artifacts are tracked in git; "
        "the live Codex transcript source is not exposed to this runner, so no synthetic raw log was created."
    )
    result["metadata"]["baseline_observation"] = (
        "The pre-harness live baseline timed out after 180 seconds. The strict runner now fails closed "
        "under bounded grounding failures instead of fabricating completion."
    )
    JSON_REPORT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_markdown_report(result, MD_REPORT)

    gate = result["strict_gate"]
    coverage = result["coverage"]
    risk = result["risk_metrics"]
    print(json.dumps({
        "case": result["metadata"]["case_title"],
        "decision": gate["decision"],
        "strict_pass": gate["strict_pass"],
        "verified": coverage["verified_micro_steps"],
        "total": coverage["total_micro_steps"],
        "blocked": coverage["downstream_blocked_steps"],
        "weighted_p_assumption": risk["weighted_p_assumption"],
        "grounded_success_estimate": risk["grounded_success_estimate"],
        "json_report": str(JSON_REPORT),
        "markdown_report": str(MD_REPORT),
    }, indent=2))
    return 0 if gate["strict_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

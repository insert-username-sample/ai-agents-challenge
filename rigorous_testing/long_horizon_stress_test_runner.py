# =====================================================================
# CLAUSELY: LONG-HORIZON SIMULATION STRESS TEST RUNNER
# =====================================================================
# Executes the MCTS long-horizon simulator on real Indian legal cases.
# Every deduction is grounded via live Google Search Grounding API.
# No fabricated cases. No hardcoded outcomes. No artificial entropy.
# =====================================================================

import os
import sys
import json
import time
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from dotenv import load_dotenv

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("clausely.stress_test")

from agents.long_horizon_simulator import LongHorizonSimulator
from agents.harness_rules import build_harness_preamble


# =====================================================================
# REAL CASE DATA
# =====================================================================
# These are actual Indian legal cases with verifiable citations.
# The simulator will ground-check every precedent and statute.
# =====================================================================

STRESS_TEST_CASES: List[Dict[str, Any]] = [
    {
        "title": "Kesavananda Bharati v. State of Kerala",
        "citation": "(1973) 4 SCC 225",
        "jurisdiction": "IN-SC",
        "subject": "Basic Structure Doctrine and limits of parliamentary amendment power",
        "document_type": "writ petition",
        "facts": (
            "Swami Kesavananda Bharati, head of the Edneer Mutt in Kerala, challenged the Kerala "
            "Land Reforms Act 1963 as amended by the 29th Amendment which placed it in the Ninth "
            "Schedule. The petitioner argued that the 24th, 25th, and 29th Amendments to the "
            "Constitution violated fundamental rights under Articles 25, 26, 14, 19(1)(f), and 31. "
            "Parliament had enacted the 24th Amendment to assert its unlimited power to amend any "
            "provision of the Constitution including fundamental rights. The 25th Amendment inserted "
            "Article 31C to give primacy to Directive Principles over fundamental rights. A 13-Judge "
            "Constitution Bench was assembled to reconsider the ratio of Golaknath v. State of Punjab."
        ),
        "precedents": [
            "Golaknath v. State of Punjab (1967) 2 SCR 762",
            "Sajjan Singh v. State of Rajasthan AIR 1965 SC 845",
            "Shankari Prasad v. Union of India AIR 1951 SC 458",
        ],
        "num_parties": 4,
        "num_statutes": 6,
    },
    {
        "title": "Navtej Singh Johar v. Union of India",
        "citation": "(2018) 10 SCC 1",
        "jurisdiction": "IN-SC",
        "subject": "Decriminalization of consensual same-sex relations under Section 377 IPC",
        "document_type": "writ petition",
        "facts": (
            "Five petitioners including dancer Navtej Singh Johar, journalist Sunil Mehra, chef "
            "Ritu Dalmia, hotelier Aman Nath, and business executive Ayesha Kapur challenged the "
            "constitutionality of Section 377 of the Indian Penal Code 1860 insofar as it "
            "criminalized consensual sexual acts between adults in private. The petitioners argued "
            "that Section 377 violated their fundamental rights under Articles 14 (equality), 15 "
            "(non-discrimination), 19(1)(a) (freedom of expression), and 21 (right to life and "
            "personal liberty including the right to privacy as recognized in Puttaswamy). The "
            "Union of India left the matter to the wisdom of the Court. A 5-Judge Constitution "
            "Bench was constituted to reconsider Suresh Kumar Koushal v. Naz Foundation (2014)."
        ),
        "precedents": [
            "Suresh Kumar Koushal v. Naz Foundation (2014) 1 SCC 1",
            "Justice K.S. Puttaswamy v. Union of India (2017) 10 SCC 1",
            "Naz Foundation v. Government of NCT of Delhi (2009) 160 DLT 277",
        ],
        "num_parties": 6,
        "num_statutes": 4,
    },
    {
        "title": "Shreya Singhal v. Union of India",
        "citation": "(2015) 5 SCC 1",
        "jurisdiction": "IN-SC",
        "subject": "Constitutionality of Section 66A Information Technology Act 2000",
        "document_type": "writ petition",
        "facts": (
            "Shreya Singhal, a law student, filed a PIL after two women were arrested in Palghar, "
            "Maharashtra under Section 66A of the Information Technology Act 2000 for posting "
            "comments on Facebook criticizing the shutdown of Mumbai following the death of Bal "
            "Thackeray. The petitioner challenged Section 66A as violative of Article 19(1)(a) "
            "(freedom of speech and expression) arguing the section was vague, overbroad, and had "
            "a chilling effect on free speech. The section penalized sending offensive messages "
            "through communication devices with imprisonment up to 3 years. Multiple intervenors "
            "including Internet Freedom Foundation supported the petition. Government defended "
            "the section as necessary to prevent misuse of social media."
        ),
        "precedents": [
            "Romesh Thapar v. State of Madras AIR 1950 SC 124",
            "S. Rangarajan v. P. Jagjivan Ram (1989) 2 SCC 574",
        ],
        "num_parties": 5,
        "num_statutes": 3,
    },
]


# =====================================================================
# RUNNER
# =====================================================================

def run_stress_test(
    cases: List[Dict[str, Any]],
    grounding_budget_per_case: int = 30,
    output_dir: str = "",
) -> None:
    """
    Execute long-horizon MCTS simulation on each case.

    Args:
        cases: List of case context dicts.
        grounding_budget_per_case: Max grounding API calls per case.
        output_dir: Directory for output reports.
    """
    if not output_dir:
        output_dir = str(PROJECT_ROOT / "rigorous_testing" / "findings")
    os.makedirs(output_dir, exist_ok=True)

    # Print harness rules preamble
    print(build_harness_preamble())
    print("=" * 72)
    print("  CLAUSELY LONG-HORIZON MCTS STRESS TEST")
    print(f"  Cases to simulate: {len(cases)}")
    print(f"  Grounding budget per case: {grounding_budget_per_case}")
    print(f"  Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 72)
    print()

    all_results = []

    for idx, case in enumerate(cases, 1):
        print(f"[{idx}/{len(cases)}] Simulating: {case['title']}")
        print(f"  Citation: {case.get('citation', 'N/A')}")
        print(f"  Subject: {case.get('subject', 'N/A')}")
        print()

        simulator = LongHorizonSimulator(
            grounding_budget=grounding_budget_per_case,
        )

        try:
            result = simulator.simulate(case, run_id=f"stress-{idx:03d}")
            all_results.append(result)

            # Print summary for this case
            gs = result["grounding_statistics"]
            ts = result["tree_statistics"]
            print(f"  [RESULT] Iterations: {result['run_metadata']['iterations']}")
            print(f"  [RESULT] Elapsed: {result['run_metadata']['elapsed_seconds']}s")
            print(f"  [RESULT] Nodes created: {ts['total_nodes_created']}")
            print(f"  [RESULT] Nodes pruned: {ts['pruned_nodes']}")
            print(f"  [RESULT] Grounding calls: {gs['total_calls']}")
            print(f"  [RESULT] Verified: {gs['verified']}")
            print(f"  [RESULT] Contradictions: {gs['contradictions_detected']}")
            print(f"  [RESULT] Entropy H: {result['entropy']['timeline_branching_entropy_H']}")
            print(f"  [RESULT] Entropy valid: {result['entropy']['entropy_valid']}")
            print(f"  [RESULT] Success probability: {result['success_probability']}%")
            print()

            # Print optimal path
            print("  [OPTIMAL PATH]:")
            for step in result["optimal_path"]:
                indent = "    " + ("  " * step["depth"])
                status = "PRUNED" if step["pruned"] else f"WR={step['win_rate']:.3f}"
                print(
                    f"{indent}[D{step['depth']}] {step['name']} "
                    f"(visits={step['visits']}, {status}, "
                    f"P_assumption={step['p_assumption']:.2f}, "
                    f"grounded={step['verified_count']}/{step['grounding_count']})"
                )
            print()

        except Exception as e:
            logger.error(f"Simulation failed for {case['title']}: {e}")
            all_results.append({
                "run_metadata": {"case_title": case["title"], "error": str(e)},
            })
            print(f"  [ERROR] {e}")
            print()

    # Write comprehensive JSON report
    json_path = os.path.join(output_dir, "long_horizon_stress_test.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, default=str)

    # Write markdown summary
    md_path = os.path.join(output_dir, "long_horizon_stress_test.md")
    _write_markdown_report(all_results, md_path)

    print("=" * 72)
    print("  STRESS TEST COMPLETED")
    print(f"  JSON report: {json_path}")
    print(f"  Markdown report: {md_path}")
    print("=" * 72)


def _write_markdown_report(
    results: List[Dict[str, Any]], output_path: str
) -> None:
    """Write a structured markdown report of all simulation results."""
    lines = [
        "# Long-Horizon MCTS Stress Test Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "---",
        "",
    ]

    for result in results:
        meta = result.get("run_metadata", {})
        title = meta.get("case_title", "Unknown")

        if "error" in meta:
            lines.append(f"## {title}")
            lines.append(f"**ERROR**: {meta['error']}")
            lines.append("")
            lines.append("---")
            lines.append("")
            continue

        gs = result.get("grounding_statistics", {})
        ts = result.get("tree_statistics", {})
        entropy = result.get("entropy", {})
        optimal = result.get("optimal_path", [])

        lines.append(f"## {title}")
        lines.append("")
        lines.append("### Simulation Metadata")
        lines.append(f"- **Iterations**: {meta.get('iterations', 'N/A')}")
        lines.append(f"- **Elapsed**: {meta.get('elapsed_seconds', 'N/A')}s")
        lines.append(f"- **Exploration constant (c)**: {meta.get('c_exploration', 'N/A')}")
        lines.append(f"- **Lambda penalty**: {meta.get('lambda_penalty', 'N/A')}")
        lines.append(f"- **Max tree depth**: {meta.get('max_depth', 'N/A')}")
        lines.append(f"- **Grounding budget**: {meta.get('grounding_budget', 'N/A')}")
        lines.append("")
        lines.append("### Tree Statistics")
        lines.append(f"- **Total nodes created**: {ts.get('total_nodes_created', 'N/A')}")
        lines.append(f"- **Pruned nodes**: {ts.get('pruned_nodes', 'N/A')}")
        lines.append(f"- **Active paths**: {ts.get('active_paths', 'N/A')}")
        lines.append(f"- **Max depth reached**: {ts.get('max_depth_reached', 'N/A')}")
        lines.append("")
        lines.append("### Grounding Verification")
        lines.append(f"- **Total grounding calls**: {gs.get('total_calls', 'N/A')}")
        lines.append(f"- **Verified**: {gs.get('verified', 'N/A')}")
        lines.append(f"- **Unverified**: {gs.get('unverified', 'N/A')}")
        lines.append(f"- **Contradictions detected**: {gs.get('contradictions_detected', 'N/A')}")
        lines.append(f"- **Verification rate**: {gs.get('verification_rate', 'N/A')}")
        lines.append("")
        lines.append("### Timeline Branching Entropy")
        lines.append(f"- **H**: {entropy.get('timeline_branching_entropy_H', 'N/A')}")
        lines.append(f"- **Valid**: {entropy.get('entropy_valid', 'N/A')}")
        lines.append(f"- **Interpretation**: {entropy.get('interpretation', 'N/A')}")
        lines.append("")
        lines.append(f"### Success Probability: {result.get('success_probability', 'N/A')}%")
        lines.append("")
        lines.append("### Optimal Path")
        for step in optimal:
            depth = step.get("depth", 0)
            indent = "  " * depth
            status = "PRUNED" if step.get("pruned") else f"WR={step.get('win_rate', 0):.3f}"
            lines.append(
                f"{indent}- **[D{depth}] {step.get('name', '?')}** "
                f"(visits={step.get('visits', 0)}, {status}, "
                f"P_assumption={step.get('p_assumption', 0):.2f}, "
                f"grounded={step.get('verified_count', 0)}/{step.get('grounding_count', 0)})"
            )
        lines.append("")

        # Grounding audit log (first 10 entries)
        audit_log = result.get("grounding_audit_log", [])
        if audit_log:
            lines.append("### Grounding Audit Log (Sample)")
            lines.append("")
            lines.append("| Agent | Node | Verified | P_assumption | Contradiction | Query (truncated) |")
            lines.append("|-------|------|----------|-------------|---------------|-------------------|")
            for entry in audit_log[:10]:
                query_short = entry.get("query", "")[:60]
                lines.append(
                    f"| {entry.get('agent_name', '?')} "
                    f"| {entry.get('node_id', '?')} "
                    f"| {entry.get('verified', '?')} "
                    f"| {entry.get('p_assumption', '?')} "
                    f"| {entry.get('contradiction_detected', '?')} "
                    f"| {query_short} |"
                )
            lines.append("")

        lines.append("---")
        lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# =====================================================================
# MAIN ENTRY POINT
# =====================================================================

if __name__ == "__main__":
    run_stress_test(
        cases=STRESS_TEST_CASES,
        grounding_budget_per_case=30,
    )

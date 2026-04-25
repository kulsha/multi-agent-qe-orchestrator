"""
Agent 6 — Coverage Analyzer Agent
─────────────────────────────────────────────────────────────────
WHAT IT DOES:
    Reads the original user story (structured JSON from Agent 1).
    Reads the generated test cases CSV from Agent 2.
    Reads the review report from Agent 5.
    Maps test cases back to Acceptance Criteria.
    Identifies coverage gaps — ACs with no or weak coverage.
    Calculates a coverage percentage.
    Saves a coverage gap report to /outputs/coverage_report.md

WHY THIS MATTERS:
    Coverage analysis is a QA Lead responsibility.
    Automating it demonstrates leadership-level thinking.
    The coverage % is a key metric for the HTML report (Agent 7).

LLM USED:
    Configurable via --provider flag.
    Groq recommended. One LLM call only.

INPUT  : outputs/US_001_poc_structured.json   (from Agent 1)
         outputs/test_cases/US_001_poc_test_cases.csv (from Agent 2)
         outputs/review_report.md             (from Agent 5)
OUTPUT : outputs/coverage_report.md
─────────────────────────────────────────────────────────────────
"""

import json
import csv
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination

import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.llm_config import get_client, PROVIDERS


# ── Paths ──────────────────────────────────────────────────────

OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"


# ── System Prompt ──────────────────────────────────────────────

SYSTEM_PROMPT = """
You are a Senior QA Lead performing a test coverage analysis.

Your job is to analyse whether the generated test cases
adequately cover all Acceptance Criteria in the user story.

You will be given:
1. The Acceptance Criteria from the user story
2. The generated test cases mapped to each AC
3. A code review report showing script quality

ANALYSIS RULES:
1. Every AC must have at least one Positive test case
2. Every AC must have at least one Negative test case
3. ACs with user input fields need Boundary test cases
4. UI ACs need at least one UI type test case
5. Critical ACs (priority High) need more thorough coverage
6. Test cases flagged as Critical in review reduce coverage confidence

COVERAGE SCORING:
  Full coverage    = Positive + Negative + appropriate Boundary/UI
  Partial coverage = Only Positive OR only Negative
  No coverage      = No test cases mapped to this AC

RESPOND WITH EXACTLY THIS FORMAT:

COVERAGE_SUMMARY:
Total ACs: [number]
Fully Covered: [number]
Partially Covered: [number]
Not Covered: [number]
Coverage Percentage: [number]%

AC_ANALYSIS:
[For each AC write:]
AC_ID: [id]
Title: [title]
Status: [FULL / PARTIAL / NONE]
Test Types Present: [list]
Missing: [what is missing or NONE]
Confidence: [HIGH / MEDIUM / LOW based on review findings]
Notes: [any specific observation]

GAPS_IDENTIFIED:
[numbered list of specific coverage gaps]

RECOMMENDATIONS:
[numbered list of specific recommendations to improve coverage]

END_ANALYSIS
"""


# ── Load Inputs ────────────────────────────────────────────────

def load_structured_json(story_id: str) -> dict:
    """
    Loads the structured JSON output from Agent 1.
    Contains the original ACs from the user story.
    """
    json_path = OUTPUTS_DIR / f"{story_id}_structured.json"
    if not json_path.exists():
        raise FileNotFoundError(
            f"[Agent 6 ERROR] Structured JSON not found: {json_path}"
            f"\nRun Agent 1 first."
        )
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_test_cases(story_id: str) -> list:
    """
    Loads the test cases CSV from Agent 2.
    Returns list of dicts, one per test case row.
    """
    csv_path = OUTPUTS_DIR / "test_cases" / f"{story_id}_test_cases.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"[Agent 6 ERROR] Test cases CSV not found: {csv_path}"
            f"\nRun Agent 2 first."
        )
    test_cases = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            test_cases.append(row)
    return test_cases


def load_review_report(story_id: str) -> str:
    """
    Loads the review report from Agent 5.
    Returns the markdown content as a string.
    Returns empty string if not found — review is optional.
    """
    report_path = OUTPUTS_DIR / "review_report.md"
    if report_path.exists():
        return report_path.read_text(encoding='utf-8')
    return ""


# ── Build Coverage Map ─────────────────────────────────────────

def build_coverage_map(
    acceptance_criteria: list,
    test_cases: list
) -> dict:
    """
    Builds a coverage map showing which test types exist
    for each AC — without LLM involvement.
    This is pure Python logic for accurate counting.

    Returns:
    {
        "AC_001": {
            "title": "...",
            "test_cases": [...],
            "types": ["Positive", "Negative", "Boundary"],
            "count": 7
        }
    }
    """
    coverage = {}

    for ac in acceptance_criteria:
        ac_id = ac.get('id')
        coverage[ac_id] = {
            "title":      ac.get('title', ''),
            "given":      ac.get('given', ''),
            "when":       ac.get('when', ''),
            "then":       ac.get('then', []),
            "test_cases": [],
            "types":      set(),
            "count":      0
        }

    for tc in test_cases:
        ac_id = tc.get('ac_id', '')
        if ac_id in coverage:
            coverage[ac_id]['test_cases'].append(tc)
            coverage[ac_id]['types'].add(tc.get('test_type', 'Unknown'))
            coverage[ac_id]['count'] += 1

    # Convert sets to lists for JSON serialisation
    for ac_id in coverage:
        coverage[ac_id]['types'] = sorted(
            list(coverage[ac_id]['types'])
        )

    return coverage


# ── Build Analysis Prompt ──────────────────────────────────────

def build_analysis_prompt(
    story_data: dict,
    coverage_map: dict,
    review_report: str
) -> str:
    """
    Builds the LLM prompt with all context needed
    for a thorough coverage analysis.
    """
    story = story_data.get('story', {})

    # Format ACs
    acs_str = ""
    for ac_id, ac_data in coverage_map.items():
        acs_str += f"""
AC ID    : {ac_id}
Title    : {ac_data['title']}
Given    : {ac_data['given']}
When     : {ac_data['when']}
Then     : {'; '.join(ac_data['then']) if ac_data['then'] else 'N/A'}
Test Cases Mapped : {ac_data['count']}
Test Types Present: {', '.join(ac_data['types']) if ac_data['types'] else 'NONE'}
Test Case IDs     : {', '.join(tc.get('tc_id','') for tc in ac_data['test_cases'])}
---"""

    # Trim review report to avoid token overuse
    review_summary = review_report[:1500] if review_report else "Not available"

    return f"""
Perform a coverage analysis for this QA pipeline run.

STORY DETAILS:
  Story ID    : {story.get('story_id')}
  Feature     : {story.get('feature')}
  Application : {story.get('application')}

ACCEPTANCE CRITERIA AND TEST COVERAGE:
{acs_str}

OUT OF SCOPE (do not flag as gaps):
{chr(10).join('- ' + item for item in story.get('out_of_scope', []))}

CODE REVIEW SUMMARY (affects coverage confidence):
{review_summary}

Analyse the coverage thoroughly and respond in the exact
format specified in your instructions.
""".strip()


# ── Parse Analysis Response ────────────────────────────────────

def parse_analysis_response(raw: str) -> dict:
    """
    Parses the structured analysis response from the LLM.
    Extracts summary stats, per-AC analysis, gaps, and
    recommendations.
    """
    result = {
        "total_acs":          0,
        "fully_covered":      0,
        "partially_covered":  0,
        "not_covered":        0,
        "coverage_pct":       0,
        "ac_analysis":        [],
        "gaps":               [],
        "recommendations":    [],
        "raw":                raw
    }

    text = raw.strip()

    # Extract summary numbers
    if "COVERAGE_SUMMARY:" in text:
        summary = text.split("COVERAGE_SUMMARY:")[1]
        if "AC_ANALYSIS:" in summary:
            summary = summary.split("AC_ANALYSIS:")[0]
        for line in summary.splitlines():
            line = line.strip().lower()
            try:
                if "total acs:" in line:
                    result["total_acs"] = int(
                        line.split("total acs:")[1].strip()
                    )
                elif "fully covered:" in line:
                    result["fully_covered"] = int(
                        line.split("fully covered:")[1].strip()
                    )
                elif "partially covered:" in line:
                    result["partially_covered"] = int(
                        line.split("partially covered:")[1].strip()
                    )
                elif "not covered:" in line:
                    result["not_covered"] = int(
                        line.split("not covered:")[1].strip()
                    )
                elif "coverage percentage:" in line:
                    pct_str = line.split(
                        "coverage percentage:"
                    )[1].strip().replace('%', '')
                    result["coverage_pct"] = float(pct_str)
            except (ValueError, IndexError):
                pass

    # Extract gaps
    if "GAPS_IDENTIFIED:" in text:
        gaps_block = text.split("GAPS_IDENTIFIED:")[1]
        if "RECOMMENDATIONS:" in gaps_block:
            gaps_block = gaps_block.split("RECOMMENDATIONS:")[0]
        result["gaps"] = [
            line.strip()
            for line in gaps_block.splitlines()
            if line.strip() and not line.strip() == "-"
        ]

    # Extract recommendations
    if "RECOMMENDATIONS:" in text:
        rec_block = text.split("RECOMMENDATIONS:")[1]
        if "END_ANALYSIS" in rec_block:
            rec_block = rec_block.split("END_ANALYSIS")[0]
        result["recommendations"] = [
            line.strip()
            for line in rec_block.splitlines()
            if line.strip() and not line.strip() == "-"
        ]

    return result


# ── Generate Coverage Report ───────────────────────────────────

def generate_coverage_report(
    analysis: dict,
    coverage_map: dict,
    story_id: str
) -> str:
    """
    Generates a Markdown coverage report combining
    the Python-computed coverage map and LLM analysis.
    """
    pct       = analysis.get('coverage_pct', 0)
    gaps      = analysis.get('gaps', [])
    recs      = analysis.get('recommendations', [])

    # Coverage bar
    filled    = int(pct / 10)
    bar       = "█" * filled + "░" * (10 - filled)

    lines = []
    lines.append(f"# Coverage Report — {story_id}")
    lines.append(
        f"\n**Generated:** "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    lines.append(f"**Agent:** Agent 6 — Coverage Analyzer\n")
    lines.append("---\n")

    # Coverage meter
    lines.append("## Coverage Score\n")
    lines.append(f"```")
    lines.append(f"[{bar}] {pct:.0f}%")
    lines.append(f"```\n")

    # Summary table
    lines.append("## Summary\n")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(
        f"| Total Acceptance Criteria | "
        f"{analysis.get('total_acs', len(coverage_map))} |"
    )
    lines.append(
        f"| Fully Covered | "
        f"{analysis.get('fully_covered', 0)} ✅ |"
    )
    lines.append(
        f"| Partially Covered | "
        f"{analysis.get('partially_covered', 0)} ⚠️ |"
    )
    lines.append(
        f"| Not Covered | "
        f"{analysis.get('not_covered', 0)} ❌ |"
    )
    lines.append(
        f"| **Coverage %** | **{pct:.0f}%** |"
    )
    lines.append("")

    # AC breakdown
    lines.append("## AC Coverage Breakdown\n")
    lines.append("| AC ID | Test Cases | Types | Status |")
    lines.append("|---|---|---|---|")
    for ac_id, ac_data in coverage_map.items():
        count  = ac_data['count']
        types  = ', '.join(ac_data['types']) if ac_data['types'] else 'None'
        if count == 0:
            status = "❌ Not Covered"
        elif 'Positive' in ac_data['types'] and 'Negative' in ac_data['types']:
            status = "✅ Full"
        else:
            status = "⚠️ Partial"
        lines.append(f"| {ac_id} | {count} | {types} | {status} |")
    lines.append("")

    # Gaps
    if gaps:
        lines.append("## Coverage Gaps\n")
        for gap in gaps:
            lines.append(f"- {gap}")
        lines.append("")

    # Recommendations
    if recs:
        lines.append("## Recommendations\n")
        for rec in recs:
            lines.append(f"- {rec}")
        lines.append("")

    lines.append("---")
    lines.append(
        "\n*Generated by multi-agent-qe-orchestrator — Agent 6*"
    )

    return "\n".join(lines)


# ── Core Async Runner ──────────────────────────────────────────

async def analyze_coverage(
    story_data: dict,
    coverage_map: dict,
    review_report: str,
    provider: str = "groq"
) -> dict:
    """
    Sends the coverage context to the LLM for analysis.
    Returns parsed analysis dict.
    """
    client = get_client(provider=provider)

    agent = AssistantAgent(
        name="Coverage_Analyzer_Agent",
        model_client=client,
        system_message=SYSTEM_PROMPT
    )

    termination = TextMentionTermination("TERMINATE")
    prompt      = build_analysis_prompt(
        story_data, coverage_map, review_report
    )

    print(f"\n  Running coverage analysis...\n")

    team = RoundRobinGroupChat(
        participants=[agent],
        termination_condition=termination,
        max_turns=2
    )

    result = await team.run(task=prompt)

    assistant_reply = ""
    for msg in result.messages:
        if msg.source != "user":
            assistant_reply = msg.content
            break

    if not assistant_reply:
        print("  ⚠️  No response from LLM")
        return {}

    return parse_analysis_response(assistant_reply)


# ── Main Entry Point ───────────────────────────────────────────

def run(
    story_id: str = "US_001_poc",
    provider: str = "groq"
) -> dict:
    """
    Orchestrates Agent 6 end-to-end:
    1. Loads structured JSON from Agent 1
    2. Loads test cases CSV from Agent 2
    3. Loads review report from Agent 5
    4. Builds Python coverage map
    5. Runs LLM analysis
    6. Generates coverage report markdown
    7. Prints summary

    Args:
        story_id : Story ID e.g. 'US_001_poc'
        provider : LLM provider — groq, ollama, claude
    """
    model_name = PROVIDERS.get(provider, {}).get('model', 'unknown')

    print(f"\n{'='*60}")
    print(f"  AGENT 6 — Coverage Analyzer Agent")
    print(f"{'='*60}")
    print(f"  Story    : {story_id}")
    print(f"  Provider : {provider} — {model_name}")

    # Load all inputs
    story_data    = load_structured_json(story_id)
    test_cases    = load_test_cases(story_id)
    review_report = load_review_report(story_id)

    story = story_data.get('story', {})
    acs   = story.get('acceptance_criteria', [])

    print(f"  ACs loaded        : {len(acs)}")
    print(f"  Test cases loaded : {len(test_cases)}")
    print(
        f"  Review report     : "
        f"{'loaded' if review_report else 'not found'}"
    )

    # Build Python coverage map
    coverage_map = build_coverage_map(acs, test_cases)

    # Print quick coverage preview
    print(f"\n  Coverage Map:")
    for ac_id, ac_data in coverage_map.items():
        types = ', '.join(ac_data['types']) if ac_data['types'] else 'NONE'
        print(
            f"    {ac_id} : "
            f"{ac_data['count']} TCs | "
            f"Types: {types}"
        )

    # Run LLM analysis
    analysis = asyncio.run(
        analyze_coverage(
            story_data, coverage_map, review_report, provider
        )
    )

    if not analysis:
        print("\n  ❌ Analysis failed.")
        return {}

    # Generate and save report
    report_md   = generate_coverage_report(
        analysis, coverage_map, story_id
    )
    report_path = OUTPUTS_DIR / "coverage_report.md"
    report_path.write_text(report_md, encoding='utf-8')

    # Print summary
    pct = analysis.get('coverage_pct', 0)

    print(f"\n{'='*60}")
    print(f"  ✅ Coverage Analysis Complete")
    print(f"\n  Total ACs          : {analysis.get('total_acs', 0)}")
    print(f"  Fully Covered      : {analysis.get('fully_covered', 0)} ✅")
    print(f"  Partially Covered  : {analysis.get('partially_covered', 0)} ⚠️")
    print(f"  Not Covered        : {analysis.get('not_covered', 0)} ❌")
    print(f"\n  Coverage           : {pct:.0f}%")
    print(f"\n  Gaps identified    : {len(analysis.get('gaps', []))}")
    print(f"  Recommendations    : {len(analysis.get('recommendations', []))}")
    print(f"\n  Report saved to    : {report_path}")
    print(f"{'='*60}\n")

    return {
        "analysis":    analysis,
        "coverage_map": coverage_map,
        "report_path": str(report_path)
    }


# ── CLI ────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Agent 6 — Coverage Analyzer Agent"
    )
    parser.add_argument(
        "--story",
        type=str,
        default="US_001_poc",
        help="Story ID to analyze e.g. US_001_poc"
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="groq",
        help="LLM provider: groq, ollama, claude"
    )
    args = parser.parse_args()
    run(args.story, args.provider)
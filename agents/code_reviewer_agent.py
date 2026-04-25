"""
Agent 5 — Code Reviewer Agent
─────────────────────────────────────────────────────────────────
WHAT IT DOES:
    Reads generated Playwright test scripts from Agent 4.
    Reviews each script for quality issues.
    Produces a review report with findings and suggestions.
    Saves improved scripts back to /outputs/scripts/reviewed/
    Saves review report to /outputs/review_report.md

WHAT IT CHECKS:
    - Missing or weak assertions
    - Hardcoded test data outside of variables
    - Missing waits / flaky patterns (time.sleep usage)
    - POM compliance (direct locators in test vs using POM)
    - Missing error handling
    - Descriptive test function names
    - Missing docstrings
    - Duplicate test coverage

LLM USED:
    Configurable via --provider flag.
    Groq recommended. Claude Haiku for best review quality.

INPUT  : outputs/scripts/test_ac_*.py
         pages/loginpage.py
OUTPUT : outputs/scripts/reviewed/test_ac_*.py
         outputs/review_report.md
─────────────────────────────────────────────────────────────────
"""

import asyncio
import argparse
from pathlib import Path
from datetime import datetime

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination

import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.llm_config import get_client, PROVIDERS


# ── Paths ──────────────────────────────────────────────────────

OUTPUTS_DIR  = Path(__file__).parent.parent / "outputs"
SCRIPTS_DIR  = OUTPUTS_DIR / "scripts"
REVIEWED_DIR = SCRIPTS_DIR / "reviewed"
PAGES_DIR    = Path(__file__).parent.parent / "pages"


# ── System Prompt ──────────────────────────────────────────────

SYSTEM_PROMPT = """
You are a Senior QA Automation Architect conducting a thorough
code review of Playwright Python test scripts.

Your job is to review each test script and produce:
1. A list of specific issues found
2. An improved version of the script

REVIEW CHECKLIST — check every item:

ASSERTIONS:
- Every test must have at least one expect() assertion
- Assertions must be specific — not just element_visible
- URL assertions must use re.compile() not string equality
- Error message assertions must check actual text content

WAITS AND STABILITY:
- No time.sleep() usage — use wait_for_load_state instead
- Network requests should wait for networkidle
- Dynamic elements need explicit waits before interaction

POM COMPLIANCE:
- Tests must use Page Object class methods not raw locators
- No page.locator() calls directly in test functions
- All interactions through POM methods only

TEST DATA:
- No hardcoded credentials in assertion strings
- Test data should come from variables or fixtures
- Username and password must be parameterised

STRUCTURE:
- Every test function needs a docstring
- Function names must describe what is being tested
- Imports must be complete and correct
- pytest.mark.asyncio decorator on every async test

RESPOND WITH EXACTLY THIS FORMAT — nothing else:

ISSUES_FOUND:
[numbered list of specific issues]

SEVERITY_SUMMARY:
Critical: [count]
Major: [count]
Minor: [count]

IMPROVED_SCRIPT:
[complete improved Python code — no markdown fences]

END_REVIEW
"""


# ── Build Review Prompt ────────────────────────────────────────

def build_review_prompt(
    script_name: str,
    script_code: str,
    pom_code: str
) -> str:
    """
    Builds the review prompt for one test script.
    Includes the POM class for context so the reviewer
    can check POM compliance accurately.
    """
    return f"""
Review this Playwright Python test script.

SCRIPT NAME: {script_name}

POM CLASS (for reference):
{pom_code}

TEST SCRIPT TO REVIEW:
{script_code}

Review thoroughly against all checklist items.
Respond with ISSUES_FOUND, SEVERITY_SUMMARY,
IMPROVED_SCRIPT, and END_REVIEW exactly as instructed.
""".strip()


# ── Parse Review Response ──────────────────────────────────────

def parse_review_response(raw: str) -> dict:
    """
    Parses the structured review response from the LLM.
    Extracts issues, severity summary, and improved script.
    Returns a dict with all parsed sections.
    """
    result = {
        "issues":           [],
        "critical":         0,
        "major":            0,
        "minor":            0,
        "improved_script":  "",
        "raw":              raw
    }

    text = raw.strip()

    # Extract issues
    if "ISSUES_FOUND:" in text and "SEVERITY_SUMMARY:" in text:
        issues_block = text.split("ISSUES_FOUND:")[1]
        issues_block = issues_block.split("SEVERITY_SUMMARY:")[0].strip()
        result["issues"] = [
            line.strip()
            for line in issues_block.splitlines()
            if line.strip() and not line.strip() == "-"
        ]

    # Extract severity counts
    if "SEVERITY_SUMMARY:" in text:
        severity_block = text.split("SEVERITY_SUMMARY:")[1]
        if "IMPROVED_SCRIPT:" in severity_block:
            severity_block = severity_block.split("IMPROVED_SCRIPT:")[0]
        for line in severity_block.splitlines():
            line = line.strip().lower()
            if "critical:" in line:
                try:
                    result["critical"] = int(
                        line.split("critical:")[1].strip()
                    )
                except ValueError:
                    pass
            elif "major:" in line:
                try:
                    result["major"] = int(
                        line.split("major:")[1].strip()
                    )
                except ValueError:
                    pass
            elif "minor:" in line:
                try:
                    result["minor"] = int(
                        line.split("minor:")[1].strip()
                    )
                except ValueError:
                    pass

    # Extract improved script
    if "IMPROVED_SCRIPT:" in text:
        script_block = text.split("IMPROVED_SCRIPT:")[1]
        if "END_REVIEW" in script_block:
            script_block = script_block.split("END_REVIEW")[0]
        script_block = script_block.strip()

        # Strip markdown fences if present
        if "```python" in script_block:
            script_block = script_block.split("```python")[1]
            script_block = script_block.split("```")[0]
        elif "```" in script_block:
            parts        = script_block.split("```")
            script_block = max(parts, key=len)

        result["improved_script"] = script_block.strip()

    return result


# ── Generate Markdown Report ───────────────────────────────────

def generate_report(
    reviews: list,
    story_id: str
) -> str:
    """
    Generates a Markdown review report from all script reviews.
    Includes per-file findings, severity breakdown, and summary.
    """
    total_critical = sum(r.get('critical', 0) for r in reviews)
    total_major    = sum(r.get('major', 0)    for r in reviews)
    total_minor    = sum(r.get('minor', 0)    for r in reviews)
    total_issues   = total_critical + total_major + total_minor
    total_files    = len(reviews)

    lines = []
    lines.append(f"# Code Review Report — {story_id}")
    lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Agent:** Agent 5 — Code Reviewer")
    lines.append(f"**Files Reviewed:** {total_files}")
    lines.append(f"\n---\n")

    # Summary table
    lines.append("## Summary\n")
    lines.append("| Severity | Count |")
    lines.append("|---|---|")
    lines.append(f"| 🔴 Critical | {total_critical} |")
    lines.append(f"| 🟡 Major    | {total_major} |")
    lines.append(f"| 🟢 Minor    | {total_minor} |")
    lines.append(f"| **Total**  | **{total_issues}** |")
    lines.append("")

    # Readiness assessment
    if total_critical == 0 and total_major <= 2:
        readiness = "✅ READY — Scripts are production quality"
    elif total_critical == 0:
        readiness = "⚠️ NEEDS WORK — Major issues should be fixed"
    else:
        readiness = "❌ NOT READY — Critical issues must be resolved"

    lines.append(f"**Readiness:** {readiness}\n")
    lines.append("---\n")

    # Per file details
    lines.append("## File-by-File Review\n")

    for review in reviews:
        filename = review.get('filename', 'unknown')
        issues   = review.get('issues', [])
        critical = review.get('critical', 0)
        major    = review.get('major', 0)
        minor    = review.get('minor', 0)

        lines.append(f"### {filename}\n")
        lines.append(
            f"**Severity:** 🔴 {critical} Critical | "
            f"🟡 {major} Major | "
            f"🟢 {minor} Minor\n"
        )

        if issues:
            lines.append("**Issues Found:**\n")
            for issue in issues:
                lines.append(f"- {issue}")
            lines.append("")
        else:
            lines.append("**No issues found — clean script ✅**\n")

        lines.append("---\n")

    # Footer
    lines.append("\n*Generated by multi-agent-qe-orchestrator — Agent 5*")

    return "\n".join(lines)


# ── Core Async Runner ──────────────────────────────────────────

async def review_scripts(
    script_files: list,
    pom_code: str,
    provider: str = "groq"
) -> list:
    """
    Reviews each test script file.
    Saves improved scripts to /outputs/scripts/reviewed/
    Returns list of review result dicts.
    """
    client = get_client(provider=provider)

    agent = AssistantAgent(
        name="Code_Reviewer_Agent",
        model_client=client,
        system_message=SYSTEM_PROMPT
    )

    termination = TextMentionTermination("TERMINATE")
    REVIEWED_DIR.mkdir(parents=True, exist_ok=True)

    reviews = []
    total   = len(script_files)

    print(f"\n  Reviewing {total} script file(s)...\n")

    for i, script_path in enumerate(script_files, 1):
        script_path = Path(script_path)
        filename    = script_path.name

        print(f"  [{i}/{total}] Reviewing {filename}")

        if not script_path.exists():
            print(f"  ⚠️  File not found — skipping")
            continue

        script_code = script_path.read_text(encoding='utf-8')
        prompt      = build_review_prompt(
            filename, script_code, pom_code
        )

        try:
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
                print(f"  ⚠️  No response — skipping")
                continue

            review = parse_review_response(assistant_reply)
            review['filename'] = filename

            # Save improved script if generated
            if review.get('improved_script'):
                reviewed_path = REVIEWED_DIR / filename
                reviewed_path.write_text(
                    review['improved_script'], encoding='utf-8'
                )
                print(
                    f"  ✅ Reviewed — "
                    f"🔴 {review['critical']} Critical | "
                    f"🟡 {review['major']} Major | "
                    f"🟢 {review['minor']} Minor"
                )
            else:
                print(f"  ⚠️  No improved script in response")

            reviews.append(review)
            await asyncio.sleep(4)

        except Exception as e:
            error_str = str(e)
            if any(c in error_str for c in ['429', '413', 'rate_limit']):
                print(f"  ⏳ Rate limit — waiting 60s...")
                await asyncio.sleep(60)
            else:
                print(f"  ❌ Error: {str(e)[:80]}")
            continue

    return reviews


# ── Main Entry Point ───────────────────────────────────────────

def run(
    story_id: str = "US_001_poc",
    provider: str = "groq"
) -> dict:
    """
    Orchestrates Agent 5 end-to-end:
    1. Finds all generated test scripts for the story
    2. Loads the POM class for context
    3. Reviews each script file
    4. Saves improved scripts to /reviewed/ subfolder
    5. Generates markdown review report
    6. Prints summary

    Args:
        story_id : Story ID to review e.g. 'US_001_poc'
        provider : LLM provider — groq, ollama, claude
    """
    model_name = PROVIDERS.get(provider, {}).get('model', 'unknown')

    # Find all test scripts for this story
    script_files = sorted(SCRIPTS_DIR.glob(f"test_ac_*_{story_id}.py"))

    if not script_files:
        raise FileNotFoundError(
            f"\n[Agent 5 ERROR] No test scripts found for {story_id}"
            f"\nExpected files matching: test_ac_*_{story_id}.py"
            f"\nRun Agent 4 first: "
            f"python agents/script_generator_agent.py"
        )

    # Load POM class for review context
    pom_file = PAGES_DIR / "loginpage.py"
    pom_code = ""
    if pom_file.exists():
        pom_code = pom_file.read_text(encoding='utf-8')
        print(f"  POM loaded : {pom_file.name}")
    else:
        print(f"  ⚠️  POM file not found — reviewing without context")

    print(f"\n{'='*60}")
    print(f"  AGENT 5 — Code Reviewer Agent")
    print(f"{'='*60}")
    print(f"  Story    : {story_id}")
    print(f"  Scripts  : {len(script_files)}")
    print(f"  Provider : {provider} — {model_name}")
    for f in script_files:
        print(f"    • {f.name}")

    # Run reviews
    reviews = asyncio.run(
        review_scripts(
            [str(f) for f in script_files],
            pom_code,
            provider
        )
    )

    if not reviews:
        print("\n  ❌ No reviews completed.")
        return {}

    # Generate report
    report_md   = generate_report(reviews, story_id)
    report_path = OUTPUTS_DIR / "review_report.md"
    report_path.write_text(report_md, encoding='utf-8')

    # Summary
    total_critical = sum(r.get('critical', 0) for r in reviews)
    total_major    = sum(r.get('major', 0)    for r in reviews)
    total_minor    = sum(r.get('minor', 0)    for r in reviews)

    print(f"\n{'='*60}")
    print(f"  ✅ Code Review Complete")
    print(f"\n  Files reviewed   : {len(reviews)}")
    print(f"  Issues found     :")
    print(f"    🔴 Critical    : {total_critical}")
    print(f"    🟡 Major       : {total_major}")
    print(f"    🟢 Minor       : {total_minor}")
    print(f"\n  Improved scripts : {REVIEWED_DIR}")
    print(f"  Review report    : {report_path}")

    if total_critical == 0 and total_major <= 2:
        print(f"\n  Readiness : ✅ READY for Agent 6")
    elif total_critical == 0:
        print(f"\n  Readiness : ⚠️  NEEDS WORK before Agent 6")
    else:
        print(f"\n  Readiness : ❌ CRITICAL issues found")

    print(f"{'='*60}\n")

    return {
        "reviews":     reviews,
        "report_path": str(report_path)
    }


# ── CLI ────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Agent 5 — Code Reviewer Agent"
    )
    parser.add_argument(
        "--story",
        type=str,
        default="US_001_poc",
        help="Story ID to review e.g. US_001_poc"
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="groq",
        help="LLM provider: groq, ollama, claude"
    )
    args = parser.parse_args()
    run(args.story, args.provider)
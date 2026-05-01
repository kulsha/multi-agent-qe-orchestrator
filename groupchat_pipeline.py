"""
groupchat_pipeline.py — AutoGen GroupChat Orchestration
─────────────────────────────────────────────────────────────────
WHAT IT DOES:
    Wires all 7 QA agents into a SelectorGroupChat team.
    Uses a deterministic custom selector function for routing.
    Each agent has a tool that executes real pipeline work.

    KEY FEATURE — INTELLIGENT RE-ROUTING:
    If Agent 5 finds more than 3 critical issues it signals
    re-route back to Agent 4 for script regeneration.
    Maximum 2 re-route attempts before proceeding.

    WHY CUSTOM SELECTOR:
    LLM-based selectors hallucinate in long pipelines.
    A deterministic Python function routes reliably based
    on signal keywords in the last message — production grade.

USAGE:
    python groupchat_pipeline.py \
        --story US_001_login_poc.md \
        --provider claude

COMPARISON WITH main.py:
    main.py              — Sequential, fixed order, fast
    groupchat_pipeline.py — SelectorGroupChat, dynamic re-routing
─────────────────────────────────────────────────────────────────
"""

import argparse
import asyncio
import csv as csv_module
from datetime import datetime
from pathlib import Path
from typing import Sequence

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import BaseChatMessage
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import (
    TextMentionTermination,
    MaxMessageTermination
)

import sys
sys.path.append(str(Path(__file__).parent))
from config.llm_config import get_client

from agents.story_intake_agent       import run as run_agent1
from agents.test_case_designer_agent import run as run_agent2
from agents.script_outline_agent     import run as run_agent3
from agents.script_generator_agent   import run as run_agent4
from agents.code_reviewer_agent      import run as run_agent5
from agents.coverage_analyzer_agent  import run as run_agent6
from agents.report_generator_agent   import run as run_agent7


# ── Paths ──────────────────────────────────────────────────────

ROOT        = Path(__file__).parent
STORIES_DIR = ROOT / "stories"
OUTPUTS_DIR = ROOT / "outputs"


# ── Shared Pipeline Context ────────────────────────────────────

class PipelineContext:
    """Shared state across all tool functions."""
    story_file        = ""
    story_id          = ""
    provider          = "claude"
    reroute_count     = 0
    max_reroutes      = 2
    reroute_threshold = 3
    completed         = []
    started_at        = None


# ── Deterministic Selector Function ───────────────────────────

def pipeline_selector(
    messages: Sequence[BaseChatMessage]
) -> str | None:
    """
    Deterministic routing function for SelectorGroupChat.
    Routes based on signal keywords in the last message.
    No LLM involved — 100% reliable routing.

    Returns the name of the next agent to speak,
    or None to let the default selector decide.
    """
    if not messages:
        return "StoryIntakeAgent"

    # Find last non-user message
    last_content = ""
    for msg in reversed(messages):
        content = getattr(msg, 'content', '')
        source  = getattr(msg, 'source', '')
        if source != 'user' and content:
            last_content = str(content)
            break

    if not last_content:
        return "StoryIntakeAgent"

    # Strict keyword-based routing
    if "PIPELINE_COMPLETE" in last_content:
        return None  # Stop

    if "AGENT_6_COMPLETE" in last_content:
        return "ReportGenerator"

    if "AGENT_5_COMPLETE" in last_content:
        return "CoverageAnalyzer"

    if "REROUTE_TO_AGENT_4" in last_content:
        return "ScriptGenerator"

    if "AGENT_4_COMPLETE" in last_content:
        return "CodeReviewer"

    if "AGENT_3_COMPLETE" in last_content:
        return "ScriptGenerator"

    if "HUMAN_APPROVED" in last_content:
        return "ScriptOutlineAgent"

    if "HUMAN_REJECTED" in last_content:
        return None  # Stop

    if "AWAITING_HUMAN_APPROVAL" in last_content:
        return "HumanApprover"

    if "AGENT_2_COMPLETE" in last_content:
        return "HumanApprover"

    if "AGENT_1_COMPLETE" in last_content:
        return "TestCaseDesigner"

    # Default — start from beginning
    return "StoryIntakeAgent"


# ── Tool Functions (Real Pipeline Work) ────────────────────────

def tool_run_story_intake() -> str:
    """Execute Agent 1 — parse user story into structured JSON."""
    print(f"\n  🔧 Executing Agent 1 — Story Intake...")
    try:
        result   = run_agent1(PipelineContext.story_file)
        story    = result.get('story', {})
        story_id = story.get('story_id', 'unknown')
        ac_count = story.get('acceptance_criteria_count', 0)
        PipelineContext.story_id = story_id
        PipelineContext.completed.append('Agent1')
        print(f"  ✅ Agent 1 — story_id={story_id} ACs={ac_count}")
        return (
            f"AGENT_1_COMPLETE | story_id={story_id} | "
            f"acs={ac_count} | "
            f"output=outputs/{story_id}_structured.json"
        )
    except Exception as e:
        return f"AGENT_1_FAILED | error={str(e)[:100]}"


def tool_run_test_case_designer() -> str:
    """Execute Agent 2 — generate test cases from structured JSON."""
    print(f"\n  🔧 Executing Agent 2 — Test Case Designer...")
    try:
        structured_file = f"{PipelineContext.story_id}_structured.json"
        run_agent2(structured_file, provider=PipelineContext.provider)

        # Read results directly from CSV
        csv_path = (
            OUTPUTS_DIR / "test_cases" /
            f"{PipelineContext.story_id}_test_cases.csv"
        )
        tc_count = 0
        tc_types = {}
        if csv_path.exists():
            with open(csv_path, 'r', encoding='utf-8') as f:
                rows = list(csv_module.DictReader(f))
            tc_count = len(rows)
            for row in rows:
                t = row.get('test_type', 'Unknown')
                tc_types[t] = tc_types.get(t, 0) + 1

        PipelineContext.completed.append('Agent2')
        print(f"  ✅ Agent 2 — {tc_count} test cases")
        return (
            f"AGENT_2_COMPLETE | test_cases={tc_count} | "
            f"positive={tc_types.get('Positive', 0)} "
            f"negative={tc_types.get('Negative', 0)} "
            f"boundary={tc_types.get('Boundary', 0)} "
            f"ui={tc_types.get('UI', 0)} | "
            f"AWAITING_HUMAN_APPROVAL"
        )
    except Exception as e:
        csv_path = (
            OUTPUTS_DIR / "test_cases" /
            f"{PipelineContext.story_id}_test_cases.csv"
        )
        if csv_path.exists():
            PipelineContext.completed.append('Agent2')
            return (
                f"AGENT_2_COMPLETE | "
                f"output={str(csv_path)} | "
                f"AWAITING_HUMAN_APPROVAL"
            )
        return f"AGENT_2_FAILED | error={str(e)[:100]}"


def tool_human_checkpoint() -> str:
    """Human approval checkpoint — pause for Y/N input."""
    print(f"\n{'='*60}")
    print(f"  ⏸  CHECKPOINT — Human Approval Required")
    print(f"{'='*60}")
    print(f"\n  Review the test cases generated above.")
    print(f"  Continue to script generation?\n")
    print(f"  [Y] Yes — continue autonomously")
    print(f"  [N] No  — stop pipeline\n")

    while True:
        try:
            choice = input("  Your choice (Y/N): ").strip().upper()
            if choice == 'Y':
                print(f"\n  ✅ Approved — continuing...\n")
                return "HUMAN_APPROVED"
            elif choice == 'N':
                print(f"\n  🛑 Pipeline stopped.\n")
                return "HUMAN_REJECTED | PIPELINE_COMPLETE"
            else:
                print("  Please type Y or N.")
        except KeyboardInterrupt:
            return "PIPELINE_COMPLETE"


def tool_run_script_outline() -> str:
    """Execute Agent 3 — create script outlines from test cases."""
    print(f"\n  🔧 Executing Agent 3 — Script Outline...")
    try:
        csv_file = f"{PipelineContext.story_id}_test_cases.csv"
        result   = run_agent3(
            csv_file,
            provider=PipelineContext.provider
        )
        count = result.get('total_cases', 0)
        pom   = list(result.get('pom_summary', {}).keys())
        PipelineContext.completed.append('Agent3')
        print(f"  ✅ Agent 3 — {count} outlines")
        return (
            f"AGENT_3_COMPLETE | outlines={count} | "
            f"pom={','.join(pom)} | "
            f"output=outputs/features/"
            f"{PipelineContext.story_id}_script_outline.json"
        )
    except Exception as e:
        return f"AGENT_3_FAILED | error={str(e)[:100]}"


def tool_run_script_generator() -> str:
    """Execute Agent 4 — generate Playwright scripts from outlines."""
    attempt = PipelineContext.reroute_count + 1
    print(
        f"\n  🔧 Executing Agent 4 — Script Generator "
        f"(attempt {attempt})..."
    )
    try:
        if PipelineContext.reroute_count > 0:
            scripts_dir  = OUTPUTS_DIR / "scripts"
            reviewed_dir = scripts_dir / "reviewed"
            for f in scripts_dir.glob(
                f"test_ac_*_{PipelineContext.story_id}.py"
            ):
                f.unlink()
            if reviewed_dir.exists():
                for f in reviewed_dir.glob("*.py"):
                    f.unlink()
            print(f"  🔄 Old scripts deleted for regeneration")

        outline_file = (
            f"{PipelineContext.story_id}_script_outline.json"
        )
        result  = run_agent4(
            outline_file,
            provider=PipelineContext.provider
        )
        scripts = result.get('script_files', [])
        pom     = result.get('pom_files', {})
        PipelineContext.completed.append(f'Agent4_attempt_{attempt}')
        print(
            f"  ✅ Agent 4 — "
            f"{len(scripts)} scripts (attempt {attempt})"
        )
        return (
            f"AGENT_4_COMPLETE | scripts={len(scripts)} | "
            f"pom={list(pom.keys())} | attempt={attempt}"
        )
    except Exception as e:
        return f"AGENT_4_FAILED | error={str(e)[:100]}"


def tool_run_code_reviewer() -> str:
    """Execute Agent 5 — review scripts, signal re-route if needed."""
    print(f"\n  🔧 Executing Agent 5 — Code Reviewer...")
    try:
        result   = run_agent5(
            PipelineContext.story_id,
            provider=PipelineContext.provider
        )
        reviews  = result.get('reviews', [])
        critical = sum(r.get('critical', 0) for r in reviews)
        major    = sum(r.get('major', 0) for r in reviews)
        minor    = sum(r.get('minor', 0) for r in reviews)

        needs_reroute = (
            critical > PipelineContext.reroute_threshold and
            PipelineContext.reroute_count < PipelineContext.max_reroutes
        )

        if needs_reroute:
            PipelineContext.reroute_count += 1
            print(
                f"\n  ⚠️  Re-routing to Agent 4 "
                f"(attempt {PipelineContext.reroute_count}"
                f"/{PipelineContext.max_reroutes}) "
                f"— {critical} critical issues"
            )
            return (
                f"REROUTE_TO_AGENT_4 | "
                f"critical={critical} major={major} minor={minor} | "
                f"reroute_attempt={PipelineContext.reroute_count}"
            )
        else:
            if PipelineContext.reroute_count >= PipelineContext.max_reroutes:
                print(
                    f"  ⚠️  Max re-routes reached — "
                    f"proceeding with {critical} issues"
                )
            PipelineContext.completed.append('Agent5')
            print(
                f"  ✅ Agent 5 — "
                f"{critical} critical {major} major"
            )
            return (
                f"AGENT_5_COMPLETE | "
                f"critical={critical} major={major} minor={minor} | "
                f"reroutes_used={PipelineContext.reroute_count}"
            )
    except Exception as e:
        return f"AGENT_5_FAILED | error={str(e)[:100]}"


def tool_run_coverage_analyzer() -> str:
    """Execute Agent 6 — analyze test coverage against ACs."""
    print(f"\n  🔧 Executing Agent 6 — Coverage Analyzer...")
    try:
        result   = run_agent6(
            PipelineContext.story_id,
            provider=PipelineContext.provider
        )
        analysis = result.get('analysis', {})
        pct      = analysis.get('coverage_pct', 0)
        gaps     = len(analysis.get('gaps', []))
        PipelineContext.completed.append('Agent6')
        print(f"  ✅ Agent 6 — {pct:.0f}% coverage")
        return (
            f"AGENT_6_COMPLETE | "
            f"acs={analysis.get('total_acs', 0)} | "
            f"fully_covered={analysis.get('fully_covered', 0)} | "
            f"coverage={pct:.0f}% | gaps={gaps}"
        )
    except Exception as e:
        return f"AGENT_6_FAILED | error={str(e)[:100]}"


def tool_run_report_generator() -> str:
    """Execute Agent 7 — generate HTML executive dashboard."""
    print(f"\n  🔧 Executing Agent 7 — Report Generator...")
    try:
        run_agent7(
            PipelineContext.story_id,
            provider=PipelineContext.provider
        )
        PipelineContext.completed.append('Agent7')
        print(f"  ✅ Agent 7 — HTML report generated")
        return (
            f"AGENT_7_COMPLETE | "
            f"report=outputs/pipeline_report.html | "
            f"pages=docs/index.html | "
            f"PIPELINE_COMPLETE"
        )
    except Exception as e:
        return (
            f"AGENT_7_FAILED | error={str(e)[:100]} | "
            f"PIPELINE_COMPLETE"
        )


# ── Strict Agent System Message ────────────────────────────────

def strict_system_message(agent_name: str, tool_name: str) -> str:
    return (
        f"You are {agent_name}. "
        f"When activated call {tool_name} immediately. "
        f"Output only the tool result. "
        f"Do not write any other text."
    )


# ── Build GroupChat Team ────────────────────────────────────────

def build_team(provider: str) -> SelectorGroupChat:
    """
    Builds SelectorGroupChat with deterministic custom selector.
    Each agent has one tool executing real pipeline work.
    Routing is handled by pipeline_selector — not LLM.
    """
    client = get_client(provider=provider)

    story_agent = AssistantAgent(
        name="StoryIntakeAgent",
        description="Parses user story. Always runs first.",
        model_client=client,
        tools=[tool_run_story_intake],
        system_message=strict_system_message(
            "StoryIntakeAgent", "tool_run_story_intake"
        )
    )

    tc_agent = AssistantAgent(
        name="TestCaseDesigner",
        description=(
            "Generates test cases. "
            "Runs after AGENT_1_COMPLETE."
        ),
        model_client=client,
        tools=[tool_run_test_case_designer],
        system_message=strict_system_message(
            "TestCaseDesigner", "tool_run_test_case_designer"
        )
    )

    human_agent = AssistantAgent(
        name="HumanApprover",
        description=(
            "Human checkpoint. "
            "Runs after AWAITING_HUMAN_APPROVAL."
        ),
        model_client=client,
        tools=[tool_human_checkpoint],
        system_message=strict_system_message(
            "HumanApprover", "tool_human_checkpoint"
        )
    )

    outline_agent = AssistantAgent(
        name="ScriptOutlineAgent",
        description=(
            "Creates script outlines. "
            "Runs after HUMAN_APPROVED."
        ),
        model_client=client,
        tools=[tool_run_script_outline],
        system_message=strict_system_message(
            "ScriptOutlineAgent", "tool_run_script_outline"
        )
    )

    script_agent = AssistantAgent(
        name="ScriptGenerator",
        description=(
            "Generates Playwright scripts. "
            "Runs after AGENT_3_COMPLETE or REROUTE_TO_AGENT_4."
        ),
        model_client=client,
        tools=[tool_run_script_generator],
        system_message=strict_system_message(
            "ScriptGenerator", "tool_run_script_generator"
        )
    )

    reviewer_agent = AssistantAgent(
        name="CodeReviewer",
        description=(
            "Reviews scripts. Runs after AGENT_4_COMPLETE. "
            "Outputs REROUTE_TO_AGENT_4 if critical > 3."
        ),
        model_client=client,
        tools=[tool_run_code_reviewer],
        system_message=strict_system_message(
            "CodeReviewer", "tool_run_code_reviewer"
        )
    )

    coverage_agent = AssistantAgent(
        name="CoverageAnalyzer",
        description=(
            "Analyzes coverage. "
            "Runs after AGENT_5_COMPLETE."
        ),
        model_client=client,
        tools=[tool_run_coverage_analyzer],
        system_message=strict_system_message(
            "CoverageAnalyzer", "tool_run_coverage_analyzer"
        )
    )

    report_agent = AssistantAgent(
        name="ReportGenerator",
        description=(
            "Generates HTML report. Always runs last. "
            "Outputs PIPELINE_COMPLETE."
        ),
        model_client=client,
        tools=[tool_run_report_generator],
        system_message=strict_system_message(
            "ReportGenerator", "tool_run_report_generator"
        )
    )

    termination = (
        TextMentionTermination("PIPELINE_COMPLETE") |
        MaxMessageTermination(40)
    )

    return SelectorGroupChat(
        participants=[
            story_agent,
            tc_agent,
            human_agent,
            outline_agent,
            script_agent,
            reviewer_agent,
            coverage_agent,
            report_agent
        ],
        model_client=client,
        termination_condition=termination,
        selector_func=pipeline_selector
    )


# ── Banner ─────────────────────────────────────────────────────

def print_banner(story_file: str, provider: str):
    print(f"\n{'='*60}")
    print(f"  QA GROUPCHAT PIPELINE")
    print(f"{'='*60}")
    print(f"  Story       : {story_file}")
    print(f"  Provider    : {provider}")
    print(f"  Mode        : SelectorGroupChat — dynamic routing")
    print(f"  Selector    : Deterministic Python function")
    print(f"  Re-routing  : Auto (critical > 3, max 2 attempts)")
    print(f"  Agents      : 7 + HumanApprover")
    print(f"  Started     : {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}\n")


# ── Summary ────────────────────────────────────────────────────

def print_summary():
    elapsed = (
        datetime.now() - PipelineContext.started_at
    ).total_seconds()
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)

    print(f"\n{'='*60}")
    print(f"  ✅ GROUPCHAT PIPELINE COMPLETE")
    print(f"{'='*60}")
    print(f"  Duration   : {minutes}m {seconds}s")
    print(f"  Re-routes  : {PipelineContext.reroute_count}")
    print(f"\n  Agents completed:")
    for stage in PipelineContext.completed:
        print(f"    ✅ {stage}")
    print(f"\n  Report     : outputs/pipeline_report.html")
    print(f"  Open with  : start outputs\\pipeline_report.html")
    print(f"{'='*60}\n")


# ── Main ───────────────────────────────────────────────────────

async def run_groupchat(story_file: str, provider: str):
    """
    Runs the 7-agent QA pipeline using SelectorGroupChat
    with a deterministic custom selector function.
    """
    PipelineContext.story_file    = story_file
    PipelineContext.provider      = provider
    PipelineContext.started_at    = datetime.now()
    PipelineContext.completed     = []
    PipelineContext.reroute_count = 0

    print_banner(story_file, provider)

    story_path = STORIES_DIR / story_file
    if not story_path.exists():
        print(f"  ❌ Story not found: {story_path}")
        return

    print(f"  Building GroupChat team...")
    team = build_team(provider)
    print(f"  ✅ Team ready — 8 participants")
    print(f"  ✅ SelectorGroupChat + deterministic selector")
    print(f"\n  Starting pipeline...\n")

    task = (
        f"Start QA pipeline for: {story_file}. "
        f"StoryIntakeAgent runs first."
    )

    try:
        async for message in team.run_stream(task=task):
            if hasattr(message, 'source') and hasattr(message, 'content'):
                source  = message.source
                content = str(message.content)

                if source == 'user':
                    continue

                # Show clean signal outputs only
                if any(sig in content for sig in [
                    'AGENT_1_COMPLETE', 'AGENT_2_COMPLETE',
                    'AGENT_3_COMPLETE', 'AGENT_4_COMPLETE',
                    'AGENT_5_COMPLETE', 'AGENT_6_COMPLETE',
                    'AGENT_7_COMPLETE', 'REROUTE_TO_AGENT_4',
                    'AWAITING_HUMAN_APPROVAL', 'HUMAN_APPROVED',
                    'PIPELINE_COMPLETE'
                ]):
                    print(f"\n  ✅ [{source}] {content[:120]}")

    except Exception as e:
        print(f"\n  ❌ GroupChat error: {str(e)[:300]}")

    print_summary()


# ── CLI ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="QA GroupChat Pipeline — dynamic agent routing"
    )
    parser.add_argument(
        "--story",
        type=str,
        required=True,
        help="Story filename e.g. US_001_login_poc.md"
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="claude",
        help="LLM provider: claude, groq, ollama"
    )
    args = parser.parse_args()
    asyncio.run(run_groupchat(args.story, args.provider))


if __name__ == "__main__":
    main()
"""
main.py — QA Multi-Agent Pipeline Entry Point
─────────────────────────────────────────────────────────────────
WHAT IT DOES:
    Orchestrates all 7 agents in sequence.
    Passes outputs from one agent as inputs to the next.
    Skips agents whose outputs already exist — saves tokens.
    Pauses after Agent 2 for human approval before
    generating scripts.
    Runs fully autonomous from Agent 3 onwards.

USAGE:
    python main.py --story US_001_login_poc.md --provider groq
    python main.py --story US_001_login_poc.md --provider ollama
    python main.py --story US_001_login_poc.md --provider claude

    # Force re-run all agents even if outputs exist
    python main.py --story US_001_login_poc.md --provider groq --force

PROVIDERS:
    groq   — Groq LLaMA3 (free tier, 100k tokens/day)
    ollama — Local Mistral (unlimited, offline)
    claude — Claude Haiku (pay as you go, best quality)
    openai — GPT-4o-mini (pay as you go)

CHECKPOINT:
    Pipeline pauses after Agent 2 (Test Case Designer).
    You review test cases and approve before scripts
    are generated. Type Y to continue, N to stop.

SKIP LOGIC:
    Each agent checks if its output already exists.
    If yes it is skipped — no LLM call made.
    Use --force to override and re-run everything.
─────────────────────────────────────────────────────────────────
"""

import argparse
import sys
import time
import csv as csv_module
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Import all agents
from agents.story_intake_agent       import run as run_agent1
from agents.test_case_designer_agent import run as run_agent2
from agents.script_outline_agent     import run as run_agent3
from agents.script_generator_agent   import run as run_agent4
from agents.code_reviewer_agent      import run as run_agent5
from agents.coverage_analyzer_agent  import run as run_agent6
from agents.report_generator_agent   import run as run_agent7


# ── Paths helper ───────────────────────────────────────────────

ROOT = Path(__file__).parent


def outputs(relative: str) -> Path:
    return ROOT / "outputs" / relative


# ── Pipeline State ─────────────────────────────────────────────

class PipelineState:
    """
    Tracks pipeline execution state across all agents.
    Records timing, outputs, and any errors per stage.
    """
    def __init__(self, story_file: str, provider: str, force: bool):
        self.story_file = story_file
        self.provider   = provider
        self.force      = force
        self.started_at = datetime.now()
        self.stages     = {}
        self.story_id   = None
        self.failed     = False
        self.stopped    = False

    def record(
        self, agent: int, name: str,
        result, elapsed: float, skipped: bool = False
    ):
        self.stages[agent] = {
            "name":    name,
            "result":  result,
            "elapsed": elapsed,
            "status":  "⏭️  Skipped" if skipped else "✅ Done"
        }

    def fail(self, agent: int, name: str, error: str):
        self.stages[agent] = {
            "name":   name,
            "error":  error,
            "status": "❌ Failed"
        }
        self.failed = True

    def total_elapsed(self) -> float:
        return (datetime.now() - self.started_at).total_seconds()


# ── Banner ─────────────────────────────────────────────────────

def print_banner(story_file: str, provider: str, force: bool):
    print(f"\n{'='*60}")
    print(f"  QA MULTI-AGENT PIPELINE")
    print(f"{'='*60}")
    print(f"  Story    : {story_file}")
    print(f"  Provider : {provider}")
    print(f"  Mode     : {'FORCE — re-run all agents' if force else 'SMART — skip completed'}")
    print(f"  Agents   : 7")
    print(f"  Started  : {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}\n")


# ── Stage Header ───────────────────────────────────────────────

def print_stage(agent_num: int, name: str):
    print(f"\n{'─'*60}")
    print(f"  AGENT {agent_num} — {name}")
    print(f"{'─'*60}")


# ── Skip Check Helper ──────────────────────────────────────────

def should_skip(output_path: Path, force: bool, label: str) -> bool:
    """
    Returns True if the output already exists and force is False.
    Prints a clear skip message with the file path.
    """
    if not force and output_path.exists():
        print(f"\n  ⏭️  Skipping — {label} already exists")
        print(f"  {output_path}")
        return True
    return False


# ── Checkpoint ─────────────────────────────────────────────────

def human_checkpoint(state: PipelineState) -> bool:
    """
    Pauses pipeline after Agent 2 for human approval.
    Shows test case summary before asking Y/N.
    Returns True to continue, False to stop.
    """
    csv_file = outputs(
        f"test_cases/{state.story_id}_test_cases.csv"
    )

    print(f"\n{'='*60}")
    print(f"  ⏸  CHECKPOINT — Human Approval Required")
    print(f"{'='*60}")

    if csv_file.exists():
        with open(csv_file, 'r', encoding='utf-8') as f:
            rows = list(csv_module.DictReader(f))

        type_counts = {}
        for row in rows:
            t = row.get('test_type', 'Unknown')
            type_counts[t] = type_counts.get(t, 0) + 1

        print(f"\n  Agent 2 generated {len(rows)} test cases:\n")
        for t_type, count in type_counts.items():
            print(f"    {t_type:<12} : {count}")

        print(f"\n  CSV: {csv_file}")

    print(f"\n  Review the test cases above.")
    print(f"  Continue to script generation?\n")
    print(f"  [Y] Yes — continue (fully autonomous from here)")
    print(f"  [N] No  — stop pipeline here")
    print()

    while True:
        try:
            choice = input("  Your choice (Y/N): ").strip().upper()
            if choice == 'Y':
                print(f"\n  ✅ Approved — continuing pipeline...\n")
                return True
            elif choice == 'N':
                print(f"\n  🛑 Pipeline stopped by user.")
                print(f"  Re-run same command to restart.\n")
                return False
            else:
                print(f"  Please type Y or N.")
        except KeyboardInterrupt:
            print(f"\n\n  Pipeline interrupted.")
            return False


# ── Final Summary ──────────────────────────────────────────────

def print_summary(state: PipelineState):
    """
    Prints a clean summary of the entire pipeline run.
    """
    elapsed = state.total_elapsed()
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)

    print(f"\n{'='*60}")
    if state.stopped:
        print(f"  🛑 PIPELINE STOPPED BY USER")
    elif state.failed:
        print(f"  ❌ PIPELINE FAILED")
    else:
        print(f"  ✅ PIPELINE COMPLETE")
    print(f"{'='*60}")

    print(f"\n  Story    : {state.story_file}")
    print(f"  Provider : {state.provider}")
    print(f"  Duration : {minutes}m {seconds}s")
    print(f"\n  Agent Results:")
    print(f"  {'─'*40}")

    for agent_num in sorted(state.stages.keys()):
        stage     = state.stages[agent_num]
        name      = stage.get('name', '')
        status    = stage.get('status', '')
        elapsed_s = stage.get('elapsed', 0)
        print(
            f"  Agent {agent_num}  {name:<28} "
            f"{status}  ({elapsed_s:.0f}s)"
        )

    if not state.failed and not state.stopped:
        report_path = outputs("pipeline_report.html")
        if report_path.exists():
            print(f"\n  📊 Report : {report_path}")
            print(f"\n  Open with:")
            print(f"  start outputs\\pipeline_report.html")

    print(f"{'='*60}\n")


# ── Main Pipeline ──────────────────────────────────────────────

def run_pipeline(story_file: str, provider: str, force: bool = False):
    """
    Runs all 7 agents in sequence.
    Skips agents whose output files already exist
    unless --force is passed.
    Stops cleanly if any agent fails.
    """
    state = PipelineState(story_file, provider, force)
    print_banner(story_file, provider, force)

    # ── AGENT 1 — Story Intake ─────────────────────────────────
    # Agent 1 always runs — it is fast (no LLM) and we need
    # story_id to determine file names for all other agents.
    print_stage(1, "Story Intake Agent")
    t0 = time.time()
    try:
        result1        = run_agent1(story_file)
        story          = result1.get('story', {})
        state.story_id = story.get('story_id', 'unknown')
        elapsed        = time.time() - t0
        state.record(1, "Story Intake", result1, elapsed)
        print(f"\n  Story ID  : {state.story_id}")
        print(f"  ACs found : {story.get('acceptance_criteria_count', 0)}")
    except Exception as e:
        state.fail(1, "Story Intake", str(e))
        print(f"\n  ❌ Agent 1 failed: {e}")
        print_summary(state)
        return

    # ── AGENT 2 — Test Case Designer ──────────────────────────
    print_stage(2, "Test Case Designer Agent")
    t0 = time.time()
    try:
        csv_path = outputs(
            f"test_cases/{state.story_id}_test_cases.csv"
        )
        skipped = should_skip(csv_path, force, "test cases CSV")
        if skipped:
            result2 = {}
        else:
            structured_file = f"{state.story_id}_structured.json"
            result2         = run_agent2(structured_file)
        elapsed = time.time() - t0
        state.record(2, "Test Case Designer", result2, elapsed, skipped)
    except Exception as e:
        state.fail(2, "Test Case Designer", str(e))
        print(f"\n  ❌ Agent 2 failed: {e}")
        print_summary(state)
        return

    # ── CHECKPOINT ─────────────────────────────────────────────
    approved = human_checkpoint(state)
    if not approved:
        state.stopped = True
        print_summary(state)
        return

    # ── AGENT 3 — Script Outline ───────────────────────────────
    print_stage(3, "Script Outline Agent")
    t0 = time.time()
    try:
        outline_path = outputs(
            f"features/{state.story_id}_script_outline.json"
        )
        skipped = should_skip(outline_path, force, "script outline JSON")
        if skipped:
            result3 = {}
        else:
            csv_file = f"{state.story_id}_test_cases.csv"
            result3  = run_agent3(csv_file, provider=provider)
        elapsed = time.time() - t0
        state.record(3, "Script Outline", result3, elapsed, skipped)
    except Exception as e:
        state.fail(3, "Script Outline", str(e))
        print(f"\n  ❌ Agent 3 failed: {e}")
        print_summary(state)
        return

    # ── AGENT 4 — Script Generator ─────────────────────────────
    print_stage(4, "Script Generator Agent")
    t0 = time.time()
    try:
        scripts_dir = outputs("scripts")
        existing    = list(
            scripts_dir.glob(f"test_ac_*_{state.story_id}.py")
        ) if scripts_dir.exists() else []

        if existing and not force:
            print(
                f"\n  ⏭️  Skipping — "
                f"{len(existing)} script file(s) already exist"
            )
            for f in existing:
                print(f"  • {f.name}")
            result4 = {}
            skipped = True
        else:
            outline_file = f"{state.story_id}_script_outline.json"
            result4      = run_agent4(outline_file, provider=provider)
            skipped      = False
        elapsed = time.time() - t0
        state.record(4, "Script Generator", result4, elapsed, skipped)
    except Exception as e:
        state.fail(4, "Script Generator", str(e))
        print(f"\n  ❌ Agent 4 failed: {e}")
        print_summary(state)
        return

    # ── AGENT 5 — Code Reviewer ────────────────────────────────
    print_stage(5, "Code Reviewer Agent")
    t0 = time.time()
    try:
        reviewed_dir  = outputs("scripts/reviewed")
        review_report = outputs("review_report.md")
        existing      = (
            list(reviewed_dir.glob("*.py"))
            if reviewed_dir.exists() else []
        )
        skipped = (
            bool(existing) and
            review_report.exists() and
            not force
        )
        if skipped:
            print(
                f"\n  ⏭️  Skipping — "
                f"{len(existing)} reviewed file(s) + report exist"
            )
            result5 = {}
        else:
            result5 = run_agent5(state.story_id, provider=provider)
        elapsed = time.time() - t0
        state.record(5, "Code Reviewer", result5, elapsed, skipped)
    except Exception as e:
        state.fail(5, "Code Reviewer", str(e))
        print(f"\n  ❌ Agent 5 failed: {e}")
        print_summary(state)
        return

    # ── AGENT 6 — Coverage Analyzer ───────────────────────────
    print_stage(6, "Coverage Analyzer Agent")
    t0 = time.time()
    try:
        coverage_report = outputs("coverage_report.md")
        skipped = should_skip(
            coverage_report, force, "coverage report"
        )
        if skipped:
            result6 = {}
        else:
            result6 = run_agent6(state.story_id, provider=provider)
        elapsed = time.time() - t0
        state.record(6, "Coverage Analyzer", result6, elapsed, skipped)
    except Exception as e:
        state.fail(6, "Coverage Analyzer", str(e))
        print(f"\n  ❌ Agent 6 failed: {e}")
        print_summary(state)
        return

    # ── AGENT 7 — Report Generator ─────────────────────────────
    print_stage(7, "Report Generator Agent")
    t0 = time.time()
    try:
        html_report = outputs("pipeline_report.html")
        skipped     = should_skip(
            html_report, force, "HTML pipeline report"
        )
        if skipped:
            result7 = {}
        else:
            result7 = run_agent7(state.story_id, provider=provider)
        elapsed = time.time() - t0
        state.record(7, "Report Generator", result7, elapsed, skipped)
    except Exception as e:
        state.fail(7, "Report Generator", str(e))
        print(f"\n  ❌ Agent 7 failed: {e}")
        print_summary(state)
        return

    # ── Done ───────────────────────────────────────────────────
    print_summary(state)


# ── CLI ────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="QA Multi-Agent Pipeline — main entry point"
    )
    parser.add_argument(
        "--story",
        type=str,
        required=True,
        help="User story filename inside /stories/ "
             "e.g. US_001_login_poc.md"
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="groq",
        help="LLM provider: groq, ollama, claude, openai"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Force re-run all agents even if outputs exist"
    )
    args = parser.parse_args()
    run_pipeline(args.story, args.provider, args.force)
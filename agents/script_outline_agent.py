"""
Agent 3 — Test Script Outline Agent
─────────────────────────────────────────────────────────────────
WHAT IT DOES:
    Reads the test cases CSV from Agent 2.
    Sends one minimal LLM call per test case.
    Produces structured JSON outlines with exact Playwright
    actions, locators, and assertions per test case.
    Builds a POM summary from all outlines.
    Saves output to /outputs/features/

WHY THIS INSTEAD OF BDD:
    Framework-agnostic, produces higher quality scripts in
    Agent 4, maps directly to real enterprise QA workflows.

LLM USED:
    Configurable — Groq or any provider via --provider flag.
    Includes JSON repair for smaller local models.

INPUT  : outputs/test_cases/US_001_test_cases.csv
OUTPUT : outputs/features/US_001_script_outline.json
─────────────────────────────────────────────────────────────────
"""

import json
import csv
import asyncio
import argparse
import re
from pathlib import Path
from collections import defaultdict

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination

import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.llm_config import get_client, PROVIDERS


# ── Paths ──────────────────────────────────────────────────────

OUTPUTS_DIR   = Path(__file__).parent.parent / "outputs"
TEST_CASE_DIR = OUTPUTS_DIR / "test_cases"
OUTLINE_DIR   = OUTPUTS_DIR / "features"


# ── System Prompt ──────────────────────────────────────────────

SYSTEM_PROMPT = """
You are a Senior Test Automation Architect for Playwright Python.
Convert test cases into structured JSON outlines for code generation.

RULES:
1. One JSON array with exactly one outline object per response.
2. Infer CSS or name-attribute locators for OrangeHRM elements.
3. Map each test step to a Playwright action.
4. End with specific, verifiable assertions.
5. Use POM naming conventions for locator names.
6. No markdown fences. No explanation. Raw JSON array only.
7. Use only double quotes in JSON. No trailing commas.

PLAYWRIGHT ACTIONS: navigate, fill, click, clear, wait, get_text, get_attr
ASSERTION TYPES: url_contains, element_visible, element_hidden,
                 text_contains, text_equals, attr_equals, not_url_contains

REQUIRED JSON FIELDS PER OUTLINE:
tc_id, ac_id, title, test_type, priority, page_object, target_url,
locators (name/strategy/value/description),
actions (step/action/target/value/description),
assertions (type/target/value/description),
test_data
"""


# ── Load CSV ───────────────────────────────────────────────────

def load_test_cases(csv_path: Path) -> list:
    """
    Reads the CSV produced by Agent 2.
    Returns a list of dicts, one per test case row.
    """
    test_cases = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row['test_data'] = json.loads(row.get('test_data', '{}'))
            except json.JSONDecodeError:
                row['test_data'] = {}
            test_cases.append(row)
    return test_cases


# ── Build Single Prompt ────────────────────────────────────────

def build_single_prompt(tc: dict, target_url: str) -> str:
    """
    Builds a minimal prompt for a single test case.
    Deliberately short to conserve tokens.
    """
    steps = " | ".join(
        tc.get('test_steps', '').split(' | ')[:5]
    )

    return f"""
Convert this QA test case to a Playwright outline JSON array (1 item).

TC_ID: {tc.get('tc_id')} | AC: {tc.get('ac_id')} | Type: {tc.get('test_type')}
Title: {tc.get('title')}
URL: {target_url}
Steps: {steps}
Expected: {tc.get('expected_result', '')[:120]}
Data: {json.dumps(tc.get('test_data', {}))}

Return ONLY a JSON array with one outline object.
Use double quotes only. No trailing commas. No markdown.
""".strip()


# ── Parse LLM Response ─────────────────────────────────────────

def parse_llm_response(raw: str, expect_list: bool = False):
    """
    Extracts JSON from LLM response.
    Includes aggressive cleaning for small local models that
    occasionally produce slightly malformed JSON.
    """
    text = raw.strip()

    # Strip markdown fences
    if "```" in text:
        lines = [l for l in text.splitlines()
                 if not l.strip().startswith("```")]
        text  = "\n".join(lines).strip()

    # Remove control characters that break JSON parsing
    # (common in llama3.2 3B output)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    # Fix trailing commas before closing brackets/braces
    text = re.sub(r',\s*}', '}', text)
    text = re.sub(r',\s*]', ']', text)

    # Fix single quotes used instead of double quotes
    # Only applies to keys and simple string values
    text = re.sub(r"'([^']*)'", r'"\1"', text)

    # Remove any text before the JSON starts
    if expect_list:
        start = text.find('[')
        end   = text.rfind(']') + 1
        if start == -1 or end == 0:
            raise ValueError(
                f"[Agent 3 ERROR] No JSON array found.\n"
                f"Raw:\n{raw[:400]}"
            )
        return json.loads(text[start:end])
    else:
        start = text.find('{')
        end   = text.rfind('}') + 1
        if start == -1 or end == 0:
            raise ValueError(
                f"[Agent 3 ERROR] No JSON object found.\n"
                f"Raw:\n{raw[:400]}"
            )
        return json.loads(text[start:end])


# ── Build POM Summary ──────────────────────────────────────────

def build_pom_summary(outlines: list) -> dict:
    """
    Analyses all outlines and produces a consolidated POM plan.
    All Page Object classes needed, their locators, and
    the methods each class should expose.
    Agent 4 uses this to generate POM class files first
    before writing individual test scripts.
    """
    pages = {}

    for outline in outlines:
        if not isinstance(outline, dict):
            continue

        page_name = outline.get('page_object', 'UnknownPage')

        if page_name not in pages:
            pages[page_name] = {
                "class_name": page_name,
                "target_url": outline.get('target_url', ''),
                "locators":   {},
                "methods":    set()
            }

        # Collect unique locators per page
        for loc in outline.get('locators', []):
            if not isinstance(loc, dict):
                continue
            loc_name = loc.get('name')
            if loc_name and loc_name not in pages[page_name]['locators']:
                pages[page_name]['locators'][loc_name] = loc

        # Infer methods from action sequences
        actions = [
            a.get('action') for a in outline.get('actions', [])
            if isinstance(a, dict)
        ]
        if 'fill' in actions and 'click' in actions:
            pages[page_name]['methods'].add('login(username, password)')
        if 'navigate' in actions:
            pages[page_name]['methods'].add('navigate()')

        for assertion in outline.get('assertions', []):
            if not isinstance(assertion, dict):
                continue
            if assertion.get('type') == 'url_contains':
                pages[page_name]['methods'].add('get_current_url()')
            if assertion.get('type') in ['text_contains', 'text_equals']:
                target = assertion.get('target', '')
                if target:
                    pages[page_name]['methods'].add(
                        f"get_{target}_text()"
                    )
            if assertion.get('type') == 'element_visible':
                target = assertion.get('target', '')
                if target:
                    pages[page_name]['methods'].add(
                        f"is_{target}_visible()"
                    )

    pom_summary = {}
    for page_name, page_data in pages.items():
        pom_summary[page_name] = {
            "class_name": page_data['class_name'],
            "target_url": page_data['target_url'],
            "locators":   list(page_data['locators'].values()),
            "methods":    sorted(list(page_data['methods']))
        }

    return pom_summary


# ── Core Async Runner ──────────────────────────────────────────

async def generate_outlines(
    test_cases: list,
    target_url: str,
    provider: str = "groq"
) -> list:
    """
    Sends one minimal LLM call per test case.
    Saves progress after each successful call so the pipeline
    resumes automatically if interrupted mid-run.
    """
    client = get_client(provider=provider)

    agent = AssistantAgent(
        name="Script_Outline_Agent",
        model_client=client,
        system_message=SYSTEM_PROMPT
    )

    termination = TextMentionTermination("TERMINATE")
    outlines    = []

    # Progress file — enables resume on interruption
    OUTLINE_DIR.mkdir(parents=True, exist_ok=True)
    progress_path = OUTLINE_DIR / "progress_temp.json"

    completed_ids = set()
    if progress_path.exists():
        with open(progress_path, 'r') as f:
            outlines      = json.load(f)
            completed_ids = {o.get('tc_id') for o in outlines
                             if isinstance(o, dict)}
        print(f"\n  Resuming — {len(completed_ids)} already completed\n")
    else:
        print(f"\n  Processing {len(test_cases)} test cases...\n")

    total = len(test_cases)

    for i, tc in enumerate(test_cases, 1):
        tc_id = tc.get('tc_id', f'TC_{i}')

        if tc_id in completed_ids:
            print(f"  [{i}/{total}] Skipping {tc_id} — already done")
            continue

        print(
            f"  [{i}/{total}] Outlining {tc_id} — "
            f"{tc.get('title', '')[:45]}"
        )

        prompt      = build_single_prompt(tc, target_url)
        max_retries = 3
        retry_delay = 12

        for attempt in range(max_retries):
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
                    break

                parsed = parse_llm_response(
                    assistant_reply, expect_list=True
                )

                if parsed and isinstance(parsed, list) and len(parsed) > 0:
                    outline = parsed[0]
                    if not isinstance(outline, dict):
                        print(f"  ⚠️  Unexpected format — skipping")
                        break

                    outlines.append(outline)

                    # Save progress after each success
                    with open(progress_path, 'w') as f:
                        json.dump(outlines, f, indent=2)

                    loc  = len([l for l in outline.get('locators', [])
                                if isinstance(l, dict)])
                    act  = len([a for a in outline.get('actions', [])
                                if isinstance(a, dict)])
                    asrt = len([a for a in outline.get('assertions', [])
                                if isinstance(a, dict)])
                    print(
                        f"  ✅ {loc} locators | "
                        f"{act} actions | "
                        f"{asrt} assertions"
                    )

                # Polite delay between calls
                await asyncio.sleep(4)
                break

            except Exception as e:
                error_str = str(e)
                if any(code in error_str
                       for code in ['429', '413', 'rate_limit']):
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        print(
                            f"  ⏳ Rate limit — waiting {wait_time}s "
                            f"(retry {attempt + 1}/{max_retries - 1})..."
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        print(f"  ❌ Failed after {max_retries} attempts.")
                        print(f"  💡 Re-run same command to resume.")
                        with open(progress_path, 'w') as f:
                            json.dump(outlines, f, indent=2)
                        return outlines
                else:
                    print(f"  ❌ Error: {str(e)[:80]}")
                    break

    # Clean up progress file on full completion
    if progress_path.exists():
        progress_path.unlink()
        print(f"\n  Progress file cleaned up.")

    return outlines


# ── Main Entry Point ───────────────────────────────────────────

def run(
    csv_file: str,
    target_url: str = None,
    provider: str = "groq"
) -> dict:
    """
    Orchestrates Agent 3 end-to-end:
    1. Loads test cases CSV from Agent 2
    2. Calls LLM once per test case with minimal prompt
    3. Builds POM summary from all outlines
    4. Saves full output JSON to /outputs/features/
    5. Returns the complete outline package
    """
    csv_path = TEST_CASE_DIR / csv_file

    if not csv_path.exists():
        raise FileNotFoundError(
            f"\n[Agent 3 ERROR] CSV not found: {csv_path}"
            f"\nRun Agent 2 first: "
            f"python agents/test_case_designer_agent.py"
        )

    story_id   = csv_file.replace('_test_cases.csv', '')
    model_name = PROVIDERS.get(provider, {}).get('model', 'unknown')

    if not target_url:
        target_url = (
            "https://opensource-demo.orangehrmlive.com"
            "/web/index.php/auth/login"
        )

    test_cases = load_test_cases(csv_path)

    print(f"\n{'='*60}")
    print(f"  AGENT 3 — Test Script Outline Agent")
    print(f"{'='*60}")
    print(f"  Story      : {story_id}")
    print(f"  Test Cases : {len(test_cases)}")
    print(f"  Target URL : {target_url}")
    print(f"  Provider   : {provider} — {model_name}")

    # Delete stale empty progress file if present
    progress_path = OUTLINE_DIR / "progress_temp.json"
    if progress_path.exists():
        with open(progress_path, 'r') as f:
            try:
                existing = json.load(f)
                if len(existing) == 0:
                    progress_path.unlink()
                    print(f"  Cleared empty progress file.")
            except Exception:
                progress_path.unlink()
                print(f"  Cleared corrupt progress file.")

    outlines = asyncio.run(
        generate_outlines(test_cases, target_url, provider)
    )

    if not outlines:
        print("\n  ❌ No outlines generated. Check LLM responses above.")
        return {}

    pom_summary = build_pom_summary(outlines)

    output = {
        "story_id":    story_id,
        "total_cases": len(outlines),
        "pom_summary": pom_summary,
        "outlines":    outlines
    }

    OUTLINE_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTLINE_DIR / f"{story_id}_script_outline.json"

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    total_locators   = sum(
        len([l for l in o.get('locators', []) if isinstance(l, dict)])
        for o in outlines if isinstance(o, dict)
    )
    total_actions    = sum(
        len([a for a in o.get('actions', []) if isinstance(a, dict)])
        for o in outlines if isinstance(o, dict)
    )
    total_assertions = sum(
        len([a for a in o.get('assertions', []) if isinstance(a, dict)])
        for o in outlines if isinstance(o, dict)
    )

    print(f"\n  ✅ Outline Generation Complete")
    print(f"\n  Outlines generated   : {len(outlines)}")
    print(f"  Total locators       : {total_locators}")
    print(f"  Total actions        : {total_actions}")
    print(f"  Total assertions     : {total_assertions}")
    print(f"\n  POM Classes identified:")
    for page_name, page_data in pom_summary.items():
        print(f"    • {page_name}")
        print(f"      Locators : {len(page_data['locators'])}")
        print(f"      Methods  : {len(page_data['methods'])}")
    print(f"\n  Output → {output_path}")
    print(f"{'='*60}\n")

    return output


# ── CLI ────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Agent 3 — Test Script Outline Agent"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="US_001_test_cases.csv",
        help="CSV filename from Agent 2 inside /outputs/test_cases/"
    )
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="Override target application URL (optional)"
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="groq",
        help="LLM provider: groq, gemini, openai, ollama"
    )
    args = parser.parse_args()
    run(args.input, args.url, args.provider)
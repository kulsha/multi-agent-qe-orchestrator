"""
Agent 4 — Script Generator Agent
─────────────────────────────────────────────────────────────────
WHAT IT DOES:
    Reads the script outline JSON from Agent 3.
    Generates the Page Object Model (POM) class file first.
    Then generates one Playwright test script per AC —
    grouping all test cases for that AC into one file.
    Saves POM to /pages/ and scripts to /outputs/scripts/

OUTPUT STRUCTURE:
    pages/loginpage.py
    outputs/scripts/test_AC_001_successful_login.py
    outputs/scripts/test_AC_002_login_fails.py
    outputs/scripts/test_AC_003_ui_elements.py

LLM USED:
    Configurable via --provider flag.
    Groq recommended for quality. Ollama for development.

INPUT  : outputs/features/US_001_poc_script_outline.json
OUTPUT : pages/loginpage.py
         outputs/scripts/test_AC_XXX_*.py
─────────────────────────────────────────────────────────────────
"""

import json
import asyncio
import argparse
from pathlib import Path
from collections import defaultdict

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination

import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.llm_config import get_client, PROVIDERS


# ── Paths ──────────────────────────────────────────────────────

OUTPUTS_DIR  = Path(__file__).parent.parent / "outputs"
SCRIPTS_DIR  = OUTPUTS_DIR / "scripts"
FEATURES_DIR = OUTPUTS_DIR / "features"
PAGES_DIR    = Path(__file__).parent.parent / "pages"


# ── System Prompt — POM Generator ─────────────────────────────

POM_SYSTEM_PROMPT = """
You are a Senior Test Automation Engineer specialising in
Python Playwright with Page Object Model pattern.

Your job is to generate a clean, production-ready Python
Page Object Model class from a POM specification.

RULES:
1. Class must accept page as constructor parameter.
2. All locators defined as properties using page.locator().
3. Locator strategy mapping:
   name  → page.locator("[name='value']")
   css   → page.locator("value")
   id    → page.locator("#value")
   xpath → page.locator("xpath=value")
   text  → page.locator("text=value")
4. Each method must have a clear docstring.
5. Use async/await throughout.
6. Use explicit waits — never time.sleep().
7. Return self from action methods for chaining.
8. No hardcoded test data in POM — pass as parameters.
9. Include navigate(), login(), get_error_message() methods.
10. Respond with ONLY Python code. No markdown. No explanation.
"""


# ── System Prompt — Test Script Generator ─────────────────────

SCRIPT_SYSTEM_PROMPT = """
You are a Senior Test Automation Engineer specialising in
Python Playwright with pytest and Page Object Model pattern.

Your job is to generate a complete pytest test file containing
multiple test functions — one per test case outline provided.

RULES:
1. One pytest async test function per test case.
2. Import the Page Object class from pages/ folder.
3. Use @pytest.mark.asyncio decorator on each test function.
4. Use playwright async_playwright for browser setup inside each test.
5. Follow the exact actions and assertions from each outline.
6. Assertion mapping:
   url_contains     → expect(page).to_have_url(re.compile(pattern))
   element_visible  → expect(page.locator(loc)).to_be_visible()
   element_hidden   → expect(page.locator(loc)).to_be_hidden()
   text_contains    → expect(page.locator(loc)).to_contain_text(text)
   text_equals      → expect(page.locator(loc)).to_have_text(text)
   attr_equals      → expect(page.locator(loc)).to_have_attribute(attr,val)
   not_url_contains → expect(page).not_to_have_url(re.compile(pattern))
7. Each test function named: test_{tc_id_lowercase}
8. Each test has a clear docstring.
9. Group tests under a comment block showing the AC ID and title.
10. Respond with ONLY Python code. No markdown. No explanation.
"""


# ── Build POM Prompt ───────────────────────────────────────────

def build_pom_prompt(pom_spec: dict, page_name: str) -> str:
    """
    Builds the LLM prompt for generating the POM class.
    """
    locators_str = "\n".join(
        f"  - name: {l.get('name')} | "
        f"strategy: {l.get('strategy')} | "
        f"value: {l.get('value')} | "
        f"desc: {l.get('description')}"
        for l in pom_spec.get('locators', [])
        if isinstance(l, dict)
    )

    methods_str = "\n".join(
        f"  - {m}" for m in pom_spec.get('methods', [])
    )

    return f"""
Generate a Python Playwright Page Object Model class.

CLASS NAME : {page_name}
FILE       : pages/{page_name.lower()}.py
TARGET URL : {pom_spec.get('target_url', '')}

LOCATORS:
{locators_str}

METHODS TO IMPLEMENT:
{methods_str}

Generate the complete Python class. Include all imports.
Raw Python only. No markdown fences.
""".strip()


# ── Build AC Script Prompt ─────────────────────────────────────

def build_ac_script_prompt(
    ac_id: str,
    ac_title: str,
    outlines: list,
    page_class_name: str
) -> str:
    """
    Builds the LLM prompt for generating one test file
    containing all test cases for a single AC.
    """
    tc_blocks = ""
    for outline in outlines:
        if not isinstance(outline, dict):
            continue

        tc_id  = outline.get('tc_id', '')
        title  = outline.get('title', '')
        t_type = outline.get('test_type', '')

        actions_str = "\n".join(
            f"      Step {a.get('step')}: {a.get('action')} "
            f"on '{a.get('target')}' "
            f"{'value=' + str(a.get('value')) if a.get('value') else ''}"
            for a in outline.get('actions', [])
            if isinstance(a, dict)
        )

        assertions_str = "\n".join(
            f"      Assert {a.get('type')} — "
            f"target='{a.get('target')}' "
            f"value='{a.get('value')}' — "
            f"{a.get('description')}"
            for a in outline.get('assertions', [])
            if isinstance(a, dict)
        )

        test_data = json.dumps(outline.get('test_data', {}))

        tc_blocks += f"""
  TEST CASE {tc_id}:
    Title     : {title}
    Type      : {t_type}
    Test Data : {test_data}
    Actions   :
{actions_str}
    Assertions:
{assertions_str}
---"""

    return f"""
Generate a complete Python pytest file for this Acceptance Criterion.

AC ID    : {ac_id}
AC TITLE : {ac_title}
FILE     : outputs/scripts/test_{ac_id.lower()}_{ac_title.lower().replace(' ', '_')[:30]}.py

PAGE OBJECT : {page_class_name}
Import from : pages.{page_class_name.lower()}

TEST CASES TO IMPLEMENT ({len(outlines)} total):
{tc_blocks}

REQUIREMENTS:
- One async test function per test case
- Function names: test_{{tc_id_lowercase}} e.g. test_tc_001_001
- Use async_playwright() context manager inside each test
- Add AC group comment before the first test
- All imports at top including: re, pytest, pytest_asyncio,
  async_playwright from playwright.async_api,
  expect from playwright.async_api
- Raw Python only. No markdown fences.
""".strip()


# ── Extract Code ───────────────────────────────────────────────

def extract_code(raw: str) -> str:
    """
    Extracts clean Python code from LLM response.
    Strips markdown fences and leading explanation text.
    """
    text = raw.strip()

    if "```python" in text:
        text = text.split("```python", 1)[1]
        text = text.split("```")[0].strip()
    elif "```" in text:
        parts = text.split("```")
        text  = max(parts, key=len).strip()

    lines      = text.splitlines()
    code_start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if (stripped.startswith('import ') or
                stripped.startswith('from ') or
                stripped.startswith('class ') or
                stripped.startswith('def ') or
                stripped.startswith('#')):
            code_start = i
            break

    return "\n".join(lines[code_start:]).strip()


# ── Consolidate POM Summary ────────────────────────────────────

def consolidate_pom(pom_summary: dict) -> dict:
    """
    Merges 'Login Page' and 'LoginPage' into one clean entry.
    Handles LLM inconsistency in page object naming.
    """
    consolidated = {}

    for page_name, page_data in pom_summary.items():
        clean_name = page_name.replace(" ", "")

        if clean_name not in consolidated:
            consolidated[clean_name] = {
                "class_name": clean_name,
                "target_url": page_data.get('target_url', ''),
                "locators":   list(page_data.get('locators', [])),
                "methods":    list(page_data.get('methods', []))
            }
        else:
            # Merge locators
            existing = {
                l.get('name')
                for l in consolidated[clean_name]['locators']
                if isinstance(l, dict)
            }
            for loc in page_data.get('locators', []):
                if isinstance(loc, dict):
                    if loc.get('name') not in existing:
                        consolidated[clean_name]['locators'].append(loc)
                        existing.add(loc.get('name'))

            # Merge methods
            existing_methods = set(consolidated[clean_name]['methods'])
            for method in page_data.get('methods', []):
                existing_methods.add(method)
            consolidated[clean_name]['methods'] = sorted(
                list(existing_methods)
            )

    return consolidated


# ── Group Outlines by AC ───────────────────────────────────────

def group_by_ac(outlines: list) -> dict:
    """
    Groups outline objects by their AC ID.
    Returns OrderedDict: { 'AC_001': [outline, ...], ... }
    Also extracts AC title from outline title heuristically.
    """
    groups = defaultdict(list)
    for outline in outlines:
        if not isinstance(outline, dict):
            continue
        ac_id = outline.get('ac_id', 'AC_000')
        groups[ac_id].append(outline)
    return dict(groups)


# ── Generate POM Class ─────────────────────────────────────────

async def generate_pom_class(
    pom_summary: dict,
    provider: str = "groq"
) -> tuple:
    """
    Generates one POM class file per consolidated page.
    Saves to /pages/ folder.
    Returns (generated_files dict, consolidated_pom dict).
    """
    client = get_client(provider=provider)

    agent = AssistantAgent(
        name="POM_Generator_Agent",
        model_client=client,
        system_message=POM_SYSTEM_PROMPT
    )

    termination = TextMentionTermination("TERMINATE")
    PAGES_DIR.mkdir(parents=True, exist_ok=True)

    init_file = PAGES_DIR / "__init__.py"
    if not init_file.exists():
        init_file.write_text("# Pages package\n")

    consolidated = consolidate_pom(pom_summary)
    generated    = {}

    print(f"\n  Generating {len(consolidated)} POM class(es)...\n")

    for page_name, page_data in consolidated.items():
        print(f"  Generating POM : {page_name}")

        pom_file = PAGES_DIR / f"{page_name.lower()}.py"

        if pom_file.exists():
            print(f"  ⏭️  Already exists — skipping")
            generated[page_name] = str(pom_file)
            continue

        prompt = build_pom_prompt(page_data, page_name)

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

            code = extract_code(assistant_reply)
            pom_file.write_text(code, encoding='utf-8')
            generated[page_name] = str(pom_file)

            print(
                f"  ✅ {pom_file.name} saved "
                f"({len(code.splitlines())} lines)"
            )
            await asyncio.sleep(3)

        except Exception as e:
            print(f"  ❌ Error: {str(e)[:80]}")
            continue

    return generated, consolidated


# ── Generate AC Test Scripts ───────────────────────────────────

async def generate_ac_scripts(
    outlines: list,
    pom_class_name: str,
    story_id: str,
    provider: str = "groq"
) -> list:
    """
    Groups outlines by AC ID.
    Generates one test file per AC group.
    Saves to /outputs/scripts/ folder.
    """
    client = get_client(provider=provider)

    agent = AssistantAgent(
        name="Script_Generator_Agent",
        model_client=client,
        system_message=SCRIPT_SYSTEM_PROMPT
    )

    termination     = TextMentionTermination("TERMINATE")
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    init_file = SCRIPTS_DIR / "__init__.py"
    if not init_file.exists():
        init_file.write_text("# Scripts package\n")

    ac_groups       = group_by_ac(outlines)
    generated_files = []
    total_groups    = len(ac_groups)

    print(f"\n  Generating {total_groups} AC test file(s)...\n")

    for group_num, (ac_id, ac_outlines) in enumerate(
        ac_groups.items(), 1
    ):
        # Derive AC title from first outline title
        first_title = ac_outlines[0].get('title', '') if ac_outlines else ''
        # Use ac_id as the anchor for filename
        safe_ac     = ac_id.lower().replace('_', '_')
        filename    = f"test_{safe_ac}_{story_id.lower()}.py"
        script_path = SCRIPTS_DIR / filename

        print(
            f"  [{group_num}/{total_groups}] {ac_id} — "
            f"{len(ac_outlines)} test case(s) → {filename}"
        )

        if script_path.exists():
            print(f"  ⏭️  Already exists — skipping")
            generated_files.append(str(script_path))
            continue

        # Derive a human-readable AC title from test case titles
        ac_title = (
            first_title.split('—')[0].strip()
            if '—' in first_title
            else ac_id
        )

        prompt = build_ac_script_prompt(
            ac_id, ac_title, ac_outlines, pom_class_name
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

            code = extract_code(assistant_reply)

            if len(code.strip()) < 80:
                print(f"  ⚠️  Response too short — skipping")
                continue

            script_path.write_text(code, encoding='utf-8')
            generated_files.append(str(script_path))

            lines = len(code.splitlines())
            print(f"  ✅ {filename} saved ({lines} lines)")

            await asyncio.sleep(4)

        except Exception as e:
            error_str = str(e)
            if any(c in error_str for c in ['429', '413', 'rate_limit']):
                print(f"  ⏳ Rate limit — waiting 60s...")
                await asyncio.sleep(60)
            else:
                print(f"  ❌ Error: {str(e)[:80]}")
            continue

    return generated_files


# ── Main Entry Point ───────────────────────────────────────────

def run(
    outline_file: str,
    provider: str = "groq"
) -> dict:
    """
    Orchestrates Agent 4 end-to-end:
    1. Loads script outline JSON from Agent 3
    2. Consolidates POM summary
    3. Generates POM class file in /pages/
    4. Groups outlines by AC
    5. Generates one test file per AC in /outputs/scripts/
    6. Prints summary

    Args:
        outline_file : JSON filename from Agent 3
                       e.g. 'US_001_poc_script_outline.json'
        provider     : LLM provider — groq, ollama, gemini
    """
    outline_path = FEATURES_DIR / outline_file

    if not outline_path.exists():
        raise FileNotFoundError(
            f"\n[Agent 4 ERROR] Outline JSON not found: {outline_path}"
            f"\nRun Agent 3 first: "
            f"python agents/script_outline_agent.py"
        )

    with open(outline_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    story_id    = data.get('story_id', 'unknown')
    pom_summary = data.get('pom_summary', {})
    outlines    = data.get('outlines', [])
    model_name  = PROVIDERS.get(provider, {}).get('model', 'unknown')

    # Count AC groups
    ac_groups  = group_by_ac(outlines)

    print(f"\n{'='*60}")
    print(f"  AGENT 4 — Script Generator Agent")
    print(f"{'='*60}")
    print(f"  Story      : {story_id}")
    print(f"  Outlines   : {len(outlines)}")
    print(f"  AC Groups  : {len(ac_groups)} → {list(ac_groups.keys())}")
    print(f"  Provider   : {provider} — {model_name}")
    print(f"  Output     : one .py file per AC")

    # Step 1 — Generate POM class
    pom_files, consolidated_pom = asyncio.run(
        generate_pom_class(pom_summary, provider)
    )

    # Determine primary POM class name
    pom_class_name = (
        list(consolidated_pom.keys())[0]
        if consolidated_pom else "LoginPage"
    )

    # Step 2 — Generate one script file per AC
    script_files = asyncio.run(
        generate_ac_scripts(
            outlines, pom_class_name, story_id, provider
        )
    )

    # Summary
    print(f"\n{'='*60}")
    print(f"  ✅ Script Generation Complete")
    print(f"\n  POM classes generated : {len(pom_files)}")
    for name, path in pom_files.items():
        print(f"    • {name} → {Path(path).name}")
    print(f"\n  Test files generated  : {len(script_files)}")
    for path in script_files:
        print(f"    • {Path(path).name}")
    print(f"\n  Scripts saved to : {SCRIPTS_DIR}")
    print(f"  POM saved to     : {PAGES_DIR}")
    print(f"{'='*60}\n")

    return {
        "pom_files":    pom_files,
        "script_files": script_files
    }


# ── CLI ────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Agent 4 — Script Generator Agent"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="US_001_poc_script_outline.json",
        help="JSON filename from Agent 3 inside /outputs/features/"
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="groq",
        help="LLM provider: groq, gemini, openai, ollama"
    )
    args = parser.parse_args()
    run(args.input, args.provider)
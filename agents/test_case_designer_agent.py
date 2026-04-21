"""
Agent 2 — Test Case Designer Agent
─────────────────────────────────────────────────────────────────
WHAT IT DOES:
    Reads the structured JSON from Agent 1.
    Sends each Acceptance Criterion to Groq LLaMA3.
    Gets back formal test cases in structured JSON format.
    Saves all test cases as a CSV to /outputs/test_cases/

LLM USED:
    Groq — llama-3.3-70b-versatile
    Why: Strong structured reasoning, follows output format
         instructions precisely, free tier sufficient.

INPUT  : outputs/US_001_structured.json
OUTPUT : outputs/test_cases/US_001_test_cases.csv
─────────────────────────────────────────────────────────────────
"""

import json
import csv
import asyncio
import argparse
from pathlib import Path
from datetime import datetime

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient

import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.llm_config import get_client


# ── Paths ──────────────────────────────────────────────────────

OUTPUTS_DIR   = Path(__file__).parent.parent / "outputs"
TEST_CASE_DIR = OUTPUTS_DIR / "test_cases"


# ── System Prompt ──────────────────────────────────────────────

SYSTEM_PROMPT = """
You are a Senior QA Engineer with 10+ years of experience writing
formal test cases for enterprise web applications.

Your job is to take an Acceptance Criterion and generate formal
test cases in strict JSON format.

RULES:
1. Generate at minimum one POSITIVE test case per AC.
2. Generate at minimum one NEGATIVE test case per AC where applicable.
3. Generate BOUNDARY test cases where input fields are involved.
4. Each test case must have clear, numbered step-by-step actions.
5. Expected results must be specific and verifiable — never vague.
6. Do NOT generate test cases for anything in the out_of_scope list.
7. Respond ONLY with a valid JSON array. No explanation. No markdown
   code fences. No preamble. Just the raw JSON array.

OUTPUT FORMAT — respond with exactly this structure:
[
  {
    "tc_id": "TC_001_001",
    "ac_id": "AC_001",
    "title": "Verify successful login with valid credentials",
    "test_type": "Positive",
    "priority": "High",
    "preconditions": [
      "User has a valid OrangeHRM account",
      "Browser is open and pointed at the login URL"
    ],
    "test_steps": [
      "Navigate to the OrangeHRM login page",
      "Enter valid username: Admin",
      "Enter valid password: admin123",
      "Click the Login button"
    ],
    "expected_result": "User is redirected to the dashboard. URL contains /dashboard. User name is visible in the top navigation bar.",
    "test_data": {
      "username": "Admin",
      "password": "admin123"
    }
  }
]

tc_id format rule:
  TC_{story_number}_{sequence}
  Example: story US_001, first test case = TC_001_001

test_type must be one of: Positive, Negative, Boundary, UI

priority must be one of: High, Medium, Low
"""


# ── Build Prompt Per AC ────────────────────────────────────────

def build_prompt(story: dict, ac: dict) -> str:
    """
    Builds the prompt sent to the LLM for one AC.
    Includes story context, the AC details, test data,
    and out-of-scope items so the LLM has full context.
    """
    out_of_scope  = "\n".join(
        f"  - {item}" for item in story.get("out_of_scope", [])
    )
    test_data_str = json.dumps(story.get("test_data", []), indent=2)
    then_str      = "\n".join(
        f"  - {t}" for t in ac.get("then", [])
    )

    return f"""
STORY CONTEXT:
  Story ID    : {story.get('story_id')}
  Feature     : {story.get('feature')}
  Application : {story.get('application')}
  Target URL  : {story.get('target_url')}

ACCEPTANCE CRITERION:
  ID    : {ac.get('id')}
  Title : {ac.get('title')}
  Given : {ac.get('given')}
  When  : {ac.get('when')}
  Then  :
{then_str}

AVAILABLE TEST DATA:
{test_data_str}

OUT OF SCOPE — do NOT generate test cases for these:
{out_of_scope}

Generate all appropriate test cases for this AC now.
Return ONLY the JSON array.
""".strip()


# ── Parse LLM Response ─────────────────────────────────────────

def parse_llm_response(raw_response: str) -> list:
    """
    Extracts and parses the JSON array from the LLM response.
    Handles cases where the LLM wraps output in markdown fences
    despite being told not to — defensive parsing.
    """
    text = raw_response.strip()

    # Strip markdown code fences if present
    if "```" in text:
        lines = text.splitlines()
        lines = [l for l in lines if not l.strip().startswith("```")]
        text  = "\n".join(lines).strip()

    # Find the JSON array boundaries
    start = text.find('[')
    end   = text.rfind(']') + 1

    if start == -1 or end == 0:
        raise ValueError(
            f"[Agent 2 ERROR] No JSON array found in LLM response.\n"
            f"Raw response:\n{raw_response[:500]}"
        )

    return json.loads(text[start:end])


# ── Save to CSV ────────────────────────────────────────────────

def save_to_csv(test_cases: list, story_id: str) -> Path:
    """
    Saves the list of test case dicts to a CSV file.
    Lists (preconditions, test_steps) are joined with ' | '
    so they fit cleanly in a spreadsheet cell.
    Dicts (test_data) are serialised as JSON strings.
    """
    TEST_CASE_DIR.mkdir(parents=True, exist_ok=True)
    output_path = TEST_CASE_DIR / f"{story_id}_test_cases.csv"

    fieldnames = [
        "tc_id", "ac_id", "title", "test_type", "priority",
        "preconditions", "test_steps", "expected_result", "test_data"
    ]

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for tc in test_cases:
            writer.writerow({
                "tc_id":           tc.get("tc_id", ""),
                "ac_id":           tc.get("ac_id", ""),
                "title":           tc.get("title", ""),
                "test_type":       tc.get("test_type", ""),
                "priority":        tc.get("priority", ""),
                "preconditions":   " | ".join(tc.get("preconditions", [])),
                "test_steps":      " | ".join(tc.get("test_steps", [])),
                "expected_result": tc.get("expected_result", ""),
                "test_data":       json.dumps(tc.get("test_data", {}))
            })

    return output_path


# ── Core Async Runner ──────────────────────────────────────────

async def design_test_cases(story: dict) -> list:
    """
    Creates one AssistantAgent per run.
    Loops through every AC in the story.
    Sends each AC to the LLM as a separate conversation.
    Collects and returns all test cases as a flat list.

    Why one conversation per AC (not all ACs at once):
    - Keeps each prompt focused and within token limits
    - Avoids the LLM mixing up test cases across ACs
    - Makes retry logic easier if one AC fails
    """
    client = get_client(provider='groq')

    agent = AssistantAgent(
        name="Test_Case_Designer_Agent",
        model_client=client,
        system_message=SYSTEM_PROMPT
    )

    termination        = TextMentionTermination("TERMINATE")
    all_test_cases     = []
    acceptance_criteria = story.get("acceptance_criteria", [])

    print(f"\n  Processing {len(acceptance_criteria)} Acceptance Criteria...\n")

    for i, ac in enumerate(acceptance_criteria, 1):
        print(f"  [{i}/{len(acceptance_criteria)}] Generating for {ac['id']} — {ac['title']}")

        prompt = build_prompt(story, ac)

        # Fresh team per AC to prevent conversation history contamination
        team = RoundRobinGroupChat(
            participants=[agent],
            termination_condition=termination,
            max_turns=2
        )

        result = await team.run(task=prompt)

        # Extract the assistant reply — skip the user echo message
        assistant_reply = ""
        for msg in result.messages:
            if msg.source != "user":
                assistant_reply = msg.content
                break

        if not assistant_reply:
            print(f"  ⚠️  No response for {ac['id']} — skipping")
            continue

        try:
            tc_list = parse_llm_response(assistant_reply)
            all_test_cases.extend(tc_list)
            print(f"  ✅ {len(tc_list)} test case(s) generated")
        except (ValueError, json.JSONDecodeError) as e:
            print(f"  ❌ Parse error for {ac['id']}: {e}")
            continue

    return all_test_cases


# ── Main Entry Point ───────────────────────────────────────────

def run(story_file: str) -> list:
    """
    Orchestrates Agent 2 end-to-end:
    1. Loads structured JSON produced by Agent 1
    2. Calls the LLM for each AC
    3. Saves results to CSV
    4. Prints summary

    Args:
        story_file : JSON output filename from Agent 1
                     e.g. 'US_001_structured.json'
    Returns:
        List of all test case dicts
    """
    json_path = OUTPUTS_DIR / story_file

    if not json_path.exists():
        raise FileNotFoundError(
            f"\n[Agent 2 ERROR] Structured JSON not found: {json_path}"
            f"\nRun Agent 1 first: python agents/story_intake_agent.py"
        )

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    story    = data["story"]
    story_id = story.get("story_id", "US_000")

    print(f"\n{'='*60}")
    print(f"  AGENT 2 — Test Case Designer Agent")
    print(f"{'='*60}")
    print(f"  Story    : {story_id} — {story.get('feature')}")
    print(f"  App      : {story.get('application')}")
    print(f"  AC Count : {story.get('acceptance_criteria_count')}")
    print(f"  LLM      : Groq — llama-3.3-70b-versatile")

    all_test_cases = asyncio.run(design_test_cases(story))

    if not all_test_cases:
        print("\n  ❌ No test cases generated. Check LLM response above.")
        return []

    output_path = save_to_csv(all_test_cases, story_id)

    positive = sum(1 for tc in all_test_cases if tc.get("test_type") == "Positive")
    negative = sum(1 for tc in all_test_cases if tc.get("test_type") == "Negative")
    boundary = sum(1 for tc in all_test_cases if tc.get("test_type") == "Boundary")
    ui       = sum(1 for tc in all_test_cases if tc.get("test_type") == "UI")

    print(f"\n  ✅ Test Case Generation Complete")
    print(f"\n  Total Test Cases : {len(all_test_cases)}")
    print(f"    Positive       : {positive}")
    print(f"    Negative       : {negative}")
    print(f"    Boundary       : {boundary}")
    print(f"    UI             : {ui}")
    print(f"\n  Output → {output_path}")
    print(f"{'='*60}\n")

    return all_test_cases


# ── CLI ────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Agent 2 — Test Case Designer Agent"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="US_001_structured.json",
        help="JSON output filename from Agent 1 inside /outputs/"
    )
    args = parser.parse_args()
    run(args.input)
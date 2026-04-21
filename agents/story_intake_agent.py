"""
Agent 1 — Story Intake Agent
─────────────────────────────────────────────────────────────────
WHAT IT DOES:
    Reads a Markdown user story file from /stories/
    Parses it into a structured JSON object
    Saves JSON to /outputs/ for Agent 2 to consume

WHY NO LLM:
    The user story format is our own predictable template.
    Regex + string parsing is faster, cheaper, and 100% reliable.
    LLMs are reserved for agents that need reasoning.

INPUT  : stories/US_001_login.md
OUTPUT : outputs/US_001_structured.json
─────────────────────────────────────────────────────────────────
"""

import re
import json
import argparse
from pathlib import Path
from datetime import datetime


# ── Paths ──────────────────────────────────────────────────────

STORIES_DIR = Path(__file__).parent.parent / "stories"
OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"


# ── Section Parsers ────────────────────────────────────────────

def extract_metadata(content: str) -> dict:
    """
    Reads the ## Metadata section.
    Each line has the pattern: - **Key:** Value
    Returns a flat dict of all key-value pairs.
    """
    metadata = {}
    section = re.search(
        r'## Metadata(.*?)(?=\n##|\Z)', content, re.DOTALL
    )
    if section:
        for line in section.group(1).strip().splitlines():
            match = re.match(r'\s*-\s*\*\*(.+?):\*\*\s*(.+)', line)
            if match:
                key   = match.group(1).strip().lower().replace(' ', '_')
                value = match.group(2).strip()
                metadata[key] = value
    return metadata


def extract_problem_statement(content: str) -> str:
    """
    Reads the ## Problem Statement section.
    Returns it as a single clean string with normalised whitespace.
    """
    section = re.search(
        r'## Problem Statement(.*?)(?=\n##|\Z)', content, re.DOTALL
    )
    if section:
        text = section.group(1).strip()
        text = re.sub(r'\n+', ' ', text)
        text = re.sub(r'\s{2,}', ' ', text)
        return text
    return ""


def extract_acceptance_criteria(content: str) -> list:
    """
    Reads each ### AC_XXX block inside ## Acceptance Criteria.

    Each AC block is parsed into:
    {
        "id":    "AC_001",
        "title": "Successful Login with Valid Credentials",
        "given": "the user is on the OrangeHRM login page",
        "when":  "the user enters valid credentials",
        "then":  ["redirected to dashboard", "URL contains /dashboard"],
        "raw":   "full original text of this AC block"
    }
    """
    ac_list = []

    ac_section = re.search(
        r'## Acceptance Criteria(.*?)(?=\n## |\Z)', content, re.DOTALL
    )
    if not ac_section:
        return ac_list

    # Split into individual blocks by ### AC_ heading
    ac_blocks = re.split(r'(?=### AC_\d+)', ac_section.group(1))

    for block in ac_blocks:
        block = block.strip()
        if not block:
            continue

        ac = {}

        # ID and title from heading
        heading = re.match(r'### (AC_\d+)\s*[—-]\s*(.+)', block)
        if not heading:
            continue
        ac['id']    = heading.group(1).strip()
        ac['title'] = heading.group(2).strip()

        # Given
        given = re.search(
            r'\*\*Given\*\*\s+(.+?)(?=\*\*When\*\*|\Z)', block, re.DOTALL
        )
        ac['given'] = given.group(1).strip() if given else ""

        # When
        when = re.search(
            r'\*\*When\*\*\s+(.+?)(?=\*\*Then\*\*|\Z)', block, re.DOTALL
        )
        ac['when'] = when.group(1).strip() if when else ""

        # Then — split on **And** to capture all conditions
        then = re.search(
            r'\*\*Then\*\*\s+(.+?)(?=###|\Z)', block, re.DOTALL
        )
        if then:
            raw_then   = then.group(1).strip()
            conditions = re.split(r'\*\*And\*\*', raw_then)
            all_conds  = []
            for c in conditions:
                lines = [
                    l.strip().lstrip('-•').strip()
                    for l in c.splitlines() if l.strip()
                ]
                all_conds.extend([l for l in lines if l])
            ac['then'] = all_conds
        else:
            ac['then'] = []

        ac['raw'] = block
        ac_list.append(ac)

    return ac_list


def extract_test_data(content: str) -> list:
    """
    Reads the ## Test Data Markdown table.
    Returns a list of dicts, one per data row.
    """
    test_data = []
    section = re.search(
        r'## Test Data(.*?)(?=\n##|\Z)', content, re.DOTALL
    )
    if not section:
        return test_data

    rows = [
        line for line in section.group(1).strip().splitlines()
        if line.strip().startswith('|') and '---' not in line
    ]
    if len(rows) < 2:
        return test_data

    headers = [h.strip() for h in rows[0].split('|') if h.strip()]
    for row in rows[1:]:
        values = [v.strip() for v in row.split('|') if v.strip()]
        if len(values) == len(headers):
            test_data.append(dict(zip(headers, values)))

    return test_data


def extract_out_of_scope(content: str) -> list:
    """
    Reads the ## Out of Scope section.
    Returns a list of strings, one per bullet point.
    """
    oos     = []
    section = re.search(
        r'## Out of Scope(.*?)(?=\n##|\Z)', content, re.DOTALL
    )
    if section:
        for line in section.group(1).strip().splitlines():
            item = line.strip().lstrip('-•').strip()
            if item:
                oos.append(item)
    return oos


# ── Main Agent Function ────────────────────────────────────────

def run(story_file: str) -> dict:
    """
    Main entry point for Agent 1.

    Reads the story file, parses all sections,
    assembles a structured dict, saves it as JSON,
    and returns it for the next agent.

    Args:
        story_file : filename only e.g. 'US_001_login.md'
                     Agent looks inside /stories/ automatically.

    Returns:
        Structured dict — input for Agent 2 (Test Case Designer).
    """

    story_path = STORIES_DIR / story_file

    if not story_path.exists():
        raise FileNotFoundError(
            f"\n[Agent 1 ERROR] File not found: {story_path}"
            f"\nEnsure your .md file is inside the /stories/ folder."
        )

    print(f"\n{'='*60}")
    print(f"  AGENT 1 — Story Intake Agent")
    print(f"{'='*60}")
    print(f"  Reading: {story_path}")

    content = story_path.read_text(encoding='utf-8')

    # Parse all sections
    metadata            = extract_metadata(content)
    problem_statement   = extract_problem_statement(content)
    acceptance_criteria = extract_acceptance_criteria(content)
    test_data           = extract_test_data(content)
    out_of_scope        = extract_out_of_scope(content)

    story_id = metadata.get('story_id', story_file.replace('.md', ''))

    # Assemble output
    structured = {
        "pipeline_meta": {
            "generated_by":  "Agent 1 — Story Intake Agent",
            "generated_at":  datetime.now().isoformat(),
            "source_file":   story_file,
            "agent_version": "1.0"
        },
        "story": {
            **metadata,
            "problem_statement":         problem_statement,
            "acceptance_criteria":       acceptance_criteria,
            "acceptance_criteria_count": len(acceptance_criteria),
            "acceptance_criteria_ids":   [ac['id'] for ac in acceptance_criteria],
            "test_data":                 test_data,
            "out_of_scope":              out_of_scope
        }
    }

    # Save JSON
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUTS_DIR / f"{story_id}_structured.json"

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(structured, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"\n  ✅ Parsed successfully")
    print(f"  Story ID  : {story_id}")
    print(f"  Feature   : {metadata.get('feature', 'N/A')}")
    print(f"  Module    : {metadata.get('module', 'N/A')}")
    print(f"  Priority  : {metadata.get('priority', 'N/A')}")
    print(f"\n  Acceptance Criteria : {len(acceptance_criteria)}")
    for ac in acceptance_criteria:
        print(f"    • {ac['id']} — {ac['title']}")
    print(f"\n  Test Data rows  : {len(test_data)}")
    print(f"  Out of Scope    : {len(out_of_scope)} items")
    print(f"\n  Output → {output_path}")
    print(f"{'='*60}\n")

    return structured


# ── CLI ────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Agent 1 — Story Intake Agent"
    )
    parser.add_argument(
        "--story",
        type=str,
        default="US_001_login.md",
        help="Filename of the .md user story inside /stories/"
    )
    args = parser.parse_args()
    run(args.story)
![Pipeline](https://github.com/kulsha/multi-agent-qe-orchestrator/actions/workflows/pipeline_smoke_test.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![AutoGen](https://img.shields.io/badge/AutoGen-0.7.5-purple)
![Playwright](https://img.shields.io/badge/Playwright-Enabled-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

# multi-agent-qe-orchestrator

> **From a plain English user story to reviewed Playwright test scripts — fully autonomous. No manual test writing. No manual code review. No manual coverage analysis.**

A 7-agent AI pipeline built with AutoGen 0.7.5 that reads a user story, generates test cases, writes Playwright scripts, reviews the code, analyzes coverage, and produces an HTML executive report — all without human intervention except one approval checkpoint.

---

## 📊 Live Pipeline Report

**[View the live pipeline dashboard →](https://kulsha.github.io/multi-agent-qe-orchestrator/)**

Real metrics from the latest pipeline run. Regenerated automatically on every run.

---

## Architecture

Current implementation uses a **sequential pipeline** orchestrated by `main.py`. Each agent produces a structured output that becomes the input for the next agent in the chain.

                ┌──────────────────────────────────────┐
                │     multi-agent-qe-orchestrator      │
                │   AutoGen 0.7.5 · Python 3.12        │
                └──────────────────┬───────────────────┘
                                   │
                     User Story (.md file)
                                   │
                                   ▼
      ┌────────────────────────────────────────────────┐
      │                  main.py                       │
      │         Single entry point orchestrator        │
      │      Smart skip · Resume · Human checkpoint    │
      └────────────────────────────────────────────────┘
                                   │
                                   ▼
                          ┌─────────────┐
                          │   Agent 1   │
                          │    Story    │
                          │   Intake    │
                          │  Pure Python│
                          └──────┬──────┘
                                 │ structured JSON
                                 ▼
                          ┌─────────────┐
                          │   Agent 2   │
                          │  Test Case  │
                          │  Designer   │
                          │ Groq LLaMA3 │
                          └──────┬──────┘
                                 │ test cases CSV
                                 │
                          ⏸ Human Checkpoint
                          Review test cases
                          Y to continue / N to stop
                                 │
                                 ▼
                          ┌─────────────┐
                          │   Agent 3   │
                          │   Script    │
                          │   Outline   │
                          │ Claude Haiku│
                          └──────┬──────┘
                                 │ outlines JSON
                                 ▼
                          ┌─────────────┐
                          │   Agent 4   │
                          │   Script    │
                          │  Generator  │
                          │ Claude Haiku│
                          └──────┬──────┘
                                 │ Playwright scripts
                                 ▼
                          ┌─────────────┐
                          │   Agent 5   │
                          │    Code     │
                          │   Reviewer  │
                          │ Claude Haiku│
                          └──────┬──────┘
                                 │ reviewed scripts
                                 ▼
                          ┌─────────────┐
                          │   Agent 6   │
                          │  Coverage   │
                          │  Analyzer   │
                          │ Claude Haiku│
                          └──────┬──────┘
                                 │ coverage report
                                 ▼
                          ┌─────────────┐
                          │   Agent 7   │
                          │   Report    │
                          │  Generator  │
                          │ Claude Haiku│
                          └──────┬──────┘
                                 │
                                 ▼
                       pipeline_report.html
                       ────────────────────
                       GitHub Pages (live)

> **Planned enhancement** — A `SelectorGroupChat` upgrade with a
> GroupChatManager will enable dynamic agent routing. For example
> if Agent 5 finds critical issues the manager can route scripts
> back to Agent 4 for regeneration instead of proceeding linearly.
> This adds true multi-agent intelligence beyond sequential execution.

---

## What Each Agent Does

| Agent | Name | LLM | Input | Output |
|---|---|---|---|---|
| 1 | Story Intake | None — Pure Python | `.md` user story | Structured JSON |
| 2 | Test Case Designer | Groq LLaMA3 70B | Structured JSON | Test cases CSV |
| 3 | Script Outline | Claude Haiku | Test cases CSV | Action/assertion outlines JSON |
| 4 | Script Generator | Claude Haiku | Outlines JSON | Playwright `.py` files per AC |
| 5 | Code Reviewer | Claude Haiku | Scripts + POM class | Reviewed scripts + MD report |
| 6 | Coverage Analyzer | Claude Haiku | Story + CSV + review | Coverage gap report |
| 7 | Report Generator | Claude Haiku | All outputs | HTML executive dashboard |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Multi-Agent Framework | AutoGen 0.7.5 (autogen-agentchat + autogen-ext) |
| Primary LLM | Claude Haiku 4.5 (Anthropic API) |
| Secondary LLM | Groq LLaMA3 70B (free tier — 100k tokens/day) |
| Local LLM Fallback | Ollama Mistral 7B (offline, unlimited) |
| Test Automation | Playwright Python (async) |
| Test Framework | pytest + pytest-asyncio |
| Page Object Model | Custom POM classes per application module |
| Target Application | OrangeHRM (open source HR demo) |
| Language | Python 3.12 |
| CI/CD | GitHub Actions |
| Report Hosting | GitHub Pages |

---

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/kulsha/multi-agent-qe-orchestrator.git
cd multi-agent-qe-orchestrator
pip install -r requirements.txt
playwright install chromium

# 2. Add your API keys
cp .env.example .env
# Edit .env and add:
# GROQ_API_KEY=your_groq_key
# ANTHROPIC_API_KEY=your_claude_key

# 3. Run the full pipeline
python main.py --story stories/US_001_login_poc.md --provider claude
```

The pipeline pauses after Agent 2 for your approval. Type `Y` to continue. Everything else runs autonomously. The HTML report opens at `outputs/pipeline_report.html`.

**Switch providers anytime:**
```bash
python main.py --story stories/US_001_login_poc.md --provider groq    # Groq free tier
python main.py --story stories/US_001_login_poc.md --provider ollama  # local offline
```

**Force a completely fresh run:**
```bash
python main.py --story stories/US_001_login_poc.md --provider claude --force
```

---

## Project Structure

multi-agent-qe-orchestrator/
│
├── main.py                          # Single entry point — runs full pipeline
│
├── agents/
│   ├── story_intake_agent.py        # Agent 1 — parses user story
│   ├── test_case_designer_agent.py  # Agent 2 — generates test cases
│   ├── script_outline_agent.py      # Agent 3 — creates action outlines
│   ├── script_generator_agent.py    # Agent 4 — writes Playwright scripts
│   ├── code_reviewer_agent.py       # Agent 5 — reviews and improves scripts
│   ├── coverage_analyzer_agent.py   # Agent 6 — maps coverage to ACs
│   └── report_generator_agent.py    # Agent 7 — generates HTML dashboard
│
├── config/
│   └── llm_config.py                # Multi-provider LLM config (Groq/Claude/Ollama)
│
├── stories/
│   └── US_001_login_poc.md          # Sample user story — OrangeHRM login
│
├── pages/
│   └── login.py                     # Playwright Page Object Model
│
├── outputs/
│   ├── test_cases/                  # Agent 2 — generated CSV
│   ├── features/                    # Agent 3 — outline JSON
│   ├── scripts/                     # Agent 4 — Playwright scripts
│   │   └── reviewed/                # Agent 5 — improved scripts
│   ├── review_report.md             # Agent 5 — code review findings
│   ├── coverage_report.md           # Agent 6 — coverage gap analysis
│   └── pipeline_report.html         # Agent 7 — executive dashboard
│
├── docs/
│   └── index.html                   # GitHub Pages — live pipeline report
│
├── .github/
│   └── workflows/
│       └── pipeline_smoke_test.yml  # CI — smoke test on every push
│
├── tests/
│   └── conftest.py                  # pytest fixtures
│
└── conftest.py                      # Project root path resolution

---

## Key Design Decisions

**One file per Acceptance Criteria** — Agent 4 groups all test cases for one AC into a single script file. This mirrors how enterprise QA teams organise test suites and makes the output directly mappable to Polarion or Jira ACs.

**Smart skip logic** — Re-running the pipeline skips agents whose outputs already exist. Zero tokens consumed on a re-run of a completed pipeline. Use `--force` to override and regenerate everything.

**Resume on interruption** — Agent 3 saves a progress file after every successful outline. If interrupted mid-run by a rate limit or crash it resumes automatically from the last completed test case on the next run.

**Provider flexibility** — All agents accept a `--provider` flag. Switch between Claude Haiku, Groq LLaMA3, and Ollama Mistral without changing a single line of agent code. Production runs use Claude. Development runs use Ollama locally at zero cost.

**Human in the loop** — The pipeline pauses after Agent 2 and shows a test case distribution summary. You approve or stop before any code is generated. This is the one intentional human gate in an otherwise fully autonomous pipeline.

---

## Providers and Cost

| Provider | Best For | Cost |
|---|---|---|
| Claude Haiku 4.5 | Production runs — best JSON and code quality | ~$0.12 per full pipeline run |
| Groq LLaMA3 70B | Development — free tier, 100k tokens/day | Free |
| Ollama Mistral 7B | Offline development — no API needed | Free (local compute) |

---

## Running the Generated Tests

After the pipeline completes, run the reviewed Playwright scripts directly against OrangeHRM:

```bash
# Run all reviewed scripts
pytest outputs/scripts/reviewed/ -v

# Run one AC at a time
pytest outputs/scripts/reviewed/test_ac_001_us_001_poc.py -v

# Run headless for CI
pytest outputs/scripts/reviewed/ -v --headed=false
```

---

## About

Built by **Shashank Kulkarni** — QA Automation Lead at Molex India Business Services, Bengaluru. 11+ years of Quality Engineering experience across PLM (Siemens Teamcenter AWC, Polarion), Banking (Wells Fargo, RBC), and Energy domains. ISTQB CT-AI certified. Part of the Quality Engineering Centre of Excellence (QECoE) driving AI-augmented test automation at enterprise scale.

This project demonstrates how Agentic AI can transform the QA lifecycle — from requirements to runnable tests — without manual intervention at any stage except a single human approval gate.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Shashank%20Kulkarni-blue?logo=linkedin)](www.linkedin.com/in/shashank-kulkarni-844b98b2)

---

*Built with AutoGen 0.7.5 · Claude Haiku · Groq LLaMA3 · Playwright · Python 3.12*
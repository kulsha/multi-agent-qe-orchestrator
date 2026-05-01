![Pipeline](https://github.com/kulsha/multi-agent-qe-orchestrator/actions/workflows/pipeline_smoke_test.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![AutoGen](https://img.shields.io/badge/AutoGen-0.7.5-purple)
![Playwright](https://img.shields.io/badge/Playwright-Enabled-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

# multi-agent-qe-orchestrator

> **From a plain English user story to reviewed Playwright test scripts — fully autonomous. No manual test writing. No manual code review. No manual coverage analysis.**

A 7-agent AI pipeline built with AutoGen 0.7.5 that reads a user story, generates test cases, writes Playwright scripts, reviews the code, analyzes coverage, and produces an HTML executive report — all without human intervention except one approval checkpoint.

Two orchestration modes available — sequential pipeline for reliability and GroupChat pipeline for intelligent dynamic routing with auto re-routing on quality issues.

---

## 📊 Live Pipeline Report

**[View the live pipeline dashboard →](https://kulsha.github.io/multi-agent-qe-orchestrator/)**

Real metrics from the latest pipeline run. Regenerated automatically on every run.

---

## Architecture

### Mode 1 — Sequential Pipeline (`main.py`)

Fixed order orchestration. Fast, reliable, production-grade. Smart skip logic saves tokens on re-runs.

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
                          │ Claude Haiku│
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

---

### Mode 2 — GroupChat Pipeline (`groupchat_pipeline.py`)
Dynamic orchestration using AutoGen `SelectorGroupChat` with a deterministic Python selector function. The key differentiator — if Agent 5 finds more than 3 critical issues it automatically re-routes back to Agent 4 for script regeneration. Maximum 2 re-route attempts before proceeding.

                ┌──────────────────────────────────────┐
                │     multi-agent-qe-orchestrator      │
                │   AutoGen 0.7.5 · SelectorGroupChat  │
                └──────────────────┬───────────────────┘
                                   │
                     User Story (.md file)
                                   │
                                   ▼
      ┌────────────────────────────────────────────────┐
      │           groupchat_pipeline.py                │
      │    SelectorGroupChat — 8 participants          │
      │    Deterministic selector function             │
      │    Dynamic routing based on signal keywords    │
      └────────────────────────────────────────────────┘
                                   │
                ┌──────────────────┴──────────────────┐
                │     Pipeline Selector Function       │
                │   Routes on AGENT_N_COMPLETE signals │
                │   No LLM involved — 100% reliable   │
                └──────────────────┬──────────────────┘
                                   │
                ┌──────────────────▼──────────────────┐
                │                                      │
      ┌─────────┴──┐                        ┌─────────┴──┐
      │  Agent 1   │                        │  Agent 2   │
      │   Story    │ ──AGENT_1_COMPLETE────▶│  Test Case │
      │   Intake   │                        │  Designer  │
      │ Pure Python│                        │Claude Haiku│
      └────────────┘                        └─────┬──────┘
                                                  │
                                           AWAITING_HUMAN_APPROVAL
                                                  │
                                           ┌──────▼──────┐
                                           │   Human     │
                                           │  Approver   │
                                           │  Y/N input  │
                                           └──────┬──────┘
                                                  │
                                           HUMAN_APPROVED
                                                  │
                                           ┌──────▼──────┐
                                           │   Agent 3   │
                                           │   Script    │
                                           │   Outline   │
                                           │Claude Haiku │
                                           └──────┬──────┘
                                                  │
                                           AGENT_3_COMPLETE
                                                  │
                                           ┌──────▼──────┐
                                ┌──────────│   Agent 4   │◀─────────────┐
                                │          │   Script    │              │
                                │          │  Generator  │              │
                                │          │Claude Haiku │              │
                                │          └──────┬──────┘              │
                                │                 │                     │
                                │          AGENT_4_COMPLETE             │
                                │                 │                REROUTE_TO_AGENT_4
                                │          ┌──────▼──────┐        (if critical > 3
                                │          │   Agent 5   │         max 2 attempts)
                                │          │    Code     │              │
                                │          │   Reviewer  │──────────────┘
                                │          │Claude Haiku │
                                │          └──────┬──────┘
                                │                 │
                                │          AGENT_5_COMPLETE
                                │                 │
                                │          ┌──────▼──────┐
                                │          │   Agent 6   │
                                │          │  Coverage   │
                                │          │  Analyzer   │
                                │          │Claude Haiku │
                                │          └──────┬──────┘
                                │                 │
                                │          AGENT_6_COMPLETE
                                │                 │
                                │          ┌──────▼──────┐
                                │          │   Agent 7   │
                                │          │   Report    │
                                └─────────▶│  Generator  │
                                           │Claude Haiku │
                                           └──────┬──────┘
                                                  │
                                           PIPELINE_COMPLETE
                                                  │
                                                  ▼
                                       pipeline_report.html
                                       ────────────────────
                                       GitHub Pages (live)

**Key GroupChat feature — auto re-routing:**
Agent 4 generates scripts
↓
Agent 5 reviews — finds 17 critical issues (> threshold of 3)
↓
⚠️  REROUTE_TO_AGENT_4 — automatic re-route
↓
Agent 4 regenerates with improvements (attempt 2)
↓
Agent 5 reviews again — 2 critical issues (≤ threshold)
↓
✅ AGENT_5_COMPLETE — proceeds to Agent 6

---

## What Each Agent Does

| Agent | Name | LLM | Input | Output |
|---|---|---|---|---|
| 1 | Story Intake | None — Pure Python | `.md` user story | Structured JSON |
| 2 | Test Case Designer | Claude Haiku | Structured JSON | Test cases CSV |
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
| GroupChat Orchestration | SelectorGroupChat with deterministic selector |
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

# 3a. Run sequential pipeline (recommended for daily use)
python main.py --story stories/US_001_login_poc.md --provider claude

# 3b. Run GroupChat pipeline (dynamic routing + auto re-routing)
python groupchat_pipeline.py --story stories/US_001_login_poc.md --provider claude
```

Both pipelines pause after Agent 2 for your approval. Type `Y` to continue.

**Switch providers anytime:**
```bash
python main.py --story stories/US_001_login_poc.md --provider groq
python main.py --story stories/US_001_login_poc.md --provider ollama
```

**Force a completely fresh run:**
```bash
python main.py --story stories/US_001_login_poc.md --provider claude --force
```

---

## Two Pipeline Modes Compared

| Feature | `main.py` Sequential | `groupchat_pipeline.py` GroupChat |
|---|---|---|
| Orchestration | Fixed order | SelectorGroupChat dynamic |
| Routing | Hardcoded in Python | Deterministic selector function |
| Re-routing | Not supported | Auto re-route on critical issues |
| Speed | Faster | Slightly slower |
| Token cost | Lower | Higher |
| Smart skip | Yes | No |
| Resume on interruption | Yes | No |
| Best for | Daily runs, CI | Demo, showcase, intelligent QA |

---

## Project Structure
multi-agent-qe-orchestrator/
│
├── main.py                          # Sequential pipeline entry point
├── groupchat_pipeline.py            # GroupChat pipeline entry point
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
│   └── llm_config.py                # Multi-provider LLM config
│
├── stories/
│   └── US_001_login_poc.md          # Sample user story — OrangeHRM login
│
├── pages/
│   └── login.py                     # Playwright Page Object Model
│
├── outputs/
│   ├── test_cases/                  # Agent 2 output
│   ├── features/                    # Agent 3 output
│   ├── scripts/                     # Agent 4 output
│   │   └── reviewed/                # Agent 5 output
│   ├── review_report.md             # Agent 5 report
│   ├── coverage_report.md           # Agent 6 report
│   └── pipeline_report.html         # Agent 7 report
│
├── docs/
│   └── index.html                   # GitHub Pages live report
│
├── .github/
│   └── workflows/
│       └── pipeline_smoke_test.yml  # CI smoke test
│
├── tests/
│   └── conftest.py                  # pytest fixtures
│
└── conftest.py                      # Project root path resolution

---

## Key Design Decisions

**Two orchestration modes** — Sequential for production reliability, GroupChat for intelligent self-correction. Same 7 agents, different orchestration layers. Demonstrates architectural maturity.

**Deterministic GroupChat selector** — Rather than relying on an LLM to decide routing (which hallucinates in long pipelines), a Python function routes based on signal keywords in agent outputs. Reliable, predictable, production-grade.

**Auto re-routing on quality issues** — GroupChat mode automatically routes back to Agent 4 if Agent 5 finds more than 3 critical issues. Maximum 2 attempts before proceeding. The pipeline self-corrects without human intervention.

**One file per Acceptance Criteria** — Agent 4 groups all test cases for one AC into a single script file. Mirrors enterprise QA test suite organisation and maps directly to Polarion or Jira ACs.

**Smart skip logic** — Sequential pipeline skips agents whose outputs already exist. Zero tokens consumed on re-runs. Use `--force` to override.

**Resume on interruption** — Agent 3 saves a progress file after every outline. Resumes automatically from the last completed test case on re-run.

**Provider flexibility** — All agents accept a `--provider` flag. Switch between Claude Haiku, Groq LLaMA3, and Ollama Mistral without changing agent code.

---

## Providers and Cost

| Provider | Best For | Cost |
|---|---|---|
| Claude Haiku 4.5 | Production — best JSON and code quality | ~$0.12 per full pipeline run |
| Groq LLaMA3 70B | Development — free tier, 100k tokens/day | Free |
| Ollama Mistral 7B | Offline development — no API needed | Free (local compute) |

---

## Running the Generated Tests

```bash
# Run all reviewed scripts
pytest outputs/scripts/reviewed/ -v

# Run one AC at a time
pytest outputs/scripts/reviewed/test_ac_001_us_001_poc.py -v
```

---

## About

Built by **Shashank Kulkarni** — QA Automation Lead at Molex India Business Services, Bengaluru. 11+ years of Quality Engineering experience across PLM (Siemens Teamcenter AWC, Polarion), Banking (Wells Fargo, RBC), and Energy domains. ISTQB CT-AI certified. Part of the Quality Engineering Centre of Excellence (QECoE) driving AI-augmented test automation at enterprise scale.

This project demonstrates how Agentic AI can transform the QA lifecycle — from requirements to runnable tests — without manual intervention at any stage except a single human approval gate.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Shashank%20Kulkarni-blue?logo=linkedin)](https://www.linkedin.com/in/shashank-kulkarni-844b98b2)

---

*Built with AutoGen 0.7.5 · Claude Haiku · Groq LLaMA3 · Playwright · Python 3.12*
# Autonomous Communication Manager

A personal AI agent that reduces communication decision overhead by acting as a **cross-channel triage layer** across Gmail and Slack.

> **Status**: Prototype — Phase 1 development

---

## The Problem

Knowledge workers with high inbound communication volume (100–250 messages/day) don't struggle with reading messages — they struggle with **making decisions about them**: respond now, defer, archive, delegate, schedule, ignore.

Existing tools (Gmail AI, Slack AI, Superhuman) operate at the message level — summarise, suggest, prioritise — but still present every message as a decision the user must make.

This system moves the AI's role from **assistant that writes messages** to **agent that performs triage decisions**.

---

## Core Thesis

The assistant's value is measured by one metric: **Inbox Decision Reduction Rate (IDRR)** — the proportion of incoming messages the agent triages without requiring user intervention. Target operating zone: 40–60% IDRR with a Correction Rate below 5%.

---

## Key Capabilities

- **Cross-channel triage** — unified decision layer across Gmail and Slack
- **Contact intelligence** — relationship graph with temporal decay scoring per contact class
- **Structural heuristics + learned priors** — useful from the first hour, improves over time
- **Interactive activity feed** — real-time visibility into every agent decision with undo/reclassify
- **Explicit correction learning** — every feed interaction is a supervised training signal
- **Draft generation** — context-aware reply drafts informed by relationship class and thread history
- **Trust ladder** — read-only → recommend → safe automation → delegated communication

---

## Architecture

```
InboxPoller (Gmail + Slack)
      ↓
DebounceBuffer (90s contact-level batching)
      ↓
AgentLoop (orchestrator)
      ↓
ContactGraph ←→ TriageEngine
                     ↓
              ActivityFeed ←→ User
                     ↓
              ActionExecutor
```

### Modules

| Module | Responsibility |
|---|---|
| `InboxPoller` | Multi-channel ingestion → unified `IncomingEvent` |
| `DebounceBuffer` | Contact-level event batching (90s window) |
| `AgentLoop` | Orchestrates the full pipeline |
| `ContactGraph` | Persistent relationship graph with temporal decay |
| `TriageEngine` | Classifies events → `{ archive, low, normal, urgent, protected }` |
| `ActivityFeed` | Real-time action stream with undo/reclassify/confirm |
| `ActionExecutor` | All write-side Gmail/Slack operations (dry-run by default) |
| `DraftGenerator` | LLM-powered reply drafts via Agentica Mini |

---

## Technology Stack

| Layer | Choice |
|---|---|
| Prototype language | Python 3.12+ |
| Target production | TypeScript / Node.js |
| Agent framework | [Agentica Mini](https://github.com/symbolica-ai/agentica-mini) |
| LLM routing | OpenRouter (Gemini, Claude, GPT models) |
| Email | Gmail API |
| Messaging | Slack Web API |

---

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- OpenRouter API key
- Gmail API credentials (`credentials.json`)
- Slack App token

### Setup

```bash
# Clone the repo (agentica-mini is a submodule)
git clone --recurse-submodules <repo-url>
cd emailManagement

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Add your keys to .env
```

### Environment Variables

```bash
OPENROUTER_API_KEY=your_openrouter_key
GMAIL_CREDENTIALS_PATH=./credentials.json
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_APP_TOKEN=xapp-your-token
```

### Run

```bash
uv run python main.py
```

---

## Project Documents

- [`PRD.md`](./PRD.md) — Full Product Requirements Document
- [`agentica-mini/README.md`](./agentica-mini/README.md) — Agent framework documentation

---

## Safety Model

- **Read-only by default** — no write permissions requested until the user triggers the first write action
- **Draft-only outgoing** — no messages sent without explicit user approval
- **Full audit log** — every agent action is logged with timestamp and action ID
- **Undo support** — all reversible actions can be undone from the activity feed
- **Protected contacts** — designated contacts are never auto-archived regardless of classification signals

---

## Metrics

| Metric | Definition | Target |
|---|---|---|
| IDRR | Automated decisions ÷ total messages | 40–60% |
| CR | User corrections ÷ automated decisions | < 5% |

**Health quadrants:**
- High IDRR + Low CR → agent removing work effectively ✅
- High IDRR + High CR → agent creating work ❌
- Low IDRR + Low CR → agent too conservative ⚠️

---

## Roadmap

| Phase | Focus | Key Deliverables |
|---|---|---|
| **1 — Core Utility** | Working prototype | InboxPoller, TriageEngine, ActivityFeed, AgentLoop |
| **2 — Intelligence** | Contact graph + cross-channel | Decay scoring, identity resolution, DraftGenerator |
| **3 — Control Interface** | Approval UX | Web dashboard, action logs, metrics view |
| **4 — Adaptation** | Personalisation | Tone adaptation, relationship-aware responses |

---

## License

Private — not licensed for public use.

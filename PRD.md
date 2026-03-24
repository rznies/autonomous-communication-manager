# PRD — Autonomous Communication Manager

## Problem Statement

Technical solo founders, seed-stage operators, and independent builders with high inbound communication volume (100–250 messages/day across email and Slack) face a problem that existing tools do not solve: **decision triage overhead**.

Current tools — Gmail Smart Reply, Slack AI, Superhuman, Shortwave — operate at the *message level*. They summarise a thread. They suggest a reply. They prioritise an inbox. But they are all single-platform and they all still present the user with the same set of micro-decisions: respond now, defer, archive, delegate, schedule, ignore.

Each of these decisions costs cognitive bandwidth. When multiplied across 100–250 daily messages across platforms — with no assistant and no filtering layer — the user spends a meaningful portion of their working day in a reactive triage loop rather than focused work.

The problem is not that users lack summaries or drafts. The problem is that **they still make every decision themselves**, one message at a time.

---

## Solution

An autonomous communication agent that operates as a **decision layer on top of communication streams** — not a replacement for email or Slack clients, but a cross-channel triage system that filters, classifies, acts on safe decisions automatically, and surfaces only the decisions that require human judgment.

The system integrates with Gmail and Slack. It monitors incoming messages, classifies them using a combination of structural heuristics, pretrained communication priors, and a learned contact graph, and performs low-risk actions automatically (archive newsletters, label by urgency, summarise threads). High-risk actions (draft replies, send messages, schedule meetings) are surfaced as suggestions and require user approval.

The agent's defining metric is the **Inbox Decision Reduction Rate (IDRR)**: the proportion of incoming messages the agent triages without requiring the user to make a decision. The target operating zone is 40–60% IDRR with a Correction Rate (CR) below 5%, prioritising precision over automation volume.

The prototype uses **Agentica Mini** for the agent runtime and runs locally against the user's personal Gmail and Slack accounts. All outgoing actions in Phase 1 are read-only. Write permissions are requested contextually when a concrete action would provide immediate value.

---

## User Stories

### Inbox Triage

1. As a solo founder, I want the agent to automatically archive newsletters, so that I don't have to manually triage low-value email every morning.
2. As a solo founder, I want newsletters and automated emails classified correctly from the first hour of use, so that I receive immediate value without a training period.
3. As a solo founder, I want emails from investors automatically flagged as high priority, so that I never accidentally miss a time-sensitive message.
4. As a solo founder, I want calendar invites categorised separately from regular emails, so that meeting requests are never buried in my inbox.
5. As a solo founder, I want to see a daily triage summary showing how many messages were handled automatically and how many require my attention, so that I understand my communication load at a glance.
6. As a solo founder, I want the agent to detect automated/no-reply emails and suppress them from my attention queue, so that system notifications don't compete with human messages.
7. As a solo founder, I want the agent to protect certain contacts from being auto-archived, so that messages from important relationships are never silently dismissed.

### Cross-Channel Awareness

8. As a solo founder, I want the agent to recognise when the same person has emailed me and Slack-messaged me within a short window, so that I'm aware of urgent cross-channel conversations without checking both platforms separately.
9. As a solo founder, I want the agent to merge cross-channel context before generating a triage decision, so that decisions are made with full conversation awareness rather than partial signals.
10. As a solo founder, I want identity links between email addresses and Slack users to be confirmed by me before they're treated as certain, so that I'm not misled by incorrect identity matches.
11. As a solo founder, I want identity matches to persist in the contact graph after confirmation, so that I don't need to re-verify the same person across sessions.

### Contact Intelligence

12. As a solo founder, I want the agent to build a profile for each contact based on interaction history, so that triage decisions improve over time as the agent learns my relationships.
13. As a solo founder, I want contacts to be assigned a relationship class (frequent collaborator, periodic contact, transactional, automated), so that importance scoring reflects the nature of the relationship rather than just recency.
14. As a solo founder, I want the importance score of a contact to decay over time if we stop interacting, so that stale relationships don't inflate priority scores.
15. As a solo founder, I want the decay rate to differ by relationship class (slower for board members, faster for recruiters), so that the model respects the natural cadence of different relationships.
16. As a solo founder, I want the agent to detect when a contact's email domain changes, so that it can reassess the relationship rather than treating the new address as an unknown sender.
17. As a solo founder, I want to be notified when a relationship reassessment is triggered, so that I can confirm or override the agent's inference.

### Draft Generation

18. As a solo founder, I want the agent to generate a draft reply for emails it classifies as requiring a response, so that I can review and send rather than compose from scratch.
19. As a solo founder, I want draft replies to reflect the contact's relationship type and communication history, so that the tone is appropriate to the relationship without manual instruction.
20. As a solo founder, I want to see the agent's reasoning for how it drafted a reply (what signals it used), so that I can trust or correct the output.
21. As a solo founder, I want to be able to edit a draft before sending, so that I remain in full control of outgoing communication.
22. As a solo founder, I want draft acceptance rate to be tracked over time, so that I can see whether the drafts are actually saving me effort.

### Activity Feed & Feedback Loop

23. As a solo founder, I want to see a real-time activity feed of every decision the agent has made, so that I have full visibility into its behaviour without needing to check my inbox.
24. As a solo founder, I want each activity feed item to show the reason for the decision, so that I understand why the agent acted rather than just what it did.
25. As a solo founder, I want to undo any agent action directly from the activity feed, so that I can reverse mistakes without navigating to Gmail or Slack.
26. As a solo founder, I want to reclassify a message from the activity feed (e.g., change "low priority" to "urgent"), so that I can correct errors without leaving the agent interface.
27. As a solo founder, I want every explicit correction I make in the activity feed to be used to improve future decisions, so that the agent learns from my feedback in near real time.
28. As a solo founder, I want the activity feed to distinguish between reversible and irreversible actions, so that I know which decisions I can undo.

### Trust & Permission Model

29. As a solo founder, I want the agent to operate in read-only mode initially, so that I can evaluate its judgment before granting it the ability to act on my accounts.
30. As a solo founder, I want write permissions to be requested contextually (at the moment the agent wants to perform a specific action), not as a bulk upfront request, so that I understand exactly what I'm authorising.
31. As a solo founder, I want the agent to never send a message without my explicit approval, so that outgoing communication is always under my control.
32. As a solo founder, I want to see a log of all agent actions with timestamps, so that I can audit what the agent has done at any time.

### Metrics & Progress

33. As a solo founder, I want to see my current IDRR (Inbox Decision Reduction Rate) over time, so that I can judge whether the agent is delivering its core promise.
34. As a solo founder, I want to see my Correction Rate (CR) alongside IDRR, so that I can detect when high automation is coming at the cost of accuracy.
35. As a solo founder, I want to be alerted if my CR rises above 5%, so that I can investigate and correct systematic misclassification before it damages my communication.

---

## Implementation Decisions

### Module Architecture

The system is composed of seven deep modules with clearly separated responsibilities:

**InboxPoller**
Handles all integration with Gmail and Slack. Manages OAuth, polling intervals, push/pull event ingestion, and normalises platform-specific message formats into a unified `IncomingEvent` schema. The rest of the system never interacts with Gmail or Slack APIs directly. Reconnection, rate limiting, and retry logic are all encapsulated here.

**ContactGraph**
Maintains the persistent communication graph. Stores contact nodes (name, identities across platforms, relationship class, importance score, last interaction, response expectations), interaction edges (timestamp, channel, message type, response time), and identity links with confidence scores. Applies time-weighted importance decay using relationship-class-specific λ values:
- Frequent collaborator: λ = 0.005 (slow decay)
- Periodic contact: λ = 0.02 (moderate decay)
- Transactional contact: λ = 0.05 (faster decay)
- Automated sender: λ = 0.1 (very fast decay)

Initial relationship class inference uses structural signals (thread depth, calendar invites, reply frequency, shared domains). User corrections override inferred classes. Role-change detection triggers when a contact's domain or interaction pattern changes significantly.

**TriageEngine**
Accepts a merged `ContactEventBatch` (from the DebounceBuffer) and a `Contact` (from the ContactGraph) and returns a `TriageDecision`: one of `{ archive, low, normal, urgent, protected }` with a confidence score and a human-readable reason string. Classification uses three layered approaches simultaneously:
1. Structural heuristics (mailing list headers, no-reply domains, calendar invite detection) — available immediately
2. Pretrained communication priors (domain-based urgency, message-type priors) — available from first hour
3. Contact graph signals (importance score, relationship class, interaction history) — improves over time

The engine exposes an `update_weights` method that accepts explicit corrections from the activity feed and updates classification weights. Protected contacts are enforced here — messages from protected contacts cannot receive an `archive` or `low` decision regardless of other signals.

**DraftGenerator**
Generates reply drafts given an `IncomingEvent`, a `Contact` profile, and thread history. Controls tone based on relationship class. Produces a `DraftReply` with a confidence score. Internally wraps LLM prompt construction and response parsing — callers receive a structured draft, not raw LLM output.

**ActionExecutor**
The only module with write access to Gmail and Slack. Executes approved actions: label, archive, send draft, schedule. Enforces the dry-run gate — all actions default to `dry_run=True` and require explicit scope elevation before execution. Every executed action is logged with a unique action ID. Exposes an `undo` method for reversible actions (label, archive). Irreversible actions (send) are flagged as such at execution time.

**ActivityFeed**
The primary human-in-the-loop interface. Emits `AgentAction` records in real time with reasoning strings. Supports user interactions: undo, confirm, reclassify. When a user interacts, the feed emits an `ExplicitCorrection` event that routes to `TriageEngine.update_weights`. This is the primary feedback channel — the learning loop depends on the activity feed being interactive from day one.

**DebounceBuffer**
Accepts `IncomingEvent` records by contact identity. Holds events from the same contact in a buffer window (default: 90 seconds) before releasing a merged `ContactEventBatch` to the agent loop. Prevents split-context processing when the same person communicates across channels in rapid succession. Grouping uses contact identity resolution and timestamp proximity; topic-similarity scoring is used as an additional deduplication signal where available.

### Identity Resolution Strategy

Identity linking across Gmail and Slack follows a layered approach:
1. **Deterministic match** — email field in Slack profile matches Gmail sender address exactly → high-confidence link
2. **Domain + name heuristic** — same company domain, similar display names → probabilistic score
3. **User confirmation** — ambiguous matches surface a confirmation prompt before the link is used for triage decisions
4. **Contact graph persistence** — confirmed links attach to a unified contact node and persist across sessions

### Technology Stack

- **Prototype language**: Python (rapid experimentation with LLM prompting, decision logic, data models)
- **Target production language**: TypeScript with Node.js (Agentica Mini, Gmail/Slack SDK compatibility)
- **Agent framework**: Agentica Mini (local, minimal abstraction, direct SDK object injection)
- **LLM routing**: OpenRouter (model-agnostic; supports Gemini, Claude, GPT models behind a single API surface)
- **Integrations**: Gmail API (Gmail read scope → Gmail modify scope on permission escalation), Slack Web API (read scope initially)

### Trust Ladder

The system progresses through four stages of autonomy:
1. **Observe** — heuristic classification, no actions taken, activity feed shows what *would* happen
2. **Recommend** — draft suggestions, triage summaries, all actions require user approval
3. **Safe Automation** — low-risk reversible actions (archiving, labelling) execute automatically; high-risk actions continue to require approval
4. **Delegated Communication** — routine outgoing messages (scheduling replies, acknowledgements) can be automated after demonstrated reliability

Stage progression is not time-gated — it is accuracy-gated. The system only escalates autonomy after IDRR and CR metrics reach target thresholds.

### Metrics System

- **IDRR** (Inbox Decision Reduction Rate) = automated decisions ÷ total incoming messages. Target: 40–60%.
- **CR** (Correction Rate) = user corrections ÷ automated decisions. Target: < 5%.
- Health quadrant: High IDRR + Low CR = healthy. High IDRR + High CR = agent is creating work. Alerts trigger when CR exceeds 5%.

---

## Testing Decisions

**What makes a good test**: Tests should verify observable, external behaviour — the decisions and outputs a module produces given specific inputs — not internal implementation details like scoring formulas, LLM prompts, or data structure internals. Tests should remain valid even if the internal algorithm changes, as long as the external contract is preserved.

### Modules to test

**TriageEngine**
- Given a mailing list email header, the decision must be `archive` or `low`
- Given a calendar invite, the decision must not be `archive`
- Given a message from a protected contact, the decision must be `protected` regardless of other signals
- Given an explicit correction, subsequent calls with equivalent inputs must produce the corrected decision class
- Given a high-importance contact (importance_score > threshold), the decision must be `urgent` or `normal`, never `archive`

**ContactGraph**
- A contact importance score must decrease over time without new interactions
- A frequent collaborator must decay slower than a transactional contact given the same elapsed time
- Identity linking two verified cross-platform identifiers must produce a unified contact node
- An unverified identity link must not affect triage decisions until confirmed

**ActionExecutor**
- In dry-run mode, no mutations must reach the Gmail or Slack APIs
- An archive action must produce a reversible undo record
- A send action must be flagged as irreversible at execution time
- Execution without write scope must be rejected with an explicit permission error, not a silent failure

**DebounceBuffer**
- Two events from the same contact within the buffer window must be released as a single batch
- Two events from the same contact outside the buffer window must be released as separate batches
- Events from different contacts must never be merged regardless of timing

### Prior art
The existing `executor_test.py` and `stubs_test.py` in `agentica-mini/agentica/` demonstrate the test patterns used in the agent framework. New tests should follow the same `asyncio` test conventions.

---

## Out of Scope

- **Autonomous message sending** — outgoing messages are always user-approved in Phase 1 and Phase 2
- **Enterprise accounts** — multi-user deployment, SOC2 compliance, data processing agreements, and enterprise OAuth flows are deferred until product validation is complete
- **Web UI / approval dashboard** — Phase 1 uses a terminal activity feed or minimal web feed; a full approval dashboard is a Phase 3 deliverable
- **Google Calendar integration** — calendar API is a Phase 2 target; Phase 1 handles calendar invites as email classification only
- **Tone adaptation / style personalisation** — requires substantial historical data; deferred to Phase 4
- **Multi-account support** — a single Gmail account and single Slack workspace per user is the Phase 1 scope
- **Mobile interface** — Phase 3 and beyond
- **Additional platforms** (Discord, Notion, CRM) — future integration candidates, not in active scope

---

## Further Notes

### Prototype Validation Hypothesis

The prototype has one job: to prove or disprove the following hypothesis within 30 days of real use by a target user:

> **Does IDRR reach 40–60% with Correction Rate below 5%?**

If yes: the thesis is validated. The prototype captures real decision reduction without generating corrective overhead. The architecture is worth porting to TypeScript and Phase 2 begins.

If no: the prototype has generated 30 days of labelled correction data and specific failure cases. The failure mode is informative — either the heuristics are too aggressive (high IDRR, high CR) or too conservative (low IDRR, low CR). Either way, the data drives the next iteration.

### Cold Start Design

The system is useful before behavioral learning occurs. From the first hour:
- Structural heuristics provide immediate newsletter/automated mail detection
- Pretrained priors provide domain-level urgency classification
- Fast behavioral adaptation begins immediately from explicit corrections in the activity feed

The user's first 48-hour experience includes: an inbox triage summary, draft suggestions, thread summaries, and an activity log. The system improves from that baseline.

### Known Risks

**First-contact classification**: New contacts with no history have no contact graph signals. Triage falls back to structural heuristics and domain priors only. This is acceptable but must be transparent — the activity feed reason string must indicate when a decision was made without graph data.

**Temporal decay λ calibration**: The λ values (0.005–0.1 by relationship class) are initial estimates, not empirically calibrated. The system must expose these values as configurable parameters and log their effect on scoring so they can be tuned against real usage data.

**Cross-channel topic similarity**: Grouping email and Slack messages from the same contact as a single conversation requires semantic similarity scoring across format boundaries. This is the most complex implementation detail in the DebounceBuffer. The first implementation should use conservative matching (timestamp proximity + same contact only) and introduce topic similarity as an additive signal in a later iteration.

**Feedback signal ambiguity**: Only *explicit* corrections (undo, reclassify in the activity feed) are treated as authoritative learning signals. Implicit behavioral signals (reopened archive, quick reply) are treated as weak signals with slow weight updates. This prevents noisy behavioral data from corrupting the classification model.

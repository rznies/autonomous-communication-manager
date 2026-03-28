# PRD — Agentica Mini Integration

## Problem Statement

The Autonomous Communication Manager currently possesses a robust event ingestion pipeline and a rule-based triage system, but lacks genuine artificial intelligence. The `DraftGenerator` is currently mocked, returning static outputs rather than context-aware replies. Furthermore, the `TriageEngine` relies entirely on static structural heuristics (e.g., mailing lists, calendar invites). Nuanced messages that require semantic understanding to classify currently bypass the heuristics or are classified incorrectly, leading to a higher Correction Rate (CR) and a lower Inbox Decision Reduction Rate (IDRR). 

## Solution

Integrate the `agentica-mini` framework to provide local, type-safe LLM intelligence to the application. `agentica-mini` will be used as a decision and generation engine rather than an autonomous execution agent. It will replace the mocked `DraftGenerator` with an LLM agent constrained to return structured `DraftReply` objects. It will also serve as an intelligent fallback layer (`AgenticaTriageRule`) within the `TriageEngine` to handle semantic classification of nuanced emails. To ensure safety and adhere to the project's Trust Ladder, the agent will only be injected with read-only wrappers for the `ContactGraph` and will strictly be forbidden from accessing the `ActionExecutor`, preserving the human-in-the-loop approval queues.

## User Stories

1. As a solo founder, I want the system to generate intelligent, context-aware draft replies to my emails, so that I spend less time typing routine responses.
2. As a solo founder, I want the generated drafts to adapt in tone based on the relationship class (e.g., investor vs. newsletter), so that I maintain appropriate professional boundaries automatically.
3. As a solo founder, I want the triage engine to intelligently classify nuanced emails that aren't caught by simple keyword rules, so that my IDRR (Inbox Decision Reduction Rate) increases.
4. As a solo founder, I want the AI to consider my historical interaction frequency with a contact when making triage decisions, so that its priority scoring mimics my actual behavior.
5. As a security-conscious user, I want the AI's execution environment to be strictly read-only, so that the LLM cannot accidentally mutate my contact database or hallucinate an action.
6. As a user relying on the Trust Ladder, I want the AI to only make *decisions* (like suggesting an archive or a draft) rather than *executing* them directly, so that all actions still flow through my UI activity feed for approval.
7. As a backend developer, I want the LLM outputs to be strictly typed to my internal dataclasses (`TriageDecision`, `DraftReply`), so that I do not have to write brittle JSON parsing logic.

## Implementation Decisions

- **DraftGenerator Module:** Will be updated to spawn an Agentica agent in its initialization. It will use `agent.call(DraftReply, prompt)` to guarantee the LLM returns the exact dataclass required by the pipeline.
- **TriageEngine Module:** A new `AgenticaTriageRule` will be added to the end of the rule evaluation chain. If structural rules return `None`, this rule will execute `agent.call(TriageDecision, prompt)` to semantically classify the message.
- **Read-Only Scope Injection:** Instead of injecting the mutable `ContactGraph` instance into the `agentica` REPL (which poses a security risk), we will inject specific, read-only wrapper functions (e.g., `get_contact_interaction_count(id)`).
- **No ActionExecutor Injection:** The `ActionExecutor` will not be exposed to the Agentica agent in any capacity. The agent acts purely as a decision-returning function, relying on the standard Python `AgentLoop` to route decisions to the execution queue.
- **Async/Await Compatibility:** `agentica-mini` uses asynchronous calls. The `DraftGenerator` and `TriageEngine` wrappers must correctly `await` the agent execution to avoid blocking the main event loop.

## Testing Decisions

- **What makes a good test:** Tests should verify that the newly integrated Agentica modules return the correct Python data types and handle LLM timeouts or failures gracefully without crashing the main `AgentLoop`.
- **Modules to be tested:** 
  - `DraftGenerator` (verifying it returns a valid `DraftReply` with content and confidence).
  - `AgenticaTriageRule` (verifying it returns a valid `TriageDecision` mapped to the correct `TriageDecisionClass` enum).
- **Prior Art:** The tests should follow the `asyncio` patterns established in `agentica-mini/agentica/executor_test.py`, potentially using a mocked LLM endpoint or a fast local model for predictable CI/CD execution.

## Out of Scope

- **Autonomous Email Sending / Action Execution:** The Agentica agent will not have access to execute Gmail/Slack API calls natively.
- **Full ContactGraph Injection:** Passing the mutable `ContactGraph` class into the LLM REPL is strictly out of scope due to data corruption risks.
- **Multi-Agent Orchestration:** While `agentica-mini` supports leader/worker patterns, Phase 1 integration will use single, isolated agents for specific tasks (Drafting, Triaging).

## Further Notes

- **Latency Considerations:** LLM generation inherently adds latency. The `AgenticaTriageRule` should only be invoked if absolutely necessary, prioritizing the fast structural heuristics first to keep the `DebounceBuffer` flowing smoothly.

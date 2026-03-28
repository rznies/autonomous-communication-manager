# Agentica Integration Issues

These vertical slices were generated from the `PRD-AGENTICA-INTEGRATION.md` and have been created as GitHub issues in the repository.

### 1. [Issue #39] Upgrade DraftGenerator to use Agentica for intelligent replies
- **Type**: AFK
- **Blocked by**: None
- **Link**: https://github.com/rznies/autonomous-communication-manager/issues/39
- **User stories covered**: 1 (Generate draft replies), 2 (Adapt tone based on relationship), 7 (Strictly typed dataclasses)
- **Description**: Replace the mocked `llm_client` in `src/emailmanagement/draft_generator.py` with an `agentica-mini` agent. The agent will be constrained via `agent.call(DraftReply, prompt)` to guarantee the output is a perfectly typed `DraftReply` dataclass that contains the AI's content and confidence score.

### 2. [Issue #40] Add AgenticaTriageRule as an intelligent fallback in TriageEngine
- **Type**: AFK
- **Blocked by**: None
- **Link**: https://github.com/rznies/autonomous-communication-manager/issues/40
- **User stories covered**: 3 (Intelligently classify nuanced emails), 7 (Strictly typed dataclasses)
- **Description**: Create a new `AgenticaTriageRule` within `src/emailmanagement/triage_engine.py`. This rule acts as a fallback after structural heuristics (like `ProtectedContactRule`) have been evaluated. It will spawn an agent to evaluate the email text and return a strict `TriageDecision` object.

### 3. [Issue #41] Inject read-only Contact Graph wrappers into AgenticaTriageRule
- **Type**: AFK
- **Blocked by**: Blocked by #40
- **Link**: https://github.com/rznies/autonomous-communication-manager/issues/41
- **User stories covered**: 4 (Consider historical interactions), 5 (Strictly read-only environment), 6 (Decisions only, no direct execution)
- **Description**: Extend the `AgenticaTriageRule` by creating safe, read-only wrapper functions for the `ContactGraph` (e.g., `get_contact_interaction_count(id)`). Inject these wrappers into the Agentica agent's `scope` upon spawn. This allows the LLM REPL to fetch context dynamically without risking database mutation or unauthorized execution.

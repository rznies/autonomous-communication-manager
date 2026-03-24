# Plan: Persistence and Error Boundary Layers

**Objective:** Transition the `emailManagement` agent from a volatile prototype into a production-grade product by ensuring state durability, ingress robustness, and supervised execution.

---

## 1. Background & Motivation
The current implementation stores all learned intelligence (Contact Graph importance scores, relationship classes, and user triage corrections) in-memory. A process restart results in a "factory reset" of the agent's brain. Furthermore, the asynchronous execution loop lacks error boundaries, meaning transient API failures or logic errors can cause silent stalls or crashes.

To be "Real World Ready," the system must:
1.  **Survive Restarts:** Retain all learned contact scoring and triage corrections.
2.  **Survive Network Instability:** Implement exponential backoff for external API calls (Gmail/Slack).
3.  **Fail Gracefully:** Report internal errors to the user via the `ActivityFeed` rather than crashing silently.
4.  **Prevent Duplicate Actions:** Ensure that retrying a failed batch doesn't result in duplicate emails or archive operations (Idempotency).

---

## 2. Proposed Solution

### A. Persistence Layer (SQLite)
Instead of a simple JSON file, we will implement an **SQLite-backed Persistence Manager**. SQLite provides atomic writes (preventing corruption during crashes) and allows for structured queries as the contact graph grows.

-   **Schema:**
    -   `contacts`: `id (PK)`, `interaction_count`, `base_score`, `relationship_class`, `last_interaction`, `is_protected`.
    -   `corrections`: `contact_id (PK)`, `decision_class`.
    -   `action_log`: `action_id (PK)`, `message_id`, `action_type`, `timestamp`, `status`.
-   **Integration:**
    -   `ContactGraph` will use the database as its "Source of Truth," using an in-memory `_nodes` cache for performance.
    -   `TriageEngine` will load `ExplicitCorrectionRule` state from the database on initialization.

### B. Error Boundary Layer (The Supervisor)
We will implement a "Supervisor" pattern within the `AgentLoop` to handle the "Real World" messiness of async tasks.

-   **Ingress Hardening:** A `backoff` decorator for `InboxPoller` to handle `429` (Rate Limit) and `5xx` (Server Error) responses from Gmail/Slack.
-   **Execution Guard:** `AgentLoop._process_batch` will be wrapped in a `try...except` block.
    -   On failure: The error is caught, the batch is logged as "Failed," and a `SystemAlert` is emitted to the `ActivityFeed` so the user knows *why* nothing is happening.
-   **Identity Safety:** `IdentityResolver` will persist "Pending" requests to the DB so they aren't lost if the app restarts before the user confirms a link.

### C. Action Idempotency
`ActionExecutor` will query the `action_log` before performing any "Write" operation.
-   If an `ARCHIVE` for `message_123` is already marked as `SUCCESS` in the log, the executor will skip the operation and return the existing result.

---

## 3. Phased Implementation Plan

### Phase 1: Persistence Foundation
- [ ] **Task 1.1:** Create `src/emailmanagement/persistence.py` with `SqliteStore` class.
- [ ] **Task 1.2:** Update `ContactGraph` to sync `_nodes` with `SqliteStore`.
- [ ] **Task 1.3:** Update `TriageEngine` to persist user corrections via `SqliteStore`.
- [ ] **Verification:** Restart the agent loop and verify that `importance_score` and `corrections` are retained.

### Phase 2: Error Boundaries & Supervision
- [ ] **Task 2.1:** Add `src/emailmanagement/utils/network.py` with an `async_retry` decorator.
- [ ] **Task 2.2:** Wrap `AgentLoop._process_batch` in a supervisor that emits errors to `ActivityFeed`.
- [ ] **Task 2.3:** Add `SystemAlert` dataclass to `ActivityFeed`.
- [ ] **Verification:** Mock a `TriageEngine` exception and verify the `ActivityFeed` displays the error instead of crashing.

### Phase 3: Idempotency & Ingress Hardening
- [ ] **Task 3.1:** Implement `ActionLog` in `SqliteStore`.
- [ ] **Task 3.2:** Update `ActionExecutor` to check the log before execution.
- [ ] **Task 3.3:** Add robust Regex and `try-except` blocks to `InboxPoller` parsing logic.
- [ ] **Verification:** Attempt to execute the same `ARCHIVE` request twice and verify the second is skipped.

---

## 4. Verification & Testing
- **Persistence Test:** A new test suite `tests/test_persistence.py` will verify DB migrations and data recovery.
- **Resilience Test:** A "Chaos Test" in `tests/test_resilience.py` will mock network failures and verify the backoff/supervisor logic.

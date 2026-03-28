# PRD — Full End-to-End Pipeline

## Problem Statement

The Autonomous Communication Manager has a fully-tested Python backend (59 passing tests, all modules implemented) and a React frontend with shadcn/ui components and MD3 design tokens. However, the two halves are not connected. The frontend has no API server to talk to, falls back to hardcoded mock data, has a broken "Approve & Send" dialog that never opens, and two of the four navigation views (Analytics, Contacts) are empty placeholder `<div>` elements. The application cannot demonstrate a single complete user flow end-to-end.

**Current state:**
- Backend: CLI-only (no HTTP server). All modules work: TriageEngine, ContactGraph, ActivityFeed, ActionExecutor, DebounceBuffer, IdentityResolver, MetricsTracker, InboxPoller, DraftGenerator, Persistence.
- Frontend: Dashboard renders with mock data fallback. Analytics (`/metrics`) and Contacts (`/contacts`) are stubs. The "Approve & Send" dialog is broken due to a nested `<button>` bug. No Vite proxy configured.
- Integration: None. The frontend's `fetch("http://127.0.0.1:8000/api/...")` calls always fail and fall back to static mock data.

The goal is to create a working end-to-end pipeline where a user can open the app, see real backend data, approve/reject drafts, view analytics metrics, browse contacts, and confirm the full flow works.

---

## Solution

Implement five changes in sequence to produce a fully-functional end-to-end application:

1. **Fix the nested button bug** in Dashboard.jsx and TopBar.jsx so all interactive elements work correctly with the @base-ui/react Dialog and Tooltip components.
2. **Build a FastAPI backend API server** that exposes the existing Python modules as HTTP endpoints (metrics, queue, approve, contacts, activity feed).
3. **Wire the frontend to the real API** by adding a Vite dev server proxy so `fetch("/api/...")` routes to the FastAPI server.
4. **Build real Analytics and Contacts pages** that fetch and display data from the API instead of showing placeholder divs.
5. **Run an end-to-end test** with agent-browser headless Chrome to verify every user-facing flow works.

---

## User Stories

### Fix Broken UI

1. As a user, I want the "Approve & Send" button on each queue item to open a confirmation dialog, so that I can approve draft messages.
2. As a user, I want the confirmation dialog to show the message type and recipient, so that I know exactly what I'm approving.
3. As a user, I want to click "Confirm & Send" inside the dialog to approve the message and remove it from the queue, so that my approval is recorded.
4. As a user, I want to click "Cancel" inside the dialog to close it without taking action, so that I can change my mind.
5. As a user, I want the notification bell icon in the top bar to show a tooltip on hover, so that I know what the icon does.
6. As a user, I want no browser console errors related to nested `<button>` elements or unrecognized `asChild` props, so that the UI is standards-compliant.

### Backend API Server

7. As a frontend developer, I want a `GET /api/metrics` endpoint that returns IDRR score, correction rate, and total handled count, so that the dashboard can display real metrics.
8. As a frontend developer, I want a `GET /api/queue` endpoint that returns pending approval items with id, type, recipient, title, score, and summary, so that the dashboard queue section shows real data.
9. As a frontend developer, I want a `POST /api/queue/{id}/approve` endpoint that approves a queued item and returns the updated queue, so that approve actions are persisted.
10. As a frontend developer, I want a `GET /api/contacts` endpoint that returns all contacts with id, relationship class, importance score, interaction count, and protected status, so that the Contacts page can display them.
11. As a frontend developer, I want a `GET /api/activity` endpoint that returns recent agent actions with timestamps, decisions, and reasons, so that the activity feed shows real data.
12. As a frontend developer, I want CORS middleware configured so the Vite dev server can make cross-origin requests during development.
13. As a frontend developer, I want the API server to be startable with a single command (`uv run uvicorn emailmanagement.api:app`), so that development setup is simple.

### Frontend-API Wiring

14. As a developer, I want a Vite proxy configuration that forwards `/api/*` requests to `http://127.0.0.1:8000`, so that the frontend can use relative URLs instead of hardcoded absolute URLs.
15. As a developer, I want the Dashboard's `useEffect` fetch calls to use relative URLs (`/api/metrics`, `/api/queue`), so that the proxy can route them to the backend.
16. As a user, I want the Dashboard to show real data from the backend when the server is running, and fall back to mock data gracefully when it isn't, so that the app remains usable in both scenarios.

### Analytics Page

17. As a user, I want the Analytics page to display the current IDRR score prominently, so that I can see the core automation metric at a glance.
18. As a user, I want the Analytics page to display the Correction Rate alongside IDRR, so that I can assess accuracy.
19. As a user, I want the Analytics page to show a health indicator (green/yellow/red) based on whether CR is below 5%, so that I can quickly assess system health.
20. As a user, I want the Analytics page to display total incoming messages and total automated decisions as summary cards, so that I understand volume.
21. As a user, I want the Analytics page to fetch data from `GET /api/metrics` on load, so that it shows real backend data.
22. As a user, I want the Analytics page to use the same MD3 design tokens and card components as the Dashboard, so that the visual style is consistent.

### Contacts Page

23. As a user, I want the Contacts page to display a list/table of all contacts from the backend, so that I can see who the system is tracking.
24. As a user, I want each contact row to show the contact ID, relationship class badge, importance score, and interaction count, so that I can understand each contact's profile.
25. As a user, I want contacts to be sorted by importance score (highest first) by default, so that the most important contacts appear at the top.
26. As a user, I want protected contacts to be visually distinguished (e.g., shield icon or highlighted row), so that I can identify them at a glance.
27. As a user, I want the Contacts page to fetch data from `GET /api/contacts` on load, so that it shows real backend data.
28. As a user, I want the Contacts page to use the same MD3 design tokens and card components as the Dashboard, so that the visual style is consistent.

### End-to-End Verification

29. As a developer, I want an automated end-to-end test that navigates to each page, verifies content renders, and confirms no console errors, so that I can trust the pipeline works.
30. As a developer, I want the end-to-end test to confirm the Approve & Send dialog opens, shows the correct content, and can be cancelled, so that the bug fix is verified.

---

## Implementation Decisions

### Module Changes

**1. Fix Nested Button Bug (Dashboard.jsx, TopBar.jsx)**

The `@base-ui/react` Dialog `Trigger` component renders its own `<button>` element. When `asChild` is passed, it is an unrecognized DOM prop (unlike Radix which supports it). The current code does `DialogTrigger asChild` wrapping `<Button>` which renders another `<button>`, creating invalid nested buttons.

Fix strategy: Remove the `asChild` prop from `DialogTrigger` and `TooltipTrigger`. Instead of wrapping a `<Button>` child, pass the button's visual content and styling directly, or use the `render` prop if supported by @base-ui/react. The simplest approach: replace `DialogTrigger asChild><Button ...>text</Button></DialogTrigger>` with `<DialogTrigger className="...button styles...">text</DialogTrigger>` — applying the button's styling classes directly to the trigger element.

Affected locations:
- `frontend/src/views/Dashboard.jsx:176` — DialogTrigger wrapping Approve & Send Button
- `frontend/src/components/TopBar.jsx:27-30` — TooltipTrigger wrapping Bell Button

**2. FastAPI Backend API Server (`src/emailmanagement/api.py`)**

New module: `api.py` containing a FastAPI application with the following endpoints:

| Method | Path | Description | Response Schema |
|--------|------|-------------|-----------------|
| GET | `/api/metrics` | Current metrics snapshot | `{ idrr_score: float, correction_rate: float, handled_total: int }` |
| GET | `/api/queue` | Pending approval items | `[{ id, type, recipient, title, score, one_line_summary }]` |
| POST | `/api/queue/{id}/approve` | Approve a queued item | `{ success: bool }` |
| GET | `/api/contacts` | All tracked contacts | `[{ id, relationship_class, importance_score, interaction_count, is_protected }]` |
| GET | `/api/activity` | Recent agent actions | `[{ id, decision, reason, timestamp, is_reversible }]` |

The API server instantiates the existing modules (ContactGraph, TriageEngine, ActivityFeed, MetricsTracker, SqliteStore) and exposes their state through the endpoints. For the initial implementation, the queue data comes from the ActivityFeed's recent actions combined with mock seed data (matching what the frontend already expects). The metrics come from MetricsTracker. Contacts come from ContactGraph/SqliteStore.

Dependencies to add: `fastapi`, `uvicorn[standard]` to `pyproject.toml`.

CORS middleware with permissive settings for development (`allow_origins=["http://localhost:5173"]`).

**3. Vite Proxy Configuration (`frontend/vite.config.js`)**

Add a `server.proxy` entry:
```js
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
    }
  }
}
```

Update `Dashboard.jsx` fetch URLs from `http://127.0.0.1:8000/api/...` to `/api/...` (relative).

**4. Analytics Page (`frontend/src/views/Analytics.jsx`)**

New view component. Layout:
- Page header: "Analytics" title with health status badge
- Top row: 3 metric cards in a grid — IDRR (large, prominent), Correction Rate, Total Automated
- Health indicator: badge color changes based on CR threshold (green < 3%, yellow 3-5%, red > 5%)
- Fallback: show skeleton loaders while loading, mock data if API unavailable

Uses existing `Card`, `CardContent`, `Badge`, `Skeleton` components. Fetches from `/api/metrics`.

**5. Contacts Page (`frontend/src/views/Contacts.jsx`)**

New view component. Layout:
- Page header: "Contacts" title with total count badge
- Contact list: vertical card list or table rows
- Each row: contact ID, relationship class badge (colored by class), importance score (bar or number), interaction count, protected shield icon if applicable
- Sorted by importance score descending
- Fallback: skeleton loaders, mock data if API unavailable

Uses existing `Card`, `CardContent`, `Badge`, `Skeleton` components. Fetches from `/api/contacts`.

**6. App.jsx Route Updates**

Replace the inline placeholder `<div>` elements with the new `Analytics` and `Contacts` view components. Add imports.

### Schema Details

**GET /api/metrics response:**
```json
{
  "idrr_score": 94.2,
  "correction_rate": 2.1,
  "handled_total": 1284,
  "total_incoming": 1362,
  "total_automated": 1284,
  "total_corrections": 27
}
```

**GET /api/queue response:**
```json
[
  {
    "id": 1,
    "type": "slack",
    "recipient": "#support",
    "title": "Urgent: API Down",
    "score": 98,
    "one_line_summary": "Customer reporting 500 errors on checkout"
  }
]
```

**GET /api/contacts response:**
```json
[
  {
    "id": "alice@example.com",
    "relationship_class": "FREQUENT",
    "importance_score": 12.5,
    "interaction_count": 24,
    "is_protected": false
  }
]
```

**GET /api/activity response:**
```json
[
  {
    "id": "uuid-string",
    "decision": "archive",
    "reason": "Mailing list detected",
    "timestamp": 1711500000.0,
    "is_reversible": true
  }
]
```

### Architecture Decisions

- The FastAPI server runs as a standalone process, separate from the Vite dev server. This mirrors a realistic production setup and avoids coupling.
- The Vite proxy is development-only. In production, a reverse proxy (nginx) or the FastAPI server serving static files would handle routing.
- The API server seeds initial mock data on startup (queue items, sample contacts) so the frontend always has something to display even without live Gmail/Slack integration. This matches the existing frontend fallback pattern.
- No database migrations needed — the existing `SqliteStore` schema is sufficient.
- The queue approval endpoint modifies in-memory state only (for now). Persistence through the existing `ActionExecutor` and `SqliteStore.log_action` is a natural extension.

---

## Testing Decisions

### What makes a good test

- Tests verify external user-facing behavior (visible content, dialog interactions, navigation) not implementation details.
- Browser console must have zero errors related to nested buttons, asChild props, or failed API calls.
- Each page must render its primary content within 5 seconds of navigation.

### Modules to test (end-to-end with agent-browser)

**Navigation:** Navigate to each route (`/queue`, `/metrics`, `/contacts`), verify the page title/heading renders, verify no console errors.

**Dashboard:** Verify metric cards display numbers, queue items render with title/recipient, "Approve & Send" button opens a dialog, dialog shows confirmation text, "Cancel" closes the dialog, "Confirm & Send" closes the dialog and removes the item.

**Analytics:** Verify IDRR score is displayed, Correction Rate is displayed, health badge color matches threshold, no console errors.

**Contacts:** Verify contact list renders, each contact shows relationship class badge and importance score, protected contacts have visual distinction, no console errors.

**Tooltip:** Hover over notification bell, verify tooltip text appears, no console errors.

### Prior art

- Existing Python tests in `tests/` use `pytest` and `asyncio` for all backend modules.
- The agent-browser skill provides `open`, `screenshot`, `click`, `fill`, `eval` commands for headless browser testing.
- Previous test report established the baseline (broken dialog, placeholder pages, console errors) to compare against.

---

## Out of Scope

- **Live Gmail/Slack integration** — the API serves from in-memory seed data and existing SQLite state. Real inbox polling is not wired to the API.
- **Authentication/authorization** — the API is open for local development.
- **Production deployment** — no Docker, nginx, or cloud configuration.
- **Edit Draft functionality** — the "Edit Draft" button in the queue remains non-functional (existing behavior).
- **Audit Log page** — `/audit-log` route is not defined in App.jsx and is not part of this PRD.
- **Real-time WebSocket updates** — the frontend uses polling (fetch on mount). WebSocket push for live activity feed is a future enhancement.
- **Mobile responsive design** — the existing frontend is desktop-focused.
- **Accessibility audit** — beyond fixing the nested button bug (which is itself an accessibility violation).

---

## Further Notes

### Implementation Order

The five steps have clear dependencies and should be implemented sequentially:

1. **Fix nested button bug** — zero-risk UI fix, unblocks dialog testing
2. **Build FastAPI API server** — independent of frontend, can be tested with curl
3. **Wire frontend to API** — depends on step 2 (server must be running), changes fetch URLs + adds proxy
4. **Build Analytics & Contacts pages** — depends on step 3 (pages need API to fetch from)
5. **End-to-end test** — depends on all above being complete

### Verification Checklist

After implementation, the following must all be true:
- [ ] `uv run uvicorn emailmanagement.api:app` starts without errors
- [ ] `curl localhost:8000/api/metrics` returns valid JSON
- [ ] `curl localhost:8000/api/queue` returns array of items
- [ ] `curl localhost:8000/api/contacts` returns array of contacts
- [ ] `npm run dev` starts Vite dev server with proxy active
- [ ] Dashboard shows real data from API (not mock fallback)
- [ ] "Approve & Send" button opens confirmation dialog
- [ ] Dialog "Cancel" closes without action
- [ ] Dialog "Confirm & Send" removes item from queue
- [ ] Analytics page shows IDRR, CR, and health badge
- [ ] Contacts page shows contact list with scores and classes
- [ ] Tooltip appears on bell icon hover
- [ ] Browser console has zero errors on any page
- [ ] All 59 existing Python tests still pass after API module addition

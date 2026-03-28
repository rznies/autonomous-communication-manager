"""FastAPI server for the Autonomous Communication Manager."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from emailmanagement.metrics import MetricsTracker
from emailmanagement.activity_feed import ActivityFeed, AgentAction
from emailmanagement.contact_graph import ContactGraph, ContactNode, RelationshipClass
from emailmanagement.persistence import SqliteStore
from emailmanagement.action_executor import ActionExecutor, ExecutionRequest, ActionType
from emailmanagement.draft_generator import DraftGenerator, DraftReply
from emailmanagement.debounce import IncomingEvent

import time
import uuid

import tempfile
import os

# ---------------------------------------------------------------------------
# Module-level instances (initialized on import)
# ---------------------------------------------------------------------------
_db_path = os.path.join(tempfile.gettempdir(), "acm_api_state.db")
store = SqliteStore(_db_path)
metrics = MetricsTracker()
feed = ActivityFeed()
graph = ContactGraph(store=store)
executor = ActionExecutor(store=store, has_write_scope=False)

# DraftGenerator — wired when an agentica agent is available (see /api/draft endpoint)
_draft_generator: DraftGenerator | None = None


def init_draft_generator(agent) -> None:
    """Wire the agentica agent into the draft generator.

    Called once at startup from main.py after spawning the agentica agent.
    """
    global _draft_generator
    _draft_generator = DraftGenerator(agent=agent)


# Seed contacts (demo data for first-time users)
_sample_contacts = [
    ("alice@engineering.com", RelationshipClass.FREQUENT, 15.0, 42, False),
    ("bot@notifications.github.com", RelationshipClass.AUTOMATED, 1.2, 200, False),
    ("investor@vc.com", RelationshipClass.FREQUENT, 20.0, 8, True),
    ("recruiter@agency.io", RelationshipClass.TRANSACTIONAL, 3.5, 5, False),
    ("team-lead@company.com", RelationshipClass.FREQUENT, 18.0, 67, False),
    ("noreply@calendar.google.com", RelationshipClass.AUTOMATED, 1.0, 150, False),
]
for cid, rcls, score, count, protected in _sample_contacts:
    node = ContactNode(
        id=cid,
        interaction_count=count,
        base_importance_score=score,
        relationship_class=rcls,
        is_protected=protected,
    )
    graph._nodes[cid] = node

# Seed activity feed (demo data)
_sample_actions = [
    ("archive", "Mailing list detected — auto-archived", True),
    ("urgent", "Investor email identified — flagged for review", True),
    ("low", "GitHub notification — Dependabot alert archived", True),
    ("normal", "Sales inquiry — draft response generated", True),
]
for decision, reason, reversible in _sample_actions:
    feed._recent_actions.append(
        AgentAction(
            id=str(uuid.uuid4()),
            event_id=str(uuid.uuid4()),
            decision=decision,
            reason=reason,
            timestamp=time.time(),
            is_reversible=reversible,
        )
    )

# In-memory approval queue (seeded with demo items)
queue_items: list[dict] = [
    {
        "id": 1,
        "type": "slack",
        "recipient": "#support",
        "title": "Urgent: API Down",
        "score": 98,
        "one_line_summary": "Customer reporting 500 errors on checkout",
    },
    {
        "id": 2,
        "type": "email",
        "recipient": "sales@example.com",
        "title": "Enterprise Pricing",
        "score": 85,
        "one_line_summary": "Inquiry about 500+ seat license",
    },
    {
        "id": 3,
        "type": "email",
        "recipient": "investor@vc.com",
        "title": "Board Deck Review",
        "score": 92,
        "one_line_summary": "Request to review Q1 board materials before Thursday",
    },
]

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(title="Autonomous Communication Manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/metrics")
def get_metrics():
    """Return current metrics snapshot."""
    return {
        "idrr_score": round(metrics.calculate_idrr() * 100, 1),
        "correction_rate": round(metrics.calculate_cr() * 100, 1),
        "handled_total": metrics.total_automated_decisions,
        "total_incoming": metrics.total_incoming_messages,
        "total_automated": metrics.total_automated_decisions,
        "total_corrections": metrics.total_corrections,
    }


@app.get("/api/queue")
def get_queue():
    """Return pending approval items."""
    return queue_items


@app.post("/api/queue/{item_id}/approve")
def approve_queue_item(item_id: int):
    """Approve a queued item by ID."""
    global queue_items
    original_len = len(queue_items)
    queue_items = [item for item in queue_items if item["id"] != item_id]
    if len(queue_items) == original_len:
        raise HTTPException(status_code=404, detail=f"Queue item {item_id} not found")
    metrics.record_automated_decision()
    return {"success": True}


@app.get("/api/contacts")
def get_contacts():
    """Return all tracked contacts."""
    results = []
    for cid in graph.get_all_contact_ids():
        node = graph._nodes[cid]
        results.append(
            {
                "id": cid,
                "relationship_class": node.relationship_class.name,
                "importance_score": round(node.base_importance_score, 1),
                "interaction_count": node.interaction_count,
                "is_protected": node.is_protected,
            }
        )
    results.sort(key=lambda c: c["importance_score"], reverse=True)
    return results


@app.get("/api/activity")
def get_activity():
    """Return recent agent actions."""
    actions = feed.get_recent_actions()
    return [
        {
            "id": a.id,
            "decision": a.decision,
            "reason": a.reason,
            "timestamp": a.timestamp,
            "is_reversible": a.is_reversible,
        }
        for a in actions
    ]


@app.post("/api/draft")
async def generate_draft(contact_id: str, content: str):
    """Generate a draft reply for an email using agentica.

    Query params:
        contact_id: The sender's email address
        content: The email body to reply to
    """
    if _draft_generator is None:
        raise HTTPException(
            status_code=503,
            detail="Draft generator not initialized. Set OPENROUTER_API_KEY and restart.",
        )

    contact = await graph.get_contact(contact_id)
    if contact is None:
        contact = ContactNode(id=contact_id)

    event = IncomingEvent(
        id=str(uuid.uuid4()),
        contact_id=contact_id,
        content=content,
        timestamp=time.time(),
        headers={},
    )

    draft = await _draft_generator.generate_draft(event, contact)
    return {
        "content": draft.content,
        "confidence": round(draft.confidence, 2),
    }

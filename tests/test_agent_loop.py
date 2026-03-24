import pytest
import asyncio
from emailmanagement.debounce import IncomingEvent, DebounceBuffer
from emailmanagement.triage_engine import TriageEngine
from emailmanagement.activity_feed import ActivityFeed
from emailmanagement.contact_graph import ContactGraph
from emailmanagement.identity_resolver import IdentityResolver
from emailmanagement.agent_loop import AgentLoop


class MockPoller:
    def __init__(self, events):
        self.events = events
    async def poll(self):
        return self.events


def make_loop(events, debounce_window=0.0):
    """Helper: build an AgentLoop via create() with a MockPoller."""
    poller = MockPoller(events)
    graph = ContactGraph()
    engine = TriageEngine()
    feed = ActivityFeed()
    return AgentLoop.create(
        poller=poller,
        graph=graph,
        engine=engine,
        feed=feed,
        debounce_window=debounce_window,
    )


@pytest.mark.asyncio
async def test_agent_loop_observe_mode():
    """
    Tracer bullet: poll → debounce → triage → emit.
    No asyncio.sleep timing hack — we use debounce_window=0 which lets the
    timer fire on the first event-loop tick after step().
    """
    event = IncomingEvent(
        id="evt_1",
        contact_id="founder@startup.com",
        timestamp=100.0,
        content="Newsletter body...",
        headers={"List-Unsubscribe": "yes"}
    )

    loop = make_loop([event])
    await loop.step()
    await asyncio.sleep(0.01)  # Allow debounce timer to fire (window=0, real timer task)

    recent_actions = loop.feed.get_recent_actions()
    assert len(recent_actions) == 1
    assert recent_actions[0].decision == "archive"
    assert recent_actions[0].event_id == "evt_1"


@pytest.mark.asyncio
async def test_agent_loop_identity_confirmation():
    """
    When two contacts with matching local parts arrive, AgentLoop should
    surface an identity confirmation request via the feed (using IdentityResolver).
    """
    event1 = IncomingEvent(
        id="evt_email",
        contact_id="john.doe@company.com",
        timestamp=100.0,
        content="Hello from email",
        headers={"source": "gmail"}
    )
    event2 = IncomingEvent(
        id="evt_slack",
        contact_id="john.doe_slack",
        timestamp=105.0,
        content="Hello from slack",
        headers={"source": "slack"}
    )

    loop = make_loop([event1, event2])
    await loop.step()
    await asyncio.sleep(0.01)

    reqs = loop.feed.get_pending_identity_requests()
    assert len(reqs) == 1
    assert "john.doe@company.com" in (reqs[0].primary_id, reqs[0].secondary_id)
    assert "john.doe_slack" in (reqs[0].primary_id, reqs[0].secondary_id)

    # Confirm it — should merge via IdentityResolver
    linked = []
    original_link = loop.graph.link_identities
    async def mock_link(id1, id2, verified):
        linked.append((id1, id2, verified))
        await original_link(id1, id2, verified)
    loop.graph.link_identities = mock_link

    await loop.feed.resolve_identity(reqs[0].id, confirmed=True)
    assert len(linked) == 1
    assert linked[0][2] is True


@pytest.mark.asyncio
async def test_agent_loop_wires_corrections():
    """
    When the user corrections a decision via ActivityFeed, the next triage of the
    same contact should reflect the corrected decision (behavioral, not internal-state).
    """
    event1 = IncomingEvent(
        id="evt_1",
        contact_id="marketing@startup.com",
        timestamp=100.0,
        content="Buy now",
        headers={"Precedence": "bulk"}
    )

    loop = make_loop([event1])
    await loop.step()
    await asyncio.sleep(0.01)

    actions = loop.feed.get_recent_actions()
    assert len(actions) == 1
    assert actions[0].decision == "archive"

    # User corrects to "normal"
    from emailmanagement.activity_feed import ExplicitCorrection
    correction = ExplicitCorrection(
        action_id=actions[0].id,
        corrected_decision="normal",
        reason="I actually want these"
    )
    await loop.feed.receive_correction(correction)
    await asyncio.sleep(0.01)

    # Behavioral assertion: triage the same contact again — should now yield "normal"
    from emailmanagement.debounce import IncomingEvent as IE
    event2 = IE(id="evt_2", contact_id="marketing@startup.com", timestamp=200.0, content="Another offer", headers={})
    result = await loop.engine.triage(event2)
    assert result.decision_class.name.lower() == "normal"

@pytest.mark.asyncio
async def test_agent_loop_updates_metrics():
    """
    AgentLoop should orchestrate the MetricsTracker by recording incoming messages,
    automated decisions, and user corrections.
    """
    event1 = IncomingEvent(
        id="evt_1",
        contact_id="marketing@startup.com",
        timestamp=100.0,
        content="Buy now",
        headers={"Precedence": "bulk"}
    )

    loop = make_loop([event1])
    
    # Before step, IDRR is 0
    assert loop.metrics.calculate_idrr() == 0.0
    
    await loop.step()
    await asyncio.sleep(0.01)

    # After step, 1 incoming, 1 automated decision
    assert loop.metrics.total_incoming_messages == 1
    assert loop.metrics.calculate_idrr() == 1.0
    assert loop.metrics.calculate_cr() == 0.0

    # User corrects the decision
    actions = loop.feed.get_recent_actions()
    from emailmanagement.activity_feed import ExplicitCorrection
    correction = ExplicitCorrection(
        action_id=actions[0].id,
        corrected_decision="normal",
        reason="I actually want these"
    )
    
    await loop.feed.receive_correction(correction)
    await asyncio.sleep(0.01)

    # After correction, cr should be > 0
    assert loop.metrics.total_corrections == 1
    assert loop.metrics.calculate_cr() == 1.0

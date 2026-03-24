import pytest
import asyncio
from emailmanagement.inbox_poller import IncomingEvent
from emailmanagement.triage_engine import TriageEngine, TriageDecision
from emailmanagement.activity_feed import ActivityFeed, AgentAction
from emailmanagement.contact_graph import ContactGraph, ContactNode

# We will need the AgentLoop class, which doesn't exist yet.
from emailmanagement.agent_loop import AgentLoop

class MockPoller:
    def __init__(self, events):
        self.events = events
    async def poll(self):
        return self.events

@pytest.mark.asyncio
async def test_agent_loop_observe_mode():
    """
    Tracer bullet: The agent loop reads from the poller, debounces, 
    triages, and emits to the activity feed (without executing actions).
    """
    event = IncomingEvent(
        id="evt_1",
        contact_id="founder@startup.com",
        timestamp=100.0,
        content="Newsletter body...", 
        headers={"List-Unsubscribe": "yes"}
    )
    
    poller = MockPoller([event])
    graph = ContactGraph()
    engine = TriageEngine()
    feed = ActivityFeed()
    
    loop = AgentLoop(
        poller=poller,
        graph=graph,
        engine=engine,
        feed=feed,
        debounce_window=0.0
    )
    
    await loop.step()
    
    # Allow background tasks from DebounceBuffer to complete
    await asyncio.sleep(0.01)
    
    recent_actions = feed.get_recent_actions()
    assert len(recent_actions) == 1
    assert recent_actions[0].decision == "archive" # based on Newsletter header
    assert recent_actions[0].event_id == "evt_1"

@pytest.mark.asyncio
async def test_agent_loop_identity_confirmation():
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
    
    poller = MockPoller([event1, event2])
    graph = ContactGraph()
    engine = TriageEngine()
    
    # We will track if graph.link_identities is called
    linked = []
    original_link = graph.link_identities
    async def mock_link(id1, id2, verified):
        linked.append((id1, id2, verified))
        await original_link(id1, id2, verified)
    graph.link_identities = mock_link
    
    feed = ActivityFeed()
    
    loop = AgentLoop(
        poller=poller,
        graph=graph,
        engine=engine,
        feed=feed,
        debounce_window=0.0
    )
    
    await loop.step()
    await asyncio.sleep(0.01)
    
    # Should have a pending identity request
    reqs = feed.get_pending_identity_requests()
    assert len(reqs) == 1
    assert reqs[0].primary_id == "john.doe@company.com" or reqs[0].secondary_id == "john.doe@company.com"
    
    # Confirm it
    await feed.resolve_identity(reqs[0].id, confirmed=True)
    
    assert len(linked) == 1
    assert linked[0][2] is True # verified

@pytest.mark.asyncio
async def test_agent_loop_wires_corrections():
    from emailmanagement.activity_feed import ExplicitCorrection
    from emailmanagement.triage_engine import TriageDecisionClass
    
    event1 = IncomingEvent(
        id="evt_1",
        contact_id="marketing@startup.com",
        timestamp=100.0,
        content="Buy now",
        headers={"Precedence": "bulk"} # Defaults to ARCHIVE
    )
    
    poller = MockPoller([event1])
    graph = ContactGraph()
    engine = TriageEngine()
    feed = ActivityFeed()
    
    loop = AgentLoop(
        poller=poller,
        graph=graph,
        engine=engine,
        feed=feed,
        debounce_window=0.0
    )
    
    await loop.step()
    await asyncio.sleep(0.01)
    
    actions = feed.get_recent_actions()
    assert len(actions) == 1
    assert actions[0].decision == "archive"
    
    # User provides a correction via ActivityFeed
    correction = ExplicitCorrection(
        action_id=actions[0].id,
        corrected_decision="normal",
        reason="I actually want these"
    )
    await feed.receive_correction(correction)
    
    # Allow the callback to run
    await asyncio.sleep(0.01)
    
    # We should see that the engine's internal weights were updated
    assert "marketing@startup.com" in engine._corrections
    assert engine._corrections["marketing@startup.com"] == TriageDecisionClass.NORMAL

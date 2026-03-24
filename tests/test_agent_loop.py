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

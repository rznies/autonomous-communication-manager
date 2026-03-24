import pytest
import asyncio
from emailmanagement.activity_feed import ActivityFeed, AgentAction, ExplicitCorrection

@pytest.mark.asyncio
async def test_emit_agent_action_stores_in_history():
    feed = ActivityFeed()
    
    action = AgentAction(
        id="act_123",
        event_id="evt_abc",
        decision="archive",
        reason="Matched low-priority newsletter heuristic",
        timestamp=1711283000.0
    )
    
    await feed.emit(action)
    
    # Verify it was stored in recent history so it can be corrected later
    assert len(feed.get_recent_actions()) == 1
    assert feed.get_recent_actions()[0].id == "act_123"

@pytest.mark.asyncio
async def test_emit_identifies_reversible_actions():
    feed = ActivityFeed()
    
    reversible_action = AgentAction(
        id="act_124",
        event_id="evt_abc",
        decision="archive",
        reason="Low priority",
        timestamp=1711283000.0,
        is_reversible=True
    )
    
    irreversible_action = AgentAction(
        id="act_125",
        event_id="evt_def",
        decision="send",
        reason="User approved",
        timestamp=1711283005.0,
        is_reversible=False
    )
    
    await feed.emit(reversible_action)
    await feed.emit(irreversible_action)
    
    recent = feed.get_recent_actions()
    assert len(recent) == 2
    assert recent[0].is_reversible is True
    assert recent[1].is_reversible is False

@pytest.mark.asyncio
async def test_receive_explicit_correction():
    received_corrections = []
    
    async def mock_callback(correction):
        received_corrections.append(correction)
        
    feed = ActivityFeed(on_correction=mock_callback)
    
    correction = ExplicitCorrection(
        action_id="act_456",
        corrected_decision="urgent",
        reason="It's from my investor"
    )
    
    await feed.receive_correction(correction)
    
    assert len(received_corrections) == 1
    assert received_corrections[0].action_id == "act_456"
    assert received_corrections[0].corrected_decision == "urgent"

@pytest.mark.asyncio
async def test_undo_reversible_action():
    received_undos = []
    
    async def mock_undo_callback(action_id):
        received_undos.append(action_id)
        
    feed = ActivityFeed(on_undo=mock_undo_callback)
    action = AgentAction(
        id="act_123", 
        event_id="evt_abc", 
        decision="archive", 
        reason="test", 
        timestamp=1.0, 
        is_reversible=True
    )
    await feed.emit(action)
    
    await feed.undo("act_123")
    
    assert len(received_undos) == 1
    assert received_undos[0] == "act_123"

@pytest.mark.asyncio
async def test_undo_irreversible_action_raises_error():
    feed = ActivityFeed()
    action = AgentAction(
        id="act_124", 
        event_id="evt_abc", 
        decision="send", 
        reason="test", 
        timestamp=1.0, 
        is_reversible=False
    )
    await feed.emit(action)
    
    with pytest.raises(ValueError, match="Action act_124 is not reversible"):
        await feed.undo("act_124")

@pytest.mark.asyncio
async def test_emit_identity_confirmation_request():
    from emailmanagement.activity_feed import IdentityConfirmationRequest
    
    received_confirmations = []
    
    async def mock_identity_callback(request_id, confirmed):
        received_confirmations.append((request_id, confirmed))
        
    feed = ActivityFeed(on_identity_confirm=mock_identity_callback)
    
    req = IdentityConfirmationRequest(
        id="req_1",
        primary_id="alice@startup.com",
        secondary_id="alice_slack",
        confidence=0.85
    )
    
    await feed.request_identity_confirmation(req)
    
    assert len(feed.get_pending_identity_requests()) == 1
    
    await feed.resolve_identity("req_1", confirmed=True)
    
    assert len(received_confirmations) == 1
    assert received_confirmations[0] == ("req_1", True)
    assert len(feed.get_pending_identity_requests()) == 0


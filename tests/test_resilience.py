import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from emailmanagement.agent_loop import AgentLoop
from emailmanagement.triage_engine import TriageEngine
from emailmanagement.activity_feed import ActivityFeed
from emailmanagement.contact_graph import ContactGraph
from emailmanagement.debounce import ContactEventBatch, IncomingEvent

@pytest.mark.asyncio
async def test_agent_loop_supervisor_catches_errors():
    # Setup mocks
    poller = AsyncMock()
    graph = AsyncMock(spec=ContactGraph)
    graph.get_all_contact_ids.return_value = []
    
    # Mock engine to raise an exception
    engine = MagicMock(spec=TriageEngine)
    engine.triage = AsyncMock(side_effect=RuntimeError("LLM Timeout"))
    
    feed = ActivityFeed()
    
    loop = AgentLoop.create(
        poller=poller,
        graph=graph,
        engine=engine,
        feed=feed,
        debounce_window=0.01
    )
    
    # Create a batch to process
    event = IncomingEvent(id="msg_err", contact_id="fail@test.com", content="test", timestamp=0.0)
    batch = ContactEventBatch(contact_id="fail@test.com", events=[event])
    
    # Manually trigger process_batch to simulate background release
    await loop._process_batch(batch)
    
    # Verify alert was emitted
    alerts = feed.get_alerts()
    assert len(alerts) == 1
    assert alerts[0].severity == "ERROR"
    assert "LLM Timeout" in alerts[0].message
    assert "fail@test.com" in alerts[0].message

@pytest.mark.asyncio
async def test_async_retry_decorator():
    from emailmanagement.utils.network import async_retry
    
    mock_func = AsyncMock(side_effect=[RuntimeError("Fail 1"), RuntimeError("Fail 2"), "Success"])
    
    @async_retry(retries=3, initial_delay=0.01)
    async def decorated_func():
        return await mock_func()
        
    result = await decorated_func()
    assert result == "Success"
    assert mock_func.call_count == 3

@pytest.mark.asyncio
async def test_async_retry_fails_after_max_retries():
    from emailmanagement.utils.network import async_retry
    
    mock_func = AsyncMock(side_effect=RuntimeError("Permanent Fail"))
    
    @async_retry(retries=2, initial_delay=0.01)
    async def decorated_func():
        return await mock_func()
        
    with pytest.raises(RuntimeError, match="Permanent Fail"):
        await decorated_func()
    
    assert mock_func.call_count == 2

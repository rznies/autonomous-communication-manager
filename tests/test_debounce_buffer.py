import pytest
import asyncio
from emailmanagement.debounce import DebounceBuffer, IncomingEvent

@pytest.mark.asyncio
async def test_debounce_buffer_releases_single_event_after_window():
    # Arrange
    released_batches = []
    
    async def on_batch(batch):
        released_batches.append(batch)
        
    buffer = DebounceBuffer(window_seconds=0.1, on_release=on_batch)
    
    event = IncomingEvent(
        id="msg_1", 
        contact_id="user_1",
        content="Hello",
        timestamp=0.0
    )
    
    # Act
    await buffer.add_event(event)
    
    # Immediately it should not be released
    assert len(released_batches) == 0
    
    # Wait for the window to pass
    await asyncio.sleep(0.15)
    
    # Assert
    assert len(released_batches) == 1
    assert released_batches[0].contact_id == "user_1"
    assert len(released_batches[0].events) == 1
    assert released_batches[0].events[0].id == "msg_1"

@pytest.mark.asyncio
async def test_debounce_buffer_batches_events_from_same_contact():
    released_batches = []
    
    async def on_batch(batch):
        released_batches.append(batch)
        
    buffer = DebounceBuffer(window_seconds=0.1, on_release=on_batch)
    
    event1 = IncomingEvent(id="msg_1", contact_id="user_1", content="Hi", timestamp=0.0)
    event2 = IncomingEvent(id="msg_2", contact_id="user_1", content="There", timestamp=0.05)
    
    await buffer.add_event(event1)
    
    # Wait some time but less than window_seconds
    await asyncio.sleep(0.06)
    assert len(released_batches) == 0
    
    # Add second event before window expires
    await buffer.add_event(event2)
    
    # Wait more time. This would exceed the first event's window but not the second's
    await asyncio.sleep(0.06)
    assert len(released_batches) == 0
    
    # Wait enough for the second event's window to pass
    await asyncio.sleep(0.06)
    
    assert len(released_batches) == 1
    assert released_batches[0].contact_id == "user_1"
    assert len(released_batches[0].events) == 2
    assert released_batches[0].events[0].id == "msg_1"
    assert released_batches[0].events[1].id == "msg_2"

@pytest.mark.asyncio
async def test_debounce_buffer_isolates_different_contacts():
    released_batches = []
    
    async def on_batch(batch):
        released_batches.append(batch)
        
    buffer = DebounceBuffer(window_seconds=0.1, on_release=on_batch)
    
    event_u1 = IncomingEvent(id="1", contact_id="user_1", content="X", timestamp=0.0)
    event_u2 = IncomingEvent(id="2", contact_id="user_2", content="Y", timestamp=0.05)
    
    await buffer.add_event(event_u1)
    await asyncio.sleep(0.05)
    await buffer.add_event(event_u2)
    
    # Wait for user_1 to timeout (0.1 from its start = 0.05 more)
    await asyncio.sleep(0.06)
    
    assert len(released_batches) == 1
    assert released_batches[0].contact_id == "user_1"
    
    # Wait for user_2 to timeout
    await asyncio.sleep(0.06)
    
    assert len(released_batches) == 2
    assert released_batches[1].contact_id == "user_2"

@pytest.mark.asyncio
async def test_debounce_buffer_flush_pending_events_on_shutdown():
    released_batches = []
    
    async def on_batch(batch):
        released_batches.append(batch)
        
    buffer = DebounceBuffer(window_seconds=0.1, on_release=on_batch)
    
    event1 = IncomingEvent(id="msg_1", contact_id="user_1", content="Hi", timestamp=0.0)
    await buffer.add_event(event1)
    
    # We do not wait 0.1s. We shutdown immediately.
    await buffer.shutdown(flush=True)
    
    assert len(released_batches) == 1
    assert released_batches[0].contact_id == "user_1"


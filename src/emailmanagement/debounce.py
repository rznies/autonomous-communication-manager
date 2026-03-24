import asyncio
from dataclasses import dataclass, field
from typing import List, Callable, Awaitable

@dataclass
class IncomingEvent:
    id: str
    contact_id: str
    content: str
    timestamp: float
    headers: dict = field(default_factory=dict)

@dataclass
class ContactEventBatch:
    contact_id: str
    events: List[IncomingEvent]

class DebounceBuffer:
    def __init__(self, window_seconds: float, on_release: Callable[[ContactEventBatch], Awaitable[None]]):
        self.window_seconds = window_seconds
        self.on_release = on_release
        self._buffers = {}
        self._tasks = {}

    async def add_event(self, event: IncomingEvent):
        contact_id = event.contact_id
        if contact_id not in self._buffers:
            self._buffers[contact_id] = []
            
        self._buffers[contact_id].append(event)
        
        # Cancel any existing timeout task
        if contact_id in self._tasks:
            self._tasks[contact_id].cancel()
            
        # Create a new timeout task
        self._tasks[contact_id] = asyncio.create_task(self._wait_and_release(contact_id))
        
    async def _wait_and_release(self, contact_id: str):
        try:
            await asyncio.sleep(self.window_seconds)
            # Window passed without cancellation, so release
            events = self._buffers.pop(contact_id)
            del self._tasks[contact_id]
            batch = ContactEventBatch(contact_id=contact_id, events=events)
            await self.on_release(batch)
        except asyncio.CancelledError:
            pass

    async def shutdown(self, flush: bool = False):
        """
        Stop the debounce buffer.
        If flush is True, any pending events are immediately released.
        """
        for contact_id, task in list(self._tasks.items()):
            task.cancel()
            
            if flush and contact_id in self._buffers:
                events = self._buffers.pop(contact_id)
                batch = ContactEventBatch(contact_id=contact_id, events=events)
                await self.on_release(batch)
            elif contact_id in self._buffers:
                del self._buffers[contact_id]
                
            if contact_id in self._tasks:
                del self._tasks[contact_id]

import uuid
import time
import asyncio
from typing import Any
from emailmanagement.debounce import DebounceBuffer, ContactEventBatch
from emailmanagement.triage_engine import TriageEngine
from emailmanagement.activity_feed import ActivityFeed, AgentAction
from emailmanagement.contact_graph import ContactGraph, InteractionType

class AgentLoop:
    def __init__(
        self, 
        poller: Any, 
        graph: ContactGraph, 
        engine: TriageEngine, 
        feed: ActivityFeed,
        debounce_window: float = 90.0
    ):
        self.poller = poller
        self.graph = graph
        self.engine = engine
        self.feed = feed
        self.buffer = DebounceBuffer(window_seconds=debounce_window, on_release=self._process_batch)

    async def step(self):
        events = await self.poller.poll()
        for event in events:
            # Reconcile different IncomingEvent schemas if necessary
            # The poller might use sender_id, Debounce expects contact_id
            if hasattr(event, "sender_id") and not hasattr(event, "contact_id"):
                event.contact_id = event.sender_id
                
            await self.graph.record_interaction(event.contact_id, InteractionType.EMAIL_RECEIVED)
            await self.buffer.add_event(event)

        # Allow the event loop to run the timeout tasks in the buffer
        # This is especially needed when testing with debounce_window=0
        await asyncio.sleep(0)

    async def _process_batch(self, batch: ContactEventBatch):
        contact = await self.graph.get_contact(batch.contact_id)
        
        # In this prototype, we triage based on the first event in the batch
        primary_event = batch.events[0] if batch.events else None
        if not primary_event:
            return
            
        decision = await self.engine.triage(primary_event, contact)
        
        decision_str = decision.decision_class.name.lower()
        
        action = AgentAction(
            id=str(uuid.uuid4()),
            event_id=primary_event.id,
            decision=decision_str,
            reason=decision.reason,
            timestamp=time.time(),
            is_reversible=(decision_str in ["archive", "low", "normal", "urgent"])
        )
        await self.feed.emit(action)

    async def shutdown(self):
        """Cleanly shutdown the loop and flush the buffer"""
        await self.buffer.shutdown(flush=True)

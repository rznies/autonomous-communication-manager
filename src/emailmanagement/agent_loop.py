import uuid
import time
import asyncio
from typing import Any
from emailmanagement.debounce import DebounceBuffer, ContactEventBatch
from emailmanagement.triage_engine import TriageEngine
from emailmanagement.activity_feed import ActivityFeed, AgentAction, IdentityConfirmationRequest
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
        
        # Wire up the identity confirmation callback
        self.feed._on_identity_confirm = self._handle_identity_confirmation

    async def _handle_identity_confirmation(self, request_id: str, confirmed: bool):
        # We need to look up the request to get the IDs, but ActivityFeed removes it.
        # For this prototype, we'll store a local map of request_id -> (id1, id2)
        if hasattr(self, "_pending_identity_links") and request_id in self._pending_identity_links:
            id1, id2 = self._pending_identity_links.pop(request_id)
            await self.graph.link_identities(id1, id2, verified=confirmed)

    async def _check_identity_heuristics(self, new_contact_id: str):
        # Basic heuristic: if one is 'john.doe@company.com' and the other is 'john.doe_slack'
        # Or if the local parts match exactly.
        if not hasattr(self, "_pending_identity_links"):
            self._pending_identity_links = {}
            
        new_local = new_contact_id.split("@")[0].replace("_slack", "")
        
        for existing_id in self.graph._nodes.keys():
            if existing_id == new_contact_id:
                continue
                
            existing_local = existing_id.split("@")[0].replace("_slack", "")
            
            if new_local == existing_local:
                # Potential match
                req_id = str(uuid.uuid4())
                self._pending_identity_links[req_id] = (existing_id, new_contact_id)
                req = IdentityConfirmationRequest(
                    id=req_id,
                    primary_id=existing_id,
                    secondary_id=new_contact_id,
                    confidence=0.8
                )
                await self.feed.request_identity_confirmation(req)
                return # Only trigger one per new contact

    async def step(self):
        events = await self.poller.poll()
        for event in events:
            # Reconcile different IncomingEvent schemas if necessary
            # The poller might use sender_id, Debounce expects contact_id
            if hasattr(event, "sender_id") and not hasattr(event, "contact_id"):
                event.contact_id = event.sender_id
                
            # Check for identity matches before recording
            if event.contact_id not in self.graph._nodes:
                await self._check_identity_heuristics(event.contact_id)
                
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

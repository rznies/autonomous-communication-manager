import uuid
import time
import asyncio
from typing import Any
from emailmanagement.debounce import DebounceBuffer, ContactEventBatch
from emailmanagement.triage_engine import TriageEngine
from emailmanagement.activity_feed import ActivityFeed, AgentAction, SystemAlert
from emailmanagement.contact_graph import ContactGraph, InteractionType
from emailmanagement.identity_resolver import IdentityResolver
from emailmanagement.metrics import MetricsTracker


class AgentLoop:
    """
    Orchestrates the poll → debounce → triage → emit pipeline.

    Construction:
      - Use AgentLoop.create() for production and simple test scenarios.
      - Use AgentLoop.__init__() directly when you need to inject a custom
        DebounceBuffer or IdentityResolver (e.g. advanced test scenarios).

    Public interface:
      - step()    — run one poll-and-buffer cycle
      - shutdown() — flush pending events and stop

    All callback wiring and internal state management is encapsulated here.
    Callers do not need to touch ActivityFeed callbacks or ContactGraph internals.
    """

    def __init__(
        self,
        poller: Any,
        graph: ContactGraph,
        engine: TriageEngine,
        feed: ActivityFeed,
        buffer: DebounceBuffer,
        resolver: IdentityResolver,
        metrics: MetricsTracker = None,
    ):
        self.poller = poller
        self.graph = graph
        self.engine = engine
        self.feed = feed
        self.buffer = buffer
        self.resolver = resolver
        self.metrics = metrics or MetricsTracker()
        # Maps event_id -> contact_id for correction routing
        self._event_contact_map: dict[str, str] = {}

    @classmethod
    def create(
        cls,
        poller: Any,
        graph: ContactGraph,
        engine: TriageEngine,
        feed: ActivityFeed,
        debounce_window: float = 90.0,
        metrics: MetricsTracker = None,
    ) -> "AgentLoop":
        """
        Factory that wires all components correctly. Use this in production.
        Internally creates the DebounceBuffer and IdentityResolver.
        AgentLoop subscribes to the ActivityFeed explicitly as an observer.
        """
        resolver = IdentityResolver(graph=graph, feed=feed)

        # Buffer is created after we have a reference to resolve the circular dep
        instance = cls(
            poller=poller,
            graph=graph,
            engine=engine,
            feed=feed,
            buffer=DebounceBuffer(window_seconds=debounce_window, on_release=None),
            resolver=resolver,
            metrics=metrics,
        )
        # Wire the buffer's on_release callback now that instance exists
        instance.buffer.on_release = instance._process_batch
        
        # Subscribe AgentLoop to ActivityFeed
        feed.subscribe(instance)
        
        return instance

    async def on_correction(self, correction):
        from emailmanagement.triage_engine import TriageDecisionClass
        action = next((a for a in self.feed.get_recent_actions() if a.id == correction.action_id), None)
        if action:
            contact_id = self._event_contact_map.get(action.event_id)
            if contact_id:
                try:
                    decision_class = TriageDecisionClass[correction.corrected_decision.upper()]
                    await self.engine.update_weights(contact_id, decision_class)
                    self.metrics.record_correction()
                except KeyError:
                    pass

    async def on_identity_confirm(self, request_id: str, confirmed: bool):
        await self.resolver.confirm(request_id, confirmed)

    async def step(self):
        """
        One full cycle: poll events → record interactions → debounce.
        Triage and emit happen asynchronously via the buffer's on_release callback.
        """
        events = await self.poller.poll()
        for event in events:
            self.metrics.record_incoming_message()
            # Reconcile different IncomingEvent schemas
            if hasattr(event, "sender_id") and not hasattr(event, "contact_id"):
                event.contact_id = event.sender_id

            # Check for identity matches before recording (only for new contacts)
            if event.contact_id not in self.graph.get_all_contact_ids():
                await self.resolver.check_and_request(event.contact_id)

            await self.graph.record_interaction(event.contact_id, InteractionType.EMAIL_RECEIVED)
            await self.buffer.add_event(event)

        # Allow the event loop to run any ready background tasks (e.g. debounce timers)
        await asyncio.sleep(0)

    async def _process_batch(self, batch: ContactEventBatch):
        try:
            contact = await self.graph.get_contact(batch.contact_id)

            primary_event = batch.events[0] if batch.events else None
            if not primary_event:
                return

            self._event_contact_map[primary_event.id] = batch.contact_id

            decision = await self.engine.triage(primary_event, contact)
            self.metrics.record_automated_decision()
            decision_str = decision.decision_class.name.lower()

            action = AgentAction(
                id=str(uuid.uuid4()),
                event_id=primary_event.id,
                decision=decision_str,
                reason=decision.reason,
                timestamp=time.time(),
                is_reversible=(decision_str in ["archive", "low", "normal", "urgent"]),
            )
            await self.feed.emit(action)
        except Exception as e:
            alert = SystemAlert(
                id=str(uuid.uuid4()),
                message=f"Triage failed for contact {batch.contact_id}: {str(e)}",
                severity="ERROR",
                timestamp=time.time()
            )
            await self.feed.emit_alert(alert)

    async def shutdown(self):
        """Cleanly shut down the loop and flush the buffer."""
        await self.buffer.shutdown(flush=True)

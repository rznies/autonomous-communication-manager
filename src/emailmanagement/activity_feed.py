from dataclasses import dataclass
from typing import Callable, Awaitable, List

@dataclass
class AgentAction:
    id: str
    event_id: str
    decision: str
    reason: str
    timestamp: float
    is_reversible: bool = True

@dataclass
class ExplicitCorrection:
    action_id: str
    corrected_decision: str
    reason: str = ""

@dataclass
class IdentityConfirmationRequest:
    id: str
    primary_id: str
    secondary_id: str
    confidence: float

@dataclass
class SystemAlert:
    id: str
    message: str
    severity: str  # e.g., "ERROR", "WARNING", "INFO"
    timestamp: float

class ActivityFeed:
    """
    Primary human-in-the-loop interface. Emits AgentAction records in real time
    and handles user corrections.
    """
    def __init__(self):
        self._recent_actions: List[AgentAction] = []
        self._pending_identity_requests: List[IdentityConfirmationRequest] = []
        self._alerts: List[SystemAlert] = []
        self._observers = []

    def subscribe(self, observer) -> None:
        """Subscribe an observer to feed events."""
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer) -> None:
        """Unsubscribe an observer."""
        if observer in self._observers:
            self._observers.remove(observer)
        
    async def emit(self, action: AgentAction):
        """
        Emits an action to the feed (e.g., terminal log) and stores it in recent history.
        """
        self._recent_actions.append(action)
        print(f"[ActivityFeed] Action {action.id}: decided {action.decision} for event {action.event_id}. Reason: {action.reason}")
        for obs in self._observers:
            if hasattr(obs, 'on_action_emitted'):
                await obs.on_action_emitted(action)

    async def emit_alert(self, alert: SystemAlert):
        """
        Emits a system alert to the feed for reporting internal failures.
        """
        self._alerts.append(alert)
        print(f"[ActivityFeed] !!! {alert.severity} ALERT !!! {alert.message}")
        for obs in self._observers:
            if hasattr(obs, 'on_alert'):
                await obs.on_alert(alert)
        
    def get_recent_actions(self) -> List[AgentAction]:
        """
        Returns the recent actions stored in the feed buffer.
        """
        return self._recent_actions

    def get_alerts(self) -> List[SystemAlert]:
        return self._alerts

    async def request_identity_confirmation(self, req: IdentityConfirmationRequest):
        self._pending_identity_requests.append(req)
        print(f"[ActivityFeed] Identity Match: Does {req.secondary_id} belong to {req.primary_id}? (Confidence: {req.confidence})")

    def get_pending_identity_requests(self) -> List[IdentityConfirmationRequest]:
        return self._pending_identity_requests
        
    async def resolve_identity(self, request_id: str, confirmed: bool):
        req = next((r for r in self._pending_identity_requests if r.id == request_id), None)
        if not req:
            raise ValueError(f"Identity request {request_id} not found")
            
        self._pending_identity_requests.remove(req)
        
        for obs in self._observers:
            if hasattr(obs, 'on_identity_confirm'):
                await obs.on_identity_confirm(request_id, confirmed)

    async def receive_correction(self, correction: ExplicitCorrection):
        """
        Receives an explicit correction from the user interface and routes it
        back to the learning system via observers.
        """
        print(f"[ActivityFeed] Received correction for action {correction.action_id}: now {correction.corrected_decision}")
        for obs in self._observers:
            if hasattr(obs, 'on_correction'):
                await obs.on_correction(correction)

    async def undo(self, action_id: str):
        """
        Undoes an action if it is reversible.
        """
        action = next((a for a in self._recent_actions if a.id == action_id), None)
        if not action:
            raise ValueError(f"Action {action_id} not found in recent history")
            
        if not action.is_reversible:
            raise ValueError(f"Action {action_id} is not reversible")
            
        print(f"[ActivityFeed] Undoing action {action_id}")
        for obs in self._observers:
            if hasattr(obs, 'on_undo'):
                await obs.on_undo(action_id)

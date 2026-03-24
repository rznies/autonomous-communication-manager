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

class ActivityFeed:
    """
    Primary human-in-the-loop interface. Emits AgentAction records in real time
    and handles user corrections.
    """
    def __init__(
        self, 
        on_correction: Callable[[ExplicitCorrection], Awaitable[None]] = None,
        on_undo: Callable[[str], Awaitable[None]] = None,
        on_identity_confirm: Callable[[str, bool], Awaitable[None]] = None
    ):
        self._on_correction = on_correction
        self._on_undo = on_undo
        self._on_identity_confirm = on_identity_confirm
        self._recent_actions: List[AgentAction] = []
        self._pending_identity_requests: List[IdentityConfirmationRequest] = []
        
    async def emit(self, action: AgentAction):
        """
        Emits an action to the feed (e.g., terminal log) and stores it in recent history.
        """
        self._recent_actions.append(action)
        print(f"[ActivityFeed] Action {action.id}: decided {action.decision} for event {action.event_id}. Reason: {action.reason}")
        
    def get_recent_actions(self) -> List[AgentAction]:
        """
        Returns the recent actions stored in the feed buffer.
        """
        return self._recent_actions

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
        
        if self._on_identity_confirm:
            await self._on_identity_confirm(request_id, confirmed)

    async def receive_correction(self, correction: ExplicitCorrection):
        """
        Receives an explicit correction from the user interface and routes it
        back to the learning system via the callback.
        """
        print(f"[ActivityFeed] Received correction for action {correction.action_id}: now {correction.corrected_decision}")
        if self._on_correction:
            await self._on_correction(correction)

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
        if self._on_undo:
            await self._on_undo(action_id)

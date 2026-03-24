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

class ActivityFeed:
    """
    Primary human-in-the-loop interface. Emits AgentAction records in real time
    and handles user corrections.
    """
    def __init__(
        self, 
        on_correction: Callable[[ExplicitCorrection], Awaitable[None]] = None,
        on_undo: Callable[[str], Awaitable[None]] = None
    ):
        self._on_correction = on_correction
        self._on_undo = on_undo
        self._recent_actions: List[AgentAction] = []
        
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

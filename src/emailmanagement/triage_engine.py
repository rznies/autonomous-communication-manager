from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional
from emailmanagement.debounce import IncomingEvent
from emailmanagement.contact_graph import ContactNode

class TriageDecisionClass(Enum):
    ARCHIVE = auto()
    LOW = auto()
    NORMAL = auto()
    URGENT = auto()
    PROTECTED = auto()

@dataclass
class TriageDecision:
    decision_class: TriageDecisionClass
    reason: str
    confidence: float
class TriageEngine:
    def __init__(self):
        self._corrections = {}

    async def update_weights(self, contact_id: str, decision_class: TriageDecisionClass) -> None:
        self._corrections[contact_id] = decision_class

    async def triage(self, event: IncomingEvent, contact: Optional[ContactNode] = None) -> TriageDecision:
        # Rule 0: Explicit corrections override everything
        if event.contact_id in self._corrections:
            return TriageDecision(
                decision_class=self._corrections[event.contact_id],
                reason="User explicitly corrected interaction with this contact.",
                confidence=1.0
            )

        # Rule 1: Protected Contacts override all other signals
        if contact and contact.is_protected:
            return TriageDecision(
                decision_class=TriageDecisionClass.PROTECTED,
                reason="Contact is explicitly protected.",
                confidence=1.0
            )
            
        # Rule 2: Calendar Invites must not be archived
        content_type = event.headers.get("Content-Type", "").lower()
        if "text/calendar" in content_type:
            return TriageDecision(
                decision_class=TriageDecisionClass.NORMAL,
                reason="Heuristic: Detected calendar invite.",
                confidence=0.9
            )
            
        # Rule 3: High importance contacts are never archived
        is_high_importance = contact and contact.importance_score > 20.0
        
        # Heuristic 1: Mailing list headers
        if event.headers and "List-Unsubscribe" in event.headers:
            if not is_high_importance:
                return TriageDecision(
                    decision_class=TriageDecisionClass.ARCHIVE,
                    reason="Heuristic: Detected 'List-Unsubscribe' header, likely a mailing list.",
                    confidence=0.9
                )
            
        # Default decision
        return TriageDecision(
            decision_class=TriageDecisionClass.NORMAL,
            reason="Default rule applied.",
            confidence=0.5
        )

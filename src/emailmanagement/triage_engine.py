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
        if event.headers:
            if "List-Unsubscribe" in event.headers:
                if not is_high_importance:
                    return TriageDecision(
                        decision_class=TriageDecisionClass.ARCHIVE,
                        reason="Heuristic: Detected 'List-Unsubscribe' header, likely a mailing list.",
                        confidence=0.9
                    )
            
            precedence = event.headers.get("Precedence", "").lower()
            if precedence in ["bulk", "list"]:
                if not is_high_importance:
                    return TriageDecision(
                        decision_class=TriageDecisionClass.ARCHIVE,
                        reason=f"Heuristic: Detected Precedence: {precedence} header.",
                        confidence=0.9
                    )
        
        # Heuristic 2: No-reply / automated sender domains
        contact_lower = event.contact_id.lower()
        if contact_lower.startswith("no-reply@") or contact_lower.startswith("donotreply@") or contact_lower.startswith("noreply@"):
            if not is_high_importance:
                return TriageDecision(
                    decision_class=TriageDecisionClass.ARCHIVE,
                    reason="Heuristic: Detected automated/no-reply sender.",
                    confidence=0.9
                )
                
        system_prefixes = ["notifications@", "alerts@", "updates@", "mailer-daemon@", "postmaster@"]
        for prefix in system_prefixes:
            if contact_lower.startswith(prefix):
                if not is_high_importance:
                    return TriageDecision(
                        decision_class=TriageDecisionClass.ARCHIVE,
                        reason="Heuristic: Detected system notification sender.",
                        confidence=0.9
                    )
            
        # Default decision
        return TriageDecision(
            decision_class=TriageDecisionClass.NORMAL,
            reason="Default rule applied.",
            confidence=0.5
        )

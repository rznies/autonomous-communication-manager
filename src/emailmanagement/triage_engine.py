from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, List, Dict
from abc import ABC, abstractmethod
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

class TriageRule(ABC):
    @abstractmethod
    async def evaluate(self, event: IncomingEvent, contact: Optional[ContactNode] = None) -> Optional[TriageDecision]:
        pass

class ExplicitCorrectionRule(TriageRule):
    def __init__(self):
        self._corrections: Dict[str, TriageDecisionClass] = {}

    def update_weights(self, contact_id: str, decision_class: TriageDecisionClass) -> None:
        self._corrections[contact_id] = decision_class

    async def evaluate(self, event: IncomingEvent, contact: Optional[ContactNode] = None) -> Optional[TriageDecision]:
        if event.contact_id in self._corrections:
            return TriageDecision(
                decision_class=self._corrections[event.contact_id],
                reason="User explicitly corrected interaction with this contact.",
                confidence=1.0
            )
        return None

class ProtectedContactRule(TriageRule):
    async def evaluate(self, event: IncomingEvent, contact: Optional[ContactNode] = None) -> Optional[TriageDecision]:
        if contact and contact.is_protected:
            return TriageDecision(
                decision_class=TriageDecisionClass.PROTECTED,
                reason="Contact is explicitly protected.",
                confidence=1.0
            )
        return None

class CalendarInviteRule(TriageRule):
    async def evaluate(self, event: IncomingEvent, contact: Optional[ContactNode] = None) -> Optional[TriageDecision]:
        content_type = event.headers.get("Content-Type", "").lower() if event.headers else ""
        if "text/calendar" in content_type:
            return TriageDecision(
                decision_class=TriageDecisionClass.NORMAL,
                reason="Heuristic: Detected calendar invite.",
                confidence=0.9
            )
        return None

class DomainPriorRule(TriageRule):
    DOMAIN_PRIORS = {
        "stripe.com": TriageDecisionClass.LOW,
        "github.com": TriageDecisionClass.NORMAL,
        "linkedin.com": TriageDecisionClass.LOW,
        "notion.so": TriageDecisionClass.LOW,
        "a16z.com": TriageDecisionClass.URGENT,
        "ycombinator.com": TriageDecisionClass.URGENT,
    }

    async def evaluate(self, event: IncomingEvent, contact: Optional[ContactNode] = None) -> Optional[TriageDecision]:
        is_high_importance = contact and contact.importance_score > 20.0
        contact_lower = event.contact_id.lower()
        domain = contact_lower.split("@")[-1] if "@" in contact_lower else ""

        if domain in self.DOMAIN_PRIORS:
            prior_class = self.DOMAIN_PRIORS[domain]
            if is_high_importance and prior_class in [TriageDecisionClass.ARCHIVE, TriageDecisionClass.LOW]:
                prior_class = TriageDecisionClass.NORMAL
            return TriageDecision(
                decision_class=prior_class,
                reason=f"Prior: Known domain {domain}.",
                confidence=0.8
            )
        return None

class MailingListRule(TriageRule):
    async def evaluate(self, event: IncomingEvent, contact: Optional[ContactNode] = None) -> Optional[TriageDecision]:
        is_high_importance = contact and contact.importance_score > 20.0
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
        return None

class AutomatedSenderRule(TriageRule):
    async def evaluate(self, event: IncomingEvent, contact: Optional[ContactNode] = None) -> Optional[TriageDecision]:
        is_high_importance = contact and contact.importance_score > 20.0
        contact_lower = event.contact_id.lower()
        
        if contact_lower.startswith(("no-reply@", "donotreply@", "noreply@")):
            if not is_high_importance:
                return TriageDecision(
                    decision_class=TriageDecisionClass.ARCHIVE,
                    reason="Heuristic: Detected automated/no-reply sender.",
                    confidence=0.9
                )
                
        system_prefixes = ("notifications@", "alerts@", "updates@", "mailer-daemon@", "postmaster@")
        if contact_lower.startswith(system_prefixes):
            if not is_high_importance:
                return TriageDecision(
                    decision_class=TriageDecisionClass.ARCHIVE,
                    reason="Heuristic: Detected system notification sender.",
                    confidence=0.9
                )
        return None


class AgenticaTriageRule(TriageRule):
    def __init__(self, agent, scope: Optional[Dict] = None):
        self.agent = agent
        self.scope = scope or {}

    async def evaluate(self, event: IncomingEvent, contact: Optional[ContactNode] = None) -> Optional[TriageDecision]:
        contact_info = ""
        if contact:
            contact_info = f"Contact relationship: {contact.relationship_class.name}, importance: {contact.importance_score}"

        prompt = f"""
        Classify the following email into a triage decision.
        Email content: {event.content}
        Sender: {event.contact_id}
        {contact_info}

        Return a TriageDecision with an appropriate decision_class from: ARCHIVE, LOW, NORMAL, URGENT.
        Include a brief reason and a confidence score between 0 and 1.
        """

        try:
            return await self.agent.call(TriageDecision, prompt)
        except Exception:
            return None

from emailmanagement.persistence import SqliteStore


def create_readonly_triage_scope(graph) -> dict:
    """Build a dict of read-only wrapper functions over a ContactGraph.

    These wrappers are injected into the Agentica agent's scope so the LLM
    can query contact context without ever mutating the graph.
    """

    def get_contact_interaction_count(contact_id: str) -> int:
        contact = graph._nodes.get(contact_id)
        return contact.interaction_count if contact else 0

    def get_contact_relationship_class(contact_id: str) -> str:
        contact = graph._nodes.get(contact_id)
        return contact.relationship_class.name if contact else "UNKNOWN"

    return {
        "get_contact_interaction_count": get_contact_interaction_count,
        "get_contact_relationship_class": get_contact_relationship_class,
    }

class TriageEngine:
    def __init__(self, rules: Optional[List[TriageRule]] = None, store: Optional[SqliteStore] = None):
        self.store = store
        self._correction_rule = ExplicitCorrectionRule()
        if rules is None:
            self.rules = [
                self._correction_rule,
                ProtectedContactRule(),
                CalendarInviteRule(),
                DomainPriorRule(),
                MailingListRule(),
                AutomatedSenderRule()
            ]
        else:
            self.rules = rules
            self._correction_rule = next((r for r in self.rules if isinstance(r, ExplicitCorrectionRule)), None)
        
        if self.store and self._correction_rule:
            stored_corrections = self.store.load_all_corrections()
            for contact_id, decision_name in stored_corrections.items():
                try:
                    decision_class = TriageDecisionClass[decision_name]
                    self._correction_rule.update_weights(contact_id, decision_class)
                except KeyError:
                    pass

    async def update_weights(self, contact_id: str, decision_class: TriageDecisionClass) -> None:
        if self._correction_rule:
            self._correction_rule.update_weights(contact_id, decision_class)
            if self.store:
                self.store.save_correction(contact_id, decision_class.name)

    async def triage(self, event: IncomingEvent, contact: Optional[ContactNode] = None) -> TriageDecision:
        for rule in self.rules:
            decision = await rule.evaluate(event, contact)
            if decision:
                return decision
                
        return TriageDecision(
            decision_class=TriageDecisionClass.NORMAL,
            reason="Default rule applied.",
            confidence=0.5
        )

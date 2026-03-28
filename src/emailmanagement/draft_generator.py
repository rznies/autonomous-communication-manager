from dataclasses import dataclass
from emailmanagement.debounce import IncomingEvent
from emailmanagement.contact_graph import ContactNode

@dataclass
class DraftReply:
    content: str
    confidence: float

class DraftGenerator:
    def __init__(self, agent):
        self.agent = agent

    async def generate_draft(self, event: IncomingEvent, contact: ContactNode, thread_history: str = "") -> DraftReply:
        prompt = f"""
        Draft a reply to the following message.
        Sender Relationship: {contact.relationship_class.name}
        Original Message: {event.content}
        Thread History: {thread_history}
        """

        try:
            return await self.agent.call(DraftReply, prompt)
        except Exception:
            return DraftReply(content="", confidence=0.0)

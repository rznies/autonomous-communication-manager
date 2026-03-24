from dataclasses import dataclass
from emailmanagement.debounce import IncomingEvent
from emailmanagement.contact_graph import ContactNode

@dataclass
class DraftReply:
    content: str
    confidence: float

class DraftGenerator:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    async def generate_draft(self, event: IncomingEvent, contact: ContactNode, thread_history: str = "") -> DraftReply:
        prompt = f"""
        Draft a reply to the following message.
        Sender Relationship: {contact.relationship_class.name}
        Original Message: {event.content}
        Thread History: {thread_history}
        """
        
        response = await self.llm_client.generate(prompt)
        
        # In a real system, we'd have the LLM return structured output with confidence.
        # For this prototype, we'll assign a static high confidence.
        return DraftReply(
            content=response.strip(),
            confidence=0.85
        )

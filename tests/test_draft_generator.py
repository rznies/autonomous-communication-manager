import pytest
from emailmanagement.draft_generator import DraftGenerator, DraftReply
from emailmanagement.debounce import IncomingEvent
from emailmanagement.contact_graph import ContactNode, RelationshipClass

class DummyLLM:
    async def generate(self, prompt: str) -> str:
        if "FREQUENT" in prompt:
            return "Hey! Sounds good, let's do it."
        return "Thank you for your email. I will review it."

@pytest.mark.asyncio
async def test_draft_generator_adapts_tone():
    generator = DraftGenerator(llm_client=DummyLLM())
    
    event = IncomingEvent(
        id="evt_1",
        contact_id="friend@example.com",
        content="Want to grab coffee?",
        timestamp=0.0,
        headers={}
    )
    
    contact = ContactNode(id="friend@example.com", relationship_class=RelationshipClass.FREQUENT)
    
    draft = await generator.generate_draft(event, contact)
    
    assert isinstance(draft, DraftReply)
    assert "Hey! Sounds good" in draft.content
    assert draft.confidence > 0.0

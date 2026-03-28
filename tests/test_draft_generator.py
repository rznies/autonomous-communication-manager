import pytest
from emailmanagement.draft_generator import DraftGenerator, DraftReply
from emailmanagement.debounce import IncomingEvent
from emailmanagement.contact_graph import ContactNode, RelationshipClass


class MockAgent:
    """Stands in for an agentica Agent with a call() method."""
    async def call(self, output_type, prompt, **kwargs):
        return output_type(
            content="Thank you for your message. I'll get back to you shortly.",
            confidence=0.92,
        )


class ToneMockAgent:
    """Mock agent that adapts response based on relationship in prompt."""
    async def call(self, output_type, prompt, **kwargs):
        if "FREQUENT" in prompt:
            return output_type(content="Hey! Sounds good, let's do it.", confidence=0.9)
        return output_type(content="Thank you for your email. I will review it.", confidence=0.85)


@pytest.mark.asyncio
async def test_draft_generator_returns_typed_reply_via_agent():
    """agent.call(DraftReply, prompt) should produce a strictly-typed DraftReply."""
    generator = DraftGenerator(agent=MockAgent())

    event = IncomingEvent(
        id="evt_1",
        contact_id="colleague@example.com",
        content="Can we sync on the roadmap?",
        timestamp=0.0,
        headers={},
    )
    contact = ContactNode(id="colleague@example.com")

    draft = await generator.generate_draft(event, contact)

    assert isinstance(draft, DraftReply)
    assert len(draft.content) > 0
    assert 0.0 < draft.confidence <= 1.0


@pytest.mark.asyncio
async def test_draft_generator_adapts_tone():
    generator = DraftGenerator(agent=ToneMockAgent())

    event = IncomingEvent(
        id="evt_1",
        contact_id="friend@example.com",
        content="Want to grab coffee?",
        timestamp=0.0,
        headers={},
    )

    contact = ContactNode(id="friend@example.com", relationship_class=RelationshipClass.FREQUENT)

    draft = await generator.generate_draft(event, contact)

    assert isinstance(draft, DraftReply)
    assert "Hey! Sounds good" in draft.content
    assert draft.confidence > 0.0


class FailingAgent:
    """Agent that always raises to simulate LLM timeout/failure."""
    async def call(self, output_type, prompt, **kwargs):
        raise RuntimeError("LLM request timed out")


@pytest.mark.asyncio
async def test_draft_generator_handles_agent_failure_gracefully():
    """If the agent fails, generate_draft should return a fallback DraftReply with low confidence."""
    generator = DraftGenerator(agent=FailingAgent())

    event = IncomingEvent(
        id="evt_fail",
        contact_id="someone@example.com",
        content="Hello?",
        timestamp=0.0,
        headers={},
    )
    contact = ContactNode(id="someone@example.com")

    draft = await generator.generate_draft(event, contact)

    assert isinstance(draft, DraftReply)
    assert draft.confidence == 0.0

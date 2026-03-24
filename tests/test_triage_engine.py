import pytest
from emailmanagement.triage_engine import TriageEngine, TriageDecisionClass
from emailmanagement.contact_graph import ContactNode
from emailmanagement.debounce import IncomingEvent

@pytest.mark.asyncio
async def test_triage_engine_detects_mailing_list():
    engine = TriageEngine()
    
    # Simulate a mailing list event
    event = IncomingEvent(
        id="msg_1",
        contact_id="newsletter@example.com",
        content="Weekly Newsletter content here...",
        timestamp=0.0
    )
    # Give it headers to simulate mailing list
    event.headers = {"List-Unsubscribe": "<mailto:unsub@example.com>"}
    
    # We pass it to the engine, perhaps with an empty contact
    decision = await engine.triage(event, contact=None)
    
    assert decision.decision_class in [TriageDecisionClass.ARCHIVE, TriageDecisionClass.LOW]
    assert "heuristic" in decision.reason.lower() or "list" in decision.reason.lower()

@pytest.mark.asyncio
async def test_triage_engine_detects_calendar_invite():
    engine = TriageEngine()
    
    event = IncomingEvent(
        id="inv_1",
        contact_id="colleague@example.com",
        content="Meeting invitation...",
        timestamp=0.0,
        headers={"Content-Type": "text/calendar; method=REQUEST"}
    )
    
    decision = await engine.triage(event, contact=None)
    
    assert decision.decision_class != TriageDecisionClass.ARCHIVE
    assert "calendar" in decision.reason.lower()

@pytest.mark.asyncio
async def test_triage_engine_respects_protected_contact():
    engine = TriageEngine()
    
    event = IncomingEvent(
        id="msg_2",
        contact_id="vip@example.com",
        content="Hello",
        timestamp=0.0,
        headers={"List-Unsubscribe": "<mailto:unsub@example.com>"} # Usually triggers archive
    )
    
    contact = ContactNode(id="vip@example.com")
    contact.is_protected = True
    
    decision = await engine.triage(event, contact=contact)
    
    assert decision.decision_class == TriageDecisionClass.PROTECTED

@pytest.mark.asyncio
async def test_triage_engine_high_importance_never_archives():
    engine = TriageEngine()
    
    event = IncomingEvent(
        id="msg_3",
        contact_id="ceo@example.com",
        content="Read this now",
        timestamp=0.0,
        headers={"List-Unsubscribe": "<mailto:unsub@example.com>"} 
    )
    
    contact = ContactNode(id="ceo@example.com")
    contact.base_importance_score = 50.0 # High threshold
    
    decision = await engine.triage(event, contact=contact)
    
    assert decision.decision_class not in [TriageDecisionClass.ARCHIVE, TriageDecisionClass.LOW]

@pytest.mark.asyncio
async def test_triage_engine_learns_from_correction():
    engine = TriageEngine()
    
    event = IncomingEvent(
        id="msg_4",
        contact_id="sales@example.com",
        content="Buy our product",
        timestamp=0.0,
        headers={}
    )
    
    decision1 = await engine.triage(event, contact=None)
    assert decision1.decision_class == TriageDecisionClass.NORMAL
    
    # Provide explicit correction
    await engine.update_weights("sales@example.com", TriageDecisionClass.ARCHIVE)
    
    decision2 = await engine.triage(event, contact=None)
    assert decision2.decision_class == TriageDecisionClass.ARCHIVE

@pytest.mark.asyncio
async def test_triage_engine_detects_noreply_domain():
    engine = TriageEngine()
    
    event = IncomingEvent(
        id="msg_noreply",
        contact_id="no-reply@company.com",
        content="System update",
        timestamp=0.0,
        headers={"source": "gmail"}
    )
    
    decision = await engine.triage(event, contact=None)
    
    assert decision.decision_class in [TriageDecisionClass.ARCHIVE, TriageDecisionClass.LOW]
    assert "no-reply" in decision.reason.lower() or "automated" in decision.reason.lower()

@pytest.mark.asyncio
async def test_triage_engine_detects_bulk_precedence():
    engine = TriageEngine()
    
    event = IncomingEvent(
        id="msg_bulk",
        contact_id="marketing@startup.com",
        content="Buy now",
        timestamp=0.0,
        headers={"Precedence": "bulk"}
    )
    
    decision = await engine.triage(event, contact=None)
    
    assert decision.decision_class in [TriageDecisionClass.ARCHIVE, TriageDecisionClass.LOW]
    assert "bulk" in decision.reason.lower() or "list" in decision.reason.lower()

@pytest.mark.asyncio
@pytest.mark.parametrize("domain_prefix", ["notifications@", "alerts@", "updates@", "mailer-daemon@", "postmaster@"])
async def test_triage_engine_detects_system_notifications(domain_prefix):
    engine = TriageEngine()
    
    event = IncomingEvent(
        id=f"msg_{domain_prefix}",
        contact_id=f"{domain_prefix}example.com",
        content="System alert",
        timestamp=0.0,
        headers={}
    )
    
    decision = await engine.triage(event, contact=None)
    
    assert decision.decision_class in [TriageDecisionClass.ARCHIVE, TriageDecisionClass.LOW]
    assert "automated" in decision.reason.lower() or "system" in decision.reason.lower()

import os
import pytest
from datetime import datetime
from emailmanagement.persistence import SqliteStore
from emailmanagement.contact_graph import ContactGraph, InteractionType, RelationshipClass
from emailmanagement.triage_engine import TriageEngine, TriageDecisionClass
from emailmanagement.debounce import IncomingEvent

@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_agent_state.db"
    return str(db_file)

@pytest.mark.asyncio
async def test_contact_persistence(temp_db):
    store = SqliteStore(temp_db)
    graph = ContactGraph(store)
    
    contact_id = "test@example.com"
    await graph.record_interaction(contact_id, InteractionType.EMAIL_RECEIVED)
    await graph.set_relationship_class(contact_id, RelationshipClass.FREQUENT)
    
    # Simulate restart by creating new objects with same DB
    store2 = SqliteStore(temp_db)
    graph2 = ContactGraph(store2)
    
    contact = await graph2.get_contact(contact_id)
    assert contact is not None
    assert contact.interaction_count == 1
    assert contact.relationship_class == RelationshipClass.FREQUENT
    assert contact.base_importance_score > 1.0

@pytest.mark.asyncio
async def test_triage_correction_persistence(temp_db):
    store = SqliteStore(temp_db)
    engine = TriageEngine(store=store)
    
    contact_id = "newsletter@spam.com"
    await engine.update_weights(contact_id, TriageDecisionClass.ARCHIVE)
    
    # Simulate restart
    store2 = SqliteStore(temp_db)
    engine2 = TriageEngine(store=store2)
    
    event = IncomingEvent(
        id="msg1",
        contact_id=contact_id,
        content="Buy now",
        timestamp=datetime.now().timestamp()
    )
    
    decision = await engine2.triage(event)
    assert decision.decision_class == TriageDecisionClass.ARCHIVE
    assert "explicitly corrected" in decision.reason.lower()

@pytest.mark.asyncio
async def test_action_log_persistence(temp_db):
    store = SqliteStore(temp_db)
    action_id = "act_123"
    store.log_action(action_id, "msg_456", "ARCHIVE", "SUCCESS")
    
    # Simulate restart
    store2 = SqliteStore(temp_db)
    status = store2.get_action_status(action_id)
    assert status == "SUCCESS"

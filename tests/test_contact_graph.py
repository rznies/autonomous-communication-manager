import pytest
from datetime import datetime, timedelta
from emailmanagement.contact_graph import ContactGraph, InteractionType

@pytest.mark.asyncio
async def test_contact_graph_record_and_retrieve():
    graph = ContactGraph()
    
    await graph.record_interaction(
        contact_id="user_1", 
        interaction_type=InteractionType.EMAIL_RECEIVED
    )
    
    contact = await graph.get_contact("user_1")
    
    assert contact is not None
    assert contact.id == "user_1"
    assert contact.interaction_count == 1

@pytest.mark.asyncio
async def test_contact_importance_score_decreases_over_time():
    graph = ContactGraph()
    base_time = datetime(2026, 1, 1, 12, 0)
    
    await graph.record_interaction(
        contact_id="user_1",
        interaction_type=InteractionType.EMAIL_RECEIVED,
        timestamp=base_time
    )
    
    contact_t0 = await graph.get_contact("user_1", current_time=base_time)
    score_t0 = contact_t0.importance_score
    
    later_time = base_time + timedelta(days=10)
    contact_later = await graph.get_contact("user_1", current_time=later_time)
    score_later = contact_later.importance_score
    
    assert score_later < score_t0

@pytest.mark.asyncio
async def test_frequent_collaborator_decays_slower_than_transactional():
    from emailmanagement.contact_graph import RelationshipClass
    graph = ContactGraph()
    base_time = datetime(2026, 1, 1, 12, 0)
    
    await graph.record_interaction("freq_user", InteractionType.EMAIL_RECEIVED, timestamp=base_time)
    await graph.record_interaction("trans_user", InteractionType.EMAIL_RECEIVED, timestamp=base_time)
    
    # Set relationship classes
    await graph.set_relationship_class("freq_user", RelationshipClass.FREQUENT)
    await graph.set_relationship_class("trans_user", RelationshipClass.TRANSACTIONAL)
    
    freq_t0 = await graph.get_contact("freq_user", current_time=base_time)
    trans_t0 = await graph.get_contact("trans_user", current_time=base_time)
    assert freq_t0.importance_score == trans_t0.importance_score  # both should be 2.0
    
    later_time = base_time + timedelta(days=10)
    freq_later = await graph.get_contact("freq_user", current_time=later_time)
    trans_later = await graph.get_contact("trans_user", current_time=later_time)
    
    assert freq_later.importance_score > trans_later.importance_score

@pytest.mark.asyncio
async def test_verified_identity_link_merges_contacts():
    graph = ContactGraph()
    await graph.record_interaction("email_id", InteractionType.EMAIL_RECEIVED)
    await graph.record_interaction("slack_id", InteractionType.EMAIL_RECEIVED)
    
    await graph.link_identities("email_id", "slack_id", verified=True)
    
    c_email = await graph.get_contact("email_id")
    c_slack = await graph.get_contact("slack_id")
    
    assert c_email is not None
    assert c_slack is not None
    assert c_email.id == c_slack.id
    assert c_email.interaction_count == 2
    assert c_slack.interaction_count == 2

@pytest.mark.asyncio
async def test_unverified_identity_link_does_not_merge():
    graph = ContactGraph()
    await graph.record_interaction("email_id_2", InteractionType.EMAIL_RECEIVED)
    await graph.record_interaction("slack_id_2", InteractionType.EMAIL_RECEIVED)
    
    await graph.link_identities("email_id_2", "slack_id_2", verified=False)
    
    c_email = await graph.get_contact("email_id_2")
    c_slack = await graph.get_contact("slack_id_2")
    
    assert c_email.id != c_slack.id
    assert c_email.interaction_count == 1

@pytest.mark.asyncio
async def test_get_all_contact_ids_returns_recorded_ids():
    """get_all_contact_ids() is the public accessor that replaces _nodes.keys() access."""
    graph = ContactGraph()
    await graph.record_interaction("alice@corp.com", InteractionType.EMAIL_RECEIVED)
    await graph.record_interaction("bob_slack", InteractionType.EMAIL_RECEIVED)

    ids = graph.get_all_contact_ids()

    assert "alice@corp.com" in ids
    assert "bob_slack" in ids
    assert len(ids) == 2

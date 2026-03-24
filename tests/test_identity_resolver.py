import pytest
from emailmanagement.identity_resolver import IdentityResolver
from emailmanagement.contact_graph import ContactGraph, InteractionType
from emailmanagement.activity_feed import ActivityFeed


@pytest.mark.asyncio
async def test_identity_resolver_detects_local_part_match():
    """
    When a new contact arrives whose email local-part matches an existing contact,
    IdentityResolver should emit an IdentityConfirmationRequest to the feed.
    """
    graph = ContactGraph()
    feed = ActivityFeed()

    # Seed the graph with an existing email contact
    await graph.record_interaction("john.doe@company.com", InteractionType.EMAIL_RECEIVED)

    resolver = IdentityResolver(graph=graph, feed=feed)
    await resolver.check_and_request("john.doe_slack")

    pending = feed.get_pending_identity_requests()
    assert len(pending) == 1
    assert "john.doe@company.com" in (pending[0].primary_id, pending[0].secondary_id)
    assert "john.doe_slack" in (pending[0].primary_id, pending[0].secondary_id)


@pytest.mark.asyncio
async def test_identity_resolver_no_match_emits_nothing():
    """No pending requests if no local-part collision."""
    graph = ContactGraph()
    feed = ActivityFeed()

    await graph.record_interaction("alice@company.com", InteractionType.EMAIL_RECEIVED)

    resolver = IdentityResolver(graph=graph, feed=feed)
    await resolver.check_and_request("bob_slack")

    assert len(feed.get_pending_identity_requests()) == 0


@pytest.mark.asyncio
async def test_identity_resolver_confirm_true_links_graph():
    """
    After a match is detected and confirm() is called with confirmed=True,
    graph.link_identities should be called with verified=True.
    """
    graph = ContactGraph()
    feed = ActivityFeed()

    await graph.record_interaction("john.doe@company.com", InteractionType.EMAIL_RECEIVED)

    resolver = IdentityResolver(graph=graph, feed=feed)
    await resolver.check_and_request("john.doe_slack")

    reqs = feed.get_pending_identity_requests()
    assert len(reqs) == 1

    await resolver.confirm(reqs[0].id, confirmed=True)

    # After a confirmed link, both IDs should resolve to the same node
    c_email = await graph.get_contact("john.doe@company.com")
    c_slack = await graph.get_contact("john.doe_slack")
    assert c_email is not None
    assert c_slack is not None
    assert c_email.id == c_slack.id


@pytest.mark.asyncio
async def test_identity_resolver_confirm_false_does_not_merge():
    """Rejected confirmation does not merge contacts in graph."""
    graph = ContactGraph()
    feed = ActivityFeed()

    await graph.record_interaction("jane.doe@company.com", InteractionType.EMAIL_RECEIVED)
    await graph.record_interaction("jane.doe_slack", InteractionType.EMAIL_RECEIVED)

    resolver = IdentityResolver(graph=graph, feed=feed)
    await resolver.check_and_request("jane.doe_slack")

    reqs = feed.get_pending_identity_requests()
    assert len(reqs) == 1

    await resolver.confirm(reqs[0].id, confirmed=False)

    c_email = await graph.get_contact("jane.doe@company.com")
    c_slack = await graph.get_contact("jane.doe_slack")
    assert c_email.id != c_slack.id

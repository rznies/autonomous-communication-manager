import uuid
from emailmanagement.contact_graph import ContactGraph
from emailmanagement.activity_feed import ActivityFeed, IdentityConfirmationRequest


class IdentityResolver:
    """
    Owns identity matching heuristics and pending-link state.
    Extracted from AgentLoop to make it a single-responsibility module.

    Responsibilities:
      - Detect when a new contact_id is a likely alias of an existing contact
      - Emit IdentityConfirmationRequest to ActivityFeed for human review
      - On confirmation, call graph.link_identities() to merge nodes

    Hidden complexity: local-part matching heuristics, pending-link state management.
    Public interface: check_and_request(), confirm()
    """

    def __init__(self, graph: ContactGraph, feed: ActivityFeed):
        self._graph = graph
        self._feed = feed
        # Maps request_id -> (id1, id2) for pending confirmations
        self._pending_links: dict[str, tuple[str, str]] = {}

    async def check_and_request(self, new_contact_id: str) -> None:
        """
        Run identity heuristics against all known contacts. If a potential alias
        is found, emit an IdentityConfirmationRequest to the feed.
        Only generates one request per call (first match found).
        """
        new_local = _normalize_local(new_contact_id)

        for existing_id in self._graph.get_all_contact_ids():
            if existing_id == new_contact_id:
                continue

            existing_local = _normalize_local(existing_id)
            if new_local == existing_local:
                req_id = str(uuid.uuid4())
                self._pending_links[req_id] = (existing_id, new_contact_id)
                req = IdentityConfirmationRequest(
                    id=req_id,
                    primary_id=existing_id,
                    secondary_id=new_contact_id,
                    confidence=0.8,
                )
                await self._feed.request_identity_confirmation(req)
                return  # Only one request per new contact

    async def confirm(self, request_id: str, confirmed: bool) -> None:
        """
        Called when the user has responded to an identity confirmation request.
        Delegates the merge decision to the ContactGraph.
        """
        if request_id not in self._pending_links:
            return  # Already resolved or unknown

        id1, id2 = self._pending_links.pop(request_id)
        await self._graph.link_identities(id1, id2, verified=confirmed)


def _normalize_local(contact_id: str) -> str:
    """Extract and normalize the local part of a contact_id for heuristic matching."""
    local = contact_id.split("@")[0]
    # Strip common platform suffixes
    for suffix in ("_slack", "_teams", "_discord"):
        if local.endswith(suffix):
            local = local[: -len(suffix)]
    return local.lower()

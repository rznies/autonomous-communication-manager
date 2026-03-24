import math
from datetime import datetime
from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Optional

class InteractionType(Enum):
    EMAIL_RECEIVED = auto()
    EMAIL_SENT = auto()

class RelationshipClass(Enum):
    FREQUENT = auto()
    PERIODIC = auto()
    TRANSACTIONAL = auto()
    AUTOMATED = auto()

LAMBDAS = {
    RelationshipClass.FREQUENT: 0.005,
    RelationshipClass.PERIODIC: 0.02,
    RelationshipClass.TRANSACTIONAL: 0.05,
    RelationshipClass.AUTOMATED: 0.1
}

@dataclass
class ContactNode:
    id: str
    interaction_count: int = 0
    base_importance_score: float = 1.0
    relationship_class: RelationshipClass = RelationshipClass.PERIODIC
    last_interaction: Optional[datetime] = None
    is_protected: bool = False

    @property
    def importance_score(self) -> float:
        # This property returns base score if not dynamically calculated
        return self.base_importance_score

from emailmanagement.persistence import SqliteStore

class ContactGraph:
    def __init__(self, store: Optional[SqliteStore] = None):
        # In-memory storage for Phase 1 prototype, synced with persistence if provided
        self.store = store
        self._nodes: Dict[str, ContactNode] = {}
        
        if self.store:
            stored_contacts = self.store.load_all_contacts()
            for contact_id, data in stored_contacts.items():
                self._nodes[contact_id] = ContactNode(
                    id=data["id"],
                    interaction_count=data["interaction_count"],
                    base_importance_score=data["base_score"],
                    relationship_class=RelationshipClass[data["relationship_class"]],
                    last_interaction=data["last_interaction"],
                    is_protected=data["is_protected"]
                )
        
    async def record_interaction(self, contact_id: str, interaction_type: InteractionType, timestamp: Optional[datetime] = None) -> None:
        if timestamp is None:
            timestamp = datetime.now()
            
        if contact_id not in self._nodes:
            self._nodes[contact_id] = ContactNode(id=contact_id)
            
        contact = self._nodes[contact_id]
        contact.interaction_count += 1
        contact.last_interaction = timestamp
        # Interaction bumps base score
        contact.base_importance_score += 1.0
        
        if self.store:
            self.store.save_contact(contact_id, {
                "interaction_count": contact.interaction_count,
                "base_score": contact.base_importance_score,
                "relationship_class": contact.relationship_class.name,
                "last_interaction": contact.last_interaction,
                "is_protected": contact.is_protected
            })
        
    async def get_contact(self, contact_id: str, current_time: Optional[datetime] = None) -> Optional[ContactNode]:
        if contact_id not in self._nodes:
            return None
            
        contact = self._nodes[contact_id]
        
        # Calculate decayed score
        if current_time is None:
            current_time = datetime.now()
            
        if contact.last_interaction and current_time > contact.last_interaction:
            days_elapsed = (current_time - contact.last_interaction).total_seconds() / 86400.0
            lambda_val = LAMBDAS[contact.relationship_class]
            # Exponential decay
            decayed_score = contact.base_importance_score * math.exp(-lambda_val * days_elapsed)
            
            # Create a dynamic copy to return so we don't mutate base store on reads
            dynamic_contact = ContactNode(
                id=contact.id,
                interaction_count=contact.interaction_count,
                base_importance_score=decayed_score,
                relationship_class=contact.relationship_class,
                last_interaction=contact.last_interaction,
                is_protected=contact.is_protected
            )
            return dynamic_contact
            
        return contact

    async def set_relationship_class(self, contact_id: str, relationship_class: RelationshipClass) -> None:
        if contact_id not in self._nodes:
            self._nodes[contact_id] = ContactNode(id=contact_id)
        
        contact = self._nodes[contact_id]
        contact.relationship_class = relationship_class

        if self.store:
            self.store.save_contact(contact_id, {
                "interaction_count": contact.interaction_count,
                "base_score": contact.base_importance_score,
                "relationship_class": contact.relationship_class.name,
                "last_interaction": contact.last_interaction,
                "is_protected": contact.is_protected
            })

    def get_all_contact_ids(self) -> list:
        """Public accessor for all known contact IDs. Replaces external _nodes.keys() access."""
        return list(self._nodes.keys())

    async def link_identities(self, id1: str, id2: str, verified: bool) -> None:
        if not verified:
            # Unverified links don't merge nodes yet.
            return
            
        # Ensure both nodes exist
        if id1 not in self._nodes:
            self._nodes[id1] = ContactNode(id=id1)
        if id2 not in self._nodes:
            self._nodes[id2] = ContactNode(id=id2)
            
        primary = self._nodes[id1]
        secondary = self._nodes[id2]
        
        if primary is secondary:
            return
            
        # Merge secondary into primary
        primary.interaction_count += secondary.interaction_count
        primary.base_importance_score = max(primary.base_importance_score, secondary.base_importance_score)
        
        if secondary.last_interaction:
            if primary.last_interaction is None or secondary.last_interaction > primary.last_interaction:
                primary.last_interaction = secondary.last_interaction
                
        # Update references for secondary and any of its aliases
        for node_id, node in list(self._nodes.items()):
            if node is secondary:
                self._nodes[node_id] = primary
                if self.store:
                    # Sync the change in primary for node_id
                    self.store.save_contact(node_id, {
                        "interaction_count": primary.interaction_count,
                        "base_score": primary.base_importance_score,
                        "relationship_class": primary.relationship_class.name,
                        "last_interaction": primary.last_interaction,
                        "is_protected": primary.is_protected
                    })

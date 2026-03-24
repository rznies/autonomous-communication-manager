import uuid
from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional

class ActionType(Enum):
    ARCHIVE = auto()
    SEND = auto()
    LABEL = auto()

@dataclass
class ExecutionRequest:
    action_type: ActionType
    message_id: str = ""
    to: str = ""
    content: str = ""
    dry_run: bool = True

@dataclass
class UndoRecord:
    action_type: ActionType
    item_id: str

@dataclass
class ExecutionResult:
    success: bool
    was_dry_run: bool
    action_id: str = ""
    is_reversible: bool = False
    undo_record: Any = None

from emailmanagement.persistence import SqliteStore

class ActionExecutor:
    def __init__(self, platform_client: Any = None, has_write_scope: bool = False, store: Optional[SqliteStore] = None):
        self.platform_client = platform_client
        self.has_write_scope = has_write_scope
        self.store = store
        
    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        if not self.has_write_scope and not request.dry_run:
            raise PermissionError("Cannot execute live action without write scope.")
            
        if request.dry_run:
            return ExecutionResult(success=True, was_dry_run=True, action_id="dry-run-id")

        # Check for idempotency if store is available
        if self.store and request.message_id:
            status = self.store.get_message_action_status(request.message_id, request.action_type.name)
            if status == "SUCCESS":
                return ExecutionResult(success=True, was_dry_run=False, action_id="already-executed")
            
        action_id = str(uuid.uuid4())
            
        if request.action_type == ActionType.ARCHIVE:
            if self.platform_client:
                await self.platform_client.archive_message(request.message_id)
            
            if self.store:
                self.store.log_action(action_id, request.message_id, "ARCHIVE", "SUCCESS")
                
            return ExecutionResult(
                success=True, 
                was_dry_run=False, 
                action_id=action_id,
                is_reversible=True,
                undo_record=UndoRecord(action_type=ActionType.ARCHIVE, item_id=request.message_id)
            )
        elif request.action_type == ActionType.SEND:
            if self.platform_client:
                await self.platform_client.send_message(request.to, request.content)
            
            if self.store:
                self.store.log_action(action_id, request.message_id, "SEND", "SUCCESS")
                
            return ExecutionResult(
                success=True, 
                was_dry_run=False, 
                action_id=action_id,
                is_reversible=False,
                undo_record=None
            )
                
        return ExecutionResult(success=True, was_dry_run=False, action_id=action_id)

import pytest
from unittest.mock import AsyncMock
from emailmanagement.action_executor import ActionExecutor, ActionType, ExecutionRequest

class DummyPlatformClient:
    def __init__(self):
        self.mutations = []
        
    async def archive_message(self, message_id: str):
        self.mutations.append(("archive", message_id))
        
    async def send_message(self, to: str, content: str):
        self.mutations.append(("send", to, content))

from emailmanagement.persistence import SqliteStore

@pytest.mark.asyncio
async def test_action_executor_idempotency(tmp_path):
    db_file = str(tmp_path / "test_idempotency.db")
    store = SqliteStore(db_file)
    
    mock_platform = AsyncMock()
    executor = ActionExecutor(platform_client=mock_platform, has_write_scope=True, store=store)
    
    request = ExecutionRequest(
        action_type=ActionType.ARCHIVE,
        message_id="msg_repeat",
        dry_run=False
    )
    
    # First execution
    result1 = await executor.execute(request)
    assert result1.success is True
    assert result1.action_id != "already-executed"
    assert mock_platform.archive_message.call_count == 1
    
    # Second execution (should be skipped)
    result2 = await executor.execute(request)
    assert result2.success is True
    assert result2.action_id == "already-executed"
    assert mock_platform.archive_message.call_count == 1  # Still 1
    # Arrange
    platform_client = DummyPlatformClient()
    executor = ActionExecutor(platform_client=platform_client)
    
    request = ExecutionRequest(
        action_type=ActionType.ARCHIVE,
        message_id="msg_1",
        dry_run=True  # Ensure dry run is respected
    )
    
    # Act
    result = await executor.execute(request)
    
    # Assert
    assert result.success is True
    assert result.was_dry_run is True
    assert len(platform_client.mutations) == 0  # No mutations happened

@pytest.mark.asyncio
async def test_action_executor_undo_record_for_archive():
    platform_client = DummyPlatformClient()
    executor = ActionExecutor(platform_client=platform_client, has_write_scope=True)
    
    request = ExecutionRequest(
        action_type=ActionType.ARCHIVE,
        message_id="msg_2",
        dry_run=False
    )
    
    result = await executor.execute(request)
    
    assert result.success is True
    assert result.is_reversible is True
    assert result.undo_record is not None

@pytest.mark.asyncio
async def test_action_executor_send_is_irreversible():
    platform_client = DummyPlatformClient()
    executor = ActionExecutor(platform_client=platform_client, has_write_scope=True)
    
    request = ExecutionRequest(
        action_type=ActionType.SEND,
        to="person@example.com",
        content="Hello",
        dry_run=False
    )
    
    result = await executor.execute(request)
    
    assert result.success is True
    assert result.is_reversible is False
    assert result.undo_record is None

@pytest.mark.asyncio
async def test_action_executor_fails_without_write_scope():
    platform_client = DummyPlatformClient()
    executor = ActionExecutor(platform_client=platform_client, has_write_scope=False)
    
    request = ExecutionRequest(
        action_type=ActionType.ARCHIVE,
        message_id="msg_3",
        dry_run=False
    )
    
    with pytest.raises(PermissionError, match="write scope"):
        await executor.execute(request)

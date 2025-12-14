import pytest
from unittest.mock import MagicMock, AsyncMock
import src.app as app

@pytest.mark.asyncio
async def test_app_start(mock_cl_fixture):
    """
    [REQ-FUN-001] Test session start.
    Should set graph and thread_id in user_session.
    """
    mock_cl, mock_user_session = mock_cl_fixture
    
    await app.start()
    
    # Check if graph and thread_id are set in session
    assert mock_user_session.set.call_count >= 2
    mock_user_session.set.assert_any_call("graph", app.app_graph)
    # Check thread_id set (value is random UUID so just check key)
    calls = [args[0] for args, _ in mock_user_session.set.call_args_list]
    assert "thread_id" in calls
    
    # Check welcome message
    assert mock_cl.Message.called
    assert mock_cl.Message.call_args[1]["content"].startswith("Hello! MABG")

@pytest.mark.asyncio
async def test_app_main_flow(mock_cl_fixture):
    """
    [REQ-FUN-010] Test main message handler.
    Should invoke graph.astream and show output.
    """
    mock_cl, mock_user_session = mock_cl_fixture
    
    # Mock message
    message = MagicMock()
    message.content = "Test Topic"
    
    # Mock Graph
    mock_graph = AsyncMock()
    mock_user_session.get.side_effect = lambda key: mock_graph if key == "graph" else "test-thread-id"
    
    # Mock astream (generator)
    async def mock_astream(*args, **kwargs):
        yield {"event": "test"}
    mock_graph.astream = mock_astream
    
    # Mock get_state (Synchoronous)
    mock_state_snapshot = MagicMock()
    mock_state_snapshot.values = {"phase": "Spec", "spec_doc": "Mock Spec"}
    mock_state_snapshot.next = ("human_review",) # Tuple for interrupt
    mock_graph.get_state = MagicMock(return_value=mock_state_snapshot)
    
    # Execute
    await app.main(message)
    
    # Assert
    # Check output message
    assert mock_cl.Message.call_count >= 1 # Consolidated to 1 (plus DEBUG likely, so >= 1)
    
    # Check if actions are displayed
    last_call = mock_cl.Message.call_args_list[-1]
    assert "actions" in last_call[1] or last_call[1].get("actions")
    
    # Check if actions were created
    assert mock_cl.Action.call_count >= 2
    action_calls = mock_cl.Action.call_args_list
    
    # Check for approve action
    approve_called = any(
        call.kwargs.get("name") == "approve" and 
        "payload" in call.kwargs
        for call in action_calls
    )
    assert approve_called, "Approve action not created or missing payload"
    
    # Check for amend action
    amend_called = any(
        call.kwargs.get("name") == "amend" and
        "payload" in call.kwargs
        for call in action_calls
    )
    assert amend_called, "Amend action not created or missing payload"

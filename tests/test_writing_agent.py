import pytest
from unittest.mock import patch
from src.state import BlogSessionState
from src.agents.writing import writing_agent_node

@pytest.fixture
def mock_run_agent():
    with patch("src.agents.writing.run_agent_chain") as mock:
        mock.return_value = "# Mock Article\n\nContent..."
        yield mock

def test_writing_agent_generate_flow(mock_run_agent):
    """
    [REQ-FUN-030] 記事生成フローのテスト
    - フィードバックがない場合、新規生成が行われること
    """
    state: BlogSessionState = {
        "spec_doc": "# Spec\n...",
        "structure_doc": "# Structure\n...",
        "user_feedback": None,
        "phase": "Structure"
    }
    
    result = writing_agent_node(state)
    
    assert result["phase"] == "Writing"
    assert result["final_article"] == "# Mock Article\n\nContent..."
    assert result["user_feedback"] is None
    
    # Verify call
    mock_run_agent.assert_called_once()
    args = mock_run_agent.call_args[1]
    assert args["input_vars"]["spec_doc"] == state["spec_doc"]
    assert args["input_vars"]["structure_doc"] == state["structure_doc"]

def test_writing_agent_refine_flow(mock_run_agent):
    """
    [REQ-FUN-031] 記事修正フローのテスト
    - フィードバックがある場合、修正が行われること
    """
    state: BlogSessionState = {
        "spec_doc": "# Spec\n...",
        "structure_doc": "# Structure\n...",
        "final_article": "# Old Article",
        "user_feedback": "Make it longer",
        "phase": "Writing"
    }
    
    result = writing_agent_node(state)
    
    assert result["phase"] == "Writing"
    assert result["final_article"] == "# Mock Article\n\nContent..."
    assert result["user_feedback"] is None
    
    # Verify call
    mock_run_agent.assert_called_once()
    args = mock_run_agent.call_args[1]
    assert args["input_vars"]["current_article"] == state["final_article"]
    assert args["input_vars"]["feedback"] == "Make it longer"

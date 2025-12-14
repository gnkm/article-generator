import pytest
from unittest.mock import patch
from src.agents.structure import structure_agent_node
from src.state import BlogSessionState

@pytest.fixture
def mock_run_agent():
    with patch("src.agents.structure.run_agent_chain") as mock:
        mock.return_value = "# Mocked Structure Plan\n\n## H2: Section 1"
        yield mock

def test_structure_agent_generation(mock_run_agent):
    """
    [REQ-FUN-020] 構成案生成フローのテスト。
    """
    # Arrange
    state = BlogSessionState(
        topic="Test Topic",
        spec_doc="# Spec Doc\nRequirements...",
        phase="Spec",
        user_feedback=None
    )
    
    # Act
    result = structure_agent_node(state)
    
    # Assert
    assert result["phase"] == "Structure"
    assert "Mocked Structure Plan" in result["structure_doc"]
    assert result["user_feedback"] is None
    
    mock_run_agent.assert_called_once()
    args = mock_run_agent.call_args[1]
    assert args["input_vars"]["spec_doc"] == state["spec_doc"]

def test_structure_agent_refinement(mock_run_agent):
    """
    [REQ-FUN-021] フィードバックによる構成案修正フローのテスト。
    """
    # Arrange
    state = BlogSessionState(
        topic="Test Topic",
        spec_doc="# Spec Doc",
        structure_doc="Old Structure",
        phase="Structure",
        user_feedback="Make it better"
    )
    
    # Act
    result = structure_agent_node(state)
    
    # Assert
    assert result["phase"] == "Structure"
    assert "Mocked Structure Plan" in result["structure_doc"]
    assert result["user_feedback"] is None # フィードバックはクリアされるべきです
    
    mock_run_agent.assert_called_once()
    args = mock_run_agent.call_args[1]
    assert args["input_vars"]["feedback"] == "Make it better"

def test_structure_agent_missing_spec():
    """
    spec_doc が欠落している場合のエラーハンドリングをテスト。
    """
    state = BlogSessionState(topic="Test Topic") # spec_doc なし
    
    result = structure_agent_node(state)
    
    assert "Error: Spec is missing" in result["structure_doc"]

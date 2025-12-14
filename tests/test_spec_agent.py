import pytest
from unittest.mock import patch
from src.agents.spec import spec_agent_node
from src.state import BlogSessionState



@pytest.fixture
def mock_run_agent():
    with patch("src.agents.spec.run_agent_chain") as mock:
        mock.return_value = "Mocked Spec Content"
        yield mock

def test_generate_spec_success(mock_run_agent):
    """
    仕様書の初期生成をテストします。
    """
    state: BlogSessionState = {"topic": "Remote Work", "phase": "Spec", "user_feedback": None}
    result = spec_agent_node(state)
    
    assert result["phase"] == "Spec"
    assert result["spec_doc"] == "Mocked Spec Content"
    assert result["user_feedback"] is None
    
    # Verify call arguments
    mock_run_agent.assert_called_once()
    args = mock_run_agent.call_args[1]
    assert args["input_vars"]["topic"] == "Remote Work"

def test_generate_spec_no_topic():
    """
    トピック欠落時のハンドリングをテストします。
    """
    state: BlogSessionState = {"topic": None, "phase": "Spec", "user_feedback": None}
    result = spec_agent_node(state)
    
    assert "Error" in result["spec_doc"]

def test_refine_spec_flow(mock_run_agent):
    """
    フィードバックがある場合の修正フローをテストします。
    """
    state: BlogSessionState = {
        "topic": "Remote Work", 
        "phase": "Spec", 
        "spec_doc": "Old Spec", 
        "user_feedback": "Add more details"
    }
    result = spec_agent_node(state)
    
    assert result["spec_doc"] == "Mocked Spec Content"
    # フィードバックはクリアされるべき（または状態遷移ロジックで処理される？ 
    # 状態定義のコメントでは承認時にクリアされるとありましたが、refine_spec がクリアするのは「処理済み」を意味します）
    # 実装を確認すると: `user_feedback: None` が返されています。
    assert result["user_feedback"] is None
    
    # Verify call arguments
    mock_run_agent.assert_called_once()
    args = mock_run_agent.call_args[1]
    assert args["input_vars"]["feedback"] == "Add more details"

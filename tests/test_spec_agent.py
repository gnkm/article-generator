import pytest
from unittest.mock import patch
from src.agents.spec import spec_agent_node
from src.state import BlogSessionState



from langchain_core.runnables import RunnableLambda

@pytest.fixture
def mock_llm_runnable():
    # モジュールレベルの `llm` を、固定出力を返す単純な Runnable に置き換えます。
    # これにより LCEL 内部との複雑な互換性問題を回避できます。
    
    fake_llm = RunnableLambda(lambda x: "Mocked Spec Content")
    
    with patch("src.agents.spec.llm", fake_llm):
        yield fake_llm

def test_generate_spec_success(mock_llm_runnable):
    """
    仕様書の初期生成をテストします。
    """
    state: BlogSessionState = {"topic": "Remote Work", "phase": "Spec", "user_feedback": None}
    result = spec_agent_node(state)
    
    assert result["phase"] == "Spec"
    assert result["spec_doc"] == "Mocked Spec Content"
    assert result["user_feedback"] is None

def test_generate_spec_no_topic():
    """
    トピック欠落時のハンドリングをテストします。
    """
    state: BlogSessionState = {"topic": None, "phase": "Spec", "user_feedback": None}
    result = spec_agent_node(state)
    
    assert "Error" in result["spec_doc"]

def test_refine_spec_flow(mock_llm_runnable):
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

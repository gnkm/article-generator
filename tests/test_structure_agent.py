import pytest
from unittest.mock import patch
from src.agents.structure import structure_agent_node
from src.state import BlogSessionState
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import AIMessage

@pytest.fixture
def mock_llm_structure():
    """
    Structure Agent の LLM レスポンスをシミュレートします。
    """
    with patch("src.agents.structure.llm"):
        # ChatOpenAI の invoke メソッドをモックし、BaseMessage (AIMessage) を返すようにします。
        # コード内では `chain = prompt | llm | StrOutputParser()` となっています。
        # 実装と同様の戦略で `RunnableLambda` を使用して LCEL パイプライン内で機能するようにします。
        
        # LLM生成をシミュレートする関数
        def fake_llm_func(input):
            return AIMessage(content="# Mocked Structure Plan\n\n## H2: Section 1")

        fake_runnable = RunnableLambda(fake_llm_func)
        
        # モジュール内の `llm` 変数をフェイクの runnable に置き換えます
        with patch("src.agents.structure.llm", new=fake_runnable):
            yield fake_runnable

@pytest.mark.asyncio
async def test_structure_agent_generation(mock_llm_structure):
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

@pytest.mark.asyncio
async def test_structure_agent_refinement(mock_llm_structure):
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
    assert "Mocked Structure Plan" in result["structure_doc"] # モックは固定文字列を返しますが、ロジックパスが重要です
    assert result["user_feedback"] is None # フィードバックはクリアされるべきです

@pytest.mark.asyncio
async def test_structure_agent_missing_spec():
    """
    spec_doc が欠落している場合のエラーハンドリングをテスト。
    """
    state = BlogSessionState(topic="Test Topic") # spec_doc なし
    
    result = structure_agent_node(state)
    
    assert "Error: Spec is missing" in result["structure_doc"]

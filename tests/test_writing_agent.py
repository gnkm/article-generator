import pytest
from unittest.mock import MagicMock, patch
from src.state import BlogSessionState
from src.agents.writing import writing_agent_node

@pytest.fixture
def mock_chain_components():
    with patch("src.agents.writing.llm"), \
         patch("src.agents.writing.ChatPromptTemplate") as mock_prompt_cls:
        
        # Setup Prompt Mock
        mock_prompt_instance = MagicMock()
        mock_prompt_cls.from_messages.return_value = mock_prompt_instance
        
        # Setup Chain Mock
        mock_chain = MagicMock()
        
        # prompt | llm -> chain (simplified for test since we mock pipe)
        mock_prompt_instance.__or__.return_value = mock_chain
        mock_chain.__or__.return_value = mock_chain # parser
        
        # Final result invocation
        mock_chain.invoke.return_value = "# Mock Article\n\nContent..."
        
        yield mock_prompt_cls, mock_chain

def test_writing_agent_generate_flow(mock_chain_components):
    """
    [REQ-FUN-030] 記事生成フローのテスト
    - フィードバックがない場合、新規生成が行われること
    """
    mock_prompt_cls, mock_chain = mock_chain_components
    
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
    
    # テンプレート作成の検証
    mock_prompt_cls.from_messages.assert_called_once()
    
    # チェーン実行の検証
    mock_chain.invoke.assert_called_once()
    args = mock_chain.invoke.call_args[0][0]
    assert args["spec_doc"] == state["spec_doc"]
    assert args["structure_doc"] == state["structure_doc"]

def test_writing_agent_refine_flow(mock_chain_components):
    """
    [REQ-FUN-031] 記事修正フローのテスト
    - フィードバックがある場合、修正が行われること
    """
    mock_prompt_cls, mock_chain = mock_chain_components
    
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
    
    mock_prompt_cls.from_messages.assert_called_once()
    
    mock_chain.invoke.assert_called_once()
    args = mock_chain.invoke.call_args[0][0]
    assert args["current_article"] == state["final_article"]
    assert args["feedback"] == "Make it longer"

from typing import Literal
from langgraph.graph import StateGraph, END
from src.state import BlogSessionState
from langgraph.checkpoint.memory import MemorySaver
from src.agents.spec import spec_agent_node
from src.agents.structure import structure_agent_node

# Placeholder functions for nodes. Actual logic will be implemented in agents/ modules.
# spec_agent_node is now imported from src.agents.spec
# structure_agent_node is now imported from src.agents.structure

def writing_agent_node(state: BlogSessionState) -> BlogSessionState:
    """
    [REQ-FUN-030] 記事本文の執筆: 構成案に基づいて記事を書く。
    """
    # TODO: Implement actual LLM call
    dummy_article = "# 記事本文\n\nこれは記事の本文です..."
    return {"final_article": dummy_article, "phase": "Writing", "user_feedback": None}

def human_review_node(state: BlogSessionState) -> BlogSessionState:
    """
    [REQ-FUN-012] [REQ-FUN-021] [REQ-FUN-031] 承認アクション
    ユーザーからの入力を待つノード（LangGraph の interrupt ポイント）。
    Chainlit側でユーザーからの入力を受け取り、stateを更新してから再開する。
    """
    # このノード自体は何もしない。Chainlit側で `user_feedback` が更新された状態でここに戻ってくる。
    # 承認された場合 (user_feedback is None)、次のフェーズへ進むための判定に使われる。
    return {}

def should_continue(state: BlogSessionState) -> Literal["structure_agent", "writing_agent", "end", "spec_agent", "structure_agent_retry", "writing_agent_retry"]:
    """
    条件付きエッジのロジック。
    ユーザーからのフィードバックがあれば、現在のフェーズのエージェントに戻る。
    承認されれば次のフェーズに進む。
    """
    feedback = state.get("user_feedback")
    phase = state.get("phase")

    if feedback:
        # 修正依頼がある場合、現在のエージェントに戻る
        if phase == "Spec":
            return "spec_agent"
        elif phase == "Structure":
            return "structure_agent_retry" # structure_agent と同じだが、名前解決のために区別するかもしくは同じノードを指す
        elif phase == "Writing":
            return "writing_agent_retry"
    
    # 承認された場合 (feedback is None)
    if phase == "Spec":
        return "structure_agent"
    elif phase == "Structure":
        return "writing_agent"
    elif phase == "Writing":
        return "end"
    
    return "end" # Default fallback

# Create the graph
workflow = StateGraph(BlogSessionState)

# Add nodes
workflow.add_node("spec_agent", spec_agent_node)
workflow.add_node("structure_agent", structure_agent_node)
workflow.add_node("writing_agent", writing_agent_node)
workflow.add_node("human_review", human_review_node)

# Set entry point
workflow.set_entry_point("spec_agent")

# Add edges
# Spec Agent -> Human Review
workflow.add_edge("spec_agent", "human_review")

# Human Review -> Conditional -> Next Agent or Retry
workflow.add_conditional_edges(
    "human_review",
    should_continue,
    {
        "spec_agent": "spec_agent", # Rewrite Spec
        "structure_agent": "structure_agent", # Approve Spec -> Create Structure
        "structure_agent_retry": "structure_agent", # Rewrite Structure
        "writing_agent": "writing_agent", # Approve Structure -> Write Article
        "writing_agent_retry": "writing_agent", # Rewrite Article
        "end": END # Approve Article -> Finish
    }
)

# Structure Agent -> Human Review
workflow.add_edge("structure_agent", "human_review")

# Writing Agent -> Human Review
workflow.add_edge("writing_agent", "human_review")

# Compile the graph
memory = MemorySaver()
app_graph = workflow.compile(checkpointer=memory, interrupt_before=["human_review"])

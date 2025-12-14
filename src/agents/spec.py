from typing import Optional
from src.state import BlogSessionState
from src.config import get_llm
from src.agents.common import run_agent_chain

# Initialize LLM with configuration
llm = get_llm("spec_agent")

def spec_agent_node(state: BlogSessionState) -> BlogSessionState:
    """
    [REQ-FUN-011] 仕様案の提示: トピックに基づいて仕様案を生成する。
    [REQ-FUN-012] 仕様案の修正: ユーザーフィードバックに基づいて仕様案を修正する。
    """
    topic = state.get("topic")
    user_feedback = state.get("user_feedback")
    current_spec = state.get("spec_doc")

    if user_feedback and current_spec:
        # Refinement flow
        return _refine_spec(topic, current_spec, user_feedback)
    else:
        # Generation flow
        return _generate_spec(topic)

def _generate_spec(topic: Optional[str]) -> BlogSessionState:
    # [REQ-FUN-011] 仕様案の提示
    if not topic:
        return {"spec_doc": "Error: Topic is missing.", "phase": "Spec", "user_feedback": None}

    spec_doc = run_agent_chain(
        llm=llm,
        system_prompt_name="spec_generator",
        user_prompt_template="以下のトピック（または要望）に基づいて、記事要求仕様書を作成してください。\n\nトピック: {topic}",
        input_vars={"topic": topic}
    )
    
    return {
        "spec_doc": spec_doc,
        "phase": "Spec",
        "user_feedback": None
    }

def _refine_spec(topic: Optional[str], current_spec: str, feedback: str) -> BlogSessionState:
    # [REQ-FUN-012] 仕様案の修正
    updated_spec = run_agent_chain(
        llm=llm,
        system_prompt_name="spec_generator",
        user_prompt_template="以下の現在の仕様書とユーザーフィードバックに基づいて、記事要求仕様書を修正・再生成してください。\n\nトピック: {topic}\n\n現在の仕様書:\n{current_spec}\n\nユーザーフィードバック:\n{feedback}",
        input_vars={
            "topic": topic,
            "current_spec": current_spec,
            "feedback": feedback
        }
    )

    return {
        "spec_doc": updated_spec,
        "phase": "Spec",
        "user_feedback": None # Feedback handled, reset
    }

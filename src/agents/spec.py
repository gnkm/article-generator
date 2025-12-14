from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.state import BlogSessionState
from src.config import get_llm
from src.utils.prompts import load_prompt

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
    if not topic:
        return {"spec_doc": "Error: Topic is missing.", "phase": "Spec", "user_feedback": None}

    system_prompt = load_prompt("spec_generator")
    
    # [REQ-FUN-011]
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", f"以下のトピック（または要望）に基づいて、記事要求仕様書を作成してください。\n\nトピック: {topic}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    spec_doc = chain.invoke({})
    
    return {
        "spec_doc": spec_doc,
        "phase": "Spec",
        "user_feedback": None
    }

def _refine_spec(topic: Optional[str], current_spec: str, feedback: str) -> BlogSessionState:
    system_prompt = load_prompt("spec_generator")
    
    # [REQ-FUN-012]
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", f"以下の現在の仕様書とユーザーフィードバックに基づいて、記事要求仕様書を修正・再生成してください。\n\nトピック: {topic}\n\n現在の仕様書:\n{current_spec}\n\nユーザーフィードバック:\n{feedback}")
    ])

    chain = prompt | llm | StrOutputParser()
    updated_spec = chain.invoke({})

    return {
        "spec_doc": updated_spec,
        "phase": "Spec",
        "user_feedback": None # Feedback handled, reset
    }

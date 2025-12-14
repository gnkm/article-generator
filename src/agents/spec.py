import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from pydantic import SecretStr
from src.state import BlogSessionState
from src.config import get_agent_config

# Initialize LLM with configuration
config = get_agent_config("spec_agent")
api_key_str = os.environ.get("OPENROUTER_API_KEY")
api_key = SecretStr(api_key_str) if api_key_str else None

llm = ChatOpenAI(
    model=config["llm"],
    temperature=config["temperature"],
    api_key=api_key,
    base_url=config.get("base_url")
)

def spec_agent_node(state: BlogSessionState) -> BlogSessionState:
    """
    [REQ-FUN-011] 仕様案の提示
    [REQ-FUN-012] 仕様の修正
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

    prompt = ChatPromptTemplate.from_messages([
        ("system", "あなたはプロのWebライター兼編集者です。与えられたトピックに基づいて、高品質なブログ記事の仕様書（構成案の前段）を作成してください。"),
        ("user", f"トピック: {topic}\n\n以下の項目を含むMarkdown形式の仕様書を作成してください：\n1. ターゲット読者\n2. 検索意図 (Search Intent)\n3. 狙うSEOキーワード\n4. 記事のゴール（読了後の状態）\n5. 想定文字数")
    ])
    
    chain = prompt | llm | StrOutputParser()
    spec_doc = chain.invoke({})
    
    return {
        "spec_doc": spec_doc,
        "phase": "Spec",
        "user_feedback": None
    }

def _refine_spec(topic: Optional[str], current_spec: str, feedback: str) -> BlogSessionState:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "あなたはプロのWebライター兼編集者です。ユーザーのフィードバックに基づいて、ブログ記事の仕様書を修正してください。"),
        ("user", f"トピック: {topic}\n\n現在の仕様書:\n{current_spec}\n\nユーザーからのフィードバック:\n{feedback}\n\nフィードバックを反映して仕様書を書き直してください。Markdown形式で出力してください。")
    ])

    chain = prompt | llm | StrOutputParser()
    updated_spec = chain.invoke({})

    return {
        "spec_doc": updated_spec,
        "phase": "Spec",
        "user_feedback": None # Feedback handled, reset
    }

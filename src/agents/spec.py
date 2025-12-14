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

def _load_prompt(prompt_name: str) -> str:
    """Load a prompt file from the prompts directory."""
    # Assuming prompts are in the root prompts/ directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    prompt_path = os.path.join(project_root, "prompts", f"{prompt_name}.md")
    
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Prompt file not found at {prompt_path}")
        
    with open(prompt_path, "r", encoding="utf-8") as f:
        content = f.read()
        # Remove frontmatter if present (simple check)
        if content.startswith("---"):
            try:
                # Find second ---
                second_dash_index = content.find("---", 3)
                if second_dash_index != -1:
                    return content[second_dash_index + 3:].strip()
            except ValueError:
                pass
        return content

def _generate_spec(topic: Optional[str]) -> BlogSessionState:
    if not topic:
        return {"spec_doc": "Error: Topic is missing.", "phase": "Spec", "user_feedback": None}

    system_prompt = _load_prompt("spec_generator")
    
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
    system_prompt = _load_prompt("spec_generator")
    
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

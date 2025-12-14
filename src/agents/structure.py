import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.state import BlogSessionState
from src.config import get_agent_config
from pydantic import SecretStr

# Initialize LLM with configuration
config = get_agent_config("structure_agent")
api_key_str = os.environ.get("OPENROUTER_API_KEY")
api_key = SecretStr(api_key_str) if api_key_str else None

llm = ChatOpenAI(
    model=config["llm"],
    temperature=config["temperature"],
    api_key=api_key,
    base_url=config.get("base_url")
)

def _load_prompt(prompt_name: str) -> str:
    """Load a prompt file from the prompts directory."""
    # DRY violation: logic duplicated from spec.py. Should extract to common util deeply later or import from spec?
    # For now, it's better to duplicate or move to src.utils?
    # Let's import from spec or move to src.utils.prompts if strict DRY is required.
    # But since this is small task, I'll duplicate for isolation or check if I can define it in a utility module.
    # Given the instructions, let's keep it simple. I heavily prefer importing if possible or defining widely.
    # Let's import from src.agents.spec if python allows, or just create src.utils.loader.
    # Re-implementing here for stability and speed as I haven't created utils yet.
    
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    prompt_path = os.path.join(project_root, "prompts", f"{prompt_name}.md")
    
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Prompt file not found at {prompt_path}")
        
    with open(prompt_path, "r", encoding="utf-8") as f:
        content = f.read()
        if content.startswith("---"):
            try:
                second_dash_index = content.find("---", 3)
                if second_dash_index != -1:
                    return content[second_dash_index + 3:].strip()
            except ValueError:
                pass
        return content

def structure_agent_node(state: BlogSessionState) -> BlogSessionState:
    """
    [REQ-FUN-020] 構成案の提示
    [REQ-FUN-021] 構成案の修正
    """
    spec_doc = state.get("spec_doc")
    user_feedback = state.get("user_feedback")
    current_structure = state.get("structure_doc")

    if user_feedback and current_structure:
        return _refine_structure(spec_doc, current_structure, user_feedback)
    else:
        return _generate_structure(spec_doc)

def _generate_structure(spec_doc: Optional[str]) -> BlogSessionState:
    if not spec_doc:
         return {"structure_doc": "Error: Spec is missing.", "phase": "Structure", "user_feedback": None}

    system_prompt = _load_prompt("structure_generator")
    
    # [REQ-FUN-020]
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", f"以下の記事要求仕様書に基づいて、記事構成案を作成してください。\n\n記事要求仕様書:\n{spec_doc}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    structure_doc = chain.invoke({})
    
    return {
        "structure_doc": structure_doc,
        "phase": "Structure",
        "user_feedback": None
    }

def _refine_structure(spec_doc: Optional[str], current_structure: str, feedback: str) -> BlogSessionState:
    system_prompt = _load_prompt("structure_generator")
    
    # [REQ-FUN-021]
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", f"以下の仕様書、現在の構成案、およびユーザーフィードバックに基づいて、記事構成案を修正してください。\n\n記事要求仕様書:\n{spec_doc}\n\n現在の性案:\n{current_structure}\n\nユーザーフィードバック:\n{feedback}")
    ])

    chain = prompt | llm | StrOutputParser()
    updated_structure = chain.invoke({})

    return {
        "structure_doc": updated_structure,
        "phase": "Structure",
        "user_feedback": None
    }

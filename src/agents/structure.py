from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.state import BlogSessionState
from src.config import get_llm
from src.utils.prompts import load_prompt

# Initialize LLM with configuration
llm = get_llm("structure_agent")

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

    system_prompt = load_prompt("structure_generator")
    
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
    system_prompt = load_prompt("structure_generator")
    
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

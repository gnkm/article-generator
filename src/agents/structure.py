from typing import Optional
from src.state import BlogSessionState
from src.config import get_llm
from src.agents.common import run_agent_chain

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
    # [REQ-FUN-020] 構成案の生成
    if not spec_doc:
         return {"structure_doc": "Error: Spec is missing.", "phase": "Structure", "user_feedback": None}

    structure_doc = run_agent_chain(
        llm=llm,
        system_prompt_name="structure_generator",
        user_prompt_template="以下の記事要求仕様書に基づいて、記事構成案を作成してください。\n\n記事要求仕様書:\n{spec_doc}",
        input_vars={"spec_doc": spec_doc}
    )
    
    return {
        "structure_doc": structure_doc,
        "phase": "Structure",
        "user_feedback": None
    }

def _refine_structure(spec_doc: Optional[str], current_structure: str, feedback: str) -> BlogSessionState:
    # [REQ-FUN-021] 構成案の修正
    updated_structure = run_agent_chain(
        llm=llm,
        system_prompt_name="structure_generator",
        user_prompt_template="以下の仕様書、現在の構成案、およびユーザーフィードバックに基づいて、記事構成案を修正してください。\n\n記事要求仕様書:\n{spec_doc}\n\n現在の性案:\n{current_structure}\n\nユーザーフィードバック:\n{feedback}",
        input_vars={
            "spec_doc": spec_doc,
            "current_structure": current_structure,
            "feedback": feedback
        }
    )

    return {
        "structure_doc": updated_structure,
        "phase": "Structure",
        "user_feedback": None
    }

from src.state import BlogSessionState
from src.config import get_llm
from src.agents.common import run_agent_chain

# Initialize LLM for this agent
llm = get_llm("writing_agent")

def writing_agent_node(state: BlogSessionState) -> BlogSessionState:
    """
    [REQ-FUN-030] 記事執筆エージェントのノード関数
    """
    feedback = state.get("user_feedback")
    spec_doc = state.get("spec_doc") or ""
    structure_doc = state.get("structure_doc") or ""
    current_article = state.get("final_article") or ""

    if feedback and current_article:
        # Refine existing article based on feedback
        new_article = _refine_article(current_article, feedback, spec_doc, structure_doc)
    else:
        # Generate new article
        new_article = _generate_article(spec_doc, structure_doc)

    return {"final_article": new_article, "phase": "Writing", "user_feedback": None}

def _generate_article(spec_doc: str, structure_doc: str) -> str:
    # [REQ-FUN-030] 記事本文の執筆
    return run_agent_chain(
        llm=llm,
        system_prompt_name="writing_generator",
        user_prompt_template="Specification:\n{spec_doc}\n\nArticle Structure:\n{structure_doc}\n\nPlease write the article.",
        input_vars={"spec_doc": spec_doc, "structure_doc": structure_doc}
    )

def _refine_article(current_article: str, feedback: str, spec_doc: str, structure_doc: str) -> str:
    # [REQ-FUN-031] 最終確認・承認（の修正フロー）
    return run_agent_chain(
        llm=llm,
        system_prompt_name="writing_generator",
        user_prompt_template="Specification:\n{spec_doc}\n\nArticle Structure:\n{structure_doc}\n\nCurrent Draft:\n{current_article}\n\nUser Feedback:\n{feedback}\n\nPlease revise the article.",
        input_vars={
            "spec_doc": spec_doc,
            "structure_doc": structure_doc,
            "current_article": current_article,
            "feedback": feedback
        }
    )

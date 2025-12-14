from typing import Any, Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models import BaseChatModel
from src.utils.prompts import load_prompt

def run_agent_chain(
    llm: BaseChatModel,
    system_prompt_name: str,
    user_prompt_template: str,
    input_vars: Dict[str, Any]
) -> str:
    """
    Common function to run an agent chain:
    1. Load system prompt from file
    2. Create prompt template with system prompt and user prompt
    3. Run chain (Prompt -> LLM -> StrOutputParser)
    """
    system_prompt = load_prompt(system_prompt_name)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt_template)
    ])
    
    # input_vars are used to format the 'user' message in the prompt template
    # The invoke call needs the actual values for these variables.
    # However, ChatPromptTemplate expects the formatting to happen during invoke
    # OR we can pre-format.
    # Standard LangChain usage: prompt elements with {var} need values at invoke time.
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke(input_vars)

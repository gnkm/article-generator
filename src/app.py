import uuid
import chainlit as cl

from src.graph import app_graph

@cl.on_chat_start
async def start():
    """
    [REQ-FUN-001] セッション開始
    """
    cl.user_session.set("graph", app_graph)
    # Create a unique thread ID for checkpointer
    thread_id = str(uuid.uuid4())
    cl.user_session.set("thread_id", thread_id)
    
    await cl.Message(content="Hello! MABG is running. Please enter a topic.").send()

@cl.on_message
async def main(message: cl.Message):
    """
    [REQ-FUN-010] トピック入力 & グラフ実行
    """
    graph = cl.user_session.get("graph")
    thread_id = cl.user_session.get("thread_id")
    config = {"configurable": {"thread_id": thread_id}}
    
    # Run graph (async)
    # If starting fresh, input is topic. If resuming, input is None usually, but here we restart on new topic text?
    # Assuming standard flow: User inputs topic -> Graph runs -> Interrupt -> User action.
    
    inputs = {"topic": message.content}
    
    # Run the graph until the first interruption
    # [REQ-PER-001] ローカルレスポンス: 非同期実行(astream/ainvoke)によりUIブロックしない
    async for event in graph.astream(inputs, config, stream_mode="values"):
         # We can stream intermediate outputs if needed, or just wait for finish/interrupt
         pass
    
    # Retrieve current state to decide what to show
    state_snapshot = graph.get_state(config)
    current_state = state_snapshot.values
    next_step = state_snapshot.next
    
    # Show output based on phase
    await cl.Message(content=f"DEBUG: Next={next_step}, Phase={current_state.get('phase')}").send()
    await _show_output_and_actions(current_state, next_step)

async def _show_output_and_actions(state: dict, next_step: tuple):
    phase = state.get("phase")
    content = _format_response(state)
    
    actions = []
    
    # If waiting for human review
    if next_step and "human_review" in next_step:
        actions = [
            cl.Action(name="approve", label="Approve (Next Phase)", payload={"value": "approve"}),
            cl.Action(name="amend", label="Amend (Feedback)", payload={"value": "amend"})
        ]
    
    msg_content = f"**Phase: {phase}**\n\n{content}"
    if phase == "Done":
        msg_content = f"**記事作成が完了しました**\n\n{content}"
    
    if actions:
        msg_content += "\n\n(Please review using the buttons below)"
        
    await cl.Message(content=msg_content, actions=actions).send()

@cl.action_callback("approve")
async def on_approve(action: cl.Action):
    await action.remove()
    
    graph = cl.user_session.get("graph")
    thread_id = cl.user_session.get("thread_id")
    config = {"configurable": {"thread_id": thread_id}}
    
    # Resume with feedback = None represents approval
    # We update the state with user_feedback=None because logic checks "if feedback:"
    # Actually logic: "if feedback: retry else: next". 
    # State update via update_state
    graph.update_state(config, {"user_feedback": None})
    
    await cl.Message(content="Approved. Proceeding to next phase...").send()
    
    # Resume graph execution (invoke with None input as we updated state directly)
    await _resume_graph(graph, config)

@cl.action_callback("amend")
async def on_amend(action: cl.Action):
    await action.remove()
    # Ask for feedback
    res = await cl.AskUserMessage(content="Please enter your feedback for revision:", timeout=600).send()
    if res:
        feedback_text = res["output"]
        
        graph = cl.user_session.get("graph")
        thread_id = cl.user_session.get("thread_id")
        config = {"configurable": {"thread_id": thread_id}}
        
        # Update state with feedback
        graph.update_state(config, {"user_feedback": feedback_text})
        
        await cl.Message(content="Feedback received. Refining...").send()
        
        # Resume graph
        await _resume_graph(graph, config)

async def _resume_graph(graph, config):
    async for event in graph.astream(None, config, stream_mode="values"):
        pass
        
    state_snapshot = graph.get_state(config)
    current_state = state_snapshot.values
    next_step = state_snapshot.next
    
    await _show_output_and_actions(current_state, next_step)

def _format_response(state: dict) -> str:
    """Helper to format content based on phase."""
    phase = state.get("phase")
    if phase == "Spec":
        return state.get("spec_doc", "")
    elif phase == "Structure":
        return state.get("structure_doc", "")
    elif phase == "Writing":
        return state.get("final_article", "")
    elif phase == "Done":
        return state.get("final_article", "Done")
    else:
        return str(state)

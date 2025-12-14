import chainlit as cl

@cl.on_chat_start
async def start():
    """
    [REQ-FUN-001] セッション開始
    チャットセッションを初期化する。
    """
    await cl.Message(content="Hello! MABG is running.").send()

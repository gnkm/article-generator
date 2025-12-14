import chainlit as cl

from src.graph import app_graph

@cl.on_chat_start
async def start():
    """
    [REQ-FUN-001] セッション開始
    チャットセッションを初期化する。
    """
    cl.user_session.set("graph", app_graph)
    await cl.Message(content="Hello! MABG is running. Please enter a topic.").send()

@cl.on_message
async def main(message: cl.Message):
    """
    [REQ-FUN-010] トピック入力
    ユーザーからの入力をトピックとしてグラフを実行する。
    """
    # テスト用: セッションからグラフを取得
    graph = cl.user_session.get("graph")
    
    # グラフ実行 (非同期)
    inputs = {"topic": message.content}
    result = await graph.ainvoke(inputs)
    
    # 結果の表示
    phase = result.get("phase")
    content = _format_response(result)

    await cl.Message(content=f"Processed (Phase: {phase}):\n\n{content}").send()

def _format_response(state: dict) -> str:
    """
    現在のフェーズに基づいて表示すべきコンテンツを抽出するヘルパー関数。
    """
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

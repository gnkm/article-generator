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
    # テスト用: セッションからグラフを取得（モック差し替え可能にするため）
    graph = cl.user_session.get("graph")
    
    # グラフ実行 (現状は同期実行。将来的に ainvoke に変更推奨)
    # 初期入力は topic として扱う
    inputs = {"topic": message.content}
    
    # Run the graph
    # Note: invoke is synchronous. in a real async app we might want to use ainvoke or run_in_executor
    result = graph.invoke(inputs)
    
    # 結果の表示 (簡易実装)
    # 最終的な実装では、phaseごとの中間生成物を表示するが、まずはテスト通過のため結果を表示
    phase = result.get("phase")
    content = ""
    if phase == "Spec":
        content = result.get("spec_doc", "")
    elif phase == "Structure":
        content = result.get("structure_doc", "")
    elif phase == "Writing":
        content = result.get("final_article", "")
    elif phase == "Done":
        content = result.get("final_article", "Done")
    else:
        content = str(result)

    await cl.Message(content=f"Processed (Phase: {phase}):\n\n{content}").send()

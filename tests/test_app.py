import pytest
from unittest.mock import MagicMock, AsyncMock
import sys

# src.app をインポートする前に chainlit をモックする
# これにより @cl.on_chat_start などのデコレータが副作用を起こすのを防ぐ
mock_cl = MagicMock()
mock_cl.on_chat_start = lambda f: f
mock_cl.on_message = lambda f: f
sys.modules["chainlit"] = mock_cl

# chainlitをモックに差し替えてからappを読み込むため、import順序のルール(E402)を無視する
import src.app as app  # noqa: E402

@pytest.fixture
def mock_cl_fixture():
    # テストごとにモックの状態をリセット
    mock_cl.reset_mock()
    
    # User Session
    mock_cl.user_session = MagicMock()
    mock_cl.user_session.get = MagicMock(return_value=None)
    
    # Message
    message_instance = AsyncMock()
    mock_cl.Message.return_value = message_instance
    
    return mock_cl

@pytest.mark.asyncio
async def test_req_fun_001_session_start(mock_cl_fixture):
    """
    [REQ-FUN-001] セッション開始
    - ウェルカムメッセージが表示されること。
    - セッションにグラフ(または状態)が初期化されること。
    """
    await app.start()
    
    # メッセージ送信の確認
    assert mock_cl_fixture.Message.called
    # contentに何か入っているか
    args, kwargs = mock_cl_fixture.Message.call_args
    assert "content" in kwargs or len(args) > 0
    
    # sendが呼ばれたか
    mock_cl_fixture.Message.return_value.send.assert_awaited_once()

@pytest.mark.asyncio
async def test_req_fun_010_topic_input_processing(mock_cl_fixture):
    """
    [REQ-FUN-010] トピック入力とグラフ実行
    - ユーザーからのメッセージを受け取り、グラフを実行するロジック。
    - まだ実装されていないが、TDDとして期待動作を記述。
    """
    # モック: ユーザー入力メッセージ
    user_message = MagicMock()
    user_message.content = "リモートワークの課題"
    
    # モック: セッションにグラフランナブルがあると仮定
    mock_graph_runnable = MagicMock()
    # invoke の戻り値 (Spec生成結果)
    mock_graph_runnable.invoke.return_value = {
        "phase": "Spec",
        "spec_doc": "# 仕様書ドラフト"
    }
    
    # user_session.get("graph") がこのランナブルを返すように設定
    mock_cl_fixture.user_session.get.return_value = mock_graph_runnable
    
    # テスト対象関数呼び出し
    if hasattr(app, 'main'):
        await app.main(user_message)
        
        # 検証ポイント:
        # 1. グラフが invoke されたか
        mock_graph_runnable.invoke.assert_called()
        
        # 2. 結果(仕様書)がメッセージとして送信されたか
        assert mock_cl_fixture.Message.call_count >= 1
    else:
        pytest.fail("app.main (on_message handler) is not implemented yet.")

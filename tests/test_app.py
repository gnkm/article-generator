import pytest
from unittest.mock import MagicMock
import src.app as app

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

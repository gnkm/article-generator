# 実装計画書: Multi-Agent Blog Generator (MABG)

この計画書は、ChainlitとLangGraphを使用したインタラクティブなブログ作成ローカルWebアプリケーション、MABGの実装詳細を定義します。

## 重要事項

> [!IMPORTANT]
> **LLMプロバイダ**: 本システムは、`langchain-openai` を介して **OpenRouter** を使用します（`docs/tech_stack.md`準拠）。`.env` に `OPENROUTER_API_KEY` (または `OPENAI_API_KEY`) が設定されていることを確認してください。

> [!NOTE]
> **プロジェクト構成**: `uv` パッケージマネージャを使用した標準的な `src/` レイアウトを採用します。

## 1. プロジェクト構成

### pyproject.toml
- `uv init` で初期化。
- 依存関係: `chainlit`, `langchain`, `langgraph`, `langchain-openai`, `pydantic`, `python-dotenv`.
- 開発依存関係: `pytest`, `pytest-asyncio`, `ruff`, `mypy`, `lefthook`.

### Dockerfile
- Python 3.13 slimイメージ。
- `uv` による依存関係インストール。
- エントリーポイント: `chainlit run src/app.py -w`.

### lefthook.yml
- Pythonコード実装前に作成します。
- commit-msg, pre-commit フックを設定 (ruff, mypy, gitleaks, pytest)。
- `uv run lefthook install` で有効化。

### docker-compose.yml
- 開発用にローカルディレクトリをマウントする `app` サービス。
- ポート8900を公開。
- `.env` の読み込み。

## 2. 実装ガイドライン (要件トレーサビリティ)

すべてのPythonファイルにおいて、実装するクラスや関数がどの要件に対応するかをdocstringまたはコメントで明記してください。
これは実装の最初のステップで実行してください。

例:
```python
def start_chat():
    """
    [REQ-FUN-001] セッション開始
    チャットセッションを初期化する。
    """
    pass
```

## 3. アプリケーションアーキテクチャ

### src/state.py (State Definition)
- `TypedDict` または Pydantic を使用して `BlogSessionState` を定義 (LangGraph要件)。
- フィールド: `topic`, `spec_doc`, `structure_doc`, `final_article`, `feedback`, `phase`.

### src/agents/spec.py (Spec Agent)
 - `generate_spec(state)`: `[REQ-FUN-011]` LLMを使用してトピックから仕様書を生成。
 - `refine_spec(state)`: `[REQ-FUN-012]` フィードバックに基づいて仕様書を更新。

### src/agents/structure.py (Structure Agent)
- `generate_structure(state)`: `[REQ-FUN-020]` 仕様書 -> 構成案。
- `refine_structure(state)`: `[REQ-FUN-021]` 構成案の改善ループ。

### src/agents/writing.py (Writing Agent)
- `write_article(state)`: `[REQ-FUN-030]` 構成案 -> 記事本文。
- `refine_article(state)`: `[REQ-FUN-031]` 記事の改善ループ。

### src/graph.py (Orchestration)
- LangGraphワークフローの定義。
- ノード: `spec_agent`, `structure_agent`, `writing_agent`, `human_review`.
- エッジ: 承認/却下に基づく条件付きエッジ。

### src/app.py (UI Entrypoint)
- Chainlitエントリーポイント。
- ハンドラ:
    - `@cl.on_chat_start`: `[REQ-FUN-001]` グラフの初期化。
    - `@cl.on_message`: `[REQ-FUN-010]` トピックまたはフィードバックの受信。
    - 中間成果物 (仕様書、構成案) を `cl.Message` で表示。
    - Action (`Approve`, `Reject`) を提示してグラフの状態遷移を駆動。

## 4. 検証計画

### 自動テスト (Requirements Verification)
各要件が満たされていることを確認するためのテストコードを作成します。テスト関数名またはdocstringにも対応する要件IDを記載します。

- `tests/test_requirements.py`:
    - `test_req_fun_011_spec_generation()`: 仕様書生成の出力フォーマット検証。
    - `test_req_fun_020_structure_generation()`: 構成案生成のロジック検証。
- `pytest` を実行してエージェントのロジックを検証 (LLM呼び出しはモック化)。
- コミット前に `lefthook` によるチェック (lint, types) を実施。

### 手動検証手順
1. `docker compose up` を実行。
2. `localhost:8900` を開く。
3. トピック「リモートワークのベストプラクティス」を入力。
4. 仕様書生成を確認 -> 「修正」をクリック -> フィードバック「ツール紹介は除外」を入力 -> 更新を確認。
5. 「承認」をクリック -> 構成案生成を確認。
6. 執筆生成 -> 最終出力を確認。

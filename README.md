# Multi-Agent Blog Generator (MABG)

**MABG** は、複数のAIエージェントが協調して高品質なブログ記事を作成するローカルWebアプリケーションです。
仕様策定、記事構成、執筆の各フェーズでユーザーのフィードバックを受け付ける **Human-in-the-Loop** ワークフローを採用しています。

## ✨ 特徴

*   **3段階のエージェントワークフロー**:
    1.  **Spec Agent**: トピックに基づき、記事のターゲット・ゴール・SEOキーワードなどの仕様を策定。
    2.  **Structure Agent**: 仕様書に基づき、記事の見出し構成（プロット）を作成。
    3.  **Writing Agent**: 承認された構成案に従って記事本文を執筆。
*   **Human-in-the-Loop**: 各フェーズでAIの出力に対して「承認 (Approve)」または「修正 (Amend)」を行えます。納得いくまでリテイク可能です。
*   **ローカル実行**: データはローカルで完結し（LLM API通信を除く）、セキュアに利用できます。

## 🚀 使い方 (Usage)

### 前提条件

*   Docker Desktop (または Docker Engine + Docker Compose)

### 1. インストール

```bash
# リポジトリのクローン
git clone <repository-url>
cd article-generator
```

### 2. 環境設定

`.env` ファイルを作成し、必要なAPIキーを設定してください（現状はOpenRouterなどを使用）。

```bash
# .env
OPENROUTER_API_KEY=your_api_key_here

# 環境 (dev / prod)
# config.toml の [*.dev] または [*.prod] 設定を読み込みます。デフォルトは dev です。
APP_ENV=dev
```

設定ファイル (`config.toml`) を用意します。

```bash
cp config.example.toml config.toml
```

※ `src/config.py` および `config.toml` の設定に従います。

### 3. アプリケーションの起動

以下のコマンドでChainlitサーバーを起動します。

```bash
docker compose up -d
```

### 4. 記事作成フロー

1.  ブラウザで `http://localhost:8900` が開きます。
2.  チャット欄に「記事のトピック」（例: *LangGraphを使ったAIエージェント開発入門*）を入力します。
3.  **Spec Agent** が記事仕様書を提案します。内容を確認し、「Approve」または「Amend」を選択します。
4.  **Structure Agent** が構成案を作成します。同様にレビューします。
5.  **Writing Agent** が記事を執筆します。最終確認を行い、問題なければ完了です。

## 📂 ドキュメント

*   [要求仕様書 (Requirements)](docs/requirements.md)
*   [基本設計書 (Design)](docs/design.md)
*   [要件・実装対応表 (Traceability)](docs/traceability.md)

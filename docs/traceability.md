# 要求仕様と実装の対応 (Traceability Matrix)

`docs/requirements.md` に定義された機能要件 (`REQ-FUN-xxx`)、品質要件 (`REQ-PER-xxx`, `REQ-MNT-xxx`) と、実際のコード実装のマッピングを示します。

## 機能要件 (Functional Requirements)

| 要件ID | 概要 | 実装ファイル (主な箇所) | 備考 |
| :--- | :--- | :--- | :--- |
| **[REQ-FUN-001]** | セッション開始 (ワークフロー制御) | `src/app.py` (`start`), `src/state.py` | アプリ起動、状態定義 |
| **[REQ-FUN-010]** | トピック入力 | `src/app.py` (`main`) | Chainlit `on_chat_start` / `on_message` |
| **[REQ-FUN-011]** | 仕様案の提示 | `src/agents/spec.py` (`spec_agent_node`) | Spec生成プロンプト実行 |
| **[REQ-FUN-012]** | 仕様の承認・修正 | `src/agents/spec.py` (`_refine_spec`), `src/graph.py` | `human_review_node`, 修正ロジック |
| **[REQ-FUN-020]** | 構成案の生成 | `src/agents/structure.py` (`structure_agent_node`) | Structure生成プロンプト実行 |
| **[REQ-FUN-021]** | 構成の承認・修正 | `src/agents/structure.py` (`_refine_structure`), `src/graph.py` | 同上 |
| **[REQ-FUN-030]** | 記事本文の執筆 | `src/agents/writing.py` (`writing_agent_node`) | Writing生成プロンプト実行 |
| **[REQ-FUN-031]** | 最終確認・承認 | `src/agents/writing.py` (`_refine_article`), `src/graph.py` | 最終成果物のフィードバックループ |

## 品質・保守性要件 (Quality & Maintenance Requirements)

| 要件ID | 概要 | 実装ファイル (主な箇所) | 備考 |
| :--- | :--- | :--- | :--- |
| **[REQ-PER-001]** | ローカルレスポンスの即時性 | `src/app.py` | 非同期実装 (`ainvoke`) によりUIブロックを回避 |
| **[REQ-MNT-001]** | コードの簡潔性 | `src/agents/common.py`, `src/graph.py` | 共通化とLangGraphによるロジックと制御の分離 |

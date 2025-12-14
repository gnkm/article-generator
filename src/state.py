from typing import TypedDict, Optional, Literal

class BlogSessionState(TypedDict):
    """
    [REQ-FUN-001] ワークフロー制御: セッション全体の状態管理
    Z記法の State Space 定義 (Section 6.1) に対応します。
    """
    phase: Literal["Spec", "Structure", "Writing", "Done"]
    topic: Optional[str]
    spec_doc: Optional[str]
    structure_doc: Optional[str]
    final_article: Optional[str]
    user_feedback: Optional[str] # 現在の phase に対応する成果物へのフィードバック。承認時にクリアされる。

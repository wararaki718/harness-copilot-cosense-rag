# Copilot Instructions

このリポジトリで作業する際は、以下の方針を常に適用してください。

## 1. 参照優先ドキュメント
- アーキテクチャの正: [architecture.md](../architecture.md)
- Agent 共通ルール: [instructions/agents.instructions.md](instructions/agents.instructions.md)
- Agent 定義: [agents](agents)
- Skill 定義: [skills](skills)

実装や仕様提案は、上記の内容と矛盾しないこと。

### 1.1 役割分離（必須）
- `agents`: エージェントの定義（担当領域・責務・スキル参照）
- `instructions`: エージェントが従う共通指示・品質基準・出力ルール
- `skills`: エージェントが参照する実装手順・チェックリスト・ノウハウ
- 矛盾時の優先順位: `instructions > agents > skills`

## 2. プロジェクト前提
- 本システムは **Cosense ベースの RAG**。
- オフライン（手動バッチ）でインデックス構築し、オンラインで質問応答を行う。
- 構成要素:
  - Batch Ingestion（Python）
  - Embedding Service（Japanese-SPLADE）
  - Retrieval Service（Python + Elasticsearch）
  - LLM Generation（Ollama Gemma3）
  - Frontend（React + TypeScript）

## 3. 実装ルール
- 変更は **最小・局所的** に行う。
- 破壊的変更は避け、必要時は影響範囲を明示する。
- 外部依存（Cosense API / Embedding API / LLM）失敗を前提に、タイムアウト・再試行・フォールバックを考慮する。
- 機密情報（APIトークン等）は環境変数で管理し、コードやログへ出力しない。
- Elasticsearch と Python クライアントのバージョン互換性を維持する。

## 4. API・検索品質ルール
- 回答生成は常に **検索コンテキスト優先**。
- citation（参照情報）の追跡可能性を維持する。
- 低関連時の「情報不足」フォールバックを壊さない。
- `sparse_vector` の扱いは埋め込みモデル仕様と整合させる。

## 5. ドキュメントルール
- 実装変更時は、関連ドキュメント（README/architecture/API仕様）も必要に応じて更新する。
- アーキテクチャやフロー説明では Mermaid を優先利用する。
- 用語を統一する（例: sparse vector, Top-K, citation）。

## 6. 期待される回答スタイル
- まず「何を変えるか」を明確にし、次に「なぜ必要か」を短く示す。
- 実装提案には、影響範囲と検証方法（最小テスト手順）を含める。
- 不明点が品質に大きく影響する場合のみ質問し、それ以外は妥当なデフォルトで前進する。

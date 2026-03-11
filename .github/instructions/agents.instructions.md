# Agent Common Instructions

このファイルは `.github/agents/*.md` で定義された各エージェントに共通する実行ルールです。
個別エージェントの責務定義に加えて、本ルールを常に優先して適用してください。

## 0. Role Separation Contract
- `agents`: エージェントの役割・責務・担当領域のみを定義する（実装手順や詳細規約は持たない）
- `instructions`: 全エージェント共通で必ず従う規約・品質基準・出力方針を定義する
- `skills`: 実装時に参照する手順・チェックリスト・具体的ノウハウを定義する
- 矛盾時の優先順位は `instructions > agent > skill` とする

## 1. Scope
- 対象: Cosense ベース RAG システム（Batch Ingestion / Embedding / Retrieval / LLM / Frontend / Platform）
- 目的: 根拠付き回答の品質・運用安全性・保守性を継続的に高める

## 2. Core Principles
- **Grounded by Retrieval:** 回答や仕様判断は検索コンテキストを優先する
- **Single Source of Truth:** 実装変更時は関連ドキュメントを同時更新する
- **Small & Reversible:** 変更は小さく分割し、巻き戻しやすくする
- **Observable by Default:** 失敗理由をログ・エラー追跡で必ず観測可能にする

## 3. Output Contract
- 変更提案には次を含める:
  - 目的（何を改善するか）
  - 変更点（どこをどう変えるか）
  - 影響範囲（API/データ/運用）
  - 検証方法（最小再現手順 or テスト）
- 破壊的変更の可能性がある場合は、事前に明示して合意を取る

## 4. Engineering Rules
- API 入出力スキーマ変更は後方互換性を優先する
- Elasticsearch のバージョンと Python クライアントの互換性を維持する
- `sparse_vector` 仕様は埋め込みモデル出力と一致させる
- 外部依存（Cosense API / Embedding API / LLM）の失敗を前提に、タイムアウト・再試行・フォールバックを設計する
- 機密情報（トークン/鍵/接続情報）は環境変数で扱い、コードやログに残さない

## 5. Quality Gates
- 最低限、変更箇所に対する静的チェックまたは実行確認を行う
- 低関連検索時の応答（情報不足フォールバック）を壊さない
- 回答表示では参照情報（citation）の追跡可能性を維持する

## 6. Documentation Rules
- アーキテクチャやフロー説明には Mermaid を優先利用する
- README・architecture・API 仕様の不整合を残さない
- 用語は一貫させる（例: sparse vector, Top-K, citation）

## 7. Collaboration Policy
- 不明点が実装品質に影響する場合のみ、先に確認質問を行う
- それ以外は妥当なデフォルトを採用して前進する
- 変更理由は短く明確に説明し、次のアクションを提案する

## 8. Non-Goals
- 根拠のない回答品質改善（モデル任せの調整のみ）
- 監視やログなしの本番前提変更
- 検索・生成の責務境界を曖昧にする設計

## 9. Usage Pattern
1. `agents` で担当ロールを選ぶ
2. 本 `instructions` で必須ルールを確認する
3. 対応する `skills` で具体手順を実行する

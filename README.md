# harness-copilot-cosense-rag

Cosense をデータソースとする RAG システムの設計・実装用リポジトリです。

## 主要ドキュメント

- システム仕様書: [docs/system-specification.md](docs/system-specification.md)
- アーキテクチャ: [architecture.md](architecture.md)

## Copilot 設定

GitHub Copilot の設定を以下に分離して配置しています。

- Agent 定義（役割/責務）: [.github/agents](.github/agents)
- Instructions（共通指示/品質基準）: [.github/instructions/agents.instructions.md](.github/instructions/agents.instructions.md)
- Skills（実装ノウハウ/手順）: [.github/skills](.github/skills)
- プロジェクト共通方針: [.github/copilot-instructions.md](.github/copilot-instructions.md)

### 使い方

1. 目的に合う agent を `.github/agents` から選択する
2. `.github/instructions/agents.instructions.md` で共通ルールを確認する
3. 対応する skill を `.github/skills` から選び、実装手順を適用する
4. 実装・ドキュメント変更時は影響範囲と検証方法を明示する

### 利用可能な agent

- `batch-ingestion-engineer`
- `embedding-service-engineer`
- `retrieval-service-engineer`
- `llm-generation-engineer`
- `frontend-ui-engineer`
- `platform-observability-engineer`
- `document-engineer`

### 利用可能な skills

- `rag-ingestion-indexing`
- `rag-embedding-service`
- `rag-retrieval-generation`
- `rag-frontend-experience`
- `rag-platform-observability`
- `rag-docs-governance`
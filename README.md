# harness-copilot-cosense-rag

Cosense をデータソースとする RAG システムの設計・実装用リポジトリです。

## Agent 設定

GitHub Copilot の agent 設定を以下に配置しています。

- Agent 定義: [.github/agents](.github/agents)
- 共通ルール: [.github/instructions/agents.instructions.md](.github/instructions/agents.instructions.md)

### 使い方

1. 目的に合う agent を `.github/agents` から選択する
2. 各 agent の `Boundaries` と `Common Instructions` を確認する
3. 実装・ドキュメント変更時は共通ルールに従って、影響範囲と検証方法を明示する

### 利用可能な agent

- `batch-ingestion-engineer`
- `embedding-service-engineer`
- `retrieval-service-engineer`
- `llm-generation-engineer`
- `frontend-ui-engineer`
- `platform-observability-engineer`
- `document-engineer`
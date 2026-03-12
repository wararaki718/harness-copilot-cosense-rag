# harness-copilot-cosense-rag

Cosense をデータソースとする RAG システムの設計・実装用リポジトリです。

## 主要ドキュメント

- システム仕様書: [docs/system-specification.md](docs/system-specification.md)
- アーキテクチャ: [architecture.md](architecture.md)

## 実装スケルトン（MVP）

以下の 3 サービスを最小構成で実装済みです。

- `services/embedding_service`: `POST /embed` を提供
- `services/retrieval_service`: `POST /search` を提供
- `services/llm_generation_service`: `POST /generate` を提供

現在のスケルトンでは、外部依存が未起動でも動作確認できるように以下を採用しています。

- Embedding Service は軽量モックで sparse vector map を返却
- LLM Generation は `LLM_MODE=mock` でモック応答（`LLM_MODE=ollama` で Ollama 呼び出し）

## クイックスタート

1. 依存インストール

```bash
make install
```

1. 環境変数ファイル作成

```bash
make init-env
```

1. サービス起動

ローカルで個別起動（3ターミナル）:

```bash
make run-embedding
make run-llm
make run-retrieval
```

または Docker Compose で一括起動:

```bash
make up
```

1. 疎通確認

```bash
curl -X POST http://localhost:8000/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"仕様書の更新手順は？"}'
```

## Makefile コマンド

- `make help`: 利用可能コマンドを表示
- `make install`: Python 依存をインストール
- `make init-env`: `.env` がなければ `.env.example` から作成
- `make run-embedding`: Embedding Service をローカル起動（`8001`）
- `make run-llm`: LLM Generation Service をローカル起動（`8002`）
- `make run-retrieval`: Retrieval Service をローカル起動（`8000`）
- `make up`: Docker Compose で全サービス起動
- `make down`: Docker Compose の全サービス停止
- `make logs`: Docker Compose のログ追跡
- `make ps`: Docker Compose の状態確認
- `make health`: 3サービスの `healthz` を順に確認
- `make check`: `services` 配下の Python 構文チェックを実行
- `make test`: `pytest` でテストスイートを実行

### 実行例

```bash
make help
make install
make init-env
make check
make test
make up
make health
make down
```

## API エンドポイント（スケルトン）

- `POST /embed`（Embedding Service）
  - request: `{ "texts": ["..."], "type": "document|query" }`
  - response: `{ "vectors": [{ "token_x": 0.5, "token_y": 0.3 }] }`
- `POST /search`（Retrieval Service）
  - request: `{ "query": "...", "top_k": 5, "score_threshold": 0.2 }`
  - response: `{ "answer": "...", "citations": [{ "title": "...", "url": "..." }] }`
- `POST /generate`（LLM Generation Service）
  - request: `{ "query": "...", "contexts": [{ "content": "...", "title": "...", "url": "..." }], "max_tokens": 512 }`
  - response: `{ "answer": "..." }`

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

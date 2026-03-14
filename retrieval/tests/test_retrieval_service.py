from fastapi.testclient import TestClient

from retrieval.app import main
from retrieval.app.schemas import RetrievedDocument

app = main.app


def test_search_returns_answer_and_citations(monkeypatch) -> None:
    async def fake_embed_query(query: str, trace_id: str) -> dict[str, float]:
        _ = (query, trace_id)
        return {"token_rag": 0.8}

    def fake_retrieve_documents_from_elasticsearch(
        sparse_vector: dict[str, float],
        top_k: int,
        trace_id: str,
    ) -> list[RetrievedDocument]:
        _ = (sparse_vector, top_k, trace_id)
        return [
            RetrievedDocument(
                title="RAG運用ガイド",
                url="https://scrapbox.io/example/rag-ops",
                content="障害時はトレースIDを確認します。",
                score=0.9,
            ),
            RetrievedDocument(
                title="RAG運用ガイド",
                url="https://scrapbox.io/example/rag-ops",
                content="重複 citation を検証するためのデータです。",
                score=0.7,
            ),
            RetrievedDocument(
                title="RAGアーキテクチャ",
                url="https://scrapbox.io/example/rag-architecture",
                content="Retrieval は LLM Generation API を呼び出します。",
                score=0.6,
            ),
        ]

    async def fake_generate_answer(
        query: str,
        docs: list[RetrievedDocument],
        trace_id: str,
        max_tokens: int,
    ) -> str:
        _ = (query, docs, trace_id, max_tokens)
        return "モック回答"

    monkeypatch.setattr(main, "embed_query", fake_embed_query)
    monkeypatch.setattr(main, "retrieve_documents_from_elasticsearch", fake_retrieve_documents_from_elasticsearch)
    monkeypatch.setattr(main, "generate_answer", fake_generate_answer)

    client = TestClient(app)
    response = client.post("/search", json={"query": "仕様書の更新手順は？"})

    assert response.status_code == 200
    body = response.json()
    assert "answer" in body
    assert "citations" in body
    assert isinstance(body["citations"], list)
    assert body["answer"] == "モック回答"
    assert body["citations"] == [
        {"title": "RAG運用ガイド", "url": "https://scrapbox.io/example/rag-ops"},
        {"title": "RAGアーキテクチャ", "url": "https://scrapbox.io/example/rag-architecture"},
    ]


def test_search_returns_fallback_when_threshold_high(monkeypatch) -> None:
    async def fake_embed_query(query: str, trace_id: str) -> dict[str, float]:
        _ = (query, trace_id)
        return {"token_rag": 1.0}

    def fake_retrieve_documents_from_elasticsearch(
        sparse_vector: dict[str, float],
        top_k: int,
        trace_id: str,
    ) -> list[RetrievedDocument]:
        _ = (sparse_vector, top_k, trace_id)
        return [
            RetrievedDocument(
                title="Low score doc",
                url="https://scrapbox.io/example/low",
                content="関連性が低い文書です。",
                score=0.1,
            )
        ]

    monkeypatch.setattr(main, "embed_query", fake_embed_query)
    monkeypatch.setattr(main, "retrieve_documents_from_elasticsearch", fake_retrieve_documents_from_elasticsearch)

    client = TestClient(app)
    response = client.post(
        "/search",
        json={"query": "仕様書の更新手順は？", "score_threshold": 0.99},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["citations"] == []
    assert "該当情報が見つからない" in body["answer"]


def test_search_returns_fallback_when_embedding_fails(monkeypatch) -> None:
    async def fake_embed_query(query: str, trace_id: str) -> dict[str, float]:
        _ = (query, trace_id)
        return {}

    monkeypatch.setattr(main, "embed_query", fake_embed_query)

    client = TestClient(app)
    response = client.post("/search", json={"query": "embedding エラー時"})

    assert response.status_code == 200
    body = response.json()
    assert body["citations"] == []
    assert body["answer"] == main.settings.fallback_message

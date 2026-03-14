from fastapi.testclient import TestClient

from embedding.app.main import app, to_sparse_vector


def test_embed_returns_sparse_vectors() -> None:
    client = TestClient(app)
    response = client.post(
        "/embed",
        json={"texts": ["RAG の設計", "検索 コンテキスト"], "type": "document"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "vectors" in body
    assert len(body["vectors"]) == 2
    assert isinstance(body["vectors"][0], dict)


def test_to_sparse_vector_is_preprocess_consistent() -> None:
    vector_document = to_sparse_vector("  RAG\nコンテキスト  ", max_tokens=64)
    vector_query = to_sparse_vector("rag コンテキスト", max_tokens=64)

    assert vector_document == vector_query


def test_embed_rejects_too_many_texts() -> None:
    client = TestClient(app)
    response = client.post(
        "/embed",
        json={"texts": ["x"] * 65, "type": "document"},
    )

    assert response.status_code == 422

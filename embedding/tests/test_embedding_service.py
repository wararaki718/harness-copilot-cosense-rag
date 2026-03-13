from fastapi.testclient import TestClient

from embedding.app.main import app


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

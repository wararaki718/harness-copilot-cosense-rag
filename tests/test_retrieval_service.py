from fastapi.testclient import TestClient

from services.retrieval_service.app.main import app


def test_search_returns_answer_and_citations() -> None:
    client = TestClient(app)
    response = client.post("/search", json={"query": "仕様書の更新手順は？"})

    assert response.status_code == 200
    body = response.json()
    assert "answer" in body
    assert "citations" in body
    assert isinstance(body["citations"], list)


def test_search_returns_fallback_when_threshold_high() -> None:
    client = TestClient(app)
    response = client.post(
        "/search",
        json={"query": "仕様書の更新手順は？", "score_threshold": 0.99},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["citations"] == []
    assert "該当情報が見つからない" in body["answer"]

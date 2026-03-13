from fastapi.testclient import TestClient

from retrieval.app import main

app = main.app


def test_search_returns_answer_and_citations(monkeypatch) -> None:
    async def fake_generate_answer(
        query: str,
        docs: list[object],
        trace_id: str,
        max_tokens: int,
    ) -> str:
        _ = (query, docs, trace_id, max_tokens)
        return "モック回答"

    monkeypatch.setattr(main, "generate_answer", fake_generate_answer)

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

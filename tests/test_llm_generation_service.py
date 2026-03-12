from fastapi.testclient import TestClient

from services.llm_generation_service.app.main import app


def test_generate_returns_answer_in_mock_mode() -> None:
    client = TestClient(app)
    response = client.post(
        "/generate",
        json={
            "query": "更新手順は？",
            "contexts": [
                {
                    "content": "README の更新は pull request で行います。",
                    "title": "運用ガイド",
                    "url": "https://scrapbox.io/example/ops",
                }
            ],
            "max_tokens": 128,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "answer" in body
    assert isinstance(body["answer"], str)
    assert body["answer"]

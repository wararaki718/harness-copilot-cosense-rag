from fastapi.testclient import TestClient

from llm_generation.app import main

app = main.app


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


def test_generate_returns_fallback_when_contexts_empty() -> None:
    client = TestClient(app)
    response = client.post(
        "/generate",
        json={"query": "情報はありますか？", "contexts": [], "max_tokens": 128},
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "該当情報が見つからないため、回答できませんでした。"


def test_build_prompt_contains_context_first_policy() -> None:
    prompt = main.build_prompt(
        query="更新手順は？",
        contexts=[
            {
                "content": "README の更新は pull request で行う。",
                "title": "運用ガイド",
                "url": "https://scrapbox.io/example/ops",
            }
        ],
    )

    assert "コンテキストを優先" in prompt
    assert "更新手順は？" in prompt
    assert "運用ガイド" in prompt
    assert "https://scrapbox.io/example/ops" in prompt


def test_generate_uses_ollama_when_mode_is_ollama(monkeypatch) -> None:
    async def fake_generate_with_ollama(prompt: str, max_tokens: int, trace_id: str) -> str:
        _ = (prompt, max_tokens, trace_id)
        return "Ollama回答"

    monkeypatch.setattr(main.settings, "mode", "ollama")
    monkeypatch.setattr(main, "generate_with_ollama", fake_generate_with_ollama)

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
            "max_tokens": 64,
        },
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "Ollama回答"

    monkeypatch.setattr(main.settings, "mode", "mock")

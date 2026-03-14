import asyncio
import pytest

from batch_ingestion.app import main
from batch_ingestion.app.schemas import ManualIngestOptions


def test_split_text_with_overlap() -> None:
    chunks = main.split_text("abcdefghijklmnopqrstuvwxyz", chunk_size=10, chunk_overlap=2)

    assert len(chunks) == 4
    assert chunks[0] == "abcdefghij"
    assert chunks[1].startswith("ijkl")


def test_run_manual_ingestion_success(monkeypatch) -> None:
    async def fake_fetch_pages_from_cosense(project: str, limit_pages: int, trace_id: str):
        _ = (project, limit_pages, trace_id)
        return [
            {
                "id": "page-1",
                "title": "ページ1",
                "url": "https://scrapbox.io/example/page-1",
                "updated_at": "2026-03-14T00:00:00Z",
                "content": "RAG のバッチ取り込みを実行します。",
            }
        ]

    async def fake_embed_texts(texts: list[str], trace_id: str):
        _ = (texts, trace_id)
        return [{"token_rag": 1.0}]

    def fake_upsert_document(document: dict, trace_id: str) -> bool:
        _ = (document, trace_id)
        return True

    monkeypatch.setattr(main, "fetch_pages_from_cosense", fake_fetch_pages_from_cosense)
    monkeypatch.setattr(main, "embed_texts", fake_embed_texts)
    monkeypatch.setattr(main, "upsert_document", fake_upsert_document)

    response = asyncio.run(main.run_manual_ingestion(ManualIngestOptions(project="example", limit_pages=10)))

    assert response.success_count == 1
    assert response.failure_count == 0
    assert response.processed_pages == 1
    assert response.processed_chunks == 1


def test_run_manual_ingestion_requires_project() -> None:
    with pytest.raises(ValueError):
        asyncio.run(main.run_manual_ingestion(ManualIngestOptions(limit_pages=1)))

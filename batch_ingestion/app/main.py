import argparse
import asyncio
import logging
import time
import uuid
from collections.abc import Sequence
from typing import Any

import httpx

try:
    from elasticsearch import Elasticsearch
except ImportError:
    Elasticsearch = None

from .config import settings
from .schemas import ManualIngestOptions, ManualIngestResponse

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)
_es_client: Any | None = None


def log_event(**kwargs):
    logger.info(kwargs)


def split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    trimmed = text.strip()
    if not trimmed:
        return []

    if chunk_overlap >= chunk_size:
        chunk_overlap = max(0, chunk_size - 1)

    chunks: list[str] = []
    step = chunk_size - chunk_overlap
    start = 0
    length = len(trimmed)
    while start < length:
        end = min(start + chunk_size, length)
        chunk = trimmed[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += step
    return chunks


def normalize_page_content(raw_page: dict[str, Any]) -> str:
    if isinstance(raw_page.get("content"), str):
        return raw_page["content"]

    descriptions = raw_page.get("descriptions")
    if isinstance(descriptions, Sequence) and not isinstance(descriptions, (str, bytes)):
        return "\n".join([str(line) for line in descriptions if str(line).strip()])

    return ""


def get_elasticsearch_client() -> Any | None:
    global _es_client
    if _es_client is not None:
        return _es_client
    if Elasticsearch is None:
        return None

    _es_client = Elasticsearch(settings.elasticsearch_url, request_timeout=settings.elasticsearch_timeout_seconds)
    return _es_client


async def fetch_pages_from_cosense(project: str, limit_pages: int, trace_id: str) -> list[dict[str, Any]]:
    dependency = "cosense-api"
    url = f"{settings.cosense_base_url}/{project}"
    params = {"limit": limit_pages}
    headers: dict[str, str] = {"x-trace-id": trace_id}
    if settings.cosense_access_token:
        headers["Authorization"] = f"Bearer {settings.cosense_access_token}"

    for attempt in range(settings.retry_count + 1):
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=settings.cosense_timeout_seconds) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
            payload = response.json()
            raw_pages = payload.get("pages", [])
            pages: list[dict[str, Any]] = []
            for raw_page in raw_pages:
                title = str(raw_page.get("title", ""))
                page_url = raw_page.get("url") or f"https://scrapbox.io/{project}/{title}"
                page_id = str(raw_page.get("id") or title)
                pages.append(
                    {
                        "id": page_id,
                        "title": title,
                        "url": page_url,
                        "updated_at": str(raw_page.get("updated") or raw_page.get("updated_at") or ""),
                        "content": normalize_page_content(raw_page),
                    }
                )

            duration_ms = int((time.perf_counter() - start) * 1000)
            log_event(
                trace_id=trace_id,
                service=settings.service_name,
                operation="fetch_pages",
                dependency=dependency,
                status_code=response.status_code,
                duration_ms=duration_ms,
                retry_count=attempt,
                page_count=len(pages),
            )
            return pages
        except Exception as error:
            duration_ms = int((time.perf_counter() - start) * 1000)
            log_event(
                trace_id=trace_id,
                service=settings.service_name,
                operation="fetch_pages",
                dependency=dependency,
                status_code=502,
                duration_ms=duration_ms,
                retry_count=attempt,
                error_type=type(error).__name__,
                error_message=str(error),
            )
            if attempt >= settings.retry_count:
                raise RuntimeError("Cosense API call failed") from error

    raise RuntimeError("Cosense API call failed")


async def embed_texts(texts: list[str], trace_id: str) -> list[dict[str, float]]:
    dependency = "embedding-api"
    payload = {"texts": texts, "type": "document"}

    for attempt in range(settings.retry_count + 1):
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=settings.embedding_timeout_seconds) as client:
                response = await client.post(
                    f"{settings.embedding_api_base_url}/embed",
                    json=payload,
                    headers={"x-trace-id": trace_id},
                )
                response.raise_for_status()
            body = response.json()
            vectors = body.get("vectors", [])

            duration_ms = int((time.perf_counter() - start) * 1000)
            log_event(
                trace_id=trace_id,
                service=settings.service_name,
                operation="embed_documents",
                dependency=dependency,
                status_code=response.status_code,
                duration_ms=duration_ms,
                retry_count=attempt,
                batch_size=len(texts),
            )
            return vectors
        except Exception as error:
            duration_ms = int((time.perf_counter() - start) * 1000)
            log_event(
                trace_id=trace_id,
                service=settings.service_name,
                operation="embed_documents",
                dependency=dependency,
                status_code=502,
                duration_ms=duration_ms,
                retry_count=attempt,
                error_type=type(error).__name__,
                error_message=str(error),
            )
            if attempt >= settings.retry_count:
                return []

    return []


def upsert_document(document: dict[str, Any], trace_id: str) -> bool:
    dependency = "elasticsearch"
    start = time.perf_counter()
    try:
        client = get_elasticsearch_client()
        if client is None:
            raise RuntimeError("Elasticsearch client is not available")

        client.index(index=settings.elasticsearch_index, id=document["doc_id"], document=document)
        duration_ms = int((time.perf_counter() - start) * 1000)
        log_event(
            trace_id=trace_id,
            service=settings.service_name,
            operation="upsert_document",
            dependency=dependency,
            status_code=200,
            duration_ms=duration_ms,
            retry_count=0,
        )
        return True
    except Exception as error:
        duration_ms = int((time.perf_counter() - start) * 1000)
        log_event(
            trace_id=trace_id,
            service=settings.service_name,
            operation="upsert_document",
            dependency=dependency,
            status_code=502,
            duration_ms=duration_ms,
            retry_count=0,
            error_type=type(error).__name__,
            error_message=str(error),
        )
        return False


async def run_manual_ingestion(options: ManualIngestOptions, trace_id: str | None = None) -> ManualIngestResponse:
    execution_trace_id = trace_id or str(uuid.uuid4())
    project = options.project or settings.cosense_project
    if not project:
        raise ValueError("project is required")

    start = time.perf_counter()
    success_count = 0
    failure_count = 0
    processed_chunks = 0

    pages = await fetch_pages_from_cosense(project=project, limit_pages=options.limit_pages, trace_id=execution_trace_id)

    for page in pages:
        chunks = split_text(page.get("content", ""), settings.chunk_size, settings.chunk_overlap)
        if not chunks:
            continue

        vectors = await embed_texts(chunks, execution_trace_id)
        processed_chunks += len(chunks)

        for index, chunk in enumerate(chunks):
            vector = vectors[index] if index < len(vectors) else {}
            document = {
                "doc_id": f"cosense:page:{page['id']}#chunk:{index}",
                "title": page["title"],
                "url": page["url"],
                "content": chunk,
                "updated_at": page.get("updated_at", ""),
                "sparse_vector": vector,
            }
            if upsert_document(document, execution_trace_id):
                success_count += 1
            else:
                failure_count += 1

    duration_ms = int((time.perf_counter() - start) * 1000)
    log_event(
        trace_id=execution_trace_id,
        service=settings.service_name,
        operation="manual_ingest",
        dependency="batch-ingestion",
        status_code=0,
        duration_ms=duration_ms,
        retry_count=0,
        success_count=success_count,
        failure_count=failure_count,
    )

    return ManualIngestResponse(
        success_count=success_count,
        failure_count=failure_count,
        processed_pages=len(pages),
        processed_chunks=processed_chunks,
        duration_ms=duration_ms,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Cosense batch ingestion once")
    parser.add_argument("--project", type=str, default=None, help="Cosense project name")
    parser.add_argument(
        "--limit-pages",
        type=int,
        default=settings.default_limit_pages,
        help="Maximum number of pages to ingest",
    )
    return parser.parse_args()


async def _run_from_cli() -> int:
    args = parse_args()
    try:
        options = ManualIngestOptions(project=args.project, limit_pages=args.limit_pages)
        result = await run_manual_ingestion(options=options)
        print(result.model_dump_json(ensure_ascii=False))
        return 0
    except ValueError as error:
        logger.error({"service": settings.service_name, "error": str(error)})
        return 2
    except Exception as error:
        logger.error({"service": settings.service_name, "error_type": type(error).__name__, "error": str(error)})
        return 1


def main() -> int:
    return asyncio.run(_run_from_cli())


if __name__ == "__main__":
    raise SystemExit(main())

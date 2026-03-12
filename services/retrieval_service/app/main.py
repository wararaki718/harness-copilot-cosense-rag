import logging
import time
import uuid
from collections import OrderedDict

import httpx
from fastapi import FastAPI, HTTPException, Request

from .config import settings
from .schemas import (
    EmbeddingRequest,
    EmbeddingResponse,
    LlmGenerateRequest,
    LlmGenerateResponse,
    RetrievedDocument,
    SearchRequest,
    SearchResponse,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Retrieval Service", version="0.1.0")


@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    trace_id = request.headers.get("x-trace-id", str(uuid.uuid4()))
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers["x-trace-id"] = trace_id
    return response


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}


def log_event(**kwargs):
    logger.info(kwargs)


async def embed_query(query: str, trace_id: str) -> dict[str, float]:
    payload = EmbeddingRequest(texts=[query], type="query").model_dump()
    start = time.perf_counter()
    dependency = "embedding-api"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{settings.embedding_api_base_url}/embed", json=payload)
            response.raise_for_status()
        data = EmbeddingResponse.model_validate(response.json())
        duration_ms = int((time.perf_counter() - start) * 1000)
        log_event(
            trace_id=trace_id,
            service=settings.service_name,
            operation="embed_query",
            dependency=dependency,
            status_code=response.status_code,
            duration_ms=duration_ms,
            retry_count=0,
        )
        return data.vectors[0] if data.vectors else {}
    except Exception as error:
        duration_ms = int((time.perf_counter() - start) * 1000)
        log_event(
            trace_id=trace_id,
            service=settings.service_name,
            operation="embed_query",
            dependency=dependency,
            status_code=502,
            duration_ms=duration_ms,
            retry_count=0,
            error_type=type(error).__name__,
            error_message=str(error),
        )
        return build_mock_sparse_vector(query)


def build_mock_sparse_vector(text: str) -> dict[str, float]:
    tokens = [token.strip().lower() for token in text.split() if token.strip()]
    if not tokens:
        return {}
    return {f"token_{token}": 1.0 / (index + 1) for index, token in enumerate(tokens[:32])}


def retrieve_documents(_sparse_vector: dict[str, float], top_k: int) -> list[RetrievedDocument]:
    samples = [
        RetrievedDocument(
            title="RAG運用ガイド",
            url="https://scrapbox.io/example/rag-ops",
            content="障害時はトレースIDを使って依存APIエラーを特定します。",
            score=0.72,
        ),
        RetrievedDocument(
            title="RAGアーキテクチャ",
            url="https://scrapbox.io/example/rag-architecture",
            content="Retrieval Service は LLM Generation API を呼び出して回答を得ます。",
            score=0.64,
        ),
        RetrievedDocument(
            title="RAGアーキテクチャ",
            url="https://scrapbox.io/example/rag-architecture",
            content="citation は検索順位順で返却し、重複排除します。",
            score=0.61,
        ),
    ]
    return samples[:top_k]


def dedupe_citations(docs: list[RetrievedDocument]) -> list[dict[str, str]]:
    ordered = OrderedDict()
    for doc in docs:
        key = (doc.url, doc.title)
        if key not in ordered:
            ordered[key] = {"title": doc.title, "url": doc.url}
    return list(ordered.values())


async def generate_answer(
    query: str,
    docs: list[RetrievedDocument],
    trace_id: str,
    max_tokens: int,
) -> str:
    payload = LlmGenerateRequest(
        query=query,
        contexts=[doc.model_dump(include={"title", "url", "content"}) for doc in docs],
        max_tokens=max_tokens,
    ).model_dump()
    dependency = "llm-generation-api"

    for attempt in range(settings.llm_retry_count + 1):
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
                response = await client.post(
                    f"{settings.llm_generation_api_base_url}/generate",
                    json=payload,
                    headers={"x-trace-id": trace_id},
                )
                response.raise_for_status()
            data = LlmGenerateResponse.model_validate(response.json())
            duration_ms = int((time.perf_counter() - start) * 1000)
            log_event(
                trace_id=trace_id,
                service=settings.service_name,
                operation="generate_answer",
                dependency=dependency,
                status_code=response.status_code,
                duration_ms=duration_ms,
                retry_count=attempt,
            )
            return data.answer
        except Exception as error:
            duration_ms = int((time.perf_counter() - start) * 1000)
            log_event(
                trace_id=trace_id,
                service=settings.service_name,
                operation="generate_answer",
                dependency=dependency,
                status_code=502,
                duration_ms=duration_ms,
                retry_count=attempt,
                error_type=type(error).__name__,
                error_message=str(error),
            )
            if attempt >= settings.llm_retry_count:
                raise HTTPException(status_code=502, detail="LLM generation API call failed") from error

    raise HTTPException(status_code=502, detail="LLM generation API call failed")


@app.post("/search", response_model=SearchResponse)
async def search(payload: SearchRequest, request: Request) -> SearchResponse:
    trace_id: str = request.state.trace_id
    top_k = payload.top_k or settings.default_top_k
    threshold = payload.score_threshold if payload.score_threshold is not None else settings.default_score_threshold

    sparse_vector = await embed_query(payload.query, trace_id)
    candidates = retrieve_documents(sparse_vector, top_k)
    filtered = [doc for doc in candidates if doc.score >= threshold]

    if not filtered:
        return SearchResponse(answer=settings.fallback_message, citations=[])

    answer = await generate_answer(
        query=payload.query,
        docs=filtered,
        trace_id=trace_id,
        max_tokens=settings.llm_max_tokens,
    )
    citations = dedupe_citations(filtered)
    return SearchResponse(answer=answer, citations=citations)

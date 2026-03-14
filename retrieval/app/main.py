import logging
import time
import uuid
from collections import OrderedDict
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

try:
    from elasticsearch import Elasticsearch
except ImportError:  # pragma: no cover - exercised only when optional dependency is absent
    Elasticsearch = None  # type: ignore[assignment]

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
_es_client: Any | None = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


def get_elasticsearch_client() -> Any | None:
    global _es_client
    if _es_client is not None:
        return _es_client
    if Elasticsearch is None:
        return None

    _es_client = Elasticsearch(settings.elasticsearch_url, request_timeout=settings.elasticsearch_timeout_seconds)
    return _es_client


async def embed_query(query: str, trace_id: str) -> dict[str, float]:
    payload = EmbeddingRequest(texts=[query], type="query").model_dump()
    dependency = "embedding-api"
    for attempt in range(settings.embedding_retry_count + 1):
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=settings.embedding_timeout_seconds) as client:
                response = await client.post(
                    f"{settings.embedding_api_base_url}/embed",
                    json=payload,
                    headers={"x-trace-id": trace_id},
                )
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
                retry_count=attempt,
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
                retry_count=attempt,
                error_type=type(error).__name__,
                error_message=str(error),
            )
            if attempt >= settings.embedding_retry_count:
                return {}

    return {}


def build_sparse_vector_search_query(sparse_vector: dict[str, float], top_k: int) -> dict[str, Any]:
    return {
        "size": top_k,
        "query": {
            "sparse_vector": {
                "field": "sparse_vector",
                "query_vector": sparse_vector,
            }
        },
        "_source": ["title", "url", "content"],
    }


def retrieve_documents_from_elasticsearch(
    sparse_vector: dict[str, float],
    top_k: int,
    trace_id: str,
) -> list[RetrievedDocument]:
    if not sparse_vector:
        return []

    dependency = "elasticsearch"
    start = time.perf_counter()
    try:
        client = get_elasticsearch_client()
        if client is None:
            raise RuntimeError("Elasticsearch client is not available")

        body = build_sparse_vector_search_query(sparse_vector=sparse_vector, top_k=top_k)
        response = client.search(index=settings.elasticsearch_index, body=body)
        duration_ms = int((time.perf_counter() - start) * 1000)

        hits = response.get("hits", {}).get("hits", [])
        documents = [
            RetrievedDocument(
                title=hit.get("_source", {}).get("title", ""),
                url=hit.get("_source", {}).get("url", ""),
                content=hit.get("_source", {}).get("content", ""),
                score=float(hit.get("_score", 0.0)),
            )
            for hit in hits
        ]

        log_event(
            trace_id=trace_id,
            service=settings.service_name,
            operation="retrieve_documents",
            dependency=dependency,
            status_code=200,
            duration_ms=duration_ms,
            retry_count=0,
            hit_count=len(documents),
        )
        return documents
    except Exception as error:
        duration_ms = int((time.perf_counter() - start) * 1000)
        log_event(
            trace_id=trace_id,
            service=settings.service_name,
            operation="retrieve_documents",
            dependency=dependency,
            status_code=502,
            duration_ms=duration_ms,
            retry_count=0,
            error_type=type(error).__name__,
            error_message=str(error),
        )
        return []


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
    candidates = retrieve_documents_from_elasticsearch(sparse_vector, top_k, trace_id)
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

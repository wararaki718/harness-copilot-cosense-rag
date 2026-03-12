import logging
import time
import uuid

import httpx
from fastapi import FastAPI, HTTPException, Request

from .config import settings
from .schemas import GenerateRequest, GenerateResponse

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="LLM Generation Service", version="0.1.0")


@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    trace_id = request.headers.get("x-trace-id", str(uuid.uuid4()))
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers["x-trace-id"] = trace_id
    return response


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name, "mode": settings.mode}


def log_event(**kwargs):
    logger.info(kwargs)


def build_prompt(query: str, contexts: list[dict[str, str]]) -> str:
    context_blocks = []
    for index, context in enumerate(contexts, start=1):
        context_blocks.append(
            f"[{index}] title={context['title']}\\nurl={context['url']}\\ncontent={context['content']}"
        )
    joined_contexts = "\\n\\n".join(context_blocks)
    return (
        "あなたはRAG回答アシスタントです。必ず与えられたコンテキストを優先して回答してください。"
        "コンテキストに根拠がない内容は推測せず、分からない場合はその旨を短く述べてください。\\n\\n"
        f"質問:\\n{query}\\n\\n"
        f"コンテキスト:\\n{joined_contexts}"
    )


def generate_mock_answer(query: str, contexts: list[dict[str, str]]) -> str:
    if not contexts:
        return "該当情報が見つからないため、回答できませんでした。"
    summary = contexts[0]["content"][:120]
    return f"質問『{query}』に対して、主要な根拠は『{summary}』です。"


async def generate_with_ollama(prompt: str, max_tokens: int, trace_id: str) -> str:
    start = time.perf_counter()
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": max_tokens},
    }

    try:
        async with httpx.AsyncClient(timeout=settings.ollama_timeout_seconds) as client:
            response = await client.post(f"{settings.ollama_base_url}/api/generate", json=payload)
            response.raise_for_status()
        data = response.json()
        answer = data.get("response", "").strip()
        duration_ms = int((time.perf_counter() - start) * 1000)
        log_event(
            trace_id=trace_id,
            service=settings.service_name,
            operation="ollama_generate",
            dependency="ollama",
            status_code=response.status_code,
            duration_ms=duration_ms,
            retry_count=0,
        )
        if not answer:
            raise HTTPException(status_code=502, detail="Ollama returned empty response")
        return answer
    except HTTPException:
        raise
    except Exception as error:
        duration_ms = int((time.perf_counter() - start) * 1000)
        log_event(
            trace_id=trace_id,
            service=settings.service_name,
            operation="ollama_generate",
            dependency="ollama",
            status_code=502,
            duration_ms=duration_ms,
            retry_count=0,
            error_type=type(error).__name__,
            error_message=str(error),
        )
        raise HTTPException(status_code=502, detail="Ollama API call failed") from error


@app.post("/generate", response_model=GenerateResponse)
async def generate(payload: GenerateRequest, request: Request) -> GenerateResponse:
    trace_id: str = request.state.trace_id
    contexts = [context.model_dump() for context in payload.contexts]

    if settings.mode == "mock":
        answer = generate_mock_answer(payload.query, contexts)
        return GenerateResponse(answer=answer)

    prompt = build_prompt(payload.query, contexts)
    answer = await generate_with_ollama(prompt, payload.max_tokens, trace_id)
    return GenerateResponse(answer=answer)

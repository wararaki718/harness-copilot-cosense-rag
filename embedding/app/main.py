import logging
import re
import uuid
from collections import Counter

from fastapi import FastAPI, Request

from .config import settings
from .schemas import EmbedRequest, EmbedResponse

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Embedding Service", version="0.1.0")


@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    trace_id = request.headers.get("x-trace-id", str(uuid.uuid4()))
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers["x-trace-id"] = trace_id
    return response


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name, "model": settings.model_name}


def normalize_text(text: str) -> str:
    normalized = text.strip().lower()
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def tokenize(text: str) -> list[str]:
    chunks = re.findall(r"[\w\-ぁ-んァ-ン一-龥]+", text)
    return [token for token in chunks if token]


def to_sparse_vector(text: str, max_tokens: int) -> dict[str, float]:
    normalized = normalize_text(text)
    tokens = tokenize(normalized)[:max_tokens]
    if not tokens:
        return {}

    counts = Counter(tokens)
    total = sum(counts.values())
    sorted_tokens = sorted(counts.items(), key=lambda item: (-item[1], item[0]))

    vector: dict[str, float] = {}
    for token, count in sorted_tokens:
        vector[f"token_{token}"] = round(count / total, 6)
    return vector


@app.post("/embed", response_model=EmbedResponse)
async def embed(payload: EmbedRequest, request: Request) -> EmbedResponse:
    trace_id: str = request.state.trace_id
    vectors = [to_sparse_vector(text, settings.max_tokens_per_text) for text in payload.texts]

    logger.info(
        {
            "trace_id": trace_id,
            "service": settings.service_name,
            "operation": "embed",
            "dependency": "local-model",
            "status_code": 200,
            "duration_ms": 0,
            "retry_count": 0,
            "input_type": payload.type,
            "batch_size": len(payload.texts),
        }
    )

    return EmbedResponse(vectors=vectors)

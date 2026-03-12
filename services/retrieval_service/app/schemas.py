from typing import Any

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int | None = Field(default=None, ge=1, le=50)
    score_threshold: float | None = Field(default=None, ge=0.0)


class Citation(BaseModel):
    title: str
    url: str


class SearchResponse(BaseModel):
    answer: str
    citations: list[Citation]


class EmbeddingRequest(BaseModel):
    texts: list[str]
    type: str = "query"


class EmbeddingResponse(BaseModel):
    vectors: list[dict[str, float]]


class RetrievedDocument(BaseModel):
    title: str
    url: str
    content: str
    score: float


class LlmGenerateRequest(BaseModel):
    query: str
    contexts: list[dict[str, Any]]
    max_tokens: int = 512


class LlmGenerateResponse(BaseModel):
    answer: str

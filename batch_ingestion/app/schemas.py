from pydantic import BaseModel, Field


class ManualIngestOptions(BaseModel):
    project: str | None = None
    limit_pages: int = Field(default=50, ge=1, le=500)


class ManualIngestResponse(BaseModel):
    success_count: int
    failure_count: int
    processed_pages: int
    processed_chunks: int
    duration_ms: int

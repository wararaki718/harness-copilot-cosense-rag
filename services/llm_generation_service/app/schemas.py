from pydantic import BaseModel, Field


class Context(BaseModel):
    content: str = Field(min_length=1)
    title: str
    url: str


class GenerateRequest(BaseModel):
    query: str = Field(min_length=1)
    contexts: list[Context]
    max_tokens: int = Field(default=512, ge=1, le=4096)


class GenerateResponse(BaseModel):
    answer: str

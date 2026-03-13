from typing import Literal

from pydantic import BaseModel, Field


class EmbedRequest(BaseModel):
    texts: list[str] = Field(min_length=1)
    type: Literal["document", "query"]


class EmbedResponse(BaseModel):
    vectors: list[dict[str, float]]

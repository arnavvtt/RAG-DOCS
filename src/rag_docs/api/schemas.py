from typing import List, Optional
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="User question")
    top_k: int = Field(4, ge=1, le=10, description="Number of chunks to retrieve")


class Source(BaseModel):
    ref: int
    filename: Optional[str] = None
    chunk_id: Optional[str] = None
    page: Optional[int] = None
    score: float


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[Source]


class HealthResponse(BaseModel):
    status: str
    chunks_indexed: int
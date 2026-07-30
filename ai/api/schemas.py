"""Pydantic modelleri — API istek/yanit semalari."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    session_id: str | None = None
    use_groq: bool = True


class SourceItem(BaseModel):
    id: int
    name: str


class RetrievedChunk(BaseModel):
    chunk_id: str
    product_id: int
    product_name: str
    field: str
    score: float
    source: str


class ChatResponse(BaseModel):
    answer: str
    source: str
    sources: list[SourceItem]
    retrieved_chunks: list[RetrievedChunk]
    session_id: str


class ProductMatch(BaseModel):
    id: int
    name: str
    category: str


class IdentifyResponse(BaseModel):
    model: str
    prompt_version: str
    plant_tr: str
    plant_en: str
    confidence: str
    note: str
    raw: str
    status: str
    message: str | None = None
    products: list[ProductMatch] = []


class SentimentBucket(BaseModel):
    count: int
    ratio: float


class SentimentDistribution(BaseModel):
    positive: SentimentBucket
    negative: SentimentBucket
    neutral: SentimentBucket
    total_comments: int


class SideEffectItem(BaseModel):
    effect: str
    count: int


class ReviewSummaryResponse(BaseModel):
    product: str | None = None
    sentiment_distribution: SentimentDistribution
    most_reported_side_effect: str | None = None
    side_effects: list[SideEffectItem]
    summary_text: str
    method: str

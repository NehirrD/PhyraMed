"""FastAPI REST katmani — chatbot, gorsel tanima, yorum ozeti."""

from pathlib import Path
import sys

from dotenv import load_dotenv

AI_DIR = Path(__file__).resolve().parents[1]
POC_DIR = AI_DIR / "poc"
sys.path.insert(0, str(POC_DIR))

load_dotenv(AI_DIR / ".env")

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .schemas import (
    ChatRequest,
    ChatResponse,
    IdentifyResponse,
    ReviewSummaryResponse,
    SourceItem,
    RetrievedChunk,
)
from memory import memory_store
from orchestrator import orchestrate
from product_db import get_product_by_id, load_products
from rag.indexer import build_index
from sentiment_summary import build_summary, enhance_with_groq, load_comments, summarize_by_product
from vision import identify_and_lookup

app = FastAPI(
    title="PhyraMed AI API",
    description="RAG chatbot, gorsel tanima ve yorum analizi servisleri",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    """Uygulama baslarken vektor indeksini olustur."""

    try:
        build_index()
    except Exception as exc:
        print(f"Indeks olusturma uyarisi: {exc}")


@app.get("/")
def root():
    return {"message": "PhyraMed AI API calisiyor", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """RAG + hafiza destekli chatbot."""

    result = orchestrate(
        request.question,
        session_id=request.session_id,
        use_groq=request.use_groq,
    )

    return ChatResponse(
        answer=result["answer"],
        source=result["source"],
        sources=[SourceItem(**s) for s in result["sources"]],
        retrieved_chunks=[RetrievedChunk(**c) for c in result["retrieved_chunks"]],
        session_id=result["session_id"],
    )


@app.delete("/api/chat/sessions/{session_id}")
def clear_session(session_id: str):
    memory_store.clear(session_id)
    return {"cleared": session_id}


@app.post("/api/identify", response_model=IdentifyResponse)
async def identify_plant(file: UploadFile = File(...)):
    """Bitki gorseli yukle ve tanima + urun eslestirme yap."""

    suffix = Path(file.filename or "image.jpg").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        raise HTTPException(status_code=400, detail="Desteklenmeyen gorsel formati")

    temp_dir = POC_DIR / "data" / "uploads"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / f"upload{suffix}"

    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Gorsel 20 MB limitini asiyor")

    temp_path.write_bytes(content)

    try:
        result = identify_and_lookup(temp_path, prompt_version="v3")
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    finally:
        temp_path.unlink(missing_ok=True)

    return IdentifyResponse(**result)


@app.get("/api/products/{product_id}/review-summary", response_model=ReviewSummaryResponse)
def review_summary(product_id: int, use_groq: bool = False):
    """Urun bazli yorum ozeti."""

    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Urun bulunamadi")

    all_comments = load_comments()
    comments = [c for c in all_comments if c.get("product") == product["name"]]

    if not comments:
        raise HTTPException(status_code=404, detail="Bu urun icin yorum bulunamadi")

    summary = build_summary(comments, product=product["name"])
    if use_groq:
        summary = enhance_with_groq(summary, comments)

    return ReviewSummaryResponse(**summary)


@app.get("/api/reviews/summary")
def all_review_summaries(use_groq: bool = False):
    """Tum urunler icin yorum ozetleri."""

    comments = load_comments()
    summaries = summarize_by_product(comments)

    if use_groq:
        for product, items in summarize_by_product(comments).items():
            product_comments = [c for c in comments if c.get("product") == product]
            summaries[product] = enhance_with_groq(items, product_comments)

    return summaries


@app.get("/api/products")
def list_products():
    """Mock urun listesi — backend entegrasyonu icin gecici."""

    return load_products()

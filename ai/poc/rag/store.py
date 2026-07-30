"""ChromaDB vektör deposu — ürün chunk'ları için kalıcı store."""

from pathlib import Path

import chromadb
from chromadb.config import Settings

COLLECTION_NAME = "phyrmed_products"
STORE_DIR = Path(__file__).resolve().parents[1] / "data" / "vector_store"


def get_collection():
    """Kalıcı Chroma koleksiyonunu döndürür."""

    STORE_DIR.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(STORE_DIR),
        settings=Settings(anonymized_telemetry=False),
    )

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

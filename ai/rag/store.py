"""PhyraMed RAG için kalıcı ChromaDB bağlantısı."""

import os
from functools import lru_cache
from pathlib import Path

import chromadb


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CHROMA_PATH = PROJECT_ROOT / ".chroma"

COLLECTION_NAME = os.getenv(
    "RAG_COLLECTION_NAME",
    "phyramed_products",
)


def get_chroma_path() -> Path:
    """Chroma verilerinin saklanacağı güvenli yerel yolu döndürür."""

    configured_path = os.getenv("RAG_CHROMA_PATH")

    if configured_path:
        return Path(configured_path).expanduser().resolve()

    return DEFAULT_CHROMA_PATH


@lru_cache(maxsize=1)
def get_chroma_client():
    """Tek bir kalıcı Chroma istemcisi oluşturur."""

    chroma_path = get_chroma_path()
    chroma_path.mkdir(parents=True, exist_ok=True)

    return chromadb.PersistentClient(
        path=str(chroma_path),
    )


@lru_cache(maxsize=1)
def get_product_collection():
    """PhyraMed ürün parçalarının tutulacağı koleksiyonu döndürür."""

    client = get_chroma_client()

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        configuration={
            "hnsw": {
                "space": "cosine",
            }
        },
    )

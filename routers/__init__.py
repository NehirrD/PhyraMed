from routers.category import router as category_router
from routers.interaction import router as interaction_router
from routers.product import router as product_router
from routers.risk import router as risk_router
from routers.search import router as search_router
from routers.source import router as source_router
from routers.comment import router as comment_router
from routers.analysis import router as analysis_router

__all__ = [
    "category_router", "interaction_router", "product_router",
    "risk_router", "search_router", "source_router",
    "comment_router", "analysis_router",
]
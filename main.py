from fastapi import FastAPI
from database import Base, engine
from routers.category import router as category_router
from routers.interaction import router as interaction_router
from routers.product import router as product_router
from routers.risk import router as risk_router
from routers.search import router as search_router
from routers.source import router as source_router
app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(category_router)
app.include_router(interaction_router)
app.include_router(product_router)
app.include_router(risk_router)
app.include_router(search_router)
app.include_router(source_router)

@app.get("/")
def root():
    return {"message": "PhyraMed API çalışıyor"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routers import (
    category_router,
    interaction_router,
    product_router,
    risk_router,
    search_router,
    source_router,
    comment_router,
    analysis_router,
    chat_router,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(category_router)
app.include_router(interaction_router)
app.include_router(product_router)
app.include_router(risk_router)
app.include_router(search_router)
app.include_router(source_router)
app.include_router(comment_router)
app.include_router(analysis_router)
app.include_router(chat_router)


@app.get("/")
def root():
    return {"message": "PhyraMed API çalışıyor"}
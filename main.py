from fastapi import FastAPI
from database import Base, engine
from routers import category_router, interaction_router, product_router, risk_router, search_router, source_router, comment_router, analysis_router, chat_router
app = FastAPI()

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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from database import Base, engine
from routers import category, product, risk ,source
import models
app = FastAPI()
app.include_router(category.router)
app.include_router(product.router)
app.include_router(risk.router)
app.include_router(source.router)

import models.category
import models.product
import models.risk
import models.interaction
import models.source

Base.metadata.create_all(bind=engine)

#routerlar eklenecek!
@app.get("/")
def root():
    return {"message": "PhyraMed API çalışıyor"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"], # Frontend portun
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

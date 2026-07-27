from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from database import Base, engine
from routers import category, product, risk ,source
from routers import analysis
from routers import comment

from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

import models
app = FastAPI()
@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend())
app.include_router(category.router)
app.include_router(product.router)
app.include_router(risk.router)
app.include_router(source.router)
app.include_router(analysis.router)
app.include_router(comment.router)

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

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)
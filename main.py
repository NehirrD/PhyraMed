from fastapi import FastAPI
from database import Base, engine
from routers import category, product
import models
app = FastAPI()
app.include_router(category.router)
app.include_router(product.router)

import models.category
import models.product
import models.risk
import models.interaction
import models.source

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "PhyraMed API çalışıyor"}

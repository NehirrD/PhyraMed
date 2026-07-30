from fastapi import FastAPI
from database import Base, engine
from routers import category, interaction, product, risk, search, source, comment, analysis, chat

app = FastAPI(title="PhyraMed API", description="Bitkisel takviye ürünleri platformu")

# Veritabanı bağlantısı varsa tabloları oluştur, yoksa hata verme
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Veritabanı bağlantı hatası (geçici yoksayıldı): {e}")

app.include_router(category.router)
app.include_router(interaction.router)
app.include_router(product.router)
app.include_router(risk.router)
app.include_router(search.router)
app.include_router(source.router)
app.include_router(comment.router)
app.include_router(analysis.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"message": "PhyraMed API çalışıyor"}
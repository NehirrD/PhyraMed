from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from collections import Counter
import re
from database import get_db
from models.product import Product
from models.comment import Comment
from ai.sentiment import analyze_product_comments

router = APIRouter(prefix="/analysis", tags=["Analysis"])

STOP_WORDS = {"ve", "ile", "veya", "ama", "fakat", "için", "gibi", "kadar", "göre", "çok", "bir", "bu", "şu", "o", "da", "de", "mı", "mi", "daha", "en", "var", "yok"}

@router.get("/comments/{product_id}")
async def analyze_product_comments(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")

    comments = db.query(Comment).filter(Comment.product_id == product_id).all()
    total_comments = len(comments)

    if total_comments == 0:
        return {"product_name": product.name, "total_comments": 0, "message": "Yorum bulunmuyor."}

    positive = sum(1 for c in comments if c.rating >= 4)
    neutral = sum(1 for c in comments if c.rating == 3)
    negative = sum(1 for c in comments if c.rating <= 2)

    all_text = " ".join([c.text.lower() for c in comments])
    words = re.findall(r'\b[a-zçğıöşü]+\b', all_text)
    filtered_words = [w for w in words if w not in STOP_WORDS and len(w) > 2]

    word_counts = Counter(filtered_words)
    top_keywords = [{"keyword": word, "count": count} for word, count in word_counts.most_common(5)]

    return {
        "product_name": product.name,
        "total_comments": total_comments,
        "sentiment_percentages": {
            "positive": round((positive / total_comments) * 100),
            "neutral": round((neutral / total_comments) * 100),
            "negative": round((negative / total_comments) * 100)
        },
        "top_keywords": top_keywords
    }

@router.get("/comments/{product_id}/deep")
async def analyze_product_comments_deep(product_id: int, use_groq: bool = False, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")

    comments = db.query(Comment).filter(Comment.product_id == product_id).all()
    result = analyze_product_comments(comments, use_groq=use_groq)
    result["product_name"] = product.name
    return result
import os
import sys
import json
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from collections import Counter # NEW: Import Counter for easy counting

from services import gemini_service
from models.chat_models import ChatRequest
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="StilDöngüsü API")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    gemini_service.configure_gemini(API_KEY)

with open('products.json', 'r', encoding='utf-8') as f:
    products_db = json.load(f)

# NEW: In-memory database to store return reasons (intents)
# In a real app, this would be a proper database (e.g., SQLite, PostgreSQL).
return_intents_db = [] 

@app.post("/api/analyze-style")
async def analyze_style_api(file: UploadFile = File(...)):
    if not API_KEY:
         raise HTTPException(status_code=500, detail="Sunucu yapılandırma hatası: Gemini API anahtarı bulunamadı.")
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Lütfen bir resim dosyası yükleyin.")

    try:
        image_bytes = await file.read()
        analysis_data = gemini_service.analyze_image_style(image_bytes)
        matched_products = gemini_service.find_matching_products(analysis_data, products_db)
        style_advice_data = gemini_service.get_style_advice(
            analysis_data.get('item_description'),
            matched_products 
        )
        return {
            "image_analysis": analysis_data,
            "style_advice": style_advice_data,
            "matched_products": matched_products
        }
    except Exception as e:
        print(f"Sunucu Hatası: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"Analiz sırasında bir sunucu hatası oluştu: {str(e)}")


@app.post("/api/chat")
async def chat_api(chat_request: ChatRequest):
    if not API_KEY:
         raise HTTPException(status_code=500, detail="Sunucu yapılandırma hatası: Gemini API anahtarı bulunamadı.")
    try:
        reply_data = gemini_service.get_chatbot_reply(chat_request.message)
        
        # NEW: Store the detected intent for analytics
        detected_intent = reply_data.get("detected_intent")
        if detected_intent:
            return_intents_db.append(detected_intent)
            print(f"INFO: Intent '{detected_intent}' stored. Total returns: {len(return_intents_db)}")

        return reply_data
    except Exception as e:
        print(f"Chatbot Sunucu Hatası: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail="Chatbot servisinde bir hata oluştu.")

# NEW: Analytics endpoint for the Seller Dashboard
@app.get("/api/return-analytics")
async def get_return_analytics():
    if not return_intents_db:
        return {"total_returns": 0, "reasons": []}

    total_returns = len(return_intents_db)
    intent_counts = Counter(return_intents_db)

    reasons_data = []
    for intent, count in intent_counts.items():
        reasons_data.append({
            "intent": intent,
            "count": count,
            "percentage": round((count / total_returns) * 100, 1)
        })
    
    # Sort by percentage descending
    reasons_data.sort(key=lambda x: x['percentage'], reverse=True)

    return {
        "total_returns": total_returns,
        "reasons": reasons_data
    }
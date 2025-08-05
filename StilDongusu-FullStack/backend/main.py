import os
import sys
import json
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

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
        return reply_data
    except Exception as e:
        print(f"Chatbot Sunucu Hatası: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail="Chatbot servisinde bir hata oluştu.")
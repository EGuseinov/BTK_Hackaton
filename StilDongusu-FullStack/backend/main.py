# main.py

import os
import sys
import json
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from collections import Counter, defaultdict
from typing import List

from services import gemini_service
from models.chat_models import ChatRequest, VisualComboRequest # VisualComboRequest'i ekleyeceğiz
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="StilDöngüsü API")

# ... (CORS ayarları aynı kalır) ...
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

# GÜNCELLENDİ: İade veritabanı artık daha fazla bilgi tutuyor
return_intents_db = [] 

@app.post("/api/analyze-style")
async def analyze_style_api(file: UploadFile = File(...)):
    # ... (Bu endpoint değişmedi) ...
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
        return { "image_analysis": analysis_data, "style_advice": style_advice_data, "matched_products": matched_products }
    except Exception as e:
        print(f"Sunucu Hatası: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"Analiz sırasında bir sunucu hatası oluştu: {str(e)}")


@app.post("/api/chat")
async def chat_api(chat_request: ChatRequest):
    # GÜNCELLENDİ: Gelen isteği ve sonucu logluyor/kaydediyor
    if not API_KEY:
         raise HTTPException(status_code=500, detail="Sunucu yapılandırma hatası.")
    try:
        reply_data = gemini_service.get_chatbot_reply(chat_request.message)
        
        detected_intent = reply_data.get("detected_intent")
        if detected_intent:
            return_intents_db.append({
                "product_name": chat_request.product,
                "intent": detected_intent,
                "message": chat_request.message
            })
            print(f"INFO: Intent '{detected_intent}' for product '{chat_request.product}' stored. DB size: {len(return_intents_db)}")

        return reply_data
    except Exception as e:
        print(f"Chatbot Sunucu Hatası: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail="Chatbot servisinde bir hata oluştu.")


# --- YENİ ENDPOINT'LER ---

@app.post("/api/create-style-profile")
async def create_style_profile_api(files: List[UploadFile] = File(...)):
    """Birden fazla resim alarak kullanıcının stil profilini oluşturur."""
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Sunucu yapılandırma hatası.")
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Lütfen en az 2 resim yükleyin.")

    image_bytes_list = []
    for file in files:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Lütfen sadece resim dosyaları yükleyin.")
        image_bytes_list.append(await file.read())
    
    try:
        profile_data = gemini_service.create_style_profile(image_bytes_list)
        return profile_data
    except Exception as e:
        print(f"Stil Profili Hatası: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"Stil profili oluşturulurken bir hata oluştu: {e}")


@app.post("/api/generate-visual-combo")
async def generate_visual_combo_api(request: VisualComboRequest):
    """Verilen parçalarla bir kombin görselinin metinsel betimlemesini oluşturur."""
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Sunucu yapılandırma hatası.")
    try:
        combo_description = gemini_service.generate_visual_combo(
            main_item=request.main_item,
            matched_items=request.matched_items
        )
        return combo_description
    except Exception as e:
        print(f"Görsel Kombin Hatası: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"Kombin görselleştirilirken bir hata oluştu: {e}")


# GÜNCELLENDİ: Satıcı Analitikleri artık çok daha akıllı
@app.get("/api/return-analytics")
async def get_return_analytics():
    if not return_intents_db:
        return {"total_returns": 0, "product_analysis": []}

    # Ürünlere göre iadeleri grupla
    returns_by_product = defaultdict(list)
    for an_intent in return_intents_db:
        returns_by_product[an_intent["product_name"]].append(an_intent)
    
    product_analysis = []
    for product_name, returns in returns_by_product.items():
        total_product_returns = len(returns)
        intents_for_product = [r["intent"] for r in returns]
        intent_counts = Counter(intents_for_product)
        
        reasons_summary = []
        for intent, count in intent_counts.items():
            reasons_summary.append({
                "intent": intent,
                "count": count,
                "percentage": round((count / total_product_returns) * 100, 1)
            })

        # Gemini'den stratejik tavsiye al
        all_messages = [r["message"] for r in returns]
        try:
            strategic_advice = gemini_service.get_strategic_return_advice(all_messages)
        except Exception as e:
            print(f"Stratejik Tavsiye Hatası: {e}")
            strategic_advice = {
                "common_theme": "Analiz sırasında bir hata oluştu.",
                "actionable_advice": "Lütfen iade mesajlarını manuel olarak kontrol edin."
            }

        product_analysis.append({
            "product_name": product_name,
            "total_returns": total_product_returns,
            "reasons": sorted(reasons_summary, key=lambda x: x['percentage'], reverse=True),
            "strategic_advice": strategic_advice
        })

    return {
        "total_returns": len(return_intents_db),
        "product_analysis": sorted(product_analysis, key=lambda x: x['total_returns'], reverse=True)
    }
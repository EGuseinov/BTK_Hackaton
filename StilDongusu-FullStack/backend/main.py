import os
import sys
import json
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from collections import Counter, defaultdict
from typing import List

from services import gemini_service
from models.chat_models import ChatRequest, VisualComboRequest, FitScoreRequest, EventStylistRequest
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

return_intents_db = [] 

@app.post("/api/analyze-style")
async def analyze_style_api(file: UploadFile = File(...)):
    if not API_KEY: raise HTTPException(status_code=500, detail="Sunucu yapılandırma hatası.")
    if not file.content_type.startswith("image/"): raise HTTPException(status_code=400, detail="Lütfen bir resim dosyası yükleyin.")
    try:
        image_bytes = await file.read()
        analysis_data = gemini_service.analyze_image_style(image_bytes)
        matched_products = gemini_service.find_matching_products(analysis_data, products_db)
        style_advice_data = gemini_service.get_style_advice(analysis_data.get('item_description'), matched_products)
        return { "image_analysis": analysis_data, "style_advice": style_advice_data, "matched_products": matched_products }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analiz sırasında hata: {str(e)}")

@app.post("/api/chat")
async def chat_api(chat_request: ChatRequest):
    if not API_KEY: raise HTTPException(status_code=500, detail="Sunucu yapılandırma hatası.")
    try:
        reply_data = gemini_service.get_chatbot_reply(chat_request.message)
        if reply_data.get("detected_intent"):
            return_intents_db.append({"product_name": chat_request.product, "intent": reply_data["detected_intent"], "message": chat_request.message})
        return reply_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot hatası: {str(e)}")

@app.post("/api/create-style-profile")
async def create_style_profile_api(files: List[UploadFile] = File(...)):
    if not API_KEY: raise HTTPException(status_code=500, detail="Sunucu yapılandırma hatası.")
    if len(files) < 2: raise HTTPException(status_code=400, detail="En az 2 resim yükleyin.")
    image_bytes_list = [await file.read() for file in files if file.content_type.startswith("image/")]
    if len(image_bytes_list) != len(files): raise HTTPException(status_code=400, detail="Lütfen sadece resim dosyaları yükleyin.")
    try:
        return await app.loop.run_in_executor(None, gemini_service.create_style_profile, image_bytes_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stil profili oluşturma hatası: {str(e)}")

@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product: raise HTTPException(status_code=404, detail="Ürün bulunamadı.")
    return product

@app.post("/api/fit-score")
async def get_fit_score_api(request: FitScoreRequest):
    if not API_KEY: raise HTTPException(status_code=500, detail="Sunucu yapılandırma hatası.")
    product = next((p for p in products_db if p["id"] == request.product_id), None)
    if not product: raise HTTPException(status_code=404, detail="Ürün bulunamadı.")
    try:
        return gemini_service.get_fit_score(request.user_body_type, product)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fit Puanı oluşturma hatası: {str(e)}")

# main.py dosyasında, sadece bu fonksiyonu güncelleyin.

@app.post("/api/event-stylist")
async def event_stylist_api(request: EventStylistRequest):
    """Kullanıcının isteğine göre kombin önerileri sunar ve ürün detaylarını ekler."""
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Sunucu yapılandırma hatası.")
    try:
        # Adım 1: Gemini'den metin tabanlı kombin önerilerini al
        combinations_from_gemini = gemini_service.get_event_style_combinations(request.user_request, products_db)

        # Adım 2: Gelen isimleri tam ürün objeleriyle zenginleştir
        enriched_combinations = []
        for combo in combinations_from_gemini.get("combinations", []):
            enriched_items = []
            for item_name in combo.get("items", []):
                # Veritabanında tam ürün objesini bul
                product_obj = next((p for p in products_db if p["name"].strip().lower() == item_name.strip().lower()), None)
                if product_obj:
                    enriched_items.append(product_obj)
            
            # Eğer ürünler bulunduysa, yeni kombini listeye ekle
            if enriched_items:
                enriched_combinations.append({
                    "title": combo["title"],
                    "vibe": combo["vibe"],
                    "items": enriched_items  # İsim listesi yerine obje listesi
                })

        return {"combinations": enriched_combinations}

    except Exception as e:
        print(f"Stilist Hatası: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"Stilist önerisi oluşturulurken bir hata oluştu: {str(e)}")

@app.get("/api/return-analytics")
async def get_return_analytics():
    product_analysis = []
    
    # Ürünlere göre iadeleri grupla (bu kısım doğru)
    returns_by_product = defaultdict(list)
    if return_intents_db:
        for intent_data in return_intents_db:
            returns_by_product[intent_data["product_name"]].append(intent_data)
        
        for product_name, returns in returns_by_product.items():
            counts = Counter(r["intent"] for r in returns)
            product_analysis.append({
                "product_name": product_name,
                "total_returns": len(returns),
                "reasons": sorted([{"intent": i, "count": c, "percentage": round((c / len(returns)) * 100, 1)} for i, c in counts.items()], key=lambda x: x['percentage'], reverse=True)
            })

    # DÜZELTME: "recent_return_feedback_summary" oluştururken,
    # 'product_analysis' yerine orijinal veriyi içeren 'returns_by_product' sözlüğünü kullanıyoruz.
    simulated_data = {
        "sales_trends": {"Bej Keten Gömlek": -25, "Deri Biker Ceket": 40},
        "top_searches": ["oversize ceket", "keten pantolon", "yazlık elbise"],
        "recent_return_feedback_summary": {
            product_name: [r["message"] for r in returns] 
            for product_name, returns in returns_by_product.items()
        }
    }

    try:
        strategic_overview = gemini_service.get_trend_analysis(simulated_data)
    except Exception as e:
        print(f"Stratejik Trend Analizi Hatası: {e}")
        strategic_overview = {"strategic_overview": {
            "trend_alarm": f"Analiz hatası: {e}",
            "stock_optimization": "N/A",
            "product_development": "N/A"
        }}

    return {
        "total_returns": len(return_intents_db),
        "product_analysis": sorted(product_analysis, key=lambda x: x['total_returns'], reverse=True),
        "strategic_overview": strategic_overview.get("strategic_overview", {})
    }
import os
import json
import sys # <-- Hata 2 için eksik olan import'u ekledik.
from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# Yeni eklenen modüller
from services import gemini_service
from models.chat_models import ChatRequest, ChatResponse

# .env dosyasındaki API anahtarını YÜKLE
load_dotenv()

# API anahtarının YÜKLENDİĞİNDEN emin ol.
# Bu kontrol, sunucu başlarken bize bilgi verecek.
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("UYARI: .env dosyasında GEMINI_API_KEY bulunamadı veya boş. Lütfen API anahtarınızı ekleyin.", file=sys.stderr)
else:
    print("Bilgi: Gemini API anahtarı başarıyla yüklendi.")
    # Anahtarı Gemini servisine iletiyoruz.
    gemini_service.configure_gemini(API_KEY)


app = FastAPI(title="StilDöngüsü API")

# Static dosyaları (css, js, img) ve templates klasörünü bağla
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Ürün veritabanını yükle
with open('products.json', 'r', encoding='utf-8') as f:
    products_db = json.load(f)

# --- Sayfa Rotaları (HTML Döndürenler) ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/siparislerim", response_class=HTMLResponse)
async def read_siparislerim(request: Request):
    dummy_orders = [
        {"id": "TR12345", "product": "Lacivert Blazer Ceket", "status": "Teslim Edildi"},
        {"id": "TR67890", "product": "Beyaz Gömlek", "status": "Teslim Edildi"}
    ]
    return templates.TemplateResponse("siparislerim.html", {"request": request, "orders": dummy_orders})

@app.get("/satici-paneli", response_class=HTMLResponse)
async def read_satici_paneli(request: Request):
    return templates.TemplateResponse("satici_paneli.html", {"request": request})


# --- API Rotaları (JSON Döndürenler) ---

@app.post("/api/analyze-style")
async def analyze_style_api(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Lütfen bir resim dosyası yükleyin.")
    
    # API anahtarı yüklü değilse, işlemi hiç başlatma.
    if not API_KEY:
         raise HTTPException(status_code=500, detail="Sunucu yapılandırma hatası: Gemini API anahtarı bulunamadı.")

    try:
        image_bytes = await file.read()
        
        # Analiz mantığını service dosyasına taşıdık
        analysis_data = gemini_service.analyze_image_style(image_bytes)
        
        # Eşleşen ürünleri bul
        matched_products = gemini_service.find_matching_products(analysis_data, products_db)
        
        if not matched_products:
             raise HTTPException(status_code=404, detail="Veritabanımızda bu stile uygun ürün bulamadık.")

        # Stil önerisi al
        style_advice_text = gemini_service.get_style_advice(
            analysis_data.get('item_description'),
            matched_products
        )

        return {
            "original_item": analysis_data,
            "style_advice": style_advice_text,
            "matched_products": matched_products
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Sunucu Hatası: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"Analiz sırasında bir sunucu hatası oluştu: {str(e)}")


@app.post("/api/chat", response_model=ChatResponse)
async def chat_api(chat_request: ChatRequest):
    # API anahtarı yüklü değilse, işlemi hiç başlatma.
    if not API_KEY:
         raise HTTPException(status_code=500, detail="Sunucu yapılandırma hatası: Gemini API anahtarı bulunamadı.")

    try:
        reply = gemini_service.get_chatbot_reply(chat_request.message)
        return ChatResponse(reply=reply)
    except Exception as e:
        print(f"Chatbot Sunucu Hatası: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail="Chatbot servisinde bir hata oluştu.")
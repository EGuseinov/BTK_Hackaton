# gemini_service.py

import os
import json
import google.generativeai as genai
from PIL import Image
import io
import sys


vision_model = None
text_model = None
is_configured = False

# --- PROMPT'LAR ---

PROMPT_ANALYZE_IMAGE = """
SENARYO: Sen, dünya standartlarında bir moda ve iç mimari gurusu olan "Stil Gözü" adlı bir yapay zekasın. Görevin, sana sunulan görseli en ince detayına kadar analiz etmek ve tüm çıkarımlarını yapısal bir JSON formatında sunmaktır. Sadece JSON döndür, başka hiçbir açıklama yapma.

İSTENEN JSON FORMATI:
{{
  "category": "(giyim/mobilya)",
  "item_description": "Objenin fiziksel özelliklerini içeren detaylı tanım. Örn: 'Beli yüksek, geniş paçalı, açık mavi renkte, yıpratmalı bir denim pantolon.'",
  "visual_attributes": {{
    "primary_colors": ["ana renk adı", "yakın renk adı"],
    "texture_guess": "tahmini doku (ör: pamuklu, ipeksi, pürüzlü, metalik)",
    "pattern": "desenin adı (ör: çizgili, ekose, düz, çiçekli)",
    "cut_style": "kesim stili (ör: slim-fit, oversize, asimetrik)"
  }},
  "inferred_style": {{
    "style_tags": ["ana stil etiketi", "ikincil stil etiketi"],
    "justification": "Bu stil etiketlerini seçme sebebini açıklayan kısa metin."
  }},
  "contextual_use": {{
    "seasons": ["ilkbahar", "yaz"],
    "environment": ["günlük", "sosyal"],
    "formality": "rahat (casual)"
  }}
}}
"""

# GÜNCELLENDİ: Stil Radarı Prompt'u daha katı hale getirildi
PROMPT_CREATE_STYLE_PROFILE = """
SENARYO: Sen, birden fazla görseldeki desenleri, renkleri ve kesimleri analiz edip bir kişinin bütünsel stil kimliğini ortaya çıkaran bir stil analistisin. Sana sunulan görsellerdeki ortak temaları belirleyerek kişinin stil profilini, renk tercihlerini ve genel bir özetini bir JSON nesnesi olarak döndür. Stilleri yüzdelik olarak ifade et ve toplamları 100 olmalı. Kesinlikle sadece JSON çıktısı ver, başka hiçbir açıklama veya giriş metni ekleme.

İSTENEN JSON FORMATI:
{{
  "style_profile": [
    {{"style": "bohem", "percentage": 60}},
    {{"style": "klasik", "percentage": 30}},
    {{"style": "sokak_modasi", "percentage": 10}}
  ],
  "dominant_colors": ["toprak tonları", "denim mavisi", "krem"],
  "summary": "Bu kişi, rahatlığı ön planda tutan, doğal kumaşları ve salaş kesimleri benimseyen bir bohem tarza sahip. Ancak dolabındaki blazer ceketler ve düz renk gömlekler, klasik parçalara da önem verdiğini gösteriyor."
}}
"""

PROMPT_GENERATE_VISUAL_COMBO = """
SENARYO: Sen, bir stilistin hayal gücünü metne döken bir betimleme uzmanısın. Sana verilen kıyafetleri giyen bir mankeni, bir e-ticaret sitesinin stüdyo çekimindeymiş gibi detaylıca betimle. Sadece JSON formatında cevap ver.

GİRDİLER:
- Ana Parça: {main_item}
- Uyumlu Ürünler: {matched_items}

İSTENEN JSON FORMATI:
{{
  "image_description": "Fotorealistik bir manken fotoğrafının detaylı açıklaması. Örn: 'Sade, gri bir stüdyo arka planının önünde duran manken, [ana parça açıklaması]'nı giyiyor. Üzerine [ürün 1 adı]'nı kombinlemiş ve ayakkabı olarak [ürün 2 adı] tercih etmiş. Duruşu kendinden emin ve modern bir hava katıyor.'"
}}
"""

PROMPT_STRATEGIC_RETURN_ADVICE = """
SENARYO: Sen bir e-ticaret veri analistisin. Sana bir ürünle ilgili bir grup müşteri iade mesajı verilecek. Bu mesajları analiz et, tekrar eden ana temayı (ör: 'kalıp dar', 'renk soluk', 'kumaş ince') bul ve satıcının iade oranını düşürmek için ürün sayfasına ekleyebileceği somut, aksiyon odaklı bir öneri metni oluştur. Sadece JSON formatında cevap ver.

Müşteri Mesajları: {messages}

İSTENEN JSON FORMATI:
{{
  "common_theme": "Müşteriler sıklıkla ürünün kalıbının beklenenden dar olduğundan şikayetçi.",
  "actionable_advice": "Ürün açıklamasına şu notu eklemeyi düşünün: 'Stil Notu: Bu ürün, vücuda oturan slim-fit bir kesime sahiptir. Daha rahat bir kullanım için bir beden büyük tercih etmenizi öneririz.'"
}}
"""

# --- FONKSİYONLAR ---

def configure_gemini(api_key: str):
    global vision_model, text_model, is_configured
    try:
        genai.configure(api_key=api_key)
        model_name = 'gemini-1.5-flash-latest'
        vision_model = genai.GenerativeModel(model_name)
        text_model = genai.GenerativeModel(model_name)
        is_configured = True
        print(f"Bilgi: Gemini servisi '{model_name}' modeli ile başarıyla yapılandırıldı.")
    except Exception as e:
        print(f"HATA: Gemini servisi yapılandırılamadı: {e}", file=sys.stderr)
        is_configured = False

# YENİ: Daha akıllı JSON ayrıştırıcı fonksiyon
def parse_gemini_json_response(response_text: str) -> dict:
    """
    Gemini'den gelen metin yanıtından JSON bloğunu ayıklar ve ayrıştırır.
    Yanıtın başında veya sonunda fazladan metin olsa bile çalışacak şekilde tasarlanmıştır.
    """
    try:
        # JSON bloğunun başlangıcını '{' ve sonunu '}' karakteriyle bul
        json_start_index = response_text.find('{')
        json_end_index = response_text.rfind('}')

        if json_start_index == -1 or json_end_index == -1:
            raise ValueError("Yanıt metninde JSON nesnesi bulunamadı.")

        # Sadece JSON bloğunu al ve ayrıştır
        json_string = response_text[json_start_index : json_end_index + 1]
        return json.loads(json_string)
        
    except (json.JSONDecodeError, ValueError) as e:
        print(f"JSON Ayrıştırma Hatası: {e}\n--- Sorunlu Orijinal Metin Başlangıcı ---\n{response_text[:500]}...\n--- Sorunlu Orijinal Metin Sonu ---", file=sys.stderr)
        raise ValueError("Gemini'den gelen yanıt geçerli bir JSON formatı içermiyor.")

def analyze_image_style(image_bytes: bytes) -> dict:
    if not is_configured:
        raise Exception("Gemini servisi yapılandırılmamış.")
    img = Image.open(io.BytesIO(image_bytes))
    response = vision_model.generate_content([PROMPT_ANALYZE_IMAGE, img])
    return parse_gemini_json_response(response.text)

def find_matching_products(analysis_data: dict, products_db: list) -> list:
    matched_products = []
    inferred_style = analysis_data.get("inferred_style", {})
    style_tags = set(inferred_style.get("style_tags", []))
    if not style_tags:
        return products_db[:3]
    for product in products_db:
        product_style_tags = set(product.get("style_tags", []))
        if style_tags.intersection(product_style_tags):
            matched_products.append(product)
    if not matched_products:
        return products_db[:3]
    return matched_products

def get_style_advice(description: str, matched_products: list) -> dict:
    if not is_configured:
        raise Exception("Gemini servisi yapılandırılmamış.")
    matched_products_names = [p['name'] for p in matched_products]
    PROMPT_GET_STYLE_ADVICE = f"""
SENARYO: Sen, kullanıcılarına ilham veren, sıcak ve bilgili bir stil danışmanı olan "StilDöngüsü Asistanı"sın. Senin işin sadece neyin neyle uyduğunu söylemek değil, bir hikaye anlatmak ve kullanıcıyı heyecanlandırmaktır. Cevabını sadece JSON formatında ver.
GİRDİLER:
- Ana Parça Tanımı: {description}
- Uyumlu Ürünler Listesi: {matched_products_names}
İSTENEN JSON FORMATI:
{{
    "title": "Kombin için yaratıcı ve akılda kalıcı başlık",
    "vibe_description": "Bu kombinin genel atmosferini ve hissini anlatan 1-2 cümlelik metin.",
    "combination_logic": "Parçaların neden uyumlu olduğunu açıklayan detaylı stil analizi metni.",
    "pro_tip": "Kombini tamamlayacak uzman ipucu."
}}
"""
    response = text_model.generate_content(PROMPT_GET_STYLE_ADVICE)
    return parse_gemini_json_response(response.text)


def get_chatbot_reply(user_message: str) -> dict:
    if not is_configured:
        raise Exception("Gemini servisi yapılandırılmamış.")
    PROMPT_CHATBOT_BRAIN = f"""
SENARYO: Sen, bir e-ticaret firmasının "ReturnLogic" adlı Müşteri Memnuniyeti Uzmanısın. Empatik, analitik ve çözüm odaklısın. Birincil hedefin, müşteriyi mutlu ederek iadeyi önlemek. Her yanıtını yapısal bir JSON formatında ver.
SÜREÇ:
1.  **Empati Kur:** Müşterinin hayal kırıklığını anladığını belirten bir cümleyle başla.
2.  **Niyet Tespiti (Intent):** Müşterinin mesajının altında yatan asıl iade sebebini şu kategorilerden birine ata: `BEDEN`, `RENK_STIL`, `KUSURLU_URUN`, `BEKLENTI_FARKI`, `COZULEBILIR_SORUN`, `BELIRSIZ`.
3.  **Aksiyona Yönelik Cevap Üret:** Tespit ettiğin niyete göre en uygun çözümü sunan bir metin oluştur. `BEDEN` veya `RENK_STIL` ise, değişim teklif et ve "Stil Analisti" özelliğini '[STIL_ANALISTI_LINK]' anahtar kelimesiyle tanıt.
4.  **JSON Çıktısı Oluştur.**
GİRDİ:
- Müşteri Mesajı: {user_message}
İSTENEN JSON FORMATI:
{{
  "detected_intent": "Tespit ettiğin niyet kategorisi (örn: BEDEN, RENK_STIL)",
  "reply_text": "Müşteriye gösterilecek, yukarıdaki kurallara göre oluşturulmuş yanıt metni.",
  "is_return_prevented": true
}}
"""
    response = text_model.generate_content(PROMPT_CHATBOT_BRAIN)
    return parse_gemini_json_response(response.text)

def create_style_profile(image_bytes_list: list) -> dict:
    if not is_configured:
        raise Exception("Gemini servisi yapılandırılmamış.")
    
    prompt_parts = [PROMPT_CREATE_STYLE_PROFILE]
    for image_bytes in image_bytes_list:
        img = Image.open(io.BytesIO(image_bytes))
        prompt_parts.append(img)
        
    response = vision_model.generate_content(prompt_parts)
    return parse_gemini_json_response(response.text)


def generate_visual_combo(main_item: str, matched_items: list) -> dict:
    if not is_configured:
        raise Exception("Gemini servisi yapılandırılmamış.")
    
    prompt = PROMPT_GENERATE_VISUAL_COMBO.format(
        main_item=main_item, 
        matched_items=", ".join(matched_items)
    )
    response = text_model.generate_content(prompt)
    return parse_gemini_json_response(response.text)

def get_strategic_return_advice(messages: list) -> dict:
    if not is_configured:
        raise Exception("Gemini servisi yapılandırılmamış.")
    
    prompt = PROMPT_STRATEGIC_RETURN_ADVICE.format(messages=json.dumps(messages, ensure_ascii=False))
    response = text_model.generate_content(prompt)
    return parse_gemini_json_response(response.text)
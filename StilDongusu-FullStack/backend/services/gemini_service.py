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
  "item_description": "Objenin fiziksel özelliklerini içeren detaylı tanım.",
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

PROMPT_FIT_SCORE = """
SENARYO: Sen bir kişisel stil danışmanısın. Bir kullanıcının vücut tipi ile bir ürünün özelliklerini karşılaştırarak, bu ürünün kullanıcıya ne kadar uygun olacağına dair bir puan ve kısa bir gerekçe üreteceksin. Sadece JSON formatında cevap ver.

VERİLER:
- Kullanıcı Vücut Tipi: {user_body_type}
- Ürün Kesimi: {product_cut}
- Ürün Materyali: {product_material}
- Ürünün Önerildiği Vücut Tipleri: {product_fit_types}

İSTENEN JSON FORMATI:
{{
  "fit_score": "10 üzerinden bir puan (örn: 8)",
  "reasoning": "Bu puanı neden verdiğini açıklayan kısa, profesyonel ve cesaretlendirici bir metin."
}}
"""

PROMPT_EVENT_STYLIST = """
SENARYO: Sen, dünya çapında bir stilistsin. Bir müşteri sana bir etkinlik veya mekan için ne giymesi gerektiğini soruyor. Müşterinin isteğini ve eldeki ürün listesini analiz ederek, ona 3 farklı, tam ve yaratıcı kombin önerisi sunacaksın. Her kombinin bir başlığı, bir "vibe" açıklaması ve hangi ürünlerden oluştuğu belirtilmeli. Sadece JSON formatında cevap ver.

VERİLER:
- Müşterinin İsteği: "{user_request}"
- Eldeki Ürünler (JSON formatında): {products_json}

İSTENEN JSON FORMATI:
{{
  "combinations": [
    {{
      "title": "Kombin 1 için yaratıcı bir başlık",
      "vibe": "Bu kombinin yarattığı atmosferi anlatan kısa metin.",
      "items": ["Ürün Adı 1", "Ürün Adı 2", "Ürün Adı 3"]
    }},
    {{
      "title": "Kombin 2 için yaratıcı bir başlık",
      "vibe": "Bu kombinin yarattığı atmosferi anlatan kısa metin.",
      "items": ["Ürün Adı 4", "Ürün Adı 5", "Ürün Adı 6"]
    }},
    {{
      "title": "Kombin 3 için yaratıcı bir başlık",
      "vibe": "Bu kombinin yarattığı atmosferi anlatan kısa metin.",
      "items": ["Ürün Adı 7", "Ürün Adı 8", "Ürün Adı 1"]
    }}
  ]
}}
"""

PROMPT_TREND_ANALYSIS = """
SENARYO: Sen, bir e-ticaret firmasının strateji direktörüsün. Sana sunulan satış, iade ve arama verilerini analiz ederek, firma için 3 adet somut ve aksiyon odaklı stratejik öneri sunacaksın. Önerilerin, "Trend Alarmı", "Stok Optimizasyonu" ve "Ürün Geliştirme" başlıkları altında olmalı. Sadece JSON formatında cevap ver.

VERİLER:
{simulated_data}

İSTENEN JSON FORMATI:
{{
  "strategic_overview": {{
    "trend_alarm": "Piyasadaki yükselen bir trend ve buna yönelik bir öneri.",
    "stock_optimization": "Mevcut stokların daha verimli yönetilmesi için bir öneri.",
    "product_development": "Müşteri geri bildirimlerine dayalı bir ürün geliştirme veya iyileştirme önerisi."
  }}
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

def parse_gemini_json_response(response_text: str) -> dict:
    try:
        json_start_index = response_text.find('{')
        json_end_index = response_text.rfind('}')
        if json_start_index == -1 or json_end_index == -1:
            raise ValueError("Yanıt metninde JSON nesnesi bulunamadı.")
        json_string = response_text[json_start_index : json_end_index + 1]
        return json.loads(json_string)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"JSON Ayrıştırma Hatası: {e}\n--- Sorunlu Metin ---\n{response_text[:500]}...", file=sys.stderr)
        raise ValueError("Gemini'den gelen yanıt geçerli bir JSON formatı içermiyor.")

def analyze_image_style(image_bytes: bytes) -> dict:
    if not is_configured: raise Exception("Gemini servisi yapılandırılmamış.")
    img = Image.open(io.BytesIO(image_bytes))
    response = vision_model.generate_content([PROMPT_ANALYZE_IMAGE, img])
    return parse_gemini_json_response(response.text)

def find_matching_products(analysis_data: dict, products_db: list) -> list:
    matched_products = []
    style_tags = set(analysis_data.get("inferred_style", {}).get("style_tags", []))
    if not style_tags: return products_db[:3]
    for product in products_db:
        if style_tags.intersection(set(product.get("style_tags", []))):
            matched_products.append(product)
    return matched_products if matched_products else products_db[:3]

def get_style_advice(description: str, matched_products: list) -> dict:
    if not is_configured: raise Exception("Gemini servisi yapılandırılmamış.")
    names = [p['name'] for p in matched_products]
    prompt = f"""
SENARYO: Sen, ilham veren bir stil danışmanısın. Bir ana parça ve ona uygun ürünler için bir hikaye anlat. Sadece JSON formatında cevap ver.
GİRDİLER:
- Ana Parça: {description}
- Uyumlu Ürünler: {names}
İSTENEN JSON FORMATI:
{{
    "title": "Kombin için yaratıcı bir başlık",
    "vibe_description": "Kombinin atmosferini anlatan 1-2 cümle.",
    "combination_logic": "Parçaların neden uyumlu olduğunu açıklayan analiz.",
    "pro_tip": "Kombini tamamlayacak uzman ipucu."
}}
"""
    response = text_model.generate_content(prompt)
    return parse_gemini_json_response(response.text)

def get_chatbot_reply(user_message: str) -> dict:
    if not is_configured: raise Exception("Gemini servisi yapılandırılmamış.")
    prompt = f"""
SENARYO: Sen "ReturnLogic" adlı bir Müşteri Memnuniyeti Uzmanısın. İadeyi önlemek ve müşteriyi mutlu etmek hedefin. Sadece JSON formatında cevap ver.
SÜREÇ:
1. Empati kur.
2. Niyeti tespit et: `BEDEN`, `RENK_STIL`, `KUSURLU_URUN`, `BEKLENTI_FARKI`, `BELIRSIZ`.
3. Niyete göre çözüm üret. `BEDEN` veya `RENK_STIL` ise, '[STIL_ANALISTI_LINK]' ile Stil Analistini tanıt.
GİRDİ:
- Müşteri Mesajı: {user_message}
İSTENEN JSON FORMATI:
{{
  "detected_intent": "Tespit edilen niyet kategorisi",
  "reply_text": "Müşteriye gösterilecek yanıt metni.",
  "is_return_prevented": true
}}
"""
    response = text_model.generate_content(prompt)
    return parse_gemini_json_response(response.text)

def create_style_profile(image_bytes_list: list) -> dict:
    if not is_configured: raise Exception("Gemini servisi yapılandırılmamış.")
    prompt_parts = [PROMPT_CREATE_STYLE_PROFILE]
    for image_bytes in image_bytes_list:
        prompt_parts.append(Image.open(io.BytesIO(image_bytes)))
    response = vision_model.generate_content(prompt_parts)
    return parse_gemini_json_response(response.text)

def get_fit_score(user_body_type: str, product: dict) -> dict:
    if not is_configured: raise Exception("Gemini servisi yapılandırılmamış.")
    prompt = PROMPT_FIT_SCORE.format(
        user_body_type=user_body_type,
        product_cut=product.get("cut_style", "belirtilmemiş"),
        product_material=product.get("material", "belirtilmemiş"),
        product_fit_types=product.get("uygun_vucut_tipleri", [])
    )
    response = text_model.generate_content(prompt)
    return parse_gemini_json_response(response.text)

def get_event_style_combinations(user_request: str, products_db: list) -> dict:
    if not is_configured: raise Exception("Gemini servisi yapılandırılmamış.")
    clothing = [p for p in products_db if "kitaplık" not in p["name"].lower() and "berjer" not in p["name"].lower()]
    prompt = PROMPT_EVENT_STYLIST.format(user_request=user_request, products_json=json.dumps(clothing, ensure_ascii=False))
    response = text_model.generate_content(prompt)
    return parse_gemini_json_response(response.text)

def get_trend_analysis(simulated_data: dict) -> dict:
    if not is_configured: raise Exception("Gemini servisi yapılandırılmamış.")
    prompt = PROMPT_TREND_ANALYSIS.format(simulated_data=json.dumps(simulated_data, ensure_ascii=False))
    response = text_model.generate_content(prompt)
    return parse_gemini_json_response(response.text)
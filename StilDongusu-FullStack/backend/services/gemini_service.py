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

SÜREÇ:
1.  **Kategori Tespiti:** Görseldeki ana obje bir 'giyim' ürünü mü yoksa bir 'mobilya' mı?
2.  **Detaylı Analiz:** Objeyi rengi, dokusu (tahmini), deseni, kesimi ve materyali (tahmini) gibi görsel özellikleriyle tanımla.
3.  **Stil Çıkarımı:** Bu görsel özelliklere dayanarak, objenin estetik stilini (ör: bohem, minimalist, endüstriyel, avangart, klasik, spor) belirle. Birden fazla etiket kullanabilirsin.
4.  **Bağlamsal Çıkarım:** Bu parçanın hangi mevsimde, ne tür bir ortamda (günlük, ofis, özel davet) ve hangi resmiyet düzeyinde (rahat, yarı-resmi, resmi) kullanılabileceğini tahmin et.
5.  **Gerekçelendirme:** Stil etiketlerini neden seçtiğine dair kısa, profesyonel bir gerekçe sun.

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
    "justification": "Bu stil etiketlerini seçme sebebini açıklayan kısa metin. Örn: 'Geniş paça kesimi ve yıpratılmış dokusu 70'ler bohem akımını, sade rengi ise minimalist estetiği yansıtıyor.'"
  }},
  "contextual_use": {{
    "seasons": ["ilkbahar", "yaz"],
    "environment": ["günlük", "sosyal"],
    "formality": "rahat (casual)"
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
    
    cleaned_text = response_text.strip().replace("```json", "").replace("```", "")
    return json.loads(cleaned_text)

def analyze_image_style(image_bytes: bytes) -> dict:
    """Verilen resim dosyasının byte'larını analiz eder ve stil bilgilerini JSON olarak döndürür."""
    if not is_configured:
        raise Exception("Gemini servisi yapılandırılmamış veya anahtar geçersiz.")
    img = Image.open(io.BytesIO(image_bytes))
    
    response = vision_model.generate_content([PROMPT_ANALYZE_IMAGE, img])
    return parse_gemini_json_response(response.text)

def find_matching_products(analysis_data: dict, products_db: list) -> list:
    """
    Analiz verilerine göre ürün veritabanında eşleşen ürünleri bulur.
    Eğer eşleşme bulamazsa, genel öneri olarak ilk 3 ürünü döndürür.
    """
    matched_products = []
    inferred_style = analysis_data.get("inferred_style", {})
    style_tags = set(inferred_style.get("style_tags", []))
    
    if not style_tags:
        print("Uyarı: Gemini analizinden stil etiketleri alınamadı. Genel öneriler döndürülüyor.")
        return products_db[:3]

    for product in products_db:
        product_style_tags = set(product.get("style_tags", []))
        if style_tags.intersection(product_style_tags):
            matched_products.append(product)
            
    if not matched_products:
        print("Uyarı: Spesifik eşleşme bulunamadı. Genel ürünler döndürülüyor.")
        return products_db[:3]
        
    return matched_products

def get_style_advice(description: str, matched_products: list) -> dict:
    """Verilen ana parça ve uyumlu ürünler için Gemini'den stil önerisi metni alır."""
    if not is_configured:
        raise Exception("Gemini servisi yapılandırılmamış veya anahtar geçersiz.")
        
    matched_products_names = [p['name'] for p in matched_products]
    
    PROMPT_GET_STYLE_ADVICE = f"""
SENARYO: Sen, kullanıcılarına ilham veren, sıcak ve bilgili bir stil danışmanı olan "StilDöngüsü Asistanı"sın. Senin işin sadece neyin neyle uyduğunu söylemek değil, bir hikaye anlatmak ve kullanıcıyı heyecanlandırmaktır. Cevabını sadece JSON formatında ver.

GİRDİLER:
- Ana Parça Tanımı: {description}
- Uyumlu Ürünler Listesi: {matched_products_names}

SÜREÇ:
1.  **Vibe Yarat:** Ana parça ve uyumlu ürünlerin bir araya geldiğinde yaratacağı genel havayı (vibe) tanımla. "Sofistike ve modern", "enerjik ve bohem", "sakin ve profesyonel" gibi.
2.  **Kombin Mantığını Açıkla:** Renk teorisi, doku kontrastı veya stil dengesi gibi profesyonel kavramları basit bir dille kullanarak bu parçaların neden birlikte "çalıştığını" açıkla.
3.  **Profesyonel İpucu (Pro-Tip):** Bu kombini bir üst seviyeye taşıyacak küçük bir aksesuar, ayakkabı seçimi veya kullanım önerisi ekle. Bu senin imzan olsun.
4.  **Başlık Oluştur:** Kombine "Hafta Sonu Şıklığı", "Ofiste Güç Duruşu" gibi akılda kalıcı bir başlık bul.

İSTENEN JSON FORMATI:
{{
    "title": "Kombin için yaratıcı ve akılda kalıcı başlık",
    "vibe_description": "Bu kombinin genel atmosferini ve hissini anlatan 1-2 cümlelik metin.",
    "combination_logic": "Parçaların neden uyumlu olduğunu açıklayan detaylı stil analizi metni.",
    "pro_tip": "Kombini tamamlayacak uzman ipucu. Örn: 'Bu kombini metalik bir kolye ile tamamlayarak modern bir dokunuş katabilirsiniz.'"
}}
"""
    response = text_model.generate_content(PROMPT_GET_STYLE_ADVICE)
    return parse_gemini_json_response(response.text)

def get_chatbot_reply(user_message: str) -> dict:
    """Kullanıcı mesajına göre iade asistanı chatbot'tan yanıt alır."""
    if not is_configured:
        raise Exception("Gemini servisi yapılandırılmamış veya anahtar geçersiz.")

    PROMPT_CHATBOT_BRAIN = f"""
SENARYO: Sen, bir e-ticaret firmasının en değerli çalışanı olan "ReturnLogic" adlı bir Müşteri Memnuniyeti Yapay Zeka Uzmanısın. Sadece bir chatbot değilsin; empatik, analitik ve çözüm odaklısın. Birincil hedefin, müşteriyi mutlu ederek iadeyi önlemek ve onu tekrar alışveriş döngüsüne dahil etmektir. Her yanıtını yapısal bir JSON formatında ver.

SÜREÇ:
1.  **Empati Kur:** Her zaman müşterinin hayal kırıklığını anladığını belirten kısa bir cümleyle başla.
2.  **Niyet Tespiti (Intent Recognition):** Müşterinin mesajının altında yatan asıl iade sebebini şu kategorilerden birine ata:
    - `BEDEN`: 'büyük/küçük geldi', 'dar/bol oldu', 'kalıbı uymadı' gibi ifadeler.
    - `RENK_STIL`: 'rengini beğenmedim', 'bana yakışmadı', 'resimdeki gibi durmadı' gibi estetik ifadeler.
    - `KUSURLU_URUN`: 'yırtık', 'bozuk', 'lekeli', 'kırık geldi' gibi bariz ürün hataları.
    - `BEKLENTI_FARKI`: 'kumaşı kaliteli değil', 'ince zannetmiştim kalın çıktı' gibi ürünün kendisiyle ilgili hayal kırıklıkları.
    - `COZULEBILIR_SORUN`: 'kurulumunu yapamadım', 'ayarı nasıl oluyor?' gibi bilgi eksikliğine dayalı sorunlar.
    - `BELIRSIZ`: 'beğenmedim', 'iade etmek istiyorum' gibi genel ifadeler.
3.  **Aksiyona Yönelik Cevap Üret:** Tespit ettiğin niyete göre en uygun çözümü sunan bir metin oluştur.
    - `BEDEN` veya `RENK_STIL` ise: Değişim teklif et ve ASIL ÖNEMLİSİ, bir sonraki sefer mükemmel ürünü bulması için "Stil Analisti (StyleSync)" özelliğini heyecan verici bir şekilde tanıt. '[STIL_ANALISTI_LINK]' anahtar kelimesini kullan.
    - `KUSURLU_URUN` ise: Koşulsuz şartsız özür dile, hemen yeni ürün göndermeyi veya tam iade yapmayı teklif et. Güveni yeniden inşa et.
    - `BEKLENTI_FARKI` ise: Üzüntünü belirt, iade alabileceğini söyle. Gelecekte daha doğru seçimler yapabilmesi için ürün açıklamalarını daha dikkatli okumasını veya müşteri yorumlarından faydalanmasını nazikçe öner.
    - `COZULEBILIR_SORUN` ise: Sorunu anında çözmeye yönelik basit bir talimat veya link ver. "Ayarlar menüsünde..." gibi.
    - `BELIRSIZ` ise: Daha fazla bilgi almak için nazikçe bir soru sor. "Elbette yardımcı olmak isterim, sakıncası yoksa beğenmeme sebebinizle ilgili biraz daha detay verebilir misiniz? Belki size daha uygun bir ürün önerebilirim."
4.  **JSON Çıktısı Oluştur:** Analizini ve oluşturduğun cevabı JSON formatında paketle.

GİRDİ:
- Müşteri Mesajı: {user_message}

İSTENEN JSON FORMATI:
{{
  "detected_intent": "Tespit ettiğin niyet kategorisi (örn: BEDEN, RENK_STIL)",
  "reply_text": "Müşteriye gösterilecek, yukarıdaki kurallara göre oluşturulmuş yanıt metni.",
  "is_return_prevented": "Bu cevapla iadenin önlenme potansiyeli var mı? (true/false)"
}}
"""
    response = text_model.generate_content(PROMPT_CHATBOT_BRAIN)
    return parse_gemini_json_response(response.text)
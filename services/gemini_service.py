import os
import json
import google.generativeai as genai
from PIL import Image
import io
import sys

# Modelleri burada tanımlıyoruz ama henüz yapılandırmıyoruz.
vision_model = None
text_model = None
is_configured = False

def configure_gemini(api_key: str):
    """
    Bu fonksiyon main.py tarafından çağrılarak Gemini API'yi yapılandırır.
    """
    global vision_model, text_model, is_configured
    try:
        genai.configure(api_key=api_key)
        # HATA ÇÖZÜMÜ: "Model bulunamadı" hatası için en güncel ve genel modeli kullanıyoruz.
        # Bu model hem metin hem de görsel (vision) yeteneğine sahiptir.
        model_name = 'gemini-1.5-flash-latest'
        vision_model = genai.GenerativeModel(model_name)
        text_model = genai.GenerativeModel(model_name)
        is_configured = True
        print(f"Bilgi: Gemini servisi '{model_name}' modeli ile başarıyla yapılandırıldı.")
    except Exception as e:
        print(f"HATA: Gemini servisi yapılandırılamadı: {e}", file=sys.stderr)
        is_configured = False


def analyze_image_style(image_bytes: bytes) -> dict:
    """Verilen resim dosyasının byte'larını analiz eder ve stil bilgilerini JSON olarak döndürür."""
    if not is_configured:
        raise Exception("Gemini servisi yapılandırılmamış veya anahtar geçersiz.")
    
    img = Image.open(io.BytesIO(image_bytes))
    
    prompt = """
    Bu resimdeki giysi veya mobilyayı analiz et. 
    Bana aşağıdaki formatta bir JSON çıktısı ver:
    {
      "item_description": "Örnek: Lacivert, yünlü, slim-fit bir blazer ceket",
      "style_tags": ["klasik", "minimalist", "ofis"],
      "color_tags": ["lacivert", "koyu mavi", "mavi"]
    }
    Sadece ve sadece JSON kodunu döndür, başka hiçbir metin veya markdown formatı ekleme.
    """
    response = vision_model.generate_content([prompt, img])
    
    analysis_json_text = response.text.strip().replace("```json", "").replace("```", "")
    return json.loads(analysis_json_text)

def find_matching_products(analysis_data: dict, products_db: list) -> list:
    """Analiz verilerine göre ürün veritabanında eşleşen ürünleri bulur."""
    matched_products = []
    style_tags = set(analysis_data.get("style_tags", []))
    
    for product in products_db:
        product_style_tags = set(product.get("style_tags", []))
        if style_tags.intersection(product_style_tags):
            matched_products.append(product)
    return matched_products

def get_style_advice(description: str, matched_products: list) -> str:
    """Verilen ana parça ve uyumlu ürünler için Gemini'den stil önerisi metni alır."""
    if not is_configured:
        raise Exception("Gemini servisi yapılandırılmamış veya anahtar geçersiz.")
        
    style_prompt = f"""
    Bir kullanıcı dolabındaki '{description}' için kombin önerisi arıyor.
    Ona uyumlu olarak şu ürünleri bulduk: {[p['name'] for p in matched_products]}.
    Bu ürünlerle ana parçanın neden şık duracağını anlatan, samimi ve ikna edici bir stil önerisi metni yaz.
    Metin, kullanıcıya ilham vermeli ve bu ürünleri satın almaya teşvik etmeli.
    """
    style_advice_response = text_model.generate_content(style_prompt)
    return style_advice_response.text

def get_chatbot_reply(user_message: str) -> str:
    """Kullanıcı mesajına göre iade asistanı chatbot'tan yanıt alır."""
    if not is_configured:
        raise Exception("Gemini servisi yapılandırılmamış veya anahtar geçersiz.")

    system_prompt = """
    Sen, 'StilDöngüsü' adlı bir e-ticaret sitesinin 'Akıllı İade Asistanı'sın. Adın 'ReturnLogic'. 
    Görevin, müşterinin iade sebebini nazikçe anlamak ve mümkünse ona bir çözüm sunarak iadeyi engellemek.
    - Eğer sorun beden veya renk/stil uyumsuzluğu ise, iadeyi başlatabileceğini söyle ama hemen ardından ona 'Stil ve Uyum Analisti (StyleSync)' özelliğimizi öner. Bu özelliğin, elindeki başka bir parçanın fotoğrafını yükleyerek ona %100 uyumlu ürünler bulabileceğini anlat. Müşteriyi ana sayfaya yönlendirmek için '[STIL_ANALISTI_LINK]' metnini kullan.
    - Eğer ürün bozuksa veya farklı bir sorun varsa, üzgün olduğunu belirt ve iade sürecinin başlatılacağını söyle.
    - Konuşmaların kısa, samimi ve çözüm odaklı olsun.
    """
    response = text_model.generate_content([system_prompt, f"Müşteri: {user_message}"])
    return response.text
import os
import json
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from PIL import Image

# .env dosyasındaki API anahtarını yükle
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

# Ürün veritabanını yükle
with open('products.json', 'r', encoding='utf-8') as f:
    products_db = json.load(f)

# Gemini Modellerini Başlat
# ESKİ:
# vision_model = genai.GenerativeModel('gemini-1.5-pro-latest') 

# YENİ ve DAHA İYİ:
vision_model = genai.GenerativeModel('gemini-pro-vision') 
text_model = genai.GenerativeModel('gemini-pro')

# --- Sayfa Rotaları ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/siparislerim')
def siparislerim():
    # Demo sipariş verisi
    dummy_orders = [
        {"id": "TR12345", "product": "Lacivert Blazer Ceket", "status": "Teslim Edildi"},
        {"id": "TR67890", "product": "Beyaz Gömlek", "status": "Teslim Edildi"}
    ]
    return render_template('siparislerim.html', orders=dummy_orders)

@app.route('/satici-paneli')
def satici_paneli():
    # Bu rapor, gerçek bir senaryoda toplanan verilerle periyodik olarak Gemini'ye ürettirilir.
    # Hackathon için demo amaçlı statik içerik gösteriyoruz.
    return render_template('satici_paneli.html')

# --- API Rotaları ---

@app.route('/api/analyze-style', methods=['POST'])
def analyze_style():
    if 'file' not in request.files:
        return jsonify({"error": "Resim dosyası bulunamadı"}), 400

    file = request.files['file']
    img = Image.open(file.stream)

    try:
        # Gemini Vision'a gönderilecek prompt
        prompt = '''
        Bu resimdeki giysi veya mobilyayı analiz et. 
        Bana aşağıdaki formatta bir JSON çıktısı ver:
        {
          "item_description": "Örnek: Lacivert, yünlü, slim-fit bir blazer ceket",
          "style_tags": ["klasik", "minimalist", "ofis"],
          "color_tags": ["lacivert", "koyu mavi", "mavi"],
          "dominant_color_name": "lacivert"
        }
        Sadece JSON kodunu döndür, başka hiçbir metin ekleme.
        '''
        response = vision_model.generate_content([prompt, img])
        
        # Gemini'den gelen yanıtı temizleyip JSON'a çevir
        analysis_json_text = response.text.strip().replace("```json", "").replace("```", "")
        analysis_data = json.loads(analysis_json_text)
        
        # Ürün veritabanında uyumlu ürünleri bul
        matched_products = []
        style_tags = set(analysis_data.get("style_tags", []))
        color_tags = set(analysis_data.get("color_tags", []))
        
        for product in products_db:
            product_style_tags = set(product.get("style_tags", []))
            # Basit bir eşleştirme mantığı: En az bir stil etiketi eşleşiyorsa uyumlu kabul et
            if style_tags.intersection(product_style_tags):
                matched_products.append(product)

        if not matched_products:
            return jsonify({"error": "Veritabanımızda bu stile uygun ürün bulamadık."}), 404
        
        # Uyumlu ürünler için Gemini'den stil önerisi al
        style_prompt = f"""
        Bir kullanıcı dolabındaki '{analysis_data.get('item_description')}' için kombin önerisi arıyor.
        Ona uyumlu olarak şu ürünleri bulduk: {[p['name'] for p in matched_products]}.
        Bu ürünlerle ana parçanın neden şık duracağını anlatan, samimi ve ikna edici bir stil önerisi metni yaz.
        Metin, kullanıcıya ilham vermeli ve bu ürünleri satın almaya teşvik etmeli.
        """
        style_advice_response = text_model.generate_content(style_prompt)

        return jsonify({
            "original_item": analysis_data,
            "style_advice": style_advice_response.text,
            "matched_products": matched_products
        })

    except Exception as e:
        print(f"Hata: {e}")
        return jsonify({"error": "Analiz sırasında bir hata oluştu. Lütfen tekrar deneyin."}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message")
    
    # Gemini'ye iade asistanı rolünü ve görevini veriyoruz
    system_prompt = """
    Sen, 'StilDöngüsü' adlı bir e-ticaret sitesinin 'Akıllı İade Asistanı'sın. Adın 'ReturnLogic'. 
    Görevin, müşterinin iade sebebini nazikçe anlamak ve mümkünse ona bir çözüm sunarak iadeyi engellemek.
    - Eğer sorun beden veya renk/stil uyumsuzluğu ise, iadeyi başlatabileceğini söyle ama hemen ardından ona 'Stil ve Uyum Analisti (StyleSync)' özelliğimizi öner. Bu özelliğin, elindeki başka bir parçanın fotoğrafını yükleyerek ona %100 uyumlu ürünler bulabileceğini anlat. Müşteriyi ana sayfaya yönlendirmek için '[STIL_ANALISTI_LINK]' metnini kullan.
    - Eğer ürün bozuksa veya farklı bir sorun varsa, üzgün olduğunu belirt ve iade sürecinin başlatılacağını söyle.
    - Konuşmaların kısa, samimi ve çözüm odaklı olsun.
    """

    try:
        response = text_model.generate_content([system_prompt, f"Müşteri: {user_message}"])
        return jsonify({"reply": response.text})
    except Exception as e:
        print(f"Chatbot Hatası: {e}")
        return jsonify({"reply": "Sistemde bir sorun oluştu, lütfen daha sonra tekrar deneyin."}), 500

if __name__ == '__main__':
    app.run(debug=True)

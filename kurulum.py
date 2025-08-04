import os

# Proje yapısı: Klasörler ve içerecekleri dosyalar
PROJECT_STRUCTURE = {
    ".env": "# .env dosyası\nGEMINI_API_KEY=\"BURAYA_API_ANAHTARINIZI_YAPISTIRIN\"",
    
    "requirements.txt": """Flask
google-generativeai
python-dotenv
Pillow
""",
    
    "app.py": """import os
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
vision_model = genai.GenerativeModel('gemini-1.5-pro-latest')
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
        style_prompt = f\"\"\"
        Bir kullanıcı dolabındaki '{analysis_data.get('item_description')}' için kombin önerisi arıyor.
        Ona uyumlu olarak şu ürünleri bulduk: {[p['name'] for p in matched_products]}.
        Bu ürünlerle ana parçanın neden şık duracağını anlatan, samimi ve ikna edici bir stil önerisi metni yaz.
        Metin, kullanıcıya ilham vermeli ve bu ürünleri satın almaya teşvik etmeli.
        \"\"\"
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
    system_prompt = \"\"\"
    Sen, 'StilDöngüsü' adlı bir e-ticaret sitesinin 'Akıllı İade Asistanı'sın. Adın 'ReturnLogic'. 
    Görevin, müşterinin iade sebebini nazikçe anlamak ve mümkünse ona bir çözüm sunarak iadeyi engellemek.
    - Eğer sorun beden veya renk/stil uyumsuzluğu ise, iadeyi başlatabileceğini söyle ama hemen ardından ona 'Stil ve Uyum Analisti (StyleSync)' özelliğimizi öner. Bu özelliğin, elindeki başka bir parçanın fotoğrafını yükleyerek ona %100 uyumlu ürünler bulabileceğini anlat. Müşteriyi ana sayfaya yönlendirmek için '[STIL_ANALISTI_LINK]' metnini kullan.
    - Eğer ürün bozuksa veya farklı bir sorun varsa, üzgün olduğunu belirt ve iade sürecinin başlatılacağını söyle.
    - Konuşmaların kısa, samimi ve çözüm odaklı olsun.
    \"\"\"

    try:
        response = text_model.generate_content([system_prompt, f"Müşteri: {user_message}"])
        return jsonify({"reply": response.text})
    except Exception as e:
        print(f"Chatbot Hatası: {e}")
        return jsonify({"reply": "Sistemde bir sorun oluştu, lütfen daha sonra tekrar deneyin."}), 500

if __name__ == '__main__':
    app.run(debug=True)
""",
    
    "products.json": """[
    {
        "id": 1,
        "name": "Bej Keten Gömlek",
        "price": "899.99 TL",
        "image": "static/img/gomlek1.jpg",
        "style_tags": ["bohem", "klasik", "minimalist", "günlük"],
        "color_tags": ["bej", "krem", "toprak"]
    },
    {
        "id": 2,
        "name": "Siyah Chino Pantolon",
        "price": "1299.90 TL",
        "image": "static/img/pantolon1.jpg",
        "style_tags": ["klasik", "modern", "ofis", "minimalist"],
        "color_tags": ["siyah", "antrasit", "koyu"]
    },
    {
        "id": 3,
        "name": "Beyaz Deri Sneaker",
        "price": "2499.00 TL",
        "image": "static/img/ayakkabi1.jpg",
        "style_tags": ["spor", "günlük", "modern", "minimalist"],
        "color_tags": ["beyaz", "krem"]
    },
    {
        "id": 4,
        "name": "Zümrüt Yeşili Saten Elbise",
        "price": "1899.50 TL",
        "image": "static/img/elbise1.jpg",
        "style_tags": ["şık", "gece", "özel gün", "klasik"],
        "color_tags": ["yeşil", "zümrüt", "koyu yeşil"]
    }
]""",

    "templates": {
        "layout.html": """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}StilDöngüsü{% endblock %}</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;700&display=swap" rel="stylesheet">
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>

    <nav class="navbar navbar-expand-lg navbar-light bg-light shadow-sm">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">StilDöngüsü 🌀</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link {% if request.path == '/' %}active{% endif %}" href="/">Stil Analisti</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.path == '/siparislerim' %}active{% endif %}" href="/siparislerim">Siparişlerim</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.path == '/satici-paneli' %}active{% endif %}" href="/satici-paneli">Satıcı Paneli</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <main class="container my-5">
        {% block content %}{% endblock %}
    </main>

    <footer class="bg-light text-center text-muted py-3 mt-5">
        <div class="container">
            <p>© 2025 StilDöngüsü - BTK Akademi Hackathon Projesi</p>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Custom JS -->
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
""",
        "index.html": """{% extends 'layout.html' %}
{% block title %}Stil ve Uyum Analisti{% endblock %}

{% block content %}
<div class="text-center">
    <h1 class="display-5 fw-bold">Stil ve Uyum Analisti (StyleSync)</h1>
    <p class="lead text-muted">Dolabınızdaki bir parçanın fotoğrafını yükleyin, ona en uygun kombinleri sizin için bulalım ve stil önerileri sunalım.</p>
</div>

<div class="row justify-content-center mt-4">
    <div class="col-md-8">
        <div class="card p-4 styled-form-container">
            <form id="style-form">
                <div class="mb-3">
                    <label for="image-upload" class="form-label fw-bold">Kombinlemek istediğiniz ürünün fotoğrafı:</label>
                    <input class="form-control" type="file" id="image-upload" name="file" accept="image/*" required>
                </div>
                <div class="d-grid">
                    <button type="submit" class="btn btn-primary btn-lg">Stilimi Analiz Et</button>
                </div>
            </form>
        </div>
    </div>
</div>

<div id="loading-spinner" class="text-center my-5 d-none">
    <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
    </div>
    <p class="mt-2">Stiliniz analiz ediliyor... Gemini sizin için çalışıyor!</p>
</div>

<div id="results-container" class="mt-5">
    <!-- Sonuçlar buraya dinamik olarak eklenecek -->
</div>
{% endblock %}
""",
        "siparislerim.html": """{% extends 'layout.html' %}
{% block title %}Siparişlerim{% endblock %}

{% block content %}
<h1 class="mb-4">Siparişlerim</h1>
<div class="list-group">
    {% for order in orders %}
    <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
        <div>
            <h5 class="mb-1">{{ order.product }}</h5>
            <p class="mb-1">Sipariş No: {{ order.id }}</p>
            <small>Durum: {{ order.status }}</small>
        </div>
        <button class="btn btn-outline-danger return-btn" 
                data-bs-toggle="modal" 
                data-bs-target="#return-chatbot-modal" 
                data-product-name="{{ order.product }}">
            İade Et
        </button>
    </div>
    {% endfor %}
</div>

<!-- ReturnLogic Chatbot Modal -->
<div class="modal fade" id="return-chatbot-modal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">🌀 Akıllı İade Asistanı (ReturnLogic)</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <div id="chat-window" class="chat-window mb-3">
                    <!-- Mesajlar buraya eklenecek -->
                </div>
                <div id="chat-typing-indicator" class="d-none">
                    <small class="text-muted">Asistan yazıyor...</small>
                </div>
                <div class="input-group">
                    <input type="text" id="chat-input" class="form-control" placeholder="Mesajınızı yazın...">
                    <button id="chat-send-btn" class="btn btn-primary">Gönder</button>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
""",
        "satici_paneli.html": """{% extends 'layout.html' %}
{% block title %}Satıcı Paneli - İade Raporu{% endblock %}

{% block content %}
<h1 class="mb-4">Aylık İade Analiz Raporu</h1>
<p class="text-muted">Bu rapor, <strong>Gemini</strong> tarafından iade konuşmaları analiz edilerek otomatik olarak oluşturulmuştur.</p>

<div class="card">
    <div class="card-header">
        <h5>Rapor Özeti: Mayıs 2025</h5>
    </div>
    <div class="card-body">
        <h6 class="card-title">Genel İade Sebepleri</h6>
        <div class="progress mb-3" style="height: 25px;">
            <div class="progress-bar bg-warning" role="progressbar" style="width: 55%" aria-valuenow="55" aria-valuemin="0" aria-valuemax="100">Beden Uyumsuzluğu (%55)</div>
            <div class="progress-bar bg-info" role="progressbar" style="width: 30%" aria-valuenow="30" aria-valuemin="0" aria-valuemax="100">Stil/Renk Beğenmeme (%30)</div>
            <div class="progress-bar bg-danger" role="progressbar" style="width: 15%" aria-valuenow="15" aria-valuemin="0" aria-valuemax="100">Diğer (%15)</div>
        </div>

        <hr>

        <h6 class="card-title mt-4">Ürün Bazlı Aksiyon Önerileri</h6>
        <div class="accordion" id="reportAccordion">
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne">
                        <strong>Ürün:</strong> Siyah Chino Pantolon - <strong>Ana Sorun:</strong> Kalıp Dar (%72)
                    </button>
                </h2>
                <div id="collapseOne" class="accordion-collapse collapse show" data-bs-parent="#reportAccordion">
                    <div class="accordion-body">
                        <strong>Gemini'nin Önerisi:</strong> Müşteriler bu ürünün kalıbını sürekli olarak 'beklenenden dar' veya 'slim fit gibi' olarak tanımlıyor. İade oranını düşürmek için ürün açıklamasına şu notun eklenmesi tavsiye edilir: <br>
                        <code>"<strong>Stil Notu:</strong> Bu ürün, vücuda oturan bir kesime sahiptir. Daha rahat bir görünüm için bir beden büyük tercih etmenizi öneririz."</code>
                    </div>
                </div>
            </div>
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTwo">
                        <strong>Ürün:</strong> Bej Keten Gömlek - <strong>Ana Sorun:</strong> Renk Algısı (%45)
                    </button>
                </h2>
                <div id="collapseTwo" class="accordion-collapse collapse" data-bs-parent="#reportAccordion">
                    <div class="accordion-body">
                         <strong>Gemini'nin Önerisi:</strong> Müşterilerin bir kısmı, ürün rengini 'ekranda göründüğünden daha sarı' olarak belirtmiş. Ürün görsellerine, farklı ışık koşullarında çekilmiş stüdyo ve dış mekan fotoğrafları eklenmesi, renk algısı konusundaki beklentiyi daha doğru yönetebilir.
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
""",
    },

    "static": {
        "css": {
            "style.css": """/* Google Font */
body {
    font-family: 'Montserrat', sans-serif;
    background-color: #f8f9fa;
}

/* Navbar */
.navbar-brand {
    color: #6f42c1 !important; /* Mor renk */
}

/* Ana Sayfa Stil Formu */
.styled-form-container {
    border: none;
    border-radius: 15px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.05);
    background: linear-gradient(145deg, #ffffff, #e6e6e6);
}

#image-upload {
    cursor: pointer;
}

.btn-primary {
    background-color: #6f42c1;
    border-color: #6f42c1;
    transition: all 0.3s ease;
}

.btn-primary:hover {
    background-color: #59359a;
    border-color: #59359a;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(111, 66, 193, 0.3);
}

/* Sonuç Kartları */
.result-card {
    border: none;
    border-radius: 10px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.result-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.12);
}

.result-card img {
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    aspect-ratio: 1 / 1;
    object-fit: cover;
}

.style-advice-card {
    background-color: #f0ebf9;
    border: 1px solid #dcd1f0;
}

/* Chatbot Modal */
.chat-window {
    height: 300px;
    border: 1px solid #ddd;
    border-radius: 5px;
    padding: 10px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
}

.chat-message {
    padding: 8px 12px;
    border-radius: 15px;
    margin-bottom: 10px;
    max-width: 80%;
    word-wrap: break-word;
}

.chat-message.user {
    background-color: #6f42c1;
    color: white;
    align-self: flex-end;
    border-bottom-right-radius: 3px;
}

.chat-message.bot {
    background-color: #e9ecef;
    color: #333;
    align-self: flex-start;
    border-bottom-left-radius: 3px;
}"""
        },
        "js": {
            "main.js": """document.addEventListener('DOMContentLoaded', () => {

    // --- Stil Analisti (StyleSync) Fonksiyonları ---
    const styleForm = document.getElementById('style-form');
    if (styleForm) {
        styleForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(styleForm);
            const spinner = document.getElementById('loading-spinner');
            const resultsContainer = document.getElementById('results-container');

            spinner.classList.remove('d-none');
            resultsContainer.innerHTML = '';

            try {
                const response = await fetch('/api/analyze-style', {
                    method: 'POST',
                    body: formData,
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'Bir hata oluştu.');
                }

                displayResults(data);

            } catch (error) {
                resultsContainer.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
            } finally {
                spinner.classList.add('d-none');
            }
        });
    }

    function displayResults(data) {
        const resultsContainer = document.getElementById('results-container');
        let productsHTML = '';

        data.matched_products.forEach(product => {
            productsHTML += `
                <div class="col-md-4 mb-4">
                    <div class="card result-card h-100">
                        <img src="${product.image}" class="card-img-top" alt="${product.name}">
                        <div class="card-body d-flex flex-column">
                            <h5 class="card-title">${product.name}</h5>
                            <p class="card-text text-muted flex-grow-1">Stil Etiketleri: ${product.style_tags.join(', ')}</p>
                            <div class="d-flex justify-content-between align-items-center">
                                <span class="fw-bold fs-5">${product.price}</span>
                                <a href="#" class="btn btn-sm btn-outline-primary">İncele</a>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        resultsContainer.innerHTML = `
            <div class="mb-4">
                <div class="card style-advice-card">
                     <div class="card-body">
                        <h5 class="card-title">✨ Gemini Stil Önerisi</h5>
                        <p class="card-text">${data.style_advice.replace(/\\n/g, '<br>')}</p>
                        <small class="text-muted">Bu öneri, <strong>${data.original_item.item_description}</strong> parçanıza göre özel olarak oluşturuldu.</small>
                     </div>
                </div>
            </div>
            <hr class="my-5">
            <h3 class="text-center mb-4">Uyumlu Ürünler</h3>
            <div class="row">
                ${productsHTML}
            </div>
        `;
    }

    // --- Akıllı İade Asistanı (ReturnLogic) Fonksiyonları ---
    const returnModal = document.getElementById('return-chatbot-modal');
    if (returnModal) {
        const chatWindow = document.getElementById('chat-window');
        const chatInput = document.getElementById('chat-input');
        const chatSendBtn = document.getElementById('chat-send-btn');
        let productName = '';

        // Modal açıldığında chat'i temizle ve başlangıç mesajını ekle
        returnModal.addEventListener('show.bs.modal', (event) => {
            productName = event.relatedTarget.getAttribute('data-product-name');
            chatWindow.innerHTML = '';
            addMessageToChat(`Merhaba! \\"${productName}\\" ürününü iade etme sebebinizi kısaca öğrenebilir miyim?`, 'bot');
        });
        
        // Gönder butonuna tıklandığında
        chatSendBtn.addEventListener('click', sendChatMessage);
        
        // Enter'a basıldığında
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendChatMessage();
            }
        });

        async function sendChatMessage() {
            const message = chatInput.value.trim();
            if (!message) return;
            
            addMessageToChat(message, 'user');
            chatInput.value = '';
            
            document.getElementById('chat-typing-indicator').classList.remove('d-none');
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: message, product: productName })
                });
                const data = await response.json();
                addMessageToChat(data.reply, 'bot');
            } catch (error) {
                addMessageToChat('Üzgünüm, şu anda size yardımcı olamıyorum. Lütfen daha sonra tekrar deneyin.', 'bot');
            } finally {
                document.getElementById('chat-typing-indicator').classList.add('d-none');
            }
        }
        
        function addMessageToChat(message, sender) {
            // [STIL_ANALISTI_LINK] gibi özel metinleri butona çevir
            if (message.includes('[STIL_ANALISTI_LINK]')) {
                message = message.replace(
                    '[STIL_ANALISTI_LINK]', 
                    '<br><a href="/" class="btn btn-success btn-sm mt-2">Stil Analistini Dene</a>'
                );
            }

            const messageElement = document.createElement('div');
            messageElement.classList.add('chat-message', sender);
            messageElement.innerHTML = message; // innerHTML kullanıyoruz çünkü link butonu ekleyebiliriz.
            chatWindow.appendChild(messageElement);
            chatWindow.scrollTop = chatWindow.scrollHeight; // Otomatik aşağı kaydır
        }
    }
});"""
        },
        "img": {
            # Bu klasör boş oluşturulacak, siz resimlerinizi ekleyeceksiniz.
        }
    }
}

def create_project_structure(base_path, structure):
    """
    Verilen sözlük yapısına göre dosya ve klasörleri özyineli olarak oluşturur.
    """
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            # Eğer içerik bir sözlük ise, bu bir klasördür
            os.makedirs(path, exist_ok=True)
            print(f"Klasör oluşturuldu: {path}")
            create_project_structure(path, content)
        else:
            # Eğer içerik bir string ise, bu bir dosyadır
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Dosya oluşturuldu: {path}")
            except Exception as e:
                print(f"HATA: {path} dosyası oluşturulamadı - {e}")

if __name__ == "__main__":
    current_directory = os.getcwd()
    print(f"Proje dosyaları şu konuma oluşturuluyor: {current_directory}")
    create_project_structure(current_directory, PROJECT_STRUCTURE)
    print("\nProje yapısı başarıyla oluşturuldu!")
    print("\nSONRAKİ ADIMLAR:")
    print("1. 'static/img/' klasörüne kendi ürün resimlerinizi ekleyin (örn: gomlek1.jpg).")
    print("2. '.env' dosyasını açıp Gemini API anahtarınızı girin.")
    print("3. Terminalde sanal ortamı kurup (`python -m venv venv`) aktif edin.")
    print("4. Gerekli kütüphaneleri yükleyin (`pip install -r requirements.txt`).")
    print("5. Projeyi başlatın (`flask run`).")
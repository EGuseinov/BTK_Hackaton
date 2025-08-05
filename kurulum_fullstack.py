import os
import sys

# Projenin tamamını oluşturan ana veri yapısı
FULL_PROJECT_STRUCTURE = {
    "backend": {
        ".env": "GEMINI_API_KEY=\"BURAYA_API_ANAHTARINIZI_YAPISTIRIN\"",
        "requirements.txt": """fastapi
uvicorn[standard]
python-dotenv
google-generativeai
Pillow
python-multipart""",
        "products.json": """[
    {
        "id": 1,
        "name": "Bej Keten Gömlek",
        "price": "899.99 TL",
        "image": "static/img/gomlek1.webp",
        "style_tags": ["bohem", "klasik", "minimalist", "günlük"],
        "color_tags": ["bej", "krem", "toprak"]
    },
    {
        "id": 2,
        "name": "Siyah Chino Pantolon",
        "price": "1299.90 TL",
        "image": "static/img/pantolon1.webp",
        "style_tags": ["klasik", "modern", "ofis", "minimalist"],
        "color_tags": ["siyah", "antrasit", "koyu"]
    },
    {
        "id": 3,
        "name": "Beyaz Deri Sneaker",
        "price": "2499.00 TL",
        "image": "static/img/ayakkabi1.jpeg",
        "style_tags": ["spor", "günlük", "modern", "minimalist"],
        "color_tags": ["beyaz", "krem"]
    },
    {
        "id": 4,
        "name": "Zümrüt Yeşili Saten Elbise",
        "price": "1899.50 TL",
        "image": "static/img/elbise1.jpeg",
        "style_tags": ["şık", "gece", "özel gün", "klasik"],
        "color_tags": ["yeşil", "zümrüt", "koyu yeşil"]
    }
]""",
        "main.py": """import os
import sys
import json
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services import gemini_service
from models.chat_models import ChatRequest, ChatResponse
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
        if not matched_products:
             raise HTTPException(status_code=404, detail="Veritabanımızda bu stile uygun ürün bulamadık.")
        style_advice_text = gemini_service.get_style_advice(
            analysis_data.get('item_description'),
            matched_products
        )
        return {
            "original_item": analysis_data,
            "style_advice": style_advice_text,
            "matched_products": matched_products
        }
    except Exception as e:
        print(f"Sunucu Hatası: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"Analiz sırasında bir sunucu hatası oluştu: {str(e)}")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_api(chat_request: ChatRequest):
    if not API_KEY:
         raise HTTPException(status_code=500, detail="Sunucu yapılandırma hatası: Gemini API anahtarı bulunamadı.")
    try:
        reply = gemini_service.get_chatbot_reply(chat_request.message)
        return ChatResponse(reply=reply)
    except Exception as e:
        print(f"Chatbot Sunucu Hatası: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail="Chatbot servisinde bir hata oluştu.")
""",
        "services": {
            "gemini_service.py": """import os
import json
import google.generativeai as genai
from PIL import Image
import io
import sys

vision_model = None
text_model = None
is_configured = False

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

def analyze_image_style(image_bytes: bytes) -> dict:
    if not is_configured:
        raise Exception("Gemini servisi yapılandırılmamış veya anahtar geçersiz.")
    img = Image.open(io.BytesIO(image_bytes))
    prompt = '''
    Bu resimdeki giysi veya mobilyayı analiz et. 
    Bana aşağıdaki formatta bir JSON çıktısı ver:
    {
      "item_description": "Örnek: Lacivert, yünlü, slim-fit bir blazer ceket",
      "style_tags": ["klasik", "minimalist", "ofis"],
      "color_tags": ["lacivert", "koyu mavi", "mavi"]
    }
    Sadece ve sadece JSON kodunu döndür, başka hiçbir metin veya markdown formatı ekleme.
    '''
    response = vision_model.generate_content([prompt, img])
    analysis_json_text = response.text.strip().replace("```json", "").replace("```", "")
    return json.loads(analysis_json_text)

def find_matching_products(analysis_data: dict, products_db: list) -> list:
    matched_products = []
    style_tags = set(analysis_data.get("style_tags", []))
    for product in products_db:
        product_style_tags = set(product.get("style_tags", []))
        if style_tags.intersection(product_style_tags):
            matched_products.append(product)
    return matched_products

def get_style_advice(description: str, matched_products: list) -> str:
    if not is_configured:
        raise Exception("Gemini servisi yapılandırılmamış veya anahtar geçersiz.")
    style_prompt = f\"\"\"
    Bir kullanıcı dolabındaki '{description}' için kombin önerisi arıyor.
    Ona uyumlu olarak şu ürünleri bulduk: {[p['name'] for p in matched_products]}.
    Bu ürünlerle ana parçanın neden şık duracağını anlatan, samimi ve ikna edici bir stil önerisi metni yaz.
    Metin, kullanıcıya ilham vermeli ve bu ürünleri satın almaya teşvik etmeli.
    \"\"\"
    style_advice_response = text_model.generate_content(style_prompt)
    return style_advice_response.text

def get_chatbot_reply(user_message: str) -> str:
    if not is_configured:
        raise Exception("Gemini servisi yapılandırılmamış veya anahtar geçersiz.")
    system_prompt = \"\"\"
    Sen, 'StilDöngüsü' adlı bir e-ticaret sitesinin 'Akıllı İade Asistanı'sın. Adın 'ReturnLogic'. 
    Görevin, müşterinin iade sebebini nazikçe anlamak ve mümkünse ona bir çözüm sunarak iadeyi engellemek.
    - Eğer sorun beden veya renk/stil uyumsuzluğu ise, iadeyi başlatabileceğini söyle ama hemen ardından ona 'Stil ve Uyum Analisti (StyleSync)' özelliğimizi öner. Bu özelliğin, elindeki başka bir parçanın fotoğrafını yükleyerek ona %100 uyumlu ürünler bulabileceğini anlat. Müşteriyi ana sayfaya yönlendirmek için '[STIL_ANALISTI_LINK]' metnini kullan.
    - Eğer ürün bozuksa veya farklı bir sorun varsa, üzgün olduğunu belirt ve iade sürecinin başlatılacağını söyle.
    - Konuşmaların kısa, samimi ve çözüm odaklı olsun.
    \"\"\"
    response = text_model.generate_content([system_prompt, f"Müşteri: {user_message}"])
    return response.text
"""
        },
        "models": {
            "chat_models.py": """from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    product: str

class ChatResponse(BaseModel):
    reply: str
"""
        }
    },
    "frontend": {
        "package.json": """{
  "name": "frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.7.2",
    "bootstrap": "^5.3.3",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.24.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "eslint": "^8.57.0",
    "eslint-plugin-react": "^7.34.2",
    "eslint-plugin-react-hooks": "^4.6.2",
    "eslint-plugin-react-refresh": "^0.4.7",
    "vite": "^5.3.1"
  }
}
""",
        ".gitignore": """# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

# Diagnostic reports (https://nodejs.org/api/report.html)
report.[0-9]*.[0-9]*.[0-9]*.[0-9]*.json

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Directory for instrumented libs generated by jscoverage/JSCover
lib-cov

# Coverage directory used by tools like istanbul
coverage
*.lcov

# nyc test coverage
.nyc_output

# Grunt intermediate storage (https://gruntjs.com/creating-plugins#storing-temporary-files)
.grunt

# Bower dependency directory (https://bower.io/)
bower_components

# node-waf configuration
.lock-wscript

# Compiled binary addons (https://nodejs.org/api/addons.html)
build/Release

# Dependency directories
node_modules/
jspm_packages/

# Snowpack dependency directory (https://snowpack.dev/)
web_modules/

# TypeScript cache
*.tsbuildinfo

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Optional stylelint cache
.stylelintcache

# Microbundle cache
.rpt2_cache/
.rts2_cache_cjs/
.rts2_cache_es/
.rts2_cache_umd/

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env
.env.development.local
.env.test.local
.env.production.local
.env.local

# Vite local development server environments file
.vite

# End-of-line markers
.DS_Store

# Vitest coverage directory
/coverage
""",
        "vite.config.js": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
""",
        "index.html": """<!doctype html>
<html lang="tr">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;700&display=swap" rel="stylesheet">
    <title>StilDöngüsü</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
""",
        "public": {
            "img": {
                ".gitkeep": "# Bu klasör ürün resimleri içindir."
            },
            "vite.svg": """<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" role="img" class="iconify iconify--logos" width="31.88" height="32" preserveAspectRatio="xMidYMid meet" viewBox="0 0 256 257"><defs><linearGradient id="IconifyId1813088fe1fbc01fb466" x1="-.828%" x2="57.636%" y1="7.652%" y2="78.411%"><stop offset="0%" stop-color="#41D1FF"></stop><stop offset="100%" stop-color="#BD34FE"></stop></linearGradient><linearGradient id="IconifyId1813088fe1fbc01fb467" x1="43.376%" x2="56.324%" y1="9.757%" y2="90.133%"><stop offset="0%" stop-color="#FFEA83"></stop><stop offset="8.333%" stop-color="#FFDD35"></stop><stop offset="100%" stop-color="#FFA800"></stop></linearGradient></defs><path fill="url(#IconifyId1813088fe1fbc01fb466)" d="M255.153 37.342L132.855 252.115a4.933 4.933 0 0 1-9.31-.001L1.247 37.342a4.934 4.934 0 0 1 4.311-7.343h244.004a4.934 4.934 0 0 1 4.311 7.343z"></path><path fill="url(#IconifyId1813088fe1fbc01fb467)" d="M185.432.775L132.855 252.115a4.933 4.933 0 0 1-9.31-.001l-11.82-50.607a4.934 4.934 0 0 1 2.943-5.62l70.55-25.545a4.934 4.934 0 0 0 2.65-4.846L185.432.775z"></path></svg>
"""
        },
        "src": {
            "index.css": """body {
    font-family: 'Montserrat', sans-serif;
    background-color: #f8f9fa;
}
.navbar-brand {
    color: #6f42c1 !important;
}
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
}
""",
            "main.jsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
""",
            "App.jsx": """import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import OrdersPage from './pages/OrdersPage';
import SellerDashboardPage from './pages/SellerDashboardPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="siparislerim" element={<OrdersPage />} />
          <Route path="satici-paneli" element={<SellerDashboardPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
""",
            "components": {
                "Layout.jsx": """import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import Footer from './Footer';

const Layout = () => {
  return (
    <>
      <Navbar />
      <main className="container my-5">
        <Outlet />
      </main>
      <Footer />
    </>
  );
};

export default Layout;
""",
                "Navbar.jsx": """import React from 'react';
import { NavLink } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-light shadow-sm">
      <div className="container">
        <NavLink className="navbar-brand fw-bold" to="/">StilDöngüsü 🌀</NavLink>
        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav ms-auto">
            <li className="nav-item">
              <NavLink className="nav-link" to="/">Stil Analisti</NavLink>
            </li>
            <li className="nav-item">
              <NavLink className="nav-link" to="/siparislerim">Siparişlerim</NavLink>
            </li>
            <li className="nav-item">
              <NavLink className="nav-link" to="/satici-paneli">Satıcı Paneli</NavLink>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
""",
                "Footer.jsx": """import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-light text-center text-muted py-3 mt-5">
      <div className="container">
        <p>© 2025 StilDöngüsü - BTK Akademi Hackathon Projesi</p>
      </div>
    </footer>
  );
};

export default Footer;
""",
                "ReturnModal.jsx": """import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const ReturnModal = ({ productName }) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const chatWindowRef = useRef(null);
    const modalRef = useRef(null);

    useEffect(() => {
        const modalElement = modalRef.current;
        const handleShowModal = (event) => {
            if (productName) {
                setMessages([{ text: `Merhaba! "${productName}" ürününü iade etme sebebinizi kısaca öğrenebilir miyim?`, sender: 'bot' }]);
                setInput('');
            }
        };

        modalElement.addEventListener('show.bs.modal', handleShowModal);
        return () => {
            modalElement.removeEventListener('show.bs.modal', handleShowModal);
        };
    }, [productName]);

    useEffect(() => {
        if (chatWindowRef.current) {
            chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSendMessage = async () => {
        if (!input.trim()) return;
        const userMessage = { text: input, sender: 'user' };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response = await axios.post('/api/chat', {
                message: input,
                product: productName
            });
            const botMessage = { text: response.data.reply, sender: 'bot' };
            setMessages(prev => [...prev, userMessage, botMessage]);
        } catch (error) {
            const errorMessage = { text: 'Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.', sender: 'bot' };
            setMessages(prev => [...prev, userMessage, errorMessage]);
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <div className="modal fade" id="return-chatbot-modal" tabIndex="-1" ref={modalRef}>
            <div className="modal-dialog modal-dialog-centered">
                <div className="modal-content">
                    <div className="modal-header">
                        <h5 className="modal-title">🌀 Akıllı İade Asistanı (ReturnLogic)</h5>
                        <button type="button" className="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div className="modal-body">
                        <div id="chat-window" className="chat-window mb-3" ref={chatWindowRef}>
                            {messages.map((msg, index) => (
                                <div key={index} className={`chat-message ${msg.sender}`} dangerouslySetInnerHTML={{ __html: msg.text.replace('[STIL_ANALISTI_LINK]', '<br/><a href="/" class="btn btn-success btn-sm mt-2">Stil Analistini Dene</a>') }}>
                                </div>
                            ))}
                            {loading && <div className="chat-message bot">...</div>}
                        </div>
                        <div className="input-group">
                            <input type="text" id="chat-input" className="form-control" placeholder="Mesajınızı yazın..." value={input} onChange={(e) => setInput(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()} />
                            <button id="chat-send-btn" className="btn btn-primary" onClick={handleSendMessage} disabled={loading}>Gönder</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ReturnModal;
"""
            },
            "pages": {
                "HomePage.jsx": """import React, { useState } from 'react';
import axios from 'axios';

const HomePage = () => {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Lütfen bir resim dosyası seçin.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    setLoading(true);
    setError('');
    setResults(null);

    try {
      const response = await axios.post('/api/analyze-style', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Analiz sırasında bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="text-center">
        <h1 className="display-5 fw-bold">Stil ve Uyum Analisti (StyleSync)</h1>
        <p className="lead text-muted">Dolabınızdaki bir parçanın fotoğrafını yükleyin, ona en uygun kombinleri sizin için bulalım ve stil önerileri sunalım.</p>
      </div>

      <div className="row justify-content-center mt-4">
        <div className="col-md-8">
          <div className="card p-4 styled-form-container">
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label htmlFor="image-upload" className="form-label fw-bold">Kombinlemek istediğiniz ürünün fotoğrafı:</label>
                <input className="form-control" type="file" id="image-upload" name="file" accept="image/*" required onChange={handleFileChange} />
              </div>
              <div className="d-grid">
                <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
                  {loading ? 'Analiz Ediliyor...' : 'Stilimi Analiz Et'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
      
      {loading && (
        <div id="loading-spinner" className="text-center my-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-2">Stiliniz analiz ediliyor... Gemini sizin için çalışıyor!</p>
        </div>
      )}

      {error && <div className="alert alert-danger mt-4">{error}</div>}

      {results && (
        <div id="results-container" className="mt-5">
          <div className="mb-4">
            <div className="card style-advice-card">
              <div className="card-body">
                <h5 className="card-title">✨ Gemini Stil Önerisi</h5>
                <p className="card-text" dangerouslySetInnerHTML={{ __html: results.style_advice.replace(/\\n/g, '<br>') }}></p>
                <small className="text-muted">Bu öneri, <strong>{results.original_item.item_description}</strong> parçanıza göre özel olarak oluşturuldu.</small>
              </div>
            </div>
          </div>
          <hr className="my-5" />
          <h3 className="text-center mb-4">Uyumlu Ürünler</h3>
          <div className="row">
            {results.matched_products.map((product) => (
              <div key={product.id} className="col-md-4 mb-4">
                <div className="card result-card h-100">
                  <img src={product.image.replace('static/img/', '/img/')} className="card-img-top" alt={product.name} />
                  <div className="card-body d-flex flex-column">
                    <h5 className="card-title">{product.name}</h5>
                    <p className="card-text text-muted flex-grow-1">Stil Etiketleri: {product.style_tags.join(', ')}</p>
                    <div className="d-flex justify-content-between align-items-center">
                      <span className="fw-bold fs-5">{product.price}</span>
                      <a href="#" className="btn btn-sm btn-outline-primary">İncele</a>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
};

export default HomePage;
""",
                "OrdersPage.jsx": """import React, { useState } from 'react';
import ReturnModal from '../components/ReturnModal';

const OrdersPage = () => {
    const [selectedProduct, setSelectedProduct] = useState(null);

    const dummyOrders = [
        { id: "TR12345", product: "Lacivert Blazer Ceket", status: "Teslim Edildi" },
        { id: "TR67890", product: "Beyaz Gömlek", status: "Teslim Edildi" }
    ];

    const handleReturnClick = (productName) => {
        setSelectedProduct(productName);
    };

    return (
        <>
            <h1 className="mb-4">Siparişlerim</h1>
            <div className="list-group">
                {dummyOrders.map((order) => (
                    <div key={order.id} className="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                        <div>
                            <h5 className="mb-1">{order.product}</h5>
                            <p className="mb-1">Sipariş No: {order.id}</p>
                            <small>Durum: {order.status}</small>
                        </div>
                        <button 
                            className="btn btn-outline-danger return-btn"
                            data-bs-toggle="modal"
                            data-bs-target="#return-chatbot-modal"
                            onClick={() => handleReturnClick(order.product)}>
                            İade Et
                        </button>
                    </div>
                ))}
            </div>
            <ReturnModal productName={selectedProduct} />
        </>
    );
};

export default OrdersPage;
""",
                "SellerDashboardPage.jsx": """import React from 'react';

const SellerDashboardPage = () => {
    return (
        <>
            <h1 className="mb-4">Aylık İade Analiz Raporu</h1>
            <p className="text-muted">Bu rapor, <strong>Gemini</strong> tarafından iade konuşmaları analiz edilerek otomatik olarak oluşturulmuştur.</p>

            <div className="card">
                <div className="card-header">
                    <h5>Rapor Özeti: Mayıs 2025</h5>
                </div>
                <div className="card-body">
                    <h6 className="card-title">Genel İade Sebepleri</h6>
                    <div className="progress mb-3" style={{ height: "25px" }}>
                        <div className="progress-bar bg-warning" role="progressbar" style={{ width: "55%" }} aria-valuenow="55" aria-valuemin="0" aria-valuemax="100">Beden Uyumsuzluğu (%55)</div>
                        <div className="progress-bar bg-info" role="progressbar" style={{ width: "30%" }} aria-valuenow="30" aria-valuemin="0" aria-valuemax="100">Stil/Renk Beğenmeme (%30)</div>
                        <div className="progress-bar bg-danger" role="progressbar" style={{ width: "15%" }} aria-valuenow="15" aria-valuemin="0" aria-valuemax="100">Diğer (%15)</div>
                    </div>
                    <hr />
                    <h6 className="card-title mt-4">Ürün Bazlı Aksiyon Önerileri</h6>
                    <div className="accordion" id="reportAccordion">
                        <div className="accordion-item">
                            <h2 className="accordion-header">
                                <button className="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne">
                                    <strong>Ürün:</strong> Siyah Chino Pantolon - <strong>Ana Sorun:</strong> Kalıp Dar (%72)
                                </button>
                            </h2>
                            <div id="collapseOne" className="accordion-collapse collapse show" data-bs-parent="#reportAccordion">
                                <div className="accordion-body">
                                    <strong>Gemini'nin Önerisi:</strong> Müşteriler bu ürünün kalıbını sürekli olarak 'beklenenden dar' veya 'slim fit gibi' olarak tanımlıyor. İade oranını düşürmek için ürün açıklamasına şu notun eklenmesi tavsiye edilir: <br />
                                    <code>"<strong>Stil Notu:</strong> Bu ürün, vücuda oturan bir kesime sahiptir. Daha rahat bir görünüm için bir beden büyük tercih etmenizi öneririz."</code>
                                </div>
                            </div>
                        </div>
                        <div className="accordion-item">
                            <h2 className="accordion-header">
                                <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTwo">
                                    <strong>Ürün:</strong> Bej Keten Gömlek - <strong>Ana Sorun:</strong> Renk Algısı (%45)
                                </button>
                            </h2>
                            <div id="collapseTwo" className="accordion-collapse collapse" data-bs-parent="#reportAccordion">
                                <div className="accordion-body">
                                    <strong>Gemini'nin Önerisi:</strong> Müşterilerin bir kısmı, ürün rengini 'ekranda göründüğünden daha sarı' olarak belirtmiş. Ürün görsellerine, farklı ışık koşullarında çekilmiş stüdyo ve dış mekan fotoğrafları eklenmesi, renk algısı konusundaki beklentiyi daha doğru yönetebilir.
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
};

export default SellerDashboardPage;
"""
            }
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
            os.makedirs(path, exist_ok=True)
            print(f"Klasör oluşturuldu: {path}")
            create_project_structure(path, content)
        else:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Dosya oluşturuldu:  {path}")
            except Exception as e:
                print(f"HATA: {path} dosyası oluşturulamadı - {e}")


if __name__ == "__main__":
    root_dir = "StilDongusu-FullStack"
    if os.path.exists(root_dir):
        print(f"'{root_dir}' klasörü zaten mevcut. Lütfen devam etmeden önce bu klasörü silin veya yeniden adlandırın.")
        sys.exit(1)
        
    print(f"Proje dosyaları '{root_dir}' adlı yeni bir klasörde oluşturuluyor...")
    print("-" * 60)
    os.makedirs(root_dir, exist_ok=True)
    create_project_structure(root_dir, FULL_PROJECT_STRUCTURE)
    print("-" * 60)
    print("\n✅ Proje yapısı başarıyla oluşturuldu!")
    print("\n🚀 SONRAKİ ADIMLAR (Sırayla takip edin):\n")
    print("--- BACKEND (FastAPI) KURULUMU ---")
    print("1. Yeni bir terminal açın ve backend klasörüne gidin:")
    print(f"   cd {root_dir}/backend")
    print("2. Sanal bir ortam oluşturun:")
    print("   python -m venv venv")
    print("3. Sanal ortamı aktif edin:")
    print("   # Windows için: .\\venv\\Scripts\\activate")
    print("   # MacOS/Linux için: source venv/bin/activate")
    print("4. Gerekli kütüphaneleri yükleyin:")
    print("   pip install -r requirements.txt")
    print("5. '.env' dosyasını açıp kendi Gemini API anahtarınızı girin.")
    print("6. Backend sunucusunu BAŞLATIN:")
    print("   uvicorn main:app --reload\n")
    
    print("--- FRONTEND (React) KURULUMU ---")
    print("1. YENİ BİR terminal daha açın ve frontend klasörüne gidin:")
    print(f"   cd {root_dir}/frontend")
    print("2. Gerekli tüm node modüllerini yükleyin (bu işlem biraz sürebilir):")
    print("   npm install")
    print("3. Ürün resimlerinizi 'frontend/public/img' klasörüne ekleyin.")
    print("4. Frontend geliştirme sunucusunu BAŞLATIN:")
    print("   npm run dev\n")

    print("--- KULLANIM ---")
    print("✅ Her iki sunucu da çalışırken, tarayıcınızda 'npm run dev' komutunun verdiği adrese (genellikle http://localhost:5173) gidin.")
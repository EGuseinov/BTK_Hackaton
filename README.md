StilDöngüsü 🌀
StilDöngüsü, Google Gemini yapay zeka modeli ile güçlendirilmiş, e-ticaretin temel sorunlarına yenilikçi çözümler sunan akıllı bir stil ve alışveriş platformudur. Bu proje, standart bir e-ticaret sitesi olmanın ötesine geçerek, kullanıcılar için kişisel bir stil asistanı, satıcılar için ise veri odaklı bir iş zekası aracı olmayı hedefler.

(Proje videosunu buraya ekleyebilirsiniz. Yukarıdaki linki kendi YouTube linkinizle değiştirin. Geçici olarak bir resim eklenmiştir.)
🎯 Projenin Amacı
Günümüz e-ticaret platformları, kullanıcılara sonsuz seçenek sunarken, iki temel sorunu çözmekte yetersiz kalıyor:
Kişiselleştirme Eksikliği: "Bu ürün bana yakışır mı?" endişesi, yüksek iade oranlarının ve müşteri memnuniyetsizliğinin ana nedenidir.
Veri Döngüsünün Kırılması: Müşteri geri bildirimleri (özellikle iade nedenleri), genellikle bir maliyet kalemi olarak görülür ve bir sonraki üretim ve pazarlama döngüsünü beslemek için etkin bir şekilde kullanılmaz.
StilDöngüsü, bu iki sorunu çözmek için tasarlanmıştır. Müşterinin stilini anlayarak başlayan, ona özel öneriler sunan ve geri bildirimlerini satıcı için stratejik bir değere dönüştüren, kendi kendini iyileştiren bir ekosistem yaratır.
✨ Temel Özellikler
Platformumuz, Gemini'nin multimodal yeteneklerini kullanarak e-ticaret yolculuğunun her adımını akıllı hale getirir:
1. 👕 Tek Parça Stil Analizi
Kullanıcı, beğendiği bir ürünün fotoğrafını yükler.
Gemini Vision, görseli analiz ederek ürünün stilini, uygun olduğu ortamları ve mevsimleri belirler.
Kullanıcıya, bu parçayla oluşturulabilecek kombinler ve uyumlu ürünler sunulur.
2. 📡 Stil Radarı (Kişisel Stil Profili)
Kullanıcı, gardırobundan sevdiği 2-5 farklı kombininin fotoğrafını yükler.
Gemini, bu çoklu görselleri analiz ederek kullanıcının baskın stillerini, renk paletini ve kesim tercihlerini içeren kişisel bir Stil Radarı oluşturur.
Bu profil, tüm site deneyimini kişiselleştirmek için kullanılır.
3. 📅 Etkinlik ve Mekan Stilisti
Kullanıcı, "Haftaya Kapadokya'da bir düğüne gideceğim" gibi doğal bir dille isteğini belirtir.
Gemini, kullanıcının isteğini, stil profilini ve veritabanındaki ürünleri analiz ederek, o etkinliğe özel 3 farklı görsel kombin önerisi sunar.
4. 📐 Gemini Fit Puanı
Kullanıcı, bir ürün sayfasında kendi vücut tipini seçer.
Gemini, ürünün kesim ve materyal bilgileriyle kullanıcının vücut tipini karşılaştırarak 10 üzerinden bir "Fit Puanı" ve nedenini açıklayan bir metin üretir.
Bu özellik, beden uyumsuzluğuna bağlı iadeleri azaltmayı hedefler.
5. 💬 Akıllı İade Asistanı (ReturnLogic)
İade sürecinde kullanıcı, bir form doldurmak yerine yapay zeka destekli bir chatbot ile konuşur.
Gemini, kullanıcının mesajını analiz ederek iadenin altında yatan asıl niyeti (BEDEN, RENK_STIL vb.) anlar ve kategorize eder.
6. 📊 Stratejik Satıcı Paneli
Tüm iade konuşmaları, satış trendleri ve popüler arama terimleri satıcı panelinde toplanır.
Gemini, bu büyük veriyi analiz ederek satıcılara sadece raporlar değil, doğrudan aksiyon alınabilir stratejik öneriler sunar:
Trend Alarmı: "Oversize ceket aramaları artıyor, yeni koleksiyona ekleyin."
Stok Optimizasyonu: "Bu üründeki satışlar yavaşladı, indirim kampanyası düzenleyin."
Ürün Geliştirme: "'Kalıp dar' şikayetleri arttı, ürün açıklamasına 'bir beden büyük tercih edin' notu ekleyin."
🛠️ Teknik Yapı
Proje, modern ve ölçeklenebilir teknolojiler kullanılarak geliştirilmiştir.
Backend:
Framework: Python, FastAPI
Yapay Zeka: Google Gemini 1.5 Flash API
Kütüphaneler: google-generativeai, uvicorn, python-dotenv
Frontend:
Framework: React (Vite ile)
Kütüphaneler: react-router-dom, axios
Stil: Bootstrap, Custom CSS
Mimarî Akış
Kullanıcı Etkileşimi (React): Kullanıcı, arayüz üzerinden bir resim yükler veya metin girer.
API İsteği (FastAPI): Frontend, backend'e güvenli bir API isteği gönderir.
Yapay Zeka İşlemi (Gemini): FastAPI sunucusu, gelen veriyi işleyerek Gemini API için uygun bir prompt oluşturur ve isteği gönderir.
Yanıt ve Sunum (React): Gemini'den gelen yapısal JSON yanıtı, backend tarafından işlenir ve frontend'e gönderilerek kullanıcıya şık ve anlaşılır bir şekilde sunulur.
🚀 Kurulum ve Başlatma
Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin.
Gereksinimler
Python 3.10+
Node.js 18+
Google Gemini API Anahtarı
Backend Kurulumu
Proje dizinine gidin:
Generated bash
cd backend
Use code with caution.
Bash
Sanal ortam oluşturun ve aktif edin:
Generated bash
python -m venv venv
# Windows için:
venv\Scripts\activate
# macOS/Linux için:
source venv/bin/activate
Use code with caution.
Bash
Gerekli Python paketlerini yükleyin:
Generated bash
pip install -r requirements.txt
Use code with caution.
Bash
.env dosyasını oluşturun:
backend klasöründe .env adında bir dosya oluşturun.
İçine Gemini API anahtarınızı ekleyin:
Generated code
GEMINI_API_KEY="YOUR_API_KEY_HERE"
Use code with caution.
Backend sunucusunu başlatın:
Generated bash
uvicorn main:app --reload
Use code with caution.
Bash
Sunucu http://127.0.0.1:8000 adresinde çalışmaya başlayacaktır.
Frontend Kurulumu
Yeni bir terminal açın ve frontend dizinine gidin:
Generated bash
cd frontend
Use code with caution.
Bash
Gerekli Node.js paketlerini yükleyin:
Generated bash
npm install
Use code with caution.
Bash
Frontend geliştirme sunucusunu başlatın:
Generated bash
npm run dev
Use code with caution.
Bash
Uygulama http://localhost:5173 adresinde açılacaktır ve API istekleri otomatik olarak backend'e yönlendirilecektir.
🤝 Katkıda Bulunma
Bu proje bir hackathon için geliştirilmiş olup, topluluk katkılarına açıktır. Katkıda bulunmak isterseniz, lütfen bir "issue" açın veya bir "pull request" gönderin.
📄 Lisans
Bu proje MIT Lisansı ile lisanslanmıştır.

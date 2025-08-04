document.addEventListener('DOMContentLoaded', () => {

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
                    // FastAPI hata mesajını 'detail' anahtarıyla gönderir
                    throw new Error(data.detail || 'Bir hata oluştu.');
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
                        <p class="card-text">${data.style_advice.replace(/\n/g, '<br>')}</p>
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
            addMessageToChat(`Merhaba! \"${productName}\" ürününü iade etme sebebinizi kısaca öğrenebilir miyim?`, 'bot');
            chatInput.value = ''; // Inputu temizle
        });
        
        // Gönder butonuna tıklandığında
        chatSendBtn.addEventListener('click', sendChatMessage);
        
        // Enter'a basıldığında
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
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

                if (!response.ok) {
                    throw new Error(data.detail || 'Chatbot ile iletişim kurulamadı.');
                }
                
                addMessageToChat(data.reply, 'bot');

            } catch (error) {
                addMessageToChat(`Üzgünüm, bir hata oluştu: ${error.message}. Lütfen daha sonra tekrar deneyin.`, 'bot');
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
});
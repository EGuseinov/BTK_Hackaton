import React, { useState, useEffect, useRef } from 'react';
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

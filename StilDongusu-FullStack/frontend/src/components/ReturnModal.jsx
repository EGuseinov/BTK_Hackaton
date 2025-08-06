import React, { useState, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom'; // FIX: Import createPortal
import axios from 'axios';

const ReturnModal = ({ productName }) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const chatWindowRef = useRef(null);

    useEffect(() => {
        if (productName) {
            setMessages([{ text: `Merhaba! "${productName}" ürününü iade etme sebebinizi kısaca öğrenebilir miyim?`, sender: 'bot' }]);
            setInput('');
        }
    }, [productName]);

    useEffect(() => {
        if (chatWindowRef.current) {
            chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSendMessage = async () => {
        const messageToSend = input.trim();
        if (!messageToSend || loading) return;

        const userMessage = { text: messageToSend, sender: 'user' };
        setMessages(prevMessages => [...prevMessages, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response = await axios.post('/api/chat', {
                message: messageToSend,
                product: productName
            });
            const botMessage = { text: response.data.reply_text, sender: 'bot' };
            setMessages(prevMessages => [...prevMessages, botMessage]);
        } catch (error) {
            const errorMessage = { text: 'Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.', sender: 'bot' };
            setMessages(prevMessages => [...prevMessages, errorMessage]);
        } finally {
            setLoading(false);
        }
    };
    
    // FIX: Wrap the entire modal JSX in createPortal
    return createPortal(
        <div className="modal fade" id="return-chatbot-modal" tabIndex="-1">
            <div className="modal-dialog modal-dialog-centered">
                <div className="modal-content">
                    <div className="modal-header border-0">
                        <h5 className="modal-title">🌀 Akıllı İade Asistanı (ReturnLogic)</h5>
                        <button type="button" className="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div className="modal-body pt-0">
                        <div id="chat-window" className="chat-window mb-3" ref={chatWindowRef}>
                            {messages.map((msg, index) => (
                                <div key={index} className={`chat-message ${msg.sender}`} dangerouslySetInnerHTML={{ __html: msg.text.replace('[STIL_ANALISTI_LINK]', '<br/><a href="/" class="btn btn-success btn-sm mt-2">Stil Analistini Dene</a>') }}>
                                </div>
                            ))}
                            {loading && <div className="chat-message bot">...</div>}
                        </div>
                        <div className="input-group">
                            <input 
                                type="text" 
                                id="chat-input" 
                                className="form-control" 
                                placeholder="Mesajınızı yazın..." 
                                value={input} 
                                onChange={(e) => setInput(e.target.value)} 
                                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                                disabled={loading}
                            />
                            <button className="btn glow-button" onClick={handleSendMessage} disabled={loading}>
                                {loading ? '...' : 'Gönder'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>,
        document.getElementById('modal-root') // Tell the portal where to render
    );
};

export default ReturnModal;
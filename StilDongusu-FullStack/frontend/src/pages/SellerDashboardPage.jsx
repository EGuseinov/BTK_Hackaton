import React, { useState, useEffect } from 'react';
import axios from 'axios';

// NEW: Helper objects to make the chart look nice
const intentLabels = {
    "BEDEN": "Beden Uyumsuzluğu",
    "RENK_STIL": "Stil/Renk Beğenmeme",
    "KUSURLU_URUN": "Kusurlu Ürün",
    "BEKLENTI_FARKI": "Beklenti Farkı",
    "COZULEBILIR_SORUN": "Çözülebilir Sorun",
    "BELIRSIZ": "Diğer/Belirsiz",
};

const intentColors = {
    "BEDEN": "#ffc107",
    "RENK_STIL": "#0dcaf0",
    "KUSURLU_URUN": "#dc3545",
    "BEKLENTI_FARKI": "#fd7e14",
    "COZULEBILIR_SORUN": "#198754",
    "BELIRSIZ": "#6c757d",
};


const SellerDashboardPage = () => {
    // NEW: State for holding analytics data, loading, and error status
    const [analytics, setAnalytics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    // NEW: useEffect to fetch data when the component mounts
    useEffect(() => {
        const fetchAnalytics = async () => {
            try {
                setLoading(true);
                const response = await axios.get('/api/return-analytics');
                setAnalytics(response.data);
                setError('');
            } catch (err) {
                setError('Rapor verileri alınırken bir hata oluştu.');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchAnalytics();
    }, []); // Empty array means this runs once on mount

    return (
        <div className="fade-in">
            <h1 className="display-5 fw-bold text-center mb-3">Aylık İade Analiz Raporu</h1>
            <p className="lead text-muted text-center mb-5">
              Bu rapor, <strong>Gemini</strong> tarafından iade konuşmaları analiz edilerek otomatik olarak oluşturulmuştur.
            </p>

            <div className="futuristic-card mb-4">
                <h4 className="mb-3">Rapor Özeti: Mayıs 2025</h4>
                {loading && <p>Rapor yükleniyor...</p>}
                {error && <div className="alert alert-danger">{error}</div>}
                
                {/* NEW: Dynamic rendering based on fetched data */}
                {analytics && (
                    <>
                        <h6 className="card-title text-muted">
                            Toplam İade Sayısı: {analytics.total_returns}
                        </h6>
                        {analytics.total_returns > 0 ? (
                            <div className="progress mt-3" style={{ height: "25px", backgroundColor: "var(--background-color)" }}>
                                {analytics.reasons.map(reason => (
                                    <div 
                                        key={reason.intent}
                                        className="progress-bar" 
                                        role="progressbar" 
                                        style={{ 
                                            width: `${reason.percentage}%`, 
                                            backgroundColor: intentColors[reason.intent] || '#6c757d' 
                                        }}
                                    >
                                        {intentLabels[reason.intent] || reason.intent} ({reason.percentage}%)
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="mt-3">Henüz iade verisi bulunmamaktadır.</p>
                        )}
                    </>
                )}
            </div>

            {/* Note: The product-specific advice below remains static for now, as it requires a more complex backend. */}
            <div className="futuristic-card">
                <h4 className="mb-4">Ürün Bazlı Aksiyon Önerileri (Statik Örnek)</h4>
                <div className="accordion accordion-flush" id="reportAccordion">
                     {/* ... accordion items remain the same ... */}
                     <div className="accordion-item" style={{backgroundColor: 'transparent'}}>
                        <h2 className="accordion-header">
                            <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" style={{backgroundColor: 'var(--surface-color)', color: 'var(--text-color)', boxShadow: 'none'}}>
                                <strong>Ürün:</strong> Siyah Chino Pantolon - <strong className="ms-2 text-danger">Ana Sorun:</strong> Kalıp Dar (%72)
                            </button>
                        </h2>
                        <div id="collapseOne" className="accordion-collapse collapse" data-bs-parent="#reportAccordion">
                            <div className="accordion-body border-top border-secondary border-opacity-25">
                                <strong>Gemini'nin Önerisi:</strong> Müşteriler bu ürünün kalıbını sürekli olarak 'beklenenden dar' veya 'slim fit gibi' olarak tanımlıyor. İade oranını düşürmek için ürün açıklamasına şu notun eklenmesi tavsiye edilir: <br />
                                <code className="d-block bg-dark p-2 rounded mt-2">"<strong>Stil Notu:</strong> Bu ürün, vücuda oturan bir kesime sahiptir. Daha rahat bir görünüm için bir beden büyük tercih etmenizi öneririz."</code>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SellerDashboardPage;
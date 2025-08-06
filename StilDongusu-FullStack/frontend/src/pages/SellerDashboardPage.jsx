import React, { useState, useEffect } from 'react';
import axios from 'axios';

const intentLabels = {
    "BEDEN": "Beden Uyumsuzluğu",
    "RENK_STIL": "Stil/Renk Beğenmeme",
    "KUSURLU_URUN": "Kusurlu Ürün",
    "BEKLENTI_FARKI": "Beklenti Farkı",
    "COZULEBILIR_SORUN": "Çözülebilir Sorun",
    "BELIRSIZ": "Diğer/Belirsiz",
};

const SellerDashboardPage = () => {
    const [analytics, setAnalytics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchAnalytics = async () => {
            try {
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
    }, []);

    return (
        <div className="fade-in">
            <h1 className="display-5 fw-bold text-center mb-3">Stratejik İade Analiz Raporu</h1>
            <p className="lead text-muted text-center mb-5">
              Bu rapor, <strong>Gemini</strong> tarafından satış, arama ve iade verileri analiz edilerek gerçek zamanlı olarak oluşturulmuştur.
            </p>

            {loading && <div className="text-center"><div className="pulsing-loader"></div><p className="mt-3">Analiz Raporu Yükleniyor...</p></div>}
            {error && <div className="alert alert-danger">{error}</div>}
            
            {analytics && (
                <>
                {analytics.strategic_overview && (
                    <div className="futuristic-card mb-4">
                        <h4 className="mb-3">📈 Gemini Stratejik Öngörü Raporu</h4>
                        <div className="row">
                            <div className="col-md-4 mb-3 mb-md-0">
                                <h6 className="text-warning">Trend Alarmı</h6>
                                <p>{analytics.strategic_overview.trend_alarm}</p>
                            </div>
                            <div className="col-md-4 mb-3 mb-md-0">
                                <h6 className="text-info">Stok Optimizasyonu</h6>
                                <p>{analytics.strategic_overview.stock_optimization}</p>
                            </div>
                            <div className="col-md-4">
                                <h6 className="text-success">Ürün Geliştirme</h6>
                                <p>{analytics.strategic_overview.product_development}</p>
                            </div>
                        </div>
                    </div>
                )}
                
                {analytics.total_returns > 0 ? (
                    <div className="futuristic-card">
                        <h4 className="mb-4">Ürün Bazlı Detaylı İade Analizi</h4>
                        <p className="text-muted">Toplam İade Sayısı: {analytics.total_returns}</p>
                        <div className="accordion accordion-flush" id="reportAccordion">
                            {analytics.product_analysis.map((product, index) => (
                                <div key={product.product_name} className="accordion-item mt-2" style={{backgroundColor: 'transparent'}}>
                                    <h2 className="accordion-header">
                                        <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target={`#collapse-${index}`} style={{backgroundColor: 'var(--surface-color)', color: 'var(--text-color)', boxShadow: 'none'}}>
                                            <strong>{product.product_name}</strong>
                                            <span className="ms-auto me-3 badge bg-danger">{product.total_returns} iade</span>
                                        </button>
                                    </h2>
                                    <div id={`collapse-${index}`} className="accordion-collapse collapse" data-bs-parent="#reportAccordion">
                                        <div className="accordion-body border-top border-secondary border-opacity-25">
                                            <h5>Detaylı İade Nedenleri:</h5>
                                            {product.reasons.map(reason => (
                                                <div key={reason.intent}>
                                                    <span>{intentLabels[reason.intent] || reason.intent}</span>
                                                    <div className="progress mb-2" style={{height: "15px"}}>
                                                        <div className="progress-bar bg-secondary" style={{width: `${reason.percentage}%`}}>{reason.percentage}%</div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                ) : (
                    <div className="futuristic-card text-center">
                        <h4>Harika Haber!</h4>
                        <p>Sistemde henüz hiç iade talebi bulunmuyor.</p>
                    </div>
                )}
                </>
            )}
        </div>
    );
};

export default SellerDashboardPage;
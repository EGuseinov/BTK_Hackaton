import React from 'react';

const SellerDashboardPage = () => {
    return (
        <div className="fade-in">
            <h1 className="display-5 fw-bold text-center mb-3">Aylık İade Analiz Raporu</h1>
            <p className="lead text-muted text-center mb-5">
              Bu rapor, <strong>Gemini</strong> tarafından iade konuşmaları analiz edilerek otomatik olarak oluşturulmuştur.
            </p>

            <div className="futuristic-card mb-4">
                <h4 className="mb-3">Rapor Özeti: Mayıs 2025</h4>
                <h6 className="card-title text-muted">Genel İade Sebepleri</h6>
                <div className="progress mb-3" style={{ height: "25px", backgroundColor: "var(--background-color)" }}>
                    <div className="progress-bar" role="progressbar" style={{ width: "55%", backgroundColor: "#ffc107" }} >Beden Uyumsuzluğu (%55)</div>
                    <div className="progress-bar" role="progressbar" style={{ width: "30%", backgroundColor: "#0dcaf0" }} >Stil/Renk Beğenmeme (%30)</div>
                    <div className="progress-bar" role="progressbar" style={{ width: "15%", backgroundColor: "#dc3545" }} >Diğer (%15)</div>
                </div>
            </div>

            <div className="futuristic-card">
                <h4 className="mb-4">Ürün Bazlı Aksiyon Önerileri</h4>
                <div className="accordion accordion-flush" id="reportAccordion">
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
                    <div className="accordion-item mt-2" style={{backgroundColor: 'transparent'}}>
                        <h2 className="accordion-header">
                            <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTwo" style={{backgroundColor: 'var(--surface-color)', color: 'var(--text-color)', boxShadow: 'none'}}>
                                <strong>Ürün:</strong> Bej Keten Gömlek - <strong className="ms-2 text-warning">Ana Sorun:</strong> Renk Algısı (%45)
                            </button>
                        </h2>
                        <div id="collapseTwo" className="accordion-collapse collapse" data-bs-parent="#reportAccordion">
                            <div className="accordion-body border-top border-secondary border-opacity-25">
                                 <strong>Gemini'nin Önerisi:</strong> Müşterilerin bir kısmı, ürün rengini 'ekranda göründüğünden daha sarı' olarak belirtmiş. Ürün görsellerine, farklı ışık koşullarında çekilmiş stüdyo ve dış mekan fotoğrafları eklenmesi, renk algısı konusundaki beklentiyi daha doğru yönetebilir.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SellerDashboardPage;
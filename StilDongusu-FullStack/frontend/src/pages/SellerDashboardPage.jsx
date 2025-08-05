import React from 'react';

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

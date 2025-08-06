// HomePage.jsx

import React, { useState } from 'react';
import axios from 'axios';

const HomePage = () => {
  // --- STATE'ler ---
  const [file, setFile] = useState(null); // Tekli analiz için
  const [files, setFiles] = useState(null); // Stil Radarı için
  const [results, setResults] = useState(null);
  const [profile, setProfile] = useState(null); // YENİ: Stil profili state'i
  const [visualCombo, setVisualCombo] = useState(null); // YENİ: Kombin görseli state'i
  const [loading, setLoading] = useState(false);
  const [profileLoading, setProfileLoading] = useState(false);
  const [comboLoading, setComboLoading] = useState(false);
  const [error, setError] = useState('');

  // --- HANDLER'lar ---
  const handleFileChange = (e) => setFile(e.target.files[0]);
  const handleFilesChange = (e) => setFiles(e.target.files);

  const handleSingleAnalysis = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Lütfen analiz için bir resim dosyası seçin.');
      return;
    }
    const formData = new FormData();
    formData.append('file', file);
    setLoading(true);
    setError('');
    setResults(null);
    setProfile(null);
    setVisualCombo(null);
    try {
      const response = await axios.post('/api/analyze-style', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Analiz sırasında bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  const handleProfileAnalysis = async (e) => {
    e.preventDefault();
    if (!files || files.length < 2) {
      setError('Lütfen stil radarınız için en az 2 resim seçin.');
      return;
    }
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }
    setProfileLoading(true);
    setError('');
    setResults(null);
    setProfile(null);
    setVisualCombo(null);
     try {
      const response = await axios.post('/api/create-style-profile', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setProfile(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Stil profili oluşturulurken bir hata oluştu.');
    } finally {
      setProfileLoading(false);
    }
  };
  
  const handleVisualizeCombo = async () => {
    if (!results) return;
    setComboLoading(true);
    setVisualCombo(null);
    try {
        const payload = {
            main_item: results.image_analysis.item_description,
            matched_items: results.matched_products.map(p => p.name)
        };
        const response = await axios.post('/api/generate-visual-combo', payload);
        setVisualCombo(response.data);
    } catch(err) {
        setError("Kombin görselleştirilirken bir hata oluştu.");
    } finally {
        setComboLoading(false);
    }
  };

  return (
    <div className="fade-in">
      <div className="text-center">
        <h1 className="display-4 fw-bold">StilDöngüsü</h1>
        <p className="lead text-muted">Yapay Zeka Destekli Kişisel Stil Asistanınız</p>
      </div>

      {/* --- YENİ BÖLÜMLENDİRME --- */}
      <div className="row justify-content-center mt-5">
        {/* TEK PARÇA ANALİZİ */}
        <div className="col-lg-6 mb-4">
          <div className="futuristic-card h-100">
            <h4 className="text-center mb-3">Tek Parça Analizi</h4>
            <p className="text-center text-muted small">Bir ürünün fotoğrafını yükleyerek anında stil önerileri alın.</p>
            <form onSubmit={handleSingleAnalysis}>
              <div className="mb-3">
                <input className="form-control" type="file" accept="image/*" required onChange={handleFileChange} />
              </div>
              <div className="d-grid">
                <button type="submit" className="glow-button" disabled={loading}>
                  {loading ? 'Analiz Ediliyor...' : 'Stilimi Analiz Et'}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* STİL RADARI */}
        <div className="col-lg-6 mb-4">
          <div className="futuristic-card h-100">
             <h4 className="text-center mb-3">Stil Radarı Oluştur</h4>
             <p className="text-center text-muted small">Sevdiğiniz 2-5 kombininizi yükleyin, kişisel stil profilinizi keşfedin.</p>
            <form onSubmit={handleProfileAnalysis}>
              <div className="mb-3">
                <input className="form-control" type="file" accept="image/*" required multiple onChange={handleFilesChange} />
              </div>
              <div className="d-grid">
                <button type="submit" className="glow-button" disabled={profileLoading}>
                  {profileLoading ? 'Profil Oluşturuluyor...' : 'Stil Radarımı Oluştur'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
      
      {/* --- YÜKLENİYOR GÖSTERGELERİ --- */}
      {(loading || profileLoading) && (
        <div className="text-center my-5">
          <div className="pulsing-loader"></div>
          <p className="mt-3">Gemini sizin için çalışıyor, stiliniz çözümleniyor...</p>
        </div>
      )}

      {error && <div className="alert alert-danger mt-4">{error}</div>}

      {/* --- SONUÇ EKRANLARI --- */}
      <div className="mt-5 pt-4 fade-in">
        {/* Stil Radarı Sonucu */}
        {profile && (
            <div className="results-card mb-5">
                <h2 className="text-center mb-3 display-6">✨ Kişisel Stil Radarınız ✨</h2>
                <p className="lead text-center text-muted">"{profile.summary}"</p>
                <hr className="my-4" />
                <div className="row">
                    <div className="col-md-6">
                        <h5>Stil Dağılımınız:</h5>
                        {profile.style_profile.map(item => (
                            <div key={item.style} className="mb-2">
                                <span className="text-capitalize">{item.style.replace('_', ' ')}</span>
                                <div className="progress" style={{height: "20px"}}>
                                    <div className="progress-bar" style={{width: `${item.percentage}%`, backgroundColor: 'var(--primary-color)'}}>{item.percentage}%</div>
                                </div>
                            </div>
                        ))}
                    </div>
                    <div className="col-md-6">
                        <h5>Baskın Renk Paletiniz:</h5>
                        <ul>
                            {profile.dominant_colors.map(color => <li key={color} className="text-capitalize">{color}</li>)}
                        </ul>
                    </div>
                </div>
            </div>
        )}

        {/* Tek Parça Analiz Sonucu */}
        {results && (
            <>
            <div className="results-card mb-5">
              <h2 className="text-center mb-3 display-6">✨ {results.style_advice.title} ✨</h2>
              <p className="lead text-center text-muted">"{results.style_advice.vibe_description}"</p>
              <hr className="my-4" />
              <h5>Kombinasyon Mantığı</h5>
              <p>{results.style_advice.combination_logic}</p>
              <h5>💡 Profesyonel İpucu</h5>
              <p className="fst-italic">{results.style_advice.pro_tip}</p>

              {/* Kombin Görselleştirme */}
              <div className="text-center mt-4">
                  <button className="btn btn-outline-light" onClick={handleVisualizeCombo} disabled={comboLoading}>
                      {comboLoading ? "Oluşturuluyor..." : "Bu Kombini Görselleştir"}
                  </button>
              </div>
              {comboLoading && <div className="pulsing-loader mx-auto my-3" style={{width: '30px', height: '30px'}}></div>}
              {visualCombo && (
                  <div className="mt-4 p-3" style={{backgroundColor: 'rgba(0,0,0,0.2)', borderLeft: '3px solid var(--primary-color)'}}>
                      <p className="fw-bold">Gemini'nin Kombin Betimlemesi:</p>
                      <p className="fst-italic">{visualCombo.image_description}</p>
                      <small className="text-muted">(Not: Bu özellik şu anda gerçek bir resim yerine, resmin metinsel bir açıklamasını üretmektedir.)</small>
                  </div>
              )}
            </div>
          
            <h3 className="text-center mb-4 display-5">Bu Stile Uyumlu Ürünler</h3>
            <div className="row">
                {results.matched_products.map((product) => (
                <div key={product.id} className="col-md-4 mb-4 fade-in">
                    <div className="product-card h-100">
                    <img src={product.image.replace('static/img/', '/img/')} className="card-img-top" alt={product.name} />
                    <div className="card-body d-flex flex-column p-4">
                        <h5 className="card-title">{product.name}</h5>
                        <p className="card-text text-muted flex-grow-1">{product.style_tags.join(', ')}</p>
                        <div className="d-flex justify-content-between align-items-center mt-3">
                        <span className="fw-bold fs-5" style={{color: 'var(--primary-color)'}}>{product.price}</span>
                        <a href="#" className="btn btn-sm btn-outline-light">İncele</a>
                        </div>
                    </div>
                    </div>
                </div>
                ))}
            </div>
            </>
        )}
      </div>
    </div>
  );
};

export default HomePage;
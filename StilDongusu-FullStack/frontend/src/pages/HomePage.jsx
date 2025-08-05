import React, { useState } from 'react';
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
      setError('Lütfen analiz için bir resim dosyası seçin.');
      return;
    }
    const formData = new FormData();
    formData.append('file', file);
    setLoading(true);
    setError('');
    setResults(null);
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

  return (
    <div className="fade-in">
      <div className="text-center">
        <h1 className="display-4 fw-bold">Stil ve Uyum Analisti</h1>
        <p className="lead text-muted">Geleceğin stil danışmanı. Bir resim yükleyin, sihrin gerçekleşmesini izleyin.</p>
      </div>

      <div className="row justify-content-center mt-5">
        <div className="col-lg-8">
          <div className="futuristic-card">
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label htmlFor="image-upload" className="form-label fw-bold">Analiz Edilecek Görsel:</label>
                <input className="form-control form-control-lg" type="file" id="image-upload" accept="image/*" required onChange={handleFileChange} />
              </div>
              <div className="d-grid mt-4">
                <button type="submit" className="glow-button btn-lg" disabled={loading}>
                  {loading ? 'Analiz Ediliyor...' : 'Stilimi Analiz Et'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
      
      {loading && (
        <div className="text-center my-5">
          <div className="pulsing-loader"></div>
          <p className="mt-3">Stiliniz analiz ediliyor... Gemini sizin için çalışıyor!</p>
        </div>
      )}

      {error && <div className="alert alert-danger mt-4">{error}</div>}

      {results && (
        <div className="mt-5 pt-4 fade-in">
          <div className="mb-5">
            <div className="results-card">
              <h2 className="text-center mb-3 display-6">✨ {results.style_advice.title} ✨</h2>
              <p className="lead text-center text-muted">"{results.style_advice.vibe_description}"</p>
              <hr className="my-4" />
              <h5 className="mt-4">Kombinasyon Mantığı</h5>
              <p>{results.style_advice.combination_logic}</p>
              <h5 className="mt-4">💡 Profesyonel İpucu</h5>
              <p className="fst-italic">{results.style_advice.pro_tip}</p>
              <hr className="my-4"/>
              <details className="mt-3">
                <summary className="fw-bold fs-5">Yüklenen Görselin Detaylı Analizi</summary>
                <div className="mt-2 p-3">
                  <p><strong>Açıklama:</strong> {results.image_analysis.item_description}</p>
                  <p><strong>Stil Etiketleri:</strong> <span className="text-warning">{results.image_analysis.inferred_style.style_tags.join(', ')}</span></p>
                  <p><strong>Gerekçe:</strong> {results.image_analysis.inferred_style.justification}</p>
                  <p><strong>Önerilen Kullanım:</strong> {results.image_analysis.contextual_use.seasons.join(', ')} mevsimlerinde, {results.image_analysis.contextual_use.environment.join('/')} ortamları için uygundur.</p>
                </div>
              </details>
            </div>
          </div>
          
          <h3 className="text-center mb-4 display-5">Bu Stile Uyumlu Ürünler</h3>
          <div className="row">
            {results.matched_products.map((product) => (
              <div key={product.id} className="col-md-4 mb-4 fade-in" style={{animationDelay: `${product.id * 100}ms`}}>
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
        </div>
      )}
    </div>
  );
};

export default HomePage;
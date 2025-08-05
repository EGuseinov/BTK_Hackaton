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
      setError('Lütfen bir resim dosyası seçin.');
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
    <>
      <div className="text-center">
        <h1 className="display-5 fw-bold">Stil ve Uyum Analisti (StyleSync)</h1>
        <p className="lead text-muted">Dolabınızdaki bir parçanın fotoğrafını yükleyin, ona en uygun kombinleri sizin için bulalım ve stil önerileri sunalım.</p>
      </div>

      <div className="row justify-content-center mt-4">
        <div className="col-md-8">
          <div className="card p-4 styled-form-container">
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label htmlFor="image-upload" className="form-label fw-bold">Kombinlemek istediğiniz ürünün fotoğrafı:</label>
                <input className="form-control" type="file" id="image-upload" name="file" accept="image/*" required onChange={handleFileChange} />
              </div>
              <div className="d-grid">
                <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
                  {loading ? 'Analiz Ediliyor...' : 'Stilimi Analiz Et'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
      
      {loading && (
        <div className="text-center my-5">
          <div className="spinner-border text-primary" role="status"><span className="visually-hidden">Loading...</span></div>
          <p className="mt-2">Stiliniz analiz ediliyor... Gemini sizin için çalışıyor!</p>
        </div>
      )}

      {error && <div className="alert alert-danger mt-4">{error}</div>}

      {results && (
        <div className="mt-5">
          <div className="mb-4">
            <div className="card style-advice-card">
              <div className="card-body">
                <h4 className="card-title text-center mb-3">✨ {results.style_advice.title} ✨</h4>
                <p className="lead text-center">"{results.style_advice.vibe_description}"</p>
                <hr/>
                <h5 className="mt-4">Kombinasyon Mantığı</h5>
                <p>{results.style_advice.combination_logic}</p>
                <h5 className="mt-4">💡 Profesyonel İpucu (Pro-Tip)</h5>
                <p className="fst-italic">{results.style_advice.pro_tip}</p>
                <hr/>
                 <details className="mt-3">
                    <summary className="fw-bold" style={{cursor: 'pointer'}}>Yüklenen Görselin Detaylı Analizi</summary>
                    <div className="mt-2 p-3 bg-light rounded">
                        <p><strong>Açıklama:</strong> {results.image_analysis.item_description}</p>
                        <p><strong>Stil Etiketleri:</strong> {results.image_analysis.inferred_style.style_tags.join(', ')}</p>
                        <p><strong>Gerekçe:</strong> {results.image_analysis.inferred_style.justification}</p>
                        <p><strong>Önerilen Kullanım:</strong> {results.image_analysis.contextual_use.seasons.join(', ')} mevsimlerinde, {results.image_analysis.contextual_use.environment.join('/')} ortamları için uygundur.</p>
                    </div>
                </details>
              </div>
            </div>
          </div>
          <hr className="my-5" />
          <h3 className="text-center mb-4">Bu Stile Uyumlu Ürünler</h3>
          <div className="row">
            {results.matched_products.map((product) => (
              <div key={product.id} className="col-md-4 mb-4">
                <div className="card result-card h-100">
                  <img src={product.image.replace('static/img/', '/img/')} className="card-img-top" alt={product.name} />
                  <div className="card-body d-flex flex-column">
                    <h5 className="card-title">{product.name}</h5>
                    <p className="card-text text-muted flex-grow-1">Stil Etiketleri: {product.style_tags.join(', ')}</p>
                    <div className="d-flex justify-content-between align-items-center">
                      <span className="fw-bold fs-5">{product.price}</span>
                      <a href="#" className="btn btn-sm btn-outline-primary">İncele</a>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
};

export default HomePage;
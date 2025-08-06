import React, { useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const HomePage = () => {
  const [file, setFile] = useState(null);
  const [files, setFiles] = useState(null);
  const [results, setResults] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [profileLoading, setProfileLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [eventRequest, setEventRequest] = useState('');
  const [eventCombinations, setEventCombinations] = useState(null);
  const [eventLoading, setEventLoading] = useState(false);

  const clearState = () => {
    setError('');
    setResults(null);
    setProfile(null);
    setEventCombinations(null);
  };

  const handleSingleAnalysis = async (e) => {
    e.preventDefault();
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    setLoading(true);
    clearState();
    try {
      const response = await axios.post('/api/analyze-style', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Analiz sırasında hata.');
    } finally {
      setLoading(false);
    }
  };

  const handleProfileAnalysis = async (e) => {
    e.preventDefault();
    if (!files || files.length < 2) {
      setError('En az 2 resim seçin.');
      return;
    }
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) formData.append('files', files[i]);
    setProfileLoading(true);
    clearState();
    try {
      const response = await axios.post('/api/create-style-profile', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
      setProfile(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Profil oluşturma hatası.');
    } finally {
      setProfileLoading(false);
    }
  };
  
  const handleEventStylist = async (e) => {
    e.preventDefault();
    if (!eventRequest) return;
    setEventLoading(true);
    clearState();
    try {
        const response = await axios.post('/api/event-stylist', { user_request: eventRequest });
        setEventCombinations(response.data.combinations);
    } catch (err) {
        setError(err.response?.data?.detail || 'Stilist önerisi oluşturma hatası.');
    } finally {
        setEventLoading(false);
    }
  };

  return (
    <div className="fade-in">
      <div className="text-center">
        <h1 className="display-4 fw-bold">StilDöngüsü</h1>
        <p className="lead text-muted">Yapay Zeka Destekli Kişisel Stil Asistanınız</p>
      </div>

      <div className="row justify-content-center mt-5">
        <div className="col-lg-6 mb-4"><div className="futuristic-card h-100"><h4 className="text-center mb-3">Tek Parça Analizi</h4><p className="text-center text-muted small">Bir ürünün fotoğrafını yükleyerek anında stil önerileri alın.</p><form onSubmit={handleSingleAnalysis}><div className="mb-3"><input className="form-control" type="file" accept="image/*" required onChange={(e) => setFile(e.target.files[0])} /></div><div className="d-grid"><button type="submit" className="glow-button" disabled={loading}>{loading ? 'Analiz Ediliyor...' : 'Stilimi Analiz Et'}</button></div></form></div></div>
        <div className="col-lg-6 mb-4"><div className="futuristic-card h-100"><h4 className="text-center mb-3">Stil Radarı Oluştur</h4><p className="text-center text-muted small">Sevdiğiniz 2-5 kombininizi yükleyin, kişisel stil profilinizi keşfedin.</p><form onSubmit={handleProfileAnalysis}><div className="mb-3"><input className="form-control" type="file" accept="image/*" required multiple onChange={(e) => setFiles(e.target.files)} /></div><div className="d-grid"><button type="submit" className="glow-button" disabled={profileLoading}>{profileLoading ? 'Profil Oluşturuluyor...' : 'Stil Radarımı Oluştur'}</button></div></form></div></div>
      </div>
      
      <div className="row justify-content-center mt-2"><div className="col-lg-12"><div className="futuristic-card"><h4 className="text-center mb-3">✨ Etkinlik ve Mekan Stilisti</h4><p className="text-center text-muted small">Nereye gideceğinizi söyleyin, Gemini sizin için 3 farklı kombin hazırlasın.</p><form onSubmit={handleEventStylist}><div className="mb-3"><textarea className="form-control" rows="2" placeholder="Örn: 'Haftaya Mardin'de bir arkadaşımın gündüz düğünü var.' veya 'İlk iş görüşmem için ciddi bir kombin lazım.'" value={eventRequest} onChange={(e) => setEventRequest(e.target.value)}></textarea></div><div className="d-grid"><button type="submit" className="glow-button" disabled={eventLoading}>{eventLoading ? 'Kombinler Hazırlanıyor...' : 'Bana Kombin Öner'}</button></div></form></div></div></div>

      {(loading || profileLoading || eventLoading) && (<div className="text-center my-5"><div className="pulsing-loader"></div><p className="mt-3">Gemini sizin için çalışıyor, stiliniz çözümleniyor...</p></div>)}
      {error && <div className="alert alert-danger mt-4">{error}</div>}

      <div className="mt-5 pt-4 fade-in">
        {profile && (<div className="results-card mb-5"><h2 className="text-center mb-3 display-6">✨ Kişisel Stil Radarınız ✨</h2><p className="lead text-center text-muted">"{profile.summary}"</p><hr className="my-4" /><div className="row"><div className="col-md-6"><h5>Stil Dağılımınız:</h5>{profile.style_profile.map(item => (<div key={item.style} className="mb-2"><span className="text-capitalize">{item.style.replace('_', ' ')}</span><div className="progress" style={{height: "20px"}}><div className="progress-bar" style={{width: `${item.percentage}%`, backgroundColor: 'var(--primary-color)'}}>{item.percentage}%</div></div></div>))}</div><div className="col-md-6"><h5>Baskın Renk Paletiniz:</h5><ul>{profile.dominant_colors.map(color => <li key={color} className="text-capitalize">{color}</li>)}</ul></div></div></div>)}
{eventCombinations && (
    <div className="results-card my-5">
        <h2 className="text-center mb-4 display-6">İşte Etkinliğiniz İçin Gemini'nin Önerileri</h2>
        {eventCombinations.map((combo, index) => (
            <div key={index} className="mb-5">
                <h4 className="fw-bold">{combo.title}</h4>
                <p className="text-primary fst-italic">"{combo.vibe}"</p>
                <div className="row">
                    {combo.items.map(item => (
                        <div key={item.id} className="col-6 col-md-3 mb-3">
                            <Link to={`/product/${item.id}`} style={{ textDecoration: 'none' }}>
                                <div className="product-card h-100">
                                    <img 
                                        src={item.image.replace('static/img/', '/img/')} 
                                        className="card-img-top" 
                                        alt={item.name} 
                                    />
                                    <div className="card-body p-2 text-center">
                                        <p className="card-title small mb-0">{item.name}</p>
                                    </div>
                                </div>
                            </Link>
                        </div>
                    ))}
                </div>
                {index < eventCombinations.length - 1 && <hr className="my-4" />}
            </div>
        ))}
    </div>
)}
        {results && (<><div className="results-card mb-5"><h2 className="text-center mb-3 display-6">✨ {results.style_advice.title} ✨</h2><p className="lead text-center text-muted">"{results.style_advice.vibe_description}"</p><hr className="my-4" /><h5>Kombinasyon Mantığı</h5><p>{results.style_advice.combination_logic}</p><h5>💡 Profesyonel İpucu</h5><p className="fst-italic">{results.style_advice.pro_tip}</p></div><h3 className="text-center mb-4 display-5">Bu Stile Uyumlu Ürünler</h3><div className="row">{results.matched_products.map((product) => (<div key={product.id} className="col-md-4 mb-4 fade-in"><div className="product-card h-100"><img src={product.image.replace('static/img/', '/img/')} className="card-img-top" alt={product.name} /><div className="card-body d-flex flex-column p-4"><h5 className="card-title">{product.name}</h5><p className="card-text text-muted flex-grow-1">{product.style_tags.join(', ')}</p><div className="d-flex justify-content-between align-items-center mt-3"><span className="fw-bold fs-5" style={{color: 'var(--primary-color)'}}>{product.price}</span><Link to={`/product/${product.id}`} className="btn btn-sm btn-outline-light">İncele</Link></div></div></div></div>))}</div></>)}
      </div>
    </div>
  );
};

export default HomePage;
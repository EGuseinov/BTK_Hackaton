import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

const ProductDetailPage = () => {
    const { productId } = useParams();
    const [product, setProduct] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    
    const [bodyType, setBodyType] = useState('');
    const [fitScore, setFitScore] = useState(null);
    const [scoreLoading, setScoreLoading] = useState(false);

    useEffect(() => {
        const fetchProduct = async () => {
            try {
                setLoading(true);
                const response = await axios.get(`/api/products/${productId}`);
                setProduct(response.data);
            } catch (err) {
                setError('Ürün yüklenirken bir hata oluştu.');
            } finally {
                setLoading(false);
            }
        };
        if (productId) {
            fetchProduct();
        }
    }, [productId]);
    
    const handleFitScoreFetch = async () => {
        if (!bodyType || !product) return;
        setScoreLoading(true);
        try {
            const response = await axios.post('/api/fit-score', {
                user_body_type: bodyType,
                product_id: product.id
            });
            setFitScore(response.data);
        } catch (err) {
            console.error("Fit Puanı alınamadı:", err);
            setFitScore({fit_score: '?', reasoning: 'Puan hesaplanırken bir hata oluştu.'})
        } finally {
            setScoreLoading(false);
        }
    };

    if (loading) return <div className="text-center"><div className="pulsing-loader"></div></div>;
    if (error) return <div className="alert alert-danger">{error}</div>;
    if (!product) return <div>Ürün bulunamadı.</div>;

    return (
        <div className="fade-in">
            <div className="row">
                <div className="col-md-6 mb-4">
                    <img src={product.image.replace('static/img/', '/img/')} alt={product.name} className="img-fluid rounded" style={{ aspectRatio: '1/1', objectFit: 'cover' }} />
                </div>
                <div className="col-md-6">
                    <h1 className="display-5">{product.name}</h1>
                    <p className="display-6" style={{color: 'var(--primary-color)'}}>{product.price}</p>
                    <p className="text-muted">{product.style_tags.join(', ')}</p>
                    <hr/>
                    
                    <div className="futuristic-card mt-4 p-4">
                        <h5 className="mb-3">✨ Gemini Fit Puanı</h5>
                        <p className="small text-muted">Vücut tipinize göre bu ürünün size ne kadar uygun olacağını öğrenin.</p>
                        <div className="input-group">
                            <select 
                                className="form-select" 
                                value={bodyType} 
                                onChange={(e) => setBodyType(e.target.value)}
                            >
                                <option value="">Vücut Tipinizi Seçin...</option>
                                <option value="armut">Armut (Geniş Kalça)</option>
                                <option value="elma">Elma (Geniş Bel)</option>
                                <option value="kum saati">Kum Saati (Dengeli)</option>
                                <option value="dikdörtgen">Dikdörtgen (Düz)</option>
                            </select>
                            <button className="btn glow-button" onClick={handleFitScoreFetch} disabled={!bodyType || scoreLoading}>
                                {scoreLoading ? '...' : 'Puanla'}
                            </button>
                        </div>
                        
                        {fitScore && (
                            <div className="mt-4 fade-in">
                                <h6>Vücut Tipinize Uygunluk: <span className="text-primary fw-bold display-6">{fitScore.fit_score}/10</span></h6>
                                <p className="fst-italic">"{fitScore.reasoning}"</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProductDetailPage;
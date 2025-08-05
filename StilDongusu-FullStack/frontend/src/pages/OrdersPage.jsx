import React, { useState } from 'react';
import ReturnModal from '../components/ReturnModal';

const OrdersPage = () => {
    const [selectedProduct, setSelectedProduct] = useState(null);

    const dummyOrders = [
        { id: "TR12345", product: "Lacivert Blazer Ceket", status: "Teslim Edildi" },
        { id: "TR67890", product: "Beyaz Gömlek", status: "Teslim Edildi" }
    ];

    const handleReturnClick = (productName) => {
        setSelectedProduct(productName);
    };

    return (
        <div className="fade-in">
            <h1 className="display-5 fw-bold text-center mb-5">Siparişlerim</h1>
            <div className="row justify-content-center">
                <div className="col-lg-8">
                    {dummyOrders.map((order) => (
                        <div key={order.id} className="futuristic-card d-flex justify-content-between align-items-center mb-3">
                            <div>
                                <h5 className="mb-1">{order.product}</h5>
                                <p className="mb-1 text-muted">Sipariş No: {order.id}</p>
                                <span className="badge bg-success">{order.status}</span>
                            </div>
                            <button 
                                className="glow-button"
                                data-bs-toggle="modal"
                                data-bs-target="#return-chatbot-modal"
                                onClick={() => handleReturnClick(order.product)}>
                                İade Et
                            </button>
                        </div>
                    ))}
                </div>
            </div>
            <ReturnModal productName={selectedProduct} />
        </div>
    );
};

export default OrdersPage;
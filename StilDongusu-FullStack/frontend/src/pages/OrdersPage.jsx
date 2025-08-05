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
        <>
            <h1 className="mb-4">Siparişlerim</h1>
            <div className="list-group">
                {dummyOrders.map((order) => (
                    <div key={order.id} className="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                        <div>
                            <h5 className="mb-1">{order.product}</h5>
                            <p className="mb-1">Sipariş No: {order.id}</p>
                            <small>Durum: {order.status}</small>
                        </div>
                        <button 
                            className="btn btn-outline-danger return-btn"
                            data-bs-toggle="modal"
                            data-bs-target="#return-chatbot-modal"
                            onClick={() => handleReturnClick(order.product)}>
                            İade Et
                        </button>
                    </div>
                ))}
            </div>
            <ReturnModal productName={selectedProduct} />
        </>
    );
};

export default OrdersPage;

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import OrdersPage from './pages/OrdersPage';
import SellerDashboardPage from './pages/SellerDashboardPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="siparislerim" element={<OrdersPage />} />
          <Route path="satici-paneli" element={<SellerDashboardPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;

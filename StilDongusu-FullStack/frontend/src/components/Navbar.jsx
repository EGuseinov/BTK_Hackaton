import React from 'react';
import { NavLink } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-light shadow-sm">
      <div className="container">
        <NavLink className="navbar-brand fw-bold" to="/">StilDöngüsü 🌀</NavLink>
        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav ms-auto">
            <li className="nav-item">
              <NavLink className="nav-link" to="/">Stil Analisti</NavLink>
            </li>
            <li className="nav-item">
              <NavLink className="nav-link" to="/siparislerim">Siparişlerim</NavLink>
            </li>
            <li className="nav-item">
              <NavLink className="nav-link" to="/satici-paneli">Satıcı Paneli</NavLink>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

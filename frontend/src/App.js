import React from "react";
import { Routes, Route, NavLink } from "react-router-dom";

function App() {
  return (
    <div className="app">
      <nav className="sidebar">
        <div className="logo">VaultGuard</div>
        <NavLink to="/" className="nav-link">Dashboard</NavLink>
        <NavLink to="/transactions" className="nav-link">Transactions</NavLink>
        <NavLink to="/live" className="nav-link">Live Feed</NavLink>
      </nav>
      <main className="main-content">
        <Routes>
          <Route path="/" element={<div className="page-placeholder">Dashboard</div>} />
          <Route path="/transactions" element={<div className="page-placeholder">Transactions</div>} />
          <Route path="/transactions/:id" element={<div className="page-placeholder">Transaction Detail</div>} />
          <Route path="/live" element={<div className="page-placeholder">Live Feed</div>} />
        </Routes>
      </main>
    </div>
  );
}

export default App;

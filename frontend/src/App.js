import React from "react";
import { Routes, Route, NavLink } from "react-router-dom";
import FraudDashboard from "./components/FraudDashboard";
import TransactionTable from "./components/TransactionTable";
import TransactionDetail from "./components/TransactionDetail";
import LiveFeed from "./components/LiveFeed";

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
          <Route path="/" element={<FraudDashboard />} />
          <Route path="/transactions" element={<TransactionTable />} />
          <Route path="/transactions/:id" element={<TransactionDetail />} />
          <Route path="/live" element={<LiveFeed />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;

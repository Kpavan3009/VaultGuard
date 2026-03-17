import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getTransactions, reviewTransaction } from "../api";

function TransactionTable() {
  const [transactions, setTransactions] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [sortField, setSortField] = useState("timestamp");
  const [sortDir, setSortDir] = useState("desc");
  const pageSize = 25;
  const navigate = useNavigate();

  useEffect(() => {
    loadTransactions();
  }, [page]);

  function loadTransactions() {
    getTransactions(page, pageSize)
      .then((res) => {
        setTransactions(res.data.transactions);
        setTotal(res.data.total);
      })
      .catch(() => {});
  }

  function handleSort(field) {
    if (sortField === field) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDir("desc");
    }
  }

  function sorted(list) {
    return [...list].sort((a, b) => {
      let va = a[sortField];
      let vb = b[sortField];
      if (typeof va === "string") va = va.toLowerCase();
      if (typeof vb === "string") vb = vb.toLowerCase();
      if (va < vb) return sortDir === "asc" ? -1 : 1;
      if (va > vb) return sortDir === "asc" ? 1 : -1;
      return 0;
    });
  }

  function handleReview(txnId, action) {
    reviewTransaction(txnId, "analyst", action)
      .then(() => loadTransactions())
      .catch(() => {});
  }

  function tierClass(tier) {
    return `badge badge-${tier || "low"}`;
  }

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div>
      <h2 className="card-title">Transactions</h2>
      <div className="card">
        <table>
          <thead>
            <tr>
              <th onClick={() => handleSort("transaction_id")} style={{ cursor: "pointer" }}>ID</th>
              <th onClick={() => handleSort("amount")} style={{ cursor: "pointer" }}>Amount</th>
              <th onClick={() => handleSort("user_id")} style={{ cursor: "pointer" }}>User</th>
              <th onClick={() => handleSort("merchant_category")} style={{ cursor: "pointer" }}>Category</th>
              <th onClick={() => handleSort("risk_tier")} style={{ cursor: "pointer" }}>Risk</th>
              <th onClick={() => handleSort("timestamp")} style={{ cursor: "pointer" }}>Time</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {sorted(transactions).map((txn) => (
              <tr key={txn.transaction_id}>
                <td
                  style={{ cursor: "pointer", color: "#6366f1" }}
                  onClick={() => navigate(`/transactions/${txn.transaction_id}`)}
                >
                  {txn.transaction_id.slice(0, 12)}...
                </td>
                <td>${txn.amount.toFixed(2)}</td>
                <td>{txn.user_id}</td>
                <td>{txn.merchant_category}</td>
                <td><span className={tierClass(txn.risk_tier)}>{txn.risk_tier || "pending"}</span></td>
                <td>{new Date(txn.timestamp).toLocaleString()}</td>
                <td>
                  <button className="btn btn-approve" onClick={() => handleReview(txn.transaction_id, "approve")}>
                    Approve
                  </button>{" "}
                  <button className="btn btn-reject" onClick={() => handleReview(txn.transaction_id, "reject")}>
                    Reject
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="pagination">
          <button disabled={page <= 1} onClick={() => setPage(page - 1)}>Prev</button>
          <span>Page {page} of {totalPages || 1}</span>
          <button disabled={page >= totalPages} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      </div>
    </div>
  );
}

export default TransactionTable;

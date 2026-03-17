import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getTransaction, reviewTransaction } from "../api";

function ShapChart({ shapValues }) {
  if (!shapValues || Object.keys(shapValues).length === 0) return null;

  const sorted = Object.entries(shapValues)
    .map(([feature, value]) => ({ feature, value }))
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
    .slice(0, 8);

  const maxVal = Math.max(...sorted.map((s) => Math.abs(s.value)), 0.01);

  return (
    <div>
      {sorted.map((item) => (
        <div className="shap-bar" key={item.feature}>
          <span className="feature-name">{item.feature}</span>
          <div className="bar-container">
            <div
              className={`bar-fill ${item.value >= 0 ? "bar-positive" : "bar-negative"}`}
              style={{ width: `${(Math.abs(item.value) / maxVal) * 100}%` }}
            />
          </div>
          <span style={{ fontSize: "11px", color: "#888", width: "50px" }}>
            {item.value.toFixed(3)}
          </span>
        </div>
      ))}
    </div>
  );
}

function TransactionDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [txn, setTxn] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTransaction(id)
      .then((res) => {
        setTxn(res.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [id]);

  function handleReview(action) {
    reviewTransaction(id, "analyst", action).then(() => {
      getTransaction(id).then((res) => setTxn(res.data));
    });
  }

  if (loading) return <div className="page-placeholder">Loading...</div>;
  if (!txn) return <div className="page-placeholder">Transaction not found</div>;

  let shapValues = {};
  if (txn.shap_values) {
    try {
      shapValues = typeof txn.shap_values === "string" ? JSON.parse(txn.shap_values) : txn.shap_values;
    } catch {
      shapValues = {};
    }
  }

  return (
    <div>
      <button className="btn btn-primary" onClick={() => navigate("/transactions")} style={{ marginBottom: "20px" }}>
        Back to Transactions
      </button>
      <div className="detail-grid">
        <div className="card">
          <div className="card-title">Transaction Details</div>
          <div className="detail-row">
            <span className="label">Transaction ID</span>
            <span className="value">{txn.transaction_id}</span>
          </div>
          <div className="detail-row">
            <span className="label">User</span>
            <span className="value">{txn.user_id}</span>
          </div>
          <div className="detail-row">
            <span className="label">Amount</span>
            <span className="value">${txn.amount.toFixed(2)}</span>
          </div>
          <div className="detail-row">
            <span className="label">Category</span>
            <span className="value">{txn.merchant_category}</span>
          </div>
          <div className="detail-row">
            <span className="label">Risk Tier</span>
            <span className="value">
              <span className={`badge badge-${txn.risk_tier || "low"}`}>{txn.risk_tier || "pending"}</span>
            </span>
          </div>
          <div className="detail-row">
            <span className="label">Fraud Probability</span>
            <span className="value">{txn.fraud_probability != null ? `${(txn.fraud_probability * 100).toFixed(1)}%` : "N/A"}</span>
          </div>
          <div className="detail-row">
            <span className="label">Status</span>
            <span className="value">{txn.status}</span>
          </div>
          <div className="detail-row">
            <span className="label">Timestamp</span>
            <span className="value">{new Date(txn.timestamp).toLocaleString()}</span>
          </div>
          <div className="review-actions">
            <button className="btn btn-approve" onClick={() => handleReview("approve")}>Approve</button>
            <button className="btn btn-reject" onClick={() => handleReview("reject")}>Reject</button>
          </div>
        </div>

        <div className="card">
          <div className="card-title">SHAP Feature Importance</div>
          <ShapChart shapValues={shapValues} />
        </div>
      </div>
    </div>
  );
}

export default TransactionDetail;

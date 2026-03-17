import React, { useState, useEffect } from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { getStats, getFlaggedTransactions } from "../api";

const TIER_COLORS = {
  critical: "#ef4444",
  high: "#f59e0b",
  medium: "#3b82f6",
  low: "#22c55e",
};

function FraudDashboard() {
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [tierData, setTierData] = useState([]);

  useEffect(() => {
    getStats()
      .then((res) => setStats(res.data))
      .catch(() => {});

    getFlaggedTransactions(1, 10)
      .then((res) => {
        const txns = res.data.transactions;
        setAlerts(txns);
        const counts = {};
        txns.forEach((t) => {
          const tier = t.risk_tier || "low";
          counts[tier] = (counts[tier] || 0) + 1;
        });
        const data = Object.entries(counts).map(([name, value]) => ({ name, value }));
        setTierData(data);
      })
      .catch(() => {});
  }, []);

  const falsePositiveRate = stats
    ? stats.flagged_transactions > 0
      ? ((stats.blocked_transactions / stats.flagged_transactions) * 100).toFixed(1)
      : "0.0"
    : "...";

  return (
    <div>
      <div className="kpi-row">
        <div className="kpi-card">
          <div className="label">Total Transactions</div>
          <div className="value">{stats ? stats.total_transactions.toLocaleString() : "..."}</div>
        </div>
        <div className="kpi-card">
          <div className="label">Flagged</div>
          <div className="value" style={{ color: "#f59e0b" }}>
            {stats ? stats.flagged_transactions.toLocaleString() : "..."}
          </div>
        </div>
        <div className="kpi-card">
          <div className="label">False Positive Rate</div>
          <div className="value">{falsePositiveRate}%</div>
        </div>
        <div className="kpi-card">
          <div className="label">Avg Amount</div>
          <div className="value">${stats ? stats.average_amount.toFixed(2) : "..."}</div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        <div className="card">
          <div className="card-title">Risk Tier Distribution</div>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={tierData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={3}
                dataKey="value"
              >
                {tierData.map((entry) => (
                  <Cell key={entry.name} fill={TIER_COLORS[entry.name] || "#888"} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="card-title">Recent Alerts</div>
          <div style={{ maxHeight: "280px", overflowY: "auto" }}>
            {alerts.length === 0 && <div style={{ color: "#888", fontSize: "13px" }}>No alerts yet</div>}
            {alerts.map((a) => (
              <div key={a.transaction_id} className="live-feed-item">
                <div>
                  <span className={`badge badge-${a.risk_tier}`}>{a.risk_tier}</span>{" "}
                  <span className="txn-id">{a.transaction_id.slice(0, 16)}</span>
                </div>
                <span className="amount">${a.amount.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default FraudDashboard;

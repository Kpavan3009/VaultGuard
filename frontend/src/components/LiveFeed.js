import React, { useState, useEffect, useRef } from "react";
import { getWebSocketUrl } from "../api";

function LiveFeed() {
  const [items, setItems] = useState([]);
  const [connected, setConnected] = useState(false);
  const feedRef = useRef(null);
  const wsRef = useRef(null);
  const retryRef = useRef(null);
  const retryDelay = useRef(1000);

  useEffect(() => {
    connectWs();
    return () => {
      if (retryRef.current) clearTimeout(retryRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight;
    }
  }, [items]);

  function scheduleReconnect() {
    if (retryRef.current) clearTimeout(retryRef.current);
    retryRef.current = setTimeout(() => {
      connectWs();
      retryDelay.current = Math.min(retryDelay.current * 2, 30000);
    }, retryDelay.current);
  }

  function connectWs() {
    const ws = new WebSocket(getWebSocketUrl());
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      retryDelay.current = 1000;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "pong" || data.type === "connected") return;
        setItems((prev) => [...prev.slice(-99), data]);
      } catch {
        return;
      }
    };

    ws.onclose = () => {
      setConnected(false);
      scheduleReconnect();
    };

    ws.onerror = () => {
      setConnected(false);
      ws.close();
    };
  }

  function tierClass(tier) {
    return `badge badge-${tier || "low"}`;
  }

  return (
    <div>
      <h2 className="card-title">Live Transaction Feed</h2>
      <div className="connection-status">
        <span className={`status-dot ${connected ? "connected" : "disconnected"}`} />
        <span>{connected ? "Connected" : "Disconnected"}</span>
      </div>
      <div className="card">
        <div className="live-feed" ref={feedRef}>
          {items.length === 0 && (
            <div style={{ color: "#888", fontSize: "13px", padding: "20px" }}>
              Waiting for transactions...
            </div>
          )}
          {items.map((item, i) => (
            <div key={i} className="live-feed-item">
              <div>
                <span className={tierClass(item.risk_tier)}>{item.risk_tier || "new"}</span>{" "}
                <span className="txn-id">{item.transaction_id || "unknown"}</span>
              </div>
              <div>
                <span className="amount">${(item.amount || 0).toFixed(2)}</span>{" "}
                <span style={{ color: "#888", fontSize: "11px" }}>{item.merchant_category || ""}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default LiveFeed;

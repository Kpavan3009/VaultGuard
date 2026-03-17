# VaultGuard

Real-time fraud detection system for financial transactions. Scores each transaction using an ensemble of ML models, explains why it was flagged using SHAP, and pushes alerts through a live WebSocket feed to an analyst dashboard.

This is a **full-stack software engineering + machine learning** project. The SWE side covers the event-driven API, Redis feature caching, WebSocket streaming, React dashboard, Docker multi-service setup, CI/CD, and test suite. The ML side covers ensemble fraud scoring with Isolation Forest + LightGBM, behavioral feature engineering, SHAP explainability, and cost-sensitive learning for extreme class imbalance.

## What This Project Produces

- A **fraud scoring API** that accepts a transaction and returns fraud probability, risk tier (LOW/MEDIUM/HIGH/CRITICAL), top 3 contributing features via SHAP, and a recommended action
- An **ensemble ML pipeline** combining unsupervised anomaly detection (Isolation Forest) with supervised classification (LightGBM), achieving 0.91 precision and 0.87 recall on a 0.5% fraud rate dataset
- A **feature engineering module** computing 20+ behavioral signals: spending velocity, geo-distance between transactions, merchant deviation, time-gap patterns, amount z-scores, and rolling 1hr/24hr aggregations
- A **SHAP explainability layer** that returns per-transaction feature importance so analysts see exactly why something was flagged instead of just a score
- A **Redis-backed feature cache** storing rolling user aggregations for fast lookups during inference
- A **WebSocket endpoint** streaming scored transactions in real-time to connected analyst dashboards
- A **React dashboard** with live transaction feed, risk tier distribution charts, SHAP breakdowns per transaction, and approve/reject review workflow
- Full **Docker Compose setup** with API + PostgreSQL + Redis running with one command

## Tech Stack

**Software Engineering:**
- FastAPI (async API with Pydantic validation, structured logging, dependency injection)
- SQLAlchemy + PostgreSQL (transaction storage, user profiles, fraud alerts)
- Redis (rolling feature aggregation cache with graceful fallback)
- WebSocket (real-time transaction streaming to frontend)
- React 18 + Recharts (analyst dashboard with live feed, charts, review actions)
- Docker Compose (multi-service: API + Postgres + Redis)
- GitHub Actions CI (mypy type checking, pytest on every push)
- pytest (10+ tests covering feature engineering, fraud service, and API contracts)

**Machine Learning:**
- LightGBM (supervised fraud classifier with cost-sensitive learning for 0.5% fraud rate)
- Isolation Forest (unsupervised anomaly detection as first-stage filter)
- SHAP TreeExplainer (per-prediction feature importance)
- NumPy + Pandas (20+ engineered features: velocity, geo-distance, z-scores, time patterns)

## Quick Start

```bash
git clone https://github.com/Kpavan3009/VaultGuard.git
cd VaultGuard
docker compose up --build
```

API runs on `http://localhost:8000`. Health check at `/health`.

To train models locally:

```bash
pip install -r requirements.txt
python data/generate_transactions.py
python -m app.ml.train
uvicorn app.main:app --reload
```

## Project Structure

```
VaultGuard/
  app/
    main.py
    config.py
    database.py
    models/
      transaction.py         SQLAlchemy models (Transaction, UserProfile, FraudAlert)
      schemas.py             Pydantic request/response schemas
    routes/
      transactions.py        CRUD, filtering, review actions
      predictions.py         single + batch fraud scoring
      websocket.py           live transaction feed (ConnectionManager)
    services/
      fraud_service.py       ensemble scoring (IsoForest + LightGBM + SHAP)
      transaction_service.py CRUD operations, fraud stats
      feature_cache.py       Redis-backed rolling user aggregations
    ml/
      feature_engineering.py 20+ behavioral features
      explainer.py           SHAP TreeExplainer wrapper
      train.py               trains both models, prints metrics
  frontend/
    src/
      components/
        FraudDashboard.js    KPI cards + risk distribution chart + alerts
        TransactionTable.js  sortable table with risk tier badges
        TransactionDetail.js SHAP bar chart + review actions
        LiveFeed.js          WebSocket-connected real-time ticker
      api.js
      App.js
  tests/
    conftest.py
    test_feature_engineering.py
    test_fraud_service.py
    test_api.py
  data/                      synthetic transaction data (100K records)
  models/                    saved model artifacts + feature columns
```

## API Endpoints

| Method | Path | What it does |
|--------|------|-------------|
| GET | `/health` | health check |
| POST | `/api/v1/transactions/` | create a transaction |
| GET | `/api/v1/transactions/` | list transactions (paginated, filterable) |
| GET | `/api/v1/transactions/{id}` | get single transaction |
| GET | `/api/v1/transactions/flagged/list` | list flagged transactions |
| POST | `/api/v1/transactions/{id}/review` | mark as reviewed (approve/reject) |
| GET | `/api/v1/transactions/stats/summary` | transaction and fraud stats |
| POST | `/api/v1/predictions/analyze` | score a single transaction |
| POST | `/api/v1/predictions/batch` | score a batch of transactions |
| WS | `/ws/transactions` | live scored transaction stream |

## How Fraud Scoring Works

Each transaction gets scored by two models. LightGBM outputs a fraud probability based on 20+ behavioral features. Isolation Forest independently flags statistical outliers. The final score is a weighted combination: 70% LightGBM + 30% Isolation Forest (normalized). This gets mapped to a risk tier: LOW (<0.3), MEDIUM (0.3-0.6), HIGH (0.6-0.8), CRITICAL (>0.8).

Every prediction also comes with SHAP values showing the top 3 features that drove the score, so analysts can tell whether it was flagged because of a sudden amount spike, unusual location, rapid transaction velocity, or something else.

## Running Tests

```bash
pytest tests/ -v
```


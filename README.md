# VaultGuard

Real-time fraud detection API for financial transactions. It scores each transaction using an ensemble of ML models, flags suspicious activity, and sends alerts through a live WebSocket feed.

Built with FastAPI on the backend and React on the frontend.

## Tech Stack

- **API:** FastAPI, SQLAlchemy, Pydantic
- **ML:** LightGBM, Isolation Forest, SHAP (for explainability)
- **Database:** PostgreSQL
- **Cache:** Redis
- **Frontend:** React 18, Recharts, React Router
- **Infra:** Docker, Docker Compose, GitHub Actions CI

## Quick Start

```bash
git clone https://github.com/Kpavan3009/VaultGuard.git
cd VaultGuard
docker compose up --build
```

API runs on `http://localhost:8000`. Health check at `/health`.

To generate training data and train models locally:

```bash
pip install -r requirements.txt
python -m app.ml.train
```

## Project Structure

```
VaultGuard/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── transaction.py
│   │   └── schemas.py
│   ├── routes/
│   │   ├── transactions.py
│   │   ├── predictions.py
│   │   └── websocket.py
│   ├── services/
│   │   ├── fraud_service.py
│   │   ├── transaction_service.py
│   │   └── feature_cache.py
│   └── ml/
│       ├── feature_engineering.py
│       ├── explainer.py
│       └── train.py
├── frontend/
├── data/
├── models/
├── tests/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/transactions/` | Create a transaction |
| `GET` | `/api/v1/transactions/` | List transactions (paginated) |
| `GET` | `/api/v1/transactions/{id}` | Get single transaction |
| `GET` | `/api/v1/transactions/flagged/list` | List flagged transactions |
| `POST` | `/api/v1/transactions/{id}/review` | Mark transaction as reviewed |
| `GET` | `/api/v1/transactions/stats/summary` | Transaction stats |
| `POST` | `/api/v1/predictions/analyze` | Score a single transaction |
| `POST` | `/api/v1/predictions/batch` | Score a batch of transactions |
| `WS` | `/ws/transactions` | Live transaction feed |

## Fraud Scoring

Each transaction gets scored by two models. LightGBM outputs a fraud probability, and Isolation Forest flags statistical outliers. If the isolation forest marks it as anomalous, the combined score gets bumped up. The result is a risk tier: low, medium, high, or critical.

## ML Models

- **Isolation Forest** - unsupervised anomaly detection, catches transactions that look nothing like normal patterns
- **LightGBM** - supervised classifier trained on labeled fraud data, handles class imbalance with `is_unbalance`
- **SHAP** - explains which features drove each prediction (amount spikes, velocity, geo distance, etc.)

Features include amount z-scores, transaction velocity (1h/24h windows), geo distance from last transaction, merchant category encoding, time-of-day patterns, and more. See `app/ml/feature_engineering.py` for the full list.

## Screenshots

<!-- TODO: add screenshots -->

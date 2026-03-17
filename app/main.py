from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routes import transactions, predictions
from app.routes.websocket import router as ws_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="VaultGuard", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions.router, prefix="/api/v1")
app.include_router(predictions.router, prefix="/api/v1")
app.include_router(ws_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}

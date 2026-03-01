from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.api import sessions, hands, stats, analysis

# Create all tables on startup (no migration tool for MVP)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Poker Hand Analyzer",
    description="GGPoker Rush & Cash hand history analyzer",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://localhost:{settings.frontend_port}",
        f"http://127.0.0.1:{settings.frontend_port}",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router, prefix="/api")
app.include_router(hands.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}

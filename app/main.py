"""FastAPI entrypoint for Portfolio Pulse."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.portfolio import router as portfolio_router

app = FastAPI(
    title="Portfolio Pulse API",
    version="1.0.0",
    description=(
        "Portfolio Pulse scores user portfolios, compares against model allocations, "
        "and suggests rebalancing ideas. This is not investment advice."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(portfolio_router)


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}

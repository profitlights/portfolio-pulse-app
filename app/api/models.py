"""Pydantic models shared across Portfolio Pulse endpoints."""
from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, root_validator


class PortfolioItem(BaseModel):
    ticker: str = Field(..., description="Ticker symbol, e.g. VTI")
    amount: Optional[float] = Field(None, ge=0, description="Nominal amount invested")
    weight: Optional[float] = Field(
        None,
        ge=0,
        description="Portfolio weight expressed as a decimal (0-1).",
    )

    @root_validator
    def check_amount_or_weight(cls, values):  # type: ignore[override]
        amount, weight = values.get("amount"), values.get("weight")
        if amount is None and weight is None:
            raise ValueError("Each holding must provide an amount or a weight.")
        return values


class PortfolioUploadRequest(BaseModel):
    portfolio: List[PortfolioItem]


class NormalizedHolding(BaseModel):
    ticker: str
    weight: float


class PortfolioUploadResponse(BaseModel):
    user_id: str
    holdings: List[NormalizedHolding]
    total_value: float


class ScoreBreakdown(BaseModel):
    diversification: float
    resilience: float
    return_efficiency: float
    risk_balance: float


class DiversificationSlice(BaseModel):
    label: str
    weight: float


class ScoreResponse(BaseModel):
    pulse_score: float
    grade: str
    breakdown: ScoreBreakdown
    diversification_chart: List[DiversificationSlice]
    top_suggestions: List[str]


class ModelPerformance(BaseModel):
    model_key: str
    model_name: str
    expected_return: float
    volatility: float
    tracking_error: float


class ModelComparisonResponse(BaseModel):
    user_expected_return: float
    models: List[ModelPerformance]


class RebalanceAdjustment(BaseModel):
    ticker: str
    action: str
    weight_diff: float
    notional_change: float


class RebalanceSuggestionResponse(BaseModel):
    target_model: str
    target_weights: Dict[str, float]
    adjustments: List[RebalanceAdjustment]


class ErrorResponse(BaseModel):
    detail: str

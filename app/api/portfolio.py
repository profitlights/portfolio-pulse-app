"""Portfolio endpoints for Portfolio Pulse."""
from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status

from ..config import MODEL_NAMES, MODEL_PORTFOLIOS
from ..services.data_loader import expected_performance
from ..services.rebalance import generate_rebalance_plan, select_target_model
from ..utils.auth import get_current_user
from ..utils.math_ops import normalize_portfolio
from . import models
from .scoring import model_tracking_error, pulse_score

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


class PortfolioStore:
    """In-memory portfolio store keyed by user id."""

    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, float]] = {}
        self._values: Dict[str, float] = {}

    def set_portfolio(self, user_id: str, weights: Dict[str, float], total_value: float) -> None:
        self._store[user_id] = weights
        self._values[user_id] = total_value

    def get_portfolio(self, user_id: str) -> Dict[str, float]:
        if user_id not in self._store:
            raise KeyError("Portfolio not found")
        return self._store[user_id]

    def get_total_value(self, user_id: str) -> float:
        return self._values.get(user_id, 100.0)


portfolio_store = PortfolioStore()


def _normalize_request(payload: models.PortfolioUploadRequest) -> tuple[Dict[str, float], float]:
    normalized_inputs = []
    total_value = 0.0
    has_amount = any(item.amount for item in payload.portfolio)
    if has_amount:
        total_value = sum((item.amount or 0) for item in payload.portfolio)
        normalized_inputs = [(item.ticker, item.amount or 0.0) for item in payload.portfolio]
    else:
        normalized_inputs = [(item.ticker, item.weight or 0.0) for item in payload.portfolio]
        total_value = 100.0
    weights = normalize_portfolio(normalized_inputs)
    return weights, total_value


@router.post(
    "/upload",
    response_model=models.PortfolioUploadResponse,
    responses={404: {"model": models.ErrorResponse}},
)
def upload_portfolio(
    payload: models.PortfolioUploadRequest,
    user=Depends(get_current_user),
):
    weights, total_value = _normalize_request(payload)
    portfolio_store.set_portfolio(user["id"], weights, total_value)
    holdings = [models.NormalizedHolding(ticker=t, weight=w) for t, w in weights.items()]
    return models.PortfolioUploadResponse(user_id=user["id"], holdings=holdings, total_value=total_value)


@router.get(
    "/score",
    response_model=models.ScoreResponse,
    responses={404: {"model": models.ErrorResponse}},
)
def get_score(user=Depends(get_current_user)):
    try:
        weights = portfolio_store.get_portfolio(user["id"])
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found.") from exc
    total, breakdown, expected_return, suggestions, grade, distribution = pulse_score(weights)
    chart = [models.DiversificationSlice(label=k, weight=round(v, 4)) for k, v in distribution.items()]
    return models.ScoreResponse(
        pulse_score=total,
        grade=grade,
        breakdown=models.ScoreBreakdown(**breakdown),
        diversification_chart=chart,
        top_suggestions=suggestions,
    )


@router.get(
    "/model-comparison",
    response_model=models.ModelComparisonResponse,
    responses={404: {"model": models.ErrorResponse}},
)
def compare_models(user=Depends(get_current_user)):
    try:
        weights = portfolio_store.get_portfolio(user["id"])
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found.") from exc
    perf = expected_performance(weights)
    tracking = model_tracking_error(weights)
    model_performances = []
    for key, model_weights in MODEL_PORTFOLIOS.items():
        metrics = expected_performance(model_weights)
        model_performances.append(
            models.ModelPerformance(
                model_key=key,
                model_name=MODEL_NAMES.get(key, key.title()),
                expected_return=round(metrics["expected_return"], 4),
                volatility=round(metrics["volatility"], 4),
                tracking_error=tracking[key],
            )
        )
    return models.ModelComparisonResponse(
        user_expected_return=round(perf["expected_return"], 4),
        models=model_performances,
    )


@router.get(
    "/rebalance-suggestions",
    response_model=models.RebalanceSuggestionResponse,
    responses={404: {"model": models.ErrorResponse}},
)
def rebalance_suggestions(user=Depends(get_current_user)):
    try:
        weights = portfolio_store.get_portfolio(user["id"])
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found.") from exc
    tracking = model_tracking_error(weights)
    model_key = select_target_model(tracking)
    plan = generate_rebalance_plan(weights, model_key, portfolio_store.get_total_value(user["id"]))
    adjustments = [models.RebalanceAdjustment(**adj) for adj in plan["adjustments"]]
    return models.RebalanceSuggestionResponse(
        target_model=MODEL_NAMES.get(plan["target_model"], plan["target_model"].title()),
        target_weights=plan["target_weights"],
        adjustments=adjustments,
    )

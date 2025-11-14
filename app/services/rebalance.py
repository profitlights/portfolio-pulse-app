"""Rebalancing helper utilities."""
from __future__ import annotations

from typing import Dict, List

from ..config import MODEL_PORTFOLIOS


def select_target_model(tracking_error: Dict[str, float]) -> str:
    return min(tracking_error, key=tracking_error.get)


def generate_rebalance_plan(
    user_weights: Dict[str, float],
    target_model_key: str,
    portfolio_value: float,
) -> Dict[str, List[Dict[str, float]]]:
    target_weights = MODEL_PORTFOLIOS[target_model_key]
    adjustments = []
    for ticker in sorted(set(user_weights) | set(target_weights)):
        current = user_weights.get(ticker, 0.0)
        target = target_weights.get(ticker, 0.0)
        diff = round(target - current, 4)
        if abs(diff) < 0.005:
            continue
        action = "buy" if diff > 0 else "sell"
        notional = round(diff * portfolio_value, 2)
        adjustments.append(
            {
                "ticker": ticker,
                "action": action,
                "weight_diff": diff,
                "notional_change": notional,
            }
        )
    return {"target_model": target_model_key, "target_weights": target_weights, "adjustments": adjustments}

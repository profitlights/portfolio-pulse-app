"""Mathematical helpers for Portfolio Pulse."""
from __future__ import annotations

from typing import Dict, Iterable, Tuple


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(min(value, maximum), minimum)


def normalize_portfolio(items: Iterable[Tuple[str, float]]) -> Dict[str, float]:
    total = sum(amount for _, amount in items)
    if total <= 0:
        raise ValueError("Portfolio must have a positive total value.")
    return {ticker.upper(): amount / total for ticker, amount in items}

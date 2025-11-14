"""Scoring utilities for Portfolio Pulse."""
from __future__ import annotations

from typing import Dict, List, Tuple

from ..config import ASSET_CLASS_MAP, EXPECTED_RETURN_BY_ASSET, MODEL_PORTFOLIOS
from ..utils.math_ops import clamp

MAX_DIVERSIFICATION_SCORE = 30
MAX_RESILIENCE_SCORE = 30
MAX_RETURN_EFFICIENCY_SCORE = 20
MAX_RISK_BALANCE_SCORE = 20


def build_asset_class_distribution(weights: Dict[str, float]) -> Dict[str, float]:
    distribution: Dict[str, float] = {}
    for ticker, weight in weights.items():
        asset_class = ASSET_CLASS_MAP.get(ticker.upper(), "Other")
        distribution[asset_class] = distribution.get(asset_class, 0.0) + weight
    return distribution


def diversification_score(distribution: Dict[str, float]) -> float:
    evenness = sum(min(weight, 0.2) for weight in distribution.values())
    normalized = min(evenness / 1.0, 1.0)
    return round(normalized * MAX_DIVERSIFICATION_SCORE, 2)


def resilience_score(weights: Dict[str, float]) -> float:
    bonds = sum(weight for ticker, weight in weights.items() if ticker in {"TLT", "IEF", "BND", "TIP"})
    gold = sum(weight for ticker, weight in weights.items() if ticker in {"IAU", "GLD"})
    commodities = sum(weight for ticker, weight in weights.items() if ticker in {"DBC", "GSG"})
    buffer = bonds + 0.5 * (gold + commodities)
    normalized = clamp(buffer / 0.6, 0.0, 1.0)
    return round(normalized * MAX_RESILIENCE_SCORE, 2)


def return_efficiency_score(distribution: Dict[str, float]) -> Tuple[float, float]:
    expected_return = 0.0
    for asset_class, weight in distribution.items():
        expected = EXPECTED_RETURN_BY_ASSET.get(asset_class, EXPECTED_RETURN_BY_ASSET["Other"])
        expected_return += weight * expected
    normalized = clamp((expected_return - 0.02) / 0.06, 0.0, 1.0)
    score = round(normalized * MAX_RETURN_EFFICIENCY_SCORE, 2)
    return score, round(expected_return, 4)


def risk_balance_score(distribution: Dict[str, float]) -> float:
    equities = distribution.get("Equities", 0.0) + distribution.get("International Equities", 0.0)
    defensive = (
        distribution.get("Long Bonds", 0.0)
        + distribution.get("Intermediate Bonds", 0.0)
        + distribution.get("Core Bonds", 0.0)
        + distribution.get("Inflation Bonds", 0.0)
    )
    diversifiers = distribution.get("Gold", 0.0) + distribution.get("Commodities", 0.0) + distribution.get("Real Estate", 0.0)
    balance_gap = abs(equities - 0.45) + abs(defensive - 0.35) + abs(diversifiers - 0.20)
    normalized = clamp(1.0 - balance_gap, 0.0, 1.0)
    return round(normalized * MAX_RISK_BALANCE_SCORE, 2)


def pulse_score(weights: Dict[str, float]) -> Tuple[float, Dict[str, float], float, List[str]]:
    distribution = build_asset_class_distribution(weights)
    diversification = diversification_score(distribution)
    resilience = resilience_score(weights)
    return_efficiency, expected_return = return_efficiency_score(distribution)
    risk_balance = risk_balance_score(distribution)
    total = round(diversification + resilience + return_efficiency + risk_balance, 2)
    grade = "🟢" if total >= 80 else ("🟡" if total >= 60 else "🔴")
    suggestions = generate_suggestions(weights, distribution)
    breakdown = {
        "diversification": diversification,
        "resilience": resilience,
        "return_efficiency": return_efficiency,
        "risk_balance": risk_balance,
    }
    return total, breakdown, expected_return, suggestions, grade, distribution


def generate_suggestions(weights: Dict[str, float], distribution: Dict[str, float]) -> List[str]:
    ideas: List[str] = []
    largest = max(weights.items(), key=lambda item: item[1]) if weights else (None, 0)
    if largest[0] and largest[1] > 0.35:
        ideas.append(f"Reduce concentration in {largest[0]} to below 30%.")
    if distribution.get("Long Bonds", 0.0) + distribution.get("Intermediate Bonds", 0.0) < 0.25:
        ideas.append("Add more bonds to improve drawdown resilience.")
    if distribution.get("Gold", 0.0) + distribution.get("Commodities", 0.0) < 0.1:
        ideas.append("Introduce gold or commodities as an inflation hedge.")
    if not ideas:
        ideas.append("Portfolio is balanced relative to the model set. Maintain current allocations.")
    return ideas


def model_tracking_error(user_weights: Dict[str, float]) -> Dict[str, float]:
    tracking: Dict[str, float] = {}
    for model_key, model_weights in MODEL_PORTFOLIOS.items():
        diff = 0.0
        for ticker in set(user_weights) | set(model_weights):
            diff += abs(user_weights.get(ticker, 0.0) - model_weights.get(ticker, 0.0))
        tracking[model_key] = round(diff / 2, 4)
    return tracking

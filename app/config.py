"""Application configuration derived from the Portfolio Pulse spec."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class GlobalConfig:
    starting_value: float = 100.0
    currency: str = "USD"
    rebalance_type: str = "calendar"
    rebalance_frequency: str = "quarterly"
    expense_ratio_bps: int = 15
    trade_cost_bp_per_rebalance: int = 1
    data_source: str = "yahoo"
    data_interval: str = "1d"
    lookback_years: int = 15


GLOBAL_CONFIG = GlobalConfig()

MODEL_PORTFOLIOS: Dict[str, Dict[str, float]] = {
    "all_weather": {
        "VTI": 0.30,
        "TLT": 0.40,
        "IEF": 0.15,
        "IAU": 0.075,
        "DBC": 0.075,
    },
    "swensen": {
        "VTI": 0.30,
        "VXUS": 0.15,
        "VNQ": 0.20,
        "TLT": 0.15,
        "TIP": 0.15,
        "IAU": 0.05,
    },
}


def build_hybrid_portfolio() -> Dict[str, float]:
    """Blend All Weather and Swensen weights equally and normalize."""
    blend: Dict[str, float] = {}
    for model in ("all_weather", "swensen"):
        for ticker, weight in MODEL_PORTFOLIOS[model].items():
            blend[ticker] = blend.get(ticker, 0.0) + weight * 0.5
    total = sum(blend.values())
    return {ticker: weight / total for ticker, weight in blend.items()}


MODEL_PORTFOLIOS["hybrid"] = build_hybrid_portfolio()
MODEL_NAMES: Dict[str, str] = {
    "all_weather": "All Weather (Ray Dalio)",
    "swensen": "Swensen (Lazy Princeton)",
    "hybrid": "Hybrid 50",
}


ASSET_CLASS_MAP: Dict[str, str] = {
    "VTI": "Equities",
    "VOO": "Equities",
    "SPY": "Equities",
    "AAPL": "Equities",
    "MSFT": "Equities",
    "VXUS": "International Equities",
    "VEA": "International Equities",
    "VNQ": "Real Estate",
    "TLT": "Long Bonds",
    "IEF": "Intermediate Bonds",
    "BND": "Core Bonds",
    "TIP": "Inflation Bonds",
    "IAU": "Gold",
    "GLD": "Gold",
    "DBC": "Commodities",
    "GSG": "Commodities",
}


EXPECTED_RETURN_BY_ASSET: Dict[str, float] = {
    "Equities": 0.07,
    "International Equities": 0.065,
    "Real Estate": 0.06,
    "Long Bonds": 0.035,
    "Intermediate Bonds": 0.03,
    "Core Bonds": 0.03,
    "Inflation Bonds": 0.028,
    "Gold": 0.025,
    "Commodities": 0.03,
    "Other": 0.04,
}

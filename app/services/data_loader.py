"""Market data helpers using yfinance as the backend."""
from __future__ import annotations

import datetime as dt
from functools import lru_cache
from typing import Dict, List

import pandas as pd
import yfinance as yf

from ..config import GLOBAL_CONFIG


@lru_cache(maxsize=32)
def fetch_price_history(ticker: str, lookback_years: int | None = None) -> pd.Series:
    """Fetch adjusted close price history for the requested ticker."""
    years = lookback_years or GLOBAL_CONFIG.lookback_years
    end = dt.datetime.utcnow()
    start = end - dt.timedelta(days=365 * years)
    data = yf.download(ticker, start=start, end=end, interval=GLOBAL_CONFIG.data_interval, progress=False)
    if data.empty:
        raise ValueError(f"No price history for {ticker}.")
    return data["Adj Close"].dropna()


def annualized_return(series: pd.Series) -> float:
    start_price, end_price = series.iloc[0], series.iloc[-1]
    years = (series.index[-1] - series.index[0]).days / 365
    if years <= 0:
        return 0.0
    return (end_price / start_price) ** (1 / years) - 1


def annualized_volatility(series: pd.Series) -> float:
    returns = series.pct_change().dropna()
    return returns.std() * (252 ** 0.5)


def expected_performance(weights: Dict[str, float]) -> Dict[str, float]:
    """Compute expected return and volatility using historical data where possible."""
    rets: List[float] = []
    vols: List[float] = []
    for ticker, weight in weights.items():
        try:
            history = fetch_price_history(ticker)
            rets.append(weight * annualized_return(history))
            vols.append((weight ** 2) * (annualized_volatility(history) ** 2))
        except Exception:
            # If data fetch fails, fall back to conservative defaults.
            rets.append(weight * 0.04)
            vols.append((weight ** 2) * (0.10 ** 2))
    expected_return = sum(rets)
    expected_vol = (sum(vols)) ** 0.5
    return {"expected_return": expected_return, "volatility": expected_vol}

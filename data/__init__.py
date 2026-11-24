"""Market data loaders (Binance, Yahoo Finance, CSV, Synthetic scenarios)."""

from .fetcher import (
    fetch_binance_klines,
    fetch_yahoo_chart,
    load_csv,
    generate_synthetic_market,
)

__all__ = [
    "fetch_binance_klines",
    "fetch_yahoo_chart",
    "load_csv",
    "generate_synthetic_market",
]

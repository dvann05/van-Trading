"""Zero-dependency market data fetcher (Binance, Yahoo Finance, CSV, Synthetic)."""

import csv
import json
import math
import random
import time
import urllib.request
from typing import List
from models import Candle


def fetch_binance_klines(symbol: str = "BTCUSDT", interval: str = "1h", limit: int = 250) -> List[Candle]:
    """Fetch OHLCV candles from Binance public REST API."""
    url = (
        f"https://api.binance.com/api/v3/klines"
        f"?symbol={symbol.upper()}&interval={interval}&limit={min(limit, 1000)}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "TradingAnalyzer/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    candles: List[Candle] = []
    for row in raw:
        candles.append(Candle(
            timestamp=int(row[0]),
            open=float(row[1]),
            high=float(row[2]),
            low=float(row[3]),
            close=float(row[4]),
            volume=float(row[5]),
        ))
    return candles


def fetch_yahoo_chart(symbol: str = "GC=F", interval: str = "1d", range_str: str = "1y") -> List[Candle]:
    """Fetch OHLCV candles from Yahoo Finance public chart endpoint (stocks, forex, gold, indices)."""
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?interval={interval}&range={range_str}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    result = data["chart"]["result"][0]
    timestamps = result["timestamp"]
    quote = result["indicators"]["quote"][0]
    opens = quote["open"]
    highs = quote["high"]
    lows = quote["low"]
    closes = quote["close"]
    vols = quote["volume"]

    candles: List[Candle] = []
    for ts, o, h, l, c, v in zip(timestamps, opens, highs, lows, closes, vols):
        if None in (o, h, l, c):
            continue
        candles.append(Candle(
            timestamp=int(ts) * 1000,
            open=float(o),
            high=float(h),
            low=float(l),
            close=float(c),
            volume=float(v or 0.0),
        ))
    return candles


def load_csv(path: str) -> List[Candle]:
    """Load OHLCV data from CSV with columns: timestamp/date, open, high, low, close, volume."""
    candles: List[Candle] = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            norm = {k.strip().lower(): v.strip() for k, v in row.items() if k}
            ts_raw = norm.get("timestamp") or norm.get("time") or str(idx)
            try:
                ts = int(float(ts_raw))
            except ValueError:
                ts = idx
            candles.append(Candle(
                timestamp=ts,
                open=float(norm["open"]),
                high=float(norm["high"]),
                low=float(norm["low"]),
                close=float(norm["close"]),
                volume=float(norm.get("volume", 1000.0) or 1000.0),
            ))
    return candles


def generate_synthetic_market(
    scenario: str = "uptrend_breakout", count: int = 240, base_price: float = 100.0, seed: int = 42
) -> List[Candle]:
    """Generate realistic synthetic OHLCV data for offline testing & demos.

    Scenarios: uptrend_breakout, downtrend_reversal, squeeze_range, double_bottom
    """
    rng = random.Random(seed)
    now_ms = int(time.time() * 1000)
    step_ms = 3600 * 1000
    price = base_price
    candles: List[Candle] = []

    for i in range(count):
        ts = now_ms - (count - i) * step_ms
        vol_mult = 1.0
        drift = 0.0008
        volatility = 0.012

        if scenario == "uptrend_breakout":
            if i < count * 0.65:
                drift = 0.0012 + 0.002 * math.sin(i / 9.0)
            elif i < count * 0.88:
                # Tight consolidation (squeeze)
                drift = 0.0001
                volatility = 0.004
                vol_mult = 0.6
            else:
                # Strong breakout with volume expansion
                drift = 0.0065
                volatility = 0.014
                vol_mult = 2.4
        elif scenario == "downtrend_reversal":
            if i < count * 0.78:
                drift = -0.0018 + 0.0015 * math.sin(i / 8.0)
            else:
                drift = 0.0055
                vol_mult = 1.9
        elif scenario == "squeeze_range":
            drift = 0.0025 * math.sin(i / 7.0)
            volatility = 0.0035 if i > count - 30 else 0.010
            vol_mult = 0.5 if i > count - 30 else 1.0
        elif scenario == "double_bottom":
            if i < count * 0.4:
                drift = -0.0025
            elif i < count * 0.55:
                drift = 0.0030
            elif i < count * 0.72:
                drift = -0.0028
            else:
                drift = 0.0045
                vol_mult = 1.8

        ret = drift + rng.gauss(0.0, volatility)
        o = price
        c = max(0.01, o * (1.0 + ret))
        wick_up = abs(rng.gauss(0.0, volatility * 0.6)) * max(o, c)
        wick_dn = abs(rng.gauss(0.0, volatility * 0.6)) * min(o, c)
        h = max(o, c) + wick_up
        l = max(0.005, min(o, c) - wick_dn)
        volume = abs(rng.gauss(1200.0, 300.0)) * vol_mult
        candles.append(Candle(ts, o, h, l, c, volume))
        price = c

    return candles

"""Volatility technical indicators."""

import math
from typing import Dict, List, Optional
from models import Candle
from .trend import ema, sma


def true_range(candles: List[Candle]) -> List[float]:
    n = len(candles)
    if n == 0:
        return []
    tr = [candles[0].high - candles[0].low]
    for i in range(1, n):
        tr.append(
            max(
                candles[i].high - candles[i].low,
                abs(candles[i].high - candles[i - 1].close),
                abs(candles[i].low - candles[i - 1].close),
            )
        )
    return tr


def atr(candles: List[Candle], period: int = 14) -> List[Optional[float]]:
    n = len(candles)
    out: List[Optional[float]] = [None] * n
    if n < period or period <= 0:
        return out
    tr = true_range(candles)
    cur = sum(tr[:period]) / period
    out[period - 1] = cur
    for i in range(period, n):
        cur = (cur * (period - 1) + tr[i]) / period
        out[i] = cur
    return out


def std_dev(values: List[float], period: int = 20) -> List[Optional[float]]:
    n = len(values)
    out: List[Optional[float]] = [None] * n
    if n < period or period <= 1:
        return out
    for i in range(period - 1, n):
        win = values[i - period + 1 : i + 1]
        mean = sum(win) / period
        var = sum((x - mean) ** 2 for x in win) / period
        out[i] = math.sqrt(var)
    return out


def bollinger_bands(
    closes: List[float], period: int = 20, mult: float = 2.0
) -> Dict[str, List[Optional[float]]]:
    mid = sma(closes, period)
    sd = std_dev(closes, period)
    n = len(closes)
    upper: List[Optional[float]] = [None] * n
    lower: List[Optional[float]] = [None] * n
    pct_b: List[Optional[float]] = [None] * n
    bandwidth: List[Optional[float]] = [None] * n

    for i in range(n):
        if mid[i] is not None and sd[i] is not None:
            u = mid[i] + mult * sd[i]  # type: ignore[operator]
            l = mid[i] - mult * sd[i]  # type: ignore[operator]
            upper[i] = u
            lower[i] = l
            pct_b[i] = (closes[i] - l) / (u - l) if u != l else 0.5
            bandwidth[i] = 100.0 * (u - l) / mid[i] if mid[i] != 0 else 0.0  # type: ignore[operator]

    return {
        "upper": upper,
        "middle": mid,
        "lower": lower,
        "percent_b": pct_b,
        "bandwidth": bandwidth,
    }


def keltner_channels(
    candles: List[Candle], ema_period: int = 20, atr_period: int = 10, mult: float = 1.5
) -> Dict[str, List[Optional[float]]]:
    closes = [c.close for c in candles]
    mid = ema(closes, ema_period)
    a = atr(candles, atr_period)
    upper = [
        (m + mult * v) if (m is not None and v is not None) else None
        for m, v in zip(mid, a)
    ]
    lower = [
        (m - mult * v) if (m is not None and v is not None) else None
        for m, v in zip(mid, a)
    ]
    return {"upper": upper, "middle": mid, "lower": lower}


def donchian_channels(candles: List[Candle], period: int = 20) -> Dict[str, List[Optional[float]]]:
    n = len(candles)
    upper: List[Optional[float]] = [None] * n
    lower: List[Optional[float]] = [None] * n
    mid: List[Optional[float]] = [None] * n
    for i in range(period - 1, n):
        hh = max(c.high for c in candles[i - period + 1 : i + 1])
        ll = min(c.low for c in candles[i - period + 1 : i + 1])
        upper[i] = hh
        lower[i] = ll
        mid[i] = (hh + ll) / 2.0
    return {"upper": upper, "middle": mid, "lower": lower}


def historical_volatility(closes: List[float], period: int = 20, annualize: int = 252) -> List[Optional[float]]:
    n = len(closes)
    out: List[Optional[float]] = [None] * n
    if n <= period:
        return out
    log_ret = [0.0] * n
    for i in range(1, n):
        if closes[i] > 0 and closes[i - 1] > 0:
            log_ret[i] = math.log(closes[i] / closes[i - 1])
    for i in range(period, n):
        win = log_ret[i - period + 1 : i + 1]
        mean = sum(win) / period
        var = sum((x - mean) ** 2 for x in win) / max(period - 1, 1)
        out[i] = math.sqrt(var * annualize) * 100.0
    return out


def chaikin_volatility(candles: List[Candle], ema_period: int = 10, roc_period: int = 10) -> List[Optional[float]]:
    hl = [c.high - c.low for c in candles]
    e = ema(hl, ema_period)
    n = len(candles)
    out: List[Optional[float]] = [None] * n
    for i in range(roc_period, n):
        if e[i] is not None and e[i - roc_period] is not None and e[i - roc_period] != 0:
            out[i] = 100.0 * (e[i] - e[i - roc_period]) / e[i - roc_period]  # type: ignore[operator]
    return out


def ttm_squeeze(
    candles: List[Candle], period: int = 20, bb_mult: float = 2.0, kc_mult: float = 1.5
) -> Dict[str, List[Optional[float]]]:
    """Detect TTM Squeeze (Bollinger Bands inside Keltner Channels) + momentum histogram."""
    closes = [c.close for c in candles]
    bb = bollinger_bands(closes, period, bb_mult)
    kc = keltner_channels(candles, period, period, kc_mult)
    dc = donchian_channels(candles, period)
    n = len(candles)
    squeeze_on: List[Optional[float]] = [None] * n  # 1.0 = squeeze active, 0.0 = off
    momentum_val: List[Optional[float]] = [None] * n

    for i in range(n):
        if (
            bb["upper"][i] is not None
            and bb["lower"][i] is not None
            and kc["upper"][i] is not None
            and kc["lower"][i] is not None
        ):
            is_sq = bb["lower"][i] > kc["lower"][i] and bb["upper"][i] < kc["upper"][i]  # type: ignore[operator]
            squeeze_on[i] = 1.0 if is_sq else 0.0
        if dc["middle"][i] is not None and bb["middle"][i] is not None:
            baseline = (dc["middle"][i] + bb["middle"][i]) / 2.0  # type: ignore[operator]
            momentum_val[i] = closes[i] - baseline

    return {"squeeze_on": squeeze_on, "momentum": momentum_val}

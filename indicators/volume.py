"""Volume technical indicators."""

from typing import Dict, List, Optional
from models import Candle
from .trend import ema, sma


def obv(candles: List[Candle]) -> List[float]:
    n = len(candles)
    if n == 0:
        return []
    out = [0.0] * n
    for i in range(1, n):
        if candles[i].close > candles[i - 1].close:
            out[i] = out[i - 1] + candles[i].volume
        elif candles[i].close < candles[i - 1].close:
            out[i] = out[i - 1] - candles[i].volume
        else:
            out[i] = out[i - 1]
    return out


def vwap(candles: List[Candle]) -> List[float]:
    out: List[float] = []
    cum_pv = 0.0
    cum_v = 0.0
    for c in candles:
        cum_pv += c.typical_price * c.volume
        cum_v += c.volume
        out.append(cum_pv / cum_v if cum_v > 0 else c.close)
    return out


def ad_line(candles: List[Candle]) -> List[float]:
    out: List[float] = []
    acc = 0.0
    for c in candles:
        rng = c.high - c.low
        mfm = ((c.close - c.low) - (c.high - c.close)) / rng if rng > 0 else 0.0
        acc += mfm * c.volume
        out.append(acc)
    return out


def cmf(candles: List[Candle], period: int = 20) -> List[Optional[float]]:
    n = len(candles)
    out: List[Optional[float]] = [None] * n
    mfv = []
    for c in candles:
        rng = c.high - c.low
        mfm = ((c.close - c.low) - (c.high - c.close)) / rng if rng > 0 else 0.0
        mfv.append(mfm * c.volume)
    for i in range(period - 1, n):
        vol_sum = sum(c.volume for c in candles[i - period + 1 : i + 1])
        out[i] = sum(mfv[i - period + 1 : i + 1]) / vol_sum if vol_sum > 0 else 0.0
    return out


def volume_oscillator(candles: List[Candle], fast: int = 5, slow: int = 10) -> List[Optional[float]]:
    vols = [c.volume for c in candles]
    ef = ema(vols, fast)
    es = ema(vols, slow)
    out: List[Optional[float]] = [None] * len(candles)
    for i in range(len(candles)):
        if ef[i] is not None and es[i] is not None and es[i] != 0:
            out[i] = 100.0 * (ef[i] - es[i]) / es[i]  # type: ignore[operator]
    return out


def force_index(candles: List[Candle], period: int = 13) -> List[Optional[float]]:
    n = len(candles)
    if n < 2:
        return [None] * n
    raw = [0.0] + [
        (candles[i].close - candles[i - 1].close) * candles[i].volume for i in range(1, n)
    ]
    return ema(raw, period)


def ease_of_movement(candles: List[Candle], period: int = 14) -> List[Optional[float]]:
    n = len(candles)
    if n < 2:
        return [None] * n
    raw = [0.0] * n
    for i in range(1, n):
        dm = ((candles[i].high + candles[i].low) / 2.0) - (
            (candles[i - 1].high + candles[i - 1].low) / 2.0
        )
        rng = candles[i].high - candles[i].low
        br = (candles[i].volume / 1e6) / rng if rng > 0 else 0.0
        raw[i] = dm / br if br > 0 else 0.0
    return sma(raw, period)


def volume_profile(candles: List[Candle], bins: int = 24) -> Dict[str, float]:
    """Compute Point of Control (POC), Value Area High (VAH), and Value Area Low (VAL)."""
    if not candles:
        return {"poc": 0.0, "vah": 0.0, "val": 0.0}
    lo = min(c.low for c in candles)
    hi = max(c.high for c in candles)
    if hi <= lo:
        return {"poc": lo, "vah": hi, "val": lo}
    step = (hi - lo) / bins
    hist = [0.0] * bins
    for c in candles:
        idx = int((c.typical_price - lo) / step)
        idx = max(0, min(bins - 1, idx))
        hist[idx] += c.volume

    poc_idx = max(range(bins), key=lambda i: hist[i])
    poc = lo + (poc_idx + 0.5) * step

    total_vol = sum(hist)
    target = total_vol * 0.70
    acc = hist[poc_idx]
    left = poc_idx
    right = poc_idx
    while acc < target and (left > 0 or right < bins - 1):
        lv = hist[left - 1] if left > 0 else -1.0
        rv = hist[right + 1] if right < bins - 1 else -1.0
        if lv >= rv and left > 0:
            left -= 1
            acc += hist[left]
        elif right < bins - 1:
            right += 1
            acc += hist[right]
        else:
            break

    return {
        "poc": poc,
        "vah": lo + (right + 1) * step,
        "val": lo + left * step,
    }

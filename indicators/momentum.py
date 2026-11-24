"""Momentum & oscillator technical indicators."""

from typing import Dict, List, Optional
from models import Candle
from .trend import ema, sma


def rsi(closes: List[float], period: int = 14) -> List[Optional[float]]:
    n = len(closes)
    out: List[Optional[float]] = [None] * n
    if n <= period:
        return out
    gains = [0.0] * n
    losses = [0.0] * n
    for i in range(1, n):
        diff = closes[i] - closes[i - 1]
        gains[i] = max(diff, 0.0)
        losses[i] = max(-diff, 0.0)

    avg_gain = sum(gains[1 : period + 1]) / period
    avg_loss = sum(losses[1 : period + 1]) / period
    out[period] = 100.0 if avg_loss == 0 else 100.0 - (100.0 / (1.0 + avg_gain / avg_loss))

    for i in range(period + 1, n):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        out[i] = 100.0 if avg_loss == 0 else 100.0 - (100.0 / (1.0 + avg_gain / avg_loss))
    return out


def stochastic(
    candles: List[Candle], k_period: int = 14, d_period: int = 3, smooth_k: int = 3
) -> Dict[str, List[Optional[float]]]:
    n = len(candles)
    raw_k: List[Optional[float]] = [None] * n
    for i in range(k_period - 1, n):
        hh = max(c.high for c in candles[i - k_period + 1 : i + 1])
        ll = min(c.low for c in candles[i - k_period + 1 : i + 1])
        raw_k[i] = 100.0 * (candles[i].close - ll) / (hh - ll) if hh != ll else 50.0

    def _sma_opt(arr: List[Optional[float]], p: int) -> List[Optional[float]]:
        res: List[Optional[float]] = [None] * len(arr)
        for i in range(len(arr)):
            if i >= p - 1:
                win = arr[i - p + 1 : i + 1]
                if all(v is not None for v in win):
                    res[i] = sum(win) / p  # type: ignore[arg-type]
        return res

    k_line = _sma_opt(raw_k, smooth_k)
    d_line = _sma_opt(k_line, d_period)
    return {"k": k_line, "d": d_line}


def stoch_rsi(
    closes: List[float], rsi_period: int = 14, stoch_period: int = 14, k_smooth: int = 3, d_smooth: int = 3
) -> Dict[str, List[Optional[float]]]:
    r = rsi(closes, rsi_period)
    n = len(closes)
    raw: List[Optional[float]] = [None] * n
    for i in range(n):
        if i >= stoch_period - 1:
            win = r[i - stoch_period + 1 : i + 1]
            if all(v is not None for v in win):
                lo = min(win)  # type: ignore[type-var]
                hi = max(win)  # type: ignore[type-var]
                raw[i] = 100.0 * (r[i] - lo) / (hi - lo) if hi != lo else 50.0  # type: ignore[operator]

    def _sma_opt(arr: List[Optional[float]], p: int) -> List[Optional[float]]:
        res: List[Optional[float]] = [None] * len(arr)
        for i in range(len(arr)):
            if i >= p - 1:
                win = arr[i - p + 1 : i + 1]
                if all(v is not None for v in win):
                    res[i] = sum(win) / p  # type: ignore[arg-type]
        return res

    k = _sma_opt(raw, k_smooth)
    d = _sma_opt(k, d_smooth)
    return {"k": k, "d": d}


def macd(
    closes: List[float], fast: int = 12, slow: int = 26, signal: int = 9
) -> Dict[str, List[Optional[float]]]:
    n = len(closes)
    e_fast = ema(closes, fast)
    e_slow = ema(closes, slow)
    macd_line: List[Optional[float]] = [
        (a - b) if (a is not None and b is not None) else None
        for a, b in zip(e_fast, e_slow)
    ]
    valid_idx = [i for i, v in enumerate(macd_line) if v is not None]
    sig_line: List[Optional[float]] = [None] * n
    if len(valid_idx) >= signal:
        clean = [macd_line[i] for i in valid_idx]
        sig_clean = ema(clean, signal)  # type: ignore[arg-type]
        for idx, val in zip(valid_idx, sig_clean):
            sig_line[idx] = val
    hist: List[Optional[float]] = [
        (m - s) if (m is not None and s is not None) else None
        for m, s in zip(macd_line, sig_line)
    ]
    return {"macd": macd_line, "signal": sig_line, "histogram": hist}


def cci(candles: List[Candle], period: int = 20) -> List[Optional[float]]:
    n = len(candles)
    out: List[Optional[float]] = [None] * n
    tp = [c.typical_price for c in candles]
    tp_sma = sma(tp, period)
    for i in range(period - 1, n):
        mean = tp_sma[i]
        if mean is None:
            continue
        mad = sum(abs(tp[j] - mean) for j in range(i - period + 1, i + 1)) / period
        out[i] = (tp[i] - mean) / (0.015 * mad) if mad > 0 else 0.0
    return out


def williams_r(candles: List[Candle], period: int = 14) -> List[Optional[float]]:
    n = len(candles)
    out: List[Optional[float]] = [None] * n
    for i in range(period - 1, n):
        hh = max(c.high for c in candles[i - period + 1 : i + 1])
        ll = min(c.low for c in candles[i - period + 1 : i + 1])
        out[i] = -100.0 * (hh - candles[i].close) / (hh - ll) if hh != ll else -50.0
    return out


def roc(closes: List[float], period: int = 12) -> List[Optional[float]]:
    n = len(closes)
    out: List[Optional[float]] = [None] * n
    for i in range(period, n):
        prev = closes[i - period]
        out[i] = 100.0 * (closes[i] - prev) / prev if prev != 0 else 0.0
    return out


def momentum(closes: List[float], period: int = 10) -> List[Optional[float]]:
    n = len(closes)
    out: List[Optional[float]] = [None] * n
    for i in range(period, n):
        out[i] = closes[i] - closes[i - period]
    return out


def mfi(candles: List[Candle], period: int = 14) -> List[Optional[float]]:
    n = len(candles)
    out: List[Optional[float]] = [None] * n
    if n <= period:
        return out
    pos_mf = [0.0] * n
    neg_mf = [0.0] * n
    for i in range(1, n):
        tp_cur = candles[i].typical_price
        tp_prev = candles[i - 1].typical_price
        rmf = tp_cur * candles[i].volume
        if tp_cur > tp_prev:
            pos_mf[i] = rmf
        elif tp_cur < tp_prev:
            neg_mf[i] = rmf
    for i in range(period, n):
        p_sum = sum(pos_mf[i - period + 1 : i + 1])
        n_sum = sum(neg_mf[i - period + 1 : i + 1])
        out[i] = 100.0 if n_sum == 0 else 100.0 - (100.0 / (1.0 + p_sum / n_sum))
    return out


def awesome_oscillator(candles: List[Candle], fast: int = 5, slow: int = 34) -> List[Optional[float]]:
    mid = [c.midpoint for c in candles]
    s_fast = sma(mid, fast)
    s_slow = sma(mid, slow)
    return [
        (a - b) if (a is not None and b is not None) else None
        for a, b in zip(s_fast, s_slow)
    ]


def ultimate_oscillator(
    candles: List[Candle], p1: int = 7, p2: int = 14, p3: int = 28
) -> List[Optional[float]]:
    n = len(candles)
    out: List[Optional[float]] = [None] * n
    if n <= p3:
        return out
    bp = [0.0] * n
    tr = [0.0] * n
    for i in range(1, n):
        min_lc = min(candles[i].low, candles[i - 1].close)
        max_hc = max(candles[i].high, candles[i - 1].close)
        bp[i] = candles[i].close - min_lc
        tr[i] = max_hc - min_lc

    for i in range(p3, n):
        a1 = sum(bp[i - p1 + 1 : i + 1]) / max(sum(tr[i - p1 + 1 : i + 1]), 1e-12)
        a2 = sum(bp[i - p2 + 1 : i + 1]) / max(sum(tr[i - p2 + 1 : i + 1]), 1e-12)
        a3 = sum(bp[i - p3 + 1 : i + 1]) / max(sum(tr[i - p3 + 1 : i + 1]), 1e-12)
        out[i] = 100.0 * (4.0 * a1 + 2.0 * a2 + a3) / 7.0
    return out


def trix(closes: List[float], period: int = 15) -> List[Optional[float]]:
    e1 = ema(closes, period)
    idx1 = [i for i, v in enumerate(e1) if v is not None]
    if len(idx1) < period:
        return [None] * len(closes)
    e2_raw = ema([e1[i] for i in idx1], period)  # type: ignore[arg-type]
    e2: List[Optional[float]] = [None] * len(closes)
    for i, v in zip(idx1, e2_raw):
        e2[i] = v
    idx2 = [i for i, v in enumerate(e2) if v is not None]
    if len(idx2) < period:
        return [None] * len(closes)
    e3_raw = ema([e2[i] for i in idx2], period)  # type: ignore[arg-type]
    e3: List[Optional[float]] = [None] * len(closes)
    for i, v in zip(idx2, e3_raw):
        e3[i] = v
    out: List[Optional[float]] = [None] * len(closes)
    for i in range(1, len(closes)):
        if e3[i] is not None and e3[i - 1] is not None and e3[i - 1] != 0:
            out[i] = 100.0 * (e3[i] - e3[i - 1]) / e3[i - 1]  # type: ignore[operator]
    return out


def cmo(closes: List[float], period: int = 14) -> List[Optional[float]]:
    n = len(closes)
    out: List[Optional[float]] = [None] * n
    if n <= period:
        return out
    up = [0.0] * n
    dn = [0.0] * n
    for i in range(1, n):
        d = closes[i] - closes[i - 1]
        up[i] = max(d, 0.0)
        dn[i] = max(-d, 0.0)
    for i in range(period, n):
        su = sum(up[i - period + 1 : i + 1])
        sd = sum(dn[i - period + 1 : i + 1])
        out[i] = 100.0 * (su - sd) / (su + sd) if (su + sd) > 0 else 0.0
    return out

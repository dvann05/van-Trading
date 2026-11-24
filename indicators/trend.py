"""Trend technical indicators (pure Python, zero external dependencies)."""

import math
from typing import Dict, List, Optional, Tuple
from models import Candle


def sma(values: List[float], period: int) -> List[Optional[float]]:
    n = len(values)
    out: List[Optional[float]] = [None] * n
    if period <= 0 or n < period:
        return out
    window_sum = sum(values[:period])
    out[period - 1] = window_sum / period
    for i in range(period, n):
        window_sum += values[i] - values[i - period]
        out[i] = window_sum / period
    return out


def ema(values: List[float], period: int) -> List[Optional[float]]:
    n = len(values)
    out: List[Optional[float]] = [None] * n
    if period <= 0 or n < period:
        return out
    k = 2.0 / (period + 1)
    first = sum(values[:period]) / period
    out[period - 1] = first
    prev = first
    for i in range(period, n):
        prev = values[i] * k + prev * (1.0 - k)
        out[i] = prev
    return out


def _ema_optional(values: List[Optional[float]], period: int) -> List[Optional[float]]:
    valid_indices = [i for i, v in enumerate(values) if v is not None]
    out: List[Optional[float]] = [None] * len(values)
    if len(valid_indices) < period or period <= 0:
        return out
    start = valid_indices[0]
    clean = [values[i] for i in valid_indices]
    computed = ema(clean, period)  # type: ignore[arg-type]
    for idx, val in zip(valid_indices, computed):
        out[idx] = val
    return out


def wma(values: List[float], period: int) -> List[Optional[float]]:
    n = len(values)
    out: List[Optional[float]] = [None] * n
    if period <= 0 or n < period:
        return out
    denom = period * (period + 1) / 2.0
    for i in range(period - 1, n):
        total = 0.0
        for j in range(period):
            total += values[i - period + 1 + j] * (j + 1)
        out[i] = total / denom
    return out


def dema(values: List[float], period: int) -> List[Optional[float]]:
    e1 = ema(values, period)
    e2 = _ema_optional(e1, period)
    return [
        (2.0 * a - b) if (a is not None and b is not None) else None
        for a, b in zip(e1, e2)
    ]


def tema(values: List[float], period: int) -> List[Optional[float]]:
    e1 = ema(values, period)
    e2 = _ema_optional(e1, period)
    e3 = _ema_optional(e2, period)
    return [
        (3.0 * a - 3.0 * b + c) if (a is not None and b is not None and c is not None) else None
        for a, b, c in zip(e1, e2, e3)
    ]


def hma(values: List[float], period: int) -> List[Optional[float]]:
    if period < 2 or len(values) < period:
        return [None] * len(values)
    half = max(1, period // 2)
    sqrt_p = max(1, int(math.sqrt(period)))
    w_half = wma(values, half)
    w_full = wma(values, period)
    diff: List[Optional[float]] = [
        (2.0 * a - b) if (a is not None and b is not None) else None
        for a, b in zip(w_half, w_full)
    ]
    valid_indices = [i for i, v in enumerate(diff) if v is not None]
    out: List[Optional[float]] = [None] * len(values)
    if len(valid_indices) < sqrt_p:
        return out
    clean = [diff[i] for i in valid_indices]
    computed = wma(clean, sqrt_p)  # type: ignore[arg-type]
    for idx, val in zip(valid_indices, computed):
        out[idx] = val
    return out


def vwma(candles: List[Candle], period: int = 20) -> List[Optional[float]]:
    n = len(candles)
    out: List[Optional[float]] = [None] * n
    if period <= 0 or n < period:
        return out
    for i in range(period - 1, n):
        pv = 0.0
        v_sum = 0.0
        for j in range(i - period + 1, i + 1):
            pv += candles[j].close * candles[j].volume
            v_sum += candles[j].volume
        out[i] = pv / v_sum if v_sum > 0 else candles[i].close
    return out


def ichimoku(
    candles: List[Candle],
    tenkan_period: int = 9,
    kijun_period: int = 26,
    senkou_b_period: int = 52,
) -> Dict[str, List[Optional[float]]]:
    n = len(candles)
    tenkan: List[Optional[float]] = [None] * n
    kijun: List[Optional[float]] = [None] * n
    senkou_a: List[Optional[float]] = [None] * n
    senkou_b: List[Optional[float]] = [None] * n
    chikou: List[Optional[float]] = [None] * n

    for i in range(n):
        if i >= tenkan_period - 1:
            hh = max(c.high for c in candles[i - tenkan_period + 1 : i + 1])
            ll = min(c.low for c in candles[i - tenkan_period + 1 : i + 1])
            tenkan[i] = (hh + ll) / 2.0
        if i >= kijun_period - 1:
            hh = max(c.high for c in candles[i - kijun_period + 1 : i + 1])
            ll = min(c.low for c in candles[i - kijun_period + 1 : i + 1])
            kijun[i] = (hh + ll) / 2.0
        if tenkan[i] is not None and kijun[i] is not None:
            senkou_a[i] = (tenkan[i] + kijun[i]) / 2.0
        if i >= senkou_b_period - 1:
            hh = max(c.high for c in candles[i - senkou_b_period + 1 : i + 1])
            ll = min(c.low for c in candles[i - senkou_b_period + 1 : i + 1])
            senkou_b[i] = (hh + ll) / 2.0
        if i >= kijun_period:
            chikou[i - kijun_period] = candles[i].close

    return {
        "tenkan": tenkan,
        "kijun": kijun,
        "senkou_a": senkou_a,
        "senkou_b": senkou_b,
        "chikou": chikou,
    }


def adx(candles: List[Candle], period: int = 14) -> Dict[str, List[Optional[float]]]:
    n = len(candles)
    adx_vals: List[Optional[float]] = [None] * n
    plus_di: List[Optional[float]] = [None] * n
    minus_di: List[Optional[float]] = [None] * n
    if n < period * 2 + 1:
        return {"adx": adx_vals, "plus_di": plus_di, "minus_di": minus_di}

    tr_list = [0.0] * n
    pdm_list = [0.0] * n
    mdm_list = [0.0] * n
    for i in range(1, n):
        up = candles[i].high - candles[i - 1].high
        down = candles[i - 1].low - candles[i].low
        pdm_list[i] = up if (up > down and up > 0) else 0.0
        mdm_list[i] = down if (down > up and down > 0) else 0.0
        tr_list[i] = max(
            candles[i].high - candles[i].low,
            abs(candles[i].high - candles[i - 1].close),
            abs(candles[i].low - candles[i - 1].close),
        )

    tr_smooth = sum(tr_list[1 : period + 1])
    pdm_smooth = sum(pdm_list[1 : period + 1])
    mdm_smooth = sum(mdm_list[1 : period + 1])

    dx_list: List[Optional[float]] = [None] * n
    for i in range(period, n):
        if i > period:
            tr_smooth = tr_smooth - (tr_smooth / period) + tr_list[i]
            pdm_smooth = pdm_smooth - (pdm_smooth / period) + pdm_list[i]
            mdm_smooth = mdm_smooth - (mdm_smooth / period) + mdm_list[i]
        pdi = 100.0 * (pdm_smooth / tr_smooth) if tr_smooth > 0 else 0.0
        mdi = 100.0 * (mdm_smooth / tr_smooth) if tr_smooth > 0 else 0.0
        plus_di[i] = pdi
        minus_di[i] = mdi
        denom = pdi + mdi
        dx_list[i] = 100.0 * abs(pdi - mdi) / denom if denom > 0 else 0.0

    first_adx_idx = period * 2 - 1
    valid_dx = [dx_list[j] for j in range(period, first_adx_idx + 1) if dx_list[j] is not None]
    if len(valid_dx) == period:
        prev_adx = sum(valid_dx) / period
        adx_vals[first_adx_idx] = prev_adx
        for i in range(first_adx_idx + 1, n):
            dx_v = dx_list[i] or 0.0
            prev_adx = ((prev_adx * (period - 1)) + dx_v) / period
            adx_vals[i] = prev_adx

    return {"adx": adx_vals, "plus_di": plus_di, "minus_di": minus_di}


def parabolic_sar(
    candles: List[Candle], af_start: float = 0.02, af_step: float = 0.02, af_max: float = 0.2
) -> Tuple[List[Optional[float]], List[int]]:
    n = len(candles)
    sar: List[Optional[float]] = [None] * n
    trend: List[int] = [0] * n  # 1 = bullish, -1 = bearish
    if n < 2:
        return sar, trend

    is_bull = candles[1].close >= candles[0].close
    ep = candles[1].high if is_bull else candles[1].low
    cur_sar = candles[0].low if is_bull else candles[0].high
    af = af_start
    sar[1] = cur_sar
    trend[1] = 1 if is_bull else -1

    for i in range(2, n):
        prev_sar = cur_sar
        cur_sar = prev_sar + af * (ep - prev_sar)
        if is_bull:
            cur_sar = min(cur_sar, candles[i - 1].low, candles[i - 2].low)
            if candles[i].low < cur_sar:
                is_bull = False
                cur_sar = ep
                ep = candles[i].low
                af = af_start
            else:
                if candles[i].high > ep:
                    ep = candles[i].high
                    af = min(af_max, af + af_step)
        else:
            cur_sar = max(cur_sar, candles[i - 1].high, candles[i - 2].high)
            if candles[i].high > cur_sar:
                is_bull = True
                cur_sar = ep
                ep = candles[i].high
                af = af_start
            else:
                if candles[i].low < ep:
                    ep = candles[i].low
                    af = min(af_max, af + af_step)
        sar[i] = cur_sar
        trend[i] = 1 if is_bull else -1

    return sar, trend


def supertrend(
    candles: List[Candle], period: int = 10, multiplier: float = 3.0
) -> Tuple[List[Optional[float]], List[int]]:
    from .volatility import atr

    n = len(candles)
    st: List[Optional[float]] = [None] * n
    direction: List[int] = [0] * n
    atr_vals = atr(candles, period)

    upper_band: List[Optional[float]] = [None] * n
    lower_band: List[Optional[float]] = [None] * n

    for i in range(n):
        if atr_vals[i] is None:
            continue
        hl2 = candles[i].midpoint
        basic_upper = hl2 + multiplier * atr_vals[i]  # type: ignore[operator]
        basic_lower = hl2 - multiplier * atr_vals[i]  # type: ignore[operator]

        if i == 0 or upper_band[i - 1] is None:
            upper_band[i] = basic_upper
            lower_band[i] = basic_lower
            direction[i] = 1
            st[i] = lower_band[i]
            continue

        prev_ub = upper_band[i - 1]
        prev_lb = lower_band[i - 1]
        upper_band[i] = (
            basic_upper
            if (basic_upper < prev_ub or candles[i - 1].close > prev_ub)  # type: ignore[operator]
            else prev_ub
        )
        lower_band[i] = (
            basic_lower
            if (basic_lower > prev_lb or candles[i - 1].close < prev_lb)  # type: ignore[operator]
            else prev_lb
        )

        prev_st = st[i - 1]
        if prev_st == prev_ub:
            if candles[i].close <= upper_band[i]:  # type: ignore[operator]
                st[i] = upper_band[i]
                direction[i] = -1
            else:
                st[i] = lower_band[i]
                direction[i] = 1
        else:
            if candles[i].close >= lower_band[i]:  # type: ignore[operator]
                st[i] = lower_band[i]
                direction[i] = 1
            else:
                st[i] = upper_band[i]
                direction[i] = -1

    return st, direction


def aroon(candles: List[Candle], period: int = 25) -> Dict[str, List[Optional[float]]]:
    n = len(candles)
    up: List[Optional[float]] = [None] * n
    down: List[Optional[float]] = [None] * n
    osc: List[Optional[float]] = [None] * n
    if n <= period:
        return {"up": up, "down": down, "osc": osc}
    for i in range(period, n):
        window = candles[i - period : i + 1]
        highs = [c.high for c in window]
        lows = [c.low for c in window]
        idx_high = len(highs) - 1 - highs[::-1].index(max(highs))
        idx_low = len(lows) - 1 - lows[::-1].index(min(lows))
        days_since_high = period - idx_high
        days_since_low = period - idx_low
        u = 100.0 * (period - days_since_high) / period
        d = 100.0 * (period - days_since_low) / period
        up[i] = u
        down[i] = d
        osc[i] = u - d
    return {"up": up, "down": down, "osc": osc}


def linear_regression_slope(values: List[float], period: int = 14) -> List[Optional[float]]:
    n = len(values)
    out: List[Optional[float]] = [None] * n
    if period < 2 or n < period:
        return out
    x_mean = (period - 1) / 2.0
    denom = sum((x - x_mean) ** 2 for x in range(period))
    for i in range(period - 1, n):
        window = values[i - period + 1 : i + 1]
        y_mean = sum(window) / period
        num = sum((x - x_mean) * (y - y_mean) for x, y in enumerate(window))
        out[i] = num / denom if denom > 0 else 0.0
    return out

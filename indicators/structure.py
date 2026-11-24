"""Support/Resistance, Pivots, Fibonacci, and Smart Money Concepts (SMC) structure."""

from typing import Any, Dict, List, Tuple
from models import Candle


def pivot_points_classic(high: float, low: float, close: float) -> Dict[str, float]:
    p = (high + low + close) / 3.0
    r1 = 2 * p - low
    s1 = 2 * p - high
    r2 = p + (high - low)
    s2 = p - (high - low)
    r3 = high + 2 * (p - low)
    s3 = low - 2 * (high - p)
    return {"P": p, "R1": r1, "R2": r2, "R3": r3, "S1": s1, "S2": s2, "S3": s3}


def pivot_points_fibonacci(high: float, low: float, close: float) -> Dict[str, float]:
    p = (high + low + close) / 3.0
    rng = high - low
    return {
        "P": p,
        "R1": p + 0.382 * rng,
        "R2": p + 0.618 * rng,
        "R3": p + 1.000 * rng,
        "S1": p - 0.382 * rng,
        "S2": p - 0.618 * rng,
        "S3": p - 1.000 * rng,
    }


def pivot_points_camarilla(high: float, low: float, close: float) -> Dict[str, float]:
    rng = high - low
    return {
        "R4": close + rng * 1.1 / 2.0,
        "R3": close + rng * 1.1 / 4.0,
        "R2": close + rng * 1.1 / 6.0,
        "R1": close + rng * 1.1 / 12.0,
        "S1": close - rng * 1.1 / 12.0,
        "S2": close - rng * 1.1 / 6.0,
        "S3": close - rng * 1.1 / 4.0,
        "S4": close - rng * 1.1 / 2.0,
    }


def fibonacci_retracement(swing_high: float, swing_low: float, is_uptrend: bool = True) -> Dict[str, float]:
    diff = swing_high - swing_low
    if is_uptrend:
        return {
            "0.0%": swing_high,
            "23.6%": swing_high - 0.236 * diff,
            "38.2%": swing_high - 0.382 * diff,
            "50.0%": swing_high - 0.500 * diff,
            "61.8%": swing_high - 0.618 * diff,
            "78.6%": swing_high - 0.786 * diff,
            "100.0%": swing_low,
            "127.2%_ext": swing_high + 0.272 * diff,
            "161.8%_ext": swing_high + 0.618 * diff,
        }
    return {
        "0.0%": swing_low,
        "23.6%": swing_low + 0.236 * diff,
        "38.2%": swing_low + 0.382 * diff,
        "50.0%": swing_low + 0.500 * diff,
        "61.8%": swing_low + 0.618 * diff,
        "78.6%": swing_low + 0.786 * diff,
        "100.0%": swing_high,
        "127.2%_ext": swing_low - 0.272 * diff,
        "161.8%_ext": swing_low - 0.618 * diff,
    }


def find_swings(candles: List[Candle], left: int = 3, right: int = 3) -> Tuple[List[Tuple[int, float]], List[Tuple[int, float]]]:
    """Return (swing_highs, swing_lows) as lists of (index, price)."""
    n = len(candles)
    highs: List[Tuple[int, float]] = []
    lows: List[Tuple[int, float]] = []
    for i in range(left, n - right):
        h = candles[i].high
        l = candles[i].low
        if all(h >= candles[j].high for j in range(i - left, i + right + 1) if j != i):
            highs.append((i, h))
        if all(l <= candles[j].low for j in range(i - left, i + right + 1) if j != i):
            lows.append((i, l))
    return highs, lows


def detect_market_structure(candles: List[Candle], left: int = 3, right: int = 3) -> Dict[str, Any]:
    """Detect HH/HL/LH/LL structure, BOS (Break of Structure), and CHoCH (Change of Character)."""
    sh, sl = find_swings(candles, left, right)
    structure = "NEUTRAL"
    events: List[Dict[str, Any]] = []

    if len(sh) >= 2 and len(sl) >= 2:
        h1, h2 = sh[-2][1], sh[-1][1]
        l1, l2 = sl[-2][1], sl[-1][1]
        if h2 > h1 and l2 > l1:
            structure = "BULLISH (HH/HL)"
        elif h2 < h1 and l2 < l1:
            structure = "BEARISH (LH/LL)"
        else:
            structure = "TRANSITION / RANGING"

        last_close = candles[-1].close
        last_sh_idx, last_sh_price = sh[-1]
        last_sl_idx, last_sl_price = sl[-1]

        if last_close > last_sh_price:
            ev_type = "BOS_BULLISH" if "BULLISH" in structure else "CHOCH_BULLISH"
            events.append({"type": ev_type, "level": last_sh_price, "index": len(candles) - 1})
        elif last_close < last_sl_price:
            ev_type = "BOS_BEARISH" if "BEARISH" in structure else "CHOCH_BEARISH"
            events.append({"type": ev_type, "level": last_sl_price, "index": len(candles) - 1})

    return {
        "structure": structure,
        "swing_highs": sh[-5:],
        "swing_lows": sl[-5:],
        "events": events,
    }


def detect_fvg(candles: List[Candle], lookback: int = 30) -> List[Dict[str, Any]]:
    """Detect Fair Value Gaps (FVG / Imbalance) in recent candles."""
    fvgs: List[Dict[str, Any]] = []
    n = len(candles)
    start = max(2, n - lookback)
    for i in range(start, n):
        c1 = candles[i - 2]
        c3 = candles[i]
        # Bullish FVG: c1.high < c3.low
        if c1.high < c3.low:
            fvgs.append({
                "type": "BULLISH_FVG",
                "index": i - 1,
                "bottom": c1.high,
                "top": c3.low,
                "mitigated": any(candles[j].low <= c3.low for j in range(i + 1, n)),
            })
        # Bearish FVG: c1.low > c3.high
        elif c1.low > c3.high:
            fvgs.append({
                "type": "BEARISH_FVG",
                "index": i - 1,
                "bottom": c3.high,
                "top": c1.low,
                "mitigated": any(candles[j].high >= c3.high for j in range(i + 1, n)),
            })
    return fvgs[-6:]


def detect_order_blocks(candles: List[Candle], lookback: int = 40) -> List[Dict[str, Any]]:
    """Detect Bullish/Bearish Order Blocks (last opposing candle before impulsive displacement)."""
    obs: List[Dict[str, Any]] = []
    n = len(candles)
    if n < 5:
        return obs
    avg_body = sum(c.body for c in candles[max(0, n - 50) :]) / min(n, 50)
    start = max(1, n - lookback)
    for i in range(start, n - 1):
        cur = candles[i]
        nxt = candles[i + 1]
        if cur.is_bearish and nxt.is_bullish and nxt.body > 1.8 * avg_body and nxt.close > cur.high:
            obs.append({
                "type": "BULLISH_OB",
                "index": i,
                "low": cur.low,
                "high": cur.high,
            })
        elif cur.is_bullish and nxt.is_bearish and nxt.body > 1.8 * avg_body and nxt.close < cur.low:
            obs.append({
                "type": "BEARISH_OB",
                "index": i,
                "low": cur.low,
                "high": cur.high,
            })
    return obs[-4:]


def detect_liquidity_sweeps(candles: List[Candle], lookback: int = 25) -> List[Dict[str, Any]]:
    """Detect Stop Hunt / Liquidity Sweep: wick pierces prior swing high/low then closes back inside."""
    sweeps: List[Dict[str, Any]] = []
    n = len(candles)
    if n < lookback + 5:
        return sweeps
    sh, sl = find_swings(candles[:-1], left=3, right=3)
    recent_start = max(0, n - 8)
    for i in range(recent_start, n):
        c = candles[i]
        for idx, level in sh[-4:]:
            if idx < i and c.high > level and c.close < level:
                sweeps.append({
                    "type": "BEARISH_LIQUIDITY_SWEEP",
                    "index": i,
                    "level": level,
                    "wick_high": c.high,
                })
                break
        for idx, level in sl[-4:]:
            if idx < i and c.low < level and c.close > level:
                sweeps.append({
                    "type": "BULLISH_LIQUIDITY_SWEEP",
                    "index": i,
                    "level": level,
                    "wick_low": c.low,
                })
                break
    return sweeps[-4:]

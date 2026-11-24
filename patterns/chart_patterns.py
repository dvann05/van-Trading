"""Geometric Chart Pattern Recognition (Double Top/Bottom, H&S, Triangles, Wedges, Flags, Channels)."""

from typing import List, Tuple
from models import Candle, PatternMatch
from indicators.structure import find_swings


def _slope(points: List[Tuple[int, float]]) -> float:
    if len(points) < 2:
        return 0.0
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    xm = sum(xs) / len(xs)
    ym = sum(ys) / len(ys)
    denom = sum((x - xm) ** 2 for x in xs)
    if denom == 0:
        return 0.0
    return sum((x - xm) * (y - ym) for x, y in zip(xs, ys)) / denom


def detect_chart_patterns(candles: List[Candle], lookback: int = 80) -> List[PatternMatch]:
    """Detect classical chart patterns from recent swing highs and swing lows."""
    matches: List[PatternMatch] = []
    n = len(candles)
    if n < 25:
        return matches

    window = candles[max(0, n - lookback) :]
    offset = max(0, n - lookback)
    sh_raw, sl_raw = find_swings(window, left=3, right=3)
    sh = [(i + offset, p) for i, p in sh_raw]
    sl = [(i + offset, p) for i, p in sl_raw]

    last_price = candles[-1].close
    price_scale = max(last_price, 1e-9)

    # 1. Double Top (M Pattern)
    if len(sh) >= 2 and len(sl) >= 1:
        (i1, h1), (i2, h2) = sh[-2], sh[-1]
        between_lows = [p for idx, p in sl if i1 < idx < i2]
        if between_lows and abs(h1 - h2) / max(h1, h2) <= 0.018 and (i2 - i1) >= 5:
            neckline = min(between_lows)
            broken = last_price < neckline
            matches.append(PatternMatch(
                name="Double Top (M Pattern)",
                category="chart_pattern",
                bias="BEARISH",
                confidence=0.84 if broken else 0.68,
                index=i2,
                description=f"Dua puncak sejajar di ~{(h1 + h2) / 2:.4f} dengan neckline {neckline:.4f}.",
                habit_rule="Kebiasaan market: buyer gagal menembus resistance dua kali; jika neckline ditembus, target turun umumnya setinggi jarak puncak ke neckline.",
            ))

    # 2. Double Bottom (W Pattern)
    if len(sl) >= 2 and len(sh) >= 1:
        (i1, l1), (i2, l2) = sl[-2], sl[-1]
        between_highs = [p for idx, p in sh if i1 < idx < i2]
        if between_highs and abs(l1 - l2) / max(l1, l2) <= 0.018 and (i2 - i1) >= 5:
            neckline = max(between_highs)
            broken = last_price > neckline
            matches.append(PatternMatch(
                name="Double Bottom (W Pattern)",
                category="chart_pattern",
                bias="BULLISH",
                confidence=0.84 if broken else 0.68,
                index=i2,
                description=f"Dua lembah sejajar di ~{(l1 + l2) / 2:.4f} dengan neckline {neckline:.4f}.",
                habit_rule="Kebiasaan market: akumulasi kuat di support; breakout neckline sering diikuti retest lalu rally setinggi pola.",
            ))

    # 3. Head & Shoulders / Inverse Head & Shoulders
    if len(sh) >= 3:
        (i1, ls), (i2, head), (i3, rs) = sh[-3], sh[-2], sh[-1]
        if head > ls and head > rs and abs(ls - rs) / max(ls, rs) <= 0.03:
            matches.append(PatternMatch(
                name="Head and Shoulders",
                category="chart_pattern",
                bias="BEARISH",
                confidence=0.78,
                index=i3,
                description=f"Left Shoulder {ls:.4f}, Head {head:.4f}, Right Shoulder {rs:.4f}.",
                habit_rule="Kebiasaan market: pola distribusi mayor; kegagalan bahu kanan mencetak high baru menandakan kelelahan tren naik.",
            ))

    if len(sl) >= 3:
        (i1, ls), (i2, head), (i3, rs) = sl[-3], sl[-2], sl[-1]
        if head < ls and head < rs and abs(ls - rs) / max(ls, rs) <= 0.03:
            matches.append(PatternMatch(
                name="Inverse Head and Shoulders",
                category="chart_pattern",
                bias="BULLISH",
                confidence=0.78,
                index=i3,
                description=f"Left Shoulder {ls:.4f}, Head {head:.4f}, Right Shoulder {rs:.4f}.",
                habit_rule="Kebiasaan market: pola akumulasi pembalikan bullish; breakout neckline biasanya memicu ekspansi tren naik.",
            ))

    # 4. Triangles, Wedges, and Channels (from last 3 swing highs & 3 swing lows)
    if len(sh) >= 3 and len(sl) >= 3:
        top_slope = _slope(sh[-3:]) / price_scale
        bot_slope = _slope(sl[-3:]) / price_scale
        flat_thresh = 0.0004

        if abs(top_slope) <= flat_thresh and bot_slope > flat_thresh:
            matches.append(PatternMatch(
                name="Ascending Triangle",
                category="chart_pattern",
                bias="BULLISH",
                confidence=0.75,
                index=n - 1,
                description="Resistance datar sementara swing low terus naik (higher lows).",
                habit_rule="Kebiasaan market: buyer semakin agresif menyerap supply di resistance; cenderung breakout ke atas.",
            ))
        elif top_slope < -flat_thresh and abs(bot_slope) <= flat_thresh:
            matches.append(PatternMatch(
                name="Descending Triangle",
                category="chart_pattern",
                bias="BEARISH",
                confidence=0.75,
                index=n - 1,
                description="Support datar sementara swing high terus turun (lower highs).",
                habit_rule="Kebiasaan market: seller menekan support berulang kali hingga likuiditas habis; cenderung breakdown ke bawah.",
            ))
        elif top_slope < -flat_thresh and bot_slope > flat_thresh:
            matches.append(PatternMatch(
                name="Symmetrical Triangle",
                category="chart_pattern",
                bias="NEUTRAL",
                confidence=0.68,
                index=n - 1,
                description="Kompresi harga membentuk lower highs dan higher lows yang menyempit.",
                habit_rule="Kebiasaan market: energi terkumpul menjelang ledakan volatilitas; ikuti arah breakout yang disertai lonjakan volume.",
            ))
        elif top_slope > flat_thresh and bot_slope > flat_thresh:
            if bot_slope > top_slope * 1.25:
                matches.append(PatternMatch(
                    name="Rising Wedge",
                    category="chart_pattern",
                    bias="BEARISH",
                    confidence=0.72,
                    index=n - 1,
                    description="Harga naik dalam saluran yang menyempit ke atas.",
                    habit_rule="Kebiasaan market: momentum kenaikan melemah meski harga naik; sering berakhir dengan breakdown tajam ke bawah.",
                ))
            else:
                matches.append(PatternMatch(
                    name="Ascending Channel",
                    category="chart_pattern",
                    bias="BULLISH",
                    confidence=0.70,
                    index=n - 1,
                    description="Tren naik rapi di dalam kanal paralel naik.",
                    habit_rule="Kebiasaan market: buy on dip di lower channel, ambil profit parsial di upper channel selama kanal tidak jebol.",
                ))
        elif top_slope < -flat_thresh and bot_slope < -flat_thresh:
            if top_slope < bot_slope * 1.25:
                matches.append(PatternMatch(
                    name="Falling Wedge",
                    category="chart_pattern",
                    bias="BULLISH",
                    confidence=0.72,
                    index=n - 1,
                    description="Harga turun dalam saluran yang menyempit ke bawah.",
                    habit_rule="Kebiasaan market: tekanan jual menyusut; probabilitas breakout bullish ke atas sangat tinggi.",
                ))
            else:
                matches.append(PatternMatch(
                    name="Descending Channel",
                    category="chart_pattern",
                    bias="BEARISH",
                    confidence=0.70,
                    index=n - 1,
                    description="Tren turun rapi di dalam kanal paralel turun.",
                    habit_rule="Kebiasaan market: sell on rally di upper channel selama belum ada breakout valid ke atas.",
                ))

    # 5. Bull Flag / Bear Flag (sharp impulse followed by tight counter-trend drift)
    if n >= 20:
        impulse_move = (candles[-8].close - candles[-18].close) / max(candles[-18].close, 1e-9)
        flag_move = (candles[-1].close - candles[-8].close) / max(candles[-8].close, 1e-9)
        if impulse_move >= 0.04 and -0.025 <= flag_move <= 0.005:
            matches.append(PatternMatch(
                name="Bull Flag",
                category="chart_pattern",
                bias="BULLISH",
                confidence=0.74,
                index=n - 1,
                description=f"Impuls naik +{impulse_move * 100:.1f}% diikuti konsolidasi korektif tipis {flag_move * 100:.1f}%.",
                habit_rule="Kebiasaan market: pola continuation klasik; profit-taking sehat sebelum leg naik kedua sepanjang tiang (flagpole).",
            ))
        elif impulse_move <= -0.04 and -0.005 <= flag_move <= 0.025:
            matches.append(PatternMatch(
                name="Bear Flag",
                category="chart_pattern",
                bias="BEARISH",
                confidence=0.74,
                index=n - 1,
                description=f"Impuls turun {impulse_move * 100:.1f}% diikuti rebound lemah +{flag_move * 100:.1f}%.",
                habit_rule="Kebiasaan market: dead-cat bounce sementara sebelum gelombang penurunan berikutnya.",
            ))

    return matches

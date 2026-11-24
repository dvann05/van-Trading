"""Market Behavioral Patterns & Indicator Habits ('Kebiasaan Pola Market')."""

from typing import Dict, List, Optional, Tuple
from models import Candle, PatternMatch
from indicators.structure import (
    detect_fvg,
    detect_liquidity_sweeps,
    detect_market_structure,
    detect_order_blocks,
    find_swings,
)


def _detect_divergence(
    candles: List[Candle],
    osc: List[Optional[float]],
    osc_name: str,
    lookback: int = 50,
) -> List[PatternMatch]:
    """Detect Regular & Hidden Bullish/Bearish Divergences between Price and an Oscillator."""
    matches: List[PatternMatch] = []
    n = len(candles)
    if n < 20:
        return matches

    start = max(0, n - lookback)
    sh_raw, sl_raw = find_swings(candles[start:], left=3, right=3)
    sh = [(i + start, p) for i, p in sh_raw]
    sl = [(i + start, p) for i, p in sl_raw]

    # Bullish divergences on Swing Lows
    if len(sl) >= 2:
        (i1, p1), (i2, p2) = sl[-2], sl[-1]
        o1, o2 = osc[i1], osc[i2]
        if o1 is not None and o2 is not None and (n - 1 - i2) <= 15:
            if p2 < p1 and o2 > o1:
                matches.append(PatternMatch(
                    name=f"Regular Bullish Divergence ({osc_name})",
                    category="divergence",
                    bias="BULLISH",
                    confidence=0.82,
                    index=i2,
                    description=f"Harga mencetak Lower Low ({p1:.4f} -> {p2:.4f}) tetapi {osc_name} mencetak Higher Low ({o1:.2f} -> {o2:.2f}).",
                    habit_rule="Kebiasaan market: tenaga jual melemah di balik penurunan harga; sangat sering memicu reversal naik tajam.",
                ))
            elif p2 > p1 and o2 < o1:
                matches.append(PatternMatch(
                    name=f"Hidden Bullish Divergence ({osc_name})",
                    category="divergence",
                    bias="BULLISH",
                    confidence=0.76,
                    index=i2,
                    description=f"Harga mencetak Higher Low ({p1:.4f} -> {p2:.4f}) sementara {osc_name} mencetak Lower Low ({o1:.2f} -> {o2:.2f}).",
                    habit_rule="Kebiasaan market: reset momentum di tengah uptrend; sinyal continuation naik yang kuat.",
                ))

    # Bearish divergences on Swing Highs
    if len(sh) >= 2:
        (i1, p1), (i2, p2) = sh[-2], sh[-1]
        o1, o2 = osc[i1], osc[i2]
        if o1 is not None and o2 is not None and (n - 1 - i2) <= 15:
            if p2 > p1 and o2 < o1:
                matches.append(PatternMatch(
                    name=f"Regular Bearish Divergence ({osc_name})",
                    category="divergence",
                    bias="BEARISH",
                    confidence=0.82,
                    index=i2,
                    description=f"Harga mencetak Higher High ({p1:.4f} -> {p2:.4f}) tetapi {osc_name} mencetak Lower High ({o1:.2f} -> {o2:.2f}).",
                    habit_rule="Kebiasaan market: momentum beli mulai bocor di puncak; peringatan keras potensi koreksi atau reversal turun.",
                ))
            elif p2 < p1 and o2 > o1:
                matches.append(PatternMatch(
                    name=f"Hidden Bearish Divergence ({osc_name})",
                    category="divergence",
                    bias="BEARISH",
                    confidence=0.76,
                    index=i2,
                    description=f"Harga mencetak Lower High ({p1:.4f} -> {p2:.4f}) sementara {osc_name} mencetak Higher High ({o1:.2f} -> {o2:.2f}).",
                    habit_rule="Kebiasaan market: reset momentum di tengah downtrend; sinyal continuation turun.",
                ))

    return matches


def detect_wyckoff_phase(
    candles: List[Candle],
    sma50: List[Optional[float]],
    adx_vals: List[Optional[float]],
    bb_bw: List[Optional[float]],
) -> str:
    """Classify current market cycle into Wyckoff phases."""
    n = len(candles)
    if n < 30:
        return "UNKNOWN"
    close = candles[-1].close
    ma = sma50[-1]
    adx_v = adx_vals[-1] or 20.0
    bw = bb_bw[-1] or 5.0
    past_close = candles[-20].close
    slope_pct = (close - past_close) / max(past_close, 1e-9) * 100.0

    if adx_v >= 23.0:
        if ma is not None and close > ma and slope_pct > 1.0:
            return "MARKUP (Fase Tren Naik / Ekspansi Bullish)"
        if ma is not None and close < ma and slope_pct < -1.0:
            return "MARKDOWN (Fase Tren Turun / Ekspansi Bearish)"

    # Low ADX or sideways: distinguish Accumulation vs Distribution using recent price location
    hi_50 = max(c.high for c in candles[-min(n, 50) :])
    lo_50 = min(c.low for c in candles[-min(n, 50) :])
    pos = (close - lo_50) / max(hi_50 - lo_50, 1e-9)
    if pos <= 0.45:
        return "ACCUMULATION (Sideways di Area Bawah / Smart Money Mengumpulkan)"
    if pos >= 0.55:
        return "DISTRIBUTION (Sideways di Area Atas / Smart Money Melepas)"
    return "RE-ACCUMULATION / CONSOLIDATION (Jeda Tren)"


def detect_market_habits(
    candles: List[Candle],
    ctx: Dict[str, object],
) -> Tuple[List[PatternMatch], str]:
    """Detect all indicator & behavioral market habits ('kebiasaan pola market')."""
    matches: List[PatternMatch] = []
    n = len(candles)
    if n < 25:
        return matches, "UNKNOWN"

    ema9: List[Optional[float]] = ctx["ema9"]  # type: ignore[assignment]
    ema21: List[Optional[float]] = ctx["ema21"]  # type: ignore[assignment]
    ema50: List[Optional[float]] = ctx["ema50"]  # type: ignore[assignment]
    sma50: List[Optional[float]] = ctx["sma50"]  # type: ignore[assignment]
    sma200: List[Optional[float]] = ctx["sma200"]  # type: ignore[assignment]
    rsi_vals: List[Optional[float]] = ctx["rsi"]  # type: ignore[assignment]
    macd_hist: List[Optional[float]] = ctx["macd_hist"]  # type: ignore[assignment]
    obv_vals: List[float] = ctx["obv"]  # type: ignore[assignment]
    bb: Dict[str, List[Optional[float]]] = ctx["bb"]  # type: ignore[assignment]
    squeeze: Dict[str, List[Optional[float]]] = ctx["squeeze"]  # type: ignore[assignment]
    adx_data: Dict[str, List[Optional[float]]] = ctx["adx"]  # type: ignore[assignment]
    dc: Dict[str, List[Optional[float]]] = ctx["donchian"]  # type: ignore[assignment]

    # 1. Divergences (RSI, MACD Histogram, OBV)
    matches.extend(_detect_divergence(candles, rsi_vals, "RSI"))
    matches.extend(_detect_divergence(candles, macd_hist, "MACD"))
    matches.extend(_detect_divergence(candles, [float(v) for v in obv_vals], "OBV"))

    # 2. Moving Average Crossovers & Ribbon Habits
    if sma50[-1] is not None and sma200[-1] is not None:
        for k in range(max(1, n - 5), n):
            if sma50[k - 1] is not None and sma200[k - 1] is not None and sma50[k] is not None and sma200[k] is not None:
                if sma50[k - 1] <= sma200[k - 1] and sma50[k] > sma200[k]:  # type: ignore[operator]
                    matches.append(PatternMatch(
                        name="Golden Cross (SMA 50/200)",
                        category="market_habit",
                        bias="BULLISH",
                        confidence=0.86,
                        index=k,
                        description="SMA 50 memotong ke atas SMA 200.",
                        habit_rule="Kebiasaan market: sinyal tren bull jangka menengah-panjang yang dipantau institusi; sering diikuti inflow berkelanjutan.",
                    ))
                elif sma50[k - 1] >= sma200[k - 1] and sma50[k] < sma200[k]:  # type: ignore[operator]
                    matches.append(PatternMatch(
                        name="Death Cross (SMA 50/200)",
                        category="market_habit",
                        bias="BEARISH",
                        confidence=0.86,
                        index=k,
                        description="SMA 50 memotong ke bawah SMA 200.",
                        habit_rule="Kebiasaan market: sinyal tren bear mayor; reli pendek cenderung dijual (sell on rally).",
                    ))

    if ema9[-1] is not None and ema21[-1] is not None and ema9[-2] is not None and ema21[-2] is not None:
        if ema9[-2] <= ema21[-2] and ema9[-1] > ema21[-1]:  # type: ignore[operator]
            matches.append(PatternMatch(
                name="EMA 9/21 Bullish Cross",
                category="market_habit",
                bias="BULLISH",
                confidence=0.74,
                index=n - 1,
                description="EMA 9 baru memotong ke atas EMA 21.",
                habit_rule="Kebiasaan market: pemicu momentum swing bullish jangka pendek; area EMA 9-21 menjadi dynamic support.",
            ))
        elif ema9[-2] >= ema21[-2] and ema9[-1] < ema21[-1]:  # type: ignore[operator]
            matches.append(PatternMatch(
                name="EMA 9/21 Bearish Cross",
                category="market_habit",
                bias="BEARISH",
                confidence=0.74,
                index=n - 1,
                description="EMA 9 baru memotong ke bawah EMA 21.",
                habit_rule="Kebiasaan market: pergeseran momentum jangka pendek ke bearish; area EMA 9-21 berubah jadi dynamic resistance.",
            ))

    if ema9[-1] is not None and ema21[-1] is not None and ema50[-1] is not None:
        if candles[-1].close > ema9[-1] > ema21[-1] > ema50[-1]:  # type: ignore[operator]
            matches.append(PatternMatch(
                name="Bullish EMA Ribbon Fan (Close > 9 > 21 > 50)",
                category="market_habit",
                bias="BULLISH",
                confidence=0.80,
                index=n - 1,
                description="Susunan EMA sejajar rapi menanjak seperti kipas terbuka.",
                habit_rule="Kebiasaan market: tren naik sangat sehat; pullback ke EMA 21 secara historis menjadi area entry terbaik.",
            ))
        elif candles[-1].close < ema9[-1] < ema21[-1] < ema50[-1]:  # type: ignore[operator]
            matches.append(PatternMatch(
                name="Bearish EMA Ribbon Fan (Close < 9 < 21 < 50)",
                category="market_habit",
                bias="BEARISH",
                confidence=0.80,
                index=n - 1,
                description="Susunan EMA sejajar rapi menurun.",
                habit_rule="Kebiasaan market: tren turun dominan; hindari menangkap pisau jatuh, tunggu retest EMA 21 untuk short.",
            ))

    # 3. Volatility Squeeze & Expansion Habit (TTM Squeeze + BB Bandwidth)
    sq_on = squeeze["squeeze_on"]
    sq_mom = squeeze["momentum"]
    if sq_on[-1] == 1.0:
        matches.append(PatternMatch(
            name="TTM Volatility Squeeze Active",
            category="market_habit",
            bias="NEUTRAL",
            confidence=0.78,
            index=n - 1,
            description="Bollinger Bands masuk ke dalam Keltner Channels (kompresi volatilitas ekstrem).",
            habit_rule="Kebiasaan market: 'calm before the storm' — volatilitas rendah selalu diikuti ekspansi besar; bersiap breakout.",
        ))
    elif n >= 3 and sq_on[-2] == 1.0 and sq_on[-1] == 0.0:
        mom_v = sq_mom[-1] or 0.0
        bias = "BULLISH" if mom_v >= 0 else "BEARISH"
        matches.append(PatternMatch(
            name=f"TTM Squeeze Firing ({bias})",
            category="market_habit",
            bias=bias,
            confidence=0.85,
            index=n - 1,
            description=f"Squeeze baru saja pecah (fired) dengan momentum {'positif' if bias == 'BULLISH' else 'negatif'}.",
            habit_rule="Kebiasaan market: fase awal ekspansi tren baru; biasanya bergerak cepat 1.5x-3x ATR ke arah momentum.",
        ))

    # 4. Bollinger Band Walk vs Mean Reversion Stretch
    pct_b = bb["percent_b"][-1]
    adx_v = adx_data["adx"][-1] or 20.0
    if pct_b is not None:
        if pct_b > 1.0 and adx_v < 22:
            matches.append(PatternMatch(
                name="Bollinger Upper Overextension (Mean Reversion)",
                category="market_habit",
                bias="BEARISH",
                confidence=0.70,
                index=n - 1,
                description=f"Harga menembus Upper Band (%B={pct_b:.2f}) saat ADX lemah ({adx_v:.1f}).",
                habit_rule="Kebiasaan market: di market sideways (ADX < 22), harga yang keluar band cenderung cepat ditarik kembali ke Middle Band (SMA 20).",
            ))
        elif pct_b < 0.0 and adx_v < 22:
            matches.append(PatternMatch(
                name="Bollinger Lower Overextension (Mean Reversion)",
                category="market_habit",
                bias="BULLISH",
                confidence=0.70,
                index=n - 1,
                description=f"Harga menembus Lower Band (%B={pct_b:.2f}) saat ADX lemah ({adx_v:.1f}).",
                habit_rule="Kebiasaan market: di market ranging, oversold ekstrem di luar Lower Band sering memantul kembali ke rata-rata.",
            ))
        elif pct_b >= 0.85 and adx_v >= 28:
            matches.append(PatternMatch(
                name="Bollinger Upper Band Walk",
                category="market_habit",
                bias="BULLISH",
                confidence=0.75,
                index=n - 1,
                description=f"Harga menempel di Upper Band (%B={pct_b:.2f}) disertai ADX kuat ({adx_v:.1f}).",
                habit_rule="Kebiasaan market: bukan sinyal jual! Pada tren kuat, harga biasa 'berjalan' di sepanjang Upper Band.",
            ))
        elif pct_b <= 0.15 and adx_v >= 28:
            matches.append(PatternMatch(
                name="Bollinger Lower Band Walk",
                category="market_habit",
                bias="BEARISH",
                confidence=0.75,
                index=n - 1,
                description=f"Harga menempel di Lower Band (%B={pct_b:.2f}) disertai ADX kuat ({adx_v:.1f}).",
                habit_rule="Kebiasaan market: tekanan jual tren kuat; harga bisa terus meluncur di sepanjang Lower Band.",
            ))

    # 5. Donchian Breakout Habit (Turtle Trading Rule)
    if dc["upper"][-2] is not None and dc["lower"][-2] is not None:
        if candles[-1].close > dc["upper"][-2]:  # type: ignore[operator]
            matches.append(PatternMatch(
                name="Donchian 20-Bar Bullish Breakout",
                category="market_habit",
                bias="BULLISH",
                confidence=0.78,
                index=n - 1,
                description="Close menembus tertinggi 20 candle terakhir (Turtle Breakout).",
                habit_rule="Kebiasaan market: breakout harga tertinggi baru sering memicu gelombang beli trend-follower.",
            ))
        elif candles[-1].close < dc["lower"][-2]:  # type: ignore[operator]
            matches.append(PatternMatch(
                name="Donchian 20-Bar Bearish Breakdown",
                category="market_habit",
                bias="BEARISH",
                confidence=0.78,
                index=n - 1,
                description="Close menembus terendah 20 candle terakhir.",
                habit_rule="Kebiasaan market: breakdown harga terendah baru sering memicu stop-loss beruntun ke bawah.",
            ))

    # 6. Volume Climax & Volume Dry-Up Habits
    recent_vols = [c.volume for c in candles[-21:-1]]
    avg_vol = sum(recent_vols) / max(len(recent_vols), 1)
    last_vol = candles[-1].volume
    if avg_vol > 0:
        if last_vol >= 2.2 * avg_vol:
            bias = "BULLISH" if candles[-1].is_bullish else "BEARISH"
            matches.append(PatternMatch(
                name=f"Volume Climax / Spike ({last_vol / avg_vol:.1f}x avg)",
                category="market_habit",
                bias=bias,
                confidence=0.76,
                index=n - 1,
                description=f"Lonjakan volume ekstrem {last_vol / avg_vol:.1f}x rata-rata 20 bar.",
                habit_rule="Kebiasaan market: jika terjadi saat breakout = konfirmasi institusi; jika terjadi setelah tren panjang = potensi klimaks/exhaustion.",
            ))
        elif last_vol <= 0.45 * avg_vol:
            matches.append(PatternMatch(
                name=f"Volume Dry-Up ({last_vol / avg_vol:.2f}x avg)",
                category="market_habit",
                bias="NEUTRAL",
                confidence=0.62,
                index=n - 1,
                description="Volume menyusut tajam di bawah setengah rata-rata.",
                habit_rule="Kebiasaan market: pelaku pasar menunggu katalis; sering muncul tepat sebelum breakout besar atau saat pullback sehat.",
            ))

    # 7. Smart Money Concepts (SMC) Habits: BOS / CHoCH, Liquidity Sweep, FVG, Order Block
    ms = detect_market_structure(candles)
    for ev in ms["events"]:
        is_bull = "BULLISH" in ev["type"]
        is_choch = "CHOCH" in ev["type"]
        matches.append(PatternMatch(
            name=ev["type"].replace("_", " "),
            category="smc",
            bias="BULLISH" if is_bull else "BEARISH",
            confidence=0.82 if is_choch else 0.78,
            index=ev["index"],
            description=f"Harga menembus level struktur {ev['level']:.4f} ({ev['type']}).",
            habit_rule=(
                "Kebiasaan SMC: Change of Character menandakan potensi pembalikan tren; tunggu retracement ke Order Block/FVG."
                if is_choch
                else "Kebiasaan SMC: Break of Structure mengonfirmasi kelanjutan tren dominan."
            ),
        ))

    for sw in detect_liquidity_sweeps(candles):
        is_bull = sw["type"] == "BULLISH_LIQUIDITY_SWEEP"
        matches.append(PatternMatch(
            name="Bullish Liquidity Sweep (Stop Hunt)" if is_bull else "Bearish Liquidity Sweep (Stop Hunt)",
            category="smc",
            bias="BULLISH" if is_bull else "BEARISH",
            confidence=0.80,
            index=sw["index"],
            description=f"Ekor menyapu likuiditas di level {sw['level']:.4f} lalu close kembali masuk range.",
            habit_rule="Kebiasaan market: smart money memicu stop-loss retail di luar swing lalu membalikkan arah dengan cepat.",
        ))

    unmitigated_fvgs = [f for f in detect_fvg(candles) if not f["mitigated"]]
    if unmitigated_fvgs:
        fvg = unmitigated_fvgs[-1]
        is_bull = fvg["type"] == "BULLISH_FVG"
        matches.append(PatternMatch(
            name="Unmitigated Bullish FVG" if is_bull else "Unmitigated Bearish FVG",
            category="smc",
            bias="BULLISH" if is_bull else "BEARISH",
            confidence=0.68,
            index=fvg["index"],
            description=f"Zona imbalance belum terisi di {fvg['bottom']:.4f} - {fvg['top']:.4f}.",
            habit_rule="Kebiasaan SMC: Fair Value Gap bekerja seperti magnet; harga sering retest mengisi gap sebelum melanjutkan arah tren.",
        ))

    obs = detect_order_blocks(candles)
    if obs:
        ob = obs[-1]
        is_bull = ob["type"] == "BULLISH_OB"
        matches.append(PatternMatch(
            name="Bullish Order Block" if is_bull else "Bearish Order Block",
            category="smc",
            bias="BULLISH" if is_bull else "BEARISH",
            confidence=0.70,
            index=ob["index"],
            description=f"Zona institusional di {ob['low']:.4f} - {ob['high']:.4f}.",
            habit_rule="Kebiasaan SMC: area akumulasi/distribusi order besar; reaksi pantulan kuat sering muncul saat harga menyentuh zona ini.",
        ))

    wyckoff = detect_wyckoff_phase(candles, sma50, adx_data["adx"], bb["bandwidth"])
    return matches, wyckoff

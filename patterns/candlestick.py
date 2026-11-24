"""Comprehensive Candlestick Pattern Recognition with Market Habit Rules."""

from typing import List
from models import Candle, PatternMatch


def _local_trend(candles: List[Candle], idx: int, window: int = 5) -> str:
    start = max(0, idx - window)
    if idx <= start:
        return "NEUTRAL"
    diff = candles[idx - 1].close - candles[start].close
    if diff > 0:
        return "UP"
    if diff < 0:
        return "DOWN"
    return "NEUTRAL"


def detect_candlestick_patterns(candles: List[Candle], scan_last: int = 5) -> List[PatternMatch]:
    """Scan recent candles for 20+ classic single, double, and triple candlestick patterns."""
    matches: List[PatternMatch] = []
    n = len(candles)
    if n < 3:
        return matches

    avg_body = sum(c.body for c in candles[max(0, n - 20) :]) / min(n, 20)
    avg_range = sum(c.range for c in candles[max(0, n - 20) :]) / min(n, 20)
    start = max(2, n - scan_last)

    for i in range(start, n):
        c = candles[i]
        p = candles[i - 1]
        p2 = candles[i - 2]
        trend = _local_trend(candles, i)
        rng = max(c.range, 1e-12)
        body_ratio = c.body / rng

        # --- SINGLE CANDLE PATTERNS ---
        # 1. Doji variants
        if body_ratio <= 0.10 and c.range > 0:
            if c.lower_wick >= 0.65 * rng and c.upper_wick <= 0.15 * rng:
                matches.append(PatternMatch(
                    name="Dragonfly Doji",
                    category="candlestick",
                    bias="BULLISH",
                    confidence=0.72 if trend == "DOWN" else 0.55,
                    index=i,
                    description="Ekor bawah panjang dengan body sangat tipis di puncak.",
                    habit_rule="Kebiasaan market: rejection kuat dari buyer di area support; sering memicu reversal naik setelah downtrend.",
                ))
            elif c.upper_wick >= 0.65 * rng and c.lower_wick <= 0.15 * rng:
                matches.append(PatternMatch(
                    name="Gravestone Doji",
                    category="candlestick",
                    bias="BEARISH",
                    confidence=0.72 if trend == "UP" else 0.55,
                    index=i,
                    description="Ekor atas panjang dengan body tipis di dasar candle.",
                    habit_rule="Kebiasaan market: buyer gagal mempertahankan kenaikan; sinyal distribusi/pembalikan turun di resistance.",
                ))
            elif c.upper_wick >= 0.35 * rng and c.lower_wick >= 0.35 * rng:
                matches.append(PatternMatch(
                    name="Long-Legged Doji",
                    category="candlestick",
                    bias="NEUTRAL",
                    confidence=0.60,
                    index=i,
                    description="Indecision ekstrem dengan volatilitas atas-bawah seimbang.",
                    habit_rule="Kebiasaan market: pertarungan buyer vs seller memuncak; tunggu breakout high/low candle ini sebagai arah.",
                ))
            else:
                matches.append(PatternMatch(
                    name="Standard Doji",
                    category="candlestick",
                    bias="NEUTRAL",
                    confidence=0.50,
                    index=i,
                    description="Harga open dan close hampir sama (indecision).",
                    habit_rule="Kebiasaan market: jeda momentum; sering mendahului pergantian arah jika muncul di area S/R.",
                ))

        # 2. Hammer / Hanging Man
        if 0.10 < body_ratio <= 0.35 and c.lower_wick >= 2.0 * c.body and c.upper_wick <= 0.5 * c.body:
            if trend == "DOWN":
                matches.append(PatternMatch(
                    name="Hammer",
                    category="candlestick",
                    bias="BULLISH",
                    confidence=0.76,
                    index=i,
                    description="Body kecil di atas dengan ekor bawah >= 2x body setelah penurunan.",
                    habit_rule="Kebiasaan market: seller menekan harga lalu diserap habis oleh buyer; reversal bullish tinggi bila dikonfirmasi candle hijau berikutnya.",
                ))
            elif trend == "UP":
                matches.append(PatternMatch(
                    name="Hanging Man",
                    category="candlestick",
                    bias="BEARISH",
                    confidence=0.65,
                    index=i,
                    description="Bentuk palu muncul di puncak uptrend.",
                    habit_rule="Kebiasaan market: peringatan awal tekanan jual mulai masuk; valid bearish jika candle berikutnya close di bawah body.",
                ))

        # 3. Shooting Star / Inverted Hammer
        if 0.10 < body_ratio <= 0.35 and c.upper_wick >= 2.0 * c.body and c.lower_wick <= 0.5 * c.body:
            if trend == "UP":
                matches.append(PatternMatch(
                    name="Shooting Star",
                    category="candlestick",
                    bias="BEARISH",
                    confidence=0.76,
                    index=i,
                    description="Body kecil di bawah dengan ekor atas panjang di puncak uptrend.",
                    habit_rule="Kebiasaan market: fake push naik langsung ditolak seller; probabilitas koreksi/reversal turun tinggi.",
                ))
            elif trend == "DOWN":
                matches.append(PatternMatch(
                    name="Inverted Hammer",
                    category="candlestick",
                    bias="BULLISH",
                    confidence=0.65,
                    index=i,
                    description="Ekor atas panjang di dasar downtrend.",
                    habit_rule="Kebiasaan market: buyer mulai menguji kekuatan naik; konfirmasi bullish bila candle selanjutnya menembus high-nya.",
                ))

        # 4. Marubozu (Strong Momentum Candle)
        if body_ratio >= 0.85 and c.body > 1.3 * avg_body:
            if c.is_bullish:
                matches.append(PatternMatch(
                    name="Bullish Marubozu",
                    category="candlestick",
                    bias="BULLISH",
                    confidence=0.78,
                    index=i,
                    description="Candle hijau penuh nyaris tanpa ekor, dominasi buyer total.",
                    habit_rule="Kebiasaan market: momentum lanjutan kuat (continuation); biasanya diikuti pullback dangkal ke 50% body lalu lanjut naik.",
                ))
            else:
                matches.append(PatternMatch(
                    name="Bearish Marubozu",
                    category="candlestick",
                    bias="BEARISH",
                    confidence=0.78,
                    index=i,
                    description="Candle merah penuh nyaris tanpa ekor, dominasi seller total.",
                    habit_rule="Kebiasaan market: tekanan jual agresif; sering menjadi awal impuls turun atau breakdown support.",
                ))

        # 5. Spinning Top
        if 0.10 < body_ratio <= 0.30 and c.upper_wick >= c.body and c.lower_wick >= c.body:
            matches.append(PatternMatch(
                name="Spinning Top",
                category="candlestick",
                bias="NEUTRAL",
                confidence=0.45,
                index=i,
                description="Body kecil di tengah dengan ekor atas dan bawah seimbang.",
                habit_rule="Kebiasaan market: tenaga tren melemah (exhaustion); waspada konsolidasi atau pembalikan.",
            ))

        # --- DOUBLE CANDLE PATTERNS ---
        # 6. Engulfing
        if p.is_bearish and c.is_bullish and c.open <= p.close and c.close >= p.open and c.body > p.body:
            matches.append(PatternMatch(
                name="Bullish Engulfing",
                category="candlestick",
                bias="BULLISH",
                confidence=0.82 if trend == "DOWN" else 0.70,
                index=i,
                description="Candle hijau menelan seluruh body candle merah sebelumnya.",
                habit_rule="Kebiasaan market: pergeseran kendali mendadak ke buyer; sangat kuat di area demand/support.",
            ))
        elif p.is_bullish and c.is_bearish and c.open >= p.close and c.close <= p.open and c.body > p.body:
            matches.append(PatternMatch(
                name="Bearish Engulfing",
                category="candlestick",
                bias="BEARISH",
                confidence=0.82 if trend == "UP" else 0.70,
                index=i,
                description="Candle merah menelan seluruh body candle hijau sebelumnya.",
                habit_rule="Kebiasaan market: seller mengambil alih agresif; sering memicu penurunan lanjutan di resistance.",
            ))

        # 7. Harami (Inside Body)
        if p.is_bearish and c.is_bullish and c.open > p.close and c.close < p.open and p.body > avg_body:
            matches.append(PatternMatch(
                name="Bullish Harami",
                category="candlestick",
                bias="BULLISH",
                confidence=0.66,
                index=i,
                description="Candle hijau kecil berada sepenuhnya di dalam body merah besar.",
                habit_rule="Kebiasaan market: tekanan jual mendadak mengerem; sinyal awal reversal atau base sebelum bounce.",
            ))
        elif p.is_bullish and c.is_bearish and c.open < p.close and c.close > p.open and p.body > avg_body:
            matches.append(PatternMatch(
                name="Bearish Harami",
                category="candlestick",
                bias="BEARISH",
                confidence=0.66,
                index=i,
                description="Candle merah kecil di dalam body hijau besar.",
                habit_rule="Kebiasaan market: momentum naik mulai kehabisan tenaga; waspadai pullback.",
            ))

        # 8. Piercing Line / Dark Cloud Cover
        p_mid = (p.open + p.close) / 2.0
        if p.is_bearish and c.is_bullish and c.open < p.close and c.close > p_mid and c.close < p.open:
            matches.append(PatternMatch(
                name="Piercing Line",
                category="candlestick",
                bias="BULLISH",
                confidence=0.72,
                index=i,
                description="Candle hijau dibuka di bawah close merah lalu ditutup di atas 50% body merah.",
                habit_rule="Kebiasaan market: penyerapan cepat (absorption) oleh buyer; reversal bullish efektif setelah penurunan tajam.",
            ))
        elif p.is_bullish and c.is_bearish and c.open > p.close and c.close < p_mid and c.close > p.open:
            matches.append(PatternMatch(
                name="Dark Cloud Cover",
                category="candlestick",
                bias="BEARISH",
                confidence=0.72,
                index=i,
                description="Candle merah dibuka di atas close hijau lalu ditutup di bawah 50% body hijau.",
                habit_rule="Kebiasaan market: bull trap klasik di puncak; seller menekan balik lebih dari separuh kenaikan sebelumnya.",
            ))

        # 9. Tweezer Top / Bottom
        tol = 0.08 * max(avg_range, 1e-9)
        if abs(c.high - p.high) <= tol and p.is_bullish and c.is_bearish and trend == "UP":
            matches.append(PatternMatch(
                name="Tweezer Top",
                category="candlestick",
                bias="BEARISH",
                confidence=0.70,
                index=i,
                description="Dua candle berurutan memiliki high hampir identik di puncak.",
                habit_rule="Kebiasaan market: resistance kuat menolak harga dua kali berturut-turut (mini double top).",
            ))
        if abs(c.low - p.low) <= tol and p.is_bearish and c.is_bullish and trend == "DOWN":
            matches.append(PatternMatch(
                name="Tweezer Bottom",
                category="candlestick",
                bias="BULLISH",
                confidence=0.70,
                index=i,
                description="Dua candle berurutan memiliki low hampir identik di dasar.",
                habit_rule="Kebiasaan market: support kuat menahan penurunan dua kali berturut-turut (mini double bottom).",
            ))

        # 10. Inside Bar (Compression / Breakout setup)
        if c.high < p.high and c.low > p.low:
            matches.append(PatternMatch(
                name="Inside Bar",
                category="candlestick",
                bias="NEUTRAL",
                confidence=0.60,
                index=i,
                description="Range candle sepenuhnya berada di dalam high-low mother bar.",
                habit_rule="Kebiasaan market: kompresi volatilitas jangka pendek; breakout high/low mother bar sering memicu impuls cepat.",
            ))

        # --- TRIPLE CANDLE PATTERNS ---
        # 11. Morning Star / Evening Star
        if p2.is_bearish and p2.body > avg_body and p.body < 0.4 * p2.body and c.is_bullish and c.close > (p2.open + p2.close) / 2.0:
            matches.append(PatternMatch(
                name="Morning Star",
                category="candlestick",
                bias="BULLISH",
                confidence=0.84,
                index=i,
                description="Pola 3 candle: merah besar -> candle jeda kecil -> hijau besar menembus 50% candle pertama.",
                habit_rule="Kebiasaan market: pola reversal bottom paling andal; menandakan transisi penuh dari distribusi ke akumulasi.",
            ))
        if p2.is_bullish and p2.body > avg_body and p.body < 0.4 * p2.body and c.is_bearish and c.close < (p2.open + p2.close) / 2.0:
            matches.append(PatternMatch(
                name="Evening Star",
                category="candlestick",
                bias="BEARISH",
                confidence=0.84,
                index=i,
                description="Pola 3 candle: hijau besar -> candle jeda kecil -> merah besar menembus 50% candle pertama.",
                habit_rule="Kebiasaan market: pola reversal top klasik; buyer kehabisan tenaga lalu seller mengambil alih.",
            ))

        # 12. Three White Soldiers / Three Black Crows
        if (
            p2.is_bullish and p.is_bullish and c.is_bullish
            and c.close > p.close > p2.close
            and p2.body > 0.7 * avg_body and p.body > 0.7 * avg_body and c.body > 0.7 * avg_body
        ):
            matches.append(PatternMatch(
                name="Three White Soldiers",
                category="candlestick",
                bias="BULLISH",
                confidence=0.82,
                index=i,
                description="Tiga candle hijau solid berturut-turut dengan close semakin tinggi.",
                habit_rule="Kebiasaan market: akselerasi tren naik yang sehat; sering diikuti retest kecil sebelum rally berlanjut.",
            ))
        if (
            p2.is_bearish and p.is_bearish and c.is_bearish
            and c.close < p.close < p2.close
            and p2.body > 0.7 * avg_body and p.body > 0.7 * avg_body and c.body > 0.7 * avg_body
        ):
            matches.append(PatternMatch(
                name="Three Black Crows",
                category="candlestick",
                bias="BEARISH",
                confidence=0.82,
                index=i,
                description="Tiga candle merah solid berturut-turut dengan close semakin rendah.",
                habit_rule="Kebiasaan market: aksi jual institusional beruntun; tekanan turun cenderung berlanjut.",
            ))

    # Deduplicate by pattern name keeping the most recent occurrence
    seen = {}
    for m in matches:
        seen[m.name] = m
    return list(seen.values())

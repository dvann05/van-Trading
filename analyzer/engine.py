"""Master Trading Analyzer Engine combining all indicators, patterns, and market habits."""

from dataclasses import asdict
from typing import Any, Dict, List
from models import AnalysisReport, Candle, IndicatorSignal, RiskPlan
from indicators import (
    ad_line,
    adx,
    aroon,
    atr,
    awesome_oscillator,
    bollinger_bands,
    cci,
    chaikin_volatility,
    cmf,
    cmo,
    dema,
    donchian_channels,
    ease_of_movement,
    ema,
    fibonacci_retracement,
    force_index,
    historical_volatility,
    hma,
    ichimoku,
    keltner_channels,
    linear_regression_slope,
    macd,
    mfi,
    momentum,
    obv,
    parabolic_sar,
    pivot_points_camarilla,
    pivot_points_classic,
    pivot_points_fibonacci,
    roc,
    rsi,
    sma,
    stoch_rsi,
    stochastic,
    supertrend,
    tema,
    trix,
    ttm_squeeze,
    ultimate_oscillator,
    volume_oscillator,
    volume_profile,
    vwap,
    vwma,
    williams_r,
    wma,
)
from indicators.structure import detect_market_structure
from patterns import (
    detect_candlestick_patterns,
    detect_chart_patterns,
    detect_market_habits,
)


def _score_bias(bias: str, strength: float) -> float:
    if bias == "BULLISH":
        return strength
    if bias == "BEARISH":
        return -strength
    return 0.0


def analyze_market(
    candles: List[Candle], symbol: str = "UNKNOWN", interval: str = "1h"
) -> AnalysisReport:
    if len(candles) < 30:
        raise ValueError("Minimal dibutuhkan 30 candle untuk analisis teknikal lengkap.")

    closes = [c.close for c in candles]
    last = candles[-1]
    prev = candles[-2]
    pct_change = (last.close - prev.close) / max(prev.close, 1e-9) * 100.0

    # --- 1. COMPUTE ALL INDICATORS ---
    sma20 = sma(closes, 20)
    sma50 = sma(closes, 50)
    sma200 = sma(closes, 200)
    ema9 = ema(closes, 9)
    ema21 = ema(closes, 21)
    ema50 = ema(closes, 50)
    wma20 = wma(closes, 20)
    dema20 = dema(closes, 20)
    tema20 = tema(closes, 20)
    hma20 = hma(closes, 20)
    vwma20 = vwma(candles, 20)
    ichi = ichimoku(candles)
    adx_data = adx(candles, 14)
    psar_vals, psar_dir = parabolic_sar(candles)
    st_vals, st_dir = supertrend(candles, 10, 3.0)
    aroon_data = aroon(candles, 25)
    linreg = linear_regression_slope(closes, 14)

    rsi_vals = rsi(closes, 14)
    stoch_data = stochastic(candles, 14, 3, 3)
    srsi_data = stoch_rsi(closes)
    macd_data = macd(closes, 12, 26, 9)
    cci_vals = cci(candles, 20)
    willr_vals = williams_r(candles, 14)
    roc_vals = roc(closes, 12)
    mom_vals = momentum(closes, 10)
    mfi_vals = mfi(candles, 14)
    ao_vals = awesome_oscillator(candles)
    uo_vals = ultimate_oscillator(candles)
    trix_vals = trix(closes, 15)
    cmo_vals = cmo(closes, 14)

    atr_vals = atr(candles, 14)
    bb = bollinger_bands(closes, 20, 2.0)
    kc = keltner_channels(candles, 20, 10, 1.5)
    dc = donchian_channels(candles, 20)
    hv_vals = historical_volatility(closes, 20)
    cv_vals = chaikin_volatility(candles, 10, 10)
    sq_data = ttm_squeeze(candles, 20, 2.0, 1.5)

    obv_vals = obv(candles)
    vwap_vals = vwap(candles)
    ad_vals = ad_line(candles)
    cmf_vals = cmf(candles, 20)
    vosc_vals = volume_oscillator(candles, 5, 10)
    fi_vals = force_index(candles, 13)
    emv_vals = ease_of_movement(candles, 14)
    vp = volume_profile(candles[-min(len(candles), 120) :])

    ms = detect_market_structure(candles)

    # --- 2. EVALUATE INDICATOR SIGNALS + HABIT NOTES ---
    signals: List[IndicatorSignal] = []

    def add_ma_sig(name: str, val: Any, habit: str) -> None:
        if val is None:
            return
        bias = "BULLISH" if last.close > val else "BEARISH" if last.close < val else "NEUTRAL"
        dist = abs(last.close - val) / max(val, 1e-9)
        strength = min(1.0, 0.45 + dist * 10.0)
        signals.append(IndicatorSignal(name, "trend", round(val, 4), bias, strength, habit))

    add_ma_sig("EMA 9", ema9[-1], "Momentum cepat; harga di atas EMA 9 menandakan akselerasi bullish jangka pendek.")
    add_ma_sig("EMA 21", ema21[-1], "Dynamic S/R favorit swing trader; pullback ke EMA 21 sering memantul mengikuti tren.")
    add_ma_sig("SMA 20", sma20[-1], "Garis tengah Bollinger; penentu bias jangka pendek-menengah.")
    add_ma_sig("SMA 50", sma50[-1], "Acuan tren menengah institusional; sering diuji saat koreksi sehat.")
    add_ma_sig("SMA 200", sma200[-1], "Batas bull vs bear market jangka panjang.")
    add_ma_sig("WMA 20", wma20[-1], "Rata-rata tertimbang lebih responsif terhadap candle terbaru.")
    add_ma_sig("DEMA 20", dema20[-1], "Double EMA mengurangi lag untuk deteksi belokan tren lebih awal.")
    add_ma_sig("TEMA 20", tema20[-1], "Triple EMA sangat cepat mendeteksi perubahan momentum.")
    add_ma_sig("HMA 20", hma20[-1], "Hull MA halus dan minim lag; perubahan arah HMA sering mendahului tren baru.")
    add_ma_sig("VWMA 20", vwma20[-1], "MA berbasis volume; jika di atas SMA 20 berarti volume mendukung kenaikan.")

    # Ichimoku Cloud
    sa, sb = ichi["senkou_a"][-1], ichi["senkou_b"][-1]
    tk, kj = ichi["tenkan"][-1], ichi["kijun"][-1]
    if sa is not None and sb is not None:
        cloud_top, cloud_bot = max(sa, sb), min(sa, sb)
        if last.close > cloud_top:
            ic_bias, ic_str, ic_note = "BULLISH", 0.85, "Harga di atas Kumo (awan); kebiasaan market tren naik solid."
        elif last.close < cloud_bot:
            ic_bias, ic_str, ic_note = "BEARISH", 0.85, "Harga di bawah Kumo (awan); tren turun dominan."
        else:
            ic_bias, ic_str, ic_note = "NEUTRAL", 0.40, "Harga di dalam Kumo (awan); area rawan whipsaw/sideways."
        signals.append(IndicatorSignal(
            "Ichimoku Cloud", "trend",
            {"tenkan": round(tk, 4) if tk else None, "kijun": round(kj, 4) if kj else None, "cloud": [round(cloud_bot, 4), round(cloud_top, 4)]},
            ic_bias, ic_str, ic_note,
        ))

    # ADX / DMI
    adx_v = adx_data["adx"][-1]
    pdi_v = adx_data["plus_di"][-1]
    mdi_v = adx_data["minus_di"][-1]
    if adx_v is not None and pdi_v is not None and mdi_v is not None:
        if adx_v < 20:
            adx_bias, adx_str, adx_note = "NEUTRAL", 0.30, "ADX < 20: market sideways/lemah; gunakan strategi mean-reversion."
        elif pdi_v > mdi_v:
            adx_bias, adx_str = "BULLISH", min(1.0, adx_v / 40.0)
            adx_note = f"ADX {adx_v:.1f} dengan +DI > -DI: tren naik aktif dan terkonfirmasi."
        else:
            adx_bias, adx_str = "BEARISH", min(1.0, adx_v / 40.0)
            adx_note = f"ADX {adx_v:.1f} dengan -DI > +DI: tren turun aktif dan terkonfirmasi."
        signals.append(IndicatorSignal(
            "ADX / DMI (14)", "trend",
            {"adx": round(adx_v, 2), "+DI": round(pdi_v, 2), "-DI": round(mdi_v, 2)},
            adx_bias, adx_str, adx_note,
        ))

    # Parabolic SAR & Supertrend
    if psar_vals[-1] is not None:
        pb = "BULLISH" if psar_dir[-1] == 1 else "BEARISH"
        signals.append(IndicatorSignal(
            "Parabolic SAR", "trend", round(psar_vals[-1], 4), pb, 0.70,
            "Titik SAR di bawah candle = trailing stop uptrend; di atas candle = downtrend.",
        ))
    if st_vals[-1] is not None:
        sb_dir = "BULLISH" if st_dir[-1] == 1 else "BEARISH"
        signals.append(IndicatorSignal(
            "Supertrend (10,3)", "trend", round(st_vals[-1], 4), sb_dir, 0.80,
            "Filter tren berbasis ATR; efektif menahan posisi selama tren tidak berbalik.",
        ))

    # Aroon & Linear Regression Slope
    if aroon_data["osc"][-1] is not None:
        ao_v = aroon_data["osc"][-1]
        ab = "BULLISH" if ao_v > 25 else "BEARISH" if ao_v < -25 else "NEUTRAL"  # type: ignore[operator]
        signals.append(IndicatorSignal(
            "Aroon (25)", "trend",
            {"up": round(aroon_data["up"][-1] or 0, 1), "down": round(aroon_data["down"][-1] or 0, 1), "osc": round(ao_v, 1)},  # type: ignore[arg-type]
            ab, min(1.0, abs(ao_v) / 100.0),  # type: ignore[arg-type]
            "Aroon > +50 menandakan high baru dominan; < -50 menandakan low baru dominan.",
        ))
    if linreg[-1] is not None:
        lb = "BULLISH" if linreg[-1] > 0 else "BEARISH" if linreg[-1] < 0 else "NEUTRAL"
        signals.append(IndicatorSignal(
            "LinReg Slope (14)", "trend", round(linreg[-1], 5), lb, 0.60,
            "Kemiringan regresi linear menunjukkan kecepatan dan arah tren statistik.",
        ))

    # --- MOMENTUM SIGNALS ---
    if rsi_vals[-1] is not None:
        rv = rsi_vals[-1]
        if rv >= 70:
            rb, rs, rn = "BEARISH", 0.72, "RSI >= 70 (Overbought): rawan pullback, kecuali saat tren parabolik."
        elif rv <= 30:
            rb, rs, rn = "BULLISH", 0.72, "RSI <= 30 (Oversold): potensi technical rebound / area serap buyer."
        elif rv > 55:
            rb, rs, rn = "BULLISH", 0.62, "RSI di zona bullish (55-70): momentum naik sehat."
        elif rv < 45:
            rb, rs, rn = "BEARISH", 0.62, "RSI di zona bearish (30-45): tekanan jual dominan."
        else:
            rb, rs, rn = "NEUTRAL", 0.30, "RSI netral (45-55): keseimbangan buyer dan seller."
        signals.append(IndicatorSignal("RSI (14)", "momentum", round(rv, 2), rb, rs, rn))

    if stoch_data["k"][-1] is not None and stoch_data["d"][-1] is not None:
        sk, sd_v = stoch_data["k"][-1], stoch_data["d"][-1]
        if sk < 20 and sk > sd_v:  # type: ignore[operator]
            stb, sts, stn = "BULLISH", 0.80, "Stochastic golden cross di area oversold (<20): sinyal pantulan kuat."
        elif sk > 80 and sk < sd_v:  # type: ignore[operator]
            stb, sts, stn = "BEARISH", 0.80, "Stochastic dead cross di area overbought (>80): sinyal koreksi kuat."
        elif sk > sd_v:  # type: ignore[operator]
            stb, sts, stn = "BULLISH", 0.55, "%K di atas %D: momentum jangka pendek mengarah naik."
        else:
            stb, sts, stn = "BEARISH", 0.55, "%K di bawah %D: momentum jangka pendek mengarah turun."
        signals.append(IndicatorSignal("Stochastic (14,3,3)", "momentum", {"%K": round(sk, 2), "%D": round(sd_v, 2)}, stb, sts, stn))  # type: ignore[arg-type]

    if srsi_data["k"][-1] is not None:
        srk = srsi_data["k"][-1]
        srb = "BULLISH" if srk < 20 else "BEARISH" if srk > 80 else "NEUTRAL"  # type: ignore[operator]
        signals.append(IndicatorSignal(
            "StochRSI", "momentum", round(srk, 2), srb, 0.60,  # type: ignore[arg-type]
            "Sangat sensitif terhadap kondisi ekstrem jangka pendek; cocok untuk timing entry.",
        ))

    if macd_data["histogram"][-1] is not None:
        mh = macd_data["histogram"][-1]
        ml = macd_data["macd"][-1] or 0.0
        msig = macd_data["signal"][-1] or 0.0
        mb = "BULLISH" if mh > 0 else "BEARISH" if mh < 0 else "NEUTRAL"  # type: ignore[operator]
        mn = "MACD di atas Signal Line (histogram positif): momentum bullish." if mb == "BULLISH" else "MACD di bawah Signal Line (histogram negatif): momentum bearish."
        signals.append(IndicatorSignal(
            "MACD (12,26,9)", "momentum",
            {"macd": round(ml, 4), "signal": round(msig, 4), "hist": round(mh, 4)},  # type: ignore[arg-type]
            mb, 0.75, mn,
        ))

    if cci_vals[-1] is not None:
        cv = cci_vals[-1]
        cb = "BULLISH" if cv > 100 else "BEARISH" if cv < -100 else "NEUTRAL"
        signals.append(IndicatorSignal(
            "CCI (20)", "momentum", round(cv, 2), cb, 0.65,
            "CCI > +100 menandakan impuls tren naik kuat; < -100 impuls turun kuat.",
        ))

    if willr_vals[-1] is not None:
        wr = willr_vals[-1]
        wb = "BULLISH" if wr < -80 else "BEARISH" if wr > -20 else "NEUTRAL"
        signals.append(IndicatorSignal(
            "Williams %R (14)", "momentum", round(wr, 2), wb, 0.60,
            "<-80 = oversold (potensi pantul); >-20 = overbought (potensi koreksi).",
        ))

    if roc_vals[-1] is not None:
        rv_roc = roc_vals[-1]
        signals.append(IndicatorSignal(
            "ROC (12)", "momentum", round(rv_roc, 2),
            "BULLISH" if rv_roc > 0 else "BEARISH" if rv_roc < 0 else "NEUTRAL",
            0.55, "Rate of Change mengukur kecepatan persentase perubahan harga.",
        ))

    if mom_vals[-1] is not None:
        mv = mom_vals[-1]
        signals.append(IndicatorSignal(
            "Momentum (10)", "momentum", round(mv, 4),
            "BULLISH" if mv > 0 else "BEARISH" if mv < 0 else "NEUTRAL",
            0.50, "Momentum positif = harga lebih tinggi dari 10 bar lalu.",
        ))

    if mfi_vals[-1] is not None:
        mf = mfi_vals[-1]
        mfb = "BULLISH" if mf < 20 else "BEARISH" if mf > 80 else ("BULLISH" if mf > 55 else "BEARISH" if mf < 45 else "NEUTRAL")
        signals.append(IndicatorSignal(
            "MFI (14)", "momentum", round(mf, 2), mfb, 0.70,
            "RSI berbasis volume; <20 aliran uang jenuh jual, >80 jenuh beli.",
        ))

    if ao_vals[-1] is not None:
        aov = ao_vals[-1]
        signals.append(IndicatorSignal(
            "Awesome Oscillator", "momentum", round(aov, 4),
            "BULLISH" if aov > 0 else "BEARISH" if aov < 0 else "NEUTRAL",
            0.60, "Di atas nol = momentum jangka pendek mengungguli jangka menengah.",
        ))

    if uo_vals[-1] is not None:
        uov = uo_vals[-1]
        uob = "BULLISH" if uov < 30 else "BEARISH" if uov > 70 else ("BULLISH" if uov > 55 else "BEARISH" if uov < 45 else "NEUTRAL")
        signals.append(IndicatorSignal(
            "Ultimate Oscillator", "momentum", round(uov, 2), uob, 0.60,
            "Menggabungkan 3 timeframe momentum (7/14/28) untuk mengurangi false signal.",
        ))

    if trix_vals[-1] is not None:
        tv = trix_vals[-1]
        signals.append(IndicatorSignal(
            "TRIX (15)", "momentum", round(tv, 4),
            "BULLISH" if tv > 0 else "BEARISH" if tv < 0 else "NEUTRAL",
            0.58, "Triple-smoothed oscillator; menyaring noise pasar jangka pendek.",
        ))

    if cmo_vals[-1] is not None:
        cmov = cmo_vals[-1]
        cmob = "BULLISH" if cmov > 25 else "BEARISH" if cmov < -25 else "NEUTRAL"
        signals.append(IndicatorSignal(
            "CMO (14)", "momentum", round(cmov, 2), cmob, 0.55,
            "Chande Momentum Oscillator: >+50 overbought, <-50 oversold.",
        ))

    # --- VOLATILITY SIGNALS ---
    atr_v = atr_vals[-1] or (last.range if last.range > 0 else last.close * 0.01)
    atr_pct = (atr_v / max(last.close, 1e-9)) * 100.0
    signals.append(IndicatorSignal(
        "ATR (14)", "volatility", {"atr": round(atr_v, 4), "atr_pct": round(atr_pct, 2)},
        "NEUTRAL", 0.50,
        f"Volatilitas rata-rata {atr_pct:.2f}% per candle; dipakai untuk ukuran SL/TP adaptif.",
    ))

    if bb["percent_b"][-1] is not None:
        pb = bb["percent_b"][-1]
        bw = bb["bandwidth"][-1] or 0.0
        bbb = "BULLISH" if pb > 0.6 else "BEARISH" if pb < 0.4 else "NEUTRAL"  # type: ignore[operator]
        signals.append(IndicatorSignal(
            "Bollinger Bands (20,2)", "volatility",
            {"%B": round(pb, 2), "bandwidth_pct": round(bw, 2)},  # type: ignore[arg-type]
            bbb, 0.60,
            "Bandwidth sempit = fase akumulasi/squeeze; %B > 0.8 saat tren kuat = Band Walk.",
        ))

    if kc["upper"][-1] is not None:
        kcb = "BULLISH" if last.close > kc["middle"][-1] else "BEARISH"  # type: ignore[operator]
        signals.append(IndicatorSignal(
            "Keltner Channels", "volatility",
            {"upper": round(kc["upper"][-1], 4), "mid": round(kc["middle"][-1], 4), "lower": round(kc["lower"][-1], 4)},  # type: ignore[arg-type]
            kcb, 0.55,
            "Kanal berbasis ATR; dikombinasikan dengan BB untuk mendeteksi TTM Squeeze.",
        ))

    if hv_vals[-1] is not None:
        signals.append(IndicatorSignal(
            "Historical Volatility", "volatility", f"{hv_vals[-1]:.1f}%", "NEUTRAL", 0.40,
            "Volatilitas tahunan historis untuk mengukur rezim risiko instrumen.",
        ))

    if cv_vals[-1] is not None:
        signals.append(IndicatorSignal(
            "Chaikin Volatility", "volatility", round(cv_vals[-1], 2), "NEUTRAL", 0.40,
            "Lonjakan positif tajam menandakan pelebaran range (potensi klimaks atau breakout).",
        ))

    # --- VOLUME SIGNALS ---
    obv_slope = obv_vals[-1] - obv_vals[-min(len(obv_vals), 10)]
    signals.append(IndicatorSignal(
        "OBV", "volume", round(obv_vals[-1], 1),
        "BULLISH" if obv_slope > 0 else "BEARISH" if obv_slope < 0 else "NEUTRAL",
        0.72, "Akumulasi volume bersih; OBV naik sebelum harga breakout adalah kebiasaan smart money.",
    ))

    vwap_v = vwap_vals[-1]
    signals.append(IndicatorSignal(
        "VWAP", "volume", round(vwap_v, 4),
        "BULLISH" if last.close > vwap_v else "BEARISH" if last.close < vwap_v else "NEUTRAL",
        0.78, "Acuan harga wajar institusi; di atas VWAP = buyer mengendalikan sesi.",
    ))

    ad_slope = ad_vals[-1] - ad_vals[-min(len(ad_vals), 10)]
    signals.append(IndicatorSignal(
        "A/D Line", "volume", round(ad_vals[-1], 1),
        "BULLISH" if ad_slope > 0 else "BEARISH" if ad_slope < 0 else "NEUTRAL",
        0.65, "Mengukur apakah candle lebih sering ditutup dekat high (akumulasi) atau low (distribusi).",
    ))

    if cmf_vals[-1] is not None:
        cmfv = cmf_vals[-1]
        signals.append(IndicatorSignal(
            "Chaikin Money Flow (20)", "volume", round(cmfv, 3),
            "BULLISH" if cmfv > 0.05 else "BEARISH" if cmfv < -0.05 else "NEUTRAL",
            0.70, "CMF > +0.05 menandakan tekanan beli institusional; < -0.05 distribusi.",
        ))

    if vosc_vals[-1] is not None:
        signals.append(IndicatorSignal(
            "Volume Oscillator", "volume", f"{vosc_vals[-1]:.1f}%", "NEUTRAL", 0.40,
            "Positif = partisipasi volume meningkat (mendukung validitas breakout).",
        ))

    if fi_vals[-1] is not None:
        fiv = fi_vals[-1]
        signals.append(IndicatorSignal(
            "Force Index (13)", "volume", round(fiv, 2),
            "BULLISH" if fiv > 0 else "BEARISH" if fiv < 0 else "NEUTRAL",
            0.65, "Menggabungkan arah harga, jarak, dan volume untuk membaca kekuatan dorongan.",
        ))

    if emv_vals[-1] is not None:
        emvv = emv_vals[-1]
        signals.append(IndicatorSignal(
            "Ease of Movement (14)", "volume", round(emvv, 4),
            "BULLISH" if emvv > 0 else "BEARISH" if emvv < 0 else "NEUTRAL",
            0.50, "Positif = harga naik ringan tanpa hambatan volume besar.",
        ))

    vp_bias = "BULLISH" if last.close > vp["poc"] else "BEARISH" if last.close < vp["poc"] else "NEUTRAL"
    signals.append(IndicatorSignal(
        "Volume Profile (POC)", "volume",
        {"POC": round(vp["poc"], 4), "VAH": round(vp["vah"], 4), "VAL": round(vp["val"], 4)},
        vp_bias, 0.70,
        "POC adalah harga dengan transaksi terbesar (magnet harga); di atas POC condong bullish.",
    ))

    # Structure signal
    ms_bias = "BULLISH" if "BULLISH" in ms["structure"] else "BEARISH" if "BEARISH" in ms["structure"] else "NEUTRAL"
    signals.append(IndicatorSignal(
        "Market Structure", "structure", ms["structure"], ms_bias, 0.85,
        "Struktur HH/HL = uptrend sehat; LH/LL = downtrend; pantau BOS/CHoCH untuk perubahan arah.",
    ))

    # --- 3. DETECT PATTERNS & MARKET HABITS ---
    candle_patterns = detect_candlestick_patterns(candles)
    chart_patterns = detect_chart_patterns(candles)
    habit_patterns, wyckoff_phase = detect_market_habits(candles, {
        "ema9": ema9, "ema21": ema21, "ema50": ema50,
        "sma50": sma50, "sma200": sma200,
        "rsi": rsi_vals, "macd_hist": macd_data["histogram"],
        "obv": obv_vals, "bb": bb, "squeeze": sq_data,
        "adx": adx_data, "donchian": dc,
    })
    all_patterns = candle_patterns + chart_patterns + habit_patterns

    # --- 4. CONFLUENCE SCORING ---
    cat_buckets: Dict[str, List[float]] = {
        "trend": [], "momentum": [], "volatility": [], "volume": [], "structure": [], "patterns": []
    }
    for s in signals:
        if s.bias != "NEUTRAL":
            cat_buckets[s.category].append(_score_bias(s.bias, s.strength))
    for p in all_patterns:
        if p.bias != "NEUTRAL":
            cat_buckets["patterns"].append(_score_bias(p.bias, p.confidence))

    category_scores: Dict[str, float] = {}
    for cat, vals in cat_buckets.items():
        category_scores[cat] = round((sum(vals) / len(vals)) * 100.0, 1) if vals else 0.0

    weights = {
        "trend": 0.28,
        "momentum": 0.22,
        "volume": 0.16,
        "structure": 0.14,
        "patterns": 0.15,
        "volatility": 0.05,
    }
    overall_score = round(sum(category_scores[k] * w for k, w in weights.items()), 1)

    if overall_score >= 45:
        overall_bias = "STRONG BUY"
    elif overall_score >= 15:
        overall_bias = "BUY"
    elif overall_score <= -45:
        overall_bias = "STRONG SELL"
    elif overall_score <= -15:
        overall_bias = "SELL"
    else:
        overall_bias = "NEUTRAL"

    # Market Regime
    adx_cur = adx_v or 20.0
    if sq_data["squeeze_on"][-1] == 1.0:
        market_regime = "SQUEEZE / VOLATILITY COMPRESSION (Siap Breakout)"
    elif adx_cur >= 28 and overall_score >= 20:
        market_regime = "STRONG UPTREND"
    elif adx_cur >= 28 and overall_score <= -20:
        market_regime = "STRONG DOWNTREND"
    elif adx_cur >= 20 and overall_score > 0:
        market_regime = "MODERATE UPTREND"
    elif adx_cur >= 20 and overall_score < 0:
        market_regime = "MODERATE DOWNTREND"
    else:
        market_regime = "RANGING / SIDEWAYS"

    # --- 5. KEY LEVELS (PIVOTS & FIBONACCI) ---
    recent_60 = candles[-min(len(candles), 60) :]
    hi60 = max(c.high for c in recent_60)
    lo60 = min(c.low for c in recent_60)
    key_levels = {
        "classic_pivots": {k: round(v, 4) for k, v in pivot_points_classic(prev.high, prev.low, prev.close).items()},
        "fibonacci_pivots": {k: round(v, 4) for k, v in pivot_points_fibonacci(prev.high, prev.low, prev.close).items()},
        "camarilla_pivots": {k: round(v, 4) for k, v in pivot_points_camarilla(prev.high, prev.low, prev.close).items()},
        "fibonacci_retracement": {
            k: round(v, 4) for k, v in fibonacci_retracement(hi60, lo60, overall_score >= 0).items()
        },
        "volume_profile": {k: round(v, 4) for k, v in vp.items()},
    }

    # --- 6. ATR-BASED RISK PLAN ---
    entry = last.close
    if overall_bias in ("STRONG BUY", "BUY"):
        sl = entry - 1.5 * atr_v
        tp1 = entry + 1.5 * atr_v
        tp2 = entry + 2.5 * atr_v
        tp3 = entry + 4.0 * atr_v
        direction = "LONG"
    elif overall_bias in ("STRONG SELL", "SELL"):
        sl = entry + 1.5 * atr_v
        tp1 = entry - 1.5 * atr_v
        tp2 = entry - 2.5 * atr_v
        tp3 = entry - 4.0 * atr_v
        direction = "SHORT"
    else:
        sl = entry - 1.5 * atr_v
        tp1 = entry + 1.5 * atr_v
        tp2 = entry + 2.5 * atr_v
        tp3 = entry + 4.0 * atr_v
        direction = "WAIT"

    risk = max(abs(entry - sl), 1e-9)
    risk_plan = RiskPlan(
        direction=direction,
        entry=round(entry, 4),
        stop_loss=round(sl, 4),
        take_profit_1=round(tp1, 4),
        take_profit_2=round(tp2, 4),
        take_profit_3=round(tp3, 4),
        atr=round(atr_v, 4),
        risk_reward_1=round(abs(tp1 - entry) / risk, 2),
        risk_reward_2=round(abs(tp2 - entry) / risk, 2),
        risk_reward_3=round(abs(tp3 - entry) / risk, 2),
    )

    # --- 7. SUMMARY NOTES ---
    summary_notes: List[str] = [
        f"Rezim Market: {market_regime} | Fase Wyckoff: {wyckoff_phase}",
        f"Bias Gabungan: {overall_bias} (Skor {overall_score:+.1f}/100) dari {len(signals)} indikator & {len(all_patterns)} pola/kebiasaan.",
    ]
    top_patterns = sorted(all_patterns, key=lambda x: x.confidence, reverse=True)[:4]
    for tp in top_patterns:
        summary_notes.append(f"[{tp.bias}] {tp.name}: {tp.habit_rule}")

    return AnalysisReport(
        symbol=symbol,
        interval=interval,
        candle_count=len(candles),
        last_price=round(last.close, 4),
        price_change_pct=round(pct_change, 2),
        market_regime=market_regime,
        wyckoff_phase=wyckoff_phase,
        overall_bias=overall_bias,
        overall_score=overall_score,
        category_scores=category_scores,
        indicators=signals,
        patterns=all_patterns,
        key_levels=key_levels,
        risk_plan=risk_plan,
        summary_notes=summary_notes,
    )


def report_to_dict(report: AnalysisReport) -> Dict[str, Any]:
    return asdict(report)


def format_report_text(report: AnalysisReport) -> str:
    lines: List[str] = []
    sep = "=" * 76
    lines.append(sep)
    lines.append(f"  TRADING ANALYZER REPORT — {report.symbol} ({report.interval}) | {report.candle_count} Candles")
    lines.append(sep)
    lines.append(f"  Harga Terakhir : {report.last_price} ({report.price_change_pct:+.2f}%)")
    lines.append(f"  Rezim Market   : {report.market_regime}")
    lines.append(f"  Fase Wyckoff   : {report.wyckoff_phase}")
    lines.append(f"  Sinyal Utama   : {report.overall_bias} (Skor Konfluensi: {report.overall_score:+.1f} / 100)")
    lines.append("-" * 76)
    lines.append("  SKOR PER KATEGORI:")
    for cat, sc in report.category_scores.items():
        bar_len = int(abs(sc) / 5)
        bar = ("+" if sc >= 0 else "-") * bar_len
        lines.append(f"    - {cat.upper():<12}: {sc:+6.1f}  {bar}")

    lines.append("-" * 76)
    lines.append(f"  POLA & KEBIASAAN MARKET TERDETEKSI ({len(report.patterns)}):")
    if not report.patterns:
        lines.append("    (Tidak ada pola signifikan pada candle terakhir)")
    for p in sorted(report.patterns, key=lambda x: x.confidence, reverse=True):
        lines.append(f"    * [{p.bias:<7}] {p.name} ({p.category}, conf {p.confidence*100:.0f}%)")
        lines.append(f"      Info   : {p.description}")
        lines.append(f"      Aturan : {p.habit_rule}")

    lines.append("-" * 76)
    lines.append(f"  RINGKASAN INDIKATOR TEKNIKAL ({len(report.indicators)}):")
    for ind in report.indicators:
        lines.append(f"    - {ind.name:<24} [{ind.bias:<7}] val={ind.value}")
        lines.append(f"      -> {ind.habit_note}")

    lines.append("-" * 76)
    rp = report.risk_plan
    if rp:
        lines.append(f"  RENCANA RISIKO ADAPTIF (ATR={rp.atr}):")
        lines.append(f"    Arah : {rp.direction} | Entry: {rp.entry} | SL: {rp.stop_loss}")
        lines.append(
            f"    TP1  : {rp.take_profit_1} (R:R 1:{rp.risk_reward_1}) | "
            f"TP2: {rp.take_profit_2} (R:R 1:{rp.risk_reward_2}) | "
            f"TP3: {rp.take_profit_3} (R:R 1:{rp.risk_reward_3})"
        )

    lines.append("-" * 76)
    piv = report.key_levels["classic_pivots"]
    vp = report.key_levels["volume_profile"]
    fib = report.key_levels["fibonacci_retracement"]
    lines.append("  LEVEL KUNCI (SUPPORT / RESISTANCE / FIBONACCI / VOLUME PROFILE):")
    lines.append(f"    Classic Pivot : S2={piv['S2']} | S1={piv['S1']} | P={piv['P']} | R1={piv['R1']} | R2={piv['R2']}")
    lines.append(f"    Volume Profile: VAL={vp['val']} | POC={vp['poc']} | VAH={vp['vah']}")
    lines.append(f"    Fibonacci     : 38.2%={fib['38.2%']} | 50.0%={fib['50.0%']} | 61.8%={fib['61.8%']} | Ext 161.8%={fib['161.8%_ext']}")
    lines.append(sep)
    return "\n".join(lines)

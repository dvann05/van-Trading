"""Complete catalog of all supported Trading Indicators & Market Pattern Habits."""

INDICATOR_CATALOG = {
    "1. Trend Indicators (13)": [
        ("SMA (20/50/200)", "Simple Moving Average — penentu tren dasar & batas bull/bear (SMA 200)."),
        ("EMA (9/21/50)", "Exponential Moving Average — dynamic S/R dan pemicu swing crossover."),
        ("WMA (20)", "Weighted Moving Average — bobot lebih besar pada harga terbaru."),
        ("DEMA (20)", "Double EMA — mengurangi lag untuk membaca belokan tren lebih cepat."),
        ("TEMA (20)", "Triple EMA — sangat responsif terhadap akselerasi tren."),
        ("HMA (20)", "Hull Moving Average — halus sekaligus minim lag."),
        ("VWMA (20)", "Volume-Weighted MA — menggabungkan harga dan kekuatan volume."),
        ("Ichimoku Cloud", "Tenkan, Kijun, Senkou A/B (Kumo), Chikou — peta tren & S/R instan."),
        ("ADX / +DI / -DI", "Mengukur kekuatan tren (ADX > 25 = trending, < 20 = sideways)."),
        ("Parabolic SAR", "Titik trailing stop & deteksi pembalikan tren cepat."),
        ("Supertrend (10,3)", "Filter tren berbasis ATR yang tahan terhadap noise."),
        ("Aroon (25)", "Mengukur seberapa baru high/low terbentuk untuk deteksi awal tren."),
        ("LinReg Slope (14)", "Kemiringan regresi linear untuk mengukur kecepatan tren statistik."),
    ],
    "2. Momentum & Oscillator Indicators (13)": [
        ("RSI (14)", "Overbought (>=70), Oversold (<=30), dan deteksi Divergence."),
        ("Stochastic (14,3,3)", "%K/%D crossover di zona ekstrem (<20 atau >80)."),
        ("StochRSI", "Stochastic di atas RSI — timing entry jangka pendek sensitif."),
        ("MACD (12,26,9)", "Trend-momentum crossover, zero-line cross, dan histogram divergence."),
        ("CCI (20)", "Deteksi impuls keluar dari rata-rata statistik (>+100 / <-100)."),
        ("Williams %R (14)", "Mengukur posisi close relatif terhadap high-low 14 bar."),
        ("ROC (12)", "Rate of Change — persentase kecepatan perubahan harga."),
        ("Momentum (10)", "Selisih harga saat ini dibanding 10 candle sebelumnya."),
        ("MFI (14)", "Money Flow Index — RSI berbobot volume untuk membaca aliran dana."),
        ("Awesome Oscillator", "Momentum 5/34 SMA midpoint untuk deteksi twin peaks & zero cross."),
        ("Ultimate Oscillator", "Gabungan 3 timeframe momentum (7/14/28) guna kurangi sinyal palsu."),
        ("TRIX (15)", "Triple-smoothed oscillator untuk menyaring noise."),
        ("CMO (14)", "Chande Momentum Oscillator — sensitivitas overbought/oversold murni."),
    ],
    "3. Volatility Indicators (7)": [
        ("ATR (14)", "Average True Range — dasar perhitungan Stop Loss & Take Profit adaptif."),
        ("Bollinger Bands (20,2)", "Upper/Mid/Lower, %B, Bandwidth — deteksi Squeeze & Band Walk."),
        ("Keltner Channels", "Kanal berbasis EMA + ATR untuk konfirmasi tren & TTM Squeeze."),
        ("Donchian Channels (20)", "Highest high / lowest low — aturan breakout klasik Turtle Trading."),
        ("Historical Volatility", "Volatilitas tahunan berbasis log-return."),
        ("Chaikin Volatility", "Kecepatan pelebaran/penyempitan range high-low."),
        ("TTM Squeeze", "Bollinger Bands di dalam Keltner Channels = kompresi sebelum ledakan harga."),
    ],
    "4. Volume Indicators (8)": [
        ("OBV", "On-Balance Volume — melacak akumulasi/distribusi tersembunyi."),
        ("VWAP", "Volume Weighted Average Price — harga wajar acuan institusi."),
        ("A/D Line", "Accumulation/Distribution — melihat tekanan beli/jual di dalam candle."),
        ("Chaikin Money Flow (20)", "Aliran uang bersih > +0.05 bullish, < -0.05 bearish."),
        ("Volume Oscillator", "Perbandingan EMA volume cepat vs lambat untuk validasi breakout."),
        ("Force Index (13)", "Kekuatan dorongan harga x volume."),
        ("Ease of Movement (14)", "Mengukur seberapa mudah harga bergerak relatif terhadap volume."),
        ("Volume Profile (POC/VAH/VAL)", "Area transaksi terbesar (Point of Control) sebagai magnet harga."),
    ],
    "5. Support, Resistance & Smart Money Structure (8)": [
        ("Classic Pivot Points", "P, R1-R3, S1-S3 harian/sesi."),
        ("Fibonacci Pivot Points", "Pivot berbasis rasio 0.382 / 0.618 / 1.000."),
        ("Camarilla Pivots", "Level intraday reversal (R3/S3) dan breakout (R4/S4)."),
        ("Fibonacci Retracement & Ext", "Level retracement 23.6%-78.6% dan ekstensi 127.2%-161.8%."),
        ("Market Structure (HH/HL/LH/LL)", "Identifikasi struktur tren utama + BOS & CHoCH."),
        ("Fair Value Gap (FVG)", "Zona imbalance 3 candle yang sering menjadi magnet retest."),
        ("Order Blocks (OB)", "Candle terakhir berlawanan sebelum impuls institusional."),
        ("Liquidity Sweep (Stop Hunt)", "Ekor menyapu swing high/low lalu close kembali masuk range."),
    ],
}

HABIT_CATALOG = {
    "A. Kebiasaan Pola Candlestick (15+ Pola)": [
        "Doji (Standard, Dragonfly, Gravestone, Long-Legged) — jeda & rejection di S/R.",
        "Hammer / Hanging Man / Inverted Hammer / Shooting Star — penolakan harga tajam.",
        "Bullish & Bearish Marubozu — dominasi penuh buyer/seller (continuation).",
        "Spinning Top & Inside Bar — kompresi momentum menjelang breakout.",
        "Bullish & Bearish Engulfing — pergeseran kendali agresif.",
        "Bullish & Bearish Harami — pengereman momentum tren sebelumnya.",
        "Piercing Line & Dark Cloud Cover — penyerapan cepat >50% candle sebelumnya.",
        "Tweezer Top & Tweezer Bottom — penolakan ganda di level identik.",
        "Morning Star & Evening Star — pola pembalikan 3 candle paling andal.",
        "Three White Soldiers & Three Black Crows — akselerasi tren beruntun.",
    ],
    "B. Kebiasaan Chart Pattern (11 Pola)": [
        "Double Top (M) & Double Bottom (W) — kegagalan tembus 2x lalu breakout neckline.",
        "Head & Shoulders / Inverse H&S — pola distribusi/akumulasi pembalikan mayor.",
        "Ascending / Descending / Symmetrical Triangle — tekanan arah menjelang breakout.",
        "Rising Wedge (bearish) & Falling Wedge (bullish) — penyempitan momentum.",
        "Ascending & Descending Channel — buy on dip / sell on rally di batas kanal.",
        "Bull Flag & Bear Flag — konsolidasi korektif singkat sebelum kelanjutan impuls.",
    ],
    "C. Kebiasaan Pola Indikator & Perilaku Market": [
        "Regular Bullish/Bearish Divergence (RSI, MACD, OBV) — peringatan dini reversal.",
        "Hidden Bullish/Bearish Divergence — sinyal kuat kelanjutan tren (continuation).",
        "Golden Cross / Death Cross (SMA 50/200) & EMA 9/21 Cross — pemicu arus tren.",
        "EMA Ribbon Fan (Close > 9 > 21 > 50) — tren sehat; pullback ke EMA 21 = entry ideal.",
        "TTM Volatility Squeeze & Firing — volatilitas sempit selalu diikuti ekspansi besar.",
        "Bollinger Band Walk (ADX >= 28) vs Mean Reversion Stretch (ADX < 22).",
        "Donchian 20-Bar Breakout — aturan trend-following Turtle Trading.",
        "Volume Climax (>2.2x avg) & Volume Dry-Up (<0.45x avg) — konfirmasi breakout/exhaustion.",
        "Fase Siklus Wyckoff — Accumulation, Markup, Distribution, Markdown.",
        "Smart Money Habits — BOS, CHoCH, Liquidity Sweep (Stop Hunt), FVG Magnet, Order Block.",
    ],
}


def format_catalog_text() -> str:
    lines = ["=" * 76, "  KATALOG LENGKAP INDIKATOR & KEBIASAAN POLA MARKET (TRADING ANALYZER)", "=" * 76]
    for section, items in INDICATOR_CATALOG.items():
        lines.append(f"\n[{section}]")
        for name, desc in items:
            lines.append(f"  - {name:<28}: {desc}")
    lines.append("\n" + "-" * 76)
    for section, items in HABIT_CATALOG.items():
        lines.append(f"\n[{section}]")
        for item in items:
            lines.append(f"  * {item}")
    lines.append("\n" + "=" * 76)
    return "\n".join(lines)

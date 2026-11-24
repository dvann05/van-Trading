# Trading Analyzer — Indikator Lengkap & Kebiasaan Pola Market

Sistem analisis teknikal market **zero-dependency** (pure Python 3) yang menggabungkan **40+ indikator teknikal**, **pola candlestick**, **chart patterns**, **divergences**, **Smart Money Concepts (SMC)**, **fase Wyckoff**, dan **kebiasaan perilaku market** ke dalam satu mesin skor konfluensi & rencana risiko berbasis ATR.

## Fitur Utama

1. **Indikator Trend (13)**: SMA (20/50/200), EMA (9/21/50), WMA, DEMA, TEMA, Hull MA (HMA), VWMA, Ichimoku Cloud, ADX/DMI, Parabolic SAR, Supertrend, Aroon, Linear Regression Slope.
2. **Indikator Momentum & Oscillator (13)**: RSI, Stochastic, StochRSI, MACD, CCI, Williams %R, ROC, Momentum, MFI, Awesome Oscillator, Ultimate Oscillator, TRIX, CMO.
3. **Indikator Volatilitas (7)**: ATR, Bollinger Bands (%B & Bandwidth), Keltner Channels, Donchian Channels, Historical Volatility, Chaikin Volatility, TTM Squeeze.
4. **Indikator Volume (8)**: OBV, VWAP, A/D Line, Chaikin Money Flow (CMF), Volume Oscillator, Force Index, Ease of Movement (EMV), Volume Profile (POC / VAH / VAL).
5. **Struktur & Level Kunci (8)**: Classic / Fibonacci / Camarilla Pivots, Fibonacci Retracement & Extension, Swing High/Low, Market Structure (HH/HL/LH/LL, BOS, CHoCH), Fair Value Gap (FVG), Order Blocks, Liquidity Sweep (Stop Hunt).
6. **Kebiasaan Pola Market**:
   - **15+ Pola Candlestick** (Doji variants, Hammer, Shooting Star, Marubozu, Engulfing, Harami, Piercing/Dark Cloud, Tweezer, Inside Bar, Morning/Evening Star, Three White Soldiers/Black Crows).
   - **11 Chart Patterns** (Double Top/Bottom, Head & Shoulders / Inverse H&S, Triangles, Rising/Falling Wedges, Channels, Bull/Bear Flag).
   - **Kebiasaan Indikator**: Regular & Hidden Divergences (RSI, MACD, OBV), Golden/Death Cross, EMA Ribbon Fan, TTM Squeeze Firing, Bollinger Band Walk vs Mean Reversion, Donchian Breakout, Volume Climax & Dry-Up, Siklus Wyckoff.

## Cara Menggunakan

```bash
cd /data/data/com.termux/files/home/trading-analyzer

# 1. Lihat katalog lengkap semua indikator & kebiasaan pola
python3 main.py --catalog

# 2. Uji coba offline (demo)
python3 main.py --demo --scenario uptrend_breakout
python3 main.py --demo --scenario downtrend_reversal
python3 main.py --demo --scenario squeeze_range
python3 main.py --demo --scenario double_bottom

# 3. Analisis market live Crypto (Binance)
python3 main.py --source binance --symbol BTCUSDT --interval 1h

# 4. Analisis Saham / Emas / Forex (Yahoo Finance)
python3 main.py --source yahoo --symbol BBCA.JK --interval 1d --range 1y
python3 main.py --source yahoo --symbol GC=F --interval 1d --range 6mo
python3 main.py --source yahoo --symbol EURUSD=X --interval 1h --range 1mo

# 5. Analisis dari file CSV lokal
python3 main.py --csv data.csv --symbol CUSTOM

# 6. Export hasil ke JSON
python3 main.py --demo --json
```

## Menjalankan Tes

```bash
python3 -m unittest discover -s tests -v
```

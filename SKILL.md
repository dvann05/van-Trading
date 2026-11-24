---
name: trading-analyzer
description: >-
  Analisa chart trading secara realtime dan mendalam menggunakan seluruh 49 indikator
  teknikal (Trend, Momentum, Volatilitas, Volume, SMC/Struktur), pola candlestick,
  chart pattern, divergence, dan siklus Wyckoff untuk menghasilkan keputusan Entry,
  Take Profit (TP1/TP2/TP3), Stop Loss (SL), Risk:Reward, serta alasan konfluensi lengkap.
  Gunakan skill ini saat user meminta analisa chart, analisa market realtime, sinyal
  trading, setup entry/TP/SL untuk Crypto (Binance), Saham/Forex/Emas/Indeks (Yahoo),
  file CSV, atau screenshot chart.
---

# Trading Analyzer — Realtime Deep Chart Analysis Skill

Skill ini menginstruksikan agen untuk melakukan **analisis chart secara realtime dan menyeluruh** menggunakan engine di `/data/data/com.termux/files/home/trading-analyzer` dan seluruh 49 indikator teknikal + kebiasaan pola market, lalu menghasilkan **Trading Plan presisi (Entry, SL, TP1, TP2, TP3, R:R, Invalidasi, dan Alasan Konfluensi)**.

---

## Prinsip Wajib Sebelum Memberi Sinyal

1. **Jangan pernah menebak harga.** Selalu ambil data realtime terbaru melalui CLI `trading-analyzer/main.py` terlebih dahulu (kecuali user hanya mengirim gambar chart tanpa simbol yang bisa di-fetch).
2. **Wajib Multi-Timeframe (MTF).** Minimal analisa **2–3 timeframe** secara top-down:
   - **HTF (Higher Timeframe)** untuk tren & struktur besar (misal `1d` atau `4h`).
   - **MTF (Main Timeframe)** untuk setup utama yang diminta user (misal `1h` atau `4h`).
   - **LTF (Lower Timeframe)** untuk presisi timing entry & konfirmasi candlestick (misal `15m` atau `1h`).
3. **Disiplin Manajemen Risiko.** Setiap rekomendasi `LONG` atau `SHORT` **wajib** memiliki:
   - Zona Entry (Agresif & Konservatif/Retest)
   - Stop Loss (SL) struktural + buffer ATR
   - TP1, TP2, TP3 dengan Risk:Reward minimal `1:1.5` pada TP1/TP2
   - Level Invalidasi yang tegas
4. **Anti-Overtrading (`WAIT / NO TRADE`).** Jika skor konfluensi berada di zona netral (`-15` s/d `+15`), HTF & MTF saling bertabrakan tanpa konfirmasi CHoCH/Divergence, atau market sedang choppy di dalam Kumo Ichimoku, **wajib rekomendasikan `WAIT`** dan berikan *Conditional Plan* (entry hanya jika breakout/retest level kunci).

---

## Langkah 1: Pengambilan Data Realtime (Multi-Timeframe)

Jalankan perintah CLI dari direktori `/data/data/com.termux/files/home/trading-analyzer`. Gunakan `--json` jika ingin membaca seluruh angka indikator secara presisi, atau output teks langsung untuk ringkasan cepat.

### A. Market Crypto (Binance Public API — Realtime)
```bash
cd /data/data/com.termux/files/home/trading-analyzer

# Analisa Multi-Timeframe (HTF 4h + Main 1h + LTF 15m)
python3 main.py --source binance --symbol BTCUSDT --interval 4h
python3 main.py --source binance --symbol BTCUSDT --interval 1h
python3 main.py --source binance --symbol BTCUSDT --interval 15m
```
*(Ganti `BTCUSDT` dengan pair yang diminta, misal `ETHUSDT`, `SOLUSDT`, `XRPUSDT`, `BNBUSDT`, dll.)*

### B. Saham, Emas, Forex & Indeks (Yahoo Finance — Realtime/Delayed Feed)
```bash
cd /data/data/com.termux/files/home/trading-analyzer

# Saham Indonesia (akhiran .JK)
python3 main.py --source yahoo --symbol BBCA.JK --interval 1d --range 1y
python3 main.py --source yahoo --symbol BBCA.JK --interval 1h --range 1mo

# Emas / Gold Futures & Forex
python3 main.py --source yahoo --symbol GC=F --interval 1d --range 6mo
python3 main.py --source yahoo --symbol GC=F --interval 1h --range 1mo
python3 main.py --source yahoo --symbol EURUSD=X --interval 1h --range 1mo
```

### C. File CSV Lokal atau Simulasi Offline
```bash
python3 main.py --csv /path/ke/data.csv --symbol NAMA_ASET
python3 main.py --demo --scenario uptrend_breakout
```

> **Jika user mengirim screenshot chart**: Baca gambar chart secara visual (harga, struktur, candlestick, S/R), lalu jika simbolnya diketahui, **tetap jalankan CLI di atas** untuk memverifikasi seluruh 49 indikator secara matematis.

---

## Langkah 2: Instruksi Analisis Mendalam Seluruh 49 Indikator (5 Pilar)

Evaluasi **semua 5 pilar** berikut secara sistematis dari hasil engine. Jangan hanya melihat 1–2 indikator.

### Pilar 1 — Trend Indicators (13 Indikator, Bobot 28%)
Instruksi pembacaan & kebiasaan pola:
1. **SMA 20 / SMA 50 / SMA 200**:
   - Harga di atas SMA 200 = bull market makro; di bawah = bear market.
   - Cek **Golden Cross** (SMA 50 potong ke atas SMA 200) atau **Death Cross**.
2. **EMA 9 / EMA 21 / EMA 50**:
   - Cek **EMA 9/21 Cross** untuk pemicu momentum swing.
   - Cek **EMA Ribbon Fan** (`Close > EMA 9 > EMA 21 > EMA 50` = uptrend sehat; pullback ke EMA 21 adalah zona *buy on dip* terbaik).
3. **WMA 20, DEMA 20, TEMA 20, HMA 20**:
   - Indikator minim lag untuk mendeteksi belokan tren lebih cepat dibanding SMA/EMA biasa. Jika HMA & TEMA sudah berbalik sementara SMA masih datar = indikasi awal reversal.
4. **VWMA 20**:
   - Bandingkan VWMA 20 vs SMA 20. Jika `VWMA > SMA` saat harga naik = kenaikan didukung volume riil (valid).
5. **Ichimoku Cloud (Tenkan 9, Kijun 26, Senkou A/B, Chikou)**:
   - Di atas Kumo (awan) = Bullish; di bawah Kumo = Bearish; **di dalam Kumo = zona rawan whipsaw (hindari entry agresif)**.
   - Tenkan > Kijun = momentum bullish aktif.
6. **ADX (14) +DI / -DI**:
   - **Filter Rezim Wajib**:
     - `ADX < 20`: Sideways/Ranging → gunakan strategi *mean reversion* (buy support / sell resistance), **jangan kejar breakout**.
     - `ADX 20–28`: Tren mulai terbentuk.
     - `ADX >= 28`: Tren kuat → ikuti arah `+DI` (bullish) atau `-DI` (bearish), hindari melawan tren.
7. **Parabolic SAR & Supertrend (10,3)**:
   - Gunakan sebagai konfirmasi arah tren & acuan **trailing stop** dinamis.
8. **Aroon (25) & Linear Regression Slope (14)**:
   - Aroon Oscillator `> +50` = dominasi high baru; `< -50` = dominasi low baru. LinReg Slope mengukur kecepatan tren statistik.

---

### Pilar 2 — Momentum & Oscillator Indicators (13 Indikator, Bobot 22%)
Instruksi pembacaan & kebiasaan pola:
1. **RSI (14)**:
   - `>= 70` Overbought, `<= 30` Oversold, `55–70` zona bullish sehat, `30–45` zona bearish.
   - **Krusial**: Cek **Regular Divergence** (sinyal reversal kuat) dan **Hidden Divergence** (sinyal continuation kuat).
2. **Stochastic (14,3,3) & StochRSI**:
   - Cari golden cross `%K > %D` di area `< 20` untuk timing entry LONG, atau dead cross `%K < %D` di area `> 80` untuk SHORT.
3. **MACD (12,26,9)**:
   - Histogram positif & membesar = akselerasi bullish. Cek **MACD Cross** dan **MACD Histogram Divergence**.
4. **CCI (20)**:
   - Tembus `> +100` = impuls breakout naik kuat; `< -100` = impuls turun kuat.
5. **Williams %R (14), ROC (12), Momentum (10)**:
   - Validasi kecepatan dorongan harga dan kondisi jenuh jangka pendek (`<-80` oversold, `>-20` overbought).
6. **MFI (14)** *(Money Flow Index)*:
   - RSI berbobot volume; `< 20` aliran dana jenuh jual, `> 80` jenuh beli. Sangat kuat jika selaras dengan RSI.
7. **Awesome Oscillator (AO), Ultimate Oscillator (UO), TRIX (15), CMO (14)**:
   - Konfirmasi momentum lintas timeframe (UO 7/14/28) dan penyaring noise (TRIX). Jika mayoritas oscillator searah dengan tren = probabilitas tinggi.

---

### Pilar 3 — Volatility Indicators (7 Indikator, Bobot 5% + Penentu SL/TP)
Instruksi pembacaan & kebiasaan pola:
1. **ATR (14)**:
   - Wajib dipakai untuk mengukur napas harga per candle (`ATR%`) dan menentukan jarak SL (`1.2x–1.5x ATR`) serta TP (`1.5x / 2.5x / 4.0x ATR`).
2. **Bollinger Bands (20,2) & Keltner Channels**:
   - **TTM Squeeze Active** (BB masuk ke dalam Keltner) = kompresi volatilitas ekstrem (*calm before the storm*), bersiap breakout besar.
   - **TTM Squeeze Firing** = ledakan tren baru baru dimulai → sangat ideal untuk entry mengikuti arah momentum.
   - **Bollinger Band Walk vs Mean Reversion**:
     - Jika `%B >= 0.85` dan `ADX >= 28` → **Band Walk Bullish** (jangan di-short!).
     - Jika `%B > 1.0` dan `ADX < 22` → **Overextension** (rawan pullback ke Middle Band).
3. **Donchian Channels (20)**:
   - Close menembus Upper Donchian = **Turtle Bullish Breakout**; menembus Lower Donchian = **Bearish Breakdown**.
4. **Historical Volatility & Chaikin Volatility**:
   - Mengukur rezim risiko aset (volatilitas tinggi = kecilkan ukuran lot / lebarkan SL berbasis ATR).

---

### Pilar 4 — Volume & Aliran Uang (8 Indikator, Bobot 16%)
Instruksi pembacaan & kebiasaan pola:
1. **OBV (On-Balance Volume)**:
   - OBV naik mendahului harga = akumulasi smart money. Cek juga **OBV Divergence**.
2. **VWAP**:
   - Harga di atas VWAP = buyer institusional mengendalikan sesi; di bawah VWAP = seller dominan.
3. **A/D Line & Chaikin Money Flow (CMF 20)**:
   - `CMF > +0.05` = arus dana masuk (bullish); `CMF < -0.05` = distribusi (bearish).
4. **Volume Oscillator, Force Index (13), Ease of Movement (14)**:
   - Breakout **hanya valid** jika didukung Volume Oscillator positif / lonjakan volume `>= 1.5x` rata-rata.
   - **Volume Climax (`>= 2.2x avg`)**: di awal breakout = konfirmasi institusi; di ujung tren panjang = sinyal *exhaustion* (siap reversal).
   - **Volume Dry-Up (`<= 0.45x avg`)**: sering muncul saat pullback sehat atau tepat sebelum breakout.
5. **Volume Profile (POC, VAH, VAL)**:
   - **POC (Point of Control)** bekerja sebagai magnet harga & S/R terkuat. Harga di atas POC/VAH condong bullish; di bawah VAL condong bearish.

---

### Pilar 5 — Struktur Market, Level Kunci & Smart Money Concepts (8 Indikator, Bobot 14%)
Instruksi pembacaan & kebiasaan pola:
1. **Market Structure (HH/HL vs LH/LL)**:
   - Pastikan struktur utama selaras dengan arah entry.
2. **BOS (Break of Structure) & CHoCH (Change of Character)**:
   - **BOS** = konfirmasi kelanjutan tren.
   - **CHoCH** = sinyal awal pembalikan tren (tunggu retracement ke Order Block / FVG sebelum entry).
3. **Order Blocks (Bullish/Bearish OB) & Fair Value Gaps (FVG)**:
   - Gunakan zona **Unmitigated FVG** dan **Order Block** terdekat sebagai area **Limit Entry (Sniper Entry)** terbaik.
4. **Liquidity Sweep (Stop Hunt)**:
   - Jika ekor candle menyapu Swing Low lalu close kembali di atasnya = **Bullish Liquidity Sweep** (sinyal reversal naik sangat kuat). Sebaliknya di Swing High = **Bearish Liquidity Sweep**.
5. **Pivot Points (Classic, Fibonacci, Camarilla) & Fibonacci Retracement/Extension**:
   - Golden Pocket Fibonacci (`50.0% – 61.8%`) adalah zona retracement paling kuat untuk entry searah tren.
   - Level Pivot (`R1/R2/R3`, `S1/S2/S3`) dan Fibonacci Extension (`127.2%`, `161.8%`) dipakai sebagai target TP presisi.

---

## Langkah 3: Analisis Pola Candlestick, Chart Pattern & Fase Wyckoff (Bobot 15%)

Periksa semua pola yang terdeteksi oleh engine:
- **Candlestick Patterns**: Dragonfly/Gravestone/Long-Legged Doji, Hammer, Hanging Man, Shooting Star, Inverted Hammer, Bullish/Bearish Marubozu, Spinning Top, Inside Bar, Bullish/Bearish Engulfing, Harami, Piercing Line, Dark Cloud Cover, Tweezer Top/Bottom, Morning/Evening Star, Three White Soldiers/Three Black Crows.
- **Chart Patterns**: Double Top (M), Double Bottom (W), Head & Shoulders, Inverse H&S, Ascending/Descending/Symmetrical Triangle, Rising/Falling Wedge, Ascending/Descending Channel, Bull/Bear Flag.
- **Fase Wyckoff**:
  - `ACCUMULATION` → cari setup LONG di support / Liquidity Sweep / Spring.
  - `MARKUP` → ikuti tren naik (*buy on dip* di EMA 21 / OB / FVG).
  - `DISTRIBUTION` → waspada pembalikan, cari setup SHORT di resistance / Upthrust.
  - `MARKDOWN` → ikuti tren turun (*sell on rally*).

---

## Langkah 4: Aturan Penentuan Entry, SL, dan TP1/TP2/TP3

Gunakan aturan presisi berikut agar sinyal tidak asal-asalan:

### 1. Menentukan Keputusan Arah
- **LONG (`STRONG BUY` / `BUY`)**: Skor konfluensi `>= +15`, struktur tidak bearish (atau sudah ada CHoCH Bullish + Divergence), dan HTF mendukung atau sedang di support mayor.
- **SHORT (`STRONG SELL` / `SELL`)**: Skor konfluensi `<= -15`, struktur tidak bullish (atau sudah ada CHoCH Bearish + Divergence), dan HTF mendukung atau sedang di resistance mayor.
- **WAIT (`NEUTRAL`)**: Skor `-15` s/d `+15`, atau sedang **TTM Squeeze Active** belum breakout, atau harga terjebak di dalam Kumo Ichimoku. Berikan 2 skenario kondisional (*Breakout Buy* di atas resistance & *Breakdown Sell* di bawah support).

### 2. Menentukan Zona Entry (Berikan 2 Opsi)
- **Entry Agresif (Market / Breakout)**: Di sekitar harga saat ini jika momentum sedang aktif (misal TTM Squeeze Firing, Donchian Breakout dengan volume spike, atau Marubozu/Engulfing baru close).
- **Entry Konservatif (Pullback / Sniper)**: Di area konfluensi terkuat antara **EMA 21**, **VWAP**, **Fibonacci 38.2%–61.8%**, **Unmitigated FVG**, atau **Order Block** terdekat.

### 3. Menentukan Stop Loss (SL) — Wajib Struktural + ATR
- **Untuk LONG**: Tempatkan SL di bawah level terkuat terdekat (**Swing Low terakhir / Bullish OB / Supertrend / Pivot S1**), lalu tambahkan buffer `0.3x – 0.5x ATR(14)` atau minimal `1.2x – 1.5x ATR(14)` dari Entry agar tidak mudah terkena noise/stop hunt.
- **Untuk SHORT**: Tempatkan SL di atas **Swing High terakhir / Bearish OB / Supertrend / Pivot R1** + buffer ATR.
- Cantumkan jarak risiko dalam **persentase (%)** dan kelipatan **ATR**.

### 4. Menentukan Take Profit (TP1, TP2, TP3) — Bertahap
- **TP1 (Target Konservatif, R:R ~ 1:1.5)**: Resistance/Support terdekat, POC Volume Profile, Pivot R1/S1, atau `1.5x ATR`. *(Manajemen: ambil profit 35–40%, geser SL ke Breakeven).*
- **TP2 (Target Utama, R:R ~ 1:2.5)**: Swing High/Low mayor, Pivot R2/S2, Fibonacci 127.2%, atau `2.5x ATR`. *(Manajemen: ambil profit 40%).*
- **TP3 (Target Ekstensi / Runner, R:R >= 1:4.0)**: Fibonacci Extension 161.8%, Pivot R3/S3, atau `4.0x ATR` dengan trailing stop mengikuti **Supertrend / Parabolic SAR / EMA 21**.

---

## Langkah 5: Format Output Wajib ke User

Setiap kali skill ini dijalankan, sajikan jawaban dalam struktur bahasa Indonesia yang rapi, tegas, dan mudah dieksekusi berikut ini:

```markdown
## Analisa Chart Realtime — [SIMBOL] ([TIMEFRAME UTAMA] | Konfirmasi HTF [HTF])

### 1. Ringkasan Eksekutif
- **Harga Realtime**: [Harga] ([Perubahan %])
- **Rezim Market**: [STRONG UPTREND / RANGING / SQUEEZE / dll]
- **Fase Wyckoff**: [ACCUMULATION / MARKUP / DISTRIBUTION / MARKDOWN]
- **Bias Multi-Timeframe**: HTF ([Bias]) | MTF ([Bias]) | LTF ([Bias])
- **Keputusan Akhir**: **[LONG / SHORT / WAIT]** (Skor Konfluensi: `[+XX.X / 100]`)

### 2. Rekap Mendalam 5 Pilar Indikator (49 Indikator)
| Pilar | Skor | Bias | Sorotan Indikator Kunci |
| :--- | :---: | :---: | :--- |
| **Trend (13)** | `+XX` | BULLISH/BEARISH | EMA 9/21/50, SMA 200, Ichimoku, ADX/DI, Supertrend, PSAR, HMA |
| **Momentum (13)** | `+XX` | BULLISH/BEARISH | RSI, Stoch, StochRSI, MACD, CCI, MFI, AO, UO, TRIX |
| **Volatilitas (7)** | `+XX` | NEUTRAL/BULL/BEAR | ATR (%), BB %B & Bandwidth, Keltner, Donchian, TTM Squeeze |
| **Volume (8)** | `+XX` | BULLISH/BEARISH | OBV, VWAP, CMF, A/D Line, Force Index, Volume Profile (POC) |
| **Struktur & SMC (8)** | `+XX` | BULLISH/BEARISH | HH/HL atau LH/LL, BOS/CHoCH, OB, FVG, Liquidity Sweep, Pivots |

### 3. Pola & Kebiasaan Market Terdeteksi
- **[Candlestick]**: [Sebutkan pola & kebiasaan marketnya]
- **[Chart Pattern]**: [Sebutkan pola & proyeksinya]
- **[Divergence / Indicator Habit]**: [Sebutkan divergence, squeeze, band walk, ribbon, volume spike]
- **[Smart Money / SMC]**: [Sebutkan BOS/CHoCH, FVG, Order Block, Liquidity Sweep]

### 4. Trading Plan Presisi (Entry, SL, TP)
- **Arah Posisi**: **[LONG / SHORT / WAIT]**
- **Zona Entry Agresif**: `[Harga]` *(kondisi pemicu)*
- **Zona Entry Konservatif (Disarankan)**: `[Rentang Harga — misal di EMA 21 / OB / FVG / Fibo 0.618]`
- **Stop Loss (SL)**: `[Harga]` *(Risiko: `X.XX%` | `1.5x ATR` — di balik level struktur `[level]`)*
- **Take Profit 1 (TP1)**: `[Harga]` *(R:R `1:1.5` — tutup 40%, geser SL ke BEP)*
- **Take Profit 2 (TP2)**: `[Harga]` *(R:R `1:2.5` — tutup 40%)*
- **Take Profit 3 (TP3)**: `[Harga]` *(R:R `1:4.0` — sisakan 20% trailing Supertrend/EMA 21)*
- **Level Invalidasi**: Setup batal jika candle `[Timeframe]` close menembus `[Harga]`.

### 5. Alasan Lengkap (Confluence Reasoning)
1. **Kenapa Entry di Zona Ini**: [Jelaskan konfluensi trend + momentum + volume + SMC/pola]
2. **Kenapa SL di Level Ini**: [Jelaskan alasan struktur + volatilitas ATR agar aman dari stop hunt]
3. **Kenapa TP di Level Ini**: [Jelaskan target berdasarkan Pivot / Fibonacci / Swing / POC]
4. **Peringatan & Skenario Alternatif**: [Jelaskan risiko utama, misal overbought/resistance dekat, dan apa yang dilakukan jika invalid]

> *Disclaimer: Analisis ini bersifat edukasi teknikal berbasis data indikator & kebiasaan pola market, bukan nasihat keuangan mutlak. Selalu sesuaikan ukuran posisi dengan toleransi risiko (disarankan maks 1–2% modal per trade).*
```

---

## Troubleshooting Cepat
- Jika koneksi ke Binance/Yahoo gagal (timeout/offline), informasikan kendala jaringan ke user dan tawarkan analisa dari file `--csv` atau screenshot chart yang dikirim user.
- Jika simbol saham Indonesia belum memakai akhiran `.JK`, tambahkan otomatis `.JK` saat query ke Yahoo Finance (misal `BBCA` → `BBCA.JK`, `BBRI` → `BBRI.JK`, `ANTM` → `ANTM.JK`).
- Jika simbol emas ditulis `XAUUSD` atau `GOLD`, gunakan `GC=F` pada Yahoo Finance (atau `PAXGUSDT` pada Binance sebagai proksi spot 24/7).

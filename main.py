#!/usr/bin/env python3
"""CLI Entrypoint for Trading Analyzer."""

import argparse
import json
import sys
from analyzer import analyze_market, format_report_text, report_to_dict
from catalog import format_catalog_text
from data import (
    fetch_binance_klines,
    fetch_yahoo_chart,
    generate_synthetic_market,
    load_csv,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Trading Analyzer — Analisis Lengkap Semua Indikator Market & Kebiasaan Pola"
    )
    parser.add_argument("--catalog", action="store_true", help="Tampilkan katalog lengkap semua indikator & kebiasaan pola")
    parser.add_argument("--demo", action="store_true", help="Jalankan simulasi offline dengan data market sintetis")
    parser.add_argument(
        "--scenario",
        default="uptrend_breakout",
        choices=["uptrend_breakout", "downtrend_reversal", "squeeze_range", "double_bottom"],
        help="Skenario market untuk mode --demo",
    )
    parser.add_argument("--source", choices=["binance", "yahoo"], default="binance", help="Sumber data live")
    parser.add_argument("--symbol", default="BTCUSDT", help="Simbol aset (misal: BTCUSDT, ETHUSDT, BBCA.JK, GC=F, EURUSD=X)")
    parser.add_argument("--interval", default="1h", help="Timeframe (misal: 15m, 1h, 4h, 1d)")
    parser.add_argument("--limit", type=int, default=250, help="Jumlah candle (Binance)")
    parser.add_argument("--range", dest="range_str", default="1y", help="Rentang waktu (Yahoo Finance, misal: 3mo, 6mo, 1y)")
    parser.add_argument("--csv", dest="csv_path", help="Path ke file CSV OHLCV lokal")
    parser.add_argument("--json", action="store_true", help="Output laporan dalam format JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.catalog:
        print(format_catalog_text())
        return 0

    try:
        if args.csv_path:
            candles = load_csv(args.csv_path)
            symbol = args.symbol if args.symbol != "BTCUSDT" else args.csv_path
        elif args.demo:
            candles = generate_synthetic_market(scenario=args.scenario, count=240)
            symbol = f"DEMO:{args.scenario.upper()}"
        elif args.source == "binance":
            candles = fetch_binance_klines(args.symbol, args.interval, args.limit)
            symbol = args.symbol.upper()
        else:
            candles = fetch_yahoo_chart(args.symbol, args.interval, args.range_str)
            symbol = args.symbol.upper()
    except Exception as exc:
        print(f"[ERROR] Gagal mengambil data market: {exc}", file=sys.stderr)
        print("Tips: gunakan `--demo` untuk uji coba offline atau `--csv file.csv`.", file=sys.stderr)
        return 1

    report = analyze_market(candles, symbol=symbol, interval=args.interval)
    if args.json:
        print(json.dumps(report_to_dict(report), indent=2, ensure_ascii=False))
    else:
        print(format_report_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

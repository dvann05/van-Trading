"""Unit and integration tests for Trading Analyzer."""

import unittest
from analyzer import analyze_market, format_report_text, report_to_dict
from data import generate_synthetic_market
from models import Candle
from patterns import detect_candlestick_patterns


class TestTradingAnalyzer(unittest.TestCase):
    def test_all_scenarios_run_cleanly(self) -> None:
        for scenario in ["uptrend_breakout", "downtrend_reversal", "squeeze_range", "double_bottom"]:
            candles = generate_synthetic_market(scenario=scenario, count=240, seed=42)
            report = analyze_market(candles, symbol=f"TEST-{scenario}", interval="1h")
            self.assertEqual(report.candle_count, 240)
            self.assertGreaterEqual(len(report.indicators), 35)
            self.assertIn(report.overall_bias, {"STRONG BUY", "BUY", "NEUTRAL", "SELL", "STRONG SELL"})
            self.assertIsNotNone(report.risk_plan)
            self.assertIn("classic_pivots", report.key_levels)
            self.assertIn("fibonacci_retracement", report.key_levels)
            self.assertIn("volume_profile", report.key_levels)
            text = format_report_text(report)
            self.assertIn("TRADING ANALYZER REPORT", text)
            as_dict = report_to_dict(report)
            self.assertEqual(as_dict["symbol"], f"TEST-{scenario}")

    def test_bullish_engulfing_and_hammer_detection(self) -> None:
        # Build downtrend followed by Hammer and Bullish Engulfing
        candles = [
            Candle(i, 120 - i * 2, 121 - i * 2, 118 - i * 2, 118.5 - i * 2, 1000)
            for i in range(10)
        ]
        # Hammer (body=0.8, range=5.5, lower_wick=4.6, upper_wick=0.1)
        candles.append(Candle(10, 99.6, 100.5, 95.0, 100.4, 1500))
        # Bearish then Bullish Engulfing
        candles.append(Candle(11, 100.4, 100.6, 98.5, 98.8, 1200))
        candles.append(Candle(12, 98.5, 102.0, 98.4, 101.8, 2200))

        pats = detect_candlestick_patterns(candles, scan_last=4)
        names = {p.name for p in pats}
        self.assertIn("Hammer", names)
        self.assertIn("Bullish Engulfing", names)

    def test_minimum_candles_validation(self) -> None:
        short_data = generate_synthetic_market(count=15)
        with self.assertRaises(ValueError):
            analyze_market(short_data)


if __name__ == "__main__":
    unittest.main()

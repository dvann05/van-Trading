"""Core data models for Trading Analyzer."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Candle:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

    @property
    def body(self) -> float:
        return abs(self.close - self.open)

    @property
    def range(self) -> float:
        return self.high - self.low

    @property
    def upper_wick(self) -> float:
        return self.high - max(self.open, self.close)

    @property
    def lower_wick(self) -> float:
        return min(self.open, self.close) - self.low

    @property
    def is_bullish(self) -> bool:
        return self.close > self.open

    @property
    def is_bearish(self) -> bool:
        return self.close < self.open

    @property
    def midpoint(self) -> float:
        return (self.high + self.low) / 2.0

    @property
    def typical_price(self) -> float:
        return (self.high + self.low + self.close) / 3.0


@dataclass
class IndicatorSignal:
    name: str
    category: str  # trend, momentum, volatility, volume, structure
    value: Any
    bias: str  # BULLISH, BEARISH, NEUTRAL
    strength: float  # 0.0 to 1.0
    habit_note: str  # Kebiasaan pola / interpretasi market


@dataclass
class PatternMatch:
    name: str
    category: str  # candlestick, chart_pattern, divergence, market_habit, smc
    bias: str  # BULLISH, BEARISH, NEUTRAL
    confidence: float  # 0.0 to 1.0
    index: int  # candle index where detected
    description: str
    habit_rule: str  # Kebiasaan reaksi market terhadap pola ini


@dataclass
class RiskPlan:
    direction: str  # LONG, SHORT, WAIT
    entry: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    take_profit_3: float
    atr: float
    risk_reward_1: float
    risk_reward_2: float
    risk_reward_3: float


@dataclass
class AnalysisReport:
    symbol: str
    interval: str
    candle_count: int
    last_price: float
    price_change_pct: float
    market_regime: str
    wyckoff_phase: str
    overall_bias: str  # STRONG BUY, BUY, NEUTRAL, SELL, STRONG SELL
    overall_score: float  # -100 to +100
    category_scores: Dict[str, float] = field(default_factory=dict)
    indicators: List[IndicatorSignal] = field(default_factory=list)
    patterns: List[PatternMatch] = field(default_factory=list)
    key_levels: Dict[str, Any] = field(default_factory=dict)
    risk_plan: Optional[RiskPlan] = None
    summary_notes: List[str] = field(default_factory=list)

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class AssetClass(str, Enum):
    EQUITY = "equity"
    ETF = "etf"
    CRYPTO = "crypto"
    BOND = "bond"
    PROPERTY = "property"
    CASH = "cash"
    CURRENCY = "currency"
    OTHER = "other"


class Holding(BaseModel):
    ticker: str = ""
    quantity: float = 0.0
    asset_class: AssetClass = AssetClass.OTHER


class IngestionRequest(BaseModel):
    user_id: Optional[str] = None
    raw_text: str = ""
    holdings: list[Holding] = Field(default_factory=list)
    news_headlines: list[str] = Field(default_factory=list)


class IngestionResult(BaseModel):
    user_id: Optional[str] = None
    normalized_text: str = ""
    holdings: list[Holding] = Field(default_factory=list)
    tickers: list[str] = Field(default_factory=list)
    prices: dict[str, float] = Field(default_factory=dict)
    news_headlines: list[str] = Field(default_factory=list)


class SentimentResult(BaseModel):
    sentiment_score: float = 0.0
    news_headlines: list[str] = Field(default_factory=list)


class QuantSignal(BaseModel):
    total_value: float = 0.0
    asset_weights: dict[str, float] = Field(default_factory=dict)
    hhi: float = 0.0
    diversification_score: float = 0.0
    liquidity_ratio: float = 0.0


class AdvisoryRecommendation(BaseModel):
    summary: str = ""
    risks: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
    outlook: str = ""
    confidence: float = 0.0
    rationale: str = ""
    warnings: list[str] = Field(default_factory=list)


class GuardrailIssue(BaseModel):
    code: str
    message: str
    severity: str = "warning"


class GuardrailResult(BaseModel):
    approved: bool = True
    issues: list[GuardrailIssue] = Field(default_factory=list)
    adjusted_recommendation: Optional[AdvisoryRecommendation] = None


class FinalAgentDecision(BaseModel):
    request_id: str = ""
    ingestion: IngestionResult = Field(default_factory=IngestionResult)
    sentiment: SentimentResult = Field(default_factory=SentimentResult)
    quant: QuantSignal = Field(default_factory=QuantSignal)
    advisory: AdvisoryRecommendation = Field(default_factory=AdvisoryRecommendation)
    guardrail: GuardrailResult = Field(default_factory=GuardrailResult)
    metadata: dict[str, Any] = Field(default_factory=dict)

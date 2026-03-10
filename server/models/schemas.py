from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


AssetType = Literal[
    "savings",
    "equity",
    "bond",
    "crypto",
    "real_estate",
    "private_equity",
]
PropertyType = Literal["residential", "commercial", "industrial", "reit"]
TxnType = Literal["income", "expense", "transfer"]
RunStatus = Literal["pending", "running", "completed", "failed"]


class AuthRequest(BaseModel):
    email: str
    password: str


class Holding(BaseModel):
    ticker: Optional[str] = None
    quantity: float = 1.0
    asset_type: AssetType
    sector: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    value: Optional[float] = None
    asset_name: Optional[str] = None


class IngestionRequest(BaseModel):
    user_id: str
    holdings: List[Holding] = Field(default_factory=list)
    raw_text: str = ""
    news_headlines: List[str] = Field(default_factory=list)


class IngestionResult(BaseModel):
    user_id: str
    normalized_text: str = ""
    holdings: List[Holding] = Field(default_factory=list)
    tickers: List[str] = Field(default_factory=list)
    prices: Dict[str, float] = Field(default_factory=dict)
    news_headlines: List[str] = Field(default_factory=list)


class QuantSignal(BaseModel):
    total_value: float = 0.0
    asset_weights: Dict[str, float] = Field(default_factory=dict)
    hhi: float = 0.0
    diversification_score: float = 0.0
    liquidity_ratio: float = 0.0
    asset_class_allocations: Dict[str, float] = Field(default_factory=dict)


class SentimentResult(BaseModel):
    sentiment_score: float = 0.0
    sector_sentiment: Dict[str, float] = Field(default_factory=dict)
    news_headlines: List[str] = Field(default_factory=list)


class AdvisoryRecommendation(BaseModel):
    summary: str = ""
    risks: List[str] = Field(default_factory=list)
    actions: List[str] = Field(default_factory=list)
    outlook: str = ""
    confidence: float = 0.0
    rationale: str = ""
    warnings: List[str] = Field(default_factory=list)


class GuardrailIssue(BaseModel):
    code: str
    message: str
    severity: Literal["info", "warning", "blocker"] = "warning"


class GuardrailResult(BaseModel):
    approved: bool = True
    issues: List[GuardrailIssue] = Field(default_factory=list)
    adjusted_recommendation: Optional[AdvisoryRecommendation] = None


class FinalAgentDecision(BaseModel):
    request_id: str
    ingestion: IngestionResult
    sentiment: SentimentResult
    quant: QuantSignal
    advisory: AdvisoryRecommendation
    guardrail: GuardrailResult
    metadata: Dict[str, Any] = Field(default_factory=dict)
    portfolio_split: Dict[str, float] = Field(default_factory=dict)
    portfolio_health: float = 0.0


class AccountCreateRequest(BaseModel):
    user_id: str
    account_type: Literal["bank", "credit_card"]
    institution_name: Optional[str] = None
    account_name: str
    currency: str = "USD"


class TransactionCreateRequest(BaseModel):
    account_id: str
    transaction_date: date
    transaction_type: TxnType
    category: Optional[str] = None
    amount: float
    description: Optional[str] = None


class TransactionUpdateRequest(BaseModel):
    transaction_date: Optional[date] = None
    transaction_type: Optional[TxnType] = None
    category: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None


class AssetCreateRequest(BaseModel):
    user_id: str
    asset_type: AssetType
    asset_name: str
    ticker: Optional[str] = None
    sector: Optional[str] = None
    quantity: Optional[float] = None
    value: Optional[float] = None
    country: Optional[str] = None
    city: Optional[str] = None
    property_type: Optional[PropertyType] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AssetUpdateRequest(BaseModel):
    asset_type: Optional[AssetType] = None
    asset_name: Optional[str] = None
    ticker: Optional[str] = None
    sector: Optional[str] = None
    quantity: Optional[float] = None
    value: Optional[float] = None
    country: Optional[str] = None
    city: Optional[str] = None
    property_type: Optional[PropertyType] = None
    metadata: Optional[Dict[str, Any]] = None


class AnalysisRunResponse(BaseModel):
    run_id: str
    status: RunStatus
    created_at: Optional[datetime] = None
    result: Optional[FinalAgentDecision] = None
// client/src/lib/types.ts
export type AssetClass =
  | "savings"
  | "equity"
  | "bond"
  | "crypto"
  | "real_estate"
  | "private_equity"
  | "other";

export interface AgentHolding {
  ticker?: string;
  quantity: number;
  asset_type?: AssetClass | string;
  asset_class?: AssetClass | string;
  sector?: string;
  country?: string;
  city?: string;
  value?: number;
}

export interface IngestionRequestPayload {
  user_id?: string;
  raw_text: string;
  holdings: AgentHolding[];
  news_headlines: string[];
}

export interface IngestionResult {
  user_id?: string;
  normalized_text: string;
  holdings: AgentHolding[];
  tickers: string[];
  prices: Record<string, number>;
  news_headlines: string[];
}

export interface SentimentResult {
  sentiment_score: number;
  news_headlines: string[];
}

export interface QuantSignal {
  total_value: number;
  asset_weights: Record<string, number>;
  hhi: number;
  diversification_score: number;
  liquidity_ratio: number;
}

export interface AdvisoryRecommendation {
  summary: string;
  risks: string[];
  actions: string[];
  outlook: string;
  confidence: number;
  rationale: string;
  warnings: string[];
}

export interface GuardrailIssue {
  code: string;
  message: string;
  severity: string;
}

export interface GuardrailResult {
  approved: boolean;
  issues: GuardrailIssue[];
}

export interface FinalAgentDecision {
  request_id: string;
  ingestion: IngestionResult;
  sentiment: SentimentResult;
  quant: QuantSignal;
  advisory: AdvisoryRecommendation;
  guardrail: GuardrailResult;
  metadata: Record<string, unknown>;
  portfolio_split?: Record<string, number>;
  portfolio_health?: number;
}

export interface Holding {
  ticker: string;
  name: string;
  weight: number;
  value: number;
  change24h: number;
  sector: string;
}

export interface PortfolioMetrics {
  totalValue: number;
  dailyChange: number;
  dailyChangePercent: number;
  diversificationScore: number;
  liquidityRatio: number;
  sentimentScore: number;
  riskLevel: "Low" | "Moderate" | "High";
}

export interface AgentStep {
  name: string;
  status: "completed" | "running" | "pending";
  summary: string;
}

export interface Recommendation {
  id: string;
  title: string;
  confidence: number;
  rationale: string;
  actions: string[];
  risks: string[];
  warnings: string[];
  guardrailStatus: "passed" | "flagged" | "blocked";
  guardrailNotes: string;
  timestamp: string;
  agentPipeline: AgentStep[];
}

export interface NewsItem {
  id: string;
  headline: string;
  source: string;
  timestamp: string;
  sentiment: "positive" | "negative" | "neutral";
  relevance: number;
  tickers: string[];
}

export interface DashboardView {
  metrics: PortfolioMetrics;
  holdings: Holding[];
  recommendations: Recommendation[];
  news: NewsItem[];
}
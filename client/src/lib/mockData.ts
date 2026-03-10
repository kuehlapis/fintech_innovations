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

export const mockMetrics: PortfolioMetrics = {
  totalValue: 1_284_730.42,
  dailyChange: 12_847.30,
  dailyChangePercent: 1.01,
  diversificationScore: 78,
  liquidityRatio: 0.64,
  sentimentScore: 0.72,
  riskLevel: "Moderate",
};

export const mockHoldings: Holding[] = [
  { ticker: "AAPL", name: "Apple Inc.", weight: 18.2, value: 233_900, change24h: 1.34, sector: "Technology" },
  { ticker: "MSFT", name: "Microsoft Corp.", weight: 15.6, value: 200_418, change24h: 0.87, sector: "Technology" },
  { ticker: "JNJ", name: "Johnson & Johnson", weight: 10.1, value: 129_758, change24h: -0.42, sector: "Healthcare" },
  { ticker: "JPM", name: "JPMorgan Chase", weight: 9.8, value: 125_903, change24h: 1.12, sector: "Financials" },
  { ticker: "PG", name: "Procter & Gamble", weight: 8.4, value: 107_917, change24h: 0.28, sector: "Consumer Staples" },
  { ticker: "AMZN", name: "Amazon.com", weight: 12.3, value: 158_022, change24h: 2.10, sector: "Technology" },
  { ticker: "XOM", name: "Exxon Mobil", weight: 7.2, value: 92_501, change24h: -0.91, sector: "Energy" },
  { ticker: "BND", name: "Vanguard Total Bond", weight: 11.4, value: 146_459, change24h: 0.05, sector: "Fixed Income" },
  { ticker: "GLD", name: "SPDR Gold Shares", weight: 4.1, value: 52_674, change24h: 0.63, sector: "Commodities" },
  { ticker: "VWO", name: "Vanguard FTSE EM", weight: 2.9, value: 37_257, change24h: -1.20, sector: "Emerging Markets" },
];

export const mockRecommendations: Recommendation[] = [
  {
    id: "rec-001",
    title: "Rebalance Technology Overweight",
    confidence: 0.87,
    rationale: "Technology sector allocation at 46.1% exceeds target of 35%. Recent earnings revisions and elevated P/E ratios suggest trimming exposure. Sentiment analysis across 142 news sources confirms increased regulatory risk narrative.",
    actions: [
      "Reduce AAPL allocation by 3.2% over 5-day TWAP",
      "Reduce MSFT allocation by 2.1%",
      "Redirect proceeds to JNJ and BND positions",
    ],
    risks: [
      "Missing continued tech rally if momentum persists",
      "Transaction costs estimated at $340",
      "Tax implications on realized gains (~$4,200 estimated)",
    ],
    warnings: [
      "Q4 earnings season begins in 18 days — consider timing",
      "AAPL has pending product launch event",
    ],
    guardrailStatus: "passed",
    guardrailNotes: "All proposed changes within risk tolerance bands. No concentration limit breaches detected.",
    timestamp: "2026-03-09T14:32:00Z",
    agentPipeline: [
      { name: "Ingestion", status: "completed", summary: "Processed 2,847 data points across 10 holdings" },
      { name: "Sentiment", status: "completed", summary: "Aggregated sentiment from 142 sources; tech sector negative bias detected" },
      { name: "Quantitative", status: "completed", summary: "Mean-variance optimization suggests tech trim of 5.3%" },
      { name: "Advisory", status: "completed", summary: "Generated rebalance recommendation with 87% confidence" },
      { name: "Guardrail", status: "completed", summary: "Passed all 12 compliance checks" },
      { name: "Decision", status: "completed", summary: "Final recommendation approved for review" },
    ],
  },
  {
    id: "rec-002",
    title: "Increase Fixed Income Duration",
    confidence: 0.73,
    rationale: "Yield curve analysis indicates potential rate cuts in next 2 quarters. Extending bond duration from 4.2 to 6.8 years could capture 180bps of price appreciation. Macro sentiment supports defensive positioning.",
    actions: [
      "Shift 40% of BND to VGLT (long-term treasuries)",
      "Add 2% allocation to TLT for duration extension",
    ],
    risks: [
      "Rate cuts may not materialize if inflation persists",
      "Duration extension increases interest rate sensitivity",
    ],
    warnings: [
      "Fed meeting in 12 days — wait for guidance before executing",
    ],
    guardrailStatus: "flagged",
    guardrailNotes: "Duration extension exceeds soft limit of 6.0 years. Manual review recommended.",
    timestamp: "2026-03-09T13:15:00Z",
    agentPipeline: [
      { name: "Ingestion", status: "completed", summary: "Analyzed yield curves and rate expectations" },
      { name: "Sentiment", status: "completed", summary: "Dovish Fed commentary detected across 89 sources" },
      { name: "Quantitative", status: "completed", summary: "Duration optimization model suggests 6.8yr target" },
      { name: "Advisory", status: "completed", summary: "Generated duration extension recommendation" },
      { name: "Guardrail", status: "completed", summary: "Soft limit flagged — duration exceeds 6.0yr threshold" },
      { name: "Decision", status: "completed", summary: "Recommendation flagged for manual review" },
    ],
  },
];

export const mockNews: NewsItem[] = [
  { id: "n1", headline: "Apple reportedly in talks for AI chip partnership with TSMC", source: "Reuters", timestamp: "2026-03-09T12:45:00Z", sentiment: "positive", relevance: 0.94, tickers: ["AAPL"] },
  { id: "n2", headline: "Fed officials signal patience on rate decisions amid mixed data", source: "WSJ", timestamp: "2026-03-09T11:30:00Z", sentiment: "neutral", relevance: 0.88, tickers: ["BND"] },
  { id: "n3", headline: "ExxonMobil faces new EPA regulations on refinery emissions", source: "Bloomberg", timestamp: "2026-03-09T10:15:00Z", sentiment: "negative", relevance: 0.82, tickers: ["XOM"] },
  { id: "n4", headline: "Amazon Web Services expands data center footprint in Asia", source: "TechCrunch", timestamp: "2026-03-09T09:00:00Z", sentiment: "positive", relevance: 0.79, tickers: ["AMZN"] },
  { id: "n5", headline: "JPMorgan raises dividend forecast amid strong Q1 outlook", source: "CNBC", timestamp: "2026-03-09T08:20:00Z", sentiment: "positive", relevance: 0.85, tickers: ["JPM"] },
  { id: "n6", headline: "Global gold demand hits record as central banks diversify", source: "FT", timestamp: "2026-03-09T07:45:00Z", sentiment: "positive", relevance: 0.71, tickers: ["GLD"] },
  { id: "n7", headline: "Emerging market currencies under pressure from dollar strength", source: "Reuters", timestamp: "2026-03-08T22:00:00Z", sentiment: "negative", relevance: 0.76, tickers: ["VWO"] },
  { id: "n8", headline: "Microsoft Azure revenue growth accelerates in cloud services", source: "Bloomberg", timestamp: "2026-03-08T20:30:00Z", sentiment: "positive", relevance: 0.91, tickers: ["MSFT"] },
];

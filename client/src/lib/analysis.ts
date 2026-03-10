// client/src/lib/analysis.ts
import { getStoredGuestHoldings } from "@/lib/storage";
import type {
  DashboardView,
  FinalAgentDecision,
  Holding,
  IngestionRequestPayload,
  NewsItem,
  Recommendation,
} from "@/lib/types";

export function buildAnalyzePayload(userId: string, query: string): IngestionRequestPayload {
  const isGuest = userId === "guest";
  const guest = isGuest ? getStoredGuestHoldings() : [];

  return {
    user_id: userId || undefined,
    raw_text: query ?? "",
    holdings: guest.map((h) => ({
      ticker: h.ticker,
      quantity: h.quantity,
      asset_type: "equity",
    })),
    news_headlines: [],
  };
}

function riskFromHHI(hhi: number): "Low" | "Moderate" | "High" {
  if (hhi >= 0.25) return "High";
  if (hhi >= 0.15) return "Moderate";
  return "Low";
}

function guardrailStatus(decision: FinalAgentDecision): "passed" | "flagged" | "blocked" {
  if (!decision.guardrail.approved) return "blocked";
  return decision.guardrail.issues.length > 0 ? "flagged" : "passed";
}

export function buildDashboardData(decision: FinalAgentDecision): DashboardView {
  const weights = decision.quant.asset_weights ?? {};
  const prices = decision.ingestion.prices ?? {};
  const ingestionHoldings = decision.ingestion.holdings ?? [];

  const holdings: Holding[] = ingestionHoldings.map((h) => {
    const ticker = h.ticker ?? "N/A";
    const price = prices[ticker] ?? 0;
    const value = (h.quantity ?? 0) * price;
    const weight = (weights[ticker] ?? 0) * 100;
    const assetType = (h.asset_type ?? h.asset_class ?? "other").toString();

    return {
      ticker,
      name: ticker,
      weight: Number(weight.toFixed(2)),
      value,
      change24h: 0,
      sector: assetType.toUpperCase(),
    };
  });

  const recommendation: Recommendation = {
    id: decision.request_id || "rec-latest",
    title: decision.advisory.summary || "Portfolio recommendation",
    confidence: Math.max(0, Math.min(1, decision.advisory.confidence ?? 0)),
    rationale: decision.advisory.rationale || decision.advisory.summary || "",
    actions: decision.advisory.actions ?? [],
    risks: decision.advisory.risks ?? [],
    warnings: decision.advisory.warnings ?? [],
    guardrailStatus: guardrailStatus(decision),
    guardrailNotes:
      decision.guardrail.issues?.map((i) => i.message).join(" | ") ||
      "No guardrail issues reported.",
    timestamp: new Date().toISOString(),
    agentPipeline: [
      { name: "Ingestion", status: "completed", summary: "Portfolio and context normalized." },
      { name: "Sentiment", status: "completed", summary: "Sentiment scoring complete." },
      { name: "Quantitative", status: "completed", summary: "Portfolio risk/weight metrics computed." },
      { name: "Advisory", status: "completed", summary: "Recommendation generated." },
      { name: "Guardrail", status: "completed", summary: "Policy checks evaluated." },
      { name: "Decision", status: "completed", summary: "Final response returned." },
    ],
  };

  const news: NewsItem[] = (decision.sentiment.news_headlines ?? []).map((headline, idx) => ({
    id: `news-${idx}`,
    headline,
    source: "Pipeline",
    timestamp: new Date().toISOString(),
    sentiment: "neutral",
    relevance: 0.5,
    tickers: decision.ingestion.tickers ?? [],
  }));

  return {
    metrics: {
      totalValue: decision.quant.total_value ?? 0,
      dailyChange: 0,
      dailyChangePercent: 0,
      diversificationScore: decision.quant.diversification_score ?? 0,
      liquidityRatio: decision.quant.liquidity_ratio ?? 0,
      sentimentScore: decision.sentiment.sentiment_score ?? 0,
      riskLevel: riskFromHHI(decision.quant.hhi ?? 0),
    },
    holdings,
    recommendations: [recommendation],
    news,
  };
}
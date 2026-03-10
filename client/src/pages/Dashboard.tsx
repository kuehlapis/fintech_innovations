import { motion } from "framer-motion";
import { DollarSign, BarChart3, Droplets, Brain, Activity, Loader2, PlayCircle } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import MetricCard from "@/components/MetricCard";
import RecommendationCard from "@/components/RecommendationCard";
import NewsCard from "@/components/NewsCard";
import { analyzePortfolio } from "@/lib/api";
import { buildAnalyzePayload, buildDashboardData } from "@/lib/analysis";
import { getStoredUserId } from "@/lib/storage";

export default function Dashboard() {
  const fmt = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
  const userId = getStoredUserId();

  const { data, isError, isFetching, refetch } = useQuery({
    queryKey: ["analysis", userId],
    queryFn: () => analyzePortfolio(buildAnalyzePayload(userId, "")),
    enabled: false,
    staleTime: Infinity,
  });

  const view = data ? buildDashboardData(data) : null;

  return (
    <div className="space-y-8">
      {!userId && (
        <div className="rounded-xl border border-border bg-card p-4 text-sm text-muted-foreground">
          Set a user id on the Analysis page to load live portfolio data.
        </div>
      )}

      {/* Analyse trigger */}
      {userId && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="rounded-xl border border-border bg-card p-4 flex flex-col sm:flex-row sm:items-center gap-3"
        >
          <div className="flex-1">
            <p className="text-sm font-medium text-card-foreground">Analyse Portfolio</p>
            <p className="text-xs text-muted-foreground mt-0.5">
              Runs the full agent pipeline — ingestion, equity, crypto, real estate, quant, sentiment, advisory, and
              guardrail. Each agent calls the Gemini API in sequence. Only press when you want a fresh analysis.
            </p>
          </div>
          <button
            type="button"
            onClick={() => refetch()}
            disabled={isFetching || !userId}
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
          >
            {isFetching ? <Loader2 className="h-4 w-4 animate-spin" /> : <PlayCircle className="h-4 w-4" />}
            {isFetching ? "Running agents…" : "Run Analysis"}
          </button>
        </motion.div>
      )}
      {/* Hero section */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative overflow-hidden rounded-2xl border border-border bg-card p-6 md:p-10"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5" />
        <div className="relative">
          <p className="text-sm font-medium uppercase tracking-wider text-muted-foreground">Portfolio Value</p>
          <h1 className="mt-2 font-display text-4xl md:text-5xl font-bold tracking-tight text-card-foreground">
            {fmt.format(view?.metrics.totalValue ?? 0)}
          </h1>
          <div className="mt-3 flex items-center gap-2">
            <span className="inline-flex items-center gap-1 rounded-full bg-chart-positive/10 px-3 py-1 text-sm font-semibold text-chart-positive">
              <Activity className="h-3.5 w-3.5" />
              +{fmt.format(view?.metrics.dailyChange ?? 0)} ({view?.metrics.dailyChangePercent ?? 0}%)
            </span>
            <span className="text-sm text-muted-foreground">today</span>
          </div>
          <div className="mt-4 flex items-center gap-2">
            <span className="rounded-full bg-secondary px-3 py-1 text-xs font-medium text-secondary-foreground">
              {view?.metrics.riskLevel ?? "Unknown"} Risk
            </span>
            <span className="text-xs text-muted-foreground">
              {(view?.recommendations.length ?? 0)} pending recommendations
            </span>
          </div>
        </div>
      </motion.section>

      {/* Metrics grid */}
      <section>
        <h2 className="font-display text-lg font-semibold text-foreground mb-4">Key Metrics</h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            label="Total Value"
            value={fmt.format(view?.metrics.totalValue ?? 0)}
            change={`+${view?.metrics.dailyChangePercent ?? 0}%`}
            changeType="positive"
            icon={<DollarSign className="h-4 w-4" />}
            delay={0}
          />
          <MetricCard
            label="Diversification"
            value={`${view?.metrics.diversificationScore ?? 0}/100`}
            changeType="neutral"
            icon={<BarChart3 className="h-4 w-4" />}
            delay={0.08}
          />
          <MetricCard
            label="Liquidity Ratio"
            value={`${((view?.metrics.liquidityRatio ?? 0) * 100).toFixed(0)}%`}
            changeType="neutral"
            icon={<Droplets className="h-4 w-4" />}
            delay={0.16}
          />
          <MetricCard
            label="Sentiment Score"
            value={(view?.metrics.sentimentScore ?? 0).toFixed(2)}
            change="Moderately positive"
            changeType="positive"
            icon={<Brain className="h-4 w-4" />}
            delay={0.24}
          />
        </div>
      </section>

      {/* Two-column: Recommendations + News */}
      <div className="grid lg:grid-cols-5 gap-8">
        <section className="lg:col-span-3">
          <h2 className="font-display text-lg font-semibold text-foreground mb-4">Recommendations</h2>
          <div className="space-y-4">
            {isFetching && (
              <p className="text-sm text-muted-foreground">Running agent pipeline…</p>
            )}
            {isError && (
              <p className="text-sm text-destructive">Unable to load recommendations.</p>
            )}
            {view?.recommendations.map((rec, i) => (
              <RecommendationCard key={rec.id} rec={rec} index={i} />
            ))}
            {!isFetching && !isError && !view && (
              <p className="text-sm text-muted-foreground">
                No analysis yet. Press "Run Analysis" above to generate recommendations.
              </p>
            )}
            {!isFetching && !isError && view?.recommendations.length === 0 && (
              <p className="text-sm text-muted-foreground">No recommendations available.</p>
            )}
          </div>
        </section>

        <section className="lg:col-span-2">
          <h2 className="font-display text-lg font-semibold text-foreground mb-4">Market Sentiment</h2>
          <div className="space-y-3">
            {(view?.news ?? []).slice(0, 5).map((item, i) => (
              <NewsCard key={item.id} item={item} index={i} />
            ))}
            {!isFetching && view?.news.length === 0 && (
              <p className="text-sm text-muted-foreground">No news available.</p>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}

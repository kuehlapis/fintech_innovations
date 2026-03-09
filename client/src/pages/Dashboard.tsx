import { motion } from "framer-motion";
import { DollarSign, BarChart3, Droplets, Brain, Activity } from "lucide-react";
import MetricCard from "@/components/MetricCard";
import RecommendationCard from "@/components/RecommendationCard";
import NewsCard from "@/components/NewsCard";
import { mockMetrics, mockRecommendations, mockNews } from "@/lib/mockData";

export default function Dashboard() {
  const fmt = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

  return (
    <div className="space-y-8">
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
            {fmt.format(mockMetrics.totalValue)}
          </h1>
          <div className="mt-3 flex items-center gap-2">
            <span className="inline-flex items-center gap-1 rounded-full bg-chart-positive/10 px-3 py-1 text-sm font-semibold text-chart-positive">
              <Activity className="h-3.5 w-3.5" />
              +{fmt.format(mockMetrics.dailyChange)} ({mockMetrics.dailyChangePercent}%)
            </span>
            <span className="text-sm text-muted-foreground">today</span>
          </div>
          <div className="mt-4 flex items-center gap-2">
            <span className="rounded-full bg-secondary px-3 py-1 text-xs font-medium text-secondary-foreground">
              {mockMetrics.riskLevel} Risk
            </span>
            <span className="text-xs text-muted-foreground">
              {mockRecommendations.length} pending recommendations
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
            value={fmt.format(mockMetrics.totalValue)}
            change={`+${mockMetrics.dailyChangePercent}%`}
            changeType="positive"
            icon={<DollarSign className="h-4 w-4" />}
            delay={0}
          />
          <MetricCard
            label="Diversification"
            value={`${mockMetrics.diversificationScore}/100`}
            changeType="neutral"
            icon={<BarChart3 className="h-4 w-4" />}
            delay={0.08}
          />
          <MetricCard
            label="Liquidity Ratio"
            value={`${(mockMetrics.liquidityRatio * 100).toFixed(0)}%`}
            changeType="neutral"
            icon={<Droplets className="h-4 w-4" />}
            delay={0.16}
          />
          <MetricCard
            label="Sentiment Score"
            value={mockMetrics.sentimentScore.toFixed(2)}
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
            {mockRecommendations.map((rec, i) => (
              <RecommendationCard key={rec.id} rec={rec} index={i} />
            ))}
          </div>
        </section>

        <section className="lg:col-span-2">
          <h2 className="font-display text-lg font-semibold text-foreground mb-4">Market Sentiment</h2>
          <div className="space-y-3">
            {mockNews.slice(0, 5).map((item, i) => (
              <NewsCard key={item.id} item={item} index={i} />
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

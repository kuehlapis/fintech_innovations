import { motion } from "framer-motion";
import { Brain, TrendingUp, TrendingDown, Minus } from "lucide-react";
import NewsCard from "@/components/NewsCard";
import { mockNews, mockMetrics } from "@/lib/mockData";

export default function Sentiment() {
  const positive = mockNews.filter((n) => n.sentiment === "positive").length;
  const negative = mockNews.filter((n) => n.sentiment === "negative").length;
  const neutral = mockNews.filter((n) => n.sentiment === "neutral").length;

  return (
    <div className="space-y-8">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <h1 className="font-display text-3xl font-bold text-foreground">Sentiment & News</h1>
        <p className="mt-1 text-sm text-muted-foreground">Real-time sentiment from the agent ingestion pipeline</p>
      </motion.div>

      {/* Sentiment overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}
          className="rounded-xl border border-border bg-card p-5"
        >
          <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
            <Brain className="h-4 w-4" /> Composite
          </div>
          <p className="mt-2 font-display text-2xl font-bold text-card-foreground">{mockMetrics.sentimentScore.toFixed(2)}</p>
          <p className="mt-1 text-xs text-chart-positive font-medium">Moderately positive</p>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="rounded-xl border border-border bg-card p-5"
        >
          <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
            <TrendingUp className="h-4 w-4 text-chart-positive" /> Positive
          </div>
          <p className="mt-2 font-display text-2xl font-bold text-chart-positive">{positive}</p>
          <p className="mt-1 text-xs text-muted-foreground">headlines</p>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
          className="rounded-xl border border-border bg-card p-5"
        >
          <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
            <TrendingDown className="h-4 w-4 text-chart-negative" /> Negative
          </div>
          <p className="mt-2 font-display text-2xl font-bold text-chart-negative">{negative}</p>
          <p className="mt-1 text-xs text-muted-foreground">headlines</p>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          className="rounded-xl border border-border bg-card p-5"
        >
          <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
            <Minus className="h-4 w-4 text-chart-neutral" /> Neutral
          </div>
          <p className="mt-2 font-display text-2xl font-bold text-chart-neutral">{neutral}</p>
          <p className="mt-1 text-xs text-muted-foreground">headlines</p>
        </motion.div>
      </div>

      {/* News feed */}
      <section>
        <h2 className="font-display text-lg font-semibold text-foreground mb-4">Latest Headlines</h2>
        <div className="space-y-3">
          {mockNews.map((item, i) => (
            <NewsCard key={item.id} item={item} index={i} />
          ))}
        </div>
      </section>
    </div>
  );
}

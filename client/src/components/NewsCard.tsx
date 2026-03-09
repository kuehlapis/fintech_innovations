import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import type { NewsItem } from "@/lib/mockData";

interface NewsCardProps {
  item: NewsItem;
  index: number;
}

export default function NewsCard({ item, index }: NewsCardProps) {
  const sentimentIcon =
    item.sentiment === "positive" ? <TrendingUp className="h-3.5 w-3.5" /> :
    item.sentiment === "negative" ? <TrendingDown className="h-3.5 w-3.5" /> :
    <Minus className="h-3.5 w-3.5" />;

  const sentimentColor =
    item.sentiment === "positive" ? "text-chart-positive bg-chart-positive/10" :
    item.sentiment === "negative" ? "text-chart-negative bg-chart-negative/10" :
    "text-chart-neutral bg-chart-neutral/10";

  const timeAgo = getTimeAgo(item.timestamp);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.06 }}
      className="flex items-start gap-3 rounded-lg border border-border bg-card p-4 hover:border-primary/20 transition-colors"
    >
      <div className={`mt-0.5 flex items-center gap-1 rounded-full px-2 py-1 text-xs font-medium shrink-0 ${sentimentColor}`}>
        {sentimentIcon}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-card-foreground leading-snug">{item.headline}</p>
        <div className="mt-1.5 flex items-center gap-2 text-xs text-muted-foreground">
          <span>{item.source}</span>
          <span>·</span>
          <span>{timeAgo}</span>
          <span>·</span>
          <span className="font-medium text-primary">{item.tickers.join(", ")}</span>
        </div>
      </div>
    </motion.div>
  );
}

function getTimeAgo(timestamp: string): string {
  const diff = Date.now() - new Date(timestamp).getTime();
  const hours = Math.floor(diff / 3_600_000);
  if (hours < 1) return "Just now";
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

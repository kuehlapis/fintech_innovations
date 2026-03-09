import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import type { ReactNode } from "react";

interface MetricCardProps {
  label: string;
  value: string;
  change?: string;
  changeType?: "positive" | "negative" | "neutral";
  icon?: ReactNode;
  delay?: number;
}

export default function MetricCard({ label, value, change, changeType = "neutral", icon, delay = 0 }: MetricCardProps) {
  const changeIcon =
    changeType === "positive" ? <TrendingUp className="h-3.5 w-3.5" /> :
    changeType === "negative" ? <TrendingDown className="h-3.5 w-3.5" /> :
    <Minus className="h-3.5 w-3.5" />;

  const changeColor =
    changeType === "positive" ? "text-chart-positive" :
    changeType === "negative" ? "text-chart-negative" :
    "text-chart-neutral";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: "easeOut" }}
      className="rounded-xl border border-border bg-card p-5 card-shine"
    >
      <div className="flex items-start justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
          {label}
        </span>
        {icon && <span className="text-muted-foreground">{icon}</span>}
      </div>
      <div className="mt-3">
        <span className="font-display text-2xl font-bold text-card-foreground">{value}</span>
      </div>
      {change && (
        <div className={`mt-2 flex items-center gap-1 text-sm font-medium ${changeColor}`}>
          {changeIcon}
          <span>{change}</span>
        </div>
      )}
    </motion.div>
  );
}

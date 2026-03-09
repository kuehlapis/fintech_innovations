import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Shield, ShieldAlert, ShieldX, ChevronRight } from "lucide-react";
import type { Recommendation } from "@/lib/mockData";

interface RecommendationCardProps {
  rec: Recommendation;
  index: number;
}

export default function RecommendationCard({ rec, index }: RecommendationCardProps) {
  const guardrailIcon =
    rec.guardrailStatus === "passed" ? <Shield className="h-4 w-4 text-chart-positive" /> :
    rec.guardrailStatus === "flagged" ? <ShieldAlert className="h-4 w-4 text-accent" /> :
    <ShieldX className="h-4 w-4 text-destructive" />;

  const guardrailLabel =
    rec.guardrailStatus === "passed" ? "Guardrails Passed" :
    rec.guardrailStatus === "flagged" ? "Flagged for Review" :
    "Blocked";

  const guardrailBg =
    rec.guardrailStatus === "passed" ? "bg-chart-positive/10 text-chart-positive" :
    rec.guardrailStatus === "flagged" ? "bg-accent/10 text-accent" :
    "bg-destructive/10 text-destructive";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 * index, ease: "easeOut" }}
    >
      <Link
        to={`/recommendation/${rec.id}`}
        className="group block rounded-xl border border-border bg-card p-5 transition-all hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5 card-shine"
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <h3 className="font-display text-lg font-semibold text-card-foreground group-hover:text-primary transition-colors">
              {rec.title}
            </h3>
            <p className="mt-2 text-sm text-muted-foreground line-clamp-2">{rec.rationale}</p>
          </div>
          <ChevronRight className="h-5 w-5 shrink-0 text-muted-foreground group-hover:text-primary transition-colors mt-1" />
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1.5 rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
            {Math.round(rec.confidence * 100)}% confidence
          </div>
          <div className={`flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${guardrailBg}`}>
            {guardrailIcon}
            {guardrailLabel}
          </div>
          <span className="text-xs text-muted-foreground">
            {rec.actions.length} action{rec.actions.length !== 1 ? "s" : ""} · {rec.risks.length} risk{rec.risks.length !== 1 ? "s" : ""}
          </span>
        </div>
      </Link>
    </motion.div>
  );
}

import { useParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Shield, ShieldAlert, ShieldX, AlertTriangle, CheckCircle2, Target, Zap } from "lucide-react";
import AgentPipeline from "@/components/AgentPipeline";
import { mockRecommendations } from "@/lib/mockData";

export default function RecommendationDetail() {
  const { id } = useParams<{ id: string }>();
  const rec = mockRecommendations.find((r) => r.id === id);

  if (!rec) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <p className="text-muted-foreground">Recommendation not found.</p>
        <Link to="/" className="mt-4 text-sm text-primary hover:underline">← Back to Dashboard</Link>
      </div>
    );
  }

  const guardrailIcon =
    rec.guardrailStatus === "passed" ? <Shield className="h-5 w-5 text-chart-positive" /> :
    rec.guardrailStatus === "flagged" ? <ShieldAlert className="h-5 w-5 text-accent" /> :
    <ShieldX className="h-5 w-5 text-destructive" />;

  const guardrailBg =
    rec.guardrailStatus === "passed" ? "border-chart-positive/30 bg-chart-positive/5" :
    rec.guardrailStatus === "flagged" ? "border-accent/30 bg-accent/5" :
    "border-destructive/30 bg-destructive/5";

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <Link to="/" className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
        <ArrowLeft className="h-4 w-4" /> Back to Dashboard
      </Link>

      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <h1 className="font-display text-3xl font-bold text-foreground">{rec.title}</h1>
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <span className="rounded-full bg-primary/10 px-3 py-1 text-sm font-semibold text-primary">
            {Math.round(rec.confidence * 100)}% confidence
          </span>
          <span className="text-sm text-muted-foreground">
            {new Date(rec.timestamp).toLocaleString()}
          </span>
        </div>
      </motion.div>

      {/* Rationale */}
      <motion.section initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1, duration: 0.5 }}
        className="rounded-xl border border-border bg-card p-6"
      >
        <h2 className="font-display text-base font-semibold text-card-foreground mb-3">Rationale</h2>
        <p className="text-sm text-muted-foreground leading-relaxed">{rec.rationale}</p>
      </motion.section>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Actions */}
        <motion.section initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15, duration: 0.5 }}
          className="rounded-xl border border-border bg-card p-6"
        >
          <h2 className="font-display text-base font-semibold text-card-foreground mb-3 flex items-center gap-2">
            <Target className="h-4 w-4 text-primary" /> Recommended Actions
          </h2>
          <ul className="space-y-2">
            {rec.actions.map((a, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                <CheckCircle2 className="h-4 w-4 shrink-0 text-primary mt-0.5" />
                {a}
              </li>
            ))}
          </ul>
        </motion.section>

        {/* Risks */}
        <motion.section initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2, duration: 0.5 }}
          className="rounded-xl border border-border bg-card p-6"
        >
          <h2 className="font-display text-base font-semibold text-card-foreground mb-3 flex items-center gap-2">
            <Zap className="h-4 w-4 text-chart-negative" /> Risks
          </h2>
          <ul className="space-y-2">
            {rec.risks.map((r, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                <span className="h-1.5 w-1.5 rounded-full bg-chart-negative mt-2 shrink-0" />
                {r}
              </li>
            ))}
          </ul>
        </motion.section>
      </div>

      {/* Warnings */}
      {rec.warnings.length > 0 && (
        <motion.section initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25, duration: 0.5 }}
          className="rounded-xl border border-accent/30 bg-accent/5 p-6"
        >
          <h2 className="font-display text-base font-semibold text-accent-foreground mb-3 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-accent" /> Warnings
          </h2>
          <ul className="space-y-2">
            {rec.warnings.map((w, i) => (
              <li key={i} className="text-sm text-muted-foreground">{w}</li>
            ))}
          </ul>
        </motion.section>
      )}

      {/* Guardrail Status */}
      <motion.section initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3, duration: 0.5 }}
        className={`rounded-xl border p-6 ${guardrailBg}`}
      >
        <h2 className="font-display text-base font-semibold text-card-foreground mb-2 flex items-center gap-2">
          {guardrailIcon} Guardrail Status: <span className="capitalize">{rec.guardrailStatus}</span>
        </h2>
        <p className="text-sm text-muted-foreground">{rec.guardrailNotes}</p>
      </motion.section>

      {/* Agent Pipeline */}
      <motion.section initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35, duration: 0.5 }}
        className="rounded-xl border border-border bg-card p-6"
      >
        <h2 className="font-display text-base font-semibold text-card-foreground mb-4">Agent Pipeline</h2>
        <AgentPipeline steps={rec.agentPipeline} />
      </motion.section>
    </div>
  );
}

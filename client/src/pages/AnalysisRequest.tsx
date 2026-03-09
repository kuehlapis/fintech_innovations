import { useState } from "react";
import { motion } from "framer-motion";
import { Send, Loader2, FileSearch } from "lucide-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { analyzePortfolio } from "@/lib/api";
import { buildAnalyzePayload } from "@/lib/analysis";
import { getStoredUserId } from "@/lib/storage";

export default function AnalysisRequest() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const userId = getStoredUserId();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (payload: { userId: string; query: string }) =>
      analyzePortfolio(buildAnalyzePayload(payload.userId, payload.query)),
    onSuccess: (data) => {
      queryClient.setQueryData(["analysis", userId], data);
      setSubmitted(true);
      navigate(`/recommendation/${data.request_id}`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || !userId.trim()) return;
    setLoading(true);
    mutation.mutate({ userId: userId.trim(), query: query.trim() }, {
      onSettled: () => setLoading(false),
    });
  };

  const presets = [
    "Rebalance my portfolio for lower risk exposure",
    "Analyze sentiment impact on tech holdings",
    "Evaluate fixed income duration strategy",
    "Run full pipeline on emerging market positions",
  ];

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <h1 className="font-display text-3xl font-bold text-foreground">Request Analysis</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Submit a query to the agent pipeline for portfolio analysis and advisory recommendations.
        </p>
      </motion.div>

      <motion.form
        onSubmit={handleSubmit}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.5 }}
        className="rounded-xl border border-border bg-card p-6 space-y-4"
      >
        <label className="block">
          <span className="text-sm font-medium text-card-foreground">Analysis Query</span>
          <textarea
            value={query}
            onChange={(e) => { setQuery(e.target.value); setSubmitted(false); }}
            rows={4}
            placeholder="Describe what you'd like the agent pipeline to analyze..."
            className="mt-2 w-full rounded-lg border border-input bg-background px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring resize-none"
          />
        </label>

        <div>
          <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Quick prompts</span>
          <div className="mt-2 flex flex-wrap gap-2">
            {presets.map((p) => (
              <button
                key={p}
                type="button"
                onClick={() => { setQuery(p); setSubmitted(false); }}
                className="rounded-full border border-border bg-muted px-3 py-1.5 text-xs text-muted-foreground hover:text-foreground hover:border-primary/30 transition-colors"
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        <button
          type="submit"
          disabled={!query.trim() || !userId.trim() || loading}
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          {loading ? "Processing…" : "Submit to Pipeline"}
        </button>

        {mutation.isError && (
          <p className="text-sm text-destructive">Unable to submit analysis request.</p>
        )}
      </motion.form>

      {submitted && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="rounded-xl border border-chart-positive/30 bg-chart-positive/5 p-6 text-center"
        >
          <FileSearch className="h-8 w-8 text-chart-positive mx-auto mb-3" />
          <h3 className="font-display text-lg font-semibold text-card-foreground">Analysis Submitted</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Your query has been sent to the agent pipeline. Results will appear in the Dashboard recommendations.
          </p>
        </motion.div>
      )}
    </div>
  );
}

import * as React from "react";
import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Minus, Loader2, PlayCircle } from "lucide-react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { addHolding, analyzePortfolio } from "@/lib/api";
import { buildAnalyzePayload, buildDashboardData } from "@/lib/analysis";
import { addStoredGuestHolding, getStoredGuestHoldings, getStoredUserId } from "@/lib/storage";

export default function Holdings() {
  const fmt = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
  const userId = getStoredUserId();
  const [ticker, setTicker] = React.useState("");
  const [quantity, setQuantity] = React.useState("");
  const [submitMessage, setSubmitMessage] = React.useState("");

  const { data, isFetching, refetch } = useQuery({
    queryKey: ["analysis", userId],
    queryFn: () => analyzePortfolio(buildAnalyzePayload(userId, "")),
    enabled: false,
    staleTime: Infinity,
  });

  const addMutation = useMutation({
    mutationFn: async () => {
      const symbol = ticker.trim().toUpperCase();
      const qty = Number(quantity);
      if (userId === "guest") {
        addStoredGuestHolding(symbol, qty);
        return { ok: true };
      }
      return addHolding(userId, symbol, qty);
    },
    onSuccess: () => {
      setSubmitMessage("Holding added. Press \"Analyse Holdings\" to update your analysis.");
      setTicker("");
      setQuantity("");
    },
    onError: () => setSubmitMessage("Unable to add holding."),
  });

  const view = data ? buildDashboardData(data) : null;
  const guestHoldings = userId === "guest" ? getStoredGuestHoldings() : [];
  const sorted = [...(view?.holdings ?? [])].sort((a, b) => b.weight - a.weight);
  const sectors = sorted.reduce<Record<string, number>>((acc, h) => {
    acc[h.sector] = (acc[h.sector] || 0) + h.weight;
    return acc;
  }, {});

  return (
    <div className="space-y-8">
      {!userId && (
        <div className="rounded-xl border border-border bg-card p-4 text-sm text-muted-foreground">
          Set a user id on the Analysis page to load holdings.
        </div>
      )}

      {userId && (
        <motion.section
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="rounded-xl border border-border bg-card p-6 space-y-4"
        >
          <div>
            <h2 className="font-display text-base font-semibold text-card-foreground">Add Holding</h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              Add your holdings here. When you are ready, press "Analyse Holdings" to run the agent pipeline on your
              current portfolio.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            <label className="block">
              <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Ticker</span>
              <input
                value={ticker}
                onChange={(e) => setTicker(e.target.value)}
                placeholder="AAPL"
                className="mt-2 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground"
              />
            </label>
            <label className="block">
              <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Quantity</span>
              <input
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                placeholder="10"
                type="number"
                className="mt-2 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground"
              />
            </label>
            <div className="flex items-end">
              <button
                type="button"
                onClick={() => addMutation.mutate()}
                disabled={!ticker.trim() || !quantity.trim() || addMutation.isPending}
                className="w-full rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground disabled:opacity-50"
              >
                {addMutation.isPending ? "Adding…" : "Add Holding"}
              </button>
            </div>
          </div>
          {submitMessage && (
            <p className="text-sm text-muted-foreground">{submitMessage}</p>
          )}
          <div className="pt-1 border-t border-border flex items-center gap-3">
            <button
              type="button"
              onClick={() => refetch()}
              disabled={isFetching}
              className="inline-flex items-center gap-2 rounded-lg bg-secondary px-4 py-2 text-sm font-semibold text-secondary-foreground hover:bg-secondary/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isFetching ? <Loader2 className="h-4 w-4 animate-spin" /> : <PlayCircle className="h-4 w-4" />}
              {isFetching ? "Running agents…" : "Analyse Holdings"}
            </button>
            <span className="text-xs text-muted-foreground">
              Calls the full Gemini agent pipeline. Only press once all holdings have been added.
            </span>
          </div>
        </motion.section>
      )}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <h1 className="font-display text-3xl font-bold text-foreground">Holdings & Allocation</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          {sorted.length || guestHoldings.length} positions across {Object.keys(sectors).length} sectors
        </p>
      </motion.div>

      {/* Sector breakdown bar */}
      <motion.section initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1, duration: 0.5 }}
        className="rounded-xl border border-border bg-card p-6"
      >
        <h2 className="font-display text-base font-semibold text-card-foreground mb-4">Sector Allocation</h2>
        <div className="flex rounded-full overflow-hidden h-4">
          {Object.entries(sectors).map(([sector, weight], i) => {
            const colors = [
              "bg-primary", "bg-accent", "bg-chart-positive", "bg-chart-neutral",
              "bg-destructive", "bg-primary/60", "bg-accent/60",
            ];
            return (
              <div
                key={sector}
                className={`${colors[i % colors.length]} transition-all`}
                style={{ width: `${weight}%` }}
                title={`${sector}: ${weight.toFixed(1)}%`}
              />
            );
          })}
        </div>
        <div className="mt-3 flex flex-wrap gap-3">
          {Object.entries(sectors).map(([sector, weight], i) => {
            const dotColors = [
              "bg-primary", "bg-accent", "bg-chart-positive", "bg-chart-neutral",
              "bg-destructive", "bg-primary/60", "bg-accent/60",
            ];
            return (
              <span key={sector} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <span className={`h-2 w-2 rounded-full ${dotColors[i % dotColors.length]}`} />
                {sector} ({weight.toFixed(1)}%)
              </span>
            );
          })}
        </div>
      </motion.section>

      {/* Holdings table */}
      <motion.section initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2, duration: 0.5 }}
        className="rounded-xl border border-border bg-card overflow-hidden"
      >
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border bg-muted/50">
                <th className="text-left px-5 py-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">Ticker</th>
                <th className="text-left px-5 py-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground hidden sm:table-cell">Name</th>
                <th className="text-right px-5 py-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">Weight</th>
                <th className="text-right px-5 py-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground hidden md:table-cell">Value</th>
                <th className="text-right px-5 py-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">24h</th>
                <th className="text-left px-5 py-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground hidden lg:table-cell">Sector</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((h, i) => {
                const changeIcon = h.change24h > 0 ? <TrendingUp className="h-3.5 w-3.5" /> : h.change24h < 0 ? <TrendingDown className="h-3.5 w-3.5" /> : <Minus className="h-3.5 w-3.5" />;
                const changeColor = h.change24h > 0 ? "text-chart-positive" : h.change24h < 0 ? "text-chart-negative" : "text-chart-neutral";
                return (
                  <motion.tr
                    key={h.ticker}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: i * 0.04 }}
                    className="border-b border-border last:border-0 hover:bg-muted/30 transition-colors"
                  >
                    <td className="px-5 py-3.5 font-display font-semibold text-sm text-card-foreground">{h.ticker}</td>
                    <td className="px-5 py-3.5 text-sm text-muted-foreground hidden sm:table-cell">{h.name}</td>
                    <td className="px-5 py-3.5 text-sm text-card-foreground text-right font-medium">
                      <div className="flex items-center justify-end gap-2">
                        <div className="w-16 h-1.5 rounded-full bg-muted overflow-hidden hidden md:block">
                          <div className="h-full rounded-full bg-primary" style={{ width: `${h.weight * 5}%` }} />
                        </div>
                        {h.weight}%
                      </div>
                    </td>
                    <td className="px-5 py-3.5 text-sm text-card-foreground text-right hidden md:table-cell">{fmt.format(h.value)}</td>
                    <td className={`px-5 py-3.5 text-sm text-right font-medium ${changeColor}`}>
                      <span className="inline-flex items-center gap-1">{changeIcon} {h.change24h > 0 ? "+" : ""}{h.change24h}%</span>
                    </td>
                    <td className="px-5 py-3.5 text-sm text-muted-foreground hidden lg:table-cell">{h.sector}</td>
                  </motion.tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </motion.section>
    </div>
  );
}

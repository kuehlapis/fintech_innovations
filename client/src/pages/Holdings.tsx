import { motion } from "framer-motion";
import { mockHoldings } from "@/lib/mockData";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

export default function Holdings() {
  const fmt = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
  const sorted = [...mockHoldings].sort((a, b) => b.weight - a.weight);
  const sectors = sorted.reduce<Record<string, number>>((acc, h) => {
    acc[h.sector] = (acc[h.sector] || 0) + h.weight;
    return acc;
  }, {});

  return (
    <div className="space-y-8">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <h1 className="font-display text-3xl font-bold text-foreground">Holdings & Allocation</h1>
        <p className="mt-1 text-sm text-muted-foreground">{sorted.length} positions across {Object.keys(sectors).length} sectors</p>
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

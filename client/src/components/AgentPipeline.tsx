import { motion } from "framer-motion";
import { CheckCircle2, Loader2, Circle } from "lucide-react";
import type { AgentStep } from "@/lib/types";

interface AgentPipelineProps {
  steps: AgentStep[];
}

export default function AgentPipeline({ steps }: AgentPipelineProps) {
  return (
    <div className="space-y-0">
      {steps.map((step, i) => {
        const icon =
          step.status === "completed" ? <CheckCircle2 className="h-5 w-5 text-chart-positive" /> :
          step.status === "running" ? <Loader2 className="h-5 w-5 text-primary animate-spin" /> :
          <Circle className="h-5 w-5 text-muted-foreground" />;

        return (
          <motion.div
            key={step.name}
            initial={{ opacity: 0, x: -16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: i * 0.08 }}
            className="flex items-start gap-3 relative"
          >
            {/* Connector line */}
            <div className="flex flex-col items-center">
              {icon}
              {i < steps.length - 1 && (
                <div className="w-px h-8 bg-border" />
              )}
            </div>
            <div className="pb-8">
              <span className="text-sm font-semibold text-card-foreground">{step.name}</span>
              <p className="text-xs text-muted-foreground mt-0.5">{step.summary}</p>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}

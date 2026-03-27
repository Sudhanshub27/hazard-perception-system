import { motion } from "framer-motion";
import { TrendingUp, Maximize, Target } from "lucide-react";

interface StatsPanelProps {
  maxRisk: number;
  avgRisk: number;
  totalDetections: number;
}

export default function StatsPanel({ maxRisk, avgRisk, totalDetections }: StatsPanelProps) {
  return (
    <div className="glass-panel p-4 flex flex-col space-y-4">
      <div className="flex items-center space-x-2 border-b border-glassBorder pb-2">
        <Target className="w-4 h-4 text-cyberTeal" />
        <h3 className="text-[10px] uppercase tracking-[0.2em] font-bold text-gray-400">
          Session Metrics
        </h3>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {/* Peak Risk */}
        <div className="flex flex-col">
          <span className="text-[9px] uppercase tracking-wider text-gray-500 mb-1">Peak Threat Level</span>
          <div className="flex items-end space-x-2">
            <span className={`text-2xl font-mono font-bold ${maxRisk > 80 ? 'text-neonRed' : 'text-white'}`}>
              {maxRisk.toFixed(1)}%
            </span>
            <TrendingUp className={`w-4 h-4 mb-1 ${maxRisk > 80 ? 'text-neonRed' : 'text-cyberTeal'}`} />
          </div>
        </div>

        {/* Total Objects Identified */}
        <div className="flex flex-col">
          <span className="text-[9px] uppercase tracking-wider text-gray-500 mb-1">Objects Identified</span>
          <div className="flex items-end space-x-2">
            <span className="text-2xl font-mono font-bold text-white">
              {totalDetections}
            </span>
            <Maximize className="w-4 h-4 mb-1 text-cyberTeal opacity-50" />
          </div>
        </div>

        {/* Status indicator */}
        <div className="pt-2 border-t border-glassBorder mt-1">
          <div className="flex items-center justify-between">
            <span className="text-[9px] uppercase tracking-wider text-gray-500">Processor Latency</span>
            <span className="text-[10px] font-mono text-cyberTeal">Sub-10ms</span>
          </div>
          <div className="w-full h-[2px] bg-glassWhite mt-2 relative overflow-hidden">
             <motion.div 
               animate={{ x: ["-100%", "100%"] }}
               transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
               className="absolute inset-0 w-1/3 bg-cyberTeal"
             />
          </div>
        </div>
      </div>
    </div>
  );
}

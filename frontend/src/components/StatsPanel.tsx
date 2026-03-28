import { memo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { TrendingUp, Maximize, Target, Activity } from "lucide-react";

interface StatsPanelProps {
  maxRisk: number;
  avgRisk: number;
  totalDetections: number;
}

const StatsPanel = memo(({ maxRisk, avgRisk, totalDetections }: StatsPanelProps) => {
  return (
    <div className="glass-panel p-4 flex flex-col space-y-4">
      {/* Onboarding Label Overlay */}
      <div className="flex items-center space-x-2 border-b border-glassBorder pb-2">
        <Activity className="w-3 h-3 text-gray-500" />
        <h3 className="text-[9px] uppercase tracking-[0.2em] font-bold text-gray-500">
          Session Intelligence
        </h3>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {/* Peak Risk */}
        <div className="flex flex-col">
          <span className="text-[9px] uppercase tracking-wider text-gray-500 mb-1">Peak Threat Level</span>
          <div className="flex items-end space-x-2">
            <span className={`text-2xl font-mono font-bold ${maxRisk > 80 ? 'text-neonRed animate-pulse' : 'text-white'}`}>
              {maxRisk.toFixed(1)}%
            </span>
          </div>
        </div>

        {/* Total Objects Identified */}
        <div className="flex flex-col">
          <span className="text-[9px] uppercase tracking-wider text-gray-500 mb-1">Detections Logged</span>
          <div className="flex items-end space-x-2">
            <span className="text-2xl font-mono font-bold text-white">
              {totalDetections}
            </span>
          </div>
        </div>

        {/* Status indicator */}
        <div className="pt-2 border-t border-glassBorder mt-1">
          <div className="flex items-center justify-between">
            <span className="text-[8px] uppercase tracking-wider text-gray-700">Stream Cache Status</span>
            <span className="text-[9px] font-mono text-cyberTeal/50">OK</span>
          </div>
          <div className="w-full h-[2px] bg-glassWhite mt-2 relative overflow-hidden">
             <motion.div 
               animate={{ x: ["-100%", "100%"] }}
               transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
               className="absolute inset-0 w-1/3 bg-cyberTeal/40"
             />
          </div>
        </div>
      </div>
    </div>
  );
});

StatsPanel.displayName = "StatsPanel";
export default StatsPanel;

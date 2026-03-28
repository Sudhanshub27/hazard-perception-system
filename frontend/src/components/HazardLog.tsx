"use client";

import { memo } from "react";
import { AlertCircle, Clock } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

type HazardEvent = {
  id: number;
  timestamp: string;
  risk_score: number;
  highest_threat_class: string;
};

const HazardLog = memo(({ events }: { events: HazardEvent[] }) => {
  return (
    <div className="flex flex-col h-full bg-transparent">
      
      {/* Header */}
      <div className="px-5 py-4 border-b border-borderSubtle flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-textMuted" />
          <span className="text-sm font-semibold tracking-tight text-white">Event Log</span>
        </div>
        <span className="text-xs text-textMuted font-mono">LATEST {events.length}</span>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto px-4 py-2 space-y-2">
        {events.length === 0 ? (
          <div className="flex items-center justify-center h-full text-xs text-textMuted font-medium">
            No active threat events.
          </div>
        ) : (
          <AnimatePresence>
            {events.map((evt) => {
              const isCritical = evt.risk_score >= 80;
              const isDanger = evt.risk_score >= 50 && evt.risk_score < 80;
              const colorBase = isCritical ? 'text-signalDanger' : isDanger ? 'text-alertWarn' : 'text-gray-300';
              const dotColor = isCritical ? 'bg-signalDanger' : isDanger ? 'bg-alertWarn' : 'bg-sysAccent';
              
              return (
                <motion.div 
                  key={evt.id} 
                  layout
                  initial={{ opacity: 0, y: -20, filter: "blur(4px)" }}
                  animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ type: "spring", stiffness: 300, damping: 25 }}
                  className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-2 h-2 rounded-full ${dotColor}`} />
                    <div className="flex flex-col space-y-0.5">
                      <span className={`text-[11px] font-bold uppercase tracking-wider ${colorBase}`}>
                        {evt.highest_threat_class}
                      </span>
                      <div className="flex items-center space-x-1.5 text-textMuted">
                        <Clock className="w-3 h-3" />
                        <span className="text-[10px] font-mono tracking-tight">
                           {new Date(evt.timestamp).toISOString().substring(11, 23)}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex flex-col items-end">
                    <span className={`text-base font-bold tracking-tighter ${colorBase}`}>
                      {evt.risk_score.toFixed(1)}
                    </span>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        )}
      </div>

    </div>
  );
});

HazardLog.displayName = "HazardLog";
export default HazardLog;

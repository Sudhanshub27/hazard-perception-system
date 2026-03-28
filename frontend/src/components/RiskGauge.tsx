"use client";

import { memo } from "react";
import { Zap } from "lucide-react";
import { motion } from "framer-motion";

const RiskGauge = memo(({ score }: { score: number }) => {
  const isDanger = score >= 50;
  const isCritical = score >= 80;

  // Determine elegant startup color based on threshold
  let strokeColor = "rgba(59, 130, 246, 1)"; // sysAccent (Blue)
  if (isCritical) strokeColor = "rgba(239, 68, 68, 1)"; // signalDanger (Red)
  else if (isDanger) strokeColor = "rgba(234, 179, 8, 1)"; // alertWarn (Yellow)

  // Circular math
  const radius = 46;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="w-full h-full p-4 flex items-center justify-between">
      
      {/* Risk Meta Text */}
      <div className="flex flex-col h-full justify-between pr-4 max-w-[50%]">
        <div className="flex items-center space-x-2">
          <Zap className={`w-4 h-4 ${isCritical ? 'text-signalDanger' : 'text-textMuted'}`} />
          <h2 className="text-sm font-semibold tracking-tight text-white">Threat Level</h2>
        </div>
        <div>
          <span className="text-xs text-textMuted uppercase tracking-wider block mb-1">Status</span>
          <span className={`text-lg font-bold tracking-tight
            ${isCritical ? 'text-signalDanger' : isDanger ? 'text-alertWarn' : 'text-sysAccent'}
          `}>
             {isCritical ? "CRITICAL" : isDanger ? "ELEVATED" : "NOMINAL"}
          </span>
        </div>
      </div>

      {/* Spring Animated Gauge Element */}
      <div className="relative flex items-center justify-center shrink-0">
         <svg width="120" height="120" className="-rotate-90">
             {/* Track */}
             <circle 
               cx="60" 
               cy="60" 
               r={radius} 
               stroke="rgba(255,255,255,0.05)" 
               strokeWidth="10" 
               fill="transparent" 
             />
             {/* Animated Progress Arc */}
             <motion.circle 
               cx="60" 
               cy="60" 
               r={radius} 
               stroke={strokeColor} 
               strokeWidth="10" 
               fill="transparent"
               strokeLinecap="round"
               initial={{ strokeDashoffset: circumference }}
               animate={{ strokeDashoffset: strokeDashoffset }}
               transition={{ type: "spring", stiffness: 60, damping: 15 }}
               style={{ strokeDasharray: circumference }}
             />
         </svg>

         {/* Center Number with Spring Roll */}
         <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <motion.span 
               className="text-2xl font-bold text-white tracking-tighter"
               key={Math.round(score)}
               initial={{ y: 5, opacity: 0 }}
               animate={{ y: 0, opacity: 1 }}
               transition={{ type: "spring", stiffness: 300, damping: 25 }}
            >
               {Math.round(score)}
            </motion.span>
         </div>
      </div>
    </div>
  );
});

RiskGauge.displayName = "RiskGauge";
export default RiskGauge;

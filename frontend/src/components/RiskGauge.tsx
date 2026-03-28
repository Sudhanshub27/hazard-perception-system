import { memo } from "react";
import { motion } from "framer-motion";

const RiskGauge = memo(({ score }: { score: number }) => {
  const isCritical = score >= 80;
  const isDanger = score >= 50 && score < 80;
  const strokeColor = isCritical ? "#FF3366" : isDanger ? "#FFCC00" : "#0FF4C6";
  
  // Array of 24 ticks for the circular gauge
  const ticks = Array.from({ length: 24 });

  return (
    <div className="flex flex-col items-center justify-center p-6 glass-panel relative overflow-hidden h-full">
      <div className="absolute top-4 left-4">
        <span className="text-[9px] uppercase tracking-[0.2em] font-bold text-gray-500">Telemetry</span>
      </div>
      
      <div className="relative w-48 h-48 flex items-center justify-center">
        {/* Animated Background Pulse */}
        <motion.div 
          animate={{ scale: isCritical ? [1, 1.2, 1] : 1, opacity: isCritical ? [0.1, 0.3, 0.1] : 0.05 }}
          transition={{ repeat: Infinity, duration: 0.8 }}
          className="absolute inset-0 rounded-full blur-2xl"
          style={{ backgroundColor: strokeColor }}
        />

        {/* Ticks (Speedometer Style) */}
        <div className="absolute inset-0 flex items-center justify-center">
          {ticks.map((_, i) => {
            const angle = (i * 360) / ticks.length;
            const threshold = (i / ticks.length) * 100;
            const isActive = score > threshold;
            
            return (
              <div
                key={i}
                className="absolute w-1 h-3 rounded-full transition-all duration-300"
                style={{
                  transform: `rotate(${angle}deg) translateY(-80px)`,
                  backgroundColor: isActive ? strokeColor : 'rgba(255,255,255,0.05)',
                  boxShadow: isActive ? `0 0 10px ${strokeColor}` : 'none'
                }}
              />
            );
          })}
        </div>

        {/* Main Numerical Display */}
        <div className="flex flex-col items-center z-10">
          <motion.div
            key={score}
            initial={{ scale: 0.9, opacity: 0.8 }}
            animate={{ scale: 1, opacity: 1 }}
            className="flex items-baseline"
          >
            <span className="text-5xl font-mono font-bold tracking-tighter text-white">
              {score.toFixed(0)}
            </span>
            <span className="text-xs text-gray-500 ml-1 mb-1">%</span>
          </motion.div>
          <span className={`text-[10px] uppercase tracking-[0.2em] font-bold mt-2 ${isCritical ? 'text-neonRed animate-pulse' : 'text-gray-400'}`}>
            {isCritical ? 'High Risk' : isDanger ? 'Caution' : 'Optimal'}
          </span>
        </div>
      </div>
    </div>
  );
});

RiskGauge.displayName = "RiskGauge";
export default RiskGauge;

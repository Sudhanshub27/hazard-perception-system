import { motion } from "framer-motion";

export default function RiskGauge({ score }: { score: number }) {
  // Determine color based on risk score (0-100)
  const isCritical = score >= 80;
  const isDanger = score >= 50 && score < 80;
  
  const strokeColor = isCritical ? "#FF3366" : isDanger ? "#FFCC00" : "#0FF4C6";
  const glowColor = isCritical ? "rgba(255, 51, 102, 0.5)" : isDanger ? "rgba(255, 204, 0, 0.4)" : "rgba(15, 244, 198, 0.3)";

  return (
    <div className="flex flex-col items-center justify-center p-6 glass-panel relative overflow-hidden">
      {/* Background glow behind gauge */}
      <motion.div 
        animate={{ opacity: isCritical ? [0.5, 0.8, 0.5] : 0.4 }}
        transition={{ repeat: Infinity, duration: 1 }}
        className="absolute w-32 h-32 blur-[40px] rounded-full"
        style={{ backgroundColor: strokeColor }}
      />
      
      <div className="relative w-40 h-40 flex items-center justify-center">
        {/* SVG Circular Track */}
        <svg className="absolute w-full h-full transform -rotate-90">
          <circle
            cx="80" cy="80" r="70"
            stroke="rgba(255,255,255,0.05)"
            strokeWidth="8" fill="none"
          />
          {/* Animated Progress Circle */}
          <motion.circle
            cx="80" cy="80" r="70"
            stroke={strokeColor}
            strokeWidth="10" 
            fill="none"
            strokeLinecap="round"
            strokeDasharray={440} // 2 * pi * r (approx)
            initial={{ strokeDashoffset: 440 }}
            animate={{ strokeDashoffset: 440 - (440 * score) / 100 }}
            transition={{ type: "spring", stiffness: 40, damping: 10 }}
            style={{ filter: `drop-shadow(0 0 10px ${glowColor})` }}
          />
        </svg>

        {/* Center Text */}
        <div className="absolute flex flex-col items-center">
          <motion.span 
            className="text-4xl font-bold font-mono tracking-tighter text-white"
          >
            {score.toFixed(0)}
          </motion.span>
          <span className="text-[10px] uppercase tracking-widest text-gray-400 mt-1">
            Risk Score
          </span>
        </div>
      </div>
    </div>
  );
}

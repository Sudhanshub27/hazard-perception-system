import { memo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Eye, Clock } from "lucide-react";

const HazardLog = memo(({ detections }: { detections: any[] }) => {
  // Only show the latest 5 detections to reduce visual noise (UX Simplification)
  const latestDetections = detections.slice(0, 5);

  return (
    <div className="glass-panel p-4 h-full flex flex-col border-l-2 border-glassBorder overflow-hidden">
      
      {/* Label Overlay for Clarity */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Clock className="w-3 h-3 text-gray-500" />
          <h3 className="text-[9px] font-bold uppercase tracking-[0.2em] text-gray-500">
            Path Hazard History
          </h3>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto pr-2 space-y-2 custom-scrollbar">
        {latestDetections.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-600 space-y-3">
            <Eye className="w-6 h-6 opacity-10" />
            <span className="text-[9px] uppercase tracking-[0.3em] font-mono font-bold italic">Path Clear</span>
          </div>
        ) : (
          <AnimatePresence mode="popLayout">
            {latestDetections.map((det, idx) => (
              <motion.div
                key={`${det.class_name}-${idx}`}
                initial={{ opacity: 0, x: 20, filter: "blur(4px)" }}
                animate={{ opacity: 1, x: 0, filter: "blur(0px)" }}
                exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.2 } }}
                className="flex items-center justify-between p-2 rounded bg-white/[0.02] border border-white/[0.03] hover:bg-white/[0.04] transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-1 h-3 rounded-full ${det.class_name === 'person' ? 'bg-neonRed' : 'bg-cyberTeal'}`} />
                  <span className="text-[11px] uppercase tracking-wider font-bold text-gray-200">
                    {det.class_name}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-[10px] font-mono text-gray-500">
                    {(det.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </div>

      <div className="mt-4 pt-4 border-t border-glassBorder">
        <div className="flex justify-between items-center text-[8px] font-mono text-gray-600 uppercase tracking-widest">
           <span>Log Archive</span>
           <span className="text-cyberTeal">{detections.length} objects total</span>
        </div>
      </div>
    </div>
  );
});

HazardLog.displayName = "HazardLog";
export default HazardLog;

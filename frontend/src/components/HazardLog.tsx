import { motion, AnimatePresence } from "framer-motion";
import { AlertCircle, Eye, ShieldAlert } from "lucide-react";

export default function HazardLog({ detections }: { detections: any[] }) {
  return (
    <div className="glass-panel p-4 h-full flex flex-col">
      <div className="flex items-center space-x-2 mb-4">
        <ShieldAlert className="w-5 h-5 text-cyberTeal" />
        <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-200">
          Active Detections
        </h3>
      </div>
      
      <div className="flex-1 overflow-y-auto pr-2 space-y-3">
        {detections.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-500 space-y-2">
            <Eye className="w-8 h-8 opacity-20" />
            <span className="text-xs uppercase tracking-widest">Clear Path</span>
          </div>
        ) : (
          <AnimatePresence>
            {detections.map((det, idx) => (
              <motion.div
                key={`${det.class_name}-${idx}`}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="flex items-center justify-between p-3 rounded-lg bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.05)]"
              >
                <div className="flex items-center space-x-3">
                  {det.class_name === "person" ? (
                      <AlertCircle className="w-4 h-4 text-neonRed" />
                  ) : (
                      <div className="w-2 h-2 rounded-full bg-cyberTeal" />
                  )}
                  <span className="text-sm capitalize font-medium text-gray-200">
                    {det.class_name}
                  </span>
                </div>
                <span className="text-xs font-mono text-gray-400">
                  {det.confidence.toFixed(2)}
                </span>
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}

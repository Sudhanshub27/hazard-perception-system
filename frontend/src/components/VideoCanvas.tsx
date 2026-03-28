"use client";

import { memo } from "react";
import { Video, AlertCircle, ShieldCheck } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const VideoCanvas = memo(({
  frameB64,
  status,
  riskScore
}: {
  frameB64: string | null;
  status: string;
  riskScore: number;
}) => {
  const isCritical = riskScore >= 80;

  return (
    <div className="relative w-full h-full bg-black flex items-center justify-center overflow-hidden">
      
      {/* Background Frame Layer */}
      <AnimatePresence mode="wait">
        {frameB64 ? (
           <motion.img
             key="feed"
             src={`data:image/jpeg;base64,${frameB64}`}
             initial={{ opacity: 0, filter: "blur(4px)" }}
             animate={{ opacity: 1, filter: "blur(0px)" }}
             transition={{ duration: 0.3 }}
             className="w-full h-full object-contain"
             alt="Live Inference Feed"
           />
        ) : (
           <motion.div 
             key="placeholder"
             initial={{ opacity: 0 }}
             animate={{ opacity: 1 }}
             exit={{ opacity: 0 }}
             className="flex flex-col items-center justify-center text-borderStrong"
           >
             <Video className="w-12 h-12 mb-4" />
             <p className="text-sm font-medium tracking-wide">Waiting for Video Source</p>
           </motion.div>
        )}
      </AnimatePresence>

      {/* Critical Danger Overlay - Smooth Flash */}
      <AnimatePresence>
        {isCritical && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: [0.1, 0.3, 0.1] }}
            exit={{ opacity: 0 }}
            transition={{ repeat: Infinity, duration: 1.5 }}
            className="absolute inset-0 bg-signalDanger pointer-events-none mix-blend-color-burn"
          />
        )}
      </AnimatePresence>

      {/* Floating Status Pill */}
      <motion.div 
         initial={{ y: -20, opacity: 0 }}
         animate={{ y: 0, opacity: 1 }}
         transition={{ delay: 0.2 }}
         className="absolute top-4 right-4 flex items-center space-x-2 bg-panel/80 backdrop-blur-md border border-borderSubtle px-3 py-1.5 rounded-full shadow-soft"
      >
        {status === "Live" && !isCritical && <ShieldCheck className="w-4 h-4 text-safeGreen" />}
        {status === "Live" && isCritical && <AlertCircle className="w-4 h-4 text-signalDanger animate-pulse" />}
        <span className="text-xs font-semibold tracking-wide text-gray-200">
           {status.toUpperCase()}
        </span>
        {status === "Live" && (
           <span className="relative flex h-2 w-2 ml-1">
             <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-sysAccent opacity-75"></span>
             <span className="relative inline-flex rounded-full h-2 w-2 bg-sysAccent"></span>
           </span>
        )}
      </motion.div>

    </div>
  );
});

VideoCanvas.displayName = "VideoCanvas";
export default VideoCanvas;

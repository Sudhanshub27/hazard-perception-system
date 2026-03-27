import { Video, Maximize2, ShieldAlert } from "lucide-react";
import { motion } from "framer-motion";

interface VideoCanvasProps {
  frameB64: string | null;
  status: string;
}

export default function VideoCanvas({ frameB64, status }: VideoCanvasProps) {
  const isActive = status === 'Live';

  return (
    <div className="glass-panel w-full aspect-video flex flex-col overflow-hidden relative group border-[rgba(15,244,198,0.2)]">
      {/* Target Reticles (Corners) */}
      <div className="absolute top-4 left-4 w-6 h-6 border-t-2 border-l-2 border-cyberTeal/40 rounded-tl-sm pointer-events-none z-20" />
      <div className="absolute top-4 right-4 w-6 h-6 border-t-2 border-r-2 border-cyberTeal/40 rounded-tr-sm pointer-events-none z-20" />
      <div className="absolute bottom-4 left-4 w-6 h-6 border-b-2 border-l-2 border-cyberTeal/40 rounded-bl-sm pointer-events-none z-20" />
      <div className="absolute bottom-4 right-4 w-6 h-6 border-b-2 border-r-2 border-cyberTeal/40 rounded-br-sm pointer-events-none z-20" />

      {/* Top HUD bar */}
      <div className="absolute top-0 w-full p-4 flex justify-between items-center z-20 bg-gradient-to-b from-black/80 to-transparent pointer-events-none">
        <div className="flex items-center space-x-3">
          <div className="flex flex-col">
            <span className="text-[10px] font-bold text-cyberTeal tracking-[0.3em] uppercase opacity-80">System.Stream.HD</span>
            <div className="flex items-center space-x-2 mt-1">
              <div className={`w-1.5 h-1.5 rounded-full ${isActive ? 'bg-neonRed animate-pulse' : 'bg-gray-500'}`} />
              <span className="text-[9px] font-mono uppercase tracking-widest text-gray-300">
                {status} :: INGESTING_RAW
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-4">
           <div className="h-6 w-[1px] bg-glassBorder mx-2" />
           <Maximize2 className="w-4 h-4 text-gray-400 opacity-50" />
        </div>
      </div>

      {/* Scanning Laser Effect */}
      {isActive && (
        <motion.div 
          initial={{ top: "0%" }}
          animate={{ top: "100%" }}
          transition={{ repeat: Infinity, duration: 4, ease: "linear" }}
          className="absolute left-0 w-full h-[1px] bg-cyberTeal/30 shadow-[0_0_15px_rgba(15,244,198,0.5)] z-20 pointer-events-none"
        />
      )}

      {/* Main Canvas Area */}
      <div className="relative w-full h-full flex flex-col items-center justify-center bg-black/40 overflow-hidden">
        {frameB64 ? (
          <>
            <img 
              src={`data:image/jpeg;base64,${frameB64}`} 
              alt="Live Dashcam Stream"
              className="w-full h-full object-contain transition-opacity duration-300"
            />
            {/* Vignette shadow to blend edges */}
            <div className="absolute inset-0 shadow-[inset_0_0_150px_rgba(0,0,0,0.8)] pointer-events-none" />
          </>
        ) : (
          <div className="flex flex-col items-center justify-center space-y-4">
            <div className="relative">
              <Video className="w-12 h-12 text-cyberTeal animate-pulse opacity-20" />
              <motion.div 
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                className="absolute -inset-2 border-t border-cyberTeal/20 rounded-full"
              />
            </div>
            <p className="text-[10px] uppercase tracking-[0.4em] font-bold text-gray-500">
              Initializing...
            </p>
          </div>
        )}
      </div>

      {/* Static Scanline Overlay */}
      <div className="absolute inset-0 pointer-events-none opacity-[0.05] bg-[linear-gradient(rgba(255,255,255,0.05)_50%,rgba(0,0,0,0.1)_50%)] bg-[length:100%_4px] mix-blend-overlay" />
    </div>
  );
}

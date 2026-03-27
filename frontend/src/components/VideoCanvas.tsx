import { Video } from "lucide-react";

interface VideoCanvasProps {
  frameB64: string | null;
  status: string;
}

export default function VideoCanvas({ frameB64, status }: VideoCanvasProps) {
  return (
    <div className="glass-panel w-full aspect-video flex flex-col overflow-hidden relative group">
      {/* Top HUD overlay */}
      <div className="absolute top-0 w-full p-4 flex justify-between items-center z-10 bg-gradient-to-b from-black/60 to-transparent pointer-events-none">
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${frameB64 ? 'bg-neonRed animate-pulse' : 'bg-gray-500'}`} />
          <span className="text-xs font-mono uppercase tracking-widest text-gray-300">
            {status}
          </span>
        </div>
      </div>

      {/* Main Canvas Area */}
      {frameB64 ? (
        // Render the raw Base64 JPEG frame directly 
        <img 
          src={`data:image/jpeg;base64,${frameB64}`} 
          alt="Live Dashcam Stream"
          className="w-full h-full object-cover transition-opacity duration-300"
        />
      ) : (
        // Waiting state
        <div className="flex flex-col items-center justify-center h-full w-full bg-black/40 text-gray-500">
          <Video className="w-12 h-12 mb-4 opacity-50" />
          <p className="text-sm uppercase tracking-widest animate-pulse">
            Awaiting Stream Connection...
          </p>
        </div>
      )}
      
      {/* Scanline overlay effect for cinematic feel */}
      <div className="absolute inset-0 pointer-events-none opacity-[0.03] bg-[linear-gradient(rgba(255,255,255,0)_50%,rgba(0,0,0,1)_50%)] bg-[length:100%_4px]" />
    </div>
  );
}

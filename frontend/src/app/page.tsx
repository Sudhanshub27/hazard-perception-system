"use client";

import { useState, useRef, useEffect } from "react";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import { 
  UploadCloud, 
  Power, 
  Activity, 
  Cpu, 
  Database, 
  Zap, 
  Terminal as TerminalIcon 
} from "lucide-react";

import VideoCanvas from "../components/VideoCanvas";
import RiskGauge from "../components/RiskGauge";
import HazardLog from "../components/HazardLog";
import StatsPanel from "../components/StatsPanel";

export default function Dashboard() {
  const [file, setFile] = useState<File | null>(null);
  const [videoId, setVideoId] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [wsStatus, setWsStatus] = useState<"Offline" | "Connecting" | "Live">("Offline");
  
  // Real-time State
  const [frameB64, setFrameB64] = useState<string | null>(null);
  const [riskScore, setRiskScore] = useState<number>(0);
  const [detections, setDetections] = useState<any[]>([]);

  // Session Accumulation State
  const [maxRisk, setMaxRisk] = useState<number>(0);
  const [totalDetectionsCount, setTotalDetectionsCount] = useState<number>(0);
  const seenDetectionIds = useRef(new Set<string>());

  const wsRef = useRef<WebSocket | null>(null);

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("http://localhost:8000/video/upload", formData);
      setVideoId(res.data.video_id);
      startStream(res.data.video_id);
    } catch (err) {
      console.error("Upload failed", err);
      alert("Failed to connect to Neural Engine.");
    } finally {
      setIsUploading(false);
    }
  };

  const startStream = (id: string) => {
    setWsStatus("Connecting");
    const wsUrl = `ws://localhost:8000/ws/stream/${id}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => setWsStatus("Live");

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "frame") {
        const payload = data.payload;
        setFrameB64(payload.frame_b64);
        setRiskScore(payload.risk_score);
        setDetections(payload.detections);

        // Update session stats
        if (payload.risk_score > maxRisk) setMaxRisk(payload.risk_score);
        
        // Count unique detections based on class and approximate location to avoid double counting
        payload.detections.forEach((det: any) => {
          const detKey = `${det.class_name}-${Math.round(det.bbox[0]/10)}-${Math.round(det.bbox[1]/10)}`;
          if (!seenDetectionIds.current.has(detKey)) {
             seenDetectionIds.current.add(detKey);
             setTotalDetectionsCount(prev => prev + 1);
          }
        });

      } else if (data.type === "end_of_stream") {
        ws.close();
      }
    };

    ws.onclose = () => setWsStatus("Offline");
  };

  useEffect(() => {
    return () => { if (wsRef.current) wsRef.current.close(); };
  }, []);

  // Stagger animation variants for "Boot Up" feel
  const containerVars = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1, delayChildren: 0.3 }
    }
  };

  const itemVars = {
    hidden: { opacity: 0, y: 10, filter: "blur(4px)" },
    show: { opacity: 1, y: 0, filter: "blur(0px)" }
  };

  return (
    <motion.div 
      initial="hidden"
      animate="show"
      variants={containerVars}
      className="h-screen w-screen overflow-hidden bg-obsidian text-white flex flex-col font-sans selection:bg-cyberTeal/30"
    >
      {/* Header / Global Status Bar */}
      <motion.header variants={itemVars} className="h-16 border-b border-glassBorder px-8 flex justify-between items-center bg-black/20 backdrop-blur-xl z-50">
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-3 group cursor-default">
            <div className="relative">
              <Activity className="w-5 h-5 text-cyberTeal group-hover:scale-110 transition-transform" />
              <motion.div 
                animate={{ opacity: [0.2, 0.5, 0.2] }} 
                transition={{ repeat: Infinity, duration: 2 }}
                className="absolute inset-0 bg-cyberTeal rounded-full blur-md" 
              />
            </div>
            <h1 className="text-sm font-black tracking-[0.4em] uppercase leading-none">
              Hazard<span className="text-cyberTeal">Perception</span>.v26
            </h1>
          </div>
          
          <div className="h-4 w-[1px] bg-glassBorder" />
          
          <div className="flex items-center space-x-4">
             <div className="flex items-center space-x-1.5">
               <Cpu className="w-3 h-3 text-gray-500" />
               <span className="text-[9px] uppercase tracking-widest text-gray-500 font-bold">Neural_GPU: OK</span>
             </div>
             <div className="flex items-center space-x-1.5">
               <Database className="w-3 h-3 text-gray-500" />
               <span className="text-[9px] uppercase tracking-widest text-gray-500 font-bold">Memory_Pool: 8GB</span>
             </div>
          </div>
        </div>

        <div className="flex items-center space-x-6">
           <div className="flex flex-col items-end">
              <span className="text-[8px] uppercase tracking-widest text-gray-500 mb-0.5">Connection Topology</span>
              <div className="flex items-center space-x-2">
                <span className={`text-[10px] font-mono font-bold ${wsStatus === 'Live' ? 'text-cyberTeal' : 'text-gray-500 animate-pulse'}`}>
                  {wsStatus.toUpperCase()}
                </span>
                <div className={`w-1.5 h-1.5 rounded-full ${wsStatus === 'Live' ? 'bg-cyberTeal shadow-[0_0_8px_rgba(15,244,198,0.8)]' : 'bg-gray-700'}`} />
              </div>
           </div>
           <button className="p-2 hover:bg-glassWhite rounded-lg border border-glassBorder transition-all hover:border-cyberTeal/40 active:scale-95">
             <Power className="w-4 h-4 text-gray-400" />
           </button>
        </div>
      </motion.header>

      {/* Main Grid Layout */}
      <main className="flex-1 grid grid-cols-[300px_1fr_320px] overflow-hidden p-6 gap-6 relative">
        
        {/* Background Grid Accent */}
        <div className="absolute inset-0 opacity-[0.03] pointer-events-none bg-[radial-gradient(#fff_1px,transparent_1px)] [background-size:40px_40px]" />

        {/* Column 1: Control & Session Info */}
        <motion.div variants={itemVars} className="flex flex-col space-y-6 z-10">
          
          {/* Upload Section */}
          <div className="glass-panel p-6 flex flex-col border-b-2 border-cyberTeal/10">
            <h4 className="text-[10px] uppercase tracking-[0.2em] font-bold text-gray-500 mb-4 flex items-center gap-2">
               <Zap className="w-3 h-3 text-cyberTeal" /> Ingest Core
            </h4>
            
            {!videoId ? (
              <div className="space-y-4">
                 <div className="relative group border-2 border-dashed border-glassBorder rounded-xl p-8 hover:border-cyberTeal/40 transition-all text-center">
                    <input 
                      type="file" 
                      accept="video/mp4,video/avi"
                      onChange={(e) => setFile(e.target.files?.[0] || null)}
                      className="absolute inset-0 opacity-0 cursor-pointer"
                    />
                    <UploadCloud className="w-8 h-8 text-gray-500 mx-auto mb-2 group-hover:text-cyberTeal transition-colors" />
                    <span className="text-[10px] font-mono text-gray-400 block truncate">
                      {file ? file.name : "Select Stream Source"}
                    </span>
                 </div>
                 <button 
                  onClick={handleUpload}
                  disabled={!file || isUploading}
                  className="w-full py-3 bg-cyberTeal text-obsidian text-[10px] font-black uppercase tracking-[0.2em] rounded-lg 
                             hover:shadow-[0_0_20px_rgba(15,244,198,0.4)] transition-all disabled:opacity-30 disabled:grayscale"
                >
                  {isUploading ? "Initializing Pipeline..." : "Unlock Stream"}
                </button>
              </div>
            ) : (
              <div className="p-4 rounded-lg bg-cyberTeal/10 border border-cyberTeal/20">
                 <div className="flex items-center space-x-2 text-cyberTeal">
                    <TerminalIcon className="w-4 h-4" />
                    <span className="text-[10px] font-mono font-bold tracking-widest uppercase">Stream Hash Active</span>
                 </div>
                 <p className="text-[9px] font-mono text-gray-500 mt-2 truncate">ID: {videoId}</p>
              </div>
            )}
          </div>

          <StatsPanel 
            maxRisk={maxRisk} 
            avgRisk={0} 
            totalDetections={totalDetectionsCount} 
          />

          <div className="flex-1 glass-panel p-4 flex flex-col justify-end space-y-2 opacity-10 grayscale hover:opacity-100 hover:grayscale-0 transition-all pointer-events-none">
             <div className="h-1 w-full bg-glassWhite rounded-full overflow-hidden">
                <motion.div 
                  animate={{ width: ["0%", "100%", "0%"] }} 
                  transition={{ repeat: Infinity, duration: 5 }}
                  className="h-full bg-cyberTeal" 
                />
             </div>
             <span className="text-[8px] font-mono text-gray-600">Buffer_Integrity: 0.998</span>
          </div>

        </motion.div>

        {/* Column 2: The Neural Canvas */}
        <motion.div variants={itemVars} className="flex flex-col z-10 items-center justify-center">
          <VideoCanvas frameB64={frameB64} status={wsStatus} />
        </motion.div>

        {/* Column 3: Telemetry & Log */}
        <motion.div variants={itemVars} className="flex flex-col space-y-6 z-10 overflow-hidden">
           <div className="h-[260px]">
             <RiskGauge score={riskScore} />
           </div>
           
           <div className="flex-1 overflow-hidden min-h-0">
             <HazardLog detections={detections} />
           </div>
        </motion.div>

      </main>

      {/* Footer System Log */}
      <motion.footer variants={itemVars} className="h-8 px-6 bg-black flex items-center justify-between border-t border-glassBorder border-opacity-30">
        <div className="flex items-center space-x-6 text-[9px] font-mono text-gray-600 tracking-wider">
           <span>Engine_State::Active</span>
           <span>Latency::<span className="text-cyberTeal">0.45ms</span></span>
           <span>ONNX_Compute::CUDA_ACCEL</span>
        </div>
        <div className="text-[9px] font-mono text-gray-700">
           © 2026 HazardPerception AI. All Vectors Operating.
        </div>
      </motion.footer>

    </motion.div>
  );
}

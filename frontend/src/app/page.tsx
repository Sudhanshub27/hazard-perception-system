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
  ShieldAlert,
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
        
        payload.detections.forEach((det: any) => {
          const detKey = `${det.class_name}-${Math.round(det.bbox[0]/15)}-${Math.round(det.bbox[1]/15)}`;
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

  const isCritical = riskScore >= 80;

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className={`h-screen w-screen overflow-hidden text-white flex flex-col font-sans transition-all duration-700 ${isCritical ? 'bg-[#1a050a]' : 'bg-obsidian'}`}
    >
      {/* Global Critical Edge Pulse (UX Focus) */}
      <AnimatePresence>
        {isCritical && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 border-[3px] border-neonRed/30 shadow-[inset_0_0_100px_rgba(255,51,102,0.2)] pointer-events-none z-50 animate-pulse"
          />
        )}
      </AnimatePresence>

      {/* Header */}
      <header className="h-16 border-b border-glassBorder px-8 flex justify-between items-center bg-black/40 backdrop-blur-xl z-[60]">
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-3 group cursor-default">
            <Activity className="w-5 h-5 text-cyberTeal" />
            <h1 className="text-sm font-black tracking-[0.4em] uppercase">
              Hazard<span className="text-cyberTeal">Perception</span>.v26
            </h1>
          </div>
        </div>

        <div className="flex items-center space-x-6">
           <div className={`flex flex-col items-end transition-opacity ${isCritical ? 'opacity-30' : 'opacity-100'}`}>
              <span className="text-[8px] uppercase tracking-widest text-gray-500 mb-0.5">Engine Status</span>
              <div className="flex items-center space-x-2">
                <span className={`text-[10px] font-mono font-bold ${wsStatus === 'Live' ? 'text-cyberTeal' : 'text-gray-500'}`}>
                  {wsStatus.toUpperCase()}
                </span>
                <div className={`w-1.5 h-1.5 rounded-full ${wsStatus === 'Live' ? 'bg-cyberTeal shadow-neon' : 'bg-gray-700'}`} />
              </div>
           </div>
           <button className="p-2 hover:bg-glassWhite rounded-lg border border-glassBorder transition-all opacity-40 hover:opacity-100">
             <Power className="w-4 h-4 text-gray-400" />
           </button>
        </div>
      </header>

      {/* Main Grid Layout */}
      <main className="flex-1 grid grid-cols-[280px_1fr_300px] overflow-hidden p-6 gap-6 relative">
        <div className="absolute inset-0 opacity-[0.02] pointer-events-none bg-[radial-gradient(#fff_1px,transparent_1px)] [background-size:40px_40px]" />

        {/* Side Panel A: Controls & Stats (UX: Dims in Danger) */}
        <motion.div 
          animate={{ opacity: isCritical ? 0.3 : 1, filter: isCritical ? 'blur(2px)' : 'blur(0px)' }}
          className="flex flex-col space-y-6 z-10 transition-all duration-500"
        >
          <div className="glass-panel p-6 flex flex-col">
            <h4 className="text-[9px] uppercase tracking-[0.2em] font-bold text-gray-500 mb-4 flex items-center gap-2">
               <Zap className="w-3 h-3 text-cyberTeal" /> Input Module
            </h4>
            
            {!videoId ? (
              <div className="space-y-4">
                 <div className="relative group border-2 border-dashed border-glassBorder rounded-xl p-8 hover:border-cyberTeal/40 transition-all text-center">
                    <input type="file" accept="video/mp4,video/avi" onChange={(e) => setFile(e.target.files?.[0] || null)} className="absolute inset-0 opacity-0 cursor-pointer" />
                    <UploadCloud className="w-8 h-8 text-gray-600 mx-auto mb-2 group-hover:text-cyberTeal" />
                    <span className="text-[10px] uppercase font-mono text-gray-500 truncate block">Source Stream</span>
                 </div>
                 <button onClick={handleUpload} disabled={!file || isUploading} className="w-full py-3 bg-cyberTeal text-obsidian text-[10px] font-black uppercase tracking-[0.2em] rounded-lg">
                  {isUploading ? "Linking..." : "Start Pipeline"}
                </button>
              </div>
            ) : (
              <div className="p-4 rounded-lg bg-cyberTeal/10 border border-cyberTeal/20 flex items-center justify-between">
                 <span className="text-[10px] font-bold text-cyberTeal tracking-widest uppercase italic">Ingest Active</span>
                 <Database className="w-4 h-4 text-cyberTeal opacity-40" />
              </div>
            )}
          </div>

          <StatsPanel maxRisk={maxRisk} avgRisk={0} totalDetections={totalDetectionsCount} />
        </motion.div>

        {/* Central Focus (UX: The Ground Truth) */}
        <div className="flex flex-col z-10 items-center justify-center scale-105">
          <VideoCanvas frameB64={frameB64} status={wsStatus} riskScore={riskScore} />
        </div>

        {/* Side Panel B: Telemetry (UX: Dims in Danger) */}
        <motion.div 
          animate={{ opacity: isCritical ? 0.3 : 1, filter: isCritical ? 'blur(2px)' : 'blur(0px)' }}
          className="flex flex-col space-y-6 z-10 overflow-hidden transition-all duration-500"
        >
           <div className="h-[260px] glass-panel p-4 flex flex-col">
              <h4 className="text-[9px] uppercase tracking-[0.2em] font-bold text-gray-500 mb-2 flex items-center gap-2">
                <ShieldAlert className="w-3 h-3" /> Live Telemetry
              </h4>
             <RiskGauge score={riskScore} />
           </div>
           
           <div className="flex-1 overflow-hidden min-h-0">
             <HazardLog detections={detections} />
           </div>
        </motion.div>

      </main>

      <footer className="h-8 px-8 bg-black/40 flex items-center justify-between border-t border-glassBorder border-opacity-30 z-[60]">
        <div className="flex items-center space-x-6 text-[8px] font-mono text-gray-600 tracking-widest">
           <span>Engine_v0.1</span>
           <span>Mode_Inference</span>
        </div>
      </footer >

    </motion.div>
  );
}

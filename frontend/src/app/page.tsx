"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { UploadCloud, ShieldAlert, Sparkles } from "lucide-react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";

import VideoCanvas from "../components/VideoCanvas";
import RiskGauge from "../components/RiskGauge";
import StatsPanel from "../components/StatsPanel";
import HazardLog from "../components/HazardLog";

const FADE_UP = {
  hidden: { opacity: 0, y: 30 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 100, damping: 20 } }
};

export default function Dashboard() {
  const [streamInfo, setStreamInfo] = useState<{ frameId: number, timestampMs: number } | null>(null);
  const [frameB64, setFrameB64] = useState<string | null>(null);
  const [detections, setDetections] = useState<any[]>([]);
  const [riskScore, setRiskScore] = useState<number>(0);
  const [status, setStatus] = useState<string>("Standby");
  const [events, setEvents] = useState<any[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setIsUploading(true);
    setStatus("Uploading");
    setFrameB64(null);
    setDetections([]);
    setRiskScore(0);
    setEvents([]);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const resp = await fetch(`http://localhost:8000/video/upload`, {
        method: "POST",
        body: formData,
      });
      const data = await resp.json();
      const videoId = data.video_id;

      startStream(videoId);
    } catch (err) {
      console.error("Upload failed", err);
      setStatus("Upload Failed");
      setIsUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop, 
    accept: { 'video/*': ['.mp4', '.mov', '.avi'] },
    multiple: false
  });

  const startStream = (videoId: string) => {
    if (ws.current) ws.current.close();

    ws.current = new WebSocket(`ws://localhost:8000/ws/stream/${videoId}`);

    ws.current.onopen = () => {
      setStatus("Live");
      setIsUploading(false);
    };

    ws.current.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === "frame") {
        const payload = msg.payload;
        setStreamInfo({ frameId: payload.frame_id, timestampMs: payload.timestamp_ms });
        setFrameB64(payload.frame_b64);
        setDetections(payload.detections);
        setRiskScore(payload.risk_score);
        
        if (payload.risk_score > 60) {
          setEvents(prev => [{
            id: payload.frame_id,
            timestamp: new Date().toISOString(),
            risk_score: payload.risk_score,
            highest_threat_class: payload.detections[0]?.class_name || "Unknown"
          }, ...prev].slice(0, 50));
        }
      } else if (msg.type === "end_of_stream") {
        setStatus("Complete");
        ws.current?.close();
      }
    };

    ws.current.onerror = () => {
      setStatus("Error");
      setIsUploading(false);
    };

    ws.current.onclose = () => {
      if (status !== "Complete") setStatus("Disconnected");
      setIsUploading(false);
    };
  };

  return (
    <div className="min-h-screen bg-surf text-gray-200 font-sans p-8 overflow-hidden flex flex-col h-screen selection:bg-sysAccent/30 selection:text-white">
      
      {/* Premium Header */}
      <motion.header 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="flex justify-between items-center mb-8 shrink-0 pb-6 border-b border-borderSubtle"
      >
        <div className="flex items-center space-x-4">
           <div className="bg-gradient-to-br from-sysAccent to-blue-700 p-2 rounded-xl shadow-glow">
             <Sparkles className="w-6 h-6 text-white" />
           </div>
           <div>
             <h1 className="text-2xl font-semibold tracking-tight text-white flex items-center gap-2">
               Platform Intelligence
               <span className="px-2 py-0.5 rounded-full bg-white/10 text-[10px] uppercase font-bold text-textMuted tracking-wider">v3.0</span>
             </h1>
             <p className="text-sm text-textMuted mt-1">Autonomous Hazard Perception System</p>
           </div>
        </div>
        
        {/* Soft Upload Dropzone */}
        {!isUploading && status !== 'Live' && (
          <motion.div 
            {...getRootProps()}
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            className={`px-5 py-2.5 rounded-xl cursor-pointer transition-colors shadow-soft border flex items-center space-x-2 text-sm font-medium
              ${isDragActive ? 'bg-sysAccent/20 border-sysAccent text-white' : 'bg-panel border-borderSubtle hover:bg-borderSubtle text-gray-300'}`}
          >
            <input {...getInputProps()} />
            <UploadCloud className="w-4 h-4 text-textMuted" />
            <span>{isDragActive ? "Drop Video" : "Load Source Video"}</span>
          </motion.div>
        )}
      </motion.header>

      {/* Main Content Staggered Entry */}
      <motion.div 
        variants={{ show: { transition: { staggerChildren: 0.1 } } }}
        initial="hidden"
        animate="show"
        className="flex-1 flex gap-8 h-full min-h-0"
      >
        
        {/* Left Focus Area: Feed & Metrics */}
        <motion.div variants={FADE_UP} className="flex-[5] flex flex-col gap-8 min-w-0">
           
           {/* Primary Video Canvas */}
           <div className="w-full shrink-0 flex items-center place-content-center bg-panel border border-borderSubtle rounded-2xl shadow-soft overflow-hidden">
             <VideoCanvas 
               frameB64={frameB64} 
               status={status} 
               riskScore={riskScore}
             />
           </div>
           
           {/* Telemetry Footer */}
           <div className="bg-panel border border-borderSubtle rounded-2xl shadow-soft p-5 flex-1 flex flex-col justify-center">
              <div className="flex justify-around items-center h-full text-center">
                 <div className="flex flex-col">
                    <span className="text-xs font-semibold text-textMuted uppercase tracking-wider mb-1">Latency</span>
                    <span className="text-2xl font-semibold text-white tracking-tight">~2.4<span className="text-lg text-textMuted">ms</span></span>
                 </div>
                 <div className="w-[1px] h-10 bg-borderSubtle/50" />
                 <div className="flex flex-col">
                    <span className="text-xs font-semibold text-textMuted uppercase tracking-wider mb-1">Frame ID</span>
                    <span className="text-2xl font-mono text-sysAccent">{streamInfo?.frameId || 0}</span>
                 </div>
                 <div className="w-[1px] h-10 bg-borderSubtle/50" />
                 <div className="flex flex-col">
                    <span className="text-xs font-semibold text-textMuted uppercase tracking-wider mb-1">Timestamp</span>
                    <span className="text-2xl font-mono text-white tracking-tight">{(streamInfo?.timestampMs || 0).toFixed(0)}</span>
                 </div>
              </div>
           </div>
        </motion.div>

        {/* Right Aux Area: Risk & Logs */}
        <motion.div variants={FADE_UP} className="flex-[3] flex flex-col gap-6 min-w-0">
           
           <div className="h-44 shrink-0 bg-panel border border-borderSubtle rounded-2xl shadow-soft overflow-hidden">
             <RiskGauge score={riskScore} />
           </div>

           <div className="h-48 shrink-0 bg-panel border border-borderSubtle rounded-2xl shadow-soft overflow-hidden">
             <StatsPanel objects={detections} />
           </div>

           <div className="flex-1 min-h-0 bg-panel border border-borderSubtle rounded-2xl shadow-soft overflow-hidden">
             <HazardLog events={events} />
           </div>
           
        </motion.div>

      </motion.div>

    </div>
  );
}

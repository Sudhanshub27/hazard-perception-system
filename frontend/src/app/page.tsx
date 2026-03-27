"use client";

import { useState, useRef, useEffect } from "react";
import axios from "axios";
import { UploadCloud, Power, Activity } from "lucide-react";
import VideoCanvas from "@/components/VideoCanvas";
import RiskGauge from "@/components/RiskGauge";
import HazardLog from "@/components/HazardLog";

export default function Dashboard() {
  const [file, setFile] = useState<File | null>(null);
  const [videoId, setVideoId] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [wsStatus, setWsStatus] = useState<"Disconnected" | "Connecting" | "Live">("Disconnected");
  
  const [frameB64, setFrameB64] = useState<string | null>(null);
  const [riskScore, setRiskScore] = useState<number>(0);
  const [detections, setDetections] = useState<any[]>([]);

  // We use a ref to hold the WS connection so it persists across renders
  const wsRef = useRef<WebSocket | null>(null);

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      // Assuming FastAPI API is exposed on localhost:8000 via Docker
      const res = await axios.post("http://localhost:8000/video/upload", formData);
      setVideoId(res.data.video_id);
      startStream(res.data.video_id);
    } catch (err) {
      console.error("Upload failed", err);
      alert("Failed to upload video to backend engine.");
    } finally {
      setIsUploading(false);
    }
  };

  const startStream = (id: string) => {
    setWsStatus("Connecting");
    
    // Connect tracking websocket
    const wsUrl = `ws://localhost:8000/ws/stream/${id}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setWsStatus("Live");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === "frame") {
        const payload = data.payload;
        setFrameB64(payload.frame_b64);
        setRiskScore(payload.risk_score);
        setDetections(payload.detections);
      } else if (data.type === "end_of_stream") {
        ws.close();
      }
    };

    ws.onclose = () => {
      setWsStatus("Disconnected");
    };
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  return (
    <div className="min-h-screen p-6 md:p-10 flex flex-col space-y-6">
      
      {/* Top Navigation Bar */}
      <header className="flex justify-between items-center glass-panel px-6 py-4">
        <div className="flex items-center space-x-3">
          <Activity className="w-6 h-6 text-cyberTeal" />
          <h1 className="text-xl font-bold tracking-widest uppercase">
            Hazard<span className="text-cyberTeal">Perception</span> Core
          </h1>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-xs font-mono uppercase tracking-wider">
            <span className={`w-2 h-2 rounded-full ${wsStatus === 'Live' ? 'bg-cyberTeal animate-pulse' : 'bg-gray-500'}`} />
            <span className={wsStatus === 'Live' ? 'text-cyberTeal' : 'text-gray-500'}>{wsStatus}</span>
          </div>
          <button className="p-2 hover:bg-[rgba(255,255,255,0.05)] rounded-full transition-colors">
            <Power className="w-5 h-5 text-gray-400" />
          </button>
        </div>
      </header>

      {/* Main Content Split */}
      <main className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* Left Column (Video Canvas & Upload) */}
        <div className="lg:col-span-3 flex flex-col space-y-6">
          <VideoCanvas frameB64={frameB64} status={wsStatus} />

          {/* Upload Widget */}
          {!videoId && (
            <div className="glass-panel p-8 flex flex-col items-center justify-center border-dashed border-2 
                            border-[rgba(255,255,255,0.1)] hover:border-cyberTeal transition-colors group">
              <UploadCloud className="w-12 h-12 text-gray-400 group-hover:text-cyberTeal transition-colors mb-4" />
              <input 
                type="file" 
                accept="video/mp4,video/avi"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="mb-4 text-sm text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 
                           file:text-sm file:font-semibold file:bg-[rgba(15,244,198,0.1)] file:text-cyberTeal hover:file:bg-[rgba(15,244,198,0.2)]"
              />
              <button 
                onClick={handleUpload}
                disabled={!file || isUploading}
                className="px-8 py-3 bg-cyberTeal text-obsidian font-bold rounded-lg uppercase tracking-wider 
                           hover:bg-opacity-80 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isUploading ? "Uploading..." : "Initialize Stream"}
              </button>
            </div>
          )}
        </div>

        {/* Right Column (Telemetry Diagnostics) */}
        <div className="lg:col-span-1 flex flex-col space-y-6 h-full">
          <RiskGauge score={riskScore} />
          
          <div className="flex-1 min-h-[400px]">
            <HazardLog detections={detections} />
          </div>
        </div>

      </main>
    </div>
  );
}

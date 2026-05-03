"use client";

import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  CartesianGrid
} from "recharts";
import { ShieldAlert, ShieldCheck, Activity, Terminal, Lock } from "lucide-react";

// 1. Type Definitions
interface TrafficData {
  timestamp: string;
  score: number;       // Mapped from 'anomaly_score'
  status: "NORMAL" | "CRITICAL";
  explanation: string;
}

export default function Dashboard() {
  // 2. State Management
  const [dataPoints, setDataPoints] = useState<TrafficData[]>([]);
  const [connectionStatus, setConnectionStatus] = useState("CONNECTING...");
  const [latestExplanation, setLatestExplanation] = useState("System Initializing...");

  useEffect(() => {
    // 3. WebSocket Connection (Ensure Port 8000 matches your Django/FastAPI port)
    // Note: Django Channels usually requires a trailing slash: /ws/traffic/
    const ws = new WebSocket("ws://127.0.0.1:8000/ws/traffic/");

    ws.onopen = () => {
      setConnectionStatus("CONNECTED");
      console.log("✅ WebSocket Connected");
    };

    ws.onmessage = (event) => {
      try {
        const rawData = JSON.parse(event.data);
        
        // ---------------------------------------------------------
        // CRITICAL FIX: Map Backend Data to Frontend Interface
        // ---------------------------------------------------------
        const processedData: TrafficData = {
          timestamp: new Date().toLocaleTimeString(), // Create a readable time
          score: rawData.anomaly_score || rawData.score || 0, // Handle different naming conventions
          status: rawData.status || "NORMAL",
          explanation: rawData.explanation || "Traffic is normal."
        };

        // Update State
        setDataPoints((prev) => {
          const updated = [...prev, processedData];
          // Keep only the last 30 data points for performance
          if (updated.length > 30) updated.shift();
          return updated;
        });

        // Update Explanation Logic
        if (processedData.status === "CRITICAL") {
          setLatestExplanation(processedData.explanation);
        } else {
          // Optional: Clear explanation if normal for a long time
          // setLatestExplanation("Monitoring traffic...");
        }

      } catch (e) {
        console.error("Error parsing WebSocket message:", e);
      }
    };

    ws.onclose = () => setConnectionStatus("DISCONNECTED");
    ws.onerror = (e) => console.error("WebSocket Error:", e);

    // Cleanup on unmount
    return () => ws.close();
  }, []);

  // 4. Derived State for UI Logic
  const currentData = dataPoints[dataPoints.length - 1] || { score: 0, status: "NORMAL" };
  const isCritical = currentData.status === "CRITICAL";

  return (
    <div className="min-h-screen bg-black text-green-500 font-mono p-4 md:p-8 overflow-hidden relative">
      
      {/* Background Grid Effect */}
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 pointer-events-none"></div>

      {/* HEADER */}
      <header className="flex flex-col md:flex-row justify-between items-center border-b border-green-900 pb-6 mb-8 z-10 relative">
        <div className="flex items-center gap-3">
          <Activity className="animate-pulse text-green-400" size={32} />
          <div>
            <h1 className="text-3xl font-bold tracking-[0.2em] text-white">ZERO-DAY IDS</h1>
            <p className="text-xs text-green-600 tracking-widest">REAL-TIME THREAT MONITORING</p>
          </div>
        </div>
        <div className={`mt-4 md:mt-0 px-4 py-1 rounded text-black font-bold text-sm tracking-widest transition-colors duration-500 ${
          connectionStatus === "CONNECTED" ? "bg-green-500 shadow-[0_0_10px_#22c55e]" : "bg-red-500"
        }`}>
          {connectionStatus}
        </div>
      </header>

      {/* MAIN DASHBOARD GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 z-10 relative">
        
        {/* 1. LIVE TRAFFIC GRAPH */}
        <div className="col-span-2 bg-gray-900/50 backdrop-blur border border-green-800 p-6 rounded-xl shadow-[0_0_20px_rgba(0,255,0,0.05)]">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold border-l-4 border-green-500 pl-3 text-white">ANOMALY SCORE STREAM</h2>
            <span className="text-xs text-gray-500">LIVE WEBSOCKET FEED</span>
          </div>
          
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={dataPoints}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1a2e1a" />
                <XAxis dataKey="timestamp" hide />
                <YAxis 
                  domain={[0, 1.2]} 
                  tick={{ fill: '#4ade80', fontSize: 12 }} 
                  axisLine={{ stroke: '#14532d' }}
                  tickLine={false}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#000', borderColor: '#22c55e', color: '#fff' }} 
                  itemStyle={{ color: '#4ade80' }}
                  labelStyle={{ color: '#86efac' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="score" 
                  stroke={isCritical ? "#ef4444" : "#22c55e"} 
                  strokeWidth={3} 
                  dot={false}
                  activeDot={{ r: 6, fill: isCritical ? "#ef4444" : "#22c55e" }}
                  isAnimationActive={true}
                  animationDuration={300}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 2. THREAT ALERT PANEL */}
        <div className={`p-8 rounded-xl border-2 flex flex-col items-center justify-center transition-all duration-500 relative overflow-hidden ${
          isCritical 
            ? "bg-red-950/30 border-red-500 shadow-[0_0_30px_rgba(239,68,68,0.3)]" 
            : "bg-green-950/10 border-green-800"
        }`}>
          {isCritical ? (
            <>
              <div className="absolute inset-0 bg-red-500/10 animate-pulse"></div>
              <ShieldAlert size={100} className="text-red-500 mb-6 z-10 drop-shadow-[0_0_10px_rgba(239,68,68,0.8)]" />
              <h2 className="text-4xl font-black text-red-500 z-10 tracking-widest text-center">INTRUSION DETECTED</h2>
              <div className="mt-4 px-4 py-2 bg-red-900/50 rounded text-red-200 z-10 border border-red-700">
                SCORE: {currentData.score.toFixed(4)}
              </div>
            </>
          ) : (
            <>
              <ShieldCheck size={100} className="text-green-500 mb-6 drop-shadow-[0_0_10px_rgba(34,197,94,0.5)]" />
              <h2 className="text-3xl font-bold text-green-500 tracking-widest">SYSTEM SECURE</h2>
              <p className="text-green-400/60 mt-2 text-sm">NO THREATS DETECTED</p>
            </>
          )}
        </div>

        {/* 3. AI EXPLANATION & LOGS */}
        <div className="col-span-1 lg:col-span-3 bg-black/80 border border-green-800 p-6 rounded-xl font-mono text-sm shadow-inner">
          <div className="flex items-center gap-3 text-green-400 mb-4 border-b border-green-900 pb-2">
            <Terminal size={18} /> 
            <span className="tracking-widest font-bold">LLM THREAT ANALYSIS LOGS</span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Left: Latest Explanation */}
            <div className="bg-gray-900/50 p-4 rounded border border-green-900/50">
               <h3 className="text-gray-500 text-xs mb-2 uppercase tracking-wider">Latest System Message</h3>
               <p className={`text-lg leading-relaxed ${isCritical ? "text-red-400 font-bold" : "text-gray-400"}`}>
                 {">"} {latestExplanation}
                 <span className="animate-pulse inline-block ml-1">_</span>
               </p>
            </div>

            {/* Right: Rolling Logs */}
            <div className="h-40 overflow-y-auto pr-2 custom-scrollbar">
              {dataPoints.slice().reverse().map((log, i) => (
                <div key={i} className="flex justify-between items-center py-2 border-b border-gray-900/50 hover:bg-gray-900/30 transition-colors px-2 rounded">
                  <span className="text-gray-600 text-xs">{log.timestamp}</span>
                  <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                    log.status === "CRITICAL" ? "bg-red-900/30 text-red-400 border border-red-900" : "text-green-600"
                  }`}>
                    {log.status === "CRITICAL" ? `⚠️ ${log.status}` : "OK"}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      
      {/* Footer / Status Bar */}
      <footer className="fixed bottom-0 left-0 w-full bg-gray-900 border-t border-green-900 py-1 px-4 flex justify-between text-[10px] text-gray-500 z-20">
        <div className="flex gap-4">
          <span>SERVER: 127.0.0.1:8000</span>
          <span>PROTOCOL: WEBSOCKET/SECURE</span>
        </div>
        <div className="flex items-center gap-1 text-green-700">
           <Lock size={10} /> ENCRYPTED CONNECTION
        </div>
      </footer>
    </div>
  );
}

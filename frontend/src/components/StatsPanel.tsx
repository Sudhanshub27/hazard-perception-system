"use client";

import { memo } from "react";
import { Activity, Car, HardHat, AlertCircle } from "lucide-react";
import { motion } from "framer-motion";

const StatsPanel = memo(({ objects }: { objects: any[] }) => {
  const peopleCount = objects.filter((d: any) => ['person', 'rider'].includes(d.class_name)).length;
  const vehicleCount = objects.filter((d: any) => ['car', 'truck', 'bus', 'motorcycle'].includes(d.class_name)).length;
  
  return (
    <div className="h-full flex flex-col bg-transparent">
      
      {/* Soft Header */}
      <div className="px-5 py-3 border-b border-borderSubtle flex items-center justify-between">
         <div className="flex items-center space-x-2">
           <Activity className="w-4 h-4 text-textMuted" />
           <span className="text-sm font-semibold text-white tracking-tight">Active Matrix</span>
         </div>
      </div>

      <div className="flex-1 px-5 py-3 flex flex-col justify-center space-y-2">
        
        <motion.div 
           whileHover={{ scale: 1.02 }} 
           className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5 transition-colors hover:bg-white/10"
        >
           <div className="flex items-center space-x-3">
             <div className="p-1.5 bg-sysAccent/10 rounded-lg">
               <Car className="w-4 h-4 text-sysAccent" />
             </div>
             <span className="text-sm font-medium text-gray-200 tracking-tight">Vehicular Targets</span>
           </div>
           <span className="text-lg font-mono font-bold text-white">{vehicleCount}</span>
        </motion.div>

        <motion.div 
           whileHover={{ scale: 1.02 }} 
           className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5 transition-colors hover:bg-white/10"
        >
           <div className="flex items-center space-x-3">
             <div className="p-1.5 bg-alertWarn/10 rounded-lg">
               <HardHat className="w-4 h-4 text-alertWarn" />
             </div>
             <span className="text-sm font-medium text-gray-200 tracking-tight">Pedestrian Assets</span>
           </div>
           <span className="text-lg font-mono font-bold text-white">{peopleCount}</span>
        </motion.div>

        {/* Global Track */}
        <div className="pt-2 flex items-center justify-between border-t border-borderSubtle mt-1 opacity-80">
           <span className="text-xs font-semibold text-textMuted uppercase tracking-wider">Total Output</span>
           <span className="text-sm font-bold text-gray-300">
             {objects.length} Entities
           </span>
        </div>

      </div>

    </div>
  );
});

StatsPanel.displayName = "StatsPanel";
export default StatsPanel;

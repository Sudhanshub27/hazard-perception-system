import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        surf: "#09090b",       // Zinc 950 - Extremely deep, essentially black but softer.
        panel: "#18181b",      // Zinc 900 - Premium elevated card layer.
        borderSubtle: "#27272a", // Zinc 800 - Barely there borders
        borderStrong: "#3f3f46", // Zinc 700 - Hover borders
        textMuted: "#a1a1aa",  // Zinc 400
        
        sysAccent: "#3b82f6",  // Blue 500
        signalDanger: "#ef4444",// Red 500
        alertWarn: "#eab308",  // Yellow 500
        safeGreen: "#22c55e",  // Green 500
      },
      fontFamily: {
        sans: ["var(--font-inter)", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains)", "Menlo", "Consolas", "monospace"],
      },
      boxShadow: {
        'soft': '0 4px 20px -2px rgba(0, 0, 0, 0.4)',
        'glow-danger': '0 0 40px rgba(239, 68, 68, 0.15)',
      }
    },
  },
  plugins: [],
};
export default config;

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

// Using Inter for a clean, premium sans-serif typography look
const inter = Inter({ 
  subsets: ["latin"], 
  variable: "--font-inter",
  display: "swap" 
});

export const metadata: Metadata = {
  title: "Hazard Perception | Command Center",
  description: "Real-time AI telemetry and inference streaming",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable}`}>
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}

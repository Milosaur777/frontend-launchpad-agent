"use client";

import { motion } from "framer-motion";

interface GodrayWindowProps {
  position?: "left" | "right";
  color?: "teal" | "crimson" | "gold";
  height?: string;
}

export default function GodrayWindow({
  position = "left",
  color = "teal",
  height = "h-96",
}: GodrayWindowProps) {
  const colorMap = {
    teal: {
      window: "from-teal-900/40 to-teal-800/20",
      light: "from-teal-400/20 via-teal-300/10 to-transparent",
      glow: "rgba(45, 212, 191, 0.3)",
    },
    crimson: {
      window: "from-red-900/40 to-red-800/20",
      light: "from-red-400/20 via-red-300/10 to-transparent",
      glow: "rgba(239, 68, 68, 0.3)",
    },
    gold: {
      window: "from-amber-900/40 to-amber-800/20",
      light: "from-amber-400/20 via-amber-300/10 to-transparent",
      glow: "rgba(251, 191, 36, 0.3)",
    },
  };

  const colors = colorMap[color];
  const positionClass = position === "left" ? "left-4 md:left-8" : "right-4 md:right-8";

  return (
    <div className={`absolute ${positionClass} top-1/4 ${height} w-24 md:w-32 lg:w-40 opacity-60`}>
      {/* Window frame */}
      <div className="relative w-full h-full">
        {/* Gothic arch window shape */}
        <svg
          viewBox="0 0 100 300"
          className="absolute inset-0 w-full h-full"
          preserveAspectRatio="none"
        >
          <defs>
            <linearGradient id={`windowGrad-${color}`} x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor={color === "teal" ? "#134e4a" : color === "crimson" ? "#7f1d1d" : "#92400e"} stopOpacity="0.6" />
              <stop offset="100%" stopColor={color === "teal" ? "#115e59" : color === "crimson" ? "#991b1b" : "#b45309"} stopOpacity="0.2" />
            </linearGradient>
          </defs>
          {/* Window frame */}
          <path
            d="M10 280 L10 80 Q50 10 90 80 L90 280 Z"
            fill={`url(#windowGrad-${color})`}
            stroke="#262626"
            strokeWidth="2"
          />
          {/* Window mullions */}
          <line x1="50" y1="80" x2="50" y2="280" stroke="#262626" strokeWidth="2" />
          <line x1="10" y1="150" x2="90" y2="150" stroke="#262626" strokeWidth="2" />
          <line x1="10" y1="220" x2="90" y2="220" stroke="#262626" strokeWidth="2" />
        </svg>

        {/* Godray light beams */}
        <motion.div
          className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full godray-shift"
          style={{ transformOrigin: "top center" }}
        >
          {/* Beam 1 - center */}
          <div
            className={`absolute top-0 left-1/2 -translate-x-1/2 w-16 h-full bg-gradient-to-b ${colors.light}`}
            style={{ filter: "blur(8px)" }}
          />
          {/* Beam 2 - left */}
          <div
            className={`absolute top-0 left-1/4 w-8 h-full bg-gradient-to-b ${colors.light} opacity-60`}
            style={{ filter: "blur(6px)", transform: "skewX(-10deg)" }}
          />
          {/* Beam 3 - right */}
          <div
            className={`absolute top-0 right-1/4 w-8 h-full bg-gradient-to-b ${colors.light} opacity-60`}
            style={{ filter: "blur(6px)", transform: "skewX(10deg)" }}
          />
        </motion.div>

        {/* Dust particles in the light */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {[...Array(8)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 rounded-full bg-white/40"
              style={{
                left: `${20 + Math.random() * 60}%`,
                top: `${20 + Math.random() * 60}%`,
              }}
              animate={{
                y: [0, -30, 0],
                x: [0, Math.random() * 10 - 5, 0],
                opacity: [0.2, 0.6, 0.2],
              }}
              transition={{
                duration: 4 + Math.random() * 4,
                repeat: Infinity,
                delay: Math.random() * 2,
                ease: "easeInOut",
              }}
            />
          ))}
        </div>

        {/* Glow at window top */}
        <div
          className="absolute top-0 left-1/2 -translate-x-1/2 w-20 h-20 rounded-full"
          style={{
            background: `radial-gradient(circle, ${colors.glow} 0%, transparent 70%)`,
            filter: "blur(10px)",
          }}
        />
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { getRiskLevel, getRiskLabel, getRiskColor } from "@/lib/utils";

interface RiskGaugeProps {
  score: number;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
  animated?: boolean;
}

export function RiskGauge({
  score,
  size = "md",
  showLabel = true,
  animated = true,
}: RiskGaugeProps) {
  const [displayScore, setDisplayScore] = useState(0);
  const riskLevel = getRiskLevel(score);
  const riskLabel = getRiskLabel(riskLevel);
  const riskColor = getRiskColor(riskLevel);

  useEffect(() => {
    if (animated) {
      const duration = 1500;
      const steps = 60;
      const increment = score / steps;
      let current = 0;
      let step = 0;

      const timer = setInterval(() => {
        step++;
        current = Math.min(step * increment, score);
        setDisplayScore(current);

        if (step >= steps) {
          clearInterval(timer);
        }
      }, duration / steps);

      return () => clearInterval(timer);
    } else {
      setDisplayScore(score);
    }
  }, [score, animated]);

  const sizes = {
    sm: {
      container: "w-32 h-32",
      stroke: 8,
      text: "text-2xl",
      label: "text-xs",
    },
    md: {
      container: "w-48 h-48",
      stroke: 12,
      text: "text-4xl",
      label: "text-sm",
    },
    lg: {
      container: "w-64 h-64",
      stroke: 16,
      text: "text-5xl",
      label: "text-base",
    },
  };

  const config = sizes[size];
  const radius = 90 - config.stroke;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (displayScore * circumference);

  const getStrokeColor = () => {
    if (displayScore < 0.3) return "#16a34a";
    if (displayScore < 0.6) return "#ca8a04";
    return "#dc2626";
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <div className={`relative ${config.container}`} role="img" aria-label={`Indicador de riesgo: ${riskLabel}, puntuación ${Math.round(displayScore * 100)} de 100`}>
        <svg className="transform -rotate-90" width="100%" height="100%" aria-hidden="true">
          <circle
            cx="50%"
            cy="50%"
            r={radius}
            stroke="#e5e7eb"
            strokeWidth={config.stroke}
            fill="none"
          />
          <circle
            cx="50%"
            cy="50%"
            r={radius}
            stroke={getStrokeColor()}
            strokeWidth={config.stroke}
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{
              transition: animated ? "stroke-dashoffset 0.3s ease" : "none",
            }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`font-bold ${config.text} ${riskColor}`}>
            {Math.round(displayScore * 100)}
          </span>
          <span className="text-sm text-gray-600">/ 100</span>
        </div>
      </div>
      {showLabel && (
        <div className="text-center">
          <p className={`font-semibold ${config.label} ${riskColor}`}>
            {riskLabel}
          </p>
        </div>
      )}
    </div>
  );
}


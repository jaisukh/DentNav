"use client";

type ScoreGaugeProps = {
  value: number;
  className?: string;
};

const R = 42;
const C = 2 * Math.PI * R;

export function ScoreGauge({ value, className = "" }: ScoreGaugeProps) {
  const pct = Math.min(100, Math.max(0, value));
  const dash = (C * pct) / 100;

  return (
    <div className={`relative flex flex-col items-center ${className}`}>
      <svg
        width={192}
        height={192}
        viewBox="0 0 100 100"
        className="-rotate-90"
        aria-hidden
      >
        <circle
          cx="50"
          cy="50"
          r={R}
          fill="none"
          stroke="#F1F5F9"
          strokeWidth="6"
          strokeLinecap="round"
        />
        <circle
          cx="50"
          cy="50"
          r={R}
          fill="none"
          stroke="#0EA5E9"
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={`${dash} ${C}`}
        />
      </svg>
      <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-display text-[48px] font-extrabold leading-none tracking-[-2.4px] text-slate-900">
          {Math.round(pct)}%
        </span>
        <span className="font-display mt-1 text-[10px] font-bold uppercase tracking-[2px] text-slate-400">
          Match Score
        </span>
      </div>
    </div>
  );
}

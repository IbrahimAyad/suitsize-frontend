import React from "react";

interface FitSelectorProps {
  fit: string;
  setFit: (fit: string) => void;
}

const options = [
  { label: "Slim", value: "Slim" },
  { label: "Regular", value: "Regular" },
  { label: "Relaxed", value: "Relaxed" },
];

const FitSelector: React.FC<FitSelectorProps> = ({ fit, setFit }) => (
  <div style={{ display: "flex", gap: 8, margin: "16px 0" }}>
    {options.map((opt) => (
      <button
        key={opt.value}
        onClick={() => setFit(opt.value)}
        style={{
          padding: "10px 24px",
          borderRadius: 24,
          border: fit === opt.value ? "2px solid #00bfff" : "1px solid #ccc",
          background: fit === opt.value ? "#e6f7ff" : "#fff",
          color: fit === opt.value ? "#0070f3" : "#222",
          fontWeight: fit === opt.value ? 700 : 400,
          cursor: "pointer",
          transition: "all 0.2s",
        }}
      >
        {opt.label}
      </button>
    ))}
  </div>
);

export default FitSelector; 
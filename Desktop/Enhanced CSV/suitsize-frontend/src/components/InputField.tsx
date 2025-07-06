import React from "react";

interface InputFieldProps {
  label: string;
  value: number;
  onChange: (val: number) => void;
  unit: string;
  min: number;
  max: number;
}

const InputField: React.FC<InputFieldProps> = ({ label, value, onChange, unit, min, max }) => (
  <div style={{ marginBottom: 16 }}>
    <label style={{ fontWeight: 600, display: "block", marginBottom: 4 }}>{label}</label>
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <input
        type="number"
        value={value}
        min={min}
        max={max}
        onChange={e => onChange(Number(e.target.value))}
        style={{
          width: 80,
          padding: "8px 12px",
          borderRadius: 8,
          border: "1px solid #ccc",
          fontSize: 16,
        }}
      />
      <span style={{ color: "#888", fontWeight: 500 }}>{unit}</span>
    </div>
  </div>
);

export default InputField; 
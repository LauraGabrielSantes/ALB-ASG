// ============================================================
// Componente: Historial
// ============================================================
// Muestra las últimas operaciones realizadas.
// ============================================================

import React from 'react';
import { HistorialEntry } from '../types';

interface HistorialProps {
  entries: HistorialEntry[];
  isOn: boolean;
  onClear: () => void;
}

const Historial: React.FC<HistorialProps> = ({ entries, isOn, onClear }) => {
  if (!isOn || entries.length === 0) return null;

  return (
    <div
      style={{
        marginTop: "16px",
        background: "#111827",
        borderRadius: "8px",
        padding: "10px",
        maxHeight: "150px",
        overflowY: "auto",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "6px",
        }}
      >
        <span style={{ color: "#9ca3af", fontSize: "0.7rem" }}>
          Historial ({entries.length})
        </span>
        <button
          onClick={onClear}
          style={{
            background: "none",
            border: "none",
            color: "#6b7280",
            fontSize: "0.65rem",
            cursor: "pointer",
            padding: "2px 6px",
          }}
        >
          Limpiar
        </button>
      </div>
      {entries.map((entry) => (
        <div
          key={entry.id}
          style={{
            color: "#00ffcc",
            fontFamily: "'Courier New', monospace",
            fontSize: "0.75rem",
            padding: "3px 0",
            borderBottom: "1px solid #1f2937",
          }}
        >
          {entry.a} {entry.operacion} {entry.b} = {entry.resultado}
        </div>
      ))}
    </div>
  );
};

export default Historial;

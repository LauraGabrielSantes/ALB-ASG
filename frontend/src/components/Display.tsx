// ============================================================
// Componente: Display
// ============================================================
// Componente presentacional puro. Solo recibe props y muestra.
// No tiene estado propio ni lógica de negocio.
// ============================================================

import React from 'react';

interface DisplayProps {
  value: string;
  isOn: boolean;
  loading: boolean;
}

const Display: React.FC<DisplayProps> = ({ value, isOn, loading }) => {
  return (
    <div className={`led-display ${isOn ? "on" : "off"}`}>
      {isOn ? (loading ? "..." : value) : ""}
    </div>
  );
};

export default Display;

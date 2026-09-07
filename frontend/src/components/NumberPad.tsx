// ============================================================
// Componente: NumberPad
// ============================================================
// Teclado numérico. Emite eventos hacia el padre.
// ============================================================

import React from 'react';

interface NumberPadProps {
  disabled: boolean;
  onNumber: (value: string) => void;
  onDot: () => void;
  onEqual: () => void;
  loading: boolean;
}

const NumberPad: React.FC<NumberPadProps> = ({
  disabled,
  onNumber,
  onDot,
  onEqual,
  loading,
}) => {
  const numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"];

  return (
    <div className="buttons_numbers">
      {numbers.map((num) => (
        <button key={num} disabled={disabled} onClick={() => onNumber(num)}>
          {num}
        </button>
      ))}
      <button disabled={disabled} onClick={onDot}>.</button>
      <button
        className="equal"
        disabled={disabled || loading}
        onClick={onEqual}
      >
        =
      </button>
    </div>
  );
};

export default NumberPad;

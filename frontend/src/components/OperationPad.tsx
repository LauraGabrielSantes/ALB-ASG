// ============================================================
// Componente: OperationPad
// ============================================================
// Botones de operaciones y CE. Emite eventos hacia el padre.
// ============================================================

import React from 'react';

interface OperationPadProps {
  disabled: boolean;
  onOperation: (op: string) => void;
  onClean: () => void;
}

const OperationPad: React.FC<OperationPadProps> = ({
  disabled,
  onOperation,
  onClean,
}) => {
  const operations = ["/", "*", "-", "+"];

  return (
    <div className="buttons_operations">
      <button disabled={disabled} onClick={onClean}>CE</button>
      {operations.map((op) => (
        <button key={op} disabled={disabled} onClick={() => onOperation(op)}>
          {op}
        </button>
      ))}
    </div>
  );
};

export default OperationPad;

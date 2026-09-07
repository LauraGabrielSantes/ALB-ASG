// ============================================================
// V4 - Calculadora: Errores + Historial
// ============================================================

import './Calculadora.css';
import { Display, NumberPad, OperationPad, StatusBar, Historial } from './components';
import { useAuth, useCalculadora } from './hooks';

const Calculator = () => {
  const imaLogo = new URL('./assets/image/mate.png', import.meta.url).href;

  const { token, isAuthenticated, error: authError, login, logout } = useAuth();
  const {
    display, isOn, loading,
    error: calcError, historial,
    handleNumber, handleDot, handleOperation,
    handleEqual, handleClean, handlePower, limpiarHistorial,
  } = useCalculadora(token, login, logout);

  const error = authError || calcError;

  return (
    <div className="calculator">
      <div className="labels">
        <div className="label">
          <img src={imaLogo} alt="icon" />
          CASIO
        </div>
        <div className="text"></div>
      </div>

      <Display value={display} isOn={isOn} loading={loading} />
      <StatusBar isOn={isOn} connected={isAuthenticated} error={error} />

      <div className="buttons_container">
        <div className="power">
          <button className="on_off" onClick={handlePower}>ON/OFF</button>
        </div>
        <div className="buttons">
          <NumberPad
            disabled={!isOn}
            onNumber={handleNumber}
            onDot={handleDot}
            onEqual={handleEqual}
            loading={loading}
          />
          <OperationPad
            disabled={!isOn}
            onOperation={handleOperation}
            onClean={handleClean}
          />
        </div>
      </div>

      <Historial entries={historial} isOn={isOn} onClear={limpiarHistorial} />
    </div>
  );
};

export default Calculator;

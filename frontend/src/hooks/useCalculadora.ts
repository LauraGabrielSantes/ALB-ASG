// ============================================================
// Custom Hook: useCalculadora (V4)
// ============================================================
// Mejoras:
// - Historial de operaciones
// - Reintento automático cuando el token expira (401)
// - Errores tipados con ApiError
// ============================================================

import { useState, useCallback } from 'react';
import * as api from '../services/api';
import { ApiError } from '../services/api';
import { HistorialEntry } from '../types';

const OPERACIONES: Record<string, string> = {
  "+": "sumar",
  "-": "restar",
  "*": "multiplicar",
  "/": "dividir",
};

const SIMBOLOS: Record<string, string> = {
  sumar: "+",
  restar: "−",
  multiplicar: "×",
  dividir: "÷",
};

interface UseCalculadoraReturn {
  display: string;
  isOn: boolean;
  loading: boolean;
  error: string | null;
  historial: HistorialEntry[];
  handleNumber: (value: string) => void;
  handleDot: () => void;
  handleOperation: (op: string) => void;
  handleEqual: () => Promise<void>;
  handleClean: () => void;
  handlePower: () => Promise<void>;
  limpiarHistorial: () => void;
}

export const useCalculadora = (
  token: string | null,
  login: () => Promise<string | null>,
  logout: () => void
): UseCalculadoraReturn => {
  const [display, setDisplay] = useState("0");
  const [primerNumero, setPrimerNumero] = useState<string | null>(null);
  const [operacion, setOperacion] = useState<string | null>(null);
  const [esperandoSegundo, setEsperandoSegundo] = useState(false);
  const [isOn, setIsOn] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [historial, setHistorial] = useState<HistorialEntry[]>([]);
  const [idCounter, setIdCounter] = useState(1);

  const handleNumber = useCallback((value: string) => {
    setError(null);
    if (esperandoSegundo) {
      setDisplay(value);
      setEsperandoSegundo(false);
    } else {
      setDisplay((prev) => (prev === "0" ? value : prev + value));
    }
  }, [esperandoSegundo]);

  const handleDot = useCallback(() => {
    setDisplay((prev) => (prev.includes(".") ? prev : prev + "."));
  }, []);

  const handleOperation = useCallback((op: string) => {
    setPrimerNumero(display);
    setOperacion(op);
    setEsperandoSegundo(true);
    setError(null);
  }, [display]);

  const handleClean = useCallback(() => {
    setDisplay("0");
    setPrimerNumero(null);
    setOperacion(null);
    setError(null);
  }, []);

  const limpiarHistorial = useCallback(() => {
    setHistorial([]);
  }, []);

  const handleEqual = useCallback(async () => {
    if (!primerNumero || !operacion) return;

    const a = parseFloat(primerNumero);
    const b = parseFloat(display);
    const endpoint = OPERACIONES[operacion];
    if (!endpoint) return;

    let tokenActual = token;
    if (!tokenActual) {
      tokenActual = await login();
      if (!tokenActual) return;
    }

    try {
      setLoading(true);
      const fn = api[endpoint as keyof typeof api] as Function;
      const data = await fn({ a, b }, tokenActual);
      setDisplay(String(data.resultado));

      // Agregar al historial
      const entry: HistorialEntry = {
        id: idCounter,
        operacion: SIMBOLOS[endpoint] || operacion,
        a,
        b,
        resultado: data.resultado,
        timestamp: new Date(),
      };
      setHistorial((prev) => [entry, ...prev]);
      setIdCounter((prev) => prev + 1);
    } catch (err: any) {
      // Si el token expiró, reintentamos con login
      if (err instanceof ApiError && err.statusCode === 401) {
        const nuevoToken = await login();
        if (nuevoToken) {
          try {
            const fn = api[endpoint as keyof typeof api] as Function;
            const data = await fn({ a, b }, nuevoToken);
            setDisplay(String(data.resultado));
            return;
          } catch (retryErr: any) {
            setError(retryErr.message);
          }
        }
      }
      setError(err.message);
    } finally {
      setLoading(false);
      setPrimerNumero(null);
      setOperacion(null);
    }
  }, [primerNumero, operacion, display, token, login, idCounter]);

  const handlePower = useCallback(async () => {
    if (!isOn) {
      await login();
    } else {
      logout();
    }
    setDisplay("0");
    setPrimerNumero(null);
    setOperacion(null);
    setError(null);
    setIsOn(!isOn);
  }, [isOn, login, logout]);

  return {
    display, isOn, loading, error, historial,
    handleNumber, handleDot, handleOperation,
    handleEqual, handleClean, handlePower, limpiarHistorial,
  };
};

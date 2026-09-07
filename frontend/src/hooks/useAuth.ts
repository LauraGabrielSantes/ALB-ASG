// ============================================================
// Custom Hook: useAuth
// ============================================================
// Encapsula toda la lógica de autenticación:
// - Login / logout
// - Almacenamiento del token
// - Estado de conexión
//
// Ventajas de usar un custom hook:
// - Reutilizable en cualquier componente
// - Testeable de forma aislada
// - Separa la lógica del componente visual
// ============================================================

import { useState, useCallback } from 'react';
import * as api from '../services/api';

interface UseAuthReturn {
  token: string | null;
  isAuthenticated: boolean;
  error: string | null;
  login: () => Promise<string | null>;
  logout: () => void;
}

export const useAuth = (): UseAuthReturn => {
  const [token, setToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const login = useCallback(async (): Promise<string | null> => {
    try {
      const resp = await api.login("admin", "admin123");
      setToken(resp.access_token);
      setError(null);
      return resp.access_token;
    } catch {
      setError("No se pudo conectar con la API");
      setToken(null);
      return null;
    }
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setError(null);
  }, []);

  return {
    token,
    isAuthenticated: !!token,
    error,
    login,
    logout,
  };
};

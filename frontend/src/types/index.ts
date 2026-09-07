export interface OperacionRequest {
  a: number;
  b: number;
}

export interface OperacionResponse {
  operacion: string;
  a: number;
  b: number;
  resultado: number;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// NUEVO: entrada del historial de operaciones
export interface HistorialEntry {
  id: number;
  operacion: string;
  a: number;
  b: number;
  resultado: number;
  timestamp: Date;
}

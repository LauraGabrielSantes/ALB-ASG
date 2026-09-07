// ============================================================
// Tests del servicio API
// ============================================================
// Usamos jest.fn() para mockear fetch.
// Así probamos la lógica del servicio sin backend real.
// ============================================================

import { login, sumar, dividir, ApiError } from './services/api';

// Mock global de fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('API Service', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  describe('login', () => {
    test('retorna token con credenciales correctas', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ access_token: 'test-token', token_type: 'bearer' }),
      });

      const result = await login('admin', 'admin123');
      expect(result.access_token).toBe('test-token');
    });

    test('lanza error con credenciales incorrectas', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      await expect(login('bad', 'creds')).rejects.toThrow('Credenciales incorrectas');
    });
  });

  describe('sumar', () => {
    test('retorna el resultado de la suma', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          operacion: 'suma',
          a: 10,
          b: 5,
          resultado: 15,
        }),
      });

      const result = await sumar({ a: 10, b: 5 }, 'test-token');
      expect(result.resultado).toBe(15);
      expect(result.operacion).toBe('suma');
    });
  });

  describe('dividir', () => {
    test('lanza ApiError 400 al dividir entre cero', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'No se puede dividir entre cero' }),
      });

      try {
        await dividir({ a: 10, b: 0 }, 'test-token');
        fail('Debería haber lanzado error');
      } catch (err) {
        expect(err).toBeInstanceOf(ApiError);
        expect((err as ApiError).statusCode).toBe(400);
      }
    });

    test('lanza ApiError 401 con token expirado', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Token inválido o expirado' }),
      });

      try {
        await dividir({ a: 10, b: 2 }, 'expired-token');
        fail('Debería haber lanzado error');
      } catch (err) {
        expect(err).toBeInstanceOf(ApiError);
        expect((err as ApiError).statusCode).toBe(401);
      }
    });
  });
});

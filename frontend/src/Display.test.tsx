// ============================================================
// Tests del componente Display
// ============================================================
// Verificamos que el display:
// - Muestra el valor cuando está encendido
// - Muestra "..." cuando está cargando
// - No muestra nada cuando está apagado
// ============================================================

import React from 'react';
import { render, screen } from '@testing-library/react';
import Display from './components/Display';

describe('Display', () => {
  test('muestra el valor cuando está encendido', () => {
    render(<Display value="42" isOn={true} loading={false} />);
    expect(screen.getByText('42')).toBeInTheDocument();
  });

  test('muestra "..." cuando está cargando', () => {
    render(<Display value="42" isOn={true} loading={true} />);
    expect(screen.getByText('...')).toBeInTheDocument();
  });

  test('no muestra nada cuando está apagado', () => {
    const { container } = render(
      <Display value="42" isOn={false} loading={false} />
    );
    const display = container.querySelector('.led-display');
    expect(display).toHaveTextContent('');
  });

  test('tiene clase "on" cuando está encendido', () => {
    const { container } = render(
      <Display value="0" isOn={true} loading={false} />
    );
    const display = container.querySelector('.led-display');
    expect(display).toHaveClass('on');
  });

  test('tiene clase "off" cuando está apagado', () => {
    const { container } = render(
      <Display value="0" isOn={false} loading={false} />
    );
    const display = container.querySelector('.led-display');
    expect(display).toHaveClass('off');
  });
});

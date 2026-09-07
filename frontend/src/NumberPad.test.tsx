// ============================================================
// Tests del componente NumberPad
// ============================================================

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import NumberPad from './components/NumberPad';

describe('NumberPad', () => {
  const defaultProps = {
    disabled: false,
    onNumber: jest.fn(),
    onDot: jest.fn(),
    onEqual: jest.fn(),
    loading: false,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renderiza los 10 botones numéricos', () => {
    render(<NumberPad {...defaultProps} />);
    for (let i = 0; i <= 9; i++) {
      expect(screen.getByText(String(i))).toBeInTheDocument();
    }
  });

  test('llama onNumber al hacer click en un número', () => {
    render(<NumberPad {...defaultProps} />);
    fireEvent.click(screen.getByText('5'));
    expect(defaultProps.onNumber).toHaveBeenCalledWith('5');
  });

  test('llama onDot al hacer click en el punto', () => {
    render(<NumberPad {...defaultProps} />);
    fireEvent.click(screen.getByText('.'));
    expect(defaultProps.onDot).toHaveBeenCalled();
  });

  test('llama onEqual al hacer click en =', () => {
    render(<NumberPad {...defaultProps} />);
    fireEvent.click(screen.getByText('='));
    expect(defaultProps.onEqual).toHaveBeenCalled();
  });

  test('botones deshabilitados cuando disabled=true', () => {
    render(<NumberPad {...defaultProps} disabled={true} />);
    const btn5 = screen.getByText('5');
    expect(btn5).toBeDisabled();
  });

  test('botón = deshabilitado cuando loading=true', () => {
    render(<NumberPad {...defaultProps} loading={true} />);
    const btnEqual = screen.getByText('=');
    expect(btnEqual).toBeDisabled();
  });
});

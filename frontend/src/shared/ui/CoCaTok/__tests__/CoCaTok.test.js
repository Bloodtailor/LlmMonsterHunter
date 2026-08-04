// CoCaTok ceremony tests - the pickup click must END in a visible
// collected keepsake, never an invisible hole. Regression coverage for a
// live-playtest bug: the old ceremony kept `forwards`-filled explosion
// styles (opacity 0) on an element that still occupied layout, so the
// victory screen showed a blank gap where the claimed token should be.
//
// WHY bare react-dom instead of @testing-library/react: the project has
// no testing-library dependency - these tests use only what
// react-scripts already ships (same pattern as ExpandableTable tests).

import React from 'react';
import { createRoot } from 'react-dom/client';
import { act } from 'react-dom/test-utils';
import CoCaTok from '../CoCaTok.js';

// createRoot outside of testing-library requires opting in to act()
global.IS_REACT_ACT_ENVIRONMENT = true;

// The explosion effect renders fine in jsdom, but its animation frames
// are irrelevant here - fake timers drive the ceremony's two setTimeouts
jest.useFakeTimers();

function renderCoCaTok(props = {}) {
  const container = document.createElement('div');
  document.body.appendChild(container);
  const root = createRoot(container);
  act(() => {
    root.render(<CoCaTok color="blue-ice" emoji="🏮" {...props} />);
  });
  return { container, root };
}

afterEach(() => {
  document.body.innerHTML = '';
});

test('click runs spin then explode, then settles into a visible collected keepsake', () => {
  const onActivate = jest.fn();
  const { container } = renderCoCaTok({ onActivate });
  const card = container.querySelector('.cocatok');

  act(() => {
    card.click();
  });
  expect(card.className).toContain('cocatok-spinning');

  // Spin completes -> explosion starts
  act(() => {
    jest.advanceTimersByTime(3000);
  });
  expect(card.className).toContain('cocatok-exploding');

  // Explosion fades -> the card SETTLES, it does not vanish
  act(() => {
    jest.advanceTimersByTime(1500);
  });
  expect(onActivate).toHaveBeenCalledWith('blue-ice', '🏮');
  expect(card.className).toContain('cocatok-collected');
  expect(card.className).not.toContain('cocatok-exploding');
  expect(card.className).not.toContain('cocatok-spinning');
  // Still a real, visible element in the layout
  expect(container.querySelector('.cocatok')).not.toBeNull();
  expect(container.querySelector('.front-emoji').textContent).toBe('🏮');
});

test('a collected keepsake ignores further clicks', () => {
  const onActivate = jest.fn();
  const { container } = renderCoCaTok({ onActivate });
  const card = container.querySelector('.cocatok');

  act(() => {
    card.click();
  });
  act(() => {
    jest.advanceTimersByTime(4500);
  });
  expect(onActivate).toHaveBeenCalledTimes(1);

  act(() => {
    card.click();
  });
  act(() => {
    jest.advanceTimersByTime(4500);
  });
  expect(onActivate).toHaveBeenCalledTimes(1);
  expect(card.className).toContain('cocatok-collected');
});

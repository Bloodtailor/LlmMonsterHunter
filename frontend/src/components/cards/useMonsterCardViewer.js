// useMonsterCardViewer Hook - Simplifies MonsterCard + MonsterCardViewer usage
// Encapsulates all viewer state management and provides pre-configured components
// Reduces boilerplate from 4 things to just 2!

import { useState, useMemo } from 'react';
import MonsterCard from './MonsterCard.js';
import MonsterCardViewer from './MonsterCardViewer.js';

/**
 * Custom hook for MonsterCard with built-in viewer functionality
 * Manages viewer state and provides pre-configured components
 *
 * @returns {object} Hook result with MonsterCard component and viewer
 */
export function useMonsterCardViewer() {
  // Internal state management - hidden from component
  const [viewingMonster, setViewingMonster] = useState(null);

  // Close viewer handler
  const closeViewer = () => setViewingMonster(null);

  // Pre-configured MonsterCard component that handles expand automatically
  // Memoized so it keeps the same component identity across re-renders -
  // otherwise React remounts every card (losing flip state) each render
  const MonsterCardWithViewer = useMemo(() => {
    return (props) => (
      <MonsterCard
        {...props}
        onExpandCard={setViewingMonster} // Automatically wired up!
      />
    );
  }, []);

  // Pre-rendered viewer (conditionally shown)
  const viewer = viewingMonster ? (
    <MonsterCardViewer monster={viewingMonster} onClose={closeViewer} />
  ) : null;

  return {
    // Pre-configured MonsterCard component - just pass your props!
    MonsterCard: MonsterCardWithViewer,

    // Pre-rendered viewer - just include in your JSX
    viewer,

    // Optional: Direct access to state/handlers if needed
    viewingMonster,
    openViewer: setViewingMonster,
    closeViewer,
    isViewerOpen: !!viewingMonster,
  };
}

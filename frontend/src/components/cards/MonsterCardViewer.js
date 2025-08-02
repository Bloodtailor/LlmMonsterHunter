// Monster Card Viewer Component - Refactored with Clean Architecture
// Full-size modal display for monster cards with no circular dependencies
// Uses callback pattern for clean separation of concerns

import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import MonsterCard from './MonsterCard.js';
import './monsterCardViewer.css'
import { IconButton } from '../../shared/ui/index.js';
import { CARD_SIZES } from '../../shared/constants/constants.js';

function MonsterCardViewer({ 
  isOpen = true, // Default to open since parent controls visibility
  onClose, 
  monster,
  startOnBack = false
}) {
  // Handle escape key to close modal
  useEffect(() => {
    const handleEscapeKey = (event) => {
      if (event.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscapeKey);
      // Prevent body scrolling when modal is open
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscapeKey);
      document.body.style.overflow = 'auto';
    };
  }, [isOpen, onClose]);

  // Don't render if not open or no monster
  if (!isOpen || !monster) return null;

  // Handle clicking on backdrop to close
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return createPortal(
    <div 
      className="monster-card-viewer-overlay"
      onClick={handleBackdropClick}
    >
      <div className="monster-card-viewer-container">
        {/* Close Button - Using refactored IconButton */}
        <IconButton
          icon="✕"
          variant="secondary"
          onClick={onClose}
          ariaLabel="Close monster card viewer"
          className="monster-card-viewer-close"
        />

        {/* Full-Size Monster Card */}
        <div className="monster-card-viewer-content">
          <MonsterCard
            monster={monster}
            size={CARD_SIZES.XL} // Updated to use new constant instead of "full"
          />
        </div>
      </div>
    </div>,
    document.body
  );
}

export default MonsterCardViewer;
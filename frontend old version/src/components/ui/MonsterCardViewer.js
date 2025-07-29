// Monster Card Viewer Component - Full-Size Modal Display
// Displays a complete flippable monster card at responsive full-size in a modal overlay
// Upgraded replacement for CardArtViewer with full card functionality

import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import MonsterCard from '../game/MonsterCard';

function MonsterCardViewer({ 
  isOpen, 
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

  // Don't render if not open
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
        {/* Close Button */}
        <button 
          className="monster-card-viewer-close"
          onClick={onClose}
          aria-label="Close monster card viewer"
        >
          ✕
        </button>

        {/* Full-Size Monster Card */}
        <div className="monster-card-viewer-content">
          <MonsterCard
            monster={monster}
            size="fullscreen"
            showPartyToggle={false}
            onAbilityGenerate={null}
          />
        </div>
      </div>
    </div>,
    document.body
  );
}

export default MonsterCardViewer;
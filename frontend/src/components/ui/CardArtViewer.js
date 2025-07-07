// Card Art Viewer Component - Full-Size Modal Display
// Displays monster card art at full resolution (1028x1028) in a modal overlay
// Reusable component with grey background and close button

import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';

function CardArtViewer({ 
  isOpen, 
  onClose, 
  artUrl, 
  monsterName = 'Monster',
  monsterSpecies = ''
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
  if (!isOpen) return null;

  // Handle clicking on backdrop to close
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  // Handle image load error
  const handleImageError = () => {
    console.error('Failed to load card art:', artUrl);
  };

  return createPortal(
    <div 
      className="card-art-viewer-overlay"
      onClick={handleBackdropClick}
    >
      <div className="card-art-viewer-container">
        {/* Close Button */}
        <button 
          className="card-art-viewer-close"
          onClick={onClose}
          aria-label="Close card art viewer"
        >
          ✕
        </button>

        {/* Card Art Image */}
        <div className="card-art-viewer-content">
          {artUrl ? (
            <img 
              src={artUrl}
              alt={`${monsterName} card art`}
              className="card-art-viewer-image"
              onError={handleImageError}
            />
          ) : (
            <div className="card-art-viewer-placeholder">
              <div className="placeholder-icon">🎨</div>
              <p>No card art available</p>
            </div>
          )}
          
          {/* Image Info */}
          <div className="card-art-viewer-info">
            <h3>{monsterName}</h3>
            {monsterSpecies && <p>{monsterSpecies}</p>}
          </div>
        </div>
      </div>
    </div>,
    document.body
  );
}

export default CardArtViewer;
// Flippable Card Component - REUSABLE FOR MONSTERS, ITEMS, AND MORE
// 3D flip animation with customizable front and back content
// Supports multiple "sides" that can be expanded later

import React, { useState } from 'react';

function FlippableCard({ 
  frontContent, 
  backContent, 
  className = '', 
  cardId = null,
  onFlip = null,
  disabled = false,
  size = 'normal' // 'small', 'normal', 'large'
}) {
  const [isFlipped, setIsFlipped] = useState(false);
  const [currentSide, setCurrentSide] = useState(0); // For future multi-side support

  const handleFlip = () => {
    if (disabled) return;

    const newFlipped = !isFlipped;
    setIsFlipped(newFlipped);
    
    // Call callback if provided
    if (onFlip) {
      onFlip(newFlipped, cardId);
    }
  };

  const cardSizeClass = `flippable-card-${size}`;

  return (
    <div className={`flippable-card-container ${cardSizeClass} ${className}`}>
      <div 
        className={`flippable-card ${isFlipped ? 'flipped' : ''} ${disabled ? 'disabled' : ''}`}
        onClick={handleFlip}
      >
        {/* Front Side */}
        <div className="card-front">
          {frontContent}
        </div>
        
        {/* Back Side */}
        <div className="card-back">
          {backContent}
        </div>
      </div>
      
      {/* Optional flip indicator */}
      {!disabled && (
        <div className="flip-indicator">
          <span className="flip-hint">
            {isFlipped ? '↻ Flip to front' : '↻ Flip for details'}
          </span>
        </div>
      )}
    </div>
  );
}

export default FlippableCard;
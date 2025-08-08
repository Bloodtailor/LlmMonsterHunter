// ExpandableContent Component - Wrapper for expanded row content
// Handles animation and provides clean container for user-provided content
// Supports both animated and instant expansion modes

import React, { useRef, useEffect, useState } from 'react';

/**
 * Wrapper component for expandable row content
 * Handles expansion animations and provides clean styling
 * 
 * @param {object} props - ExpandableContent props
 * @param {object} props.row - Row data object
 * @param {Function} props.renderContent - Function to render the content: (row) => ReactElement
 * @param {boolean} props.animateExpansion - Whether to animate the expansion
 * @returns {React.ReactElement} ExpandableContent component
 */
function ExpandableContent({ 
  row, 
  renderContent, 
  animateExpansion = true 
}) {
  
  const contentRef = useRef(null);
  const [isAnimating, setIsAnimating] = useState(animateExpansion);
  
  // Handle animation on mount if enabled
  useEffect(() => {
    if (!animateExpansion || !contentRef.current) {
      setIsAnimating(false);
      return;
    }
    
    const element = contentRef.current;
    
    // Get the natural height of the content
    element.style.height = 'auto';
    const naturalHeight = element.scrollHeight;
    
    // Start from 0 height and animate to natural height
    element.style.height = '0px';
    element.style.overflow = 'hidden';
    
    // Force a reflow to ensure the 0 height is applied
    // eslint-disable-next-line no-unused-expressions
    element.offsetHeight;
    
    // Animate to natural height
    element.style.transition = 'height var(--transition-medium) ease-out';
    element.style.height = `${naturalHeight}px`;
    
    // Clean up after animation completes
    const handleTransitionEnd = () => {
      element.style.height = 'auto';
      element.style.overflow = 'visible';
      element.style.transition = '';
      setIsAnimating(false);
    };
    
    element.addEventListener('transitionend', handleTransitionEnd, { once: true });
    
    // Cleanup function
    return () => {
      element.removeEventListener('transitionend', handleTransitionEnd);
    };
  }, [animateExpansion]);
  
  // Build CSS classes
  const contentClasses = [
    'expandable-content',
    isAnimating && 'expandable-content-animating'
  ].filter(Boolean).join(' ');
  
  // Render user content with error boundary
  const renderUserContent = () => {
    try {
      return renderContent(row);
    } catch (error) {
      console.error('Error rendering expanded content:', error);
      return (
        <div className="expandable-content-error">
          <div style={{ 
            color: 'var(--color-red-intense)', 
            fontSize: 'var(--font-size-sm)',
            padding: '16px' 
          }}>
            ⚠️ Error loading expanded content
          </div>
        </div>
      );
    }
  };
  
  return (
    <div 
      ref={contentRef}
      className={contentClasses}
      role="region"
      aria-label="Expanded row details"
    >
      <div className="expandable-content-inner">
        {renderUserContent()}
      </div>
    </div>
  );
}

export default ExpandableContent;
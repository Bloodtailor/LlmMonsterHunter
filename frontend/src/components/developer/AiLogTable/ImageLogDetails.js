// ImageLogDetails - Displays detailed image log information in expanded row
// Shows image info, preview, and generation metadata
// Used by AiLogTable when expanding image generation logs

import React from 'react';

/**
 * ImageLogDetails - Displays detailed image log information
 * @param {object} props - Component props
 * @param {object} props.log - Generation log object
 * @returns {React.ReactElement} ImageLogDetails component
 */
function ImageLogDetails({ log }) {
  const imageLog = log.imageLogId;
  
  if (!imageLog) {
    return (
      <div style={{ padding: '16px', color: 'var(--text-dim)' }}>
        No image log details available.
      </div>
    );
  }

  return (
    <div style={{ padding: '16px', background: 'var(--background-dark)' }}>
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
        gap: '16px'
      }}>
        {/* Image Info */}
        <div>
          <h4 style={{ margin: '0 0 8px 0', color: 'var(--text-light)' }}>Image Details</h4>
          <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-dim)' }}>
            <div><strong>Filename:</strong> {imageLog.imageFilename || 'Unknown'}</div>
            <div><strong>Path:</strong> {imageLog.imagePath || 'Unknown'}</div>
          </div>
        </div>

        {/* Image Preview */}
        {imageLog.imagePath && (
          <div>
            <h4 style={{ margin: '0 0 8px 0', color: 'var(--text-light)' }}>Preview</h4>
            <img
              src={imageLog.imagePath}
              alt={imageLog.imageFilename || 'Generated image'}
              style={{
                maxWidth: '200px',
                maxHeight: '200px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--background-light)'
              }}
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'block';
              }}
            />
            <div style={{ display: 'none', color: 'var(--text-dim)' }}>
              Image not found
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ImageLogDetails;
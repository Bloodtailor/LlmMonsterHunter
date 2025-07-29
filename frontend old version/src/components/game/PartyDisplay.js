// Party Display Component - REUSABLE
// Displays active party monsters with configurable options
// Used in both HomeBase and Dungeon screens with different configurations

import React from 'react';
import MonsterCard from './MonsterCard';

function PartyDisplay({
  // Core data
  partyMonsters = [],
  
  // Display options
  title = "Active Party",
  showHeader = true,
  showPartyToggles = false,
  showActions = false,
  
  // Empty state customization
  emptyTitle = "No Party Members",
  emptyMessage = "Party members will appear here",
  emptyIcon = "👥",
  
  // Event handlers (optional)
  onPartyToggle = null,
  onActionClick = null,
  
  // Status info (optional)
  partyReady = false,
  updating = false,
  maxPartySize = 4,
  
  // Additional props
  className = ""
}) {
  const partyCount = partyMonsters.length;

  return (
    <section className={`party-display-section ${className}`}>
      {/* Section Header */}
      {showHeader && (
        <div className="party-display-header">
          <h2>{title} ({partyCount}/{maxPartySize})</h2>
          {showActions && (
            <div className="party-status">
              {partyReady ? (
                <span className="status-badge status-success">✅ Ready for Dungeon</span>
              ) : (
                <span className="status-badge status-pending">⏳ Add Monsters to Party</span>
              )}
            </div>
          )}
        </div>
      )}

      {/* Party Content */}
      <div className="party-display-container">
        {partyCount === 0 ? (
          /* Empty State */
          <div className="party-display-empty">
            <div className="party-empty-content">
              <div className="empty-icon">{emptyIcon}</div>
              <h3>{emptyTitle}</h3>
              <p>{emptyMessage}</p>
            </div>
          </div>
        ) : (
          /* Party Grid */
          <div className="party-display-grid">
            {partyMonsters.map(monster => (
              <div key={monster.id} className="party-monster-wrapper">
                <MonsterCard
                  monster={monster}
                  size="small"
                  showPartyToggle={showPartyToggles}
                  isInParty={true}
                  isPartyFull={false}
                  onPartyToggle={onPartyToggle}
                  partyDisabled={updating}
                />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      {showActions && (
        <div className="party-display-actions">
          <button 
            onClick={onActionClick}
            disabled={!partyReady || updating}
            className={`btn btn-lg ${partyReady ? 'btn-primary' : 'btn-secondary'}`}
          >
            {updating ? '⏳ Updating Party...' : 
             partyReady ? '🏰 Enter Dungeon' : '⏳ Form Party First'}
          </button>
        </div>
      )}
    </section>
  );
}

export default PartyDisplay;
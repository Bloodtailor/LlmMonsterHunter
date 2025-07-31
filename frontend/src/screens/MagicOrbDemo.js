// Treasure Card Usage Examples - See the magic in action!

import React from 'react';
import { TreasureCard, TREASURE_TYPES, TREASURE_SIZES } from './../shared/ui/MagicOrbs';

function MagicOrbDemo() {
  const handleHeal = () => {
    console.log('💚 Player healed for 50 HP!');
    // Trigger healing logic
  };

  const handleFireSpell = () => {
    console.log('🔥 Cast fireball spell!');
    // Trigger fire spell
  };

  const handleSpeedBoost = () => {
    console.log('💨 Speed boost activated!');
    // Trigger speed buff
  };

  return (
    <div className="treasure-card-showcase">
      <h2>Interactive Treasure Cards</h2>
      
      {/* Different Types */}
      <div className="treasure-collection">
        <TreasureCard 
          type={TREASURE_TYPES.HEALTH} 
          size={TREASURE_SIZES.LG}
          onActivate={handleHeal}
        />
        
        <TreasureCard 
          type={TREASURE_TYPES.FIRE} 
          size={TREASURE_SIZES.LG}
          onActivate={handleFireSpell}
        />
        
        <TreasureCard 
          type={TREASURE_TYPES.ICE} 
          size={TREASURE_SIZES.LG}
          emoji="❄️"
        />
        
        <TreasureCard 
          type={TREASURE_TYPES.LIGHTNING} 
          size={TREASURE_SIZES.LG}
        />
        
        <TreasureCard 
          type={TREASURE_TYPES.MAGIC} 
          size={TREASURE_SIZES.LG}
        />
        
        <TreasureCard 
          type={TREASURE_TYPES.POISON} 
          size={TREASURE_SIZES.LG}
        />
      </div>

      {/* Different Sizes */}
      <div className="size-showcase">
        <TreasureCard type="health" size={TREASURE_SIZES.SM} />
        <TreasureCard type="health" size={TREASURE_SIZES.MD} />
        <TreasureCard type="health" size={TREASURE_SIZES.LG} />
        <TreasureCard type="health" size={TREASURE_SIZES.XL} />
      </div>

      {/* Custom Cards */}
      <div className="custom-treasures">
        <TreasureCard 
          type="speed" 
          emoji="🏃‍♂️" 
          onActivate={handleSpeedBoost}
        />
        
        <TreasureCard 
          type="shield" 
          emoji="🛡️" 
          onActivate={() => console.log('🛡️ Shield activated!')}
        />
      </div>

      {/* Disabled State */}
      <TreasureCard 
        type="magic" 
        disabled 
        size={TREASURE_SIZES.LG}
      />
    </div>
  );
}

export default MagicOrbDemo;
// Treasure Card Usage Examples - See the magic in action!

import React from 'react';
import CoCaTok, {COCATOK_SIZES, COCATOK_TYPES} from '../shared/ui/CoCaTok/CoCaTok';

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
    <div >
      <h2>Collectable Card Tokens</h2>
      
      {/* Different Types */}
      <div>
        <CoCaTok 
          type={COCATOK_TYPES.HEALTH} 
          size={COCATOK_SIZES.LG}
          onActivate={handleHeal}
        />
        
        <CoCaTok 
          type={COCATOK_TYPES.FIRE} 
          size={COCATOK_SIZES.LG}
          onActivate={handleFireSpell}
        />
        
        <CoCaTok 
          type={COCATOK_TYPES.ICE} 
          size={COCATOK_SIZES.LG}
          emoji="❄️"
        />
        
        <CoCaTok 
          type={COCATOK_TYPES.LIGHTNING} 
          size={COCATOK_SIZES.LG}
        />
        
        <CoCaTok 
          type={COCATOK_TYPES.MAGIC} 
          size={COCATOK_SIZES.LG}
        />
        
        <CoCaTok 
          type={COCATOK_TYPES.POISON} 
          size={COCATOK_SIZES.LG}
        />
      </div>

      {/* Different Sizes */}
      <div >
        <CoCaTok type="health" size={COCATOK_SIZES.SM} />
        <CoCaTok type="health" size={COCATOK_SIZES.MD} />
        <CoCaTok type="health" size={COCATOK_SIZES.LG} />
        <CoCaTok type="health" size={COCATOK_SIZES.XL} />
      </div>

      {/* Custom Cards */}
      <div >
        <CoCaTok 
          type="speed" 
          emoji="🏃‍♂️" 
          onActivate={handleSpeedBoost}
        />
        
        <CoCaTok 
          type="shield" 
          emoji="🛡️" 
          onActivate={() => console.log('🛡️ Shield activated!')}
        />
      </div>

      {/* Disabled State */}
      <CoCaTok 
        type="magic" 
        disabled 
        size={COCATOK_SIZES.LG}
      />
    </div>
  );
}

export default MagicOrbDemo;
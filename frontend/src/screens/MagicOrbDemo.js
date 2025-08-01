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
          color='red-intense' 
          emoji='🔥'
          size={COCATOK_SIZES.LG}
        />
        
        <CoCaTok 
          color='rainbow-6'
          size={COCATOK_SIZES.LG}
          emoji="🌈"
        />
        
        <CoCaTok 
          color='blue-electric'
          size={COCATOK_SIZES.LG}
          emoji="❄️"
        />
        
        <CoCaTok 
          size={COCATOK_SIZES.LG}
          color='gold-bright'
          emoji='🔮'
        />
        
        <CoCaTok 
          size={COCATOK_SIZES.LG}
          color='green-forest'
          emoji='=D'
        />
        
        <CoCaTok 
          size={COCATOK_SIZES.LG}
          color='white-pearl'
          emoji=''
        />
      </div>

      {/* Different Sizes */}
      <div >
        <CoCaTok size={COCATOK_SIZES.SM} />
        <CoCaTok size={COCATOK_SIZES.MD} />
        <CoCaTok size={COCATOK_SIZES.LG} />
        <CoCaTok size={COCATOK_SIZES.XL} />
      </div>

      {/* Disabled State */}
      <CoCaTok 
        disabled 
        size={COCATOK_SIZES.LG}
      />
    </div>
  );
}

export default MagicOrbDemo;
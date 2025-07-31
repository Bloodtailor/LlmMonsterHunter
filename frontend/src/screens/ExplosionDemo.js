// Explosion Usage Examples - See the epic explosions in action!

import React, { useState } from 'react';
import { Explosion, EXPLOSION_TYPES, EXPLOSION_SIZES, EXPLOSION_COLORS } from './../shared/ui/Explosion';

function ExplosionDemo() {
  const [activeExplosion, setActiveExplosion] = useState(null);

  const triggerExplosion = (type) => {
    setActiveExplosion(type);
    // Reset after explosion completes
    setTimeout(() => setActiveExplosion(null), 2000);
  };

  return (
    <div className="explosion-showcase" style={{ position: 'relative', padding: '100px' }}>
      <h2>Epic Explosion System</h2>
      
      {/* Trigger Buttons */}
      <div className="explosion-triggers">
        <button onClick={() => triggerExplosion('treasure')}>
          💎 Treasure Explosion
        </button>
        
        <button onClick={() => triggerExplosion('fire')}>
          🔥 Fire Explosion
        </button>
        
        <button onClick={() => triggerExplosion('ice')}>
          ❄️ Ice Explosion
        </button>
        
        <button onClick={() => triggerExplosion('lightning')}>
          ⚡ Lightning Explosion
        </button>
        
        <button onClick={() => triggerExplosion('magic')}>
          ✨ Magic Explosion
        </button>
        
        <button onClick={() => triggerExplosion('sparkle')}>
          🌟 Sparkle Explosion
        </button>
      </div>

      {/* Active Explosions */}
      {activeExplosion === 'treasure' && (
        <Explosion 
          type={EXPLOSION_TYPES.BURST}
          size={EXPLOSION_SIZES.LG}
          color={EXPLOSION_COLORS.TREASURE}
          duration={1500}
          particleCount={20}
          onComplete={() => console.log('💎 Treasure collected!')}
        />
      )}

      {activeExplosion === 'fire' && (
        <Explosion 
          type={EXPLOSION_TYPES.FIRE}
          size={EXPLOSION_SIZES.XL}
          color={EXPLOSION_COLORS.FIRE}
          duration={2000}
          onComplete={() => console.log('🔥 Fire spell cast!')}
        />
      )}

      {activeExplosion === 'ice' && (
        <Explosion 
          type={EXPLOSION_TYPES.ICE}
          size={EXPLOSION_SIZES.LG}
          color={EXPLOSION_COLORS.ICE}
          duration={1800}
          onComplete={() => console.log('❄️ Ice spell cast!')}
        />
      )}

      {activeExplosion === 'lightning' && (
        <Explosion 
          type={EXPLOSION_TYPES.LIGHTNING}
          size={EXPLOSION_SIZES.XL}
          color={EXPLOSION_COLORS.LIGHTNING}
          duration={1200}
          particleCount={16}
          onComplete={() => console.log('⚡ Lightning strike!')}
        />
      )}

      {activeExplosion === 'magic' && (
        <Explosion 
          type={EXPLOSION_TYPES.MAGIC}
          size={EXPLOSION_SIZES.MASSIVE}
          color={EXPLOSION_COLORS.MAGIC}
          duration={2500}
          particleCount={32}
          onComplete={() => console.log('✨ Powerful magic unleashed!')}
        />
      )}

      {activeExplosion === 'sparkle' && (
        <Explosion 
          type={EXPLOSION_TYPES.SPARKLE}
          size={EXPLOSION_SIZES.LG}
          color={EXPLOSION_COLORS.MAGIC}
          duration={2000}
          onComplete={() => console.log('🌟 Magical sparkles!')}
        />
      )}

      {/* Usage Examples in Code */}
      <div className="code-examples">
        <h3>Usage Examples:</h3>
        <pre>{`
// Treasure card explosion
<Explosion 
  type="burst"
  size="lg" 
  color="treasure"
  onComplete={() => collectTreasure()}
/>

// Monster defeat explosion  
<Explosion 
  type="fire"
  size="xl"
  color="fire"
  duration={2000}
  particleCount={24}
/>

// Spell cast sparkles
<Explosion 
  type="sparkle"
  size="md"
  color="magic"
/>
        `}</pre>
      </div>
    </div>
  );
}

export default ExplosionDemo;
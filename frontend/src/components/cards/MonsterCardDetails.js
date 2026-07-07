// MonsterCardDetails.js - Details side of monster card
// Full information view: stats, description, backstory, personality traits
// Uses new CardSection system and useTypographyScale hook for consistent typography

import React from 'react';
import './monsterCard.css';
import {
  Card,
  CardSection,
  IconButton,
  StatusBadge,
  Badge,
  EmptyState,
} from '../../shared/ui/index.js';
import { CARD_SIZES } from '../../shared/constants/constants.js';
import { useTypographyScale } from '../../shared/hooks/useTypographyScale.js';
import useCooldown from '../../shared/hooks/useButtonCooldown.js';
import { useAbilityGeneration, useMonsterMemories } from '../../app/hooks/useMonsters.js';

// Memory kinds -> a small glyph for the timeline (kinds carry the tone)
const MEMORY_KIND_ICONS = {
  was_defeated: '💥',
  defeated_party: '👑',
  joined_party: '🤝',
  yielded_to_party: '🏳️',
  fled_from_party: '💨',
  spared_party: '🕊️',
  let_party_pass: '🚪',
  gave_reward: '🎁',
  punished_party: '⚖️',
  talked_with_party: '💬',
  avoided: '👀',
  camp: '🔥',
  growth: '🌱',
  lesson: '📿',
  returned: '🔁',
  run_complete: '🏆',
};

const MAX_MEMORIES_SHOWN = 10;

// Classic rarity palette for the rarity badge
const RARITY_COLORS = {
  common: '#6c757d',
  uncommon: '#2f9e44',
  rare: '#1c7ed6',
  epic: '#9c36b5',
  legendary: '#e8590c',
};

function MonsterCardDetails({ monster, size = 'md' }) {
  const classType = 'monster';

  const { generate: generateAbility, isGenerating: isGeneratingAbility } = useAbilityGeneration();
  const { isOnCooldown, startCooldown } = useCooldown();

  // Get typography scaling functions
  const { getTextSize } = useTypographyScale(size, classType);

  // Handle ability generation
  const handleAbilityGenerate = async (e) => {
    e.stopPropagation();
    startCooldown();
    generateAbility(monster.id);
  };

  // Determine badge size based on card size
  const getBadgeSize = () => {
    switch (size) {
      case CARD_SIZES.SM:
        return 'sm';
      case CARD_SIZES.MD:
        return 'md';
      case CARD_SIZES.LG:
        return 'md';
      case CARD_SIZES.XL:
        return 'lg';
      default:
        return 'sm';
    }
  };

  // Determine button size based on card size
  const getButtonSize = () => {
    switch (size) {
      case CARD_SIZES.SM:
        return 'sm';
      case CARD_SIZES.MD:
        return 'sm';
      case CARD_SIZES.LG:
        return 'md';
      case CARD_SIZES.XL:
        return 'md';
      default:
        return 'sm';
    }
  };

  // Helper to get ability count based on card size
  const getMaxAbilities = () => {
    switch (size) {
      case CARD_SIZES.SM:
        return 2;
      case CARD_SIZES.MD:
        return 3;
      case CARD_SIZES.LG:
        return 4;
      case CARD_SIZES.XL:
        return undefined; // Show all
      default:
        return 3;
    }
  };

  // Helper to get trait count based on card size
  const getMaxTraits = () => {
    switch (size) {
      case CARD_SIZES.SM:
        return 2;
      case CARD_SIZES.MD:
        return 3;
      case CARD_SIZES.LG:
        return 4;
      case CARD_SIZES.XL:
        return 5;
      default:
        return 3;
    }
  };

  const maxAbilities = getMaxAbilities();
  const maxTraits = getMaxTraits();

  const taxonomy = monster.taxonomy || {};
  const ecology = monster.ecology || {};
  const persona = monster.persona || {};
  const isXL = size === CARD_SIZES.XL;

  // Memories: only the full-size card fetches them (they live-append as
  // the monster records new moments with the party)
  const { memories } = useMonsterMemories(isXL ? monster.id : null);

  const joinList = (values) => (values || []).join(', ');

  // The full persona dossier (XL card only). The monster's SECRET is
  // deliberately absent - secrets are discovered through conversation.
  const personaRows = [
    ['Wish', persona.core_wish],
    ['Profession', persona.profession],
    ['Voice', persona.speech_style],
    ['Battle cry', persona.battle_line],
    ['Moral character', persona.moral_character],
    ['Beliefs', persona.beliefs],
    ['Motivations', persona.motivations],
    ['Goals', joinList(persona.goals)],
    ['Fears', joinList(persona.fears)],
    ['Likes', joinList(persona.likes)],
    ['Dislikes', joinList(persona.dislikes)],
    ['Hobbies', joinList(persona.hobbies)],
    ['Toward strangers', persona.attitude_toward_strangers],
    ['Responds well to', joinList(persona.responds_well_to)],
    ['Responds poorly to', joinList(persona.responds_poorly_to)],
    ['Would join a party for', persona.recruitment_lever],
    ['Drawn to', persona.social_bonds?.drawn_to],
    ['Clashes with', persona.social_bonds?.clashes_with],
    ['Grudges & bonds', joinList(persona.grudges_and_bonds)],
  ].filter(([, value]) => value);

  const lineage = ['domain', 'kingdom', 'family', 'genus', 'species']
    .map((rank) => taxonomy[rank])
    .filter(Boolean)
    .join(' › ');

  const habitat = ecology.habitat || {};
  const diet = ecology.diet || {};
  const classChain = (monster.classTaxonomy || [])
    .map((entry) =>
      [entry.domain, entry.discipline, entry.specialization].filter(Boolean).join(' › '),
    )
    .join('; ');

  const ecologyRows = [
    ['Size', ecology.size_class],
    [
      'Habitat',
      habitat.primary &&
        `${habitat.primary}${(habitat.biomes || []).length ? ` (${joinList(habitat.biomes)})` : ''}`,
    ],
    ['Diet', diet.feeding_style && `${diet.feeding_style}${diet.notes ? ` — ${diet.notes}` : ''}`],
    ['Sustained by', joinList(diet.sustenance)],
    ['Social life', ecology.social_structure?.primary],
    ['Mind', ecology.sapience],
    ['Communicates by', joinList(ecology.communication)],
    ['Elements', joinList(ecology.elemental_affinities)],
    ['Came to be', ecology.creation_mechanism],
    ['Lifecycle', ecology.lifecycle_stage],
    ['Active', ecology.activity_cycle],
    ['Class', classChain],
  ].filter(([, value]) => value);

  return (
    <Card variant="flat" padding="md" className="monster-card-details">
      {/* Header - CardSection automatically handles title typography */}
      <CardSection
        type="header"
        size={size}
        classType={classType}
        title={monster.name}
        alignment="center"
      >
        <Badge variant="info" size={getBadgeSize()}>
          {taxonomy.race_label || monster.species}
        </Badge>
        {monster.rarity && (
          <Badge
            size={getBadgeSize()}
            color={RARITY_COLORS[monster.rarity]}
            ariaLabel={`Rarity: ${monster.rarity}`}
          >
            {monster.rarity}
          </Badge>
        )}
        {monster.partyRole && (
          <Badge variant="secondary" size={getBadgeSize()}>
            {monster.partyRole}
          </Badge>
        )}
      </CardSection>

      {/* Description - CardSection handles content typography */}
      <CardSection type="content" size={size} classType={classType}>
        <p className={getTextSize('body')}>{monster.description}</p>
      </CardSection>

      {/* Backstory - Hide on small size */}
      {size !== CARD_SIZES.SM && monster.backstory && (
        <CardSection type="content" size={size} classType={classType} title="📖 Backstory">
          <p className={getTextSize('body')}>{monster.backstory}</p>
        </CardSection>
      )}

      {/* Stats */}
      <CardSection type="content" size={size} classType={classType} title="Stats">
        <div className="monster-card-stats-grid">
          <div className="stat-item">
            <span className={getTextSize('caption')}>Health:</span>
            <span className={`stat-value ${getTextSize('caption')}`}>
              {monster.stats?.currentHealth || 0}/{monster.stats?.maxHealth || 0}
            </span>
          </div>
          <div className="stat-item">
            <span className={getTextSize('caption')}>Attack:</span>
            <span className={`stat-value ${getTextSize('caption')}`}>
              {monster.stats?.attack || 0}
            </span>
          </div>
          <div className="stat-item">
            <span className={getTextSize('caption')}>Defense:</span>
            <span className={`stat-value ${getTextSize('caption')}`}>
              {monster.stats?.defense || 0}
            </span>
          </div>
          <div className="stat-item">
            <span className={getTextSize('caption')}>Speed:</span>
            <span className={`stat-value ${getTextSize('caption')}`}>
              {monster.stats?.speed || 0}
            </span>
          </div>
        </div>
      </CardSection>

      {/* Abilities */}
      <CardSection
        type="content"
        size={size}
        classType={classType}
        title="Abilities"
        action={
          <IconButton
            icon="⚡"
            variant="ghost"
            size={getButtonSize()}
            onClick={handleAbilityGenerate}
            disabled={isOnCooldown}
            loading={isGeneratingAbility}
            ariaLabel="Generate new ability"
          />
        }
      >
        {monster.abilities && monster.abilities.length > 0 ? (
          <div className="monster-card-abilities-list">
            {/* Show limited abilities based on card size */}
            {monster.abilities.slice(0, maxAbilities).map((ability, index) => (
              <div key={index} className="monster-card-ability-item">
                <div className={`monster-card-ability-name ${getTextSize('subtitle')}`}>
                  {ability.name}
                </div>
                <div className={`monster-card-ability-description ${getTextSize('caption')}`}>
                  {ability.description}
                </div>
              </div>
            ))}

            {/* Show "more abilities" indicator if there are more */}
            {maxAbilities && monster.abilities.length > maxAbilities && (
              <div className={`more-abilities-indicator ${getTextSize('caption')}`}>
                +{monster.abilities.length - maxAbilities} more abilities
              </div>
            )}
          </div>
        ) : (
          <EmptyState
            icon="⚡"
            title="No Abilities Yet"
            message="Generate some abilities!"
            size="sm"
          />
        )}
      </CardSection>

      {/* Personality Traits - Hide on small size */}
      {maxTraits > 0 && monster.personalityTraits && monster.personalityTraits.length > 0 && (
        <CardSection type="content" size={size} classType={classType} title="Personality">
          <div className="monster-card-traits-list">
            {monster.personalityTraits.slice(0, maxTraits).map((trait, index) => (
              <Badge key={index} variant="secondary" size={getBadgeSize()}>
                {trait}
              </Badge>
            ))}

            {/* Show "more traits" indicator if there are more */}
            {maxTraits && monster.personalityTraits.length > maxTraits && (
              <span className={`more-traits-indicator ${getTextSize('caption')}`}>
                +{monster.personalityTraits.length - maxTraits} more
              </span>
            )}
          </div>
        </CardSection>
      )}

      {/* Persona dossier - full-size card only */}
      {isXL && personaRows.length > 0 && (
        <CardSection type="content" size={size} classType={classType} title="🧠 Persona">
          <div className="monster-card-dossier">
            {personaRows.map(([label, value]) => (
              <div key={label} className="monster-card-dossier-row">
                <span className={`monster-card-dossier-label ${getTextSize('caption')}`}>
                  {label}
                </span>
                <span className={getTextSize('caption')}>{value}</span>
              </div>
            ))}
          </div>
        </CardSection>
      )}

      {/* Memories - full-size card only; what this monster remembers of
          the party, newest first (live-appends as new moments happen) */}
      {isXL && memories.length > 0 && (
        <CardSection type="content" size={size} classType={classType} title="🕯️ Memories">
          <div className="monster-card-dossier">
            {[...memories]
              .reverse()
              .slice(0, MAX_MEMORIES_SHOWN)
              .map((memory) => (
                <div key={memory.id} className="monster-card-dossier-row">
                  <span className={`monster-card-dossier-label ${getTextSize('caption')}`}>
                    {MEMORY_KIND_ICONS[memory.kind] || '🕯️'}{' '}
                    {memory.runNumber ? `run ${memory.runNumber}` : 'long ago'}
                  </span>
                  <span className={getTextSize('caption')}>{memory.content}</span>
                </div>
              ))}
            {memories.length > MAX_MEMORIES_SHOWN && (
              <div className={`more-abilities-indicator ${getTextSize('caption')}`}>
                +{memories.length - MAX_MEMORIES_SHOWN} older memories
              </div>
            )}
          </div>
        </CardSection>
      )}

      {/* Taxonomy & Ecology - full-size card only */}
      {isXL && (lineage || ecologyRows.length > 0) && (
        <CardSection type="content" size={size} classType={classType} title="🌿 Taxonomy & Ecology">
          {lineage && <p className={`monster-card-lineage ${getTextSize('caption')}`}>{lineage}</p>}
          <div className="monster-card-dossier">
            {ecologyRows.map(([label, value]) => (
              <div key={label} className="monster-card-dossier-row">
                <span className={`monster-card-dossier-label ${getTextSize('caption')}`}>
                  {label}
                </span>
                <span className={getTextSize('caption')}>{value}</span>
              </div>
            ))}
          </div>
        </CardSection>
      )}

      <CardSection type="footer" size={size} classType={classType}></CardSection>
    </Card>
  );
}

export default MonsterCardDetails;

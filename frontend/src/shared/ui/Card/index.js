// Card Components Export - Clean imports for all card-related components
// Allows for clean imports like: import { Card, CardSection } from 'shared/components/ui/Card'

export { 
  default as Card, 
  CARD_VARIANTS,
  CARD_PADDING,
  CARD_BACKGROUNDS 
} from './Card.js';

export { 
  default as CardSection, 
  CARD_SECTION_TYPES, 
  CARD_SECTION_ALIGNMENT 
} from './CardSection.js';

export { EmptyPartySlot } from './PlaceholderCard.js';
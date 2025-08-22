// NavigationContext exports - Clean imports for navigation functionality
// Allows for: import { NavigationProvider, useNavigation } from 'app/contexts/NavigationContext'
// Follows the established pattern from PartyContext

export { NavigationContext } from './NavigationContext.js';
export { default as NavigationProvider } from './NavigationProvider.js';
export { useNavigation } from './useNavigation.js';
// ToggleButton Component - Generic toggle for adding/removing items from collections
// Reusable for party, favorites, wishlist, inventory, etc.
// Handles all visual states: add, remove, full, loading, error

import React from 'react';
import { IconButton, LoadingSpinner } from '../index.js';
import './toggleButton.css';

/**
 * Generic toggle button for collection management
 * @param {object} props - ToggleButton props
 * @param {boolean} props.isInCollection - Whether item is currently in the collection
 * @param {boolean} props.isCollectionFull - Whether collection is at max capacity
 * @param {boolean} props.isLoading - Whether a toggle operation is in progress
 * @param {boolean} props.hasError - Whether there's an error state
 * @param {Function} props.onToggle - Function to call when toggled
 * @param {string} props.itemName - Name of the item (for accessibility)
 * @param {string} props.collectionName - Name of the collection (for accessibility)
 * @param {string} props.size - Button size (sm, md, lg)
 * @param {number} props.maxItems - Maximum items in collection (for tooltips)
 * @param {boolean} props.disabled - Additional disabled state
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.rest - Additional props passed to the rendered component
 * @returns {React.ReactElement} ToggleButton component
 */
function ToggleButton({
  isInCollection = false,
  isCollectionFull = false,
  isLoading = false,
  hasError = false,
  onToggle = null,
  itemName = 'item',
  collectionName = 'collection',
  size = 'md',
  maxItems = null,
  disabled = false,
  className = '',
  ...rest
}) {

  // Handle toggle click
  const handleToggle = (event) => {
    if (disabled || isLoading || hasError) {
      return;
    }
    
    if (onToggle) {
      onToggle(event);
    }
  };

  // Add shared classes
  const toggleClasses = [
    'toggle-button',
    className
  ].filter(Boolean).join(' ');

  // LOADING STATE - Show spinner, not clickable
  if (isLoading) {
    return (
      <IconButton
      icon={ <LoadingSpinner size={size} type="spin" color="secondary"/> }
      variant="primary"
      size={size}
      disabled={true}
      className={toggleClasses}
      {...rest}
      />
    );
  }

  // ERROR STATE - Show warning icon, not clickable
  if (hasError) {
    return (
      <IconButton
        icon="⚠️"
        variant="warning"
        size={size}
        disabled={true}
        ariaLabel={`Error updating ${collectionName}`}
        title={`Error updating ${collectionName}`}
        className={toggleClasses}
        {...rest}
      />
    );
  }

  // ITEM IN COLLECTION - Show remove icon, clickable
  if (isInCollection) {
    return (
      <IconButton
        icon="➖"
        variant="primary"
        size={size}
        onClick={handleToggle}
        disabled={disabled}
        ariaLabel={`Remove ${itemName} from ${collectionName}`}
        title={`Remove ${itemName} from ${collectionName}`}
        className={toggleClasses}
        {...rest}
      />
    );
  }

  // COLLECTION FULL - Show block icon, not clickable
  if (isCollectionFull) {
    const fullTooltip = maxItems 
      ? `${collectionName} is full (${maxItems}/${maxItems})`
      : `${collectionName} is full`;
      
    return (
      <IconButton
        icon="🚫"
        variant="primary"
        size={size}
        disabled={true}
        ariaLabel={`${collectionName} is full`}
        title={fullTooltip}
        className={toggleClasses}
        {...rest}
      />
    );
  }

  // DEFAULT STATE - Show add icon, clickable
  return (
    <IconButton
      icon="➕"
      variant="primary"
      size={size}
      onClick={handleToggle}
      disabled={disabled}
      ariaLabel={`Add ${itemName} to ${collectionName}`}
      title={`Add ${itemName} to ${collectionName}`}
      className={toggleClasses}
      {...rest}
    />
  );
}

export default ToggleButton;
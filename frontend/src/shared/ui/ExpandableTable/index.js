// ExpandableTable Components Export - Clean imports for expandable table functionality
// Allows for clean imports like: import { ExpandableTable, useExpandableRows } from 'shared/ui/ExpandableTable'
// Follows established pattern from other UI component exports

// ===== PRIMARY COMPONENTS =====
export { default as ExpandableTable } from './ExpandableTable.js';
export { useExpandableRows } from './useExpandableRows.js';

// ===== INTERNAL COMPONENTS (for advanced usage) =====
export { default as ExpandableTableRow } from './ExpandableTableRow.js';
export { default as ExpandableContent } from './ExpandableContent.js';

// Note: CSS is imported automatically by ExpandableTable.js
// Users only need to import { ExpandableTable, useExpandableRows }
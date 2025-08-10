// ExpandableTableRow Component - Individual expandable row with inline content
// Handles row expansion state, click events, and expanded content rendering
// Composes existing TableRow and TableCell components

import React from 'react';
import { TableRow, TableCell } from '../Table/index.js';
import ExpandableContent from './ExpandableContent.js';

/**
 * Individual expandable table row component
 * Renders main row + optional expanded content row
 * 
 * @param {object} props - ExpandableTableRow props
 * @param {object} props.row - Row data object (must have id property)
 * @param {number} props.rowIndex - Row index in the data array
 * @param {Array} props.columns - Column definitions
 * @param {object} props.expandableRows - Result from useExpandableRows hook
 * @param {Function} props.renderExpandedContent - Function to render expanded content
 * @param {string} props.iconColumnKey - Column key to show expand icon
 * @param {boolean} props.animateExpansion - Whether to animate expansion
 * @returns {React.ReactElement} ExpandableTableRow component
 */
function ExpandableTableRow({
  row,
  rowIndex,
  columns,
  expandableRows,
  renderExpandedContent,
  iconColumnKey,
  animateExpansion
}) {
  
  // Get expansion state for this row
  const isExpanded = expandableRows.isRowExpanded(row.id);
  
  // Handle row expansion toggle
  const handleToggleExpansion = (e) => {
    e.stopPropagation(); // Prevent event bubbling
    expandableRows.toggleRow(row.id);
  };
  
  // Handle keyboard navigation
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleToggleExpansion(e);
    }
  };

  return (
    <>
      {/* Main Row */}
      <TableRow 
        className={`expandable-row ${isExpanded ? 'expandable-row-expanded' : ''}`}
        onClick={handleToggleExpansion}
        onKeyDown={handleKeyDown}
        tabIndex={0}
        role="button"
        aria-expanded={isExpanded}
        aria-label={`${isExpanded ? 'Collapse' : 'Expand'} row details`}
      >
        {columns.map((col, colIndex) => {
          const value = row[col.key];
          const displayValue = col.render ? col.render(value, row) : value;
          
          // Add expand icon to the designated column
          const isIconColumn = col.key === iconColumnKey;
          
          return (
            <TableCell 
              key={col.key || colIndex}
              truncate={col.truncate !== false}
              className={`${col.cellClass || ''} ${isIconColumn ? 'expandable-icon-cell' : ''}`}
            >
              <div className="expandable-cell-content">
                {/* Expand/Collapse Icon */}
                {isIconColumn && (
                  <button
                    type="button"
                    className={`expand-icon ${isExpanded ? 'expand-icon-expanded' : ''}`}
                    onClick={handleToggleExpansion}
                    tabIndex={-1} // Row itself is focusable
                    aria-hidden="true" // Screen readers use row's aria-expanded
                  >
                    {isExpanded ? '▼' : '▶'}
                  </button>
                )}
                
                {/* Cell Content */}
                <span className="cell-value">
                  {displayValue}
                </span>
              </div>
            </TableCell>
          );
        })}
      </TableRow>

      {/* Expanded Content Row */}
      {isExpanded && (
        <TableRow className="expandable-content-row">
          <TableCell 
            colSpan={columns.length}
            className="expandable-content-cell"
            truncate={false}
          >
            <ExpandableContent 
              row={row}
              renderContent={renderExpandedContent}
              animateExpansion={animateExpansion}
            />
          </TableCell>
        </TableRow>
      )}
    </>
  );
}

export default ExpandableTableRow;
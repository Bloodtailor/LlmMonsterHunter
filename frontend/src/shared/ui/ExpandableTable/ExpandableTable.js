// ExpandableTable Component - Table with inline row expansion functionality
// Composes existing Table components and adds expansion capabilities
// Works seamlessly with existing pagination and maintains responsive behavior

import React from 'react';
import { 
  Table,
  TableHead, 
  TableBody, 
  TableRow, 
  TableHeaderCell, 
  TableCell 
} from '../Table/index.js';
import ExpandableTableRow from './ExpandableTableRow.js';
import './expandableTable.css';

/**
 * Expandable table component with inline row expansion
 * Extends existing Table functionality with expansion capabilities
 * 
 * @param {object} props - ExpandableTable props
 * @param {Array} props.columns - Column definitions (same as Table)
 * @param {Array} props.data - Row data (same as Table)
 * @param {object} props.expandableRows - Result from useExpandableRows hook
 * @param {Function} props.renderExpandedContent - Function to render expanded content: (row) => ReactElement
 * @param {string} props.expandIconColumn - Column key to show expand icon (default: first column)
 * @param {string} props.emptyMessage - Message when no data (default: 'No data available')
 * @param {string} props.size - Table size (sm, md, lg) (default: 'md')
 * @param {boolean} props.striped - Alternating row colors (default: false)
 * @param {boolean} props.bordered - Show borders (default: false)
 * @param {boolean} props.hover - Hover effects on rows (default: false)
 * @param {boolean} props.animateExpansion - Animate expand/collapse (default: true)
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.rest - Additional table attributes
 * @returns {React.ReactElement} ExpandableTable component
 */
function ExpandableTable({
  // Required props
  columns = [],
  data = [],
  expandableRows = null,
  renderExpandedContent = null,
  
  // Optional configuration
  expandIconColumn = null, // Auto-detect first column if null
  emptyMessage = 'No data available',
  
  // Table styling (same as existing Table)
  size = 'md',
  striped = false,
  bordered = false,
  hover = false,
  
  // Expansion behavior
  animateExpansion = true,
  
  // Standard props
  className = '',
  ...rest
}) {
  
  // Validation
  if (!expandableRows) {
    console.error('ExpandableTable requires expandableRows prop from useExpandableRows hook');
    return null;
  }
  
  if (!renderExpandedContent) {
    console.error('ExpandableTable requires renderExpandedContent function');
    return null;
  }
  
  // Determine which column should show the expand icon
  const iconColumnKey = expandIconColumn || (columns[0]?.key);
  
  // Build CSS classes (same pattern as existing Table)
  const tableClasses = [
    'expandable-table',
    `expandable-table-${size}`,
    striped && 'expandable-table-striped',
    bordered && 'expandable-table-bordered', 
    hover && 'expandable-table-hover',
    animateExpansion && 'expandable-table-animated',
    className
  ].filter(Boolean).join(' ');

  // Handle empty state
  if (data.length === 0) {
    return (
      <div className="table-container">
        <table className={tableClasses} {...rest}>
          <TableHead>
            <TableRow>
              {columns.map((col, index) => (
                <TableHeaderCell 
                  key={col.key || index}
                  style={col.width ? { width: col.width } : undefined}
                >
                  {col.header}
                </TableHeaderCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            <TableRow>
              <TableCell 
                colSpan={columns.length}
                className="table-empty"
                truncate={false}
              >
                {emptyMessage}
              </TableCell>
            </TableRow>
          </TableBody>
        </table>
      </div>
    );
  }

  return (
    <div className="table-container">
      <table className={tableClasses} {...rest}>
        {/* Table Header - Same as existing Table */}
        <TableHead>
          <TableRow>
            {columns.map((col, index) => (
              <TableHeaderCell 
                key={col.key || index}
                style={col.width ? { width: col.width } : undefined}
              >
                {col.header}
              </TableHeaderCell>
            ))}
          </TableRow>
        </TableHead>
        
        {/* Table Body with Expandable Rows */}
        <TableBody>
          {data.map((row, rowIndex) => (
            <ExpandableTableRow
              key={row.id || rowIndex}
              row={row}
              rowIndex={rowIndex}
              columns={columns}
              expandableRows={expandableRows}
              renderExpandedContent={renderExpandedContent}
              iconColumnKey={iconColumnKey}
              animateExpansion={animateExpansion}
            />
          ))}
        </TableBody>
      </table>
    </div>
  );
}

export default ExpandableTable;
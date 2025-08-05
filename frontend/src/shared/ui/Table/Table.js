// Table Component - Tight, responsive table that never scrolls horizontally
// Perfect for streaming display data that needs to fit in constrained spaces
// Automatically truncates content to prevent horizontal overflow

import React from 'react';
import './table.css';

/**
 * Responsive table component with automatic text truncation
 * Supports both simple data-driven API and manual markup
 * 
 * SIMPLE API (recommended):
 * <Table 
 *   columns={[
 *     { key: 'id', header: 'ID', width: '15%' },
 *     { key: 'status', header: 'Status', render: (val) => <Badge>{val}</Badge> }
 *   ]}
 *   data={[{ id: 1002, status: 'completed' }]}
 * />
 * 
 * MANUAL API (for complex cases):
 * <Table><TableHead>...</TableHead></Table>
 * 
 * @param {object} props - Table props
 * @param {Array} props.columns - Column definitions (for simple API)
 * @param {Array} props.data - Row data (for simple API)
 * @param {React.ReactNode} props.children - Manual table content
 * @param {string} props.size - Table size (sm, md, lg)
 * @param {boolean} props.striped - Alternating row colors
 * @param {boolean} props.bordered - Show borders
 * @param {boolean} props.hover - Hover effects on rows
 * @param {string} props.emptyMessage - Message when no data
 * @param {string} props.className - Additional CSS classes
 * @param {object} props.rest - Additional table attributes
 * @returns {React.ReactElement} Table component
 */
function Table({
  // Simple API props
  columns = null,
  data = null,
  emptyMessage = 'No data available',
  
  // Manual API props
  children = null,
  
  // Styling props
  size = 'md',
  striped = false,
  bordered = false,
  hover = false,
  className = '',
  ...rest
}) {
  
  // Build CSS classes
  const tableClasses = [
    'table',
    `table-${size}`,
    striped && 'table-striped',
    bordered && 'table-bordered',
    hover && 'table-hover',
    className
  ].filter(Boolean).join(' ');

  // Simple API: Generate table from columns/data
  if (columns && data !== null) {
    return (
      <div className="table-container">
        <table className={tableClasses} {...rest}>
          {/* Generate header */}
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
          
          {/* Generate body */}
          <TableBody>
            {data.length === 0 ? (
              <TableRow>
                <TableCell 
                  colSpan={columns.length}
                  className="table-empty"
                  truncate={false}
                >
                  {emptyMessage}
                </TableCell>
              </TableRow>
            ) : (
              data.map((row, rowIndex) => (
                <TableRow key={row.id || rowIndex}>
                  {columns.map((col, colIndex) => {
                    const value = row[col.key];
                    const displayValue = col.render ? col.render(value, row) : value;
                    
                    return (
                      <TableCell 
                        key={col.key || colIndex}
                        truncate={col.truncate !== false}
                        className={col.cellClass || ''}
                      >
                        {displayValue}
                      </TableCell>
                    );
                  })}
                </TableRow>
              ))
            )}
          </TableBody>
        </table>
      </div>
    );
  }

  // Manual API: Use provided children
  return (
    <div className="table-container">
      <table className={tableClasses} {...rest}>
        {children}
      </table>
    </div>
  );
}

/**
 * Table header component with consistent styling
 */
export function TableHead({ children, className = '', ...rest }) {
  return (
    <thead className={`table-head ${className}`} {...rest}>
      {children}
    </thead>
  );
}

/**
 * Table body component with consistent styling
 */
export function TableBody({ children, className = '', ...rest }) {
  return (
    <tbody className={`table-body ${className}`} {...rest}>
      {children}
    </tbody>
  );
}

/**
 * Table row component with consistent styling
 */
export function TableRow({ children, className = '', ...rest }) {
  return (
    <tr className={`table-row ${className}`} {...rest}>
      {children}
    </tr>
  );
}

/**
 * Table header cell with truncation and responsive behavior
 */
export function TableHeaderCell({ children, className = '', ...rest }) {
  return (
    <th className={`table-header-cell ${className}`} {...rest}>
      <span className="cell-content">{children}</span>
    </th>
  );
}

/**
 * Table data cell with truncation and responsive behavior
 */
export function TableCell({ children, className = '', truncate = true, ...rest }) {
  const cellClasses = [
    'table-cell',
    truncate && 'table-cell-truncate',
    className
  ].filter(Boolean).join(' ');

  return (
    <td className={cellClasses} {...rest}>
      <span className="cell-content" title={typeof children === 'string' ? children : undefined}>
        {children}
      </span>
    </td>
  );
}

// Size constants for easy imports
export const TABLE_SIZES = {
  SM: 'sm',
  MD: 'md',
  LG: 'lg'
};

export default Table;
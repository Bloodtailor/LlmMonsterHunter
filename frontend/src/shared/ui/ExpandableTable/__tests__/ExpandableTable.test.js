// ExpandableTable tests - the loading prop must be consumed, never spread
// onto the DOM <table>. Regression coverage for the React warning
// "Received `false` for a non-boolean attribute `loading`" that fired on the
// Developer screen (AiLogTableView passes loading={isLoading}), plus coverage
// for the three body states (loading row / empty row / data rows).
//
// WHY bare react-dom instead of @testing-library/react: the project has no
// testing-library dependency, and node_modules must not be touched from a
// worktree checkout, so these tests use only what react-scripts already ships.

import React from 'react';
import { createRoot } from 'react-dom/client';
import { act } from 'react-dom/test-utils';
import ExpandableTable from '../ExpandableTable.js';

// createRoot outside of testing-library requires opting in to act()
global.IS_REACT_ACT_ENVIRONMENT = true;

const COLUMNS = [
  { key: 'id', header: 'ID' },
  { key: 'name', header: 'Name' },
];

const DATA = [
  { id: 1, name: 'Emberwing' },
  { id: 2, name: 'Mosslurker' },
];

// Minimal stand-in for the useExpandableRows hook result - ExpandableTable
// and ExpandableTableRow only call these two members
function makeExpandableRows(expandedIds = []) {
  return {
    isRowExpanded: (id) => expandedIds.includes(id),
    toggleRow: jest.fn(),
  };
}

function renderExpandedContent(row) {
  return <div className="test-expanded-content">Details for {row.name}</div>;
}

describe('ExpandableTable', () => {
  let container;
  let root;

  function render(element) {
    // The no-unnecessary-act rule assumes Testing Library's auto-acting
    // render; with bare createRoot, React requires the act() wrapper.
    // eslint-disable-next-line testing-library/no-unnecessary-act
    act(() => {
      root.render(element);
    });
  }

  beforeEach(() => {
    container = document.createElement('div');
    document.body.appendChild(container);
    root = createRoot(container);
  });

  afterEach(() => {
    act(() => {
      root.unmount();
    });
    container.remove();
  });

  test('consumes loading instead of spreading it onto the <table> (no React warning)', () => {
    const errorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    render(
      <ExpandableTable
        columns={COLUMNS}
        data={DATA}
        expandableRows={makeExpandableRows()}
        renderExpandedContent={renderExpandedContent}
        loading={false}
      />,
    );

    // Direct DOM proof: the attribute never reaches the element
    const table = container.querySelector('table');
    expect(table).not.toBeNull();
    expect(table.hasAttribute('loading')).toBe(false);

    // And React never had to complain about it
    const warnings = errorSpy.mock.calls.map((args) => String(args[0]));
    expect(warnings.filter((message) => message.includes('non-boolean attribute'))).toEqual([]);

    errorSpy.mockRestore();
  });

  test('still forwards legitimate extra attributes through ...rest', () => {
    render(
      <ExpandableTable
        columns={COLUMNS}
        data={DATA}
        expandableRows={makeExpandableRows()}
        renderExpandedContent={renderExpandedContent}
        data-testid="log-table"
      />,
    );

    expect(container.querySelector('table').getAttribute('data-testid')).toBe('log-table');
  });

  test('loading replaces body rows with the spinner status row', () => {
    render(
      <ExpandableTable
        columns={COLUMNS}
        data={DATA}
        expandableRows={makeExpandableRows()}
        renderExpandedContent={renderExpandedContent}
        loading
      />,
    );

    const loadingCell = container.querySelector('.expandable-table-loading-cell');
    expect(loadingCell).not.toBeNull();
    expect(loadingCell.querySelector('.loading-spinner')).not.toBeNull();
    expect(loadingCell.textContent).toContain('Loading');

    // The status row spans the full table and stands in for the data rows,
    // while the header keeps its shape
    expect(loadingCell.getAttribute('colspan')).toBe(String(COLUMNS.length));
    expect(container.querySelectorAll('.expandable-row')).toHaveLength(0);
    expect(container.querySelectorAll('th')).toHaveLength(COLUMNS.length);
  });

  test('shows the empty message when not loading and there is no data', () => {
    render(
      <ExpandableTable
        columns={COLUMNS}
        data={[]}
        expandableRows={makeExpandableRows()}
        renderExpandedContent={renderExpandedContent}
        emptyMessage="No logs found"
      />,
    );

    expect(container.querySelector('.table-empty').textContent).toBe('No logs found');
    expect(container.querySelector('.expandable-table-loading-cell')).toBeNull();
  });

  test('renders data rows and expanded content for expanded rows', () => {
    render(
      <ExpandableTable
        columns={COLUMNS}
        data={DATA}
        expandableRows={makeExpandableRows([2])}
        renderExpandedContent={renderExpandedContent}
        animateExpansion={false}
      />,
    );

    expect(container.querySelectorAll('.expandable-row')).toHaveLength(DATA.length);
    expect(container.querySelector('.test-expanded-content').textContent).toBe(
      'Details for Mosslurker',
    );
  });
});

// Workflow transformer tests - the shape every workflow event shares.

import { transformWorkflowItem, transformWorkflowItems } from '../workflows.js';

const RAW_ITEM = {
  workflow_id: 42,
  workflow_type: 'choose_path',
  context: { path_id: 'p1' },
  priority: 5,
  created_at: '2026-07-06T10:00:00',
  status: 'processing',
  result: null,
  error: null,
  started_at: '2026-07-06T10:00:01',
  completed_at: null,
};

describe('transformWorkflowItem', () => {
  it('maps every backend field to camelCase', () => {
    const item = transformWorkflowItem(RAW_ITEM);
    expect(item).toEqual({
      workflowId: 42,
      workflowType: 'choose_path',
      context: { path_id: 'p1' },
      priority: 5,
      createdAt: '2026-07-06T10:00:00',
      status: 'processing',
      result: null,
      error: null,
      startedAt: '2026-07-06T10:00:01',
      completedAt: null,
    });
  });

  it('passes null through untouched', () => {
    expect(transformWorkflowItem(null)).toBeNull();
    expect(transformWorkflowItem(undefined)).toBeNull();
  });
});

describe('transformWorkflowItems', () => {
  it('transforms whole queues', () => {
    const items = transformWorkflowItems([RAW_ITEM, RAW_ITEM]);
    expect(items).toHaveLength(2);
    expect(items[1].workflowType).toBe('choose_path');
  });

  it('answers non-arrays with null', () => {
    expect(transformWorkflowItems(null)).toBeNull();
    expect(transformWorkflowItems({})).toBeNull();
  });
});

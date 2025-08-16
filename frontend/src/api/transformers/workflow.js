// Workflow Transformer - Reusable for all workflow events
// Transforms snake_case backend workflow data to camelCase frontend format
// Used by events that include workflow item data

/**
 * Transform workflow item from backend format to frontend format
 * Backend item structure from WorkflowItem.to_dict():
 * {
 *   workflow_id, workflow_type, context, priority, created_at, status,
 *   result, error, started_at, completed_at
 * }
 * 
 * @param {Object|null} workflowItem - Workflow item from backend event
 * @returns {Object|null} Transformed workflow item in camelCase
 */
export function transformWorkflowItem(workflowItem) {
  // Handle null/undefined items
  if (!workflowItem) {
    return null;
  }

  return {
    workflowId: workflowItem.workflow_id || null,
    workflowType: workflowItem.workflow_type || null,
    context: workflowItem.context || null,
    priority: workflowItem.priority || null,
    createdAt: workflowItem.created_at || null,
    status: workflowItem.status || null,
    result: workflowItem.result || null,
    error: workflowItem.error || null,
    startedAt: workflowItem.started_at || null,
    completedAt: workflowItem.completed_at || null
  };
}

/**
 * Transform array of workflow items
 * Used by workflow.queue.update event which sends all_items array
 * 
 * @param {Array|null} workflowItems - Array of workflow items from backend
 * @returns {Array|null} Array of transformed workflow items
 */
export function transformWorkflowItems(workflowItems) {
  // Handle null/undefined arrays
  if (!Array.isArray(workflowItems)) {
    return null;
  }

  return workflowItems.map(item => transformWorkflowItem(item));
}
// Workflow Event Handlers - External (non-React) event handling
// Transforms SSE events and broadcasts to state stores and event subscribers
// No React state - just pure event transformation and routing
// Mirror of aiEventHandlers.js for the workflow domain

import { transformWorkflowItem, transformWorkflowItems } from '../transformers/workflows.js';
import { broadcastEvent } from '../core/eventBroadcast.js';

/**
 * Workflow Event Handlers - External event processing system
 * Each handler transforms event data and broadcasts to state stores
 */
export const workflowEventHandlers = {
  'workflow.started': (eventData) => {
    const transformedData = {
      workflowItem: transformWorkflowItem(eventData.item),
      workflowId: eventData.workflow_id || null,
      timestamp: eventData.timestamp || null,
    };
    broadcastEvent('workflowStarted', transformedData);
  },

  'workflow.completed': (eventData) => {
    const transformedData = {
      workflowItem: transformWorkflowItem(eventData.item),
      workflowId: eventData.workflow_id || null,
      result: eventData.result || null,
      timestamp: eventData.timestamp || null,
    };
    broadcastEvent('workflowCompleted', transformedData);
  },

  'workflow.failed': (eventData) => {
    const transformedData = {
      workflowItem: transformWorkflowItem(eventData.item),
      workflowId: eventData.workflow_id || null,
      error: eventData.error || null,
      timestamp: eventData.timestamp || null,
    };
    broadcastEvent('workflowFailed', transformedData);
  },

  'workflow.update': (eventData) => {
    const transformedData = {
      workflowId: eventData.workflow_id || null,
      workflowType: eventData.workflow_type || null,
      step: eventData.step || null,
      data: eventData.data || null,
      timestamp: eventData.timestamp || null,
    };
    broadcastEvent('workflowUpdate', transformedData);
  },

  'workflow.queue.update': (eventData) => {
    const transformedData = {
      trigger: eventData.trigger || null,
      allWorkflowItems: transformWorkflowItems(eventData.all_items),
      timestamp: eventData.timestamp || null,
    };
    broadcastEvent('workflowQueueUpdate', transformedData);
  },
};

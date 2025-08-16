import { useState } from 'react';
import { 
  transformWorkflowItem, 
  transformWorkflowItems
} from "../transformers/workflows.js"

export const useWorkflowEvents = () => {
  // Create one useState(null) per event
  const [workflowStartedEvent, setWorkflowStartedEvent] = useState(null);
  const [workflowCompletedEvent, setWorkflowCompletedEvent] = useState(null);
  const [workflowFailedEvent, setWorkflowFailedEvent] = useState(null);
  const [workflowUpdateEvent, setWorkflowUpdateEvent] = useState(null);
  const [workflowQueueUpdateEvent, setWorkflowQueueUpdateEvent] = useState(null);

  // Define eventHandlers object
  const eventHandlers = {
    'workflow.started': (eventData) => {
      // Transform eventData directly
      const transformedData = {
        workflowItem: transformWorkflowItem(eventData.item),
        workflowId: eventData.workflow_id || null,
        timestamp: eventData.timestamp || null
      };
      setWorkflowStartedEvent(transformedData);
    },
    'workflow.completed': (eventData) => {
      // Transform eventData directly
      const transformedData = {
        workflowItem: transformWorkflowItem(eventData.item),
        workflowId: eventData.workflow_id || null,
        result: eventData.result || null,
        timestamp: eventData.timestamp || null
      };
      setWorkflowCompletedEvent(transformedData);
    },
    'workflow.failed': (eventData) => {
      // Transform eventData directly
      const transformedData = {
        workflowItem: transformWorkflowItem(eventData.item),
        workflowId: eventData.workflow_id || null,
        error: eventData.error || null,
        timestamp: eventData.timestamp || null
      };
      setWorkflowFailedEvent(transformedData);
    },
    'workflow.update': (eventData) => {
      // Transform eventData directly
      const transformedData = {
        workflowId: eventData.workflow_id || null,
        workflowType: eventData.workflow_type || null,
        step: eventData.step || null,
        data: eventData.data || null,
        timestamp: eventData.timestamp || null
      };
      setWorkflowUpdateEvent(transformedData);
    },
    'workflow.queue.update': (eventData) => {
      // Transform eventData directly
      const transformedData = {
        trigger: eventData.trigger || null,
        allWorkflowItems: transformWorkflowItems(eventData.all_items),
        timestamp: eventData.timestamp || null
      };
      setWorkflowQueueUpdateEvent(transformedData);
    }
  };

  return {
    state: {
      workflowStartedEvent,
      workflowCompletedEvent,
      workflowFailedEvent,
      workflowUpdateEvent,
      workflowQueueUpdateEvent
    },
    eventHandlers
  };
};
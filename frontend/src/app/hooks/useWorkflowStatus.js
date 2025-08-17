// useWorkflowStatus Hook - Simple workflow status tracking
// Lightweight version focusing on essential workflow state

import { useState, useEffect, useMemo } from 'react';
import { useEventContext } from '../contexts/EventContext';

export function useWorkflowStatus() {
  
  // Get workflow events
  const {
    workflowStartedEvent,
    workflowCompletedEvent,
    workflowFailedEvent,
    workflowUpdateEvent,
    workflowQueueUpdateEvent
  } = useEventContext();
  
  // Simple state tracking
  const [activeWorkflow, setActiveWorkflow] = useState(null);
  const [workflowStatus, setWorkflowStatus] = useState('idle');
  const [currentStep, setCurrentStep] = useState(null);
  const [isWorkflowActive, setIsWorkflowActive] = useState(false);

  // Handle workflow events
  useEffect(() => {
    if (workflowStartedEvent) {
      setActiveWorkflow(workflowStartedEvent.workflowItem);
      setWorkflowStatus('running');
      setCurrentStep(null);
      setIsWorkflowActive(true);
    }
  }, [workflowStartedEvent]);

  useEffect(() => {
    if (workflowUpdateEvent) {
      setCurrentStep(workflowUpdateEvent.step);
      setWorkflowStatus('processing...');
    }
  }, [workflowUpdateEvent]);

  useEffect(() => {
    if (workflowCompletedEvent) {
      setWorkflowStatus('completed');
      setIsWorkflowActive(false);
    }
  }, [workflowCompletedEvent]);

  useEffect(() => {
    if (workflowFailedEvent) {
      setWorkflowStatus('failed');
      setIsWorkflowActive(false);
    }
  }, [workflowFailedEvent]);

  const workflowQueueStatus = useMemo(() => {
    if (!workflowQueueUpdateEvent || !workflowQueueUpdateEvent.allWorkflowItems) {
      return {
        total: 0,
        pending: 0,
        processing: 0,
        completed: 0,
        failed: 0,
        items: []
      };
    }

    const items = workflowQueueUpdateEvent.allWorkflowItems;
    const statusCounts = items.reduce((acc, item) => {
      const status = item.status || 'pending';
      acc[status] = (acc[status] || 0) + 1;
      return acc;
    }, {});

    return {
      total: items.length,
      pending: statusCounts.pending || 0,
      processing: statusCounts.processing || 0,
      completed: statusCounts.completed || 0,
      failed: statusCounts.failed || 0,
      items,
      trigger: workflowQueueUpdateEvent.trigger
    };
  }, [workflowQueueUpdateEvent]);

  return {
    // Core state
    activeWorkflow,
    workflowStatus,
    currentStep,
    isWorkflowActive,
    workflowQueueStatus
  };
}
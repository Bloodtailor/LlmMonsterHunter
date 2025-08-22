// StreamingDisplay Component - Uses new useAiStatus hook with original layout
// Real-time AI generation monitoring with original fixed-position styling  
// Header + single scrollable Card with multiple CardSections

import React, { useState } from 'react';
import { Badge, Button, Card, CardSection, Alert, Scroll, Table } from '../../shared/ui/index.js';
import { useEventContext } from '../../app/contexts/EventContext/useEventContext.js';
import { useAiStatus } from '../../app/hooks/useAiStatus.js';
import { useWorkflowStatus } from '../../app/hooks/useWorkflowStatus.js';
import { formatTime, formatDuration } from '../../shared/utils/time.js';
import './streaming.css';

function StreamingDisplay() {
  
  // Get simple connection state from streaming context
  const { isConnected, connect, disconnect, lastActivity } = useEventContext();
  
  // Get all computed AI status from the hook
  const { currentActivity, queueStatus, llmStatus, imageStatus } = useAiStatus();
  const { workflowQueueStatus, workflowStatus, currentStep, currentData, activeWorkflow } = useWorkflowStatus();

  // UI state for main card minimization
  const [isMinimized, setIsMinimized] = useState(false);

  return (
    <div className={`streaming-display ${isMinimized ? 'streaming-display-minimized' : ''}`}>
      
      {/* Header - Always visible with activity status (NOT A CARD) */}
      <div 
        className="streaming-header"
        onClick={() => setIsMinimized(!isMinimized)}
      >
        <div className="streaming-status">
          
          {/* Activity Badge */}
          {currentActivity?.type ? (
            <Badge variant="primary">
              {`${currentActivity.label || 'Unknown'}: ${currentActivity.progress || ''}`}
            </Badge>
          ) : currentActivity?.label === 'Idle' ? (
            <Badge variant="primary">🟢 Idle</Badge>
          ) : isConnected ? (
            <Badge variant="success">🟢 Connected</Badge>
          ) : (
            <Badge variant="error">🔴 Disconnected</Badge>
          )}
          
          {/* Last Activity */}
          {lastActivity && !isMinimized && (
            <span className="last-activity">
              Last: {formatTime(lastActivity)}
            </span>
          )}
        </div>

        <Button size="sm" variant="ghost">
          {isMinimized ? '◀️' : '🔽'}
        </Button>

      </div>

      {/* Main content - ONE CARD with scrollable content and multiple sections */}
      {!isMinimized && (
        <Card style={{maxHeight: '800px'}}> 
          {/* Connection Controls Section */}
          <div className="connection-controls">
            <Badge variant={isConnected ? 'success' : 'error'} />
            <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
            <Button onClick={connect} disabled={isConnected} size="sm">
              Connect
            </Button>
            <Button onClick={disconnect} disabled={!isConnected} size="sm">
              Disconnect
            </Button>
          </div>

          {/* Queue Status Section */}
          <CardSection title={`Queue Status (${queueStatus?.total || 0} items)`}>

            {/* Queue Table */}
            {queueStatus?.items?.length > 0 ? (
              <Table
                columns={[
                  { key: 'generationId', header: 'ID', width: '10%' },
                  { key: 'generationType', header: 'Type', width: '11%' },
                  { key: 'promptType', header: 'Prompt Type', width: '30%' },
                  { key: 'promptName', header: 'Prompt', width: '30%' },
                  { key: 'status', header: 'Status', width: '19%' }
                ]}
                data={queueStatus.items.map(item => ({
                  ...item,
                  generationId: item?.generationId ? String(item.generationId).slice(-8) : 'N/A',
                  generationType: item?.generationType || 'N/A',
                  promptType: item?.promptType || 'N/A',
                  promptName: item?.promptName || 'N/A',
                  status: item?.status || 'pending'
                }))}
                maxHeight="200px"
                emptyMessage="No items in queue"
              />
            ) : (
              <div className="empty-table">No items in queue</div>
            )}
          </CardSection>

          {/* LLM Generation Section */}
          <CardSection title="LLM Generation">

            {/* LLM Table */}
            {llmStatus?.status ? (
              <Table
                columns={[
                  { key: 'status', header: 'status', width: '18%' },
                  { key: 'tokens', header: 'tokens', width: '12%' },
                  { key: 'type', header: 'type', width: '30%' },
                  { key: 'name', header: 'name', width: '40%' },
                ]}
                data={[{
                  status: llmStatus.status,
                  tokens: llmStatus.tokensSoFar,
                  type: llmStatus.promptType,
                  name: llmStatus.promptName,
                }]}
                maxHeight="200px"
                emptyMessage="No items available"
              />
            ) : (
              <div className="empty-table">No items available</div>
            )}

            {/* Generation Progress */}
            {llmStatus.partialText && (
              <CardSection type='content'>                 
                <Scroll maxHeight="200px">
                  <div className="text-preview">
                    {llmStatus.partialText}
                    <span className="cursor"></span>
                  </div>
                </Scroll>
              </CardSection>
            )}

            {/* Error */}
            { llmStatus?.error && (
              <Alert type='error' title='LLM Generation Failed' >
                {String(llmStatus.error)}
              </Alert>
            )}
          </CardSection>

          {/* Image Generation Section */}
          <CardSection title="Image Generation">

            {/* Image Table */}
            {imageStatus?.status ? (
              <Table
                columns={[
                  { key: 'status', header: 'status', width: '18%' },
                  { key: 'seconds', header: 'seconds', width: '12%' },
                  { key: 'name', header: 'name', width: '40%' },
                ]}
                data={[{
                  status: imageStatus.status,
                  seconds: imageStatus.elapsedSeconds,
                  name: imageStatus.promptName,
                }]}
                maxHeight="200px"
                emptyMessage="No items available"
              />
            ) : (
              <div className="empty-table">No items available</div>
            )}

            {/* Display image if URL available */}
            { imageStatus?.imageUrl && (
              <CardSection type='content'>
                <img 
                  src={imageStatus.imageUrl} 
                  alt="Generated image"
                  style={{ maxWidth: '100px', height: 'auto' }}
                />
              </CardSection>
            )}

            {/* Error */}
            {imageStatus?.status === 'failed' && imageStatus?.error && (
              <Alert type='error' title='Image Generation Failed' >
                {String(imageStatus.error)}
              </Alert>
            )}
          </CardSection>

          {/* Workflow Status Section */}
          <CardSection title="Workflow Status">

            {/* Current Workflow Table */}
            <Table
              columns={[
                { key: 'status', header: 'Status', width: '20%' },
                { key: 'currentStep', header: 'Current Step', width: '30%' },
                { key: 'workflowType', header: 'Workflow Name', width: '30%' },
                { key: 'workflowId', header: 'ID', width: '10%' }
              ]}
              data={[{
                status: workflowStatus,
                currentStep: currentStep,
                workflowType: activeWorkflow?.workflowType,
                workflowId: activeWorkflow?.workflowId 
              }]}
              maxHeight="100px"
              emptyMessage="No workflow status available"
            />
          </CardSection>

          <CardSection title={`Workflow Queue (${workflowQueueStatus?.total || 0} items)`}>
            {/* Workflow Queue Table */}
            {workflowQueueStatus?.items?.length > 0 ? (
              <Table
                columns={[
                  { key: 'workflowId', header: 'ID', width: '10%' },
                  { key: 'workflowType', header: 'Workflow Name', width: '30%' },
                  { key: 'status', header: 'Status', width: '15%' },
                  { key: 'priority', header: 'Priority', width: '15%' },
                  { key: 'createdAt', header: 'Created', width: '20%' }
                ]}
                data={workflowQueueStatus.items.map(item => ({
                  ...item,
                  workflowId: item?.workflowId ? String(item.workflowId).slice(-8) : 'N/A',
                  workflowType: item?.workflowType || 'N/A',
                  status: item?.status || 'pending',
                  priority: item?.priority || 'N/A',
                  createdAt: item?.createdAt ? new Date(item.createdAt).toLocaleTimeString() : 'N/A'
                }))}
                maxHeight="200px"
                emptyMessage="No workflow items in queue"
              />
            ) : (
              <div style={{ marginTop: '16px' }}>
                <div className="empty-table">No workflow items in queue</div>
              </div>
            )}

            {/* Generation Progress */}
            <CardSection type='content'>                 
              <Scroll maxHeight="200px">
                <div className="text-preview">
                  {JSON.stringify(currentData, null, 2)}
                  <span className="cursor"></span>
                </div>
              </Scroll>
            </CardSection>

          </CardSection>
          <CardSection type='footer'></CardSection>
        </Card>
      )}
    </div>
  );
}

export default StreamingDisplay;
//
//
//

import React, { useCallback, useEffect, useState } from 'react';
import { useGenerationLogs } from '../../app/hooks/useGeneration';
import { Button, Card, CardSection, Table} from '../../shared/ui';

function ApiServicesTestScreen() {

  const GenHook = useGenerationLogs();

  const logs = JSON.stringify(GenHook.logs)
  const rawResponse = JSON.stringify(GenHook.rawResponse)
  const count = GenHook.count

  // Load monsters when filters or pagination changes
  const loadLogs = useCallback(() => {
    GenHook.loadLogs({
      limit: 10
    });
  }, [GenHook.loadLogs]);

  useEffect(()=>{
    loadLogs();
  },[loadLogs])
  

  return(
    <Card>
      <CardSection type='header' title='useGenerationLogs test'>
      </CardSection>
      <CardSection title='cleaned data' type='content'>
        count: {count}
        <Table
          columns={[
            { key: 'generationType', header: 'Type', width: '10%' },
            { key: 'promptType', header: 'Prompt Type', width: '30%' },
            { key: 'promptName', header: 'Prompt Name', width: '30%' },
            { key: 'status', header: 'Status', width: '20%' },
            { key: 'durationSeconds', header: 'Duration', width: '10%' },
            { key: 'generationAttempt', header: 'Attempt', width: '10%' },
            { key: 'startTime', header: 'Date', width: '10%' },
          ]}
          data={(GenHook.logs || []).map(log => ({
            generationType: log.generationType || 'N/A',
            promptType: log.promptType || 'N/A',
            promptName: log.promptName || 'N/A',
            status: log.status || 'N/A',
            durationSeconds: log.durationSeconds ? `${log.durationSeconds}s` : 'N/A',
            generationAttempt: log.generationAttempt ? `${log.generationAttempt}/${log.maxAttempts}` : 'N/A',
            startTime: log.startTime ? log.startTime.toLocaleDateString() : 'N/A',
          }))}
          maxHeight="200px"
          emptyMessage="No items in queue"
        />
      </CardSection>
      <CardSection title='Raw object and response' type='content'>
        <div>isLoading: {GenHook.isLoading}</div>
        <div>logs: {logs}</div>
        <div>rawResponse: {rawResponse}</div>
      </CardSection>
    </Card>
  )

}

export default ApiServicesTestScreen;
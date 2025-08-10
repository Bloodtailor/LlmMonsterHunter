//
//
//

import React, { useCallback, useEffect, useState } from 'react';
import { useGenerationLogs, useGenerationLogOptions } from '../../app/hooks/useGeneration';
import { Button, Card, CardSection, Table, FilterSelectGroup} from '../../shared/ui';

function ApiServicesTestScreen() {

  const GenHook = useGenerationLogs();
  const LogOptionsHook = useGenerationLogOptions();

  const logs = JSON.stringify(GenHook.logs);
  const rawResponse = JSON.stringify(LogOptionsHook.rawResponse);
  const count = GenHook.count;
  const filterOptions = LogOptionsHook.filterOptions;
  const sortOptions = LogOptionsHook.sortOptions;

  const [ filterValues, setFilterValues ] = useState({});
  const [ sortValues, setSortValues ] = useState({});
  const [ updatedFilterOptions, setUpdatedFilterOptions ] = useState({});

  const handleFilterChange = (fieldName, newValue, updatedValues) => {
    
    // Update state with new values
    setFilterValues(updatedValues);
  };

  const handleSortChange = (fieldName, newValue, updatedValues) => {
    setSortValues(updatedValues);
  };

  // Load monsters when filters or pagination changes
  const loadLogs = useCallback(() => {
    GenHook.loadLogs({
      limit: 10
    });
  }, [GenHook.loadLogs]);

  useEffect(()=>{
    loadLogs();
  },[loadLogs])

  useEffect(() => {
  // Add "all" option to filter options and set default values
  if (filterOptions) {
    const updatedFilterOptions = {};

    Object.keys(filterOptions).forEach((key) => {
      updatedFilterOptions[key] = ['all', ...filterOptions[key]]; // Add "all" option
    });

    // Set default filter values to "all"
    if (Object.keys(updatedFilterOptions).length > 0) {
      setFilterValues(Object.fromEntries(Object.keys(updatedFilterOptions).map(key => [key, 'all'])));
    }

    setUpdatedFilterOptions(updatedFilterOptions);
    setFilterValues(Object.fromEntries(Object.keys(updatedFilterOptions).map(key => [key, 'all'])));
  }

}, [filterOptions]);
  

  return(
    <Card>
      <CardSection type='header' title='useGenerationLogs test'>
        <div>
          Sort Options: 
          <FilterSelectGroup
          filterOptions={sortOptions}
          values={sortValues}
          onChange={handleSortChange}
        />
        </div>
        <div>
          Filter Options:
          <FilterSelectGroup
            filterOptions={updatedFilterOptions}
            values={filterValues}
            onChange={handleFilterChange}
          />
          
        </div>
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
        <div>rawResponse: {rawResponse}</div>
      </CardSection>
    </Card>
  )

}

export default ApiServicesTestScreen;
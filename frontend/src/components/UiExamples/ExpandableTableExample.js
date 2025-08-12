// ExpandableTable Examples Component - Showcase all ExpandableTable variations
// Interactive examples and builder for ExpandableTable with useExpandableRows hook
// Perfect for development reference and testing different configurations

import React, { useState } from 'react';
import { 
  ExpandableTable, 
  useExpandableRows 
} from '../../shared/ui/ExpandableTable/index.js';
import { Card, CardSection } from '../../shared/ui/Card/index.js';
import { Select, FormField } from '../../shared/ui/Form/index.js';
import { Badge, StatusBadge } from '../../shared/ui/Badge/index.js';
import { Button } from '../../shared/ui/Button/index.js';

function ExpandableTableExamples() {
  // Sample data for examples
  const sampleData = [
    {
      id: 1,
      name: 'Monster Generation Request',
      type: 'LLM',
      status: 'completed',
      created: '2024-01-15 14:30',
      priority: 5,
      details: {
        prompt: 'Generate a fire-breathing dragon with ancient wisdom',
        model: 'GPT-4',
        tokens: 1250,
        duration: '3.2s',
        metadata: { temperature: 0.8, maxTokens: 2000 }
      }
    },
    {
      id: 2,
      name: 'Party Formation Analysis',
      type: 'Analytics',
      status: 'processing',
      created: '2024-01-15 14:25',
      priority: 3,
      details: {
        analysis: 'Evaluating optimal party composition for dungeon raid',
        metrics: ['damage_output', 'survivability', 'synergy'],
        progress: 0.65,
        estimatedCompletion: '2 minutes'
      }
    },
    {
      id: 3,
      name: 'Card Art Generation',
      type: 'Image',
      status: 'failed',
      created: '2024-01-15 14:20',
      priority: 1,
      details: {
        prompt: 'Epic fantasy card artwork with magical effects',
        service: 'DALL-E',
        error: 'Content policy violation: magical effects too intense',
        retryCount: 2,
        lastAttempt: '2024-01-15 14:22'
      }
    },
    {
      id: 4,
      name: 'Dungeon Layout Generator',
      type: 'Procedural',
      status: 'queued',
      created: '2024-01-15 14:15',
      priority: 4,
      details: {
        algorithm: 'Recursive Backtracking',
        size: '50x50',
        difficulty: 'Hard',
        features: ['traps', 'secret_passages', 'boss_room'],
        queuePosition: 3
      }
    },
    {
      id: 5,
      name: 'Lore Generation',
      type: 'LLM',
      status: 'completed',
      created: '2024-01-15 14:10',
      priority: 2,
      details: {
        category: 'Ancient Civilizations',
        wordCount: 850,
        references: ['Book of Dragons', 'Historia Magica'],
        themes: ['mystery', 'ancient power', 'forgotten knowledge']
      }
    }
  ];

  // Column definitions
  const columns = [
    { 
      key: 'name', 
      header: 'Name', 
      width: '35%',
      render: (value) => (
        <span style={{ fontWeight: 'var(--font-weight-medium)' }}>{value}</span>
      )
    },
    { 
      key: 'type', 
      header: 'Type', 
      width: '15%',
      render: (value) => (
        <Badge variant="secondary" size="sm">{value}</Badge>
      )
    },
    { 
      key: 'status', 
      header: 'Status', 
      width: '15%',
      render: (value) => {
        const statusMap = {
          completed: 'success',
          processing: 'info',
          failed: 'error',
          queued: 'warning'
        };
        return <StatusBadge status={statusMap[value]} size="sm">{value}</StatusBadge>;
      }
    },
    { 
      key: 'priority', 
      header: 'Priority', 
      width: '10%',
      render: (value) => (
        <Badge 
          variant={value >= 4 ? 'error' : value >= 3 ? 'warning' : 'success'} 
          size="sm"
        >
          {value}
        </Badge>
      )
    },
    { 
      key: 'created', 
      header: 'Created', 
      width: '25%',
      render: (value) => (
        <span style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>
          {value}
        </span>
      )
    }
  ];

  // Expandable rows hooks for different examples
  const basicExpandableRows = useExpandableRows({
    allowMultiple: true,
    defaultExpanded: []
  });

  const singleExpandableRows = useExpandableRows({
    allowMultiple: false,
    defaultExpanded: []
  });

  // Interactive builder state
  const [builderConfig, setBuilderConfig] = useState({
    size: 'md',
    striped: false,
    bordered: false,
    hover: true,
    animateExpansion: true,
    allowMultiple: true,
    expandIconColumn: 'name'
  });

  const builderExpandableRows = useExpandableRows({
    allowMultiple: builderConfig.allowMultiple,
    defaultExpanded: []
  });

  const handleBuilderChange = (field, value) => {
    setBuilderConfig(prev => ({
      ...prev,
      [field]: value === 'true' ? true : value === 'false' ? false : value
    }));
  };

  // Render expanded content function
  const renderExpandedContent = (row) => {
    const { details } = row;
    
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        gap: '12px',
        fontSize: '14px'
      }}>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
          gap: '12px' 
        }}>
          {Object.entries(details).map(([key, value]) => (
            <div key={key} style={{ 
              background: 'var(--color-surface-secondary)', 
              padding: '8px', 
              borderRadius: 'var(--radius-sm)' 
            }}>
              <div style={{ 
                fontWeight: 'var(--font-weight-medium)', 
                color: 'var(--color-text-primary)',
                marginBottom: '4px',
                textTransform: 'capitalize'
              }}>
                {key.replace(/([A-Z])/g, ' $1').replace(/_/g, ' ')}
              </div>
              <div style={{ color: 'var(--color-text-secondary)' }}>
                {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
              </div>
            </div>
          ))}
        </div>
        
        <div style={{ 
          display: 'flex', 
          gap: '8px', 
          marginTop: '8px',
          paddingTop: '8px',
          borderTop: '1px solid var(--color-surface-secondary)'
        }}>
          <Button size="sm" variant="primary">View Details</Button>
          <Button size="sm" variant="secondary">Edit</Button>
          {row.status === 'failed' && (
            <Button size="sm" variant="warning">Retry</Button>
          )}
        </div>
      </div>
    );
  };

  return (
    <Card size="lg" padding="lg" className="expandable-table-examples">
      <CardSection type="header" title="ExpandableTable Components Showcase" />
      
      {/* Basic Example */}
      <CardSection type="content" title="Basic Expandable Table">
        <div style={{ marginBottom: '16px' }}>
          <p style={{ color: 'var(--color-text-secondary)', margin: '0 0 12px 0' }}>
            Click on any row to expand and see detailed information. Multiple rows can be expanded simultaneously.
          </p>
          <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
            <Button 
              size="sm" 
              variant="secondary"
              onClick={() => basicExpandableRows.expandAll(sampleData)}
            >
              Expand All
            </Button>
            <Button 
              size="sm" 
              variant="secondary"
              onClick={basicExpandableRows.collapseAll}
            >
              Collapse All
            </Button>
            <Badge size="sm" variant="info">
              {basicExpandableRows.expandedCount} expanded
            </Badge>
          </div>
        </div>
        
        <ExpandableTable
          columns={columns}
          data={sampleData}
          expandableRows={basicExpandableRows}
          renderExpandedContent={renderExpandedContent}
          expandIconColumn="name"
          hover={true}
        />
      </CardSection>

      {/* Single Row Expansion */}
      <CardSection type="content" title="Single Row Expansion">
        <div style={{ marginBottom: '16px' }}>
          <p style={{ color: 'var(--color-text-secondary)', margin: '0 0 12px 0' }}>
            Only one row can be expanded at a time. Expanding a new row collapses the previous one.
          </p>
        </div>
        
        <ExpandableTable
          columns={columns}
          data={sampleData.slice(0, 3)} // Fewer rows for this example
          expandableRows={singleExpandableRows}
          renderExpandedContent={renderExpandedContent}
          expandIconColumn="name"
          striped={true}
        />
      </CardSection>

      {/* Styling Variations */}
      <CardSection type="content" title="Styling Variations">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Small, Bordered */}
          <div>
            <h4 style={{ marginBottom: '8px', color: 'var(--color-text-primary)' }}>
              Small Size, Bordered
            </h4>
            <ExpandableTable
              columns={columns}
              data={sampleData.slice(0, 2)}
              expandableRows={useExpandableRows()}
              renderExpandedContent={renderExpandedContent}
              size="sm"
              bordered={true}
              animateExpansion={false}
            />
          </div>

          {/* Large, No Animation */}
          <div>
            <h4 style={{ marginBottom: '8px', color: 'var(--color-text-primary)' }}>
              Large Size, No Animation
            </h4>
            <ExpandableTable
              columns={columns}
              data={sampleData.slice(0, 2)}
              expandableRows={useExpandableRows()}
              renderExpandedContent={renderExpandedContent}
              size="lg"
              striped={true}
              hover={false}
              animateExpansion={false}
            />
          </div>
        </div>
      </CardSection>

      {/* Interactive Builder */}
      <CardSection type="content" title="Interactive Table Builder">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Builder Controls */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '16px',
            padding: '16px',
            background: 'var(--color-surface-secondary)',
            borderRadius: 'var(--radius-md)'
          }}>
            
            <FormField label="Table Size">
              <Select
                value={builderConfig.size}
                onChange={(e) => handleBuilderChange('size', e.target.value)}
                options={[
                  { value: 'sm', label: 'Small' },
                  { value: 'md', label: 'Medium' },
                  { value: 'lg', label: 'Large' }
                ]}
              />
            </FormField>

            <FormField label="Striped Rows">
              <Select
                value={builderConfig.striped.toString()}
                onChange={(e) => handleBuilderChange('striped', e.target.value)}
                options={[
                  { value: 'false', label: 'No' },
                  { value: 'true', label: 'Yes' }
                ]}
              />
            </FormField>

            <FormField label="Bordered">
              <Select
                value={builderConfig.bordered.toString()}
                onChange={(e) => handleBuilderChange('bordered', e.target.value)}
                options={[
                  { value: 'false', label: 'No' },
                  { value: 'true', label: 'Yes' }
                ]}
              />
            </FormField>

            <FormField label="Hover Effects">
              <Select
                value={builderConfig.hover.toString()}
                onChange={(e) => handleBuilderChange('hover', e.target.value)}
                options={[
                  { value: 'true', label: 'Yes' },
                  { value: 'false', label: 'No' }
                ]}
              />
            </FormField>

            <FormField label="Animate Expansion">
              <Select
                value={builderConfig.animateExpansion.toString()}
                onChange={(e) => handleBuilderChange('animateExpansion', e.target.value)}
                options={[
                  { value: 'true', label: 'Yes' },
                  { value: 'false', label: 'No' }
                ]}
              />
            </FormField>

            <FormField label="Multiple Expansion">
              <Select
                value={builderConfig.allowMultiple.toString()}
                onChange={(e) => handleBuilderChange('allowMultiple', e.target.value)}
                options={[
                  { value: 'true', label: 'Allow Multiple' },
                  { value: 'false', label: 'Single Only' }
                ]}
              />
            </FormField>
          </div>

          {/* Builder Result */}
          <div>
            <div style={{ display: 'flex', gap: '8px', marginBottom: '12px', alignItems: 'center' }}>
              <h4 style={{ margin: 0, color: 'var(--color-text-primary)' }}>Your Table</h4>
              <Badge size="sm" variant="info">
                {builderExpandableRows.expandedCount} expanded
              </Badge>
            </div>
            
            <ExpandableTable
              columns={columns}
              data={sampleData.slice(0, 3)}
              expandableRows={builderExpandableRows}
              renderExpandedContent={renderExpandedContent}
              size={builderConfig.size}
              striped={builderConfig.striped}
              bordered={builderConfig.bordered}
              hover={builderConfig.hover}
              animateExpansion={builderConfig.animateExpansion}
              expandIconColumn={builderConfig.expandIconColumn}
            />
          </div>

          {/* Code Example */}
          <div style={{ 
            background: 'var(--color-surface-primary)', 
            padding: '16px', 
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--color-text-muted)'
          }}>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)', fontSize: '14px' }}>
              Code Example:
            </h4>
            <code style={{ 
              fontFamily: 'var(--font-family-mono)', 
              fontSize: '12px',
              color: 'var(--color-text-secondary)',
              display: 'block',
              whiteSpace: 'pre-wrap'
            }}>
{`// Hook setup
const expandableRows = useExpandableRows({
  allowMultiple: ${builderConfig.allowMultiple}
});

// Component usage
<ExpandableTable
  columns={columns}
  data={data}
  expandableRows={expandableRows}
  renderExpandedContent={(row) => <div>{/* Your content */}</div>}
  size="${builderConfig.size}"
  ${builderConfig.striped ? 'striped' : ''}
  ${builderConfig.bordered ? 'bordered' : ''}
  ${builderConfig.hover ? 'hover' : ''}
  ${builderConfig.animateExpansion ? 'animateExpansion' : ''}
  expandIconColumn="${builderConfig.expandIconColumn}"
/>`}
            </code>
          </div>
        </div>
      </CardSection>

      {/* Hook Examples */}
      <CardSection type="content" title="useExpandableRows Hook Examples">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ 
            padding: '16px', 
            background: 'var(--color-surface-secondary)', 
            borderRadius: 'var(--radius-md)' 
          }}>
            <h4 style={{ margin: '0 0 12px 0', color: 'var(--color-text-primary)' }}>
              Hook Configuration Options
            </h4>
            <code style={{ 
              fontFamily: 'var(--font-family-mono)', 
              fontSize: '12px',
              color: 'var(--color-text-secondary)',
              display: 'block',
              whiteSpace: 'pre-wrap'
            }}>
{`// Basic usage
const expandableRows = useExpandableRows();

// Single row expansion only
const expandableRows = useExpandableRows({
  allowMultiple: false
});

// With default expanded rows
const expandableRows = useExpandableRows({
  defaultExpanded: [1, 3, 5],
  allowMultiple: true
});

// With callbacks
const expandableRows = useExpandableRows({
  onExpand: (rowId) => console.log('Expanded:', rowId),
  onCollapse: (rowId) => console.log('Collapsed:', rowId)
});`}
            </code>
          </div>

          <div style={{ 
            padding: '16px', 
            background: 'var(--color-surface-secondary)', 
            borderRadius: 'var(--radius-md)' 
          }}>
            <h4 style={{ margin: '0 0 12px 0', color: 'var(--color-text-primary)' }}>
              Available Hook Methods
            </h4>
            <ul style={{ 
              margin: 0, 
              paddingLeft: '20px',
              color: 'var(--color-text-secondary)',
              fontSize: '14px'
            }}>
              <li><code>toggleRow(id)</code> - Toggle specific row</li>
              <li><code>expandRow(id)</code> - Expand specific row</li>
              <li><code>collapseRow(id)</code> - Collapse specific row</li>
              <li><code>expandAll(data)</code> - Expand all rows</li>
              <li><code>collapseAll()</code> - Collapse all rows</li>
              <li><code>isRowExpanded(id)</code> - Check if row is expanded</li>
              <li><code>expandedCount</code> - Number of expanded rows</li>
              <li><code>hasExpandedRows</code> - Boolean if any rows expanded</li>
            </ul>
          </div>
        </div>
      </CardSection>
    </Card>
  );
}

export default ExpandableTableExamples;
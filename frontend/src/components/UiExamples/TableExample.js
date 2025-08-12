// Table Examples Component - Showcase all Table component variations
// Interactive examples and builder for Table component with all styling options
// Perfect for development reference and testing different table configurations

import React, { useState } from 'react';
import { 
  Table,
  TableHead, 
  TableBody, 
  TableRow, 
  TableHeaderCell, 
  TableCell,
  TABLE_SIZES
} from '../../shared/ui/Table/index.js';
import { Badge, StatusBadge } from '../../shared/ui/Badge/index.js';
import { Button } from '../../shared/ui/Button/index.js';
import { Card, CardSection } from '../../shared/ui/Card/index.js';
import { Select, FormField } from '../../shared/ui/Form/index.js';

function TableExamples() {
  // Interactive builder state
  const [tableBuilder, setTableBuilder] = useState({
    size: 'md',
    striped: false,
    bordered: false,
    hover: true,
    dataType: 'monsters', // 'monsters', 'users', 'logs'
    showActions: true,
    customRender: true
  });

  const handleBuilderChange = (field, value) => {
    setTableBuilder(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Sample data sets
  const sampleData = {
    monsters: [
      { 
        id: 1001, 
        name: 'Fire Drake', 
        type: 'Dragon', 
        level: 45, 
        status: 'active',
        health: 850,
        created: '2024-03-15'
      },
      { 
        id: 1002, 
        name: 'Shadow Wolf', 
        type: 'Beast', 
        level: 23, 
        status: 'resting',
        health: 320,
        created: '2024-03-14'
      },
      { 
        id: 1003, 
        name: 'Crystal Golem', 
        type: 'Elemental', 
        level: 67, 
        status: 'training',
        health: 1200,
        created: '2024-03-13'
      },
      { 
        id: 1004, 
        name: 'Void Mage', 
        type: 'Humanoid', 
        level: 89, 
        status: 'injured',
        health: 45,
        created: '2024-03-12'
      }
    ],
    users: [
      { 
        id: 501, 
        username: 'dragonmaster99', 
        email: 'user@example.com', 
        role: 'admin',
        status: 'online',
        lastLogin: '2024-03-15',
        monstersOwned: 12
      },
      { 
        id: 502, 
        username: 'beastwhisperer', 
        email: 'beast@example.com', 
        role: 'user',
        status: 'offline',
        lastLogin: '2024-03-14',
        monstersOwned: 8
      },
      { 
        id: 503, 
        username: 'voidcaller', 
        email: 'void@example.com', 
        role: 'moderator',
        status: 'away',
        lastLogin: '2024-03-15',
        monstersOwned: 15
      }
    ],
    logs: [
      { 
        id: 'log_001', 
        type: 'generation', 
        message: 'Monster generation completed',
        timestamp: '2024-03-15 14:32:15',
        status: 'success',
        duration: '2.3s'
      },
      { 
        id: 'log_002', 
        type: 'battle', 
        message: 'Battle simulation started',
        timestamp: '2024-03-15 14:30:45',
        status: 'pending',
        duration: '1.8s'
      },
      { 
        id: 'log_003', 
        type: 'error', 
        message: 'Failed to load monster assets',
        timestamp: '2024-03-15 14:28:12',
        status: 'error',
        duration: '0.1s'
      }
    ]
  };

  // Column definitions for different data types
  const columnDefinitions = {
    monsters: [
      { key: 'id', header: 'ID', width: '10%' },
      { 
        key: 'name', 
        header: 'Name', 
        width: '25%',
        render: tableBuilder.customRender ? 
          (value, row) => <strong style={{ color: 'var(--primary-color)' }}>{value}</strong> : 
          null
      },
      { key: 'type', header: 'Type', width: '15%' },
      { key: 'level', header: 'Level', width: '10%', cellClass: 'table-cell-numeric' },
      { 
        key: 'status', 
        header: 'Status', 
        width: '15%',
        render: tableBuilder.customRender ? 
          (value) => <StatusBadge status={value === 'active' ? 'success' : value === 'injured' ? 'error' : 'warning'} size="sm">{value}</StatusBadge> :
          null
      },
      { key: 'health', header: 'Health', width: '10%', cellClass: 'table-cell-numeric' },
      ...(tableBuilder.showActions ? [{ 
        key: 'actions', 
        header: 'Actions', 
        width: '15%',
        render: () => (
          <div style={{ display: 'flex', gap: '4px' }}>
            <Button size="sm" variant="primary">Edit</Button>
            <Button size="sm" variant="secondary">View</Button>
          </div>
        ),
        cellClass: 'table-cell-actions'
      }] : [])
    ],
    users: [
      { key: 'id', header: 'ID', width: '8%' },
      { 
        key: 'username', 
        header: 'Username', 
        width: '20%',
        render: tableBuilder.customRender ? 
          (value) => <code style={{ background: 'var(--color-surface-secondary)', padding: '2px 4px', borderRadius: '2px' }}>{value}</code> :
          null
      },
      { key: 'email', header: 'Email', width: '25%' },
      { 
        key: 'role', 
        header: 'Role', 
        width: '12%',
        render: tableBuilder.customRender ? 
          (value) => <Badge variant={value === 'admin' ? 'error' : value === 'moderator' ? 'warning' : 'secondary'} size="sm">{value}</Badge> :
          null
      },
      { 
        key: 'status', 
        header: 'Status', 
        width: '10%',
        render: tableBuilder.customRender ? 
          (value) => <StatusBadge status={value === 'online' ? 'success' : value === 'offline' ? 'error' : 'warning'} size="sm">{value}</StatusBadge> :
          null
      },
      { key: 'monstersOwned', header: 'Monsters', width: '10%', cellClass: 'table-cell-numeric' },
      ...(tableBuilder.showActions ? [{ 
        key: 'actions', 
        header: 'Actions', 
        width: '15%',
        render: () => (
          <div style={{ display: 'flex', gap: '4px' }}>
            <Button size="sm" variant="primary">Edit</Button>
            <Button size="sm" variant="danger">Ban</Button>
          </div>
        ),
        cellClass: 'table-cell-actions'
      }] : [])
    ],
    logs: [
      { key: 'id', header: 'Log ID', width: '12%' },
      { 
        key: 'type', 
        header: 'Type', 
        width: '12%',
        render: tableBuilder.customRender ? 
          (value) => <Badge variant={value === 'error' ? 'error' : value === 'generation' ? 'success' : 'info'} size="sm">{value}</Badge> :
          null
      },
      { key: 'message', header: 'Message', width: '35%' },
      { key: 'timestamp', header: 'Time', width: '18%' },
      { 
        key: 'status', 
        header: 'Status', 
        width: '10%',
        render: tableBuilder.customRender ? 
          (value) => <StatusBadge status={value} size="sm" /> :
          null
      },
      { key: 'duration', header: 'Duration', width: '8%', cellClass: 'table-cell-numeric' },
      ...(tableBuilder.showActions ? [{ 
        key: 'actions', 
        header: 'Actions', 
        width: '8%',
        render: () => (
          <Button size="sm" variant="secondary">View</Button>
        ),
        cellClass: 'table-cell-actions'
      }] : [])
    ]
  };

  const getCurrentData = () => sampleData[tableBuilder.dataType];
  const getCurrentColumns = () => columnDefinitions[tableBuilder.dataType];

  return (
    <Card size="lg" padding="lg" className="table-examples">
      <CardSection type="header" title="Table Components Showcase" />
      
      {/* Basic Table Examples */}
      <CardSection type="content" title="Basic Table Examples">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
          
          {/* Size Variations */}
          <div>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>Table Sizes</h4>
            
            <div style={{ marginBottom: '16px' }}>
              <h5 style={{ marginBottom: '8px', color: 'var(--color-text-secondary)' }}>Small Table</h5>
              <Table
                size="sm"
                columns={[
                  { key: 'name', header: 'Name', width: '40%' },
                  { key: 'type', header: 'Type', width: '30%' },
                  { key: 'level', header: 'Level', width: '30%' }
                ]}
                data={sampleData.monsters.slice(0, 2)}
              />
            </div>
            
            <div style={{ marginBottom: '16px' }}>
              <h5 style={{ marginBottom: '8px', color: 'var(--color-text-secondary)' }}>Medium Table (Default)</h5>
              <Table
                size="md"
                columns={[
                  { key: 'name', header: 'Name', width: '40%' },
                  { key: 'type', header: 'Type', width: '30%' },
                  { key: 'level', header: 'Level', width: '30%' }
                ]}
                data={sampleData.monsters.slice(0, 2)}
              />
            </div>
            
            <div>
              <h5 style={{ marginBottom: '8px', color: 'var(--color-text-secondary)' }}>Large Table</h5>
              <Table
                size="lg"
                columns={[
                  { key: 'name', header: 'Name', width: '40%' },
                  { key: 'type', header: 'Type', width: '30%' },
                  { key: 'level', header: 'Level', width: '30%' }
                ]}
                data={sampleData.monsters.slice(0, 2)}
              />
            </div>
          </div>

          {/* Style Variations */}
          <div>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>Style Variations</h4>
            
            <div style={{ display: 'grid', gap: '24px' }}>
              <div>
                <h5 style={{ marginBottom: '8px', color: 'var(--color-text-secondary)' }}>Default</h5>
                <Table
                  columns={[
                    { key: 'username', header: 'Username', width: '30%' },
                    { key: 'role', header: 'Role', width: '20%' },
                    { key: 'status', header: 'Status', width: '20%' },
                    { key: 'monstersOwned', header: 'Monsters', width: '30%' }
                  ]}
                  data={sampleData.users}
                />
              </div>
              
              <div>
                <h5 style={{ marginBottom: '8px', color: 'var(--color-text-secondary)' }}>Striped</h5>
                <Table
                  striped
                  columns={[
                    { key: 'username', header: 'Username', width: '30%' },
                    { key: 'role', header: 'Role', width: '20%' },
                    { key: 'status', header: 'Status', width: '20%' },
                    { key: 'monstersOwned', header: 'Monsters', width: '30%' }
                  ]}
                  data={sampleData.users}
                />
              </div>
              
              <div>
                <h5 style={{ marginBottom: '8px', color: 'var(--color-text-secondary)' }}>Bordered</h5>
                <Table
                  bordered
                  columns={[
                    { key: 'username', header: 'Username', width: '30%' },
                    { key: 'role', header: 'Role', width: '20%' },
                    { key: 'status', header: 'Status', width: '20%' },
                    { key: 'monstersOwned', header: 'Monsters', width: '30%' }
                  ]}
                  data={sampleData.users}
                />
              </div>
              
              <div>
                <h5 style={{ marginBottom: '8px', color: 'var(--color-text-secondary)' }}>Hover + Striped + Bordered</h5>
                <Table
                  striped
                  bordered
                  hover
                  columns={[
                    { key: 'username', header: 'Username', width: '30%' },
                    { key: 'role', header: 'Role', width: '20%' },
                    { key: 'status', header: 'Status', width: '20%' },
                    { key: 'monstersOwned', header: 'Monsters', width: '30%' }
                  ]}
                  data={sampleData.users}
                />
              </div>
            </div>
          </div>

          {/* Custom Rendering Examples */}
          <div>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>Custom Column Rendering</h4>
            <Table
              hover
              striped
              columns={[
                { 
                  key: 'name', 
                  header: 'Monster Name', 
                  width: '25%',
                  render: (value, row) => (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{ 
                        width: '24px', 
                        height: '24px', 
                        borderRadius: '50%', 
                        background: `linear-gradient(45deg, var(--primary-color), var(--secondary-color))`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '12px'
                      }}>
                        {row.type[0]}
                      </div>
                      <strong>{value}</strong>
                    </div>
                  )
                },
                { 
                  key: 'level', 
                  header: 'Level', 
                  width: '15%',
                  render: (value) => (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span>{value}</span>
                      <div style={{
                        width: '40px',
                        height: '4px',
                        background: 'var(--color-surface-secondary)',
                        borderRadius: '2px',
                        overflow: 'hidden'
                      }}>
                        <div style={{
                          width: `${Math.min(100, (value / 100) * 100)}%`,
                          height: '100%',
                          background: value > 50 ? 'var(--success-color)' : value > 25 ? 'var(--warning-color)' : 'var(--error-color)',
                          transition: 'width 0.3s ease'
                        }} />
                      </div>
                    </div>
                  ),
                  cellClass: 'table-cell-numeric'
                },
                { 
                  key: 'health', 
                  header: 'Health', 
                  width: '20%',
                  render: (value, row) => (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                      <span style={{ fontSize: '14px', fontWeight: 'bold' }}>
                        {value} HP
                      </span>
                      <div style={{
                        width: '100%',
                        height: '6px',
                        background: 'var(--color-surface-secondary)',
                        borderRadius: '3px',
                        overflow: 'hidden'
                      }}>
                        <div style={{
                          width: `${Math.min(100, (value / 1200) * 100)}%`,
                          height: '100%',
                          background: value > 800 ? 'var(--success-color)' : value > 400 ? 'var(--warning-color)' : 'var(--error-color)',
                          transition: 'width 0.3s ease'
                        }} />
                      </div>
                    </div>
                  )
                },
                { 
                  key: 'status', 
                  header: 'Status', 
                  width: '20%',
                  render: (value) => (
                    <StatusBadge 
                      status={value === 'active' ? 'success' : value === 'injured' ? 'error' : 'warning'} 
                      size="sm"
                    >
                      {value}
                    </StatusBadge>
                  )
                },
                { 
                  key: 'actions', 
                  header: 'Actions', 
                  width: '20%',
                  render: (_, row) => (
                    <div style={{ display: 'flex', gap: '4px' }}>
                      <Button size="sm" variant="primary">Edit</Button>
                      <Button size="sm" variant="secondary">Battle</Button>
                      <Button size="sm" variant="danger">Release</Button>
                    </div>
                  ),
                  cellClass: 'table-cell-actions'
                }
              ]}
              data={sampleData.monsters}
            />
          </div>

          {/* Empty State */}
          <div>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>Empty State</h4>
            <Table
              columns={[
                { key: 'name', header: 'Name', width: '50%' },
                { key: 'status', header: 'Status', width: '50%' }
              ]}
              data={[]}
              emptyMessage="No monsters found in your collection"
            />
          </div>
        </div>
      </CardSection>

      {/* Manual Table API Example */}
      <CardSection type="content" title="Manual Table API">
        <div>
          <p style={{ marginBottom: '16px', color: 'var(--color-text-secondary)' }}>
            For complex tables, you can use the manual API with TableHead, TableBody, TableRow, etc.
          </p>
          <Table size="md" hover>
            <TableHead>
              <TableRow>
                <TableHeaderCell>Custom Header</TableHeaderCell>
                <TableHeaderCell>Complex Content</TableHeaderCell>
                <TableHeaderCell>Manual Control</TableHeaderCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow>
                <TableCell>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '12px', height: '12px', background: 'var(--success-color)', borderRadius: '50%' }} />
                    Custom Cell Content
                  </div>
                </TableCell>
                <TableCell>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <span>Multi-line content</span>
                    <span style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>
                      With detailed information
                    </span>
                  </div>
                </TableCell>
                <TableCell className="table-cell-actions">
                  <Button size="sm" variant="primary">Action</Button>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>
                  <Badge variant="warning">Important</Badge>
                </TableCell>
                <TableCell>
                  <code style={{ background: 'var(--color-surface-secondary)', padding: '2px 4px', borderRadius: '2px' }}>
                    Code content
                  </code>
                </TableCell>
                <TableCell className="table-cell-actions">
                  <Button size="sm" variant="secondary">View</Button>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
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
            
            <FormField label="Data Type">
              <Select
                value={tableBuilder.dataType}
                onChange={(e) => handleBuilderChange('dataType', e.target.value)}
                options={[
                  { value: 'monsters', label: 'Monster Data' },
                  { value: 'users', label: 'User Data' },
                  { value: 'logs', label: 'Log Data' }
                ]}
              />
            </FormField>

            <FormField label="Table Size">
              <Select
                value={tableBuilder.size}
                onChange={(e) => handleBuilderChange('size', e.target.value)}
                options={Object.values(TABLE_SIZES).map(size => ({
                  value: size,
                  label: size.toUpperCase()
                }))}
              />
            </FormField>

            <FormField label="Style Options">
              <Select
                value={`${tableBuilder.striped ? 'striped' : 'plain'}-${tableBuilder.bordered ? 'bordered' : 'borderless'}-${tableBuilder.hover ? 'hover' : 'static'}`}
                onChange={(e) => {
                  const [stripeStyle, borderStyle, hoverStyle] = e.target.value.split('-');
                  handleBuilderChange('striped', stripeStyle === 'striped');
                  handleBuilderChange('bordered', borderStyle === 'bordered');
                  handleBuilderChange('hover', hoverStyle === 'hover');
                }}
                options={[
                  { value: 'plain-borderless-static', label: 'Default' },
                  { value: 'striped-borderless-static', label: 'Striped' },
                  { value: 'plain-bordered-static', label: 'Bordered' },
                  { value: 'plain-borderless-hover', label: 'Hover Effects' },
                  { value: 'striped-bordered-hover', label: 'All Styles' }
                ]}
              />
            </FormField>

            <FormField label="Show Actions">
              <Select
                value={tableBuilder.showActions ? 'true' : 'false'}
                onChange={(e) => handleBuilderChange('showActions', e.target.value === 'true')}
                options={[
                  { value: 'true', label: 'Yes' },
                  { value: 'false', label: 'No' }
                ]}
              />
            </FormField>

            <FormField label="Custom Rendering">
              <Select
                value={tableBuilder.customRender ? 'true' : 'false'}
                onChange={(e) => handleBuilderChange('customRender', e.target.value === 'true')}
                options={[
                  { value: 'true', label: 'Enhanced' },
                  { value: 'false', label: 'Plain Text' }
                ]}
              />
            </FormField>
          </div>

          {/* Builder Result */}
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>
              Your Table ({getCurrentData().length} rows)
            </h4>
            <Table
              size={tableBuilder.size}
              striped={tableBuilder.striped}
              bordered={tableBuilder.bordered}
              hover={tableBuilder.hover}
              columns={getCurrentColumns()}
              data={getCurrentData()}
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
              {`<Table
  size="${tableBuilder.size}"${tableBuilder.striped ? '\n  striped' : ''}${tableBuilder.bordered ? '\n  bordered' : ''}${tableBuilder.hover ? '\n  hover' : ''}
  columns={[
    { key: 'id', header: 'ID', width: '10%' },
    { 
      key: 'name', 
      header: 'Name', 
      width: '30%'${tableBuilder.customRender ? ',\n      render: (value) => <strong>{value}</strong>' : ''} 
    },
    // ... more columns
  ]}
  data={${tableBuilder.dataType}Data}
  emptyMessage="No ${tableBuilder.dataType} found"
/>`}
            </code>
          </div>
        </div>
      </CardSection>
    </Card>
  );
}

export default TableExamples;
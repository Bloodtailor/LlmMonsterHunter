// Pagination Examples Component - Showcase all Pagination component variations
// Interactive examples and builder for Pagination layouts and configurations
// Perfect for development reference and testing different pagination setups

import React, { useState } from 'react';
import { 
  Pagination,
  PaginationInfo,
  PageJumper,
  ItemsPerPageSelector,
  PaginationPrimitive
} from '../../shared/ui/Pagination/index.js';
import { usePagination } from '../../shared/ui/Pagination/usePagination.js';
import { Card, CardSection } from '../../shared/ui/Card/index.js';
import { Select, FormField } from '../../shared/ui/Form/index.js';
import { Button } from '../../shared/ui/Button/index.js';

function PaginationExamples() {
  // Interactive builder state
  const [builderConfig, setBuilderConfig] = useState({
    layout: 'default',
    total: 150,
    limit: 12,
    currentPage: 5,
    itemName: 'items',
    showFirstLast: true,
    showPrevNext: true
  });

  // Example pagination instances for showcases
  const smallPagination = usePagination({ 
    limit: 5, 
    total: 23,
    initialPage: 3
  });

  const mediumPagination = usePagination({ 
    limit: 10, 
    total: 156,
    initialPage: 8
  });

  const largePagination = usePagination({ 
    limit: 25, 
    total: 2847,
    initialPage: 15
  });

  // Builder pagination instance
  const builderPagination = usePagination({
    limit: builderConfig.limit,
    total: builderConfig.total,
    initialPage: builderConfig.currentPage
  });

  const handleBuilderChange = (field, value) => {
    setBuilderConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleLimitChange = (newLimit) => {
    setBuilderConfig(prev => ({
      ...prev,
      limit: newLimit
    }));
    // Note: In real usage, you'd also call builderPagination.setLimit(newLimit)
  };

  const renderBuilderPagination = () => {
    const commonProps = {
      pagination: builderPagination,
      itemName: builderConfig.itemName
    };

    switch (builderConfig.layout) {
      case 'simple':
        return (
          <Pagination
            layout="simple"
            {...commonProps}
          />
        );
      
      case 'full':
        return (
          <Pagination
            layout="full"
            currentLimit={builderConfig.limit}
            onLimitChange={handleLimitChange}
            itemsPerPageOptions={[5, 10, 12, 25, 50]}
            {...commonProps}
          />
        );
      
      default:
        return (
          <Pagination
            layout="default"
            {...commonProps}
          />
        );
    }
  };

  return (
    <Card size="lg" padding="lg" className="pagination-examples">
      <CardSection type="header" title="Pagination Components Showcase" />
      
      {/* Layout Examples */}
      <CardSection type="content" title="Pagination Layouts">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
          
          {/* Default Layout */}
          <div>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>
              Default Layout (Centered Pagination)
            </h4>
            <div style={{ 
              padding: '20px', 
              background: 'var(--color-surface-secondary)', 
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--color-text-muted)'
            }}>
              <Pagination
                layout="default"
                pagination={mediumPagination}
                itemName="monsters"
              />
            </div>
            <p style={{ 
              fontSize: '14px', 
              color: 'var(--color-text-muted)', 
              marginTop: '8px',
              margin: '8px 0 0 0'
            }}>
              Clean centered pagination with first/last and prev/next buttons
            </p>
          </div>

          {/* Simple Layout */}
          <div>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>
              Simple Layout (Info + Basic Pagination)
            </h4>
            <div style={{ 
              padding: '20px', 
              background: 'var(--color-surface-secondary)', 
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--color-text-muted)'
            }}>
              <Pagination
                layout="simple"
                pagination={smallPagination}
                itemName="items"
              />
            </div>
            <p style={{ 
              fontSize: '14px', 
              color: 'var(--color-text-muted)', 
              marginTop: '8px',
              margin: '8px 0 0 0'
            }}>
              Info display with simplified pagination controls (no first/last buttons)
            </p>
          </div>

          {/* Full Layout */}
          <div>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>
              Full Layout (Items Per Page + Pagination + Jumper)
            </h4>
            <div style={{ 
              padding: '20px', 
              background: 'var(--color-surface-secondary)', 
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--color-text-muted)'
            }}>
              <Pagination
                layout="full"
                pagination={largePagination}
                itemName="results"
                currentLimit={25}
                onLimitChange={(newLimit) => console.log('Limit changed to:', newLimit)}
                itemsPerPageOptions={[10, 25, 50, 100]}
              />
            </div>
            <p style={{ 
              fontSize: '14px', 
              color: 'var(--color-text-muted)', 
              marginTop: '8px',
              margin: '8px 0 0 0'
            }}>
              Complete pagination with items-per-page selector and page jumper
            </p>
          </div>
        </div>
      </CardSection>

      {/* Individual Components */}
      <CardSection type="content" title="Individual Pagination Components">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* PaginationInfo */}
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>
              PaginationInfo - Status Display
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ 
                padding: '12px', 
                background: 'var(--color-surface-secondary)', 
                borderRadius: 'var(--radius-sm)' 
              }}>
                <PaginationInfo pagination={mediumPagination} itemName="monsters" />
              </div>
              <div style={{ 
                padding: '12px', 
                background: 'var(--color-surface-secondary)', 
                borderRadius: 'var(--radius-sm)' 
              }}>
                <PaginationInfo pagination={smallPagination} itemName="party members" />
              </div>
            </div>
          </div>

          {/* PageJumper */}
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>
              PageJumper - Direct Page Navigation
            </h4>
            <div style={{ 
              padding: '16px', 
              background: 'var(--color-surface-secondary)', 
              borderRadius: 'var(--radius-sm)',
              display: 'flex',
              justifyContent: 'center'
            }}>
              <PageJumper pagination={largePagination} />
            </div>
          </div>

          {/* ItemsPerPageSelector */}
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>
              ItemsPerPageSelector - Change Page Size
            </h4>
            <div style={{ 
              padding: '16px', 
              background: 'var(--color-surface-secondary)', 
              borderRadius: 'var(--radius-sm)',
              display: 'flex',
              justifyContent: 'center'
            }}>
              <ItemsPerPageSelector
                value={25}
                onChange={(newValue) => console.log('Items per page changed to:', newValue)}
                options={[5, 10, 25, 50, 100]}
                itemName="results"
              />
            </div>
          </div>

          {/* PaginationPrimitive */}
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>
              PaginationPrimitive - Core Navigation Controls
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ 
                padding: '16px', 
                background: 'var(--color-surface-secondary)', 
                borderRadius: 'var(--radius-sm)',
                display: 'flex',
                justifyContent: 'center'
              }}>
                <PaginationPrimitive
                  pagination={mediumPagination}
                  showFirstLast={true}
                  showPrevNext={true}
                />
              </div>
              <div style={{ 
                padding: '16px', 
                background: 'var(--color-surface-secondary)', 
                borderRadius: 'var(--radius-sm)',
                display: 'flex',
                justifyContent: 'center'
              }}>
                <PaginationPrimitive
                  pagination={mediumPagination}
                  showFirstLast={false}
                  showPrevNext={true}
                />
              </div>
            </div>
          </div>
        </div>
      </CardSection>

      {/* Interactive Builder */}
      <CardSection type="content" title="Interactive Pagination Builder">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Builder Result */}
          <div style={{ 
            padding: '24px', 
            background: 'var(--color-surface-secondary)', 
            borderRadius: 'var(--radius-md)',
            border: '2px dashed var(--color-text-muted)'
          }}>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)', textAlign: 'center' }}>
              Your Pagination
            </h4>
            {renderBuilderPagination()}
          </div>

          {/* Builder Controls */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '16px' 
          }}>
            
            <FormField label="Layout">
              <Select
                value={builderConfig.layout}
                onChange={(e) => handleBuilderChange('layout', e.target.value)}
                options={[
                  { value: 'default', label: 'Default (Centered)' },
                  { value: 'simple', label: 'Simple (Info + Pagination)' },
                  { value: 'full', label: 'Full (Complete Controls)' }
                ]}
              />
            </FormField>

            <FormField label="Total Items">
              <Select
                value={builderConfig.total}
                onChange={(e) => handleBuilderChange('total', parseInt(e.target.value))}
                options={[
                  { value: '23', label: '23 items' },
                  { value: '150', label: '150 items' },
                  { value: '500', label: '500 items' },
                  { value: '1247', label: '1,247 items' },
                  { value: '5000', label: '5,000 items' }
                ]}
              />
            </FormField>

            <FormField label="Items Per Page">
              <Select
                value={builderConfig.limit}
                onChange={(e) => handleBuilderChange('limit', parseInt(e.target.value))}
                options={[
                  { value: '5', label: '5 per page' },
                  { value: '10', label: '10 per page' },
                  { value: '12', label: '12 per page' },
                  { value: '25', label: '25 per page' },
                  { value: '50', label: '50 per page' }
                ]}
              />
            </FormField>

            <FormField label="Current Page">
              <Select
                value={builderConfig.currentPage}
                onChange={(e) => handleBuilderChange('currentPage', parseInt(e.target.value))}
                options={(() => {
                  const totalPages = Math.ceil(builderConfig.total / builderConfig.limit);
                  const options = [];
                  for (let i = 1; i <= Math.min(totalPages, 20); i++) {
                    options.push({ value: i.toString(), label: `Page ${i}` });
                  }
                  return options;
                })()}
              />
            </FormField>

            <FormField label="Item Name">
              <Select
                value={builderConfig.itemName}
                onChange={(e) => handleBuilderChange('itemName', e.target.value)}
                options={[
                  { value: 'items', label: 'items' },
                  { value: 'monsters', label: 'monsters' },
                  { value: 'results', label: 'results' },
                  { value: 'records', label: 'records' },
                  { value: 'entries', label: 'entries' }
                ]}
              />
            </FormField>

            {builderConfig.layout === 'default' && (
              <FormField label="Show Controls">
                <Select
                  value={`${builderConfig.showFirstLast ? 'firstlast' : 'nofirstlast'}-${builderConfig.showPrevNext ? 'prevnext' : 'noprevnext'}`}
                  onChange={(e) => {
                    const [firstLast, prevNext] = e.target.value.split('-');
                    handleBuilderChange('showFirstLast', firstLast === 'firstlast');
                    handleBuilderChange('showPrevNext', prevNext === 'prevnext');
                  }}
                  options={[
                    { value: 'firstlast-prevnext', label: 'All Controls' },
                    { value: 'nofirstlast-prevnext', label: 'Prev/Next Only' },
                    { value: 'firstlast-noprevnext', label: 'First/Last Only' },
                    { value: 'nofirstlast-noprevnext', label: 'Numbers Only' }
                  ]}
                />
              </FormField>
            )}
          </div>

          {/* Quick Actions */}
          <div style={{ 
            display: 'flex', 
            gap: '12px', 
            justifyContent: 'center',
            flexWrap: 'wrap'
          }}>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => builderPagination.firstPage()}
            >
              Go to First
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => builderPagination.prevPage()}
              disabled={!builderPagination.hasPrev}
            >
              Previous
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => builderPagination.nextPage()}
              disabled={!builderPagination.hasNext}
            >
              Next
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => builderPagination.lastPage()}
            >
              Go to Last
            </Button>
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
              {(() => {
                const baseCode = `// Setup pagination hook
const pagination = usePagination({
  limit: ${builderConfig.limit},
  total: ${builderConfig.total},
  initialPage: ${builderConfig.currentPage}
});

// Render pagination component
<Pagination
  layout="${builderConfig.layout}"
  pagination={pagination}
  itemName="${builderConfig.itemName}"`;

                if (builderConfig.layout === 'full') {
                  return baseCode + `
  currentLimit={${builderConfig.limit}}
  onLimitChange={handleLimitChange}
  itemsPerPageOptions={[5, 10, 25, 50]}
/>`;
                } else if (builderConfig.layout === 'default') {
                  return baseCode + `
  showFirstLast={${builderConfig.showFirstLast}}
  showPrevNext={${builderConfig.showPrevNext}}
/>`;
                } else {
                  return baseCode + `
/>`;
                }
              })()}
            </code>
          </div>

          {/* Pagination State Info */}
          <div style={{ 
            background: 'var(--color-surface-primary)', 
            padding: '16px', 
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--color-text-muted)'
          }}>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)', fontSize: '14px' }}>
              Current Pagination State:
            </h4>
            <div style={{ 
              fontFamily: 'var(--font-family-mono)', 
              fontSize: '12px',
              color: 'var(--color-text-secondary)',
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
              gap: '8px'
            }}>
              <div>Page: {builderPagination.currentPage}</div>
              <div>Total Pages: {builderPagination.totalPages}</div>
              <div>Total Items: {builderPagination.total}</div>
              <div>Items Per Page: {builderPagination.limit}</div>
              <div>Has Next: {builderPagination.hasNext ? 'Yes' : 'No'}</div>
              <div>Has Prev: {builderPagination.hasPrev ? 'Yes' : 'No'}</div>
            </div>
          </div>
        </div>
      </CardSection>
    </Card>
  );
}

export default PaginationExamples;
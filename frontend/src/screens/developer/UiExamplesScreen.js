// UiExamplesScreen - Developer showcase for all UI components
// Navigate between different component examples to see all variations and options
// Perfect for development reference and testing component configurations

import React, { useState } from 'react';
import { Card, CardSection } from '../../shared/ui/Card/index.js';
import { Button, ButtonGroup } from '../../shared/ui/Button/index.js';
import { Badge } from '../../shared/ui/Badge/index.js';
import { EmptyState } from '../../shared/ui/Feedback/index.js';
import BadgeExamples from '../../components/UiExamples/BadgeExample.js';
import TableExamples from '../../components/UiExamples/TableExample.js';
import ExpandableTableExamples from '../../components/UiExamples/ExpandableTableExample.js';
import CardExamples from '../../components/UiExamples/CardExamples.js';
import CoCaTokExamples from '../../components/UiExamples/CoCaTokExample.js';
import FeedbackExamples from '../../components/UiExamples/FeedbackExamples.js';
import ButtonExamples from '../../components/UiExamples/ButtonExample.js';
import ExplosionExamples from '../../components/UiExamples/ExplosionExamples.js';
import FilterControlsExamples from '../../components/UiExamples/FilterControlsExample.js';
import FormExamples from '../../components/UiExamples/FormExample.js';
import LoadingStatesExamples from '../../components/UiExamples/LoadingStatesExample.js';
import PaginationExamples from '../../components/UiExamples/PaginiationExample.js';

function UiExamplesScreen() {
  const [activeComponent, setActiveComponent] = useState('badges');

  // Component categories for navigation
  const componentCategories = [
    {
      id: 'badges',
      label: 'Badges',
      description: 'Labels, status indicators, and counters',
      component: BadgeExamples,
      status: 'complete'
    },
    {
      id: 'buttons',
      label: 'Buttons',
      description: 'All button types and variants',
      component: ButtonExamples, 
      status: 'complete'
    },
    {
      id: 'forms',
      label: 'Forms',
      description: 'Inputs, selects, and form controls',
      component: FormExamples, // TODO: Create FormExamples
      status: 'complete'
    },
    {
      id: 'cards',
      label: 'Cards',
      description: 'Card layouts and sections',
      component: CardExamples, 
      status: 'complete'
    },
    {
      id: 'feedback',
      label: 'Feedback',
      description: 'Alerts, empty states, and notifications',
      component: FeedbackExamples, 
      status: 'complete'
    },
    {
      id: 'filter-controls',
      label: 'Filter Controls',
      description: 'Alerts, empty states, and notifications',
      component: FilterControlsExamples, 
      status: 'complete'
    },
    {
      id: 'loading',
      label: 'Loading',
      description: 'Spinners, skeletons, and loading states',
      component: LoadingStatesExamples, // TODO: Create LoadingExamples
      status: 'complete'
    },
    {
      id: 'pagination',
      label: 'Pagination',
      description: 'Page navigation and controls',
      component: PaginationExamples, // TODO: Create PaginationExamples
      status: 'complete'
    },
    {
      id: 'tables',
      label: 'Tables',
      description: 'Data tables rows',
      component: TableExamples,
      status: 'complete'
    },
    {
      id: 'expandable-tables',
      label: 'Expandable Tables',
      description: 'Data tables with expandable rows',
      component: ExpandableTableExamples,
      status: 'complete'
    },
    {
      id: 'explosions',
      label: 'Explosions',
      description: 'Visual effects and animations',
      component: ExplosionExamples,
      status: 'complete'
    },
    {
      id: 'cocatoks',
      label: 'CoCaToks',
      description: 'Collectible card tokens',
      component: CoCaTokExamples, 
      status: 'complete'
    }
  ];

  // Get current component
  const currentCategory = componentCategories.find(cat => cat.id === activeComponent);
  const CurrentComponent = currentCategory?.component;

  // Render component showcase or placeholder
  const renderComponentShowcase = () => {
    if (CurrentComponent) {
      return <CurrentComponent />;
    }

    // Placeholder for components that don't have examples yet
    return (
      <Card size="lg" padding="lg">
        <CardSection type="header" title={`${currentCategory.label} Examples`} />
        <CardSection type="content">
          <EmptyState
            icon="🚧"
            title="Component Examples Coming Soon"
            message={
              <div style={{ textAlign: 'center' }}>
                <p>Examples for {currentCategory.label} components are not implemented yet.</p>
                <p style={{ fontSize: '14px', color: 'var(--color-text-muted)', marginTop: '8px' }}>
                  {currentCategory.description}
                </p>
              </div>
            }
            action={
              <Button
                variant="primary"
                onClick={() => {
                  console.log(`TODO: Create ${currentCategory.label}Examples component`);
                  alert(`Create Examples.js file for ${currentCategory.label} components`);
                }}
              >
                Create Examples Component
              </Button>
            }
          />
        </CardSection>
      </Card>
    );
  };

  return (
    <div className="ui-examples-screen" style={{ 
      padding: '24px',
      maxWidth: '1200px',
      margin: '0 auto'
    }}>
      {/* Header */}
      <Card size="lg" padding="md" style={{ marginBottom: '24px' }}>
        <CardSection type="header" title="UI Component Showcase" />
        <CardSection type="content">
          <p style={{ color: 'var(--color-text-secondary)', margin: 0 }}>
            Developer reference for all UI components. Navigate between components to see examples, 
            variations, and interactive builders for testing different configurations.
          </p>
        </CardSection>
      </Card>

      {/* Component Navigation */}
      <Card size="lg" padding="md" style={{ marginBottom: '24px' }}>
        <CardSection type="header" title="Components" />
        <CardSection type="content">
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
            gap: '12px' 
          }}>
            {componentCategories.map(category => (
              <div
                key={category.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '12px'
                }}
              >
                <Button
                  variant={activeComponent === category.id ? 'secondary' : 'primary'}
                  size="sm"
                  onClick={() => setActiveComponent(category.id)}
                  style={{ flex: 1, justifyContent: 'flex-start' }}
                >
                  {category.label}
                </Button>
                
                <Badge
                  variant={category.status === 'complete' ? 'success' : 'warning'}
                  size="sm"
                >
                  {category.status === 'complete' ? 'Ready' : 'TODO'}
                </Badge>
              </div>
            ))}
          </div>
          
          {/* Quick stats */}
          <div style={{ 
            marginTop: '16px', 
            padding: '12px', 
            background: 'var(--color-surface-secondary)', 
            borderRadius: 'var(--radius-sm)',
            fontSize: '14px',
            color: 'var(--color-text-secondary)'
          }}>
            <strong>{componentCategories.filter(c => c.status === 'complete').length}</strong> of{' '}
            <strong>{componentCategories.length}</strong> component showcases completed
          </div>
        </CardSection>
      </Card>

      {/* Current Component Showcase */}
      <div className="component-showcase">
        {renderComponentShowcase()}
      </div>

      {/* Development Notes */}
      <Card size="lg" padding="md" style={{ marginTop: '24px' }}>
        <CardSection type="header" title="Development Notes" />
        <CardSection type="content">
          <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)' }}>
            <h4 style={{ margin: '0 0 8px 0', color: 'var(--color-text-primary)' }}>
              To add more component examples:
            </h4>
            <ol style={{ margin: 0, paddingLeft: '20px' }}>
              <li>Create <code>Examples.js</code> files in each component folder</li>
              <li>Import the example component in this file</li>
              <li>Update the componentCategories array with the new component</li>
              <li>Set status to 'complete' when examples are ready</li>
            </ol>
            
            <h4 style={{ margin: '16px 0 8px 0', color: 'var(--color-text-primary)' }}>
              Example structure:
            </h4>
            <code style={{ 
              display: 'block',
              background: 'var(--color-surface-primary)',
              padding: '8px',
              borderRadius: 'var(--radius-sm)',
              fontFamily: 'var(--font-family-mono)',
              fontSize: '12px'
            }}>
              frontend/src/shared/ui/Button/Examples.js<br/>
              frontend/src/shared/ui/Form/Examples.js<br/>
              frontend/src/shared/ui/Card/Examples.js<br/>
              etc...
            </code>
          </div>
        </CardSection>
      </Card>
    </div>
  );
}

export default UiExamplesScreen;
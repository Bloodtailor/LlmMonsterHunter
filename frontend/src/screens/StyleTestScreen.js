import React, { useState } from 'react';
import {
  Button, IconButton, ButtonGroup,
  Badge, StatusBadge, CountBadge,
  LoadingSpinner, LoadingContainer, LoadingSkeleton,
  Alert, EmptyState,
  Card, CardSection,
  Input, Textarea, Select, SearchInput, FormField, Form,
  Pagination, PaginationInfo, PageJumper, ItemsPerPageSelector,
  BUTTON_VARIANTS, BUTTON_SIZES,
  BADGE_VARIANTS, BADGE_SIZES, STATUS_TYPES, COUNT_FORMATS,
  LOADING_SIZES, LOADING_COLORS, LOADING_TYPES,
  ALERT_TYPES, ALERT_SIZES,
  EMPTY_STATE_SIZES, EMPTY_STATE_VARIANTS, EMPTY_STATE_PRESETS,
  CARD_VARIANTS, CARD_SIZES, CARD_PADDING, CARD_BACKGROUNDS,
  CARD_SECTION_TYPES, CARD_SECTION_ALIGNMENT
} from '../shared/ui/index.js';

// Mock pagination data for testing
const mockPagination = {
  currentPage: 2,
  totalPages: 5,
  hasNext: true,
  hasPrev: true,
  isFirstPage: false,
  isLastPage: false,
  paginationInfo: {
    startItem: 11,
    endItem: 20,
    total: 45,
    pageRange: [1, 2, 3, '...', 5]
  },
  goToPage: (page) => console.log('Go to page:', page),
  nextPage: () => console.log('Next page'),
  prevPage: () => console.log('Previous page'),
  firstPage: () => console.log('First page'),
  lastPage: () => console.log('Last page')
};

function StyleTestScreen() {
  const [formValues, setFormValues] = useState({
    input: '',
    textarea: '',
    select: '',
    search: ''
  });

  const handleFormChange = (field) => (event) => {
    setFormValues(prev => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  const SectionHeader = ({ title, description }) => (
    <div style={{ marginBottom: '2rem', borderBottom: '2px solid #4a90e2', paddingBottom: '1rem' }}>
      <h2 style={{ color: '#f39c12', fontSize: '1.5rem', marginBottom: '0.5rem' }}>{title}</h2>
      {description && <p style={{ color: '#b0b0b0', fontSize: '0.9rem' }}>{description}</p>}
    </div>
  );

  const ComponentGrid = ({ children, columns = 3 }) => (
    <div style={{ 
      display: 'grid', 
      gridTemplateColumns: `repeat(auto-fit, minmax(250px, 1fr))`, 
      gap: '1.5rem',
      marginBottom: '3rem'
    }}>
      {children}
    </div>
  );

  const ComponentDemo = ({ title, children }) => (
    <Card variant="elevated" padding="md" style={{ height: 'fit-content' }}>
      <CardSection type="header" title={title} />
      <CardSection type="content">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', alignItems: 'flex-start' }}>
          {children}
        </div>
      </CardSection>
    </Card>
  );

  return (
    <div style={{ 
      padding: '2rem',
      backgroundColor: '#1a1a2e',
      minHeight: '100vh',
      fontFamily: 'Segoe UI, sans-serif'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <h1 style={{ color: '#f39c12', fontSize: '2.5rem', marginBottom: '1rem' }}>
            🎨 Style Test Screen
          </h1>
          <p style={{ color: '#e0e0e0', fontSize: '1.1rem' }}>
            Complete showcase of all UI primitives and components
          </p>
        </div>

        {/* BUTTONS SECTION */}
        <SectionHeader 
          title="🔘 Buttons" 
          description="Primary interactive elements - Button, IconButton, ButtonGroup"
        />
        
        <ComponentGrid>
          <ComponentDemo title="Button Variants">
            {Object.values(BUTTON_VARIANTS).map(variant => (
              <Button key={variant} variant={variant}>
                {variant.charAt(0).toUpperCase() + variant.slice(1)}
              </Button>
            ))}
          </ComponentDemo>

          <ComponentDemo title="Button Sizes">
            {Object.values(BUTTON_SIZES).map(size => (
              <Button key={size} variant="primary" size={size}>
                Size {size.toUpperCase()}
              </Button>
            ))}
          </ComponentDemo>

          <ComponentDemo title="Button States">
            <Button variant="primary">Normal</Button>
            <Button variant="primary" loading>Loading</Button>
            <Button variant="primary" disabled>Disabled</Button>
            <Button variant="primary" icon="🚀">With Icon</Button>
            <Button variant="primary" icon="⭐" iconPosition="right">Icon Right</Button>
          </ComponentDemo>

          <ComponentDemo title="Icon Buttons">
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              <IconButton icon="❤️" ariaLabel="Heart" />
              <IconButton icon="⭐" ariaLabel="Star" variant="secondary" />
              <IconButton icon="🔥" ariaLabel="Fire" variant="danger" />
              <IconButton icon="✅" ariaLabel="Check" variant="success" />
              <IconButton icon="⚠️" ariaLabel="Warning" variant="warning" />
            </div>
          </ComponentDemo>

          <ComponentDemo title="Button Groups">
            <ButtonGroup>
              <Button variant="secondary">First</Button>
              <Button variant="secondary">Second</Button>
              <Button variant="secondary">Third</Button>
            </ButtonGroup>
            <ButtonGroup orientation="vertical" spacing="tight">
              <Button variant="primary" size="sm">Top</Button>
              <Button variant="primary" size="sm">Middle</Button>
              <Button variant="primary" size="sm">Bottom</Button>
            </ButtonGroup>
          </ComponentDemo>
        </ComponentGrid>

        {/* BADGES SECTION */}
        <SectionHeader 
          title="🏷️ Badges" 
          description="Small informational labels - Badge, StatusBadge, CountBadge"
        />
        
        <ComponentGrid>
          <ComponentDemo title="Badge Variants">
            {Object.values(BADGE_VARIANTS).map(variant => (
              <Badge key={variant} variant={variant}>
                {variant}
              </Badge>
            ))}
          </ComponentDemo>

          <ComponentDemo title="Badge Sizes">
            {Object.values(BADGE_SIZES).map(size => (
              <Badge key={size} variant="primary" size={size}>
                {size.toUpperCase()}
              </Badge>
            ))}
          </ComponentDemo>

          <ComponentDemo title="Status Badges">
            {Object.values(STATUS_TYPES).map(status => (
              <StatusBadge key={status} status={status} />
            ))}
          </ComponentDemo>

          <ComponentDemo title="Count Badges">
            <CountBadge count={5} />
            <CountBadge count={12} max={20} format="fraction" />
            <CountBadge count={75} max={100} format="percentage" />
            <CountBadge count={0} label="Items" />
            <CountBadge count={999} icon="👥" label="Users" />
          </ComponentDemo>

          <ComponentDemo title="Badge Modifiers">
            <Badge variant="primary" pill>Pill Shape</Badge>
            <Badge variant="secondary" outlined>Outlined</Badge>
            <Badge variant="success" removable onRemove={() => {}}>Removable</Badge>
            <Badge variant="info" onClick={() => {}}>Clickable</Badge>
          </ComponentDemo>
        </ComponentGrid>

        {/* LOADING SECTION */}
        <SectionHeader 
          title="⏳ Loading States" 
          description="Loading indicators - LoadingSpinner, LoadingContainer, LoadingSkeleton"
        />
        
        <ComponentGrid>
          <ComponentDemo title="Loading Spinner Types">
            {Object.values(LOADING_TYPES).map(type => (
              <div key={type} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <LoadingSpinner type={type} size="md" />
                <span>{type}</span>
              </div>
            ))}
          </ComponentDemo>

          <ComponentDemo title="Loading Spinner Sizes">
            {Object.values(LOADING_SIZES).map(size => (
              <div key={size} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <LoadingSpinner size={size} />
                <span>{size}</span>
              </div>
            ))}
          </ComponentDemo>

          <ComponentDemo title="Loading Container">
            <LoadingContainer message="Loading data..." />
          </ComponentDemo>

          <ComponentDemo title="Loading Skeleton">
            <LoadingSkeleton type="text" count={3} />
            <div style={{ marginTop: '1rem' }}>
              <LoadingSkeleton type="monsterCard" />
            </div>
          </ComponentDemo>
        </ComponentGrid>

        {/* FEEDBACK SECTION */}
        <SectionHeader 
          title="💬 Feedback" 
          description="User feedback components - Alert, EmptyState"
        />
        
        <ComponentGrid columns={2}>
          <ComponentDemo title="Alert Types">
            {Object.values(ALERT_TYPES).map(type => (
              <Alert 
                key={type} 
                type={type} 
                title={`${type.charAt(0).toUpperCase() + type.slice(1)} Alert`}
              >
                This is a {type} alert message.
              </Alert>
            ))}
          </ComponentDemo>

          <ComponentDemo title="Alert Variations">
            <Alert type="info" size="sm" title="Small Alert">Small size alert</Alert>
            <Alert type="warning" outlined title="Outlined Alert">Outlined style</Alert>
            <Alert 
              type="error" 
              closeable 
              onClose={() => {}}
              action={<Button size="sm" variant="ghost">Retry</Button>}
            >
              Alert with close button and action
            </Alert>
          </ComponentDemo>

          <ComponentDemo title="Empty States">
            <EmptyState 
              icon="📋" 
              title="No Data" 
              message="Nothing to display here"
              size="sm"
            />
            <EmptyState 
              {...EMPTY_STATE_PRESETS.NO_SEARCH_RESULTS}
              action={<Button variant="primary" size="sm">Clear Filters</Button>}
            />
          </ComponentDemo>
        </ComponentGrid>

        {/* CARDS SECTION */}
        <SectionHeader 
          title="🃏 Cards" 
          description="Content containers - Card, CardSection"
        />
        
        <ComponentGrid>
          <ComponentDemo title="Card Variants">
            {Object.values(CARD_VARIANTS).map(variant => (
              <Card key={variant} variant={variant} padding="md" style={{ minHeight: '100px' }}>
                <p>{variant.charAt(0).toUpperCase() + variant.slice(1)} Card</p>
              </Card>
            ))}
          </ComponentDemo>

          <ComponentDemo title="Card with Sections">
            <Card variant="elevated" padding="none">
              <CardSection type="header" title="Card Header" />
              <CardSection type="content" padding="md">
                <p>This is the main content area of the card.</p>
              </CardSection>
              <CardSection type="footer" padding="md">
                <Button variant="primary" size="sm">Action</Button>
              </CardSection>
            </Card>
          </ComponentDemo>

          <ComponentDemo title="Interactive Card">
            <Card 
              variant="outlined" 
              interactive 
              onClick={() => alert('Card clicked!')}
              padding="md"
            >
              <p>Click me! I'm interactive.</p>
            </Card>
          </ComponentDemo>
        </ComponentGrid>

        {/* FORM SECTION */}
        <SectionHeader 
          title="📝 Form Components" 
          description="Input elements - Input, Textarea, Select, SearchInput, FormField"
        />
        
        <ComponentGrid>
          <ComponentDemo title="Basic Inputs">
            <FormField label="Text Input">
              <Input 
                value={formValues.input}
                onChange={handleFormChange('input')}
                placeholder="Enter text..."
              />
            </FormField>
            
            <FormField label="Textarea">
              <Textarea 
                value={formValues.textarea}
                onChange={handleFormChange('textarea')}
                placeholder="Enter description..."
                rows={3}
              />
            </FormField>
          </ComponentDemo>

          <ComponentDemo title="Select & Search">
            <FormField label="Select Option">
              <Select 
                value={formValues.select}
                onChange={handleFormChange('select')}
                options={[
                  { value: 'option1', label: '🔥 Fire', icon: '🔥' },
                  { value: 'option2', label: '💧 Water', icon: '💧' },
                  { value: 'option3', label: '🌍 Earth', icon: '🌍' }
                ]}
                placeholder="Choose element..."
              />
            </FormField>
            
            <FormField label="Search">
              <SearchInput 
                value={formValues.search}
                onChange={handleFormChange('search')}
                placeholder="Search monsters..."
              />
            </FormField>
          </ComponentDemo>

          <ComponentDemo title="Input States">
            <Input placeholder="Normal input" />
            <Input placeholder="Disabled input" disabled />
            <Input placeholder="Error input" error="This field is required" />
          </ComponentDemo>
        </ComponentGrid>

        {/* PAGINATION SECTION */}
        <SectionHeader 
          title="📄 Pagination" 
          description="Navigation components - Pagination controls and info"
        />
        
        <ComponentGrid columns={1}>
          <ComponentDemo title="Pagination Controls">
            <div style={{ display: 'flex', justifyContent: 'center', width: '100%' }}>
              <Pagination pagination={mockPagination} />
            </div>
          </ComponentDemo>

          <ComponentDemo title="Pagination Info & Jumper">
            <div style={{ display: 'flex', justify: 'space-between', alignItems: 'center', width: '100%', gap: '2rem' }}>
              <PaginationInfo pagination={mockPagination} itemName="monsters" />
              <PageJumper pagination={mockPagination} />
            </div>
          </ComponentDemo>

          <ComponentDemo title="Items Per Page Selector">
            <ItemsPerPageSelector 
              value={10}
              onChange={(value) => console.log('Items per page:', value)}
              itemName="monsters"
            />
          </ComponentDemo>
        </ComponentGrid>

        {/* TESTING SECTION */}
        <SectionHeader 
          title="🧪 Interactive Tests" 
          description="Test component interactions and state changes"
        />
        
        <ComponentGrid>
          <ComponentDemo title="Form Layout">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <FormField label="Monster Name">
                <Input placeholder="Enter monster name..." />
              </FormField>
              <FormField label="Element">
                <Select 
                  options={['Fire', 'Water', 'Earth', 'Air']}
                  placeholder="Choose element..."
                />
              </FormField>
              <Button variant="success" onClick={() => alert('Form submitted!')}>
                Create Monster
              </Button>
            </div>
          </ComponentDemo>

          <ComponentDemo title="State Toggles">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <StatusBadge status="ready" />
              <StatusBadge status="loading" />
              <StatusBadge status="success" />
              <StatusBadge status="error" />
            </div>
          </ComponentDemo>

          <ComponentDemo title="Count Examples">
            <CountBadge count={3} max={6} label="Party" />
            <CountBadge count={15} max={50} format="fraction" label="Inventory" />
            <CountBadge count={80} max={100} format="percentage" warningThreshold="75%" />
          </ComponentDemo>
        </ComponentGrid>

        {/* Footer */}
        <div style={{ 
          textAlign: 'center', 
          marginTop: '4rem', 
          padding: '2rem',
          borderTop: '1px solid #4a90e2',
          color: '#b0b0b0'
        }}>
          <p>🎉 All UI primitives and components displayed successfully!</p>
          <p style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>
            This style guide shows every variation of our design system components.
          </p>
        </div>

      </div>
    </div>
  );
}

export default StyleTestScreen;
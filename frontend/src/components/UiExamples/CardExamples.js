// Card Examples Component - Showcase all Card component variations
// Interactive examples and builder for Card, CardSection, and related components
// Perfect for development reference and testing different card configurations

import React, { useState } from 'react';
import { 
  Card, 
  CardSection,
  CARD_VARIANTS,
  CARD_PADDING,
  CARD_BACKGROUNDS,
  CARD_SECTION_TYPES,
  CARD_SECTION_ALIGNMENT,
  EmptyPartySlot
} from '../../shared/ui/Card/index.js';
import { Button, IconButton, ButtonGroup } from '../../shared/ui/Button/index.js';
import { Badge, StatusBadge } from '../../shared/ui/Badge/index.js';
import { Select, FormField } from '../../shared/ui/Form/index.js';

function CardExamples() {
  // Interactive builder state
  const [cardBuilder, setCardBuilder] = useState({
    variant: 'default',
    size: 'md',
    padding: 'md',
    background: 'default',
    fullWidth: false,
    interactive: false,
    disabled: false,
    // Section configuration
    hasHeader: true,
    hasContent: true,
    hasFooter: true,
    headerTitle: 'Card Header',
    contentTitle: 'Content Section',
    alignment: 'left'
  });

  const handleBuilderChange = (field, value) => {
    setCardBuilder(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const renderBuilderCard = () => {
    const cardProps = {
      variant: cardBuilder.variant,
      size: cardBuilder.size,
      padding: cardBuilder.padding,
      background: cardBuilder.background,
      fullWidth: cardBuilder.fullWidth,
      interactive: cardBuilder.interactive,
      disabled: cardBuilder.disabled,
      onClick: cardBuilder.interactive ? () => alert('Card clicked!') : undefined,
      className: 'builder-card'
    };

    return (
      <Card {...cardProps}>
        {cardBuilder.hasHeader && (
          <CardSection 
            type="header" 
            title={cardBuilder.headerTitle}
            action={<Button size="sm" variant="ghost">Action</Button>}
            alignment={cardBuilder.alignment}
          />
        )}
        
        {cardBuilder.hasContent && (
          <CardSection 
            type="content" 
            title={cardBuilder.contentTitle || null}
            alignment={cardBuilder.alignment}
          >
            <p style={{ margin: 0, color: 'var(--color-text-secondary)' }}>
              This is the card content area. It can contain any React elements, 
              text, components, or complex layouts. The content automatically 
              adapts to the card's size and padding settings.
            </p>
          </CardSection>
        )}
        
        {cardBuilder.hasFooter && (
          <CardSection 
            type="footer" 
            alignment={cardBuilder.alignment}
          >
            <ButtonGroup spacing="tight" alignment={cardBuilder.alignment}>
              <Button size="sm" variant="primary">Primary</Button>
              <Button size="sm" variant="secondary">Secondary</Button>
            </ButtonGroup>
          </CardSection>
        )}
      </Card>
    );
  };

  return (
    <Card size="lg" padding="lg" className="card-examples">
      <CardSection type="header" title="Card Components Showcase" />
      
      {/* Basic Card Examples */}
      <CardSection type="content" title="Basic Cards">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Card Variants */}
          <div>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>Card Variants</h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              {Object.values(CARD_VARIANTS).map(variant => (
                <Card key={variant} variant={variant} padding="md">
                  <CardSection type="content" alignment="center">
                    <h5 style={{ margin: '0 0 8px 0', color: 'var(--color-text-primary)' }}>
                      {variant.charAt(0).toUpperCase() + variant.slice(1)}
                    </h5>
                    <p style={{ margin: 0, fontSize: '14px', color: 'var(--color-text-secondary)' }}>
                      {variant} card variant
                    </p>
                  </CardSection>
                </Card>
              ))}
            </div>
          </div>

          {/* Card Sizes */}
          <div>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>Card Sizes</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {['sm', 'md', 'lg', 'xl'].map(size => (
                <Card key={size} size={size} variant="outlined" padding="sm">
                  <CardSection type="content" alignment="center">
                    <Badge variant="primary" size="sm">{size.toUpperCase()}</Badge>
                    <p style={{ margin: '8px 0 0 0', fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                      Size {size} card
                    </p>
                  </CardSection>
                </Card>
              ))}
            </div>
          </div>

          {/* Card Backgrounds */}
          <div>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>Card Backgrounds</h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
              {Object.values(CARD_BACKGROUNDS).map(background => (
                <Card key={background} background={background} padding="md" variant="outlined">
                  <CardSection type="content" alignment="center">
                    <Badge variant="secondary" size="sm">{background}</Badge>
                  </CardSection>
                </Card>
              ))}
            </div>
          </div>

          {/* Interactive Cards */}
          <div>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>Interactive Cards</h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <Card 
                interactive 
                onClick={() => alert('Interactive card clicked!')}
                padding="md"
              >
                <CardSection type="content" alignment="center">
                  <h5 style={{ margin: '0 0 8px 0', color: 'var(--color-text-primary)' }}>
                    Clickable Card
                  </h5>
                  <p style={{ margin: 0, fontSize: '14px', color: 'var(--color-text-secondary)' }}>
                    Click me! 👆
                  </p>
                </CardSection>
              </Card>

              <Card disabled padding="md">
                <CardSection type="content" alignment="center">
                  <h5 style={{ margin: '0 0 8px 0', color: 'var(--color-text-primary)' }}>
                    Disabled Card
                  </h5>
                  <p style={{ margin: 0, fontSize: '14px', color: 'var(--color-text-secondary)' }}>
                    Cannot interact
                  </p>
                </CardSection>
              </Card>
            </div>
          </div>
        </div>
      </CardSection>

      {/* CardSection Examples */}
      <CardSection type="content" title="Card Sections">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Section Types */}
          <div>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>Section Types</h4>
            <Card variant="outlined" padding="none">
              <CardSection type="header" title="Header Section" action={
                <StatusBadge status="success" size="sm">Active</StatusBadge>
              } />
              
              <CardSection type="content" title="Content Section">
                <p style={{ margin: 0, color: 'var(--color-text-secondary)' }}>
                  This is a content section with a title. Content sections can have optional titles 
                  and contain any React elements or components.
                </p>
              </CardSection>
              
              <CardSection type="content">
                <p style={{ margin: 0, color: 'var(--color-text-secondary)' }}>
                  This is a content section without a title. Multiple content sections 
                  can be used to organize information within a card.
                </p>
              </CardSection>
              
              <CardSection type="footer">
                <ButtonGroup spacing="tight">
                  <Button size="sm" variant="primary">Save</Button>
                  <Button size="sm" variant="ghost">Cancel</Button>
                </ButtonGroup>
              </CardSection>
            </Card>
          </div>

          {/* Section Alignment */}
          <div>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>Section Alignment</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {Object.values(CARD_SECTION_ALIGNMENT).map(alignment => (
                <Card key={alignment} variant="outlined" padding="sm">
                  <CardSection type="content" alignment={alignment}>
                    <Badge variant="primary" size="sm">
                      {alignment.charAt(0).toUpperCase() + alignment.slice(1)} Aligned
                    </Badge>
                  </CardSection>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </CardSection>

      {/* Placeholder Cards */}
      <CardSection type="content" title="Placeholder Cards">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Empty Party Slots</h4>
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            {['sm', 'md', 'lg'].map(size => (
              <EmptyPartySlot key={size} size={size}>
                <div style={{ 
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  height: '100%',
                  color: 'var(--color-text-muted)',
                  textAlign: 'center',
                  padding: '16px'
                }}>
                  <div style={{ fontSize: '24px', marginBottom: '8px' }}>➕</div>
                  <div style={{ fontSize: '12px' }}>Add Monster</div>
                  <div style={{ fontSize: '10px', marginTop: '4px' }}>Size: {size}</div>
                </div>
              </EmptyPartySlot>
            ))}
          </div>
        </div>
      </CardSection>

      {/* Complex Card Example */}
      <CardSection type="content" title="Complex Card Example">
        <Card variant="elevated" padding="none">
          <CardSection 
            type="header" 
            title="Monster Profile" 
            action={
              <ButtonGroup spacing="tight">
                <IconButton icon="⚙️" size="sm" ariaLabel="Settings" />
                <IconButton icon="❤️" size="sm" ariaLabel="Favorite" />
              </ButtonGroup>
            }
          />
          
          <CardSection type="content">
            <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
              <div style={{ 
                width: '80px', 
                height: '80px', 
                background: 'var(--color-surface-secondary)', 
                borderRadius: 'var(--radius-md)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '32px'
              }}>
                🐲
              </div>
              
              <div style={{ flex: 1 }}>
                <h4 style={{ margin: '0 0 8px 0', color: 'var(--color-text-primary)' }}>
                  Fire Drake
                </h4>
                <p style={{ margin: '0 0 12px 0', color: 'var(--color-text-secondary)', fontSize: '14px' }}>
                  A mighty dragon with flames that can melt steel. Known for its fierce loyalty 
                  and protective nature when bonded with a trainer.
                </p>
                
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  <Badge variant="error" size="sm">Fire</Badge>
                  <Badge variant="warning" size="sm">Flying</Badge>
                  <StatusBadge status="ready" size="sm" />
                </div>
              </div>
            </div>
          </CardSection>
          
          <CardSection type="footer">
            <ButtonGroup spacing="normal" alignment="end">
              <Button size="sm" variant="ghost">View Details</Button>
              <Button size="sm" variant="primary">Add to Party</Button>
            </ButtonGroup>
          </CardSection>
        </Card>
      </CardSection>

      {/* Interactive Builder */}
      <CardSection type="content" title="Interactive Card Builder">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Builder Result */}
          <div style={{ 
            padding: '24px', 
            background: 'var(--color-surface-secondary)', 
            borderRadius: 'var(--radius-md)',
            border: '2px dashed var(--color-text-muted)'
          }}>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)', textAlign: 'center' }}>
              Your Card
            </h4>
            <div style={{ maxWidth: '400px', margin: '0 auto' }}>
              {renderBuilderCard()}
            </div>
          </div>

          {/* Builder Controls */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '16px' 
          }}>
            
            <FormField label="Variant">
              <Select
                value={cardBuilder.variant}
                onChange={(e) => handleBuilderChange('variant', e.target.value)}
                options={Object.values(CARD_VARIANTS).map(variant => ({
                  value: variant,
                  label: variant.charAt(0).toUpperCase() + variant.slice(1)
                }))}
              />
            </FormField>

            <FormField label="Size">
              <Select
                value={cardBuilder.size}
                onChange={(e) => handleBuilderChange('size', e.target.value)}
                options={['sm', 'md', 'lg', 'xl'].map(size => ({
                  value: size,
                  label: size.toUpperCase()
                }))}
              />
            </FormField>

            <FormField label="Padding">
              <Select
                value={cardBuilder.padding}
                onChange={(e) => handleBuilderChange('padding', e.target.value)}
                options={Object.values(CARD_PADDING).map(padding => ({
                  value: padding,
                  label: padding.charAt(0).toUpperCase() + padding.slice(1)
                }))}
              />
            </FormField>

            <FormField label="Background">
              <Select
                value={cardBuilder.background}
                onChange={(e) => handleBuilderChange('background', e.target.value)}
                options={Object.values(CARD_BACKGROUNDS).map(bg => ({
                  value: bg,
                  label: bg.charAt(0).toUpperCase() + bg.slice(1)
                }))}
              />
            </FormField>

            <FormField label="Width">
              <Select
                value={cardBuilder.fullWidth ? 'full' : 'constrained'}
                onChange={(e) => handleBuilderChange('fullWidth', e.target.value === 'full')}
                options={[
                  { value: 'constrained', label: 'Constrained' },
                  { value: 'full', label: 'Full Width' }
                ]}
              />
            </FormField>

            <FormField label="Behavior">
              <Select
                value={`${cardBuilder.interactive ? 'interactive' : 'static'}-${cardBuilder.disabled ? 'disabled' : 'enabled'}`}
                onChange={(e) => {
                  const [behavior, state] = e.target.value.split('-');
                  handleBuilderChange('interactive', behavior === 'interactive');
                  handleBuilderChange('disabled', state === 'disabled');
                }}
                options={[
                  { value: 'static-enabled', label: 'Static' },
                  { value: 'interactive-enabled', label: 'Interactive' },
                  { value: 'static-disabled', label: 'Disabled' },
                  { value: 'interactive-disabled', label: 'Interactive + Disabled' }
                ]}
              />
            </FormField>

            <FormField label="Header Section">
              <Select
                value={cardBuilder.hasHeader ? 'true' : 'false'}
                onChange={(e) => handleBuilderChange('hasHeader', e.target.value === 'true')}
                options={[
                  { value: 'true', label: 'Show Header' },
                  { value: 'false', label: 'Hide Header' }
                ]}
              />
            </FormField>

            <FormField label="Content Title">
              <Select
                value={cardBuilder.contentTitle ? 'true' : 'false'}
                onChange={(e) => handleBuilderChange('contentTitle', e.target.value === 'true' ? 'Content Section' : '')}
                options={[
                  { value: 'false', label: 'No Title' },
                  { value: 'true', label: 'With Title' }
                ]}
              />
            </FormField>

            <FormField label="Footer Section">
              <Select
                value={cardBuilder.hasFooter ? 'true' : 'false'}
                onChange={(e) => handleBuilderChange('hasFooter', e.target.value === 'true')}
                options={[
                  { value: 'true', label: 'Show Footer' },
                  { value: 'false', label: 'Hide Footer' }
                ]}
              />
            </FormField>

            <FormField label="Alignment">
              <Select
                value={cardBuilder.alignment}
                onChange={(e) => handleBuilderChange('alignment', e.target.value)}
                options={Object.values(CARD_SECTION_ALIGNMENT).map(alignment => ({
                  value: alignment,
                  label: alignment.charAt(0).toUpperCase() + alignment.slice(1)
                }))}
              />
            </FormField>
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
              {`<Card
  variant="${cardBuilder.variant}"
  size="${cardBuilder.size}"
  padding="${cardBuilder.padding}"
  background="${cardBuilder.background}"
  ${cardBuilder.fullWidth ? 'fullWidth' : ''}
  ${cardBuilder.interactive ? 'interactive' : ''}
  ${cardBuilder.disabled ? 'disabled' : ''}
  ${cardBuilder.interactive ? 'onClick={() => {}}' : ''}
>
  ${cardBuilder.hasHeader ? `<CardSection type="header" title="${cardBuilder.headerTitle}" />` : ''}
  <CardSection type="content"${cardBuilder.contentTitle ? ` title="${cardBuilder.contentTitle}"` : ''}>
    Your content here
  </CardSection>
  ${cardBuilder.hasFooter ? `<CardSection type="footer">
    Footer content here
  </CardSection>` : ''}
</Card>`}
            </code>
          </div>
        </div>
      </CardSection>
    </Card>
  );
}

export default CardExamples;
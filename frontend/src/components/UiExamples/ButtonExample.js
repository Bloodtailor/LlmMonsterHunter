// Button Examples Component - Showcase all Button component variations
// Interactive examples and builder for Button, IconButton, and ButtonGroup
// Perfect for development reference and testing different configurations

import React, { useState } from 'react';
import { 
  Button, 
  IconButton, 
  ButtonGroup,
  BUTTON_VARIANTS,
  BUTTON_SIZES,
  BUTTON_GROUP_ORIENTATIONS,
  BUTTON_GROUP_SPACING,
  BUTTON_GROUP_ALIGNMENT
} from '../../shared/ui/Button/index.js';
import { Card, CardSection } from '../../shared/ui/Card/index.js';
import { Select, FormField } from '../../shared/ui/Form/index.js';

function ButtonExamples() {
  // Interactive builder state
  const [buttonBuilder, setButtonBuilder] = useState({
    type: 'button', // 'button', 'icon', 'group'
    variant: 'primary',
    size: 'md',
    loading: false,
    disabled: false,
    icon: '',
    iconPosition: 'left',
    text: 'Button Text',
    // IconButton specific
    iconButtonIcon: '⚙️',
    iconButtonTitle: 'Settings',
    // ButtonGroup specific
    orientation: 'horizontal',
    spacing: 'normal',
    alignment: 'start',
    groupButtons: 3
  });

  const handleBuilderChange = (field, value) => {
    setButtonBuilder(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const renderBuilderButton = () => {
    const commonProps = {
      variant: buttonBuilder.variant,
      size: buttonBuilder.size,
      loading: buttonBuilder.loading,
      disabled: buttonBuilder.disabled
    };

    switch (buttonBuilder.type) {
      case 'icon':
        return (
          <IconButton
            icon={buttonBuilder.iconButtonIcon}
            title={buttonBuilder.iconButtonTitle}
            ariaLabel={buttonBuilder.iconButtonTitle}
            {...commonProps}
          />
        );
      
      case 'group':
        const groupButtons = Array.from({ length: buttonBuilder.groupButtons }, (_, i) => (
          <Button 
            key={i} 
            variant={buttonBuilder.variant} 
            size={buttonBuilder.size}
            disabled={buttonBuilder.disabled}
            loading={i === 0 ? buttonBuilder.loading : false} // Only first button shows loading
          >
            Button {i + 1}
          </Button>
        ));
        
        return (
          <ButtonGroup
            orientation={buttonBuilder.orientation}
            spacing={buttonBuilder.spacing}
            alignment={buttonBuilder.alignment}
          >
            {groupButtons}
          </ButtonGroup>
        );
      
      default:
        return (
          <Button
            icon={buttonBuilder.icon || null}
            iconPosition={buttonBuilder.iconPosition}
            {...commonProps}
          >
            {buttonBuilder.text}
          </Button>
        );
    }
  };

  return (
    <Card size="lg" padding="lg" className="button-examples">
      <CardSection type="header" title="Button Components Showcase" />
      
      {/* Basic Button Examples */}
      <CardSection type="content" title="Basic Buttons">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Variant Variations */}
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Variants</h4>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
              {Object.values(BUTTON_VARIANTS).map(variant => (
                <Button key={variant} variant={variant}>
                  {variant.charAt(0).toUpperCase() + variant.slice(1)}
                </Button>
              ))}
            </div>
          </div>

          {/* Size Variations */}
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Sizes</h4>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
              {Object.values(BUTTON_SIZES).map(size => (
                <Button key={size} variant="primary" size={size}>
                  {size.toUpperCase()}
                </Button>
              ))}
            </div>
          </div>

          {/* Button States */}
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>States</h4>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
              <Button variant="primary">Normal</Button>
              <Button variant="primary" loading>Loading</Button>
              <Button variant="primary" disabled>Disabled</Button>
              <Button variant="primary" onClick={() => alert('Clicked!')}>Clickable</Button>
            </div>
          </div>

          {/* Buttons with Icons */}
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>With Icons</h4>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
              <Button variant="primary" icon="➕">Add Item</Button>
              <Button variant="secondary" icon="📝" iconPosition="right">Edit</Button>
              <Button variant="danger" icon="🗑️">Delete</Button>
              <Button variant="success" icon="✅">Save</Button>
              <Button variant="warning" icon="⚠️">Warning</Button>
            </div>
          </div>
        </div>
      </CardSection>

      {/* Icon Button Examples */}
      <CardSection type="content" title="Icon Buttons">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Common Icon Buttons</h4>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
              <IconButton icon="⚙️" title="Settings" variant="primary" />
              <IconButton icon="🔍" title="Search" variant="secondary" />
              <IconButton icon="❤️" title="Favorite" variant="danger" />
              <IconButton icon="📤" title="Share" variant="success" />
              <IconButton icon="✏️" title="Edit" variant="warning" />
              <IconButton icon="❌" title="Close" variant="ghost" />
            </div>
          </div>
          
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Icon Button Sizes</h4>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
              {Object.values(BUTTON_SIZES).map(size => (
                <IconButton 
                  key={size} 
                  icon="⭐" 
                  title={`Star (${size})`}
                  variant="primary" 
                  size={size} 
                />
              ))}
            </div>
          </div>

          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Icon Button States</h4>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
              <IconButton icon="🔄" title="Normal" variant="primary" />
              <IconButton icon="🔄" title="Loading" variant="primary" loading />
              <IconButton icon="🔄" title="Disabled" variant="primary" disabled />
            </div>
          </div>
        </div>
      </CardSection>

      {/* Button Group Examples */}
      <CardSection type="content" title="Button Groups">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Orientations</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
                  Horizontal:
                </div>
                <ButtonGroup orientation="horizontal" spacing="normal">
                  <Button variant="primary">First</Button>
                  <Button variant="primary">Second</Button>
                  <Button variant="primary">Third</Button>
                </ButtonGroup>
              </div>
              
              <div>
                <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
                  Vertical:
                </div>
                <ButtonGroup orientation="vertical" spacing="normal">
                  <Button variant="secondary">Top</Button>
                  <Button variant="secondary">Middle</Button>
                  <Button variant="secondary">Bottom</Button>
                </ButtonGroup>
              </div>
            </div>
          </div>

          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Spacing Options</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {Object.values(BUTTON_GROUP_SPACING).map(spacing => (
                <div key={spacing}>
                  <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
                    {spacing.charAt(0).toUpperCase() + spacing.slice(1)}:
                  </div>
                  <ButtonGroup spacing={spacing} orientation="horizontal">
                    <Button variant="primary" size="sm">A</Button>
                    <Button variant="primary" size="sm">B</Button>
                    <Button variant="primary" size="sm">C</Button>
                  </ButtonGroup>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Alignment Options</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {Object.values(BUTTON_GROUP_ALIGNMENT).map(alignment => (
                <div key={alignment} style={{ width: '100%' }}>
                  <div style={{ fontSize: '14px', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>
                    {alignment.charAt(0).toUpperCase() + alignment.slice(1)}:
                  </div>
                  <div style={{ border: '1px dashed var(--color-text-muted)', padding: '8px', borderRadius: '4px' }}>
                    <ButtonGroup alignment={alignment} orientation="horizontal">
                      <Button variant="secondary" size="sm">Left</Button>
                      <Button variant="secondary" size="sm">Center</Button>
                      <Button variant="secondary" size="sm">Right</Button>
                    </ButtonGroup>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Mixed Button Types</h4>
            <ButtonGroup spacing="normal" orientation="horizontal">
              <Button variant="primary" icon="➕">Add</Button>
              <Button variant="secondary" icon="✏️">Edit</Button>
              <IconButton icon="🗑️" title="Delete" variant="danger" />
              <Button variant="ghost">Cancel</Button>
            </ButtonGroup>
          </div>
        </div>
      </CardSection>

      {/* Interactive Builder */}
      <CardSection type="content" title="Interactive Button Builder">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Builder Result */}
          <div style={{ 
            padding: '24px', 
            background: 'var(--color-surface-secondary)', 
            borderRadius: 'var(--radius-md)',
            border: '2px dashed var(--color-text-muted)',
            minHeight: '80px'
          }}>
            <div style={{ 
              textAlign: 'center',
              marginBottom: '16px'
            }}>
              <h4 style={{ margin: 0, color: 'var(--color-text-primary)' }}>Your Button</h4>
            </div>
            
            {/* Button Group needs full width container to show alignment */}
            {buttonBuilder.type === 'group' ? (
              <div style={{ 
                width: '100%',
                border: '1px dashed var(--color-text-muted)', 
                padding: '12px', 
                borderRadius: '4px',
                background: 'var(--color-surface-primary)'
              }}>
                {renderBuilderButton()}
              </div>
            ) : (
              <div style={{ 
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                {renderBuilderButton()}
              </div>
            )}
          </div>

          {/* Builder Controls */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '16px' 
          }}>
            
            <FormField label="Button Type">
              <Select
                value={buttonBuilder.type}
                onChange={(e) => handleBuilderChange('type', e.target.value)}
                options={[
                  { value: 'button', label: 'Basic Button' },
                  { value: 'icon', label: 'Icon Button' },
                  { value: 'group', label: 'Button Group' }
                ]}
              />
            </FormField>

            <FormField label="Variant">
              <Select
                value={buttonBuilder.variant}
                onChange={(e) => handleBuilderChange('variant', e.target.value)}
                options={Object.values(BUTTON_VARIANTS).map(variant => ({
                  value: variant,
                  label: variant.charAt(0).toUpperCase() + variant.slice(1)
                }))}
              />
            </FormField>

            <FormField label="Size">
              <Select
                value={buttonBuilder.size}
                onChange={(e) => handleBuilderChange('size', e.target.value)}
                options={Object.values(BUTTON_SIZES).map(size => ({
                  value: size,
                  label: size.toUpperCase()
                }))}
              />
            </FormField>

            <FormField label="State">
              <Select
                value={`${buttonBuilder.loading ? 'loading' : ''}${buttonBuilder.disabled ? 'disabled' : ''}` || 'normal'}
                onChange={(e) => {
                  const value = e.target.value;
                  handleBuilderChange('loading', value === 'loading');
                  handleBuilderChange('disabled', value === 'disabled');
                }}
                options={[
                  { value: 'normal', label: 'Normal' },
                  { value: 'loading', label: 'Loading' },
                  { value: 'disabled', label: 'Disabled' }
                ]}
              />
            </FormField>

            {/* Basic Button Controls */}
            {buttonBuilder.type === 'button' && (
              <>
                <FormField label="Button Text">
                  <Select
                    value={buttonBuilder.text}
                    onChange={(e) => handleBuilderChange('text', e.target.value)}
                    options={[
                      { value: 'Button Text', label: 'Button Text' },
                      { value: 'Save Changes', label: 'Save Changes' },
                      { value: 'Cancel', label: 'Cancel' },
                      { value: 'Delete Item', label: 'Delete Item' },
                      { value: 'Add New', label: 'Add New' }
                    ]}
                  />
                </FormField>

                <FormField label="Icon (optional)">
                  <Select
                    value={buttonBuilder.icon}
                    onChange={(e) => handleBuilderChange('icon', e.target.value)}
                    options={[
                      { value: '', label: 'No Icon' },
                      { value: '➕', label: '➕ Add' },
                      { value: '✏️', label: '✏️ Edit' },
                      { value: '🗑️', label: '🗑️ Delete' },
                      { value: '💾', label: '💾 Save' },
                      { value: '🔍', label: '🔍 Search' },
                      { value: '⚙️', label: '⚙️ Settings' }
                    ]}
                  />
                </FormField>

                {buttonBuilder.icon && (
                  <FormField label="Icon Position">
                    <Select
                      value={buttonBuilder.iconPosition}
                      onChange={(e) => handleBuilderChange('iconPosition', e.target.value)}
                      options={[
                        { value: 'left', label: 'Left' },
                        { value: 'right', label: 'Right' }
                      ]}
                    />
                  </FormField>
                )}
              </>
            )}

            {/* Icon Button Controls */}
            {buttonBuilder.type === 'icon' && (
              <>
                <FormField label="Icon">
                  <Select
                    value={buttonBuilder.iconButtonIcon}
                    onChange={(e) => handleBuilderChange('iconButtonIcon', e.target.value)}
                    options={[
                      { value: '⚙️', label: '⚙️ Settings' },
                      { value: '🔍', label: '🔍 Search' },
                      { value: '❤️', label: '❤️ Favorite' },
                      { value: '📤', label: '📤 Share' },
                      { value: '✏️', label: '✏️ Edit' },
                      { value: '❌', label: '❌ Close' },
                      { value: '⭐', label: '⭐ Star' },
                      { value: '🔄', label: '🔄 Refresh' }
                    ]}
                  />
                </FormField>

                <FormField label="Tooltip">
                  <Select
                    value={buttonBuilder.iconButtonTitle}
                    onChange={(e) => handleBuilderChange('iconButtonTitle', e.target.value)}
                    options={[
                      { value: 'Settings', label: 'Settings' },
                      { value: 'Search', label: 'Search' },
                      { value: 'Add to favorites', label: 'Add to favorites' },
                      { value: 'Share item', label: 'Share item' },
                      { value: 'Edit item', label: 'Edit item' },
                      { value: 'Close dialog', label: 'Close dialog' }
                    ]}
                  />
                </FormField>
              </>
            )}

            {/* Button Group Controls */}
            {buttonBuilder.type === 'group' && (
              <>
                <FormField label="Orientation">
                  <Select
                    value={buttonBuilder.orientation}
                    onChange={(e) => handleBuilderChange('orientation', e.target.value)}
                    options={Object.values(BUTTON_GROUP_ORIENTATIONS).map(orientation => ({
                      value: orientation,
                      label: orientation.charAt(0).toUpperCase() + orientation.slice(1)
                    }))}
                  />
                </FormField>

                <FormField label="Spacing">
                  <Select
                    value={buttonBuilder.spacing}
                    onChange={(e) => handleBuilderChange('spacing', e.target.value)}
                    options={Object.values(BUTTON_GROUP_SPACING).map(spacing => ({
                      value: spacing,
                      label: spacing.charAt(0).toUpperCase() + spacing.slice(1)
                    }))}
                  />
                </FormField>

                <FormField label="Alignment">
                  <Select
                    value={buttonBuilder.alignment}
                    onChange={(e) => handleBuilderChange('alignment', e.target.value)}
                    options={Object.values(BUTTON_GROUP_ALIGNMENT).map(alignment => ({
                      value: alignment,
                      label: alignment.charAt(0).toUpperCase() + alignment.slice(1)
                    }))}
                  />
                </FormField>

                <FormField label="Number of Buttons">
                  <Select
                    value={buttonBuilder.groupButtons}
                    onChange={(e) => handleBuilderChange('groupButtons', parseInt(e.target.value))}
                    options={[2, 3, 4, 5].map(num => ({
                      value: num,
                      label: num.toString()
                    }))}
                  />
                </FormField>
              </>
            )}
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
                if (buttonBuilder.type === 'icon') {
                  return `<IconButton
  icon="${buttonBuilder.iconButtonIcon}"
  variant="${buttonBuilder.variant}"
  size="${buttonBuilder.size}"
  title="${buttonBuilder.iconButtonTitle}"
  ${buttonBuilder.loading ? 'loading' : ''}
  ${buttonBuilder.disabled ? 'disabled' : ''}
/>`;
                } else if (buttonBuilder.type === 'group') {
                  return `<ButtonGroup
  orientation="${buttonBuilder.orientation}"
  spacing="${buttonBuilder.spacing}"
  alignment="${buttonBuilder.alignment}"
>
  <Button variant="${buttonBuilder.variant}" size="${buttonBuilder.size}">Button 1</Button>
  <Button variant="${buttonBuilder.variant}" size="${buttonBuilder.size}">Button 2</Button>
  <Button variant="${buttonBuilder.variant}" size="${buttonBuilder.size}">Button 3</Button>
</ButtonGroup>`;
                } else {
                  return `<Button
  variant="${buttonBuilder.variant}"
  size="${buttonBuilder.size}"
  ${buttonBuilder.icon ? `icon="${buttonBuilder.icon}"` : ''}
  ${buttonBuilder.icon && buttonBuilder.iconPosition === 'right' ? `iconPosition="right"` : ''}
  ${buttonBuilder.loading ? 'loading' : ''}
  ${buttonBuilder.disabled ? 'disabled' : ''}
>
  ${buttonBuilder.text}
</Button>`;
                }
              })()}
            </code>
          </div>
        </div>
      </CardSection>
    </Card>
  );
}

export default ButtonExamples;
// Feedback Examples Component - Showcase all Feedback component variations
// Interactive examples and builder for Alert and EmptyState components
// Perfect for development reference and testing different configurations

import React, { useState } from 'react';
import { 
  Alert, 
  EmptyState,
  ALERT_TYPES,
  ALERT_SIZES,
  EMPTY_STATE_SIZES,
  EMPTY_STATE_VARIANTS,
  EMPTY_STATE_PRESETS
} from '../../shared/ui/Feedback/index.js';
import { Card, CardSection } from '../../shared/ui/Card/index.js';
import { Select, FormField } from '../../shared/ui/Form/index.js';
import { Button } from '../../shared/ui/Button/index.js';

function FeedbackExamples() {
  // Interactive builder state
  const [feedbackBuilder, setFeedbackBuilder] = useState({
    type: 'alert', // 'alert', 'emptyState'
    // Alert specific
    alertType: 'info',
    size: 'md',
    outlined: false,
    closeable: false,
    showIcon: true,
    title: 'Alert Title',
    message: 'This is an alert message that provides feedback to the user.',
    hasAction: false,
    // EmptyState specific
    emptyVariant: 'default',
    emptySize: 'md',
    icon: '📋',
    emptyTitle: 'No Data Found',
    emptyMessage: 'There are no items to display at this time.',
    preset: 'none',
    hasEmptyAction: false,
    illustration: null
  });

  const handleBuilderChange = (field, value) => {
    setFeedbackBuilder(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const renderBuilderComponent = () => {
    if (feedbackBuilder.type === 'alert') {
      return (
        <Alert
          type={feedbackBuilder.alertType}
          size={feedbackBuilder.size}
          outlined={feedbackBuilder.outlined}
          closeable={feedbackBuilder.closeable}
          showIcon={feedbackBuilder.showIcon}
          title={feedbackBuilder.title}
          onClose={feedbackBuilder.closeable ? () => alert('Alert closed!') : undefined}
          action={feedbackBuilder.hasAction ? (
            <Button variant="primary" size="sm">Take Action</Button>
          ) : undefined}
        >
          {feedbackBuilder.message}
        </Alert>
      );
    } else {
      // Handle presets
      if (feedbackBuilder.preset !== 'none') {
        const presetConfig = EMPTY_STATE_PRESETS[feedbackBuilder.preset];
        return (
          <EmptyState
            {...presetConfig}
            size={feedbackBuilder.emptySize}
            variant={feedbackBuilder.emptyVariant}
            action={feedbackBuilder.hasEmptyAction ? (
              <Button variant="primary">Take Action</Button>
            ) : undefined}
          />
        );
      }

      return (
        <EmptyState
          icon={feedbackBuilder.icon}
          title={feedbackBuilder.emptyTitle}
          message={feedbackBuilder.emptyMessage}
          size={feedbackBuilder.emptySize}
          variant={feedbackBuilder.emptyVariant}
          illustration={feedbackBuilder.illustration}
          action={feedbackBuilder.hasEmptyAction ? (
            <Button variant="primary">Take Action</Button>
          ) : undefined}
        />
      );
    }
  };

  return (
    <Card size="lg" padding="lg" className="feedback-examples">
      <CardSection type="header" title="Feedback Components Showcase" />
      
      {/* Alert Examples */}
      <CardSection type="content" title="Alert Components">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Alert Types */}
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Alert Types</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {Object.values(ALERT_TYPES).map(type => (
                <Alert key={type} type={type} title={`${type.charAt(0).toUpperCase() + type.slice(1)} Alert`}>
                  This is a {type} alert message providing feedback to the user.
                </Alert>
              ))}
            </div>
          </div>

          {/* Alert Sizes */}
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Alert Sizes</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {Object.values(ALERT_SIZES).map(size => (
                <Alert key={size} type="info" size={size} title={`${size.toUpperCase()} Alert`}>
                  This is a {size} sized alert message.
                </Alert>
              ))}
            </div>
          </div>

          {/* Alert Variations */}
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Alert Variations</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <Alert type="success" outlined title="Outlined Alert">
                This alert uses the outlined style instead of filled background.
              </Alert>
              <Alert type="warning" closeable title="Closeable Alert" onClose={() => alert('Closed!')}>
                This alert can be closed by clicking the X button.
              </Alert>
              <Alert type="error" showIcon={false} title="No Icon Alert">
                This alert has the icon hidden.
              </Alert>
              <Alert 
                type="info" 
                title="Alert with Action"
                action={<Button variant="primary" size="sm">Learn More</Button>}
              >
                This alert includes an action button for user interaction.
              </Alert>
              <Alert type="success" icon="🎉" title="Custom Icon Alert">
                This alert uses a custom icon instead of the default.
              </Alert>
            </div>
          </div>
        </div>
      </CardSection>

      {/* EmptyState Examples */}
      <CardSection type="content" title="Empty State Components">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* EmptyState Sizes */}
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Empty State Sizes</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {Object.values(EMPTY_STATE_SIZES).map(size => (
                <EmptyState
                  key={size}
                  icon="📦"
                  title={`${size.toUpperCase()} Empty State`}
                  message={`This is a ${size} sized empty state component.`}
                  size={size}
                />
              ))}
            </div>
          </div>

          {/* EmptyState Variants */}
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Empty State Variants</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {Object.values(EMPTY_STATE_VARIANTS).map(variant => (
                <EmptyState
                  key={variant}
                  icon="🎯"
                  title={`${variant.charAt(0).toUpperCase() + variant.slice(1)} Variant`}
                  message={`This empty state uses the ${variant} visual variant.`}
                  variant={variant}
                />
              ))}
            </div>
          </div>

          {/* EmptyState Presets */}
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Common Empty State Presets</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {Object.entries(EMPTY_STATE_PRESETS).slice(0, 6).map(([presetKey, preset]) => (
                <EmptyState
                  key={presetKey}
                  {...preset}
                  action={presetKey.includes('ERROR') ? (
                    <Button variant="primary">Retry</Button>
                  ) : presetKey.includes('NO_') ? (
                    <Button variant="primary">Add {presetKey.includes('MONSTERS') ? 'Monster' : 'Item'}</Button>
                  ) : undefined}
                />
              ))}
            </div>
          </div>

          {/* EmptyState with Action */}
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Empty State with Actions</h4>
            <EmptyState
              icon="⚡"
              title="Get Started"
              message="Start building your collection by adding your first item."
              action={
                <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', justifyContent: 'center' }}>
                  <Button variant="primary">Add Item</Button>
                  <Button variant="secondary">Learn More</Button>
                </div>
              }
            />
          </div>
        </div>
      </CardSection>

      {/* Interactive Builder */}
      <CardSection type="content" title="Interactive Feedback Builder">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Builder Result */}
          <div style={{ 
            padding: '24px', 
            background: 'var(--color-surface-secondary)', 
            borderRadius: 'var(--radius-md)',
            border: '2px dashed var(--color-text-muted)',
            minHeight: '200px'
          }}>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)', textAlign: 'center' }}>
              Your {feedbackBuilder.type === 'alert' ? 'Alert' : 'Empty State'}
            </h4>
            {renderBuilderComponent()}
          </div>

          {/* Builder Controls */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '16px' 
          }}>
            
            <FormField label="Component Type">
              <Select
                value={feedbackBuilder.type}
                onChange={(e) => handleBuilderChange('type', e.target.value)}
                options={[
                  { value: 'alert', label: 'Alert' },
                  { value: 'emptyState', label: 'Empty State' }
                ]}
              />
            </FormField>

            <FormField label="Size">
              <Select
                value={feedbackBuilder.type === 'alert' ? feedbackBuilder.size : feedbackBuilder.emptySize}
                onChange={(e) => handleBuilderChange(
                  feedbackBuilder.type === 'alert' ? 'size' : 'emptySize', 
                  e.target.value
                )}
                options={Object.values(feedbackBuilder.type === 'alert' ? ALERT_SIZES : EMPTY_STATE_SIZES).map(size => ({
                  value: size,
                  label: size.toUpperCase()
                }))}
              />
            </FormField>

            {/* Alert-specific controls */}
            {feedbackBuilder.type === 'alert' && (
              <>
                <FormField label="Alert Type">
                  <Select
                    value={feedbackBuilder.alertType}
                    onChange={(e) => handleBuilderChange('alertType', e.target.value)}
                    options={Object.values(ALERT_TYPES).map(type => ({
                      value: type,
                      label: type.charAt(0).toUpperCase() + type.slice(1)
                    }))}
                  />
                </FormField>

                <FormField label="Style">
                  <Select
                    value={feedbackBuilder.outlined ? 'outlined' : 'filled'}
                    onChange={(e) => handleBuilderChange('outlined', e.target.value === 'outlined')}
                    options={[
                      { value: 'filled', label: 'Filled' },
                      { value: 'outlined', label: 'Outlined' }
                    ]}
                  />
                </FormField>

                <FormField label="Show Icon">
                  <Select
                    value={feedbackBuilder.showIcon ? 'true' : 'false'}
                    onChange={(e) => handleBuilderChange('showIcon', e.target.value === 'true')}
                    options={[
                      { value: 'true', label: 'Yes' },
                      { value: 'false', label: 'No' }
                    ]}
                  />
                </FormField>

                <FormField label="Closeable">
                  <Select
                    value={feedbackBuilder.closeable ? 'true' : 'false'}
                    onChange={(e) => handleBuilderChange('closeable', e.target.value === 'true')}
                    options={[
                      { value: 'false', label: 'No' },
                      { value: 'true', label: 'Yes' }
                    ]}
                  />
                </FormField>

                <FormField label="Has Action">
                  <Select
                    value={feedbackBuilder.hasAction ? 'true' : 'false'}
                    onChange={(e) => handleBuilderChange('hasAction', e.target.value === 'true')}
                    options={[
                      { value: 'false', label: 'No' },
                      { value: 'true', label: 'Yes' }
                    ]}
                  />
                </FormField>
              </>
            )}

            {/* EmptyState-specific controls */}
            {feedbackBuilder.type === 'emptyState' && (
              <>
                <FormField label="Preset">
                  <Select
                    value={feedbackBuilder.preset}
                    onChange={(e) => handleBuilderChange('preset', e.target.value)}
                    options={[
                      { value: 'none', label: 'Custom' },
                      ...Object.keys(EMPTY_STATE_PRESETS).map(preset => ({
                        value: preset,
                        label: preset.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase())
                      }))
                    ]}
                  />
                </FormField>

                <FormField label="Variant">
                  <Select
                    value={feedbackBuilder.emptyVariant}
                    onChange={(e) => handleBuilderChange('emptyVariant', e.target.value)}
                    options={Object.values(EMPTY_STATE_VARIANTS).map(variant => ({
                      value: variant,
                      label: variant.charAt(0).toUpperCase() + variant.slice(1)
                    }))}
                  />
                </FormField>

                {feedbackBuilder.preset === 'none' && (
                  <FormField label="Icon">
                    <Select
                      value={feedbackBuilder.icon}
                      onChange={(e) => handleBuilderChange('icon', e.target.value)}
                      options={[
                        { value: '📋', label: '📋 Clipboard' },
                        { value: '🏛️', label: '🏛️ Building' },
                        { value: '👥', label: '👥 People' },
                        { value: '🔍', label: '🔍 Search' },
                        { value: '🔌', label: '🔌 Plugin' },
                        { value: '⚠️', label: '⚠️ Warning' },
                        { value: '🎯', label: '🎯 Target' },
                        { value: '📦', label: '📦 Package' },
                        { value: '🚧', label: '🚧 Construction' }
                      ]}
                    />
                  </FormField>
                )}

                <FormField label="Has Action">
                  <Select
                    value={feedbackBuilder.hasEmptyAction ? 'true' : 'false'}
                    onChange={(e) => handleBuilderChange('hasEmptyAction', e.target.value === 'true')}
                    options={[
                      { value: 'false', label: 'No' },
                      { value: 'true', label: 'Yes' }
                    ]}
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
                if (feedbackBuilder.type === 'alert') {
                  return `<Alert
  type="${feedbackBuilder.alertType}"
  size="${feedbackBuilder.size}"
  ${feedbackBuilder.outlined ? 'outlined' : ''}
  ${feedbackBuilder.closeable ? 'closeable' : ''}
  ${!feedbackBuilder.showIcon ? 'showIcon={false}' : ''}
  title="${feedbackBuilder.title}"
  ${feedbackBuilder.hasAction ? 'action={<Button variant="primary" size="sm">Action</Button>}' : ''}
  ${feedbackBuilder.closeable ? 'onClose={() => console.log("Closed")}' : ''}
>
  ${feedbackBuilder.message}
</Alert>`;
                } else {
                  if (feedbackBuilder.preset !== 'none') {
                    return `<EmptyState
  {...EMPTY_STATE_PRESETS.${feedbackBuilder.preset}}
  size="${feedbackBuilder.emptySize}"
  variant="${feedbackBuilder.emptyVariant}"
  ${feedbackBuilder.hasEmptyAction ? 'action={<Button variant="primary">Action</Button>}' : ''}
/>`;
                  } else {
                    return `<EmptyState
  icon="${feedbackBuilder.icon}"
  title="${feedbackBuilder.emptyTitle}"
  message="${feedbackBuilder.emptyMessage}"
  size="${feedbackBuilder.emptySize}"
  variant="${feedbackBuilder.emptyVariant}"
  ${feedbackBuilder.hasEmptyAction ? 'action={<Button variant="primary">Action</Button>}' : ''}
/>`;
                  }
                }
              })()}
            </code>
          </div>
        </div>
      </CardSection>
    </Card>
  );
}

export default FeedbackExamples;
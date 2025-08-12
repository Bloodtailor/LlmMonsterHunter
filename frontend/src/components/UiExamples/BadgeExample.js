// Badge Examples Component - Showcase all Badge component variations
// Interactive examples and builder for Badge, StatusBadge, and CountBadge
// Perfect for development reference and testing different configurations

import React, { useState } from 'react';
import { 
  Badge, 
  StatusBadge, 
  CountBadge,
  BADGE_VARIANTS,
  BADGE_SIZES,
  STATUS_TYPES,
  COUNT_FORMATS
} from '../../shared/ui/Badge/index.js';
import { Card, CardSection } from '../../shared/ui/Card/index.js';
import { Select, FormField } from '../../shared/ui/Form/index.js';

function BadgeExamples() {
  // Interactive builder state
  const [badgeBuilder, setBadgeBuilder] = useState({
    type: 'badge', // 'badge', 'status', 'count'
    variant: 'primary',
    size: 'md',
    outlined: false,
    pill: false,
    removable: false,
    // Status badge specific
    status: 'success',
    showIcon: true,
    // Count badge specific
    count: 5,
    max: 10,
    format: 'simple',
    label: ''
  });

  const handleBuilderChange = (field, value) => {
    setBadgeBuilder(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const renderBuilderBadge = () => {
    const commonProps = {
      size: badgeBuilder.size,
      outlined: badgeBuilder.outlined,
      className: 'builder-badge'
    };

    switch (badgeBuilder.type) {
      case 'status':
        return (
          <StatusBadge
            status={badgeBuilder.status}
            showIcon={badgeBuilder.showIcon}
            {...commonProps}
          >
            Status Badge
          </StatusBadge>
        );
      
      case 'count':
        return (
          <CountBadge
            count={badgeBuilder.count}
            max={badgeBuilder.max || null}
            format={badgeBuilder.format}
            label={badgeBuilder.label || null}
            {...commonProps}
          />
        );
      
      default:
        return (
          <Badge
            variant={badgeBuilder.variant}
            pill={badgeBuilder.pill}
            removable={badgeBuilder.removable}
            {...commonProps}
          >
            Custom Badge
          </Badge>
        );
    }
  };

  return (
    <Card size="lg" padding="lg" className="badge-examples">
      <CardSection type="header" title="Badge Components Showcase" />
      
      {/* Basic Badge Examples */}
      <CardSection type="content" title="Basic Badges">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Size Variations */}
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Sizes</h4>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
              {Object.values(BADGE_SIZES).map(size => (
                <Badge key={size} variant="primary" size={size}>
                  {size.toUpperCase()}
                </Badge>
              ))}
            </div>
          </div>

          {/* Variant Variations */}
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Variants</h4>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
              {Object.values(BADGE_VARIANTS).map(variant => (
                <Badge key={variant} variant={variant}>
                  {variant.charAt(0).toUpperCase() + variant.slice(1)}
                </Badge>
              ))}
            </div>
          </div>

          {/* Style Modifiers */}
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Style Modifiers</h4>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
              <Badge variant="primary">Default</Badge>
              <Badge variant="primary" outlined>Outlined</Badge>
              <Badge variant="primary" pill>Pill Shape</Badge>
              <Badge variant="primary" removable onRemove={() => alert('Remove clicked!')}>
                Removable
              </Badge>
              <Badge variant="primary" onClick={() => alert('Badge clicked!')} className="badge-interactive">
                Clickable
              </Badge>
            </div>
          </div>
        </div>
      </CardSection>

      {/* Status Badge Examples */}
      <CardSection type="content" title="Status Badges">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>All Status Types</h4>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
              {Object.values(STATUS_TYPES).map(status => (
                <StatusBadge key={status} status={status}>
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </StatusBadge>
              ))}
            </div>
          </div>
          
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Status Badge Variations</h4>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
              <StatusBadge status="success" showIcon={false}>No Icon</StatusBadge>
              <StatusBadge status="error" outlined>Outlined</StatusBadge>
              <StatusBadge status="pending" size="sm">Small</StatusBadge>
              <StatusBadge status="warning" size="lg">Large</StatusBadge>
              <StatusBadge status="info" iconOverride="🔥">Custom Icon</StatusBadge>
            </div>
          </div>
        </div>
      </CardSection>

      {/* Count Badge Examples */}
      <CardSection type="content" title="Count Badges">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Count Formats</h4>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
              <CountBadge count={42} format="simple" />
              <CountBadge count={7} max={10} format="fraction" />
              <CountBadge count={8} max={10} format="percentage" />
            </div>
          </div>
          
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Count Badge States</h4>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
              <CountBadge count={0} max={5} label="Empty" />
              <CountBadge count={3} max={5} label="Partial" />
              <CountBadge count={5} max={5} label="Full" />
              <CountBadge count={4} max={5} label="Warning" warningThreshold="80%" />
              <CountBadge count={12} label="Party" showIcon icon="👥" />
            </div>
          </div>
        </div>
      </CardSection>

      {/* Interactive Builder */}
      <CardSection type="content" title="Interactive Badge Builder">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Builder Result */}
          <div style={{ 
            padding: '24px', 
            background: 'var(--color-surface-secondary)', 
            borderRadius: 'var(--radius-md)',
            textAlign: 'center',
            border: '2px dashed var(--color-text-muted)'
          }}>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>Your Badge</h4>
            {renderBuilderBadge()}
          </div>

          {/* Builder Controls */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '16px' 
          }}>
            
            <FormField label="Badge Type">
              <Select
                value={badgeBuilder.type}
                onChange={(e) => handleBuilderChange('type', e.target.value)}
                options={[
                  { value: 'badge', label: 'Basic Badge' },
                  { value: 'status', label: 'Status Badge' },
                  { value: 'count', label: 'Count Badge' }
                ]}
              />
            </FormField>

            <FormField label="Size">
              <Select
                value={badgeBuilder.size}
                onChange={(e) => handleBuilderChange('size', e.target.value)}
                options={Object.values(BADGE_SIZES).map(size => ({
                  value: size,
                  label: size.toUpperCase()
                }))}
              />
            </FormField>

            {/* Basic Badge Controls */}
            {badgeBuilder.type === 'badge' && (
              <>
                <FormField label="Variant">
                  <Select
                    value={badgeBuilder.variant}
                    onChange={(e) => handleBuilderChange('variant', e.target.value)}
                    options={Object.values(BADGE_VARIANTS).map(variant => ({
                      value: variant,
                      label: variant.charAt(0).toUpperCase() + variant.slice(1)
                    }))}
                  />
                </FormField>

                <FormField label="Style">
                  <Select
                    value={`${badgeBuilder.outlined ? 'outlined' : 'filled'}-${badgeBuilder.pill ? 'pill' : 'normal'}`}
                    onChange={(e) => {
                      const [fillStyle, shape] = e.target.value.split('-');
                      handleBuilderChange('outlined', fillStyle === 'outlined');
                      handleBuilderChange('pill', shape === 'pill');
                    }}
                    options={[
                      { value: 'filled-normal', label: 'Filled' },
                      { value: 'outlined-normal', label: 'Outlined' },
                      { value: 'filled-pill', label: 'Filled Pill' },
                      { value: 'outlined-pill', label: 'Outlined Pill' }
                    ]}
                  />
                </FormField>
              </>
            )}

            {/* Status Badge Controls */}
            {badgeBuilder.type === 'status' && (
              <>
                <FormField label="Status Type">
                  <Select
                    value={badgeBuilder.status}
                    onChange={(e) => handleBuilderChange('status', e.target.value)}
                    options={Object.values(STATUS_TYPES).map(status => ({
                      value: status,
                      label: status.charAt(0).toUpperCase() + status.slice(1)
                    }))}
                  />
                </FormField>

                <FormField label="Show Icon">
                  <Select
                    value={badgeBuilder.showIcon ? 'true' : 'false'}
                    onChange={(e) => handleBuilderChange('showIcon', e.target.value === 'true')}
                    options={[
                      { value: 'true', label: 'Yes' },
                      { value: 'false', label: 'No' }
                    ]}
                  />
                </FormField>

                <FormField label="Outlined">
                  <Select
                    value={badgeBuilder.outlined ? 'true' : 'false'}
                    onChange={(e) => handleBuilderChange('outlined', e.target.value === 'true')}
                    options={[
                      { value: 'false', label: 'Filled' },
                      { value: 'true', label: 'Outlined' }
                    ]}
                  />
                </FormField>
              </>
            )}

            {/* Count Badge Controls */}
            {badgeBuilder.type === 'count' && (
              <>
                <FormField label="Count">
                  <Select
                    value={badgeBuilder.count}
                    onChange={(e) => handleBuilderChange('count', parseInt(e.target.value))}
                    options={[0, 1, 3, 5, 8, 10, 15, 25, 99].map(num => ({
                      value: num,
                      label: num.toString()
                    }))}
                  />
                </FormField>

                <FormField label="Max (optional)">
                  <Select
                    value={badgeBuilder.max || ''}
                    onChange={(e) => handleBuilderChange('max', e.target.value ? parseInt(e.target.value) : null)}
                    options={[
                      { value: '', label: 'None' },
                      { value: '5', label: '5' },
                      { value: '10', label: '10' },
                      { value: '20', label: '20' },
                      { value: '100', label: '100' }
                    ]}
                  />
                </FormField>

                <FormField label="Format">
                  <Select
                    value={badgeBuilder.format}
                    onChange={(e) => handleBuilderChange('format', e.target.value)}
                    options={Object.values(COUNT_FORMATS).map(format => ({
                      value: format,
                      label: format.charAt(0).toUpperCase() + format.slice(1)
                    }))}
                  />
                </FormField>

                <FormField label="Label (optional)">
                  <Select
                    value={badgeBuilder.label}
                    onChange={(e) => handleBuilderChange('label', e.target.value)}
                    options={[
                      { value: '', label: 'None' },
                      { value: 'Party', label: 'Party' },
                      { value: 'Items', label: 'Items' },
                      { value: 'Score', label: 'Score' },
                      { value: 'Level', label: 'Level' }
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
                if (badgeBuilder.type === 'status') {
                  return `<StatusBadge
  status="${badgeBuilder.status}"
  size="${badgeBuilder.size}"
  ${badgeBuilder.outlined ? 'outlined' : ''}
  ${!badgeBuilder.showIcon ? 'showIcon={false}' : ''}
>
  Status Text
</StatusBadge>`;
                } else if (badgeBuilder.type === 'count') {
                  return `<CountBadge
  count={${badgeBuilder.count}}
  ${badgeBuilder.max ? `max={${badgeBuilder.max}}` : ''}
  format="${badgeBuilder.format}"
  ${badgeBuilder.label ? `label="${badgeBuilder.label}"` : ''}
  size="${badgeBuilder.size}"
  ${badgeBuilder.outlined ? 'outlined' : ''}
/>`;
                } else {
                  return `<Badge
  variant="${badgeBuilder.variant}"
  size="${badgeBuilder.size}"
  ${badgeBuilder.outlined ? 'outlined' : ''}
  ${badgeBuilder.pill ? 'pill' : ''}
  ${badgeBuilder.removable ? 'removable' : ''}
>
  Badge Text
</Badge>`;
                }
              })()}
            </code>
          </div>
        </div>
      </CardSection>
    </Card>
  );
}

export default BadgeExamples;
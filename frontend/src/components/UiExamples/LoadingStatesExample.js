// LoadingStates Examples Component - Showcase all loading component variations
// Interactive examples and builder for LoadingSpinner, LoadingContainer, and LoadingSkeleton
// Perfect for development reference and testing different loading configurations

import React, { useState } from 'react';
import { 
  LoadingSpinner, 
  LoadingContainer, 
  LoadingSkeleton,
  LOADING_SIZES,
  LOADING_COLORS,
  LOADING_TYPES
} from '../../shared/ui/LoadingStates/index.js';
import { Card, CardSection } from '../../shared/ui/Card/index.js';
import { Select, FormField } from '../../shared/ui/Form/index.js';
import { Button } from '../../shared/ui/Button/index.js';

function LoadingStatesExamples() {
  // Interactive builder state
  const [spinnerBuilder, setSpinnerBuilder] = useState({
    size: 'md',
    color: 'primary',
    type: 'spin'
  });

  const [containerBuilder, setContainerBuilder] = useState({
    message: 'Loading...',
    overlay: false,
    centered: true,
    showCancel: false
  });

  const [skeletonBuilder, setSkeletonBuilder] = useState({
    type: 'text',
    count: 1,
    animated: true
  });

  const [showContainerDemo, setShowContainerDemo] = useState(false);

  const handleSpinnerChange = (field, value) => {
    setSpinnerBuilder(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleContainerChange = (field, value) => {
    setContainerBuilder(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSkeletonChange = (field, value) => {
    setSkeletonBuilder(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <Card size="lg" padding="lg" className="loading-examples">
      <CardSection type="header" title="Loading States Components Showcase" />
      
      {/* Loading Spinner Examples */}
      <CardSection type="content" title="Loading Spinners">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Size Variations */}
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Sizes</h4>
            <div style={{ display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
              {Object.values(LOADING_SIZES).map(size => (
                <div key={size} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
                  <LoadingSpinner size={size} type="spin" color="primary" />
                  <span style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>{size}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Color Variations */}
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Colors</h4>
            <div style={{ display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
              {Object.values(LOADING_COLORS).map(color => (
                <div key={color} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
                  <LoadingSpinner size="lg" type="spin" color={color} />
                  <span style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>{color}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Animation Types */}
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Animation Types</h4>
            <div style={{ display: 'flex', gap: '24px', alignItems: 'center', flexWrap: 'wrap' }}>
              {Object.values(LOADING_TYPES).map(type => (
                <div key={type} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
                  <LoadingSpinner size="lg" type={type} color="primary" />
                  <span style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>{type}</span>
                </div>
              ))}
            </div>
          </div>

          {/* In-Context Examples */}
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>In-Context Usage</h4>
            <div style={{ display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
              <Button variant="primary" loading>
                Loading Button
              </Button>
              
              <div style={{ 
                padding: '12px', 
                background: 'var(--color-surface-secondary)', 
                borderRadius: 'var(--radius-md)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <LoadingSpinner size="sm" type="pulse" color="secondary" />
                <span style={{ fontSize: '14px' }}>Inline loading text</span>
              </div>

              <div style={{ 
                width: '200px', 
                height: '120px',
                background: 'var(--color-surface-secondary)', 
                borderRadius: 'var(--radius-md)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexDirection: 'column',
                gap: '8px'
              }}>
                <LoadingSpinner size="section" type="cardFlip" color="primary" />
                <span style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>Loading card</span>
              </div>
            </div>
          </div>
        </div>
      </CardSection>

      {/* Loading Container Examples */}
      <CardSection type="content" title="Loading Containers">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Container Variations</h4>
            <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
              
              {/* Inline Container */}
              <div style={{ 
                width: '300px', 
                height: '150px',
                border: '1px solid var(--color-text-muted)',
                borderRadius: 'var(--radius-md)',
                position: 'relative'
              }}>
                <LoadingContainer 
                  message="Loading data..." 
                  overlay={false}
                  centered={true}
                />
              </div>

              {/* Container with Cancel */}
              <div style={{ 
                width: '300px', 
                height: '150px',
                border: '1px solid var(--color-text-muted)',
                borderRadius: 'var(--radius-md)',
                position: 'relative'
              }}>
                <LoadingContainer 
                  message="Processing request..." 
                  overlay={false}
                  centered={true}
                  onCancel={() => alert('Cancelled!')}
                />
              </div>
            </div>
          </div>

          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Overlay Demo</h4>
            <Button 
              variant="primary" 
              onClick={() => {
                setShowContainerDemo(true);
                setTimeout(() => setShowContainerDemo(false), 3000);
              }}
            >
              Show 3-Second Overlay Demo
            </Button>
            
            {showContainerDemo && (
              <LoadingContainer 
                message="Demo overlay loading..." 
                overlay={true}
                centered={true}
                onCancel={() => setShowContainerDemo(false)}
              />
            )}
          </div>
        </div>
      </CardSection>

      {/* Loading Skeleton Examples */}
      <CardSection type="content" title="Loading Skeletons">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          
          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Skeleton Types</h4>
            <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
              
              {/* Text Skeleton */}
              <div style={{ width: '200px' }}>
                <h5 style={{ margin: '0 0 8px 0', fontSize: '14px' }}>Text Skeleton</h5>
                <LoadingSkeleton type="text" count={3} animated={true} />
              </div>

              {/* Monster Card Skeleton */}
              <div>
                <h5 style={{ margin: '0 0 8px 0', fontSize: '14px' }}>Monster Card Skeleton</h5>
                <LoadingSkeleton type="monsterCard" count={1} animated={true} />
              </div>
            </div>
          </div>

          <div>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)' }}>Animation States</h4>
            <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
              <div style={{ width: '200px' }}>
                <h5 style={{ margin: '0 0 8px 0', fontSize: '14px' }}>Animated</h5>
                <LoadingSkeleton type="text" count={2} animated={true} />
              </div>
              
              <div style={{ width: '200px' }}>
                <h5 style={{ margin: '0 0 8px 0', fontSize: '14px' }}>Static</h5>
                <LoadingSkeleton type="text" count={2} animated={false} />
              </div>
            </div>
          </div>
        </div>
      </CardSection>

      {/* Interactive Spinner Builder */}
      <CardSection type="content" title="Interactive Spinner Builder">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Builder Result */}
          <div style={{ 
            padding: '24px', 
            background: 'var(--color-surface-secondary)', 
            borderRadius: 'var(--radius-md)',
            textAlign: 'center',
            border: '2px dashed var(--color-text-muted)'
          }}>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>Your Spinner</h4>
            <LoadingSpinner 
              size={spinnerBuilder.size}
              color={spinnerBuilder.color}
              type={spinnerBuilder.type}
            />
          </div>

          {/* Spinner Controls */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '16px' 
          }}>
            
            <FormField label="Size">
              <Select
                value={spinnerBuilder.size}
                onChange={(e) => handleSpinnerChange('size', e.target.value)}
                options={Object.values(LOADING_SIZES).map(size => ({
                  value: size,
                  label: size.toUpperCase()
                }))}
              />
            </FormField>

            <FormField label="Color">
              <Select
                value={spinnerBuilder.color}
                onChange={(e) => handleSpinnerChange('color', e.target.value)}
                options={Object.values(LOADING_COLORS).map(color => ({
                  value: color,
                  label: color.charAt(0).toUpperCase() + color.slice(1)
                }))}
              />
            </FormField>

            <FormField label="Animation Type">
              <Select
                value={spinnerBuilder.type}
                onChange={(e) => handleSpinnerChange('type', e.target.value)}
                options={Object.values(LOADING_TYPES).map(type => ({
                  value: type,
                  label: type.charAt(0).toUpperCase() + type.slice(1).replace(/([A-Z])/g, ' $1')
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
              {`<LoadingSpinner
  size="${spinnerBuilder.size}"
  color="${spinnerBuilder.color}"
  type="${spinnerBuilder.type}"
/>`}
            </code>
          </div>
        </div>
      </CardSection>

      {/* Interactive Skeleton Builder */}
      <CardSection type="content" title="Interactive Skeleton Builder">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Builder Result */}
          <div style={{ 
            padding: '24px', 
            background: 'var(--color-surface-secondary)', 
            borderRadius: 'var(--radius-md)',
            border: '2px dashed var(--color-text-muted)'
          }}>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>Your Skeleton</h4>
            <LoadingSkeleton 
              type={skeletonBuilder.type}
              count={skeletonBuilder.count}
              animated={skeletonBuilder.animated}
            />
          </div>

          {/* Skeleton Controls */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '16px' 
          }}>
            
            <FormField label="Type">
              <Select
                value={skeletonBuilder.type}
                onChange={(e) => handleSkeletonChange('type', e.target.value)}
                options={[
                  { value: 'text', label: 'Text Lines' },
                  { value: 'monsterCard', label: 'Monster Card' }
                ]}
              />
            </FormField>

            <FormField label="Count">
              <Select
                value={skeletonBuilder.count}
                onChange={(e) => handleSkeletonChange('count', parseInt(e.target.value))}
                options={[1, 2, 3, 4, 5].map(num => ({
                  value: num,
                  label: num.toString()
                }))}
              />
            </FormField>

            <FormField label="Animated">
              <Select
                value={skeletonBuilder.animated ? 'true' : 'false'}
                onChange={(e) => handleSkeletonChange('animated', e.target.value === 'true')}
                options={[
                  { value: 'true', label: 'Yes' },
                  { value: 'false', label: 'No' }
                ]}
              />
            </FormField>
          </div>

          {/* Skeleton Code Example */}
          <div style={{ 
            background: 'var(--color-surface-primary)', 
            padding: '16px', 
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--color-text-muted)'
          }}>
            <h4 style={{ marginBottom: '12px', color: 'var(--color-text-primary)', fontSize: '14px' }}>
              Skeleton Code Example:
            </h4>
            <code style={{ 
              fontFamily: 'var(--font-family-mono)', 
              fontSize: '12px',
              color: 'var(--color-text-secondary)',
              display: 'block',
              whiteSpace: 'pre-wrap'
            }}>
              {`<LoadingSkeleton
  type="${skeletonBuilder.type}"
  count={${skeletonBuilder.count}}
  animated={${skeletonBuilder.animated}}
/>`}
            </code>
          </div>
        </div>
      </CardSection>
    </Card>
  );
}

export default LoadingStatesExamples;
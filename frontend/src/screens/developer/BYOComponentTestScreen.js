import React, { useState } from 'react';
import {
  Button, IconButton, ButtonGroup,
  Badge, StatusBadge, CountBadge,
  LoadingSpinner, LoadingContainer, LoadingSkeleton,
  Alert, EmptyState,
  Card, CardSection,
  Input, Textarea, Select, SearchInput, FormField,
  BUTTON_VARIANTS, BUTTON_SIZES,
  BADGE_VARIANTS, BADGE_SIZES, STATUS_TYPES, COUNT_FORMATS,
  LOADING_SIZES, LOADING_COLORS, LOADING_TYPES,
  ALERT_TYPES, ALERT_SIZES,
  EMPTY_STATE_SIZES, EMPTY_STATE_VARIANTS, EMPTY_STATE_PRESETS,
  CARD_VARIANTS, CARD_PADDING, CARD_BACKGROUNDS,
  CARD_SECTION_TYPES, CARD_SECTION_ALIGNMENT
} from '../../shared/ui/index.js';
import { CARD_SIZES } from '../../shared/constants/constants.js';

function BYOComponentTestScreen() {
  // Component selection state
  const [selectedComponent, setSelectedComponent] = useState('Button');
  
  // Component configuration states
  const [buttonConfig, setButtonConfig] = useState({
    variant: 'primary',
    size: 'md',
    disabled: false,
    loading: false,
    icon: '',
    iconPosition: 'left',
    children: 'Click Me'
  });

  const [badgeConfig, setBadgeConfig] = useState({
    variant: 'primary',
    size: 'md',
    pill: false,
    outlined: false,
    removable: false,
    children: 'Badge Text'
  });

  const [statusBadgeConfig, setStatusBadgeConfig] = useState({
    status: 'success',
    size: 'md',
    showIcon: true,
    outlined: false,
    children: ''
  });

  const [countBadgeConfig, setCountBadgeConfig] = useState({
    count: 5,
    max: 10,
    format: 'simple',
    size: 'md',
    label: '',
    icon: '',
    warningThreshold: ''
  });

  const [loadingSpinnerConfig, setLoadingSpinnerConfig] = useState({
    size: 'md',
    color: 'primary',
    type: 'spin'
  });

  const [alertConfig, setAlertConfig] = useState({
    type: 'info',
    size: 'md',
    outlined: false,
    closeable: false,
    showIcon: true,
    title: 'Alert Title',
    children: 'This is an alert message.'
  });

  const [emptyStateConfig, setEmptyStateConfig] = useState({
    size: 'md',
    variant: 'default',
    centered: true,
    icon: '📋',
    title: 'No Data Found',
    message: 'Nothing to display here.'
  });

  const [cardConfig, setCardConfig] = useState({
    variant: 'default',
    size: 'md',
    padding: 'md',
    background: 'default',
    interactive: false,
    children: 'Card content goes here.'
  });

  const [inputConfig, setInputConfig] = useState({
    type: 'text',
    placeholder: 'Enter text...',
    disabled: false,
    error: '',
    value: ''
  });

  // Available component types
  const componentTypes = [
    'Button', 'IconButton', 'Badge', 'StatusBadge', 'CountBadge',
    'LoadingSpinner', 'Alert', 'EmptyState', 'Card', 'Input', 'Textarea', 'Select', 'SearchInput'
  ];

  // Icon options for components
  const iconOptions = ['', '🚀', '⭐', '❤️', '🔥', '💧', '🌍', '⚡', '🎯', '🛡️', '⚔️', '🏆'];

  // Helper to update component config
  const updateConfig = (component, field, value) => {
    const setters = {
      Button: setButtonConfig,
      Badge: setBadgeConfig,
      StatusBadge: setStatusBadgeConfig,
      CountBadge: setCountBadgeConfig,
      LoadingSpinner: setLoadingSpinnerConfig,
      Alert: setAlertConfig,
      EmptyState: setEmptyStateConfig,
      Card: setCardConfig,
      Input: setInputConfig,
      Textarea: setInputConfig,
      SearchInput: setInputConfig
    };

    const configs = {
      Button: buttonConfig,
      Badge: badgeConfig,
      StatusBadge: statusBadgeConfig,
      CountBadge: countBadgeConfig,
      LoadingSpinner: loadingSpinnerConfig,
      Alert: alertConfig,
      EmptyState: emptyStateConfig,
      Card: cardConfig,
      Input: inputConfig,
      Textarea: inputConfig,
      SearchInput: inputConfig
    };

    const setter = setters[component];
    const currentConfig = configs[component];
    
    if (setter && currentConfig) {
      setter({ ...currentConfig, [field]: value });
    }
  };

  // Render component configuration controls
  const renderConfigControls = () => {
    switch (selectedComponent) {
      case 'Button':
        return (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <FormField label="Variant">
              <Select
                value={buttonConfig.variant}
                onChange={(e) => updateConfig('Button', 'variant', e.target.value)}
                options={Object.values(BUTTON_VARIANTS)}
              />
            </FormField>
            <FormField label="Size">
              <Select
                value={buttonConfig.size}
                onChange={(e) => updateConfig('Button', 'size', e.target.value)}
                options={Object.values(BUTTON_SIZES)}
              />
            </FormField>
            <FormField label="Icon">
              <Select
                value={buttonConfig.icon}
                onChange={(e) => updateConfig('Button', 'icon', e.target.value)}
                options={iconOptions.map(icon => ({ value: icon, label: icon || 'None' }))}
              />
            </FormField>
            <FormField label="Icon Position">
              <Select
                value={buttonConfig.iconPosition}
                onChange={(e) => updateConfig('Button', 'iconPosition', e.target.value)}
                options={['left', 'right']}
              />
            </FormField>
            <FormField label="Text">
              <Input
                value={buttonConfig.children}
                onChange={(e) => updateConfig('Button', 'children', e.target.value)}
                placeholder="Button text"
              />
            </FormField>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input
                  type="checkbox"
                  checked={buttonConfig.disabled}
                  onChange={(e) => updateConfig('Button', 'disabled', e.target.checked)}
                />
                Disabled
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input
                  type="checkbox"
                  checked={buttonConfig.loading}
                  onChange={(e) => updateConfig('Button', 'loading', e.target.checked)}
                />
                Loading
              </label>
            </div>
          </div>
        );

      case 'IconButton':
        return (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <FormField label="Variant">
              <Select
                value={buttonConfig.variant}
                onChange={(e) => updateConfig('Button', 'variant', e.target.value)}
                options={Object.values(BUTTON_VARIANTS)}
              />
            </FormField>
            <FormField label="Size">
              <Select
                value={buttonConfig.size}
                onChange={(e) => updateConfig('Button', 'size', e.target.value)}
                options={Object.values(BUTTON_SIZES)}
              />
            </FormField>
            <FormField label="Icon">
              <Select
                value={buttonConfig.icon || '🚀'}
                onChange={(e) => updateConfig('Button', 'icon', e.target.value)}
                options={iconOptions.filter(icon => icon).map(icon => ({ value: icon, label: icon }))}
              />
            </FormField>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <input
                type="checkbox"
                checked={buttonConfig.disabled}
                onChange={(e) => updateConfig('Button', 'disabled', e.target.checked)}
              />
              Disabled
            </label>
          </div>
        );

      case 'Badge':
        return (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <FormField label="Variant">
              <Select
                value={badgeConfig.variant}
                onChange={(e) => updateConfig('Badge', 'variant', e.target.value)}
                options={Object.values(BADGE_VARIANTS)}
              />
            </FormField>
            <FormField label="Size">
              <Select
                value={badgeConfig.size}
                onChange={(e) => updateConfig('Badge', 'size', e.target.value)}
                options={Object.values(BADGE_SIZES)}
              />
            </FormField>
            <FormField label="Text">
              <Input
                value={badgeConfig.children}
                onChange={(e) => updateConfig('Badge', 'children', e.target.value)}
                placeholder="Badge text"
              />
            </FormField>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input
                  type="checkbox"
                  checked={badgeConfig.pill}
                  onChange={(e) => updateConfig('Badge', 'pill', e.target.checked)}
                />
                Pill
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input
                  type="checkbox"
                  checked={badgeConfig.outlined}
                  onChange={(e) => updateConfig('Badge', 'outlined', e.target.checked)}
                />
                Outlined
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input
                  type="checkbox"
                  checked={badgeConfig.removable}
                  onChange={(e) => updateConfig('Badge', 'removable', e.target.checked)}
                />
                Removable
              </label>
            </div>
          </div>
        );

      case 'StatusBadge':
        return (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <FormField label="Status">
              <Select
                value={statusBadgeConfig.status}
                onChange={(e) => updateConfig('StatusBadge', 'status', e.target.value)}
                options={Object.values(STATUS_TYPES)}
              />
            </FormField>
            <FormField label="Size">
              <Select
                value={statusBadgeConfig.size}
                onChange={(e) => updateConfig('StatusBadge', 'size', e.target.value)}
                options={Object.values(BADGE_SIZES)}
              />
            </FormField>
            <FormField label="Custom Text">
              <Input
                value={statusBadgeConfig.children}
                onChange={(e) => updateConfig('StatusBadge', 'children', e.target.value)}
                placeholder="Custom status text"
              />
            </FormField>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input
                  type="checkbox"
                  checked={statusBadgeConfig.showIcon}
                  onChange={(e) => updateConfig('StatusBadge', 'showIcon', e.target.checked)}
                />
                Show Icon
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input
                  type="checkbox"
                  checked={statusBadgeConfig.outlined}
                  onChange={(e) => updateConfig('StatusBadge', 'outlined', e.target.checked)}
                />
                Outlined
              </label>
            </div>
          </div>
        );

      case 'CountBadge':
        return (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <FormField label="Count">
              <Input
                type="number"
                value={countBadgeConfig.count}
                onChange={(e) => updateConfig('CountBadge', 'count', parseInt(e.target.value) || 0)}
                placeholder="0"
              />
            </FormField>
            <FormField label="Max (optional)">
              <Input
                type="number"
                value={countBadgeConfig.max || ''}
                onChange={(e) => updateConfig('CountBadge', 'max', parseInt(e.target.value) || null)}
                placeholder="10"
              />
            </FormField>
            <FormField label="Format">
              <Select
                value={countBadgeConfig.format}
                onChange={(e) => updateConfig('CountBadge', 'format', e.target.value)}
                options={Object.values(COUNT_FORMATS)}
              />
            </FormField>
            <FormField label="Size">
              <Select
                value={countBadgeConfig.size}
                onChange={(e) => updateConfig('CountBadge', 'size', e.target.value)}
                options={Object.values(BADGE_SIZES)}
              />
            </FormField>
            <FormField label="Label">
              <Input
                value={countBadgeConfig.label}
                onChange={(e) => updateConfig('CountBadge', 'label', e.target.value)}
                placeholder="Items"
              />
            </FormField>
            <FormField label="Icon">
              <Select
                value={countBadgeConfig.icon}
                onChange={(e) => updateConfig('CountBadge', 'icon', e.target.value)}
                options={iconOptions.map(icon => ({ value: icon, label: icon || 'None' }))}
              />
            </FormField>
          </div>
        );

      case 'LoadingSpinner':
        return (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <FormField label="Type">
              <Select
                value={loadingSpinnerConfig.type}
                onChange={(e) => updateConfig('LoadingSpinner', 'type', e.target.value)}
                options={Object.values(LOADING_TYPES)}
              />
            </FormField>
            <FormField label="Size">
              <Select
                value={loadingSpinnerConfig.size}
                onChange={(e) => updateConfig('LoadingSpinner', 'size', e.target.value)}
                options={Object.values(LOADING_SIZES)}
              />
            </FormField>
            <FormField label="Color">
              <Select
                value={loadingSpinnerConfig.color}
                onChange={(e) => updateConfig('LoadingSpinner', 'color', e.target.value)}
                options={Object.values(LOADING_COLORS)}
              />
            </FormField>
          </div>
        );

      case 'Alert':
        return (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <FormField label="Type">
              <Select
                value={alertConfig.type}
                onChange={(e) => updateConfig('Alert', 'type', e.target.value)}
                options={Object.values(ALERT_TYPES)}
              />
            </FormField>
            <FormField label="Size">
              <Select
                value={alertConfig.size}
                onChange={(e) => updateConfig('Alert', 'size', e.target.value)}
                options={Object.values(ALERT_SIZES)}
              />
            </FormField>
            <FormField label="Title">
              <Input
                value={alertConfig.title}
                onChange={(e) => updateConfig('Alert', 'title', e.target.value)}
                placeholder="Alert title"
              />
            </FormField>
            <FormField label="Message">
              <Textarea
                value={alertConfig.children}
                onChange={(e) => updateConfig('Alert', 'children', e.target.value)}
                placeholder="Alert message"
                rows={2}
              />
            </FormField>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input
                  type="checkbox"
                  checked={alertConfig.outlined}
                  onChange={(e) => updateConfig('Alert', 'outlined', e.target.checked)}
                />
                Outlined
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input
                  type="checkbox"
                  checked={alertConfig.closeable}
                  onChange={(e) => updateConfig('Alert', 'closeable', e.target.checked)}
                />
                Closeable
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input
                  type="checkbox"
                  checked={alertConfig.showIcon}
                  onChange={(e) => updateConfig('Alert', 'showIcon', e.target.checked)}
                />
                Show Icon
              </label>
            </div>
          </div>
        );

      case 'EmptyState':
        return (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <FormField label="Size">
              <Select
                value={emptyStateConfig.size}
                onChange={(e) => updateConfig('EmptyState', 'size', e.target.value)}
                options={Object.values(EMPTY_STATE_SIZES)}
              />
            </FormField>
            <FormField label="Variant">
              <Select
                value={emptyStateConfig.variant}
                onChange={(e) => updateConfig('EmptyState', 'variant', e.target.value)}
                options={Object.values(EMPTY_STATE_VARIANTS)}
              />
            </FormField>
            <FormField label="Icon">
              <Select
                value={emptyStateConfig.icon}
                onChange={(e) => updateConfig('EmptyState', 'icon', e.target.value)}
                options={iconOptions.filter(icon => icon).map(icon => ({ value: icon, label: icon }))}
              />
            </FormField>
            <FormField label="Title">
              <Input
                value={emptyStateConfig.title}
                onChange={(e) => updateConfig('EmptyState', 'title', e.target.value)}
                placeholder="Empty state title"
              />
            </FormField>
            <FormField label="Message">
              <Textarea
                value={emptyStateConfig.message}
                onChange={(e) => updateConfig('EmptyState', 'message', e.target.value)}
                placeholder="Empty state message"
                rows={2}
              />
            </FormField>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <input
                type="checkbox"
                checked={emptyStateConfig.centered}
                onChange={(e) => updateConfig('EmptyState', 'centered', e.target.checked)}
              />
              Centered
            </label>
          </div>
        );

      case 'Card':
        return (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <FormField label="Variant">
              <Select
                value={cardConfig.variant}
                onChange={(e) => updateConfig('Card', 'variant', e.target.value)}
                options={Object.values(CARD_VARIANTS)}
              />
            </FormField>
            <FormField label="Size">
              <Select
                value={cardConfig.size}
                onChange={(e) => updateConfig('Card', 'size', e.target.value)}
                options={Object.values(CARD_SIZES)}
              />
            </FormField>
            <FormField label="Padding">
              <Select
                value={cardConfig.padding}
                onChange={(e) => updateConfig('Card', 'padding', e.target.value)}
                options={Object.values(CARD_PADDING)}
              />
            </FormField>
            <FormField label="Background">
              <Select
                value={cardConfig.background}
                onChange={(e) => updateConfig('Card', 'background', e.target.value)}
                options={Object.values(CARD_BACKGROUNDS)}
              />
            </FormField>
            <FormField label="Content">
              <Textarea
                value={cardConfig.children}
                onChange={(e) => updateConfig('Card', 'children', e.target.value)}
                placeholder="Card content"
                rows={3}
              />
            </FormField>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <input
                type="checkbox"
                checked={cardConfig.interactive}
                onChange={(e) => updateConfig('Card', 'interactive', e.target.checked)}
              />
              Interactive
            </label>
          </div>
        );

      case 'Input':
      case 'SearchInput':
        return (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            {selectedComponent === 'Input' && (
              <FormField label="Type">
                <Select
                  value={inputConfig.type}
                  onChange={(e) => updateConfig('Input', 'type', e.target.value)}
                  options={['text', 'email', 'password', 'number', 'tel', 'url']}
                />
              </FormField>
            )}
            <FormField label="Placeholder">
              <Input
                value={inputConfig.placeholder}
                onChange={(e) => updateConfig('Input', 'placeholder', e.target.value)}
                placeholder="Placeholder text"
              />
            </FormField>
            <FormField label="Value">
              <Input
                value={inputConfig.value}
                onChange={(e) => updateConfig('Input', 'value', e.target.value)}
                placeholder="Input value"
              />
            </FormField>
            <FormField label="Error Message">
              <Input
                value={inputConfig.error}
                onChange={(e) => updateConfig('Input', 'error', e.target.value)}
                placeholder="Error message"
              />
            </FormField>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <input
                type="checkbox"
                checked={inputConfig.disabled}
                onChange={(e) => updateConfig('Input', 'disabled', e.target.checked)}
              />
              Disabled
            </label>
          </div>
        );

      case 'Textarea':
        return (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <FormField label="Placeholder">
              <Input
                value={inputConfig.placeholder}
                onChange={(e) => updateConfig('Input', 'placeholder', e.target.value)}
                placeholder="Placeholder text"
              />
            </FormField>
            <FormField label="Value">
              <Textarea
                value={inputConfig.value}
                onChange={(e) => updateConfig('Input', 'value', e.target.value)}
                placeholder="Textarea value"
                rows={3}
              />
            </FormField>
            <FormField label="Error Message">
              <Input
                value={inputConfig.error}
                onChange={(e) => updateConfig('Input', 'error', e.target.value)}
                placeholder="Error message"
              />
            </FormField>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <input
                type="checkbox"
                checked={inputConfig.disabled}
                onChange={(e) => updateConfig('Input', 'disabled', e.target.checked)}
              />
              Disabled
            </label>
          </div>
        );

      case 'Select':
        return (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <FormField label="Placeholder">
              <Input
                value={inputConfig.placeholder}
                onChange={(e) => updateConfig('Input', 'placeholder', e.target.value)}
                placeholder="Placeholder text"
              />
            </FormField>
            <FormField label="Error Message">
              <Input
                value={inputConfig.error}
                onChange={(e) => updateConfig('Input', 'error', e.target.value)}
                placeholder="Error message"
              />
            </FormField>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <input
                type="checkbox"
                checked={inputConfig.disabled}
                onChange={(e) => updateConfig('Input', 'disabled', e.target.checked)}
              />
              Disabled
            </label>
          </div>
        );

      default:
        return <p>Select a component to configure its properties.</p>;
    }
  };

  // Render the actual component based on configuration
  const renderComponent = () => {
    switch (selectedComponent) {
      case 'Button':
        return (
          <Button
            variant={buttonConfig.variant}
            size={buttonConfig.size}
            disabled={buttonConfig.disabled}
            loading={buttonConfig.loading}
            icon={buttonConfig.icon || undefined}
            iconPosition={buttonConfig.iconPosition}
            onClick={() => alert('Button clicked!')}
          >
            {buttonConfig.children}
          </Button>
        );

      case 'IconButton':
        return (
          <IconButton
            icon={buttonConfig.icon || '🚀'}
            variant={buttonConfig.variant}
            size={buttonConfig.size}
            disabled={buttonConfig.disabled}
            ariaLabel="Test icon button"
            onClick={() => alert('Icon button clicked!')}
          />
        );

      case 'Badge':
        return (
          <Badge
            variant={badgeConfig.variant}
            size={badgeConfig.size}
            pill={badgeConfig.pill}
            outlined={badgeConfig.outlined}
            removable={badgeConfig.removable}
            onRemove={badgeConfig.removable ? () => alert('Badge removed!') : undefined}
          >
            {badgeConfig.children}
          </Badge>
        );

      case 'StatusBadge':
        return (
          <StatusBadge
            status={statusBadgeConfig.status}
            size={statusBadgeConfig.size}
            showIcon={statusBadgeConfig.showIcon}
            outlined={statusBadgeConfig.outlined}
          >
            {statusBadgeConfig.children || undefined}
          </StatusBadge>
        );

      case 'CountBadge':
        return (
          <CountBadge
            count={countBadgeConfig.count}
            max={countBadgeConfig.max || undefined}
            format={countBadgeConfig.format}
            size={countBadgeConfig.size}
            label={countBadgeConfig.label || undefined}
            icon={countBadgeConfig.icon || undefined}
            warningThreshold={countBadgeConfig.warningThreshold || undefined}
          />
        );

      case 'LoadingSpinner':
        return (
          <LoadingSpinner
            type={loadingSpinnerConfig.type}
            size={loadingSpinnerConfig.size}
            color={loadingSpinnerConfig.color}
          />
        );

      case 'Alert':
        return (
          <Alert
            type={alertConfig.type}
            size={alertConfig.size}
            title={alertConfig.title}
            outlined={alertConfig.outlined}
            closeable={alertConfig.closeable}
            showIcon={alertConfig.showIcon}
            onClose={alertConfig.closeable ? () => alert('Alert closed!') : undefined}
          >
            {alertConfig.children}
          </Alert>
        );

      case 'EmptyState':
        return (
          <EmptyState
            size={emptyStateConfig.size}
            variant={emptyStateConfig.variant}
            centered={emptyStateConfig.centered}
            icon={emptyStateConfig.icon}
            title={emptyStateConfig.title}
            message={emptyStateConfig.message}
          />
        );

      case 'Card':
        return (
          <Card
            variant={cardConfig.variant}
            size={cardConfig.size}
            padding={cardConfig.padding}
            background={cardConfig.background}
            interactive={cardConfig.interactive}
            onClick={cardConfig.interactive ? () => alert('Card clicked!') : undefined}
          >
            {cardConfig.children}
          </Card>
        );

      case 'Input':
        return (
          <Input
            type={inputConfig.type}
            placeholder={inputConfig.placeholder}
            value={inputConfig.value}
            disabled={inputConfig.disabled}
            error={inputConfig.error || undefined}
            onChange={() => {}}
          />
        );

      case 'Textarea':
        return (
          <Textarea
            placeholder={inputConfig.placeholder}
            value={inputConfig.value}
            disabled={inputConfig.disabled}
            error={inputConfig.error || undefined}
            onChange={() => {}}
            rows={4}
          />
        );

      case 'Select':
        return (
          <Select
            placeholder={inputConfig.placeholder || undefined}
            disabled={inputConfig.disabled}
            error={inputConfig.error || undefined}
            options={[
              { value: 'fire', label: '🔥 Fire', icon: '🔥' },
              { value: 'water', label: '💧 Water', icon: '💧' },
              { value: 'earth', label: '🌍 Earth', icon: '🌍' },
              { value: 'air', label: '💨 Air', icon: '💨' }
            ]}
            onChange={() => {}}
          />
        );

      case 'SearchInput':
        return (
          <SearchInput
            placeholder={inputConfig.placeholder}
            value={inputConfig.value}
            disabled={inputConfig.disabled}
            error={inputConfig.error || undefined}
            onChange={() => {}}
          />
        );

      default:
        return <p>Select a component to see preview.</p>;
    }
  };

  // Generate code for the current component configuration
  const generateCode = () => {
    switch (selectedComponent) {
      case 'Button':
        const buttonProps = [];
        if (buttonConfig.variant !== 'primary') buttonProps.push(`variant="${buttonConfig.variant}"`);
        if (buttonConfig.size !== 'md') buttonProps.push(`size="${buttonConfig.size}"`);
        if (buttonConfig.disabled) buttonProps.push('disabled');
        if (buttonConfig.loading) buttonProps.push('loading');
        if (buttonConfig.icon) buttonProps.push(`icon="${buttonConfig.icon}"`);
        if (buttonConfig.iconPosition !== 'left') buttonProps.push(`iconPosition="${buttonConfig.iconPosition}"`);
        
        return `<Button${buttonProps.length ? ' ' + buttonProps.join(' ') : ''}>
  ${buttonConfig.children}
</Button>`;

      case 'StatusBadge':
        const statusProps = [];
        if (statusBadgeConfig.status !== 'success') statusProps.push(`status="${statusBadgeConfig.status}"`);
        if (statusBadgeConfig.size !== 'md') statusProps.push(`size="${statusBadgeConfig.size}"`);
        if (!statusBadgeConfig.showIcon) statusProps.push('showIcon={false}');
        if (statusBadgeConfig.outlined) statusProps.push('outlined');
        
        return `<StatusBadge${statusProps.length ? ' ' + statusProps.join(' ') : ''}${statusBadgeConfig.children ? '>' : ' />'} ${statusBadgeConfig.children ? '\n  ' + statusBadgeConfig.children + '\n</StatusBadge>' : ''}`;

      // Add more cases for other components as needed
      default:
        return `// Code generation for ${selectedComponent} coming soon...`;
    }
  };

  return (
    <div style={{ 
      padding: '2rem',
      backgroundColor: '#1a1a2e',
      minHeight: '100vh',
      fontFamily: 'Segoe UI, sans-serif'
    }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <h1 style={{ color: '#f39c12', fontSize: '2.5rem', marginBottom: '1rem' }}>
            🧪 Build Your Own Component
          </h1>
          <p style={{ color: '#e0e0e0', fontSize: '1.1rem' }}>
            Interactive component playground - select a component and customize its properties
          </p>
        </div>

        {/* Component Selector */}
        <div style={{ marginBottom: '2rem' }}>
          <Card variant="elevated" padding="md">
            <CardSection type="header" title="🎯 Component Selection" />
            <CardSection type="content">
              <FormField label="Choose Component Type">
                <Select
                  value={selectedComponent}
                  onChange={(e) => setSelectedComponent(e.target.value)}
                  options={componentTypes}
                />
              </FormField>
            </CardSection>
          </Card>
        </div>

        {/* Main Layout */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', alignItems: 'start' }}>
          
          {/* Configuration Panel */}
          <Card variant="elevated" padding="md" style={{ height: 'fit-content' }}>
            <CardSection type="header" title="⚙️ Configuration" />
            <CardSection type="content">
              {renderConfigControls()}
            </CardSection>
          </Card>

          {/* Preview Panel */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            {/* Live Preview */}
            <Card variant="outlined" padding="lg">
              <CardSection type="header" title="👀 Live Preview" />
              <CardSection type="content">
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'center', 
                  alignItems: 'center',
                  minHeight: '150px',
                  padding: '2rem',
                  border: '2px dashed #4a90e2',
                  borderRadius: '8px',
                  backgroundColor: '#16213e'
                }}>
                  {renderComponent()}
                </div>
              </CardSection>
            </Card>

            {/* Code Output */}
            <Card variant="flat" padding="md" background="dark">
              <CardSection type="header" title="📝 Generated Code" />
              <CardSection type="content">
                <pre style={{ 
                  backgroundColor: '#0f3460',
                  padding: '1rem',
                  borderRadius: '4px',
                  overflow: 'auto',
                  fontSize: '14px',
                  fontFamily: 'Courier New, monospace',
                  color: '#e0e0e0',
                  border: '1px solid #4a90e2'
                }}>
                  {generateCode()}
                </pre>
              </CardSection>
            </Card>
          </div>

        </div>

        {/* Tips */}
        <div style={{ marginTop: '3rem' }}>
          <Alert type="info" title="💡 Tips for Using This Playground">
            <ul style={{ margin: '0.5rem 0', paddingLeft: '1.5rem' }}>
              <li>Select a component from the dropdown to start customizing</li>
              <li>Adjust properties using the configuration controls</li>
              <li>See live changes in the preview panel</li>
              <li>Copy the generated code to use in your app</li>
              <li>Experiment with different combinations to understand component behavior</li>
            </ul>
          </Alert>
        </div>

      </div>
    </div>
  );
}

export default BYOComponentTestScreen;
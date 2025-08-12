// Form Examples Component - Showcase all Form component variations
// Interactive examples and builder for Input, Textarea, Select, SearchInput, FormField, and Form
// Perfect for development reference and testing different form configurations

import React, { useState } from 'react';
import { 
  Input,
  Textarea,
  Select,
  SearchInput,
  FormField,
  Form
} from '../../shared/ui/Form/index.js';
import { Card, CardSection } from '../../shared/ui/Card/index.js';
import { Button } from '../../shared/ui/Button/index.js';
import { Alert } from '../../shared/ui/Feedback/index.js';

function FormExamples() {
  // Form state for examples
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    description: '',
    category: '',
    searchTerm: '',
    newsletter: false
  });

  // Interactive builder state
  const [builder, setBuilder] = useState({
    componentType: 'input',
    inputType: 'text',
    placeholder: 'Enter text...',
    disabled: false,
    error: '',
    label: 'Field Label',
    useFormField: true,
    rows: 4,
    // Select options
    selectOptions: [
      'Option 1',
      'Option 2', 
      'Option 3'
    ]
  });

  // Sample form submission
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleInputChange = (field) => (event) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  const handleBuilderChange = (field, value) => {
    setBuilder(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleFormSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    setLoading(false);
    setSubmitted(true);
    
    // Reset after 3 seconds
    setTimeout(() => setSubmitted(false), 3000);
  };

  const renderBuilderComponent = () => {
    const commonProps = {
      placeholder: builder.placeholder,
      disabled: builder.disabled,
      error: builder.error || null,
      value: 'Sample value'
    };

    let component;

    switch (builder.componentType) {
      case 'textarea':
        component = (
          <Textarea
            {...commonProps}
            rows={builder.rows}
            onChange={() => {}} // Dummy handler for demo
          />
        );
        break;
        
      case 'select':
        component = (
          <Select
            {...commonProps}
            options={builder.selectOptions}
            onChange={() => {}} // Dummy handler for demo
          />
        );
        break;
        
      case 'search':
        component = (
          <SearchInput
            {...commonProps}
            onChange={() => {}} // Dummy handler for demo
            onClear={() => {}}
          />
        );
        break;
        
      default:
        component = (
          <Input
            {...commonProps}
            type={builder.inputType}
            onChange={() => {}} // Dummy handler for demo
          />
        );
    }

    if (builder.useFormField) {
      return (
        <FormField label={builder.label} error={builder.error || null}>
          {component}
        </FormField>
      );
    }

    return component;
  };

  return (
    <Card size="lg" padding="lg" className="form-examples">
      <CardSection type="header" title="Form Components Showcase" />
      
      {/* Input Examples */}
      <CardSection type="content" title="Input Components">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
          
          {/* Basic Inputs */}
          <div>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>Input Types</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <Input
                type="text"
                placeholder="Text input"
                value={formData.username}
                onChange={handleInputChange('username')}
              />
              <Input
                type="email"
                placeholder="Email input"
                value={formData.email}
                onChange={handleInputChange('email')}
              />
              <Input
                type="password"
                placeholder="Password input"
                value={formData.password}
                onChange={handleInputChange('password')}
              />
              <Input
                type="number"
                placeholder="Number input"
              />
              <Input
                type="text"
                placeholder="Disabled input"
                disabled
              />
              <Input
                type="text"
                placeholder="Input with error"
                error="This field is required"
              />
            </div>
          </div>

          {/* Textarea Examples */}
          <div>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>Textarea</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <Textarea
                placeholder="Standard textarea"
                value={formData.description}
                onChange={handleInputChange('description')}
                rows={3}
              />
              <Textarea
                placeholder="Large textarea"
                rows={5}
              />
              <Textarea
                placeholder="Disabled textarea"
                disabled
                rows={3}
              />
              <Textarea
                placeholder="Textarea with error"
                error="Description is too short"
                rows={3}
              />
            </div>
          </div>

          {/* Select Examples */}
          <div>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>Select Dropdowns</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <Select
                options={['Option 1', 'Option 2', 'Option 3']}
                placeholder="Select an option"
                value={formData.category}
                onChange={handleInputChange('category')}
              />
              <Select
                options={[
                  { value: 'red', label: '🔴 Red' },
                  { value: 'blue', label: '🔵 Blue' },
                  { value: 'green', label: '🟢 Green' }
                ]}
                placeholder="Select with icons"
              />
              <Select
                options={['Option 1', 'Option 2']}
                placeholder="Disabled select"
                disabled
              />
              <Select
                options={['Option 1', 'Option 2']}
                placeholder="Select with error"
                error="Please make a selection"
              />
            </div>
          </div>

          {/* Search Input Examples */}
          <div>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>Search Input</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <SearchInput
                placeholder="Search..."
                value={formData.searchTerm}
                onChange={handleInputChange('searchTerm')}
                onClear={() => setFormData(prev => ({ ...prev, searchTerm: '' }))}
              />
              <SearchInput
                placeholder="Search monsters..."
                value=""
              />
              <SearchInput
                placeholder="Disabled search"
                disabled
              />
              <SearchInput
                placeholder="Search with error"
                error="Invalid search term"
              />
            </div>
          </div>
        </div>
      </CardSection>

      {/* FormField Examples */}
      <CardSection type="content" title="Form Fields with Labels">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
          
          <div>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>Labeled Fields</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <FormField label="Username">
                <Input
                  type="text"
                  placeholder="Enter username"
                />
              </FormField>
              
              <FormField label="Email Address" error="Please enter a valid email">
                <Input
                  type="email"
                  placeholder="Enter email"
                  error="Please enter a valid email"
                />
              </FormField>
              
              <FormField label="Category">
                <Select
                  options={['Gaming', 'Work', 'Personal']}
                  placeholder="Choose category"
                />
              </FormField>
              
              <FormField label="Description">
                <Textarea
                  placeholder="Enter description"
                  rows={3}
                />
              </FormField>
            </div>
          </div>

          <div>
            <h4 style={{ marginBottom: '16px', color: 'var(--color-text-primary)' }}>Complex Form</h4>
            <Form
              onSubmit={handleFormSubmit}
              loading={loading}
              error={submitted ? null : (formData.username.length < 3 ? "Username too short" : null)}
            >
              <FormField label="Full Name">
                <Input
                  type="text"
                  placeholder="Enter your full name"
                  value={formData.username}
                  onChange={handleInputChange('username')}
                />
              </FormField>

              <FormField label="Email">
                <Input
                  type="email"
                  placeholder="Enter your email"
                  value={formData.email}
                  onChange={handleInputChange('email')}
                />
              </FormField>

              <FormField label="Message">
                <Textarea
                  placeholder="Enter your message"
                  value={formData.description}
                  onChange={handleInputChange('description')}
                  rows={4}
                />
              </FormField>

              <Button
                type="submit"
                variant="primary"
                loading={loading}
                disabled={!formData.username || !formData.email}
              >
                {loading ? 'Submitting...' : 'Submit Form'}
              </Button>
            </Form>
          </div>
        </div>
      </CardSection>

      {/* Success Alert */}
      {submitted && (
        <CardSection type="content">
          <Alert type="success" title="Form Submitted Successfully!">
            Your form has been submitted with the following data:
            <pre style={{ 
              marginTop: '8px', 
              fontSize: '12px', 
              background: 'var(--color-surface-secondary)',
              padding: '8px',
              borderRadius: '4px'
            }}>
              {JSON.stringify(formData, null, 2)}
            </pre>
          </Alert>
        </CardSection>
      )}
    </Card>
  );
}

export default FormExamples;
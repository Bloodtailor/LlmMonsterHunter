// AppLoadingScreen Component - Reusable full-screen loading interface
// Handles loading states, error states, and success states with clean UI
// Uses existing shared UI components for consistent styling

import React from 'react';
import { 
  LoadingSpinner, 
  Alert, 
  Card, 
  CardSection 
} from '../../shared/ui/index.js';

/**
 * Full-screen loading screen for app initialization and other loading scenarios
 * @param {object} props - AppLoadingScreen props
 * @param {Array} props.loadingStates - Array of loading state objects with {isLoading, message}
 * @param {Array} props.errorStates - Array of error state objects with {hasError, message, error}
 * @param {string} props.title - Main title for the loading screen
 * @param {string} props.successMessage - Message to show when all states are complete (optional)
 * @param {React.ReactNode} props.successButton - Button component to show in success state (optional)
 * @returns {React.ReactElement} AppLoadingScreen component
 */
function AppLoadingScreen({
  loadingStates = [],
  errorStates = [],
  title = "Loading Application",
  successMessage = null,
  successButton = null
}) {

  // Find first error state that is active
  const activeError = errorStates.find(errorState => errorState.hasError);

  // Find first loading state that is active  
  const activeLoading = loadingStates.find(loadingState => loadingState.isLoading);

  // Determine if we're in success state (no errors, no loading)
  const isSuccess = !activeError && !activeLoading;

  // Full screen overlay styles
  const overlayStyles = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'linear-gradient(135deg, var(--background-dark) 0%, var(--background-medium) 100%)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 9999,
    backdropFilter: 'blur(4px)'
  };

  // Container styles for the card
  const containerStyles = {
    maxWidth: '500px',
    width: '90%',
    margin: '0 auto'
  };

  // Render loading content
  const renderLoadingContent = () => {
    if (!activeLoading) return null;

    return (
      <div style={{ textAlign: 'center' }}>
        <LoadingSpinner size="screen" />
        <div style={{ 
          marginTop: '1.5rem', 
          fontSize: 'var(--font-size-lg)', 
          color: 'var(--warning-color)',
          fontWeight: 'var(--font-weight-medium)'
        }}>
          {activeLoading.message}
        </div>
      </div>
    );
  };

  // Render error content
  const renderErrorContent = () => {
    if (!activeError) return null;

    return (
      <Alert 
        type="error"
        title={activeError.message}
        size="lg"
      >
        {activeError?.error}
      </Alert>
    );
  };

  // Render success content
  const renderSuccessContent = () => {
    if (!isSuccess) return null;

    return (
      <div >
        {successMessage && (
          <div style={{ 
            fontSize: 'var(--font-size-2xl)', 
            color: 'var(--success-color)', 
            fontWeight: 'var(--font-weight-bold)'
          }}>
            {successMessage}
          </div>
        )}
        {successButton && (
          <div style={{ marginTop: '1rem' }}>
            {successButton}
          </div>
        )}
      </div>
    );
  };

  // Determine main content to display
  const renderMainContent = () => {
    // Priority: Error > Loading > Success
    if (activeError) return renderErrorContent();
    if (activeLoading) return renderLoadingContent();
    if (isSuccess) return renderSuccessContent();
    
    // Fallback (shouldn't happen)
    return <div>Ready</div>;
  };

  return (
    <div style={overlayStyles}>
      <div style={containerStyles}>
        <Card size="xl" background="default">

          <CardSection 
            size="xl"  
            type="header" 
            alignment="center" 
            title={title}
          />

          <CardSection size="xl" alignment="center">
            {/* Dynamic content based on state */}
            {renderMainContent()}
          </CardSection>

        </Card>
      </div>
    </div>
  );
}

export default AppLoadingScreen;
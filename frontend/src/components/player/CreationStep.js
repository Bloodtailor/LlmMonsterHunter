// CreationStep.js - one step of the character development wizard
// Options to choose from AND a free-text answer, always both: clicking
// an option fills the text box, and the text box is the single source
// of truth for what gets saved. LLM-backed steps fetch their options on
// entry (conditioned on everything chosen so far) and can ask for
// fresh ideas; the role step uses its static list.

import React, { useEffect, useRef, useState } from 'react';
import {
  Alert,
  Button,
  Card,
  CardSection,
  LoadingContainer,
  Textarea,
} from '../../shared/ui/index.js';
import { useCreationOptions } from './useCreationOptions.js';

const optionButtonStyles = {
  display: 'block',
  width: '100%',
  textAlign: 'left',
  padding: '12px 16px',
  marginBottom: '8px',
  borderRadius: 'var(--border-radius-md, 8px)',
  border: '1px solid var(--color-border, #444)',
  background: 'var(--color-background-secondary, #222)',
  color: 'var(--color-text-primary)',
  cursor: 'pointer',
  fontSize: 'var(--font-size-md)',
  lineHeight: 1.4,
};

const selectedOptionStyles = {
  ...optionButtonStyles,
  border: '2px solid var(--color-primary, #7b5cff)',
  background: 'var(--color-background-tertiary, #2c2c40)',
};

function CreationStep({ step, choices, value, onChange, onNext, onBack, canBack, stepLabel }) {
  const { options, isLoading, error, request } = useCreationOptions(step.field);
  const [pickedOption, setPickedOption] = useState(null);

  // LLM-backed steps fetch their options once per entry, conditioned on
  // the choices made so far (a re-entered step asks again - earlier
  // answers may have changed what fits)
  const requestedRef = useRef(false);
  useEffect(() => {
    if (step.optionsFromLLM && !requestedRef.current) {
      requestedRef.current = true;
      request(choices);
    }
  }, [step.optionsFromLLM, request, choices]);

  const shownOptions = step.optionsFromLLM ? options : step.staticOptions || [];

  const pickOption = (option) => {
    setPickedOption(option);
    onChange(option);
  };

  return (
    <Card size="xl" background="light">
      <CardSection type="header" size="lg" title={step.title} alignment="center">
        <p style={{ color: 'var(--color-text-secondary)', margin: 0 }}>{step.subtitle}</p>
        <p
          style={{
            color: 'var(--color-text-secondary)',
            margin: '4px 0 0',
            fontSize: 'var(--font-size-sm)',
          }}
        >
          {stepLabel}
        </p>
      </CardSection>

      <CardSection type="content" padding="lg">
        {error && (
          <Alert type="error" title="The options did not arrive">
            {String(error)}
          </Alert>
        )}

        {step.optionsFromLLM && isLoading ? (
          <LoadingContainer isLoading={true} loadingText="Gathering ideas..." />
        ) : (
          <div>
            {shownOptions.map((option) => (
              <button
                key={option}
                type="button"
                style={option === pickedOption ? selectedOptionStyles : optionButtonStyles}
                onClick={() => pickOption(option)}
              >
                {option}
              </button>
            ))}
          </div>
        )}

        <div style={{ marginTop: '16px' }}>
          <Textarea
            value={value}
            onChange={(e) => {
              setPickedOption(null);
              onChange(e.target.value);
            }}
            placeholder={step.placeholder}
            rows={3}
          />
          <p
            style={{
              color: 'var(--color-text-secondary)',
              fontSize: 'var(--font-size-sm)',
              margin: '4px 0 0',
            }}
          >
            Pick an option or write your own - your words win.
          </p>
        </div>
      </CardSection>

      <CardSection type="content" alignment="center" padding="sm">
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
          {canBack && (
            <Button size="lg" variant="secondary" onClick={onBack}>
              Back
            </Button>
          )}
          {step.optionsFromLLM && (
            <Button
              size="lg"
              variant="secondary"
              icon="🎲"
              disabled={isLoading}
              onClick={() => request(choices)}
            >
              Fresh ideas
            </Button>
          )}
          <Button size="lg" variant="primary" disabled={!value.trim()} onClick={onNext}>
            Continue
          </Button>
        </div>
      </CardSection>
    </Card>
  );
}

export default CreationStep;

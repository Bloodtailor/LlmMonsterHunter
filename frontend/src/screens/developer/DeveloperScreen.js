// DeveloperScreen - the developer hub
// Sub-navigation over every dev tool: the AI log table + test runner
// (Overview), API tests, event tests, demos, and the UI style guides.

import React, { useState } from 'react';

import AiLogTableContainer from '../../components/developer/AiLogTable/AiLogTableContainer.js';
import TestRunner from '../../components/developer/GameTestRunner/GameTestRunner.js';
import { Card, CardSection } from '../../shared/ui/index.js';
import NavButtons from '../../shared/ui/Button/NavButtons.js';

import ApiServicesTestScreen from './ApiServicesTestScreen';
import BYOComponentTestScreen from './BYOComponentTestScreen';
import CoCaTokDemo from './CoCaTokDemo';
import EventTestScreen from './EventTestScreen.js';
import ExplosionDemo from './ExplosionDemo';
import StyleTestScreen from './StyleTestScreen';
import UiExamplesScreen from './UiExamplesScreen.js';

const DEV_SCREENS = [
  { screen: 'overview', label: '🛠️ Overview' },
  { screen: 'api-services', label: '🧪 API Tests' },
  { screen: 'event-test', label: '🧪 Event Context Test' },
  { screen: 'cocatok-demo', label: '❄️ CoCaTok Demo' },
  { screen: 'explosion-demo', label: '💥 Explosion Demo' },
  { screen: 'style-test', label: '🧪 Style Test' },
  { screen: 'ui-examples', label: '🧪 UI Examples' },
  { screen: 'byo-component', label: '🧱 BYO Component' },
];

function DeveloperScreen() {
  const [devScreen, setDevScreen] = useState('overview');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header + dev sub-navigation */}
      <Card background="light" size="xl">
        <CardSection type="header" title="Developer Screen" alignment="center">
          <p>
            Monitor LLM and Image generation logs with expandable details. Run backend tests, try
            the demos, and browse the UI library.
          </p>
        </CardSection>
        <CardSection type="content" alignment="center">
          <NavButtons
            buttons={DEV_SCREENS}
            activeScreen={devScreen}
            onScreenChange={setDevScreen}
            spacing="tight"
            alignment="center"
          />
        </CardSection>
      </Card>

      {devScreen === 'overview' && (
        <>
          <TestRunner />
          <AiLogTableContainer />
        </>
      )}
      {devScreen === 'api-services' && <ApiServicesTestScreen />}
      {devScreen === 'event-test' && <EventTestScreen />}
      {devScreen === 'cocatok-demo' && <CoCaTokDemo />}
      {devScreen === 'explosion-demo' && <ExplosionDemo />}
      {devScreen === 'style-test' && <StyleTestScreen />}
      {devScreen === 'ui-examples' && <UiExamplesScreen />}
      {devScreen === 'byo-component' && <BYOComponentTestScreen />}
    </div>
  );
}

export default DeveloperScreen;

// SettingsOverlay - the gear-opened settings surface
// A fixed overlay (like StreamingDisplay) rather than a game screen:
// opening it must never unmount a live dungeon or battle screen, and it
// works identically on the title screen and the Developer view.
// Sectioned by design - Text Generation and Images ship; future
// sections (gameplay knobs, ...) join SETTINGS_SECTIONS.

import React, { useState } from 'react';
import { Button, Card, CardSection } from '../../shared/ui/index.js';
import ImageSettingsSection from './ImageSettingsSection.js';
import LlmSettingsSection from './LlmSettingsSection.js';
import './settings.css';

const SETTINGS_SECTIONS = [
  { id: 'text-generation', label: '🗣️ Text Generation', Section: LlmSettingsSection },
  { id: 'image-generation', label: '🎨 Images', Section: ImageSettingsSection },
  // Future sections slot in here: gameplay knobs, ...
];

function SettingsOverlay({ isOpen, onClose }) {
  const [activeSectionId, setActiveSectionId] = useState(SETTINGS_SECTIONS[0].id);

  if (!isOpen) {
    return null;
  }

  const activeSection = SETTINGS_SECTIONS.find((section) => section.id === activeSectionId);
  const ActiveSectionBody = activeSection ? activeSection.Section : LlmSettingsSection;

  return (
    <div className="settings-backdrop" onClick={onClose}>
      <div className="settings-panel" onClick={(event) => event.stopPropagation()}>
        <Card size="lg" background="light">
          <div className="settings-panel-header">
            <h2 className="settings-panel-title">⚙️ Settings</h2>
            <Button size="sm" variant="ghost" onClick={onClose}>
              ✖️
            </Button>
          </div>

          {/* Section tabs appear once there is more than one section */}
          {SETTINGS_SECTIONS.length > 1 && (
            <div className="settings-section-tabs">
              {SETTINGS_SECTIONS.map((section) => (
                <Button
                  key={section.id}
                  size="sm"
                  variant={section.id === activeSectionId ? 'primary' : 'secondary'}
                  onClick={() => setActiveSectionId(section.id)}
                >
                  {section.label}
                </Button>
              ))}
            </div>
          )}

          <CardSection title={activeSection ? activeSection.label : ''}>
            <ActiveSectionBody />
          </CardSection>
        </Card>
      </div>
    </div>
  );
}

export default SettingsOverlay;

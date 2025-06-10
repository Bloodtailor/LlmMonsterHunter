# Requirements Document

**Date:** February 28, 2025  
**Document Type:** Design Phase Deliverable

## 1. Functional Requirements

### 1.1 Home Base Screen

#### 1.1.1 Party Management
- Display all captured monsters with their stats and traits
- Allow players to select and view detailed monster stats
- Provide options to evolve monsters if requirements are met
- Allow players to rename monsters
- Enable players to add or remove monsters from their active party

#### 1.1.2 Inventory Management
- Display all available items
- Allow players to add or remove items from the dungeon inventory

#### 1.1.3 Enter Dungeon
- Provide a button to start a new dungeon run

### 1.2 Dungeon Screen

#### 1.2.1 Choosing Doors
- Display three door options with descriptive names
- Allow players to select a door to proceed

#### 1.2.2 Encounters

**1.2.2.1 Traps**
- Present players with traps and options to avoid or disarm them
- Apply consequences based on player actions

**1.2.2.2 Treasures**
- Display found treasures and add them to the player's inventory

**1.2.2.3 Monsters**
- Transition to the Battle Screen when monsters are encountered

#### 1.2.3 Start New Dungeon
- Display thematic transition from Home Screen to Dungeon Screen

### 1.3 Battle Screen

#### 1.3.1 Start New Battle
- Display text description of the monsters encountered
- Monsters encountered will have a chance to have dialog with user

#### 1.3.2 Select Monster Actions
- Allow players to select actions for each monster (attack, defend, use item, capture)
- Confirm and execute actions with the Execute button

#### 1.3.3 Execute Actions
- Display enemy actions determined by the system
- Calculate and display turn order based on monsters' energy levels and recharge rates
- Execute results of each action in the battle log one by one with Next button

#### 1.3.4 Determine Round Outcome
- If all enemies are defeated, go to Battle Victory
- If all monsters in the user's party are defeated, go to Battle Defeat
- If there is at least 1 enemy and 1 ally monster undefeated, go to Select Monster Action

### 1.4 Battle Outcome Screen

#### 1.4.1 Battle Victory
- Display text description of the celebration of the victory
- Chance to gain new Item
- Chance to gain new Ability
- Chance to gain new Title
- Display option to talk with a defeated Monster

#### 1.4.2 Battle Defeat
- Display text review of the battle detailing the final blow that ended the battle in a defeat

#### 1.4.3 Encounter Exit
- Provide the option to exit the dungeon to the Home Base Screen or continue to the Dungeon Screen

#### 1.4.4 Exit in Victory
- Monsters have a chance to gain new Ability
- Monsters have a chance to gain new Title
- Add inventory to Home Base
- Add captured monsters to Home Base
- Display closing remarks summarizing the dungeon run
- Chance to encounter an exit, if not, return to Dungeon Screen

#### 1.4.5 Exit in Defeat
- Monsters have a chance to gain new Ability
- Items in inventory are lost
- Captured monsters are lost
- Display closing remarks summarizing the Dungeon Run
- Return to Home Base

### 1.5 Chat Screen

#### 1.5.1 Start New Chat
- Create a new chat with one of the Monsters
- Display Monster's introduction message

#### 1.5.2 Chat with Monster
- Allow Users to chat with Monster as a roleplay chatbot
- Display Monster response

## 2. Non-Functional Requirements

### 2.1 Performance
- **2.1.1** The game should load within 5 seconds
- **2.1.2** Battles and dungeon transitions should not exceed a 2-second delay
- **2.1.3** AI-related tasks (e.g., generating monster evolutions, new abilities) should not make the player wait longer than 20 seconds. AI tasks should run in the background proactively when possible

### 2.2 Usability
- **2.2.1** The interface should be intuitive and easy to navigate
- **2.2.2** Provide tooltips and help options for new players

### 2.3 Expandability
- **2.3.1** The game should be easy to expand with new items, abilities, monster types, traps, and encounters
- **2.3.2** The combat system should allow for adding more depth and new functionalities in the home base
- **2.3.3** Code should be modular, intuitive, and well-commented to facilitate future expansions

### 2.4 Reliability
- **2.4.1** Ensure the game saves progress frequently to prevent data loss
- **2.4.2** Implement error handling to manage unexpected issues gracefully

### 2.5 Compatibility
- **2.5.1** The game should run on a Windows machine with specific hardware requirements (see Section 3)

## 3. System Requirements

### 3.1 Hardware
- **3.1.1** 8GB VRAM (NVIDIA GPU required for AI models)
- **3.1.2** 32GB RAM available
- **3.1.3** Minimum 10GB available storage

### 3.2 Software
- **3.2.1** Windows 11
- **3.2.2** Python 3.8 or higher
- **3.2.3** Flask
- **3.2.4** MySQL
- **3.2.5** HTML, CSS, JavaScript, React
- **3.2.6** Pygame
- **3.2.7** Llama-cpp-python for LLM
- **3.2.8** ComfyUI for image generation

### 3.3 Dependencies
- **3.3.1** Ensure all necessary libraries and frameworks are installed and updated
- **3.3.2** Maintain documentation for setting up the development environment

## MVP Considerations

Based on the [MVP Development Strategy](../strategy/mvp_development_strategy.md), the following requirements are **simplified for initial implementation**:

### Simplified Monster Abilities
- **Original Requirement:** Complex ability trees and dynamic ability acquisition
- **MVP Implementation:** 1-2 basic abilities per monster with predefined effects

### Simplified Battle Processing
- **Original Requirement:** Full LLM-processed battle outcomes
- **MVP Implementation:** Basic math-driven combat with simple LLM narrative enhancement

### Simplified Evolution System
- **Original Requirement:** Complete stat/ability regeneration with new artwork
- **MVP Implementation:** Title changes only (e.g., "Rokk" → "Rokk the Brave")

### Simplified AI Integration
- **Original Requirement:** Complex emergent storytelling
- **MVP Implementation:** Basic personality responses and encounter descriptions

## Future Enhancement Requirements

The following requirements are **preserved for post-MVP iterations**:

- Advanced monster ability system with complex interactions
- Deep LLM integration for battle processing and narrative generation
- Complete evolution system with stat regeneration and new artwork
- Advanced inventory management with complex item effects
- Sophisticated AI-driven story generation
- Complex dungeon generation with varied encounter types

---

**Previous:** [MVP Development Strategy](../strategy/mvp_development_strategy.md) | **Next:** [Use Cases](../use_cases/use_cases.md)
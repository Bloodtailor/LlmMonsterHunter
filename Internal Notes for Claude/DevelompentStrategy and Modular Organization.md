# Internal Notes for Claude - Development Strategy and Modular Organization

**READ THIS FIRST IN NEXT CHAT:** This document outlines how to break down the PreMVP prototype into a better modular structure for the actual MVP development.

## Session-by-Session Development Plan

### Session 1: Foundation Setup
**Goal:** Get basic Flask app running with database connection
**Files:** 3-4 files, ~150 lines total
- `app.py` - Basic Flask app (30 lines)
- `config/database.py` - Database connection (40 lines)
- `models/base.py` - SQLAlchemy base setup (30 lines)
- `requirements.txt` - Dependencies (20 lines)
- `run.py` - Application runner (20 lines)

### Session 2: First Model and API
**Goal:** Create Player model and basic API endpoint
**Files:** 3 files, ~180 lines total
- `models/player.py` - Player model (60 lines)
- `routes/game_routes.py` - Basic game API (80 lines)
- `services/game_service.py` - Game business logic (40 lines)

### Session 3: Monster Foundation
**Goal:** Monster models and basic monster API
**Files:** 3 files, ~200 lines total
- `models/monster.py` - Monster models (80 lines)
- `routes/monster_routes.py` - Monster API endpoints (70 lines)
- `services/monster_service.py` - Monster business logic (50 lines)

### Session 4: React Foundation
**Goal:** Basic React app that calls Flask API
**Files:** 4 files, ~160 lines total
- `frontend/src/App.js` - Main React app (40 lines)
- `frontend/src/services/api.js` - API service (50 lines)
- `frontend/src/components/HomeBase.js` - Basic home screen (50 lines)
- `frontend/src/App.css` - Basic styling (20 lines)

### Session 5: Home Base Functionality
**Goal:** Complete home base with monster management
**Files:** 3-4 files, ~200 lines total
- `frontend/src/components/MonsterCard.js` - Monster display (60 lines)
- `frontend/src/components/PartyManager.js` - Party management (70 lines)
- `frontend/src/hooks/useGameState.js` - State management (50 lines)
- CSS files as needed

### Sessions 6-10: Core Features
- Dungeon exploration system
- Battle system implementation
- LLM integration
- Chat system
- Save/load functionality

## File Organization Strategy

### Backend Structure:
```
backend/
├── app.py                 # Flask app factory
├── run.py                 # Application runner
├── config/
│   ├── __init__.py
│   ├── database.py        # DB connection settings
│   ├── game_constants.py  # Game rules and values
│   ├── api_config.py      # API configuration
│   └── llm_config.py      # LLM settings
├── models/
│   ├── __init__.py
│   ├── base.py           # SQLAlchemy base
│   ├── player.py         # Player model
│   ├── monster.py        # Monster models
│   ├── inventory.py      # Item models
│   ├── chat.py           # Chat models
│   └── battle.py         # Battle models
├── routes/
│   ├── __init__.py
│   ├── game_routes.py    # Game state endpoints
│   ├── monster_routes.py # Monster management
│   ├── chat_routes.py    # Chat system
│   ├── dungeon_routes.py # Dungeon exploration
│   └── battle_routes.py  # Battle system
├── services/
│   ├── __init__.py
│   ├── game_service.py   # Game logic
│   ├── monster_service.py # Monster management
│   ├── llm_service.py    # LLM integration
│   ├── chat_service.py   # Chat logic
│   ├── dungeon_service.py # Dungeon logic
│   └── battle_service.py # Battle logic
├── utils/
│   ├── __init__.py
│   ├── validators.py     # Input validation
│   ├── helpers.py        # Utility functions
│   └── exceptions.py     # Custom exceptions
└── tests/
    ├── test_api.py       # API testing script
    └── test_models.py    # Model testing
```

### Frontend Structure:
```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── App.js
│   ├── index.js
│   ├── components/
│   │   ├── ui/              # Reusable UI components
│   │   │   ├── Button.js
│   │   │   ├── Card.js
│   │   │   ├── Modal.js
│   │   │   └── LoadingSpinner.js
│   │   ├── game/            # Game-specific components
│   │   │   ├── MonsterCard.js
│   │   │   ├── PartySlot.js
│   │   │   ├── InventoryPanel.js
│   │   │   └── BattleField.js
│   │   └── screens/         # Full screen components
│   │       ├── HomeBase.js
│   │       ├── Dungeon.js
│   │       ├── Battle.js
│   │       └── Chat.js
│   ├── hooks/
│   │   ├── useGameState.js  # Game state management
│   │   ├── useApi.js        # API interaction
│   │   └── useLocalStorage.js # Local storage
│   ├── services/
│   │   ├── api.js           # API service
│   │   └── gameLogic.js     # Client-side game logic
│   ├── utils/
│   │   ├── constants.js     # Game constants
│   │   ├── helpers.js       # Utility functions
│   │   └── validators.js    # Input validation
│   ├── styles/
│   │   ├── globals.css      # Global styles
│   │   ├── theme.css        # Color theme
│   │   ├── components/      # Component-specific CSS
│   │   └── screens/         # Screen-specific CSS
│   └── assets/
│       └── images/
```

## Configuration Management

### Game Constants (`config/game_constants.py`):
```python
# Game Rules
MAX_PARTY_SIZE = 4
MAX_DUNGEON_INVENTORY = 10
MAX_MONSTER_LEVEL = 50

# Battle System
BASE_ATTACK_POWER = 20
DEFENSE_REDUCTION_FACTOR = 0.5
CRITICAL_HIT_CHANCE = 0.1

# Experience System
BASE_EXP_GAIN = 25
EXP_PER_LEVEL = 100

# Affinity System
MIN_AFFINITY = 0
MAX_AFFINITY = 100
DEFAULT_AFFINITY = 50
```

### Theme Configuration (`frontend/src/styles/theme.css`):
```css
:root {
  /* Color Palette */
  --primary-color: #007bff;
  --secondary-color: #6c757d;
  --success-color: #28a745;
  --danger-color: #dc3545;
  --warning-color: #ffc107;
  
  /* Game-Specific Colors */
  --monster-health-high: #4CAF50;
  --monster-health-medium: #FF9800;
  --monster-health-low: #F44336;
  
  /* Gradients */
  --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --gradient-battle: linear-gradient(135deg, #8B0000 0%, #DC143C 50%, #FF6347 100%);
  
  /* Spacing */
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
}
```

## Modular Breakdown of PreMVP Components

### Large CSS Files → Component CSS:
**PreMVP:** Single 800+ line CSS file
**MVP:** Split into:
- `theme.css` (50 lines) - Color scheme and spacing
- `globals.css` (80 lines) - Reset and base styles
- `components/MonsterCard.css` (60 lines)
- `components/Battle.css` (90 lines)
- `screens/HomeBase.css` (70 lines)

### Large API Route Files → Feature Routes:
**PreMVP:** Single routes file with all endpoints
**MVP:** Split by feature:
- `game_routes.py` (60 lines) - Save/load, status
- `monster_routes.py` (80 lines) - Monster CRUD operations
- `chat_routes.py` (50 lines) - Chat system
- `battle_routes.py` (70 lines) - Battle system

### React Context → Multiple Hooks:
**PreMVP:** Single context managing everything
**MVP:** Split by concern:
- `useGameState.js` (80 lines) - Core game state
- `useApi.js` (60 lines) - API interactions
- `useBattle.js` (70 lines) - Battle-specific state
- `useChat.js` (50 lines) - Chat system state

## Development Best Practices

### Code Documentation:
- **Every function:** JSDoc/docstring explaining purpose
- **Complex logic:** Inline comments explaining why
- **API endpoints:** Clear parameter and response docs
- **Component props:** PropTypes or TypeScript interfaces

### Error Handling:
- **API errors:** Structured error responses with codes
- **Frontend errors:** Error boundaries and user feedback
- **Development errors:** Detailed logging for debugging
- **User errors:** Clear, helpful error messages

### Testing Strategy:
- **API testing:** Simple Python scripts to test endpoints
- **Manual testing:** Step-by-step user flow verification
- **Error testing:** Deliberately break things to test recovery
- **Integration testing:** End-to-end feature testing

### Performance Considerations:
- **Database:** Add indexes as needed
- **API:** Keep responses small and focused
- **React:** Use React.memo for expensive components
- **LLM:** Cache responses where appropriate

## Development Tools and Scripts

### Essential Development Scripts:
- `scripts/setup.py` - Initial project setup
- `scripts/test_api.py` - API endpoint testing
- `scripts/reset_db.py` - Database reset for testing
- `scripts/seed_data.py` - Add sample data

### Debugging Tools:
- Enhanced error logging
- API request/response logging
- React DevTools integration
- Database query logging

## Windows-Specific Considerations

### Path Handling:
```python
from pathlib import Path
# Always use Path objects, never string concatenation
MODEL_PATH = Path(__file__).parent / "models" / "llm_model.gguf"
```

### GPU Setup:
```bash
# CUDA-enabled llama-cpp-python
pip install llama-cpp-python[cuda] --no-cache-dir
```

### Virtual Environment:
```bash
# Windows-specific activation
python -m venv venv
venv\Scripts\activate
```

This modular approach will make each development session focused and manageable while building toward a complete, working game.
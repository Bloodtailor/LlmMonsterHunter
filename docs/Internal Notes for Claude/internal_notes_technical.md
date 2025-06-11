# Internal Notes for Claude - Technical Architecture Lessons from PreMVP

**READ THIS FIRST IN NEXT CHAT:** This document contains technical insights from the PreMVP prototype to improve the actual MVP implementation. User wants fast development with learning through troubleshooting, not tutorials.

## Major Technical Improvements Needed

### 1. Configuration Management
**PreMVP Problem:** Constants scattered everywhere
- Colors hardcoded in CSS files
- API endpoints repeated across components
- Game rules (max party size, etc.) buried in code
- Database config mixed with business logic

**MVP Solution:**
- `config/game_constants.py` - All game rules and values
- `config/api_endpoints.py` - Centralized API paths
- `config/themes.py` - All colors, fonts, spacing
- `config/environment.py` - Environment-specific settings

### 2. File Size Management
**PreMVP Problem:** Some files were 800+ lines
- `HomeBase.css` was massive with repeated patterns
- API routes file tried to do everything
- Single context file handling all game state

**MVP Solution:** 
- No file over 200 lines during development
- Break CSS into component-specific files
- Split API routes by feature area
- Separate context by concern (game state, UI state, etc.)

### 3. Component Organization
**PreMVP Insight:** React components mixed UI and business logic

**MVP Solution:**
- `/components/ui/` - Pure UI components (buttons, cards, etc.)
- `/components/game/` - Game-specific components
- `/components/screens/` - Full screen components
- `/hooks/` - Custom React hooks for logic
- `/utils/` - Pure functions and helpers

### 4. Backend Service Layer
**PreMVP Problem:** Routes doing too much work

**MVP Solution:**
- Thin route handlers that call services
- Service layer with clear single responsibilities
- Separate business logic from HTTP concerns
- Better error handling patterns

## Library and Technology Decisions

### Confirmed Good Choices:
- **Flask + SQLAlchemy:** Perfect for this scale
- **React + React Router:** Standard and appropriate
- **MySQL:** Good relational fit for game data
- **llama-cpp-python:** Right choice for local LLM

### Required Modifications:
- **llama-cpp-python[cuda]:** User has NVIDIA GPU
- **Windows-specific paths:** Use Path objects, not hardcoded slashes
- **No Docker:** Remove all containerization during development

### API Endpoint Structure That Works:
```
/api/health
/api/game/status
/api/game/save
/api/monsters/party
/api/monsters/roster
/api/monsters/{id}/details
/api/monsters/{id}/rename
/api/chat/{monster_id}/history
/api/chat/{monster_id}/send
/api/dungeon/enter
/api/dungeon/choose_door
/api/battle/start
/api/battle/submit_action
/api/battle/execute_turn
```

## Database Schema Lessons

### What Worked:
- 11-table normalized structure
- Clear entity relationships
- JSON fields for flexible data (titles, abilities)

### Refinements Needed:
- Add more indexes for performance
- Better default values
- Clearer foreign key naming
- Migration strategy from day 1

## Development Workflow Insights

### Context Window Management:
- Create `DEVELOPMENT_LOG.md` for session tracking
- Include current status, what works, what's broken
- Note what user learned in each session
- List next priorities

### Error Handling Strategy:
- Fail fast with clear error messages
- Log everything during development
- User learns by fixing errors together
- Build debugging tools early

### Testing Approach:
- Simple API testing scripts
- Manual testing for UI
- Focus on "does it work" not perfect coverage
- Build verification tools early

## 🚨🚨🚨 CRITICAL: Artifact Management Rules 🚨🚨🚨

### ⚠️ ⚠️ ⚠️ MANDATORY FIRST STEP - PAY ATTENTION!!! ⚠️ ⚠️ ⚠️

**BEFORE TYPING ANY ARTIFACT COMMAND:**
**ALWAYS ANNOUNCE YOUR INTENTION FIRST!**

Examples:
- "I'll **create** a new artifact for the streaming display component"
- "I'll **update** the existing Flask app to add new routes"  
- "I'll **rewrite** the monster generation function"

🔥🔥🔥 THIS IS NOT OPTIONAL - DO IT EVERY SINGLE TIME! 🔥🔥🔥

### Git Repo Files vs Artifacts
**IMPORTANT:** Files in the git repo are READ-ONLY context, NOT editable artifacts!

- **Git repo files:** Can read for context, cannot directly edit
- **Artifacts:** Can create/update/rewrite using artifact system

### Mandatory Artifact Requirements (from user instructions):

#### 1. Every Artifact MUST Have a Title
- **No exceptions** - every single artifact needs a title
- Use `title` parameter in ALL artifact commands

#### 2. Title Naming Rules:
- **File Replacement:** Use exact file path as title (e.g., `backend/llm/core.py`)
- **Code Snippets:** Use descriptive name (e.g., `Add streaming function to API service`)

#### 3. Implementation Instructions Required:
- **File Replacement:** Title = file path, user replaces entire file
- **Code Snippets:** Give exact instructions on where/how to integrate the code
- **Examples:** "Add this function after line 150" or "Import this at the top of the file"

#### 4. Always Announce Artifact Actions:
- **Before creating:** "I'll **create** a new artifact for..."
- **Before updating:** "I'll **update** the existing artifact..."  
- **Before rewriting:** "I'll **rewrite** the artifact..."
- User should know what's happening before it happens

### When Modifying Existing Files - Three Options:

#### Option 1: Full File Replacement (Large changes)
```
command: create
title: backend/llm/core.py  (exact file path)
content: [entire file with modifications]
```
User replaces the whole file.

#### Option 2: Code Snippet + Instructions (Small changes)
```
command: create  
title: "Add queue_generation function to LLM core"
content: [just the new function/code]
```
Tell user exactly where to put it (e.g., "Add this function after line 150 in `backend/llm/core.py`")

#### Option 3: Update Existing Artifact (Only if artifact already exists)
```
command: update
title: backend/llm/core.py  (must have been created as artifact first)
old_str: [exact text to replace]
new_str: [replacement text]
```

### Common Mistake to Avoid:
❌ NEVER use `update` command on files that haven't been created as artifacts
❌ NEVER assume git repo files are editable artifacts  
❌ NEVER create artifacts without titles
❌ NEVER create code snippets without implementation instructions
✅ ALWAYS use `create` for first-time file modifications
✅ ALWAYS include `title` parameter for ALL artifacts
✅ ALWAYS announce what artifact action you're taking
✅ ALWAYS provide clear implementation instructions for code snippets

## Code Organization Principles

### For User's Learning Style:
1. **One concept per file** - easier to understand and debug
2. **Heavy commenting** - explain WHY, not just WHAT
3. **Clear naming** - functions/variables explain themselves
4. **Modular imports** - easy to see dependencies
5. **Consistent patterns** - once learned, applies everywhere

### File Naming Convention:
- `snake_case` for Python files
- `PascalCase` for React components
- `kebab-case` for CSS files
- Clear, descriptive names (no abbreviations)

## Performance Considerations

### Development Phase:
- Don't optimize prematurely
- Focus on working functionality
- Use simple, readable solutions
- Plan for optimization later

### Known Future Optimizations:
- Database query optimization
- React component memoization
- CSS bundle optimization
- LLM response caching

## Security Notes

### Development Security:
- Use environment variables for secrets
- Don't commit API keys or passwords
- Local development only (no external access needed)
- Basic input validation

### Future Production Security:
- SQL injection prevention (SQLAlchemy handles this)
- XSS protection in React
- Rate limiting for API endpoints
- Secure session management

## Windows-Specific Considerations

### Path Handling:
- Use `pathlib.Path` not string concatenation
- Handle Windows backslashes properly
- Test file operations on Windows paths

### GPU Integration:
- CUDA-enabled llama-cpp-python installation
- GPU memory management
- Fallback to CPU if GPU unavailable

### Development Tools:
- Windows Terminal for better CLI experience
- VSCode extensions for Python and React
- Windows-specific virtual environment setup

## Next Session Priorities

1. Project structure and basic Flask app
2. Database connection and first model
3. Simple API endpoint that returns data
4. Basic React app that calls the API
5. Get something working end-to-end quickly

The user wants to see progress and have something working to experiment with, not perfect architecture from day one.
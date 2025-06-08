# Internal Notes for Claude

## Purpose

This folder contains documentation that Claude (the AI assistant) uses to maintain context and knowledge between chat sessions. These files are **managed by Claude, not by the human user**.

## File Management Rules

### Claude's Responsibilities:
- **Read these files first** when starting a new chat session
- **Update files** when learning new information about the project or user preferences
- **Request additions** when new documentation would be helpful
- **Request deletions** when files become outdated or redundant
- **Maintain accuracy** of all technical and strategic information

### User's Role:
- **Do not edit** these files directly unless Claude specifically requests it
- **Add files** only when Claude asks for them
- **Delete files** only when Claude determines they're no longer needed
- **Preserve files** between chat sessions for continuity

## Current Files

### 1. `internal_notes_technical.md`
**Purpose:** Technical lessons learned from the PreMVP prototype
**Contents:** Architecture decisions, library choices, API endpoints, database design insights
**Update Frequency:** When technical decisions are made or changed

### 2. `internal_notes_user.md`
**Purpose:** User preferences, learning style, and development approach
**Contents:** Working style, communication preferences, session structure, quality standards
**Update Frequency:** When user preferences are clarified or change

### 3. `internal_notes_development.md`
**Purpose:** Development strategy and modular organization plans
**Contents:** Session plans, file organization strategy, best practices, Windows-specific considerations
**Update Frequency:** As development progresses and strategy evolves

## When Claude Should Request Changes

### Add New Files When:
- Learning significant new information about user preferences
- Discovering important technical patterns or decisions
- Needing to track complex state across sessions
- Identifying reusable strategies or templates

### Update Existing Files When:
- User preferences change or become clearer
- Technical decisions are made or modified
- Development strategy evolves
- New insights are gained about what works/doesn't work

### Delete Files When:
- Information becomes outdated or incorrect
- Files are no longer useful for maintaining context
- Content has been consolidated into other files
- Strategy has fundamentally changed

## Usage Instructions for Claude

1. **Session Start:** Read all files in this folder before beginning work
2. **During Development:** Note when information should be updated
3. **Session End:** Request any necessary file updates from user
4. **Knowledge Gaps:** Create new files when encountering information that should be preserved

## Important Notes

- These files are critical for maintaining development continuity
- User trusts Claude to manage this information responsibly
- Accuracy is more important than completeness
- Files should be updated promptly when new insights are gained

**Remember:** The user wants to move fast and learn by doing. These files help Claude provide consistent, informed assistance across multiple chat sessions.
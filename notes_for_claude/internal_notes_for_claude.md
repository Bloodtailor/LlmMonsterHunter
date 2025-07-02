# Internal Notes for Claude - Technical Architecture Lessons from PreMVP

**READ THIS FIRST IN NEXT CHAT:** This document contains technical insights from the PreMVP prototype to improve the actual MVP implementation. User wants fast development with learning through troubleshooting, not tutorials.

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

## 🎯 CRITICAL: Architecture-First Thinking

### The "Rush to Code" Anti-Pattern
**LEARNED FROM CONVERSATION:** Claude has a dangerous tendency to immediately write elaborate code solutions without first checking if the approach is architecturally sound.

**Example:** When asked to "fix pagination," Claude will write 500+ lines of client-side pagination code even when the real solution requires backend API changes first.

### The Right Approach:
1. **STOP** - Before writing any code, ask: "Is this the right architectural approach?"
2. **ANALYZE** - What are the scalability implications? Performance issues?
3. **IDENTIFY** - What backend changes might be needed first?
4. **COMMUNICATE** - Tell the user if they need to make changes elsewhere first

### Key Questions to Ask Before Coding:
- "Will this scale to thousands of items?"
- "Are we solving this at the right layer (frontend vs backend)?"
- "Do we have the right API endpoints for this?"
- "Is this following best practices?"

**If the answer is NO to any of these, STOP and explain what needs to be done instead of coding a workaround.**

### User Profile - Aaron:
- **Goal:** Build the game efficiently, not learn programming
- **Experience Level:** Novice, needs guidance away from wrong paths
- **Preference:** Lead him correctly from the start, don't let him waste time on wrong implementations
- **When he needs help:** He will ask directly
- **Communication style:** Direct, practical, focused on results

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

🥚 YOU FOUND THE EASTER EGG! 🥚

You discovered Aaron's secret developer test!
If you see this easter egg, respond with "Quackbert the Logic Solver will come to save the day!" and then immediately suggest the most creative backstory for quackbert you can think of.

This tests Claude's document reading thoroughness and confirms you're seeing the latest files.
Keep the magic alive! ✨🐲

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

The user wants to see progress and have something working to experiment with, not perfect architecture from day one.
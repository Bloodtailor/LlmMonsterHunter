# MVP Development Strategy

**Date:** June 8, 2025  
**Author:** Aaron Orelup  
**Document Type:** Strategy Pivot

## Executive Summary

After completing comprehensive planning documentation in February 2025, development has pivoted from a documentation-heavy Waterfall approach to a Rapid Prototyping / MVP-First methodology. This document defines the simplified scope for the Minimum Viable Product (MVP) while preserving the full vision for future iterations.

## Methodology Change

### Original Approach (Feb 2025)
- **Waterfall SDLC** with complete documentation before coding
- Comprehensive planning phase with detailed specifications
- Risk of losing motivation due to documentation overhead

### New Approach (June 2025)  
- **Rapid Prototyping / MVP-First Development**
- Build working version quickly to validate core concepts
- Learn by doing, iterate based on experience
- Add complexity incrementally after core systems proven

### Catalyst for Change
- **3-month gap** led to motivation loss due to documentation focus
- **Android app project** (March-May 2025) successfully taught:
  - Python model loading and inference
  - Local server setup and API design
  - Prompt engineering and model testing
  - Practical LLM integration experience

## MVP Scope Definition

### Core Features (Simplified Implementation)

#### ✅ **Home Base System**
- Monster roster management
- Basic inventory system
- Party selection (4 monsters max)
- Simple save/load functionality

#### ✅ **Dungeon Exploration**  
- Three-door choice system
- Basic encounters: Monster, Trap, Treasure, Exit
- Simple narrative generation via LLM

#### ✅ **Battle System (Simplified)**
- Turn-based combat with basic actions: Attack, Defend, Use Item
- **Simplified Monster Abilities:** 1-2 basic abilities per monster (e.g., "Fire Attack", "Heal")
- **Simplified Battle Processing:** Basic damage calculations, minimal status effects
- Victory/defeat conditions

#### ✅ **Monster Chat System**
- Basic conversational interface with captured monsters
- Simple personality responses via LLM
- Conversation history storage

#### ✅ **Monster Capture**
- Post-battle recruitment dialog
- Basic affinity system (simplified)

#### ✅ **Monster Generation (Simplified)**
- **Basic Monster Design:** Name, 2-3 basic stats, simple description
- **Simplified Evolution:** Title change only (e.g., "Rokk" → "Rokk the Brave")
- Basic AI-generated monster cards

### Deliberately Simplified for MVP

#### 🔄 **Complex Monster Systems** (Future Enhancement)
- **Original Vision:** Deep ability trees, complex stat interactions, dynamic ability acquisition
- **MVP Version:** 1-2 predefined abilities per monster, basic stats only
- **Rationale:** Gameplay balance is complex; start simple and iterate

#### 🔄 **Advanced Battle Mechanics** (Future Enhancement)  
- **Original Vision:** LLM-processed battle outcomes, complex ability interactions
- **MVP Version:** Basic math-driven combat with simple LLM narrative
- **Rationale:** Core loop must be fun before adding complexity

#### 🔄 **Deep Evolution System** (Future Enhancement)
- **Original Vision:** Full stat/ability regeneration, new artwork, personality changes  
- **MVP Version:** Title changes only
- **Rationale:** Artwork pipeline and complex evolution logic can be added later

#### 🔄 **Advanced Story Elements** (Future Enhancement)
- **Original Vision:** Emergent narratives, complex monster motivations
- **MVP Version:** Basic encounter descriptions and monster personalities
- **Rationale:** Focus on core gameplay loop first

## Technical Implementation Strategy

### Phase 1: Core Systems (MVP)
1. **Database Schema:** Basic tables for monsters, players, inventory
2. **Flask Backend:** Simple API endpoints for game actions
3. **Basic Frontend:** Functional UI without advanced styling
4. **LLM Integration:** Simple prompts for monster generation and chat
5. **Local Testing:** Desktop deployment only

### Phase 2: Enhancement Iterations (Post-MVP)
- Complex ability system implementation
- Advanced battle mechanics
- Rich evolution system  
- Improved UI/UX
- Additional content types

## Success Criteria for MVP

### Technical Success
- [ ] Game runs locally without crashes
- [ ] Complete core gameplay loop functional
- [ ] Basic LLM integration working
- [ ] Save/load system operational

### Learning Success  
- [ ] Practical experience with full-stack Python/React development
- [ ] LLM integration in real application context
- [ ] Database design and management experience
- [ ] Project completion satisfaction

### Gameplay Success
- [ ] Core loop is engaging for at least 30 minutes of play
- [ ] Monster generation produces interesting variety
- [ ] Battle system feels strategic despite simplicity
- [ ] Chat system creates connection with monsters

## Risk Mitigation

### Scope Management
- **Risk:** Feature creep during MVP development
- **Mitigation:** Strict adherence to simplified scope; track enhancement ideas separately

### Technical Complexity
- **Risk:** LLM integration complexity 
- **Mitigation:** Leverage Android app experience; start with simple prompts

### Motivation Maintenance
- **Risk:** Losing motivation during development
- **Mitigation:** Focus on working software over documentation; celebrate small wins

## Future Vision Preservation

This MVP approach does **not** abandon the original comprehensive vision documented in February 2025. Instead, it provides:

- **Validation Platform:** Test core concepts before investing in complexity
- **Learning Foundation:** Build technical skills incrementally  
- **Motivation Maintenance:** Working software provides ongoing engagement
- **Iteration Base:** Solid foundation for adding sophisticated features

The full feature set from the original proposal remains the target for future iterations, informed by lessons learned during MVP development.

## Next Steps

1. **Environment Setup:** Configure development environment (Python, Flask, React, MySQL)
2. **Database Design:** Create simplified schema for MVP scope
3. **Core Backend:** Implement basic game logic and LLM integration
4. **Basic Frontend:** Create functional UI for core features
5. **Testing & Iteration:** Play-test and refine core gameplay loop

---

**Previous:** [Project Plan](../planning/06_project_plan.md) | **Next:** [Requirements Document](../design/requirements.md)

**Document Location:** Place this document chronologically after "Project Proposal - 2/28/2025" in your project documentation folder to maintain the development timeline and decision trail.
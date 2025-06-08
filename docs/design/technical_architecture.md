# Technical Architecture

**Date:** February 28, 2025  
**Document Type:** Design Phase Deliverable

## System Overview

The Monster Hunter Game employs a modern full-stack architecture designed to leverage AI technologies while maintaining performance and scalability. The system is built around a Python/Flask backend with React frontend, integrated with local LLM services for dynamic content generation.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Layer                             │
├─────────────────────────────────────────────────────────────┤
│  React Frontend (JavaScript/HTML/CSS)                      │
│  ├── Home Base Components                                  │
│  ├── Dungeon Interface                                     │
│  ├── Battle System UI                                      │
│  └── Chat Interface                                        │
└─────────────────────────────────────────────────────────────┘
                                │
                          HTTP/REST API
                                │
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                         │
├─────────────────────────────────────────────────────────────┤
│  Flask Backend (Python)                                    │
│  ├── API Routes                                            │
│  ├── Game Logic Services                                   │
│  ├── LLM Integration Services                              │
│  └── Database Access Layer                                 │
└─────────────────────────────────────────────────────────────┘
                                │
                         Local Network
                                │
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                            │
├─────────────────────────────────────────────────────────────┤
│  AI Services (Local)                                       │
│  ├── Llama-cpp-python Server                               │
│  ├── ComfyUI API Server                                    │
│  └── Model Management                                      │
└─────────────────────────────────────────────────────────────┘
                                │
                         Database Layer
                                │
┌─────────────────────────────────────────────────────────────┐
│                     Data Layer                              │
├─────────────────────────────────────────────────────────────┤
│  MySQL Database                                            │
│  ├── Game State Tables                                     │
│  ├── Monster Data                                          │
│  ├── Chat History                                          │
│  └── System Configuration                                  │
└─────────────────────────────────────────────────────────────┘
```

## Technical Stack

### Backend Technologies

#### **Python 3.8+ with Flask 3.0**
- **Primary Application Framework:** Flask provides lightweight, flexible web application structure
- **API Development:** RESTful API endpoints for frontend communication
- **Modular Design:** Flask blueprints for organizing different game systems
- **Development Benefits:** Rapid development, extensive library ecosystem, excellent AI integration

#### **MySQL Database**
- **Relational Data Storage:** Structured storage for game entities and relationships
- **ACID Compliance:** Ensures data consistency for game state management
- **Performance:** Optimized queries for real-time gameplay requirements
- **Scalability:** Can handle growing player data and monster collections

#### **Game Logic Framework**
- **Pygame Integration:** Handles game state management and logic processing
- **Custom Game Engine:** Built on top of Flask for web-based gaming
- **Turn-Based Processing:** Optimized for strategic gameplay mechanics
- **State Management:** Persistent game state across sessions

### Frontend Technologies

#### **React 18+ with Modern JavaScript**
- **Component-Based Architecture:** Modular UI components for different game screens
- **State Management:** React hooks for local state, context for global game state
- **Dynamic Rendering:** Real-time updates for battle sequences and monster interactions
- **User Experience:** Smooth, responsive interface for engaging gameplay

#### **HTML5/CSS3**
- **Semantic Structure:** Accessible markup for screen readers and assistive technologies
- **Responsive Design:** Flexible layouts that adapt to different screen sizes
- **Modern Styling:** CSS Grid and Flexbox for complex UI layouts
- **Performance:** Optimized CSS for fast rendering

#### **Development Tools**
- **Create React App:** Standardized development environment and build process
- **ES6+ Features:** Modern JavaScript features for cleaner, more maintainable code
- **Module Bundling:** Webpack for optimized asset delivery
- **Hot Reloading:** Rapid development feedback during frontend development

### AI Integration Layer

#### **Large Language Model (LLM) Integration**

**Llama-cpp-python for Text Generation**
- **Local Inference:** Privacy-focused local model execution
- **API Compatibility:** OpenAI-compatible API for easy integration
- **Performance Optimization:** CUDA acceleration for fast response times
- **Model Flexibility:** Support for various model sizes and types

**Implementation:**
```python
from llama_cpp import Llama

class LLMService:
    def __init__(self, model_path):
        self.llm = Llama(
            model_path=model_path,
            n_gpu_layers=35,  # GPU acceleration
            n_ctx=4096,      # Context window
            n_batch=512      # Batch size
        )
    
    def generate_monster(self, prompt):
        response = self.llm(
            prompt,
            max_tokens=256,
            temperature=0.8,
            stop=["</monster>"]
        )
        return response
```

#### **Image Generation Integration**

**ComfyUI for Image Generation**
- **Workflow-Based Generation:** Visual node-based image creation pipelines
- **API Server:** REST API for programmatic image generation
- **Model Management:** Support for various Stable Diffusion models
- **Batch Processing:** Efficient generation of multiple monster images

**Integration Considerations:**
- **Standalone Application:** ComfyUI runs as separate service
- **API Communication:** HTTP requests for image generation
- **File Management:** Generated images stored and served efficiently
- **Error Handling:** Graceful degradation when image generation fails

*Note: ComfyUI dependency may prevent standalone application deployment*

### Development Environment

#### **Version Control**
- **Git:** Source code management and collaboration
- **GitHub:** Remote repository hosting and issue tracking
- **Branching Strategy:** Feature branches for development, main branch for stable releases

#### **Package Management**
- **pip/virtualenv:** Python dependency management and isolation
- **npm:** Node.js package management for frontend dependencies
- **requirements.txt:** Python dependency specification
- **package.json:** Node.js dependency and script management

#### **Development Tools**
- **VS Code:** Primary development environment with Python and React extensions
- **Postman:** API endpoint testing and documentation
- **MySQL Workbench:** Database design and management
- **Browser DevTools:** Frontend debugging and performance analysis

## System Architecture Patterns

### **Model-View-Controller (MVC) Pattern**

**Backend MVC Structure:**
```
models/
├── monster.py          # Monster data models
├── player.py           # Player data models
├── game_state.py       # Game state management
└── database.py         # Database connection and ORM

views/ (routes/)
├── api_monsters.py     # Monster-related endpoints
├── api_game.py         # Game state endpoints
├── api_chat.py         # Chat system endpoints
└── api_dungeon.py      # Dungeon exploration endpoints

controllers/ (services/)
├── monster_service.py  # Monster business logic
├── battle_service.py   # Combat system logic
├── llm_service.py      # AI integration logic
└── game_service.py     # Core game mechanics
```

### **Service-Oriented Architecture (SOA)**

**Microservice Separation:**
- **Game Logic Service:** Core gameplay mechanics and rules
- **LLM Service:** AI text generation and processing
- **Image Service:** Monster artwork generation and management
- **Database Service:** Data persistence and retrieval
- **Authentication Service:** Player session management (future)

### **Event-Driven Architecture**

**Game Event System:**
```python
class GameEventManager:
    def __init__(self):
        self.listeners = {}
    
    def emit(self, event_type, data):
        for listener in self.listeners.get(event_type, []):
            listener(data)
    
    def on(self, event_type, callback):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)

# Usage examples:
# events.emit('monster_captured', monster_data)
# events.emit('battle_won', battle_results)
# events.emit('monster_evolved', evolution_data)
```

## Data Architecture

### **Database Schema Design**

**Entity Relationship Overview:**
```
Players 1:M PlayerMonsters M:1 MonsterTemplates
PlayerMonsters 1:M MonsterChats
PlayerMonsters M:M Abilities (through MonsterAbilities)
Players 1:M PlayerInventory M:1 Items
Players 1:M GameSaves
```

### **Data Flow Patterns**

**Read Operations:**
```
Frontend Request → Flask Route → Service Layer → Database → Response
```

**Write Operations:**
```
Frontend Action → Flask Route → Business Logic → Database Transaction → Event Emission
```

**AI Integration Flow:**
```
Game Event → LLM Service → Prompt Processing → Model Inference → Result Processing → Database Update
```

## Performance Considerations

### **Backend Optimization**
- **Database Indexing:** Optimized queries for frequently accessed data
- **Connection Pooling:** Efficient database connection management
- **Caching Strategy:** Redis integration for frequently accessed game data (future enhancement)
- **Lazy Loading:** On-demand loading of monster details and images

### **Frontend Optimization**
- **Component Optimization:** React.memo for preventing unnecessary re-renders
- **Code Splitting:** Dynamic imports for large components
- **Asset Optimization:** Compressed images and minified JavaScript
- **Virtual Scrolling:** Efficient rendering of large monster collections

### **AI Performance**
- **Model Optimization:** Quantized models for faster inference
- **Batch Processing:** Group similar AI requests for efficiency
- **Async Processing:** Non-blocking AI operations with progress indicators
- **Fallback Systems:** Graceful degradation when AI services are unavailable

## Security Architecture

### **Data Protection**
- **Input Validation:** Sanitization of all user inputs
- **SQL Injection Prevention:** Parameterized queries and ORM usage
- **XSS Protection:** Output encoding and Content Security Policy
- **Local Data Only:** No external data transmission for privacy

### **API Security**
- **Rate Limiting:** Prevent abuse of AI generation endpoints
- **Request Validation:** Schema validation for all API requests
- **Error Handling:** Secure error messages that don't leak system information
- **Session Management:** Secure player session handling

## Deployment Architecture

### **Development Environment**
```
localhost:3000  → React Development Server
localhost:5000  → Flask Application Server
localhost:3306  → MySQL Database Server
localhost:8188  → ComfyUI API Server
localhost:8080  → LLM Inference Server
```

### **Production Considerations (Future)**
- **Containerization:** Docker containers for consistent deployment
- **Load Balancing:** Multiple application instances for scalability
- **Database Clustering:** High availability database configuration
- **CDN Integration:** Fast asset delivery for global users

## MVP Architecture Simplifications

For the initial MVP, the architecture is simplified:

### **Reduced Complexity**
- **Single Server Deployment:** All services on local development machine
- **Simplified AI Integration:** Basic LLM calls without complex orchestration
- **File-Based Configuration:** Simple configuration management
- **Local Storage Only:** No cloud or external service dependencies

### **Development Priorities**
1. **Core Game Loop:** Home → Dungeon → Battle → Return cycle
2. **Basic AI Integration:** Monster generation and chat functionality
3. **Data Persistence:** Save/load game state
4. **UI Functionality:** All core screens working smoothly

### **Enhancement Roadmap**
- **Advanced AI Orchestration:** Complex prompt chaining and context management
- **Performance Optimization:** Caching, optimization, and scaling improvements
- **Feature Expansion:** Additional game mechanics and content types
- **Production Deployment:** Cloud hosting and distribution capabilities

## Technology Rationale

### **Flask vs Alternatives**
- **Django:** Too heavyweight for game-focused application
- **FastAPI:** Less mature ecosystem, overkill for current requirements
- **Node.js:** Python chosen for better AI library integration

### **React vs Alternatives**
- **Vue.js:** React ecosystem better suited for complex interactive UIs
- **Angular:** Too heavyweight for single-page game application
- **Vanilla JS:** React provides better component organization and state management

### **MySQL vs Alternatives**
- **PostgreSQL:** MySQL adequate for current requirements, simpler setup
- **SQLite:** Insufficient for future multi-user considerations
- **NoSQL:** Relational data model fits game entity relationships well

---

**Related Documents:**
- [Requirements Document](requirements.md)
- [MVP Development Strategy](../strategy/mvp_development_strategy.md)
- [UI Design](ui_design.md)
# LLM Monster Hunter Game

![Project Header](docs/assets/images/moodboard/header_image.png)

*An AI-powered monster-catching adventure where every creature has a story to tell*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React 18+](https://img.shields.io/badge/react-18+-61dafb.svg)](https://reactjs.org/)
[![Flask 3.0](https://img.shields.io/badge/flask-3.0-green.svg)](https://flask.palletsprojects.com/)

## 🎮 **What is This?**

A revolutionary text-based monster-catching game that leverages **Large Language Models (LLMs)** to create truly unique creatures. Every monster you encounter is generated from scratch with its own personality, backstory, abilities, and motivations. Chat with them, earn their trust, and watch them evolve based on your interactions.

**This isn't just a game—it's a demonstration of AI in interactive entertainment.**

## 🚀 **Quick Start**

### Prerequisites (Install BEFORE running setup)

#### ✅ **Required Software:**
1. **Python 3.8+** - [Download from python.org](https://www.python.org/downloads/)
2. **Node.js 16+** - [Download from nodejs.org](https://nodejs.org/) 
   - ✅ npm comes included with Node.js
3. **MySQL Server** - [Download MySQL Community Server](https://dev.mysql.com/downloads/mysql/)
   - ⚠️ **Important:** MySQL Workbench is just the GUI - you need the actual server
   - 💡 During installation, remember your root password!
4. **Git** - [Download from git-scm.com](https://git-scm.com/downloads)

#### 🎯 **For CUDA Support (Recommended for AI features):**
5. **NVIDIA GPU Drivers** - [Download latest drivers](https://www.nvidia.com/drivers/)
6. **CUDA Toolkit** - [Download CUDA 12.x](https://developer.nvidia.com/cuda-toolkit)
7. **Visual Studio Build Tools** - [Download Build Tools](https://visualstudio.microsoft.com/downloads/)
   - Install the "C++ build tools" workload

#### 🔧 **Hardware Requirements:**
- **NVIDIA GPU** with 8GB+ VRAM (for AI model acceleration)
- **32GB RAM** recommended (16GB minimum)
- **10GB+ free storage**

### Installation Steps

Installation steps need to be added here. Make sure to mention that start_game bat helps you setup the enviroment, check if everything is set up correctly and can be ran multiple times safely.

🎉 **The game will be available at `http://localhost:3000`**


### Troubleshooting

#### **What are Node.js and npm?**
- **Node.js:** A JavaScript runtime that lets you run JavaScript outside web browsers
- **npm:** Node Package Manager - comes with Node.js, manages JavaScript libraries
- **Why we need them:** React frontend is built with JavaScript and needs these tools
- **To verify:** Run `node --version` and `npm --version` in command prompt

## ✨ **Key Features**

### 🤖 **AI-Powered Everything**
- **Dynamic Monster Generation:** Every creature created by LLM with unique personality
- **Evolving Conversations:** Chat with monsters and influence their development
- **Procedural Storytelling:** Emergent narratives based on your choices and relationships
- **AI-Generated Artwork:** Custom images for each monster using ComfyUI

### 🎯 **Strategic Gameplay**
- **Turn-Based Combat:** Tactical battles where monster personalities affect fighting styles
- **Monster Recruitment:** Convince creatures to join your party through conversation
- **Dungeon Exploration:** Navigate procedurally generated encounters and challenges
- **Evolution System:** Watch your monsters grow and change based on their experiences


## 🏗️ **Project Architecture**

### Tech Stack
- **Backend:** Python 3.8+, Flask 3.0, MySQL 8.0
- **Frontend:** React 18+, HTML5, CSS3, JavaScript ES6+
- **AI Integration:** llama-cpp-python, ComfyUI
- **Development:** Git, VS Code, npm/pip

### System Overview
```
React Frontend ←→ Flask API ←→ MySQL Database
                     ↓
              LLM Services (Local)
                     ↓
              ComfyUI (Image Gen)
```

## 📚 **Documentation**

This project includes comprehensive documentation following SDLC methodology:

### 📋 **Core Documents**
- **[MVP Development Strategy](docs/strategy/mvp_development_strategy.md)** - Current development approach
- **[Technical Architecture](docs/design/technical_architecture.md)** - System design and implementation

### 🗂️ **Full Documentation Structure**
```
docs/
├── planning/           # Project planning and feasibility analysis
├── design/            # System design and architecture
├── use_cases/         # Detailed use case specifications
├── strategy/          # Development methodology and MVP approach
└── assets/           # Images, diagrams, and mockups
```

## 🎯 **Current Status: MVP Development**

**Development Phase:** Rapid Prototyping (June 2025)  
**Methodology:** MVP-First Development after comprehensive planning

Development status needs to be updated!
### ✅ **Completed**
- [x] Complete SDLC planning documentation (February 2025)
- [x] Feasibility analysis and risk assessment
- [x] Technical architecture design
- [x] Database schema design
- [x] MVP scope definition and strategy pivot

### 🔄 **In Progress**
- [ ] Flask backend implementation
- [ ] Basic LLM integration
- [ ] Core game loop development
- [ ] React frontend components

### 🎯 **MVP Goals**
- Home base monster and inventory management
- Simple dungeon exploration with three-door choice system
- Turn-based battle system with basic actions
- Monster chat system with personality responses
- Basic monster generation and capture mechanics

## 🎮 **Gameplay Preview**

### Core Game Loop
1. **Home Base** - Manage your monster party and inventory
2. **Enter Dungeon** - Choose from three mysterious doors
3. **Encounter** - Face monsters, traps, treasures, or exits
4. **Battle** - Strategic turn-based combat with unique creatures
5. **Chat & Recruit** - Convince monsters to join your party
6. **Return & Evolve** - Develop your monsters and prepare for the next adventure

### What Makes It Special
Every monster you meet has been created by AI with:
- **Unique Personality** - Distinct speaking patterns and motivations
- **Personal Backstory** - Individual history and goals
- **Dynamic Abilities** - Skills that reflect their character
- **Evolution Potential** - Growth based on experiences and relationships

## 🎓 **Educational Objectives**

This is a personal project of mine and serves as a capstone demonstrating:

### **Academic Application**
- **CSUF Information Systems & Data Science** degree knowledge
- **SDLC Methodology** with complete documentation deliverables
- **Database Design** with complex relational structures
- **Systems Analysis** through comprehensive use cases

### **Professional Skills Development**
- **Full-Stack Development** - Python backend, React frontend
- **AI Integration** - Local LLM inference and prompt engineering
- **Project Management** - Adaptive methodology and scope management
- **Technical Documentation** - Professional-grade system documentation

### **Portfolio Demonstration**
- **Innovation** - Novel application of AI in gaming
- **Technical Depth** - Complex system with multiple integrated technologies
- **Adaptability** - Methodology pivot based on practical learning
- **Completion Focus** - MVP approach ensuring deliverable results

## 🤝 **Contributing**

This is primarily an educational and portfolio project, but feedback and suggestions are welcome!

### **Development Principles**
- **Documentation First** - Comprehensive planning and analysis
- **MVP Focus** - Working software over perfect features
- **Learning Oriented** - Educational value prioritized
- **AI Integration** - Practical application of LLM technology

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Open Source Community** - Flask, React, and AI model ecosystems
- **AI Research Community** - LLM advancement enabling this type of application

## **Contact**

**Aaron Orelup**  
📧 Email: Aaronjorelup@gmail.com
📞 Text(best): (510) 695-1134 

---

**Ready to catch some AI-generated monsters?** 🐉✨

*This project represents the intersection of traditional game design, modern web development, and cutting-edge AI technology - built as a demonstration of practical skills and innovative thinking.*
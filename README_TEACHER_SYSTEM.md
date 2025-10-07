# Humanoid Teaching Assistant - Complete System Guide

## Overview

This project implements a comprehensive humanoid teaching assistant with the following key features:

1. **Animated Avatar**: Cartoon-like character with moving mouth, eyes, and expressions
2. **Teaching-Focused AI**: Specialized prompts designed for educational interactions with children
3. **Teacher Interface**: GUI for teachers to create custom learning modules
4. **Custom Games**: Interactive learning activities with multiple input methods
5. **Integrated System**: Seamless integration between all components

## System Architecture

```
Capstone/
├── py_app.py                    # Main teaching assistant application
├── chatbot_logic.py             # Core AI logic with teaching enhancements
├── avatar_system.py             # Animated avatar system
├── teaching_prompts.py          # Teaching-focused AI prompts
├── game_manager.py              # Unified game management system
├── module_executor.py           # Custom teaching module execution
├── teacher_interface.py         # Teacher GUI for creating modules
├── launch_teacher_interface.py  # Easy launcher for teachers
├── image detector/              # Interactive games directory
│   ├── detector.py              # Placard detection system
│   ├── finger_counting_game.py  # Finger counting educational game
│   ├── healthyVSjunk.py         # Healthy food classification game
│   ├── fruits_vs_vegetables.py  # Fruits vs vegetables game (example)
│   ├── main_ui.py               # Games menu interface
│   └── fingers_counting_trails.py # Hand tracking for finger counting
├── backend/                     # RAG system and TTS
├── docs/                        # Documentation files
├── animations/                  # Avatar animation GIFs (optional)
├── teaching_modules/            # Teacher-created modules storage
├── active_modules/              # Deployed modules
└── sounds/                      # Audio files for games
```

## Features Implemented from Meeting Requirements

### ✅ 1. Animated Teaching Assistant
- **Cartoon-like Avatar**: Programmatically generated character with moving mouth, eyes, and expressions
- **State-based Animation**: Different animations for idle, listening, thinking, and speaking
- **Fallback System**: Works with or without external animation files

### ✅ 2. Teaching-Focused AI
- **Educational Prompts**: Specialized prompting system that makes the AI behave like a patient teacher
- **Subject Detection**: Automatically detects math, science, health, reading topics
- **Encouraging Language**: Uses positive reinforcement and child-friendly language
- **Interactive Suggestions**: Suggests relevant educational activities

### ✅ 3. Teacher Interface for Module Creation
- **GUI Application**: Easy-to-use interface for teachers to create learning modules
- **Module Configuration**: Set title, subject, difficulty, interaction methods
- **Content Creation**: Add questions, activities, and learning objectives
- **Resource Upload**: Upload images and files for use in activities
- **Deployment System**: Deploy modules directly to the teaching assistant

### ✅ 4. Customizable Games and Input Methods

#### Available Input Methods:
- **Voice Response**: Child speaks their answer
- **Finger Counting**: Child shows fingers for number recognition
- **Placard System**: Child shows GREEN (Yes) or RED (No) cards
- **Multiple Choice**: Child selects from options

#### Available Game Types:
- **Classification Games**: Right/Wrong activities (like fruits vs vegetables)
- **Counting Games**: Number recognition and finger counting
- **Memory Games**: Recall and recognition activities
- **Quiz Games**: Question and answer format

### ✅ 5. Fruits vs Vegetables Example
- **Custom Game**: Example implementation as requested in the meeting
- **Image Upload**: Teachers can upload their own fruit and vegetable images
- **Placard Input**: Uses GREEN/RED placard detection for Yes/No responses
- **Configurable**: Questions and images can be customized through teacher interface

### ✅ 6. Integrated Placard Detection
- **Real-time Detection**: Uses camera to detect colored placards
- **Visual Feedback**: Shows detection progress and confirmation
- **Robust System**: Works with various lighting conditions
- **User-Friendly**: Clear instructions and visual indicators

## Quick Start Guide

### For Teachers: Creating Custom Learning Modules

1. **Launch Teacher Interface**:
   ```bash
   python launch_teacher_interface.py
   ```

2. **Create a New Module**:
   - Fill in basic information (title, subject, difficulty)
   - Choose interaction method (voice, placard, fingers)
   - Select game type (classification, counting, quiz)
   - Add questions and activities
   - Upload relevant images/resources

3. **Example: Fruits vs Vegetables Module**:
   - Title: "Fruit or Vegetable Classification"
   - Subject: Health
   - Interaction: Placard (Yes/No)
   - Game Type: Classification
   - Upload fruit and vegetable images
   - Add questions like "Is this a fruit?"

4. **Deploy Module**:
   - Save the module
   - Go to "Manage Modules" tab
   - Click "Deploy to Bot" for your module

### For Students: Using the Teaching Assistant

1. **Start the Main Application**:
   ```bash
   python py_app.py
   ```

2. **Interact with Jarvis**:
   - Say "Hey Jarvis" to activate
   - Ask questions about math, science, health, etc.
   - Request games: "I want to play a counting game"
   - Follow instructions for placard/finger input

3. **Access Games**:
   - Say "show me games" or "launch games menu"
   - Choose from available educational activities
   - Follow on-screen instructions for each game

## Installation Requirements

### Required Python Packages:
```bash
pip install PyQt6 opencv-python numpy pygame mediapipe torch scipy inflect
```

### Optional Dependencies (for full functionality):
```bash
pip install anthropic  # For advanced AI features
```

### Hardware Requirements:
- **Camera**: Required for placard detection and finger counting
- **Microphone**: Required for voice interaction
- **Speakers**: Required for TTS output

## System Configuration

### 1. Setting up the RAG System
- Place educational documents in the `docs/` folder
- The system will automatically ingest PDF, DOCX, PPTX, and TXT files
- Documents are used to provide accurate educational responses

### 2. Configuring Games
- Games are automatically detected in the `image detector/` directory
- New games can be added by following the existing game structure
- Update `game_manager.py` to register new games

### 3. Avatar Customization
- Default programmatic avatar works out of the box
- Optional: Add custom GIF animations in the `animations/` folder
- Supported: `idle.gif`, `listening.gif`, `thinking.gif`, `speaking.gif`

## Usage Examples

### Example 1: Creating a Colors Learning Module

1. **Teacher Interface**:
   - Title: "Learn Basic Colors"
   - Subject: General
   - Input Method: Voice Response
   - Questions: "What color is this?", "Name a red object"
   - Upload colored object images

2. **Student Experience**:
   - Jarvis shows colored objects
   - Student says the color name
   - Positive feedback for correct answers
   - Encouragement for incorrect attempts

### Example 2: Math Counting Activity

1. **Teacher Interface**:
   - Title: "Count Objects 1-5"
   - Subject: Math
   - Input Method: Finger Counting
   - Upload images with different quantities of objects

2. **Student Experience**:
   - Jarvis shows image with objects
   - Student holds up corresponding number of fingers
   - Camera detects finger count
   - Immediate feedback and progression

## Troubleshooting

### Common Issues:

1. **Camera not working**:
   - Check camera permissions
   - Ensure camera is not used by other applications
   - Try different camera index in the code

2. **Microphone not detecting**:
   - Check microphone permissions
   - Verify microphone is working in system settings
   - Check audio device configuration

3. **Teacher interface not launching**:
   - Run `python launch_teacher_interface.py` for automatic setup
   - Check all dependencies are installed
   - Ensure you're in the correct directory

4. **Games not loading**:
   - Check that `image detector` directory exists
   - Verify all game files are present
   - Check file permissions

5. **Module not deploying**:
   - Ensure `active_modules` directory exists
   - Check module file format (should be valid JSON)
   - Verify module has required fields

## Advanced Configuration

### Customizing AI Responses
Edit `teaching_prompts.py` to modify:
- Subject-specific teaching styles
- Encouragement phrases
- Question starters
- Response formatting

### Adding New Input Methods
1. Extend `detector.py` with new detection logic
2. Update game templates to handle new input type
3. Add configuration options in teacher interface

### Creating New Game Types
1. Create new game script in `image detector/` directory
2. Follow existing game structure and UI patterns
3. Register in `game_manager.py`
4. Add to `main_ui.py` menu

## Project Structure Details

### Core Components:

- **py_app.py**: Main PyQt6 application with STT/TTS integration
- **chatbot_logic.py**: Enhanced with teaching prompts and module support
- **avatar_system.py**: Programmatic cartoon avatar with animations
- **teacher_interface.py**: Complete GUI for teachers to create modules

### Game System:

- **game_manager.py**: Unified management of all educational games
- **module_executor.py**: Runs custom teacher-created modules
- **detector.py**: Computer vision for placard and gesture detection

### Educational Content:

- **teaching_prompts.py**: Age-appropriate language and teaching strategies
- **Teaching modules**: JSON-based custom learning activities
- **Resource management**: Image and file handling for activities

## Future Enhancements

Potential improvements that could be added:

1. **Advanced Avatar**: 3D character with lip-sync
2. **More Input Methods**: Gesture recognition, eye tracking
3. **Assessment System**: Track student progress over time
4. **Multiplayer Mode**: Collaborative learning activities
5. **Voice Synthesis**: Custom voices for different characters
6. **Content Library**: Pre-built educational modules
7. **Analytics Dashboard**: Teacher insights into student performance

## Meeting Requirements Summary

This implementation addresses all the key points from your project meeting:

✅ **Animated Teaching Assistant**: Cartoon-like avatar with moving mouth and expressions  
✅ **Teaching-Focused**: AI behaves like a teacher, not just a chatbot  
✅ **Teacher Interface**: Complete GUI for creating and managing learning modules  
✅ **Customizable Games**: Multiple game types with different interaction methods  
✅ **Fruits vs Vegetables Example**: Working implementation with placard input  
✅ **Limited Scope**: Focused on 3-4 core games as requested  
✅ **Educational Value**: All activities designed for child learning and engagement

The system is ready for your midsem evaluation and demonstrates a complete, working educational technology solution that teachers can use to create engaging learning experiences for children.
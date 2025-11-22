# Grade 1 Learning Platform

## Overview
An educational platform designed for Grade 1 children (ages 6-7) to learn English and Math. Teachers upload lecture content, which is automatically summarized by AI into child-friendly text. Students read the summaries and take quizzes to test their understanding.

## Purpose
- Help Grade 1 students learn English and Math through simplified, AI-generated summaries
- Allow teachers to create engaging content and quizzes
- Provide immediate feedback with score calculation and answer reviews

## Features
### Teacher Features
- Upload lectures with title, subject (Math/English), and content
- AI automatically generates child-friendly summaries using Hugging Face API
- Create quizzes with up to 10 questions per lecture
- View all lectures and quizzes in organized dashboard

### Student Features
- Browse available lectures by subject
- Read AI-generated summaries designed for Grade 1 comprehension level
- Take quizzes after reading lectures
- View scores and detailed answer reviews
- Bright, playful interface optimized for young children

## Tech Stack
### Frontend
- React with TypeScript
- Wouter for routing
- TanStack Query for data fetching
- Shadcn UI components
- Tailwind CSS
- Fredoka font for child-friendly typography

### Backend
- Express.js
- In-memory storage (MemStorage)
- Hugging Face Inference API for text summarization
- Model: facebook/bart-large-cnn

## Design System
Following design_guidelines.md:
- **Primary Colors**: Sky blue (#3B97D3), bright green, warm orange
- **Typography**: Fredoka for student UI (large, rounded), Inter for teacher UI
- **Text Sizes**: text-2xl for student content (high readability)
- **Touch Targets**: Minimum 56px (h-14) for all interactive elements
- **Spacing**: Generous padding and margins for breathing room
- **Contrast**: WCAG AAA for young learners

## Project Structure
```
client/src/
  pages/
    student-dashboard.tsx - Student home page with lecture cards
    teacher-dashboard.tsx - Teacher management interface
    lecture-view.tsx - Display lecture summary and quiz link
    quiz-taking.tsx - Interactive quiz interface
    quiz-results.tsx - Score display and answer review
  components/
    lecture-upload.tsx - Modal for creating lectures
    quiz-builder.tsx - Modal for creating quizzes
shared/
  schema.ts - Data models for lectures, quizzes, questions, submissions
server/
  routes.ts - API endpoints
  storage.ts - In-memory data storage
```

## API Endpoints
- GET /api/lectures - Fetch all lectures
- GET /api/lectures/:id - Fetch single lecture
- POST /api/lectures - Create lecture (triggers AI summarization)
- GET /api/quizzes - Fetch all quizzes
- GET /api/quizzes/:id - Fetch single quiz
- GET /api/quizzes/:id/questions - Fetch questions for quiz
- POST /api/quizzes - Create quiz with questions
- POST /api/submissions - Submit quiz answers, calculate score
- GET /api/submissions/:id - Fetch submission with review data

## Recent Changes
- 2025-01-XX: Initial project setup with schema and all frontend components
- Implemented teacher dashboard with lecture and quiz management
- Created student-facing interface with large text and playful design
- Built quiz-taking flow with progress tracking
- Added comprehensive results page with answer review

## User Preferences
- Free AI summarization using Hugging Face instead of paid APIs
- Child-friendly design with large text and bright colors
- Maximum 10 questions per quiz
- Simple, intuitive navigation for young students

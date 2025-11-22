# BudgetBridge

A full‑stack app for creating Grade‑1 friendly study material:
- Teachers add lectures (text) and get an AI summary.
- Generate multiple‑choice quizzes from a lecture with AI.
- Students can take quizzes; scores are stored and retrievable.

This repo includes:
- Client (Vite + React + Tailwind + shadcn/ui + React Query)
- Server (Express + TypeScript + Vite middleware)
- AI via Groq API
- Storage: In‑memory by default, optional MongoDB persistence via Mongoose

---

## Quick Start

Prerequisites:
- Node.js 18+
- npm
- Optional: MongoDB Atlas (or any MongoDB) if you want persistence

Install deps (run at project root):

```
npm install
```

Run dev server (Express + Vite):

```
npm run dev
```

Then open:
- App: http://localhost:5000

You should see server logs such as:
- "[storage] backend: In-Memory" or "MongoDB (Mongoose)"
- "[mongo] connected (db: <name>)" when using MongoDB

---

## Environment Variables

Create a file named `.env` in the project root or `server/.env` with:

- GROQ_API_KEY=<your_groq_api_key>
  - Required for AI summary and quiz generation (Groq Chat Completions API)
- MONGODB_URI=<your_mongodb_connection_string>
  - Optional; if set the app uses MongoDB via Mongoose; otherwise in‑memory storage is used
- PORT=5000
  - Optional; default is 5000

Examples:

```
# server/.env
GROQ_API_KEY=sk-...
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/mydb?retryWrites=true&w=majority&appName=Cluster0
PORT=5000
```

Notes:
- The server attempts to load env from multiple locations (project root and server/.env).
- On startup you’ll see which storage backend is active.

---

## Scripts

- npm run dev
  - Starts the Express server with Vite in middleware mode (development)
- npm run build
  - Builds the client for production (if configured)
- npm run preview
  - Runs a production preview server (if configured)

---

## Features

- Add lectures with title/subject/content
  - Server generates a Grade‑1 friendly summary using Groq
- Generate quiz questions from lecture content with AI
  - 5 multiple‑choice questions by default
- Create quizzes (persist to DB if Mongo is enabled)
- Take quizzes and view results

---

## API Overview (server)

Base URL: http://localhost:5000

- GET /api/lectures
- GET /api/lectures/:id
- POST /api/lectures
  - Body: { title, subject, content }
  - Auto‑summarized on the server
- PATCH /api/lectures/:id
- DELETE /api/lectures/:id

- GET /api/quizzes
- GET /api/quizzes/:id
- GET /api/quizzes/:id/questions
- POST /api/quizzes
  - Body: { quizTitle, lectureId, questions: InsertQuestion[] }
- PATCH /api/quizzes/:id
- DELETE /api/quizzes/:id
- POST /api/quizzes/generate
  - Body: { lectureId, count? }
  - Returns: Generated questions from AI

- POST /api/submissions
  - Body: { quizId, studentName, answers }
- GET /api/submissions/:id

See `server/routes.ts` for details.

---

## Data & Storage

Two storage modes are available (auto‑selected on startup):

- In‑Memory (default)
  - No persistence; resets on server restart
- MongoDB via Mongoose (set `MONGODB_URI`)
  - Collections: Lecture, Quiz, Question, Submission
  - We use UUID `id` fields to keep API stable
  - Connection logs:
    - [mongo] connecting / connected / disconnected / error

---

## AI Integration

- File: `server/huggingface.ts`
- Endpoints call Groq Chat Completions API for:
  - Summaries: `summarizeForGrade1(text)`
  - Quiz generation: `generateQuizQuestions(text, count)`
- Logs include input prompt and truncated content/response for debugging

---

## Troubleshooting

- "Waiting for MongoDB connection..." and stuck:
  - Check `MONGODB_URI` value and Atlas network access (IP allowlist)
  - We log errors under `[mongo] connection error:`
  - A 7‑second fallback prevents indefinite hanging and continues startup
- No AI output:
  - Verify `GROQ_API_KEY`
  - Check console for Groq API error logs
- Only 4 questions generated:
  - We normalize/keep questions even if AI outputs an out‑of‑range `correctAnswer`.
  - Review questions in the UI and adjust correct answer if needed.

---

## Project Structure (high level)

```
client/                     # React app (Vite)
server/
  index.ts                  # Express app entry
  routes.ts                 # REST endpoints
  storage.ts                # Storage (in‑memory or Mongo via Mongoose)
  huggingface.ts            # AI calls and normalization
shared/
  schema.ts                 # Shared types (Zod)
```

---

## Contributing

- Create a feature branch, keep PRs focused.
- Follow existing code style; TypeScript across server and client.

---

## License

MIT

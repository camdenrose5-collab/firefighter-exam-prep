# 🔥 Firefighter Exam Prep

A RAG-powered study platform for firefighter written exam preparation.

**Live at:** [firefighterhire.com](https://firefighterhire.com)

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Google Cloud project with Vertex AI enabled

### Frontend (Next.js)
```bash
npm install
npm run dev
# Open http://localhost:3000
```

### Backend (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

## Environment Setup

1. Copy example files:
```bash
cp .env.development.example .env.development
cp .env.production.example .env.production
```

2. Fill in your Google Cloud credentials

## Features

- **Quiz Engine** - 1,200+ pre-generated questions across 4 subjects
- **Study Deck** - Save questions for personalized review
- **Flashcards** - AI-generated term/definition cards
- **Fire Captain AI** - Tutoring with firehouse analogies

## Deployment

Deploy backend to Google Cloud Run:
```bash
./deploy.sh
```

## API Docs

Backend API documentation available at `/docs` when running.

## Tech Stack

- **Frontend:** Next.js 16, React 19, Tailwind CSS
- **Backend:** FastAPI, SQLite, ChromaDB
- **AI:** Vertex AI (Gemini 2.0 Flash), Discovery Engine

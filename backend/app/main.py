"""
Firefighter Exam Prep - FastAPI Backend
Main application entry point with CORS and API routes.
"""

import os
import uuid
from pathlib import Path
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from app.ingestion import PDFIngestionPipeline
from app.rag_engine import RAGEngine
from app.features.captains_review import CaptainsReviewFeature
from app.features.quiz_engine import create_quiz_engine, FireCaptainQuizEngine
from app.features.tutor import create_tutor_engine, FireCaptainTutor
from app import db
from app.auth import (
    hash_password, verify_password, create_session, 
    get_user_from_token, invalidate_session
)

# Load environment variables
load_dotenv()

# Initialize components
ingestion_pipeline: PDFIngestionPipeline = None
rag_engine: RAGEngine = None
captains_review: CaptainsReviewFeature = None
quiz_engine: FireCaptainQuizEngine = None
tutor_engine: FireCaptainTutor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize components on startup."""
    global ingestion_pipeline, rag_engine, captains_review, quiz_engine, tutor_engine

    
    # Setup paths
    base_dir = Path(__file__).parent.parent
    upload_dir = base_dir / "data" / "uploads"
    chroma_dir = base_dir / "data" / "chroma_db"
    
    upload_dir.mkdir(parents=True, exist_ok=True)
    chroma_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize pipeline components
    ingestion_pipeline = PDFIngestionPipeline(
        upload_dir=str(upload_dir),
        chroma_dir=str(chroma_dir),
    )
    
    rag_engine = RAGEngine(chroma_dir=str(chroma_dir))
    captains_review = CaptainsReviewFeature(rag_engine=rag_engine)
    
    # Initialize Fire Captain Quiz Engine (gracefully handles missing creds)
    quiz_engine = create_quiz_engine()
    
    # Initialize Fire Captain Tutor Engine
    tutor_engine = create_tutor_engine()
    
    print("🔥 Firefighter Exam Prep backend initialized!")
    yield
    print("👋 Shutting down...")


app = FastAPI(
    title="Firefighter Exam Prep API",
    description="RAG-powered study assistant for firefighter certification exams",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Request/Response Models ==============

class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    chunks_count: int


class ReviewRequest(BaseModel):
    question: str
    answer: str
    document_ids: List[str]


class Citation(BaseModel):
    source: str
    page: int | None = None
    excerpt: str


class ReviewResponse(BaseModel):
    grade: str  # "correct", "partial", "incorrect"
    feedback: str
    textbook_answer: str
    citations: List[Citation]


class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo]


class QuizRequest(BaseModel):
    topic: str


class QuizResponse(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str


class ReportRequest(BaseModel):
    question_id: str
    reason: str | None = None


class TutorRequest(BaseModel):
    subject: str  # e.g., "fractions" or "hydraulics"
    user_input: str  # The specific question or "I'm stuck"


class TutorResponse(BaseModel):
    explanation: str


class FlashcardResponse(BaseModel):
    term: str
    definition: str
    source: str | None = None


# Auth Models
class RegisterRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user_id: str
    email: str


class UserResponse(BaseModel):
    user_id: str
    email: str


# Study Deck Models
class StudyDeckAddRequest(BaseModel):
    question_id: str


# Question Bank Models
class QuestionBankRequest(BaseModel):
    subjects: List[str]
    count: int = 10
    study_deck_ratio: float = 0.0  # 0.0-1.0


class QuestionBankResponse(BaseModel):
    questions: List[QuizResponse]


# ============== API Endpoints ==============

@app.get("/")
async def root():
    return {"message": "🔥 Firefighter Exam Prep API", "status": "operational"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "rag_ready": rag_engine is not None}


# ============== AUTH ENDPOINTS ==============

@app.post("/api/auth/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register a new user account."""
    if not request.email or not request.password:
        raise HTTPException(status_code=400, detail="Email and password required")
    
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    # Check if user already exists
    existing = db.get_user_by_email(request.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    try:
        password_hash = hash_password(request.password)
        user_id = db.create_user(request.email, password_hash)
        token = create_session(user_id, request.email)
        
        return AuthResponse(token=token, user_id=user_id, email=request.email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@app.post("/api/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login with email and password."""
    user = db.get_user_by_email(request.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_session(user["id"], user["email"])
    return AuthResponse(token=token, user_id=user["id"], email=user["email"])


@app.post("/api/auth/logout")
async def logout(token: str):
    """Logout and invalidate session."""
    invalidate_session(token)
    return {"status": "logged_out"}


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user(token: str):
    """Get current user from token."""
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return UserResponse(user_id=user["user_id"], email=user["email"])


# ============== QUESTION BANK ENDPOINTS ==============

@app.post("/api/quiz/bank", response_model=QuestionBankResponse)
async def get_questions_from_bank(request: QuestionBankRequest, token: str = ""):
    """
    Fetch quiz questions from pre-generated bank.
    Optionally mix in questions from user's study deck.
    """
    questions = []
    
    # Calculate how many from study deck vs bank
    study_deck_count = 0
    bank_count = request.count
    
    if request.study_deck_ratio > 0 and token:
        user = get_user_from_token(token)
        if user:
            study_deck_count = int(request.count * request.study_deck_ratio)
            bank_count = request.count - study_deck_count
            
            # Get questions from study deck
            deck_questions = db.get_study_deck_questions(user["user_id"], study_deck_count)
            for q in deck_questions:
                questions.append(QuizResponse(
                    question=q["question"],
                    options=q["options"],
                    correct_answer=q["correct_answer"],
                    explanation=q["explanation"]
                ))
    
    # Get remaining questions from bank
    if bank_count > 0:
        bank_questions = db.get_random_questions(request.subjects, bank_count)
        for q in bank_questions:
            questions.append(QuizResponse(
                question=q["question"],
                options=q["options"],
                correct_answer=q["correct_answer"],
                explanation=q["explanation"]
            ))
    
    # If bank is empty, fall back to live generation
    if not questions:
        raise HTTPException(
            status_code=404, 
            detail="Question bank is empty. Please wait for questions to be generated."
        )
    
    return QuestionBankResponse(questions=questions)


@app.get("/api/quiz/bank/stats")
async def get_bank_stats():
    """Get question bank statistics."""
    subjects = ["human-relations", "mechanical-aptitude", "reading-ability", "math"]
    stats = {}
    for subject in subjects:
        stats[subject] = db.get_question_count(subject)
    stats["total"] = db.get_question_count()
    return stats


# ============== STUDY DECK ENDPOINTS ==============

@app.get("/api/study-deck")
async def get_study_deck(token: str):
    """Get all questions in user's study deck."""
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    questions = db.get_study_deck(user["user_id"])
    return {"questions": questions, "count": len(questions)}


@app.post("/api/study-deck/add")
async def add_to_study_deck(request: StudyDeckAddRequest, token: str):
    """Add a question to user's study deck."""
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    try:
        entry_id = db.add_to_study_deck(user["user_id"], request.question_id)
        return {"status": "added", "entry_id": entry_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add to deck: {str(e)}")


@app.delete("/api/study-deck/{question_id}")
async def remove_from_study_deck(question_id: str, token: str):
    """Remove a question from user's study deck."""
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    removed = db.remove_from_study_deck(user["user_id"], question_id)
    if removed:
        return {"status": "removed"}
    return {"status": "not_found"}


@app.post("/api/upload", response_model=DocumentInfo)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file, extract text with MarkItDown, 
    and index chunks into ChromaDB.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        
        # Process the PDF
        result = await ingestion_pipeline.process_pdf(
            file=file,
            document_id=doc_id,
        )
        
        return DocumentInfo(
            document_id=doc_id,
            filename=file.filename,
            chunks_count=result["chunks_count"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/api/documents", response_model=DocumentListResponse)
async def list_documents():
    """List all uploaded documents."""
    try:
        docs = ingestion_pipeline.list_documents()
        return DocumentListResponse(documents=docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@app.post("/api/review", response_model=ReviewResponse)
async def submit_for_review(request: ReviewRequest):
    """
    Captain's Review: Submit a question and answer pair.
    The AI will grade the answer using RAG-retrieved context.
    """
    if not request.question.strip() or not request.answer.strip():
        raise HTTPException(status_code=400, detail="Question and answer are required")
    
    try:
        result = await captains_review.review(
            question=request.question,
            user_answer=request.answer,
            document_ids=request.document_ids,
        )
        
        return ReviewResponse(
            grade=result["grade"],
            feedback=result["feedback"],
            textbook_answer=result["textbook_answer"],
            citations=[
                Citation(
                    source=c["source"],
                    page=c.get("page"),
                    excerpt=c["excerpt"],
                )
                for c in result["citations"]
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review failed: {str(e)}")


@app.post("/api/quiz/generate", response_model=QuizResponse)
async def generate_quiz_question(request: QuizRequest):
    """
    Fire Captain Quiz: Generate a multiple-choice question on a topic.
    Uses Discovery Engine for retrieval and Vertex AI for generation.
    """
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic is required")
    
    try:
        result = await quiz_engine.generate_quiz_question(request.topic)
        return QuizResponse(
            question=result["question"],
            options=result["options"],
            correct_answer=result["correct_answer"],
            explanation=result["explanation"],
        )
    except Exception as e:
        error_msg = str(e)
        # Check for typical Google Cloud errors (404, 500 equivalent)
        if "404" in error_msg or "500" in error_msg or "ServiceUnavailable" in error_msg:
             raise HTTPException(
                status_code=503, 
                detail="The Captain is currently on a call. Please try your quiz again in a moment."
            )
        
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {error_msg}")


@app.post("/api/quiz/report")
async def report_question(request: ReportRequest):
    """
    Log a flagged question for manual review.
    Saves to database for admin review.
    """
    try:
        report_id = db.report_question(
            question_id=request.question_id,
            reason=request.reason
        )
        print(f"⚠️ [REPORT] Question {request.question_id} flagged. Report ID: {report_id}")
        return {"status": "reported", "question_id": request.question_id, "report_id": report_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reporting failed: {str(e)}")


@app.post("/api/tutor/explain", response_model=TutorResponse)
async def get_tutoring(request: TutorRequest):
    """
    Fire Captain Tutor: Get scaffolded explanation using firehouse analogies.
    Follows the 4-step pedagogical flow: Hook → Analogy → Practice → Verify
    """
    if not request.subject.strip():
        raise HTTPException(status_code=400, detail="Subject is required")
    
    try:
        explanation = await tutor_engine.explain(
            subject=request.subject,
            user_input=request.user_input or "Help me understand this"
        )
        return TutorResponse(explanation=explanation)
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "500" in error_msg or "ServiceUnavailable" in error_msg:
            raise HTTPException(
                status_code=503,
                detail="The Captain is currently on a call. Please try again in a moment."
            )
        raise HTTPException(status_code=500, detail=f"Tutoring failed: {error_msg}")


# ============== BATCH QUIZ ENDPOINT ==============

class BatchQuizRequest(BaseModel):
    topics: List[str]
    count: int = 5


class BatchQuizResponse(BaseModel):
    questions: List[QuizResponse]


@app.post("/api/quiz/batch", response_model=BatchQuizResponse)
async def generate_batch_quiz(request: BatchQuizRequest):
    """
    Generate multiple quiz questions in parallel for faster loading.
    Includes retry logic to ensure we get the requested count.
    """
    if not quiz_engine:
        raise HTTPException(status_code=503, detail="Quiz engine not initialized")
    
    import asyncio
    
    questions = []
    
    # Distribute questions across topics
    topics = request.topics if request.topics else ["General Fire Service"]
    
    async def generate_one(topic: str, attempt: int = 1):
        try:
            result = await quiz_engine.generate_quiz_question(topic)
            return QuizResponse(
                question=result["question"],
                options=result["options"],
                correct_answer=result["correct_answer"],
                explanation=result["explanation"],
            )
        except Exception as e:
            print(f"⚠️ Generation attempt {attempt} failed for {topic}: {e}")
            return None
    
    # Initial batch - generate requested count + buffer for failures
    buffer_count = min(request.count, 3)  # Extra attempts to account for failures
    tasks = []
    topic_cycle = (topics * ((request.count + buffer_count) // len(topics) + 1))[:request.count + buffer_count]
    
    for topic in topic_cycle:
        tasks.append(generate_one(topic))
    
    # Run all in parallel
    results = await asyncio.gather(*tasks)
    questions = [q for q in results if q is not None]
    
    # If we still need more, do targeted retries
    max_retries = 2
    retry_count = 0
    while len(questions) < request.count and retry_count < max_retries:
        retry_count += 1
        needed = request.count - len(questions)
        retry_tasks = [generate_one(topics[i % len(topics)], retry_count + 1) for i in range(needed)]
        retry_results = await asyncio.gather(*retry_tasks)
        questions.extend([q for q in retry_results if q is not None])
    
    if not questions:
        raise HTTPException(status_code=503, detail="Failed to generate any questions")
    
    # Return exactly the requested count (or all we got if fewer)
    return BatchQuizResponse(questions=questions[:request.count])


# ============== AI-POWERED FLASHCARDS ==============

import random

# Subject-specific flashcard prompts
FLASHCARD_PROMPTS = {
    "human-relations": "teamwork, communication, conflict resolution, leadership in fire service",
    "mechanical-aptitude": "fire tools, hydraulics, pumps, mechanical advantage, leverage",
    "reading-ability": "SOP terminology, fire codes, incident command, NFPA standards",
    "math": "flow rates GPM, friction loss, percentages, pump pressure calculations",
}


@app.get("/api/quiz/flashcards", response_model=FlashcardResponse)
async def get_flashcard(subjects: str = ""):
    """
    Generate a flashcard using AI based on the data store content.
    Falls back to cached terms if AI is unavailable.
    """
    try:
        # Parse subjects from query parameter
        subject_list = [s.strip() for s in subjects.split(",") if s.strip()]
        
        if tutor_engine and subject_list:
            # Use AI to generate a flashcard-style term/definition
            subject_context = ", ".join([FLASHCARD_PROMPTS.get(s, s) for s in subject_list])
            
            prompt = f"""Generate ONE flashcard for firefighter exam prep.
Subject areas: {subject_context}

Return in this exact format:
TERM: [A specific fire service term or concept]
DEFINITION: [A clear, concise definition in 1-2 sentences]

Make it relevant to written exam preparation. Use realistic numbers and examples."""

            try:
                response = await tutor_engine.explain("flashcard", prompt)
                
                # Parse the response
                lines = response.strip().split("\n")
                term = ""
                definition = ""
                
                for line in lines:
                    if line.startswith("TERM:"):
                        term = line.replace("TERM:", "").strip()
                    elif line.startswith("DEFINITION:"):
                        definition = line.replace("DEFINITION:", "").strip()
                
                if term and definition:
                    return FlashcardResponse(
                        term=term,
                        definition=definition,
                        source="Fire Captain AI"
                    )
            except Exception as e:
                print(f"⚠️ AI flashcard generation failed: {e}")
        
        # Fallback to hardcoded terms
        FALLBACK_TERMS = [
            {"term": "GPM", "definition": "Gallons Per Minute - flow rate through hose/nozzle. Handlines: 150-200 GPM.", "source": "Hydraulics"},
            {"term": "Friction Loss", "definition": "Pressure lost in hose from turbulence. Formula: FL = C × Q² × L", "source": "Hydraulics"},
            {"term": "Pre-connect", "definition": "Hoseline pre-connected to pump, ready for immediate deployment. Typically 200ft.", "source": "Operations"},
            {"term": "Flashover", "definition": "Near-simultaneous ignition of all combustibles when reaching ignition temp (900-1100°F).", "source": "Fire Behavior"},
            {"term": "Halligan Bar", "definition": "Multipurpose forcible entry tool: claw, blade, and pike. Named for Deputy Chief Halligan.", "source": "Tools"},
        ]
        
        card = random.choice(FALLBACK_TERMS)
        return FlashcardResponse(
            term=card["term"],
            definition=card["definition"],
            source=card.get("source")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flashcard retrieval failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)



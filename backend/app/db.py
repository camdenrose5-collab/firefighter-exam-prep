"""
Database module for Question Bank & Study Deck.
Uses SQLite for storage of pre-generated questions, user accounts, and study decks.
"""

import os
import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

# Database location
DB_PATH = Path(__file__).parent.parent / "data" / "questions.db"


@contextmanager
def get_db():
    """Context manager for database connections."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize database schema."""
    with get_db() as conn:
        conn.executescript("""
            -- Pre-generated question bank
            CREATE TABLE IF NOT EXISTS questions (
                id TEXT PRIMARY KEY,
                subject TEXT NOT NULL,
                question TEXT NOT NULL,
                options TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                explanation TEXT NOT NULL,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                quality_score REAL DEFAULT 1.0,
                reported_count INTEGER DEFAULT 0,
                is_approved BOOLEAN DEFAULT TRUE
            );

            -- User accounts
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- User study deck
            CREATE TABLE IF NOT EXISTS study_deck (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                question_id TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (question_id) REFERENCES questions(id)
            );

            -- Question reports
            CREATE TABLE IF NOT EXISTS reported_questions (
                id TEXT PRIMARY KEY,
                question_id TEXT NOT NULL,
                user_id TEXT,
                reason TEXT,
                reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (question_id) REFERENCES questions(id)
            );

            -- User feedback (general ideas/suggestions)
            CREATE TABLE IF NOT EXISTS user_feedback (
                id TEXT PRIMARY KEY,
                study_mode TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed BOOLEAN DEFAULT FALSE
            );

            -- Email leads (pre-registration email capture)
            CREATE TABLE IF NOT EXISTS email_leads (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                converted BOOLEAN DEFAULT FALSE
            );

            -- Pre-generated flashcard bank
            CREATE TABLE IF NOT EXISTS flashcards (
                id TEXT PRIMARY KEY,
                subject TEXT NOT NULL,
                card_type TEXT NOT NULL,
                front_content TEXT NOT NULL,
                back_content TEXT NOT NULL,
                hint TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reported_count INTEGER DEFAULT 0,
                is_approved BOOLEAN DEFAULT TRUE
            );

            -- User flashcard study deck
            CREATE TABLE IF NOT EXISTS flashcard_study_deck (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                flashcard_id TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (flashcard_id) REFERENCES flashcards(id)
            );

            -- Indexes
            CREATE INDEX IF NOT EXISTS idx_questions_subject ON questions(subject);
            CREATE INDEX IF NOT EXISTS idx_questions_approved ON questions(is_approved);
            CREATE INDEX IF NOT EXISTS idx_study_deck_user ON study_deck(user_id);
            CREATE INDEX IF NOT EXISTS idx_reports_reviewed ON reported_questions(reviewed);
            CREATE INDEX IF NOT EXISTS idx_feedback_reviewed ON user_feedback(reviewed);
            CREATE INDEX IF NOT EXISTS idx_flashcards_subject ON flashcards(subject);
            CREATE INDEX IF NOT EXISTS idx_flashcards_type ON flashcards(card_type);
            CREATE INDEX IF NOT EXISTS idx_flashcards_approved ON flashcards(is_approved);
            CREATE INDEX IF NOT EXISTS idx_flashcard_study_deck_user ON flashcard_study_deck(user_id);
        """)


# =============================================================================
# QUESTION BANK CRUD
# =============================================================================

def add_question(
    subject: str,
    question: str,
    options: List[str],
    correct_answer: str,
    explanation: str,
    quality_score: float = 1.0,
    is_approved: bool = True,
    image_path: Optional[str] = None
) -> str:
    """Add a question to the bank. Returns the question ID."""
    question_id = str(uuid.uuid4())
    with get_db() as conn:
        conn.execute(
            """INSERT INTO questions 
               (id, subject, question, options, correct_answer, explanation, quality_score, is_approved, image_path)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (question_id, subject, question, json.dumps(options), correct_answer, explanation, quality_score, is_approved, image_path)
        )
    return question_id


def get_random_questions(
    subjects: List[str],
    count: int = 10,
    approved_only: bool = True
) -> List[Dict[str, Any]]:
    """Get random questions from the bank."""
    with get_db() as conn:
        placeholders = ",".join("?" * len(subjects))
        approved_clause = "AND is_approved = TRUE" if approved_only else ""
        
        rows = conn.execute(
            f"""SELECT id, subject, question, options, correct_answer, explanation
                FROM questions
                WHERE subject IN ({placeholders}) {approved_clause}
                ORDER BY RANDOM()
                LIMIT ?""",
            (*subjects, count)
        ).fetchall()
        
        return [
            {
                "id": row["id"],
                "subject": row["subject"],
                "question": row["question"],
                "options": json.loads(row["options"]),
                "correct_answer": row["correct_answer"],
                "explanation": row["explanation"]
            }
            for row in rows
        ]


def get_question_count(subject: Optional[str] = None) -> int:
    """Get count of questions, optionally filtered by subject."""
    with get_db() as conn:
        if subject:
            row = conn.execute(
                "SELECT COUNT(*) as cnt FROM questions WHERE subject = ? AND is_approved = TRUE",
                (subject,)
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT COUNT(*) as cnt FROM questions WHERE is_approved = TRUE"
            ).fetchone()
        return row["cnt"]


def increment_report_count(question_id: str):
    """Increment the reported_count for a question."""
    with get_db() as conn:
        conn.execute(
            "UPDATE questions SET reported_count = reported_count + 1 WHERE id = ?",
            (question_id,)
        )


def find_matching_mechanical_image(query: str) -> Optional[str]:
    """
    Find a mechanical aptitude image that matches the user's query.
    Searches question content for keyword matches.
    Returns image_path if found, None otherwise.
    """
    # Define keyword groups for different mechanical concepts
    CONCEPT_KEYWORDS = {
        "pulley": ["pulley", "block and tackle", "rope", "lift", "hoist"],
        "lever": ["lever", "crowbar", "pry", "fulcrum", "halligan"],
        "gear": ["gear", "teeth", "rotation", "clockwise", "counter-clockwise", "mesh"],
        "wheel": ["wheelbarrow", "wheel", "axle"],
        "incline": ["ramp", "incline", "slope", "wedge"],
        "screw": ["screw", "thread", "jack"],
        "force": ["force", "effort", "load", "mechanical advantage", "ma"],
    }
    
    query_lower = query.lower()
    matched_concepts = []
    
    # Find which concepts the query mentions
    for concept, keywords in CONCEPT_KEYWORDS.items():
        if any(kw in query_lower for kw in keywords):
            matched_concepts.extend(keywords)
    
    if not matched_concepts:
        return None
    
    with get_db() as conn:
        # Build search query - look for questions containing any matched keywords
        conditions = " OR ".join(["question LIKE ?" for _ in matched_concepts])
        params = [f"%{kw}%" for kw in matched_concepts]
        
        row = conn.execute(
            f"""SELECT image_path FROM questions 
                WHERE subject = 'mechanical-aptitude' 
                AND image_path IS NOT NULL 
                AND ({conditions})
                ORDER BY RANDOM()
                LIMIT 1""",
            tuple(params)
        ).fetchone()
        
        if row and row["image_path"]:
            return row["image_path"]
    
    return None



# =============================================================================
# USER CRUD
# =============================================================================

def create_user(email: str, password_hash: str) -> str:
    """Create a new user. Returns user ID."""
    user_id = str(uuid.uuid4())
    with get_db() as conn:
        conn.execute(
            "INSERT INTO users (id, email, password_hash) VALUES (?, ?, ?)",
            (user_id, email, password_hash)
        )
    return user_id


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, email, password_hash, created_at FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        if row:
            return dict(row)
    return None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, email, created_at FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        if row:
            return dict(row)
    return None


# =============================================================================
# STUDY DECK CRUD
# =============================================================================

def add_to_study_deck(user_id: str, question_id: str) -> str:
    """Add question to user's study deck. Returns deck entry ID."""
    entry_id = str(uuid.uuid4())
    with get_db() as conn:
        # Check if already in deck
        existing = conn.execute(
            "SELECT id FROM study_deck WHERE user_id = ? AND question_id = ?",
            (user_id, question_id)
        ).fetchone()
        if existing:
            return existing["id"]
        
        conn.execute(
            "INSERT INTO study_deck (id, user_id, question_id) VALUES (?, ?, ?)",
            (entry_id, user_id, question_id)
        )
    return entry_id


def remove_from_study_deck(user_id: str, question_id: str) -> bool:
    """Remove question from study deck. Returns True if removed."""
    with get_db() as conn:
        cursor = conn.execute(
            "DELETE FROM study_deck WHERE user_id = ? AND question_id = ?",
            (user_id, question_id)
        )
        return cursor.rowcount > 0


def get_study_deck(user_id: str) -> List[Dict[str, Any]]:
    """Get all questions in user's study deck."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT q.id, q.subject, q.question, q.options, q.correct_answer, q.explanation, sd.added_at
               FROM study_deck sd
               JOIN questions q ON sd.question_id = q.id
               WHERE sd.user_id = ?
               ORDER BY sd.added_at DESC""",
            (user_id,)
        ).fetchall()
        
        return [
            {
                "id": row["id"],
                "subject": row["subject"],
                "question": row["question"],
                "options": json.loads(row["options"]),
                "correct_answer": row["correct_answer"],
                "explanation": row["explanation"],
                "added_at": row["added_at"]
            }
            for row in rows
        ]


def get_study_deck_questions(user_id: str, count: int) -> List[Dict[str, Any]]:
    """Get random questions from user's study deck."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT q.id, q.subject, q.question, q.options, q.correct_answer, q.explanation
               FROM study_deck sd
               JOIN questions q ON sd.question_id = q.id
               WHERE sd.user_id = ?
               ORDER BY RANDOM()
               LIMIT ?""",
            (user_id, count)
        ).fetchall()
        
        return [
            {
                "id": row["id"],
                "subject": row["subject"],
                "question": row["question"],
                "options": json.loads(row["options"]),
                "correct_answer": row["correct_answer"],
                "explanation": row["explanation"]
            }
            for row in rows
        ]


# =============================================================================
# REPORTED QUESTIONS CRUD
# =============================================================================

def report_question(question_id: str, user_id: Optional[str] = None, reason: Optional[str] = None) -> str:
    """Report a question. Returns report ID."""
    report_id = str(uuid.uuid4())
    with get_db() as conn:
        conn.execute(
            "INSERT INTO reported_questions (id, question_id, user_id, reason) VALUES (?, ?, ?, ?)",
            (report_id, question_id, user_id, reason)
        )
        # Also increment the question's report count
        conn.execute(
            "UPDATE questions SET reported_count = reported_count + 1 WHERE id = ?",
            (question_id,)
        )
    return report_id


def get_pending_reports() -> List[Dict[str, Any]]:
    """Get all unreviewed question reports."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT r.*, q.question, q.subject
               FROM reported_questions r
               JOIN questions q ON r.question_id = q.id
               WHERE r.reviewed = FALSE
               ORDER BY r.reported_at DESC"""
        ).fetchall()
        return [dict(row) for row in rows]


def mark_report_reviewed(report_id: str):
    """Mark a report as reviewed."""
    with get_db() as conn:
        conn.execute(
            "UPDATE reported_questions SET reviewed = TRUE WHERE id = ?",
            (report_id,)
        )


# =============================================================================
# USER FEEDBACK CRUD
# =============================================================================

def submit_feedback(study_mode: str, message: str) -> str:
    """Submit user feedback. Returns feedback ID."""
    feedback_id = str(uuid.uuid4())
    with get_db() as conn:
        conn.execute(
            "INSERT INTO user_feedback (id, study_mode, message) VALUES (?, ?, ?)",
            (feedback_id, study_mode, message)
        )
    return feedback_id


def get_all_feedback(reviewed_only: bool = False) -> List[Dict[str, Any]]:
    """Get all feedback entries."""
    with get_db() as conn:
        if reviewed_only:
            rows = conn.execute(
                """SELECT * FROM user_feedback WHERE reviewed = TRUE ORDER BY created_at DESC"""
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT * FROM user_feedback ORDER BY created_at DESC"""
            ).fetchall()
        return [dict(row) for row in rows]


def get_pending_feedback() -> List[Dict[str, Any]]:
    """Get all unreviewed feedback."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT * FROM user_feedback WHERE reviewed = FALSE ORDER BY created_at DESC"""
        ).fetchall()
        return [dict(row) for row in rows]


def mark_feedback_reviewed(feedback_id: str):
    """Mark feedback as reviewed."""
    with get_db() as conn:
        conn.execute(
            "UPDATE user_feedback SET reviewed = TRUE WHERE id = ?",
            (feedback_id,)
        )


# =============================================================================
# EMAIL LEADS CRUD
# =============================================================================

def create_email_lead(email: str) -> str:
    """Create an email lead. Returns the lead ID."""
    lead_id = str(uuid.uuid4())
    with get_db() as conn:
        # Check if email already exists
        existing = conn.execute(
            "SELECT id FROM email_leads WHERE email = ?",
            (email,)
        ).fetchone()
        if existing:
            return existing["id"]
        
        conn.execute(
            "INSERT INTO email_leads (id, email) VALUES (?, ?)",
            (lead_id, email)
        )
    return lead_id


def get_email_lead_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get email lead by email address."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM email_leads WHERE email = ?",
            (email,)
        ).fetchone()
        if row:
            return dict(row)
    return None


# =============================================================================
# FLASHCARD BANK CRUD
# =============================================================================

def add_flashcard(
    subject: str,
    card_type: str,
    front_content: str,
    back_content: str,
    hint: Optional[str] = None,
    source: Optional[str] = None,
    is_approved: bool = True
) -> str:
    """Add a flashcard to the bank. Returns the flashcard ID."""
    flashcard_id = str(uuid.uuid4())
    with get_db() as conn:
        conn.execute(
            """INSERT INTO flashcards 
               (id, subject, card_type, front_content, back_content, hint, source, is_approved)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (flashcard_id, subject, card_type, front_content, back_content, hint, source, is_approved)
        )
    return flashcard_id


def get_random_flashcards(
    subjects: List[str],
    count: int = 10,
    card_types: Optional[List[str]] = None,
    approved_only: bool = True
) -> List[Dict[str, Any]]:
    """Get random flashcards from the bank."""
    with get_db() as conn:
        subject_placeholders = ",".join("?" * len(subjects))
        approved_clause = "AND is_approved = TRUE" if approved_only else ""
        
        params = list(subjects)
        type_clause = ""
        if card_types:
            type_placeholders = ",".join("?" * len(card_types))
            type_clause = f"AND card_type IN ({type_placeholders})"
            params.extend(card_types)
        
        params.append(count)
        
        rows = conn.execute(
            f"""SELECT id, subject, card_type, front_content, back_content, hint, source
                FROM flashcards
                WHERE subject IN ({subject_placeholders}) {type_clause} {approved_clause}
                ORDER BY RANDOM()
                LIMIT ?""",
            tuple(params)
        ).fetchall()
        
        return [
            {
                "id": row["id"],
                "subject": row["subject"],
                "card_type": row["card_type"],
                "front_content": row["front_content"],
                "back_content": row["back_content"],
                "hint": row["hint"],
                "source": row["source"]
            }
            for row in rows
        ]


def get_flashcard_count(subject: Optional[str] = None, card_type: Optional[str] = None) -> int:
    """Get count of flashcards, optionally filtered by subject and/or card_type."""
    with get_db() as conn:
        query = "SELECT COUNT(*) as cnt FROM flashcards WHERE is_approved = TRUE"
        params = []
        
        if subject:
            query += " AND subject = ?"
            params.append(subject)
        if card_type:
            query += " AND card_type = ?"
            params.append(card_type)
        
        row = conn.execute(query, tuple(params)).fetchone()
        return row["cnt"]


# =============================================================================
# FLASHCARD STUDY DECK CRUD
# =============================================================================

def add_to_flashcard_study_deck(user_id: str, flashcard_id: str) -> str:
    """Add flashcard to user's flashcard study deck. Returns deck entry ID."""
    entry_id = str(uuid.uuid4())
    with get_db() as conn:
        # Check if already in deck
        existing = conn.execute(
            "SELECT id FROM flashcard_study_deck WHERE user_id = ? AND flashcard_id = ?",
            (user_id, flashcard_id)
        ).fetchone()
        if existing:
            return existing["id"]
        
        conn.execute(
            "INSERT INTO flashcard_study_deck (id, user_id, flashcard_id) VALUES (?, ?, ?)",
            (entry_id, user_id, flashcard_id)
        )
    return entry_id


def remove_from_flashcard_study_deck(user_id: str, flashcard_id: str) -> bool:
    """Remove flashcard from study deck. Returns True if removed."""
    with get_db() as conn:
        cursor = conn.execute(
            "DELETE FROM flashcard_study_deck WHERE user_id = ? AND flashcard_id = ?",
            (user_id, flashcard_id)
        )
        return cursor.rowcount > 0


def get_flashcard_study_deck(user_id: str) -> List[Dict[str, Any]]:
    """Get all flashcards in user's flashcard study deck."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT f.id, f.subject, f.card_type, f.front_content, f.back_content, f.hint, f.source, fsd.added_at
               FROM flashcard_study_deck fsd
               JOIN flashcards f ON fsd.flashcard_id = f.id
               WHERE fsd.user_id = ?
               ORDER BY fsd.added_at DESC""",
            (user_id,)
        ).fetchall()
        
        return [
            {
                "id": row["id"],
                "subject": row["subject"],
                "card_type": row["card_type"],
                "front_content": row["front_content"],
                "back_content": row["back_content"],
                "hint": row["hint"],
                "source": row["source"],
                "added_at": row["added_at"]
            }
            for row in rows
        ]


def get_flashcard_study_deck_cards(user_id: str, count: int) -> List[Dict[str, Any]]:
    """Get random flashcards from user's study deck."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT f.id, f.subject, f.card_type, f.front_content, f.back_content, f.hint, f.source
               FROM flashcard_study_deck fsd
               JOIN flashcards f ON fsd.flashcard_id = f.id
               WHERE fsd.user_id = ?
               ORDER BY RANDOM()
               LIMIT ?""",
            (user_id, count)
        ).fetchall()
        
        return [
            {
                "id": row["id"],
                "subject": row["subject"],
                "card_type": row["card_type"],
                "front_content": row["front_content"],
                "back_content": row["back_content"],
                "hint": row["hint"],
                "source": row["source"]
            }
            for row in rows
        ]


# Initialize on import
init_db()



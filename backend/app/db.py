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

            -- Indexes
            CREATE INDEX IF NOT EXISTS idx_questions_subject ON questions(subject);
            CREATE INDEX IF NOT EXISTS idx_questions_approved ON questions(is_approved);
            CREATE INDEX IF NOT EXISTS idx_study_deck_user ON study_deck(user_id);
            CREATE INDEX IF NOT EXISTS idx_reports_reviewed ON reported_questions(reviewed);
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
    is_approved: bool = True
) -> str:
    """Add a question to the bank. Returns the question ID."""
    question_id = str(uuid.uuid4())
    with get_db() as conn:
        conn.execute(
            """INSERT INTO questions 
               (id, subject, question, options, correct_answer, explanation, quality_score, is_approved)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (question_id, subject, question, json.dumps(options), correct_answer, explanation, quality_score, is_approved)
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


# Initialize on import
init_db()

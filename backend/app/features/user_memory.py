"""
User Memory System
Tracks which question patterns a user has seen to avoid repeats.

Simple in-memory implementation. Can be swapped to Redis/DB later.
"""

import hashlib
from typing import Dict, Set, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class UserSession:
    """Tracks a single user's question history."""
    user_id: str
    seen_signatures: Set[str] = field(default_factory=set)
    question_count: int = 0
    session_start: datetime = field(default_factory=datetime.now)
    
    def has_seen(self, signature: str) -> bool:
        """Check if user has seen this question pattern."""
        return signature in self.seen_signatures
    
    def mark_seen(self, signature: str) -> None:
        """Mark a question pattern as seen."""
        self.seen_signatures.add(signature)
        self.question_count += 1
    
    def get_stats(self) -> dict:
        """Return session statistics."""
        return {
            "user_id": self.user_id,
            "questions_seen": self.question_count,
            "unique_patterns": len(self.seen_signatures),
            "session_duration_minutes": (datetime.now() - self.session_start).seconds // 60
        }


class UserMemory:
    """
    In-memory store for user question history.
    Production: Replace with Redis or database.
    """
    
    def __init__(self):
        self._sessions: Dict[str, UserSession] = {}
    
    def get_or_create_session(self, user_id: str) -> UserSession:
        """Get existing session or create new one."""
        if user_id not in self._sessions:
            self._sessions[user_id] = UserSession(user_id=user_id)
        return self._sessions[user_id]
    
    def generate_signature(self, subject: str, question_type: str, key_variable: Optional[str] = None) -> str:
        """
        Generate a unique signature for a question pattern.
        
        Examples:
        - "math_percentage_tank_capacity"
        - "human_relations_lazy_coworker"
        - "mechanical_halligan_leverage"
        
        Args:
            subject: The exam subject (math, human-relations, etc.)
            question_type: The type of question (percentage, conflict, leverage)
            key_variable: Optional key differentiator
        
        Returns:
            A hash signature for tracking
        """
        parts = [subject.lower().replace(" ", "_"), question_type.lower().replace(" ", "_")]
        if key_variable:
            parts.append(key_variable.lower().replace(" ", "_"))
        
        raw = "_".join(parts)
        return hashlib.md5(raw.encode()).hexdigest()[:12]
    
    def check_and_mark(self, user_id: str, subject: str, question_type: str, key_variable: Optional[str] = None) -> bool:
        """
        Check if user has seen this pattern. If not, mark as seen.
        
        Returns:
            True if this is a NEW pattern (user hasn't seen it)
            False if user has already seen this pattern
        """
        session = self.get_or_create_session(user_id)
        signature = self.generate_signature(subject, question_type, key_variable)
        
        if session.has_seen(signature):
            return False
        
        session.mark_seen(signature)
        return True
    
    def get_unseen_patterns(self, user_id: str, all_patterns: List[str]) -> List[str]:
        """
        Given a list of pattern signatures, return only unseen ones.
        """
        session = self.get_or_create_session(user_id)
        return [p for p in all_patterns if not session.has_seen(p)]
    
    def get_user_stats(self, user_id: str) -> dict:
        """Get statistics for a user."""
        session = self.get_or_create_session(user_id)
        return session.get_stats()
    
    def clear_session(self, user_id: str) -> None:
        """Clear a user's session (for testing or reset)."""
        if user_id in self._sessions:
            del self._sessions[user_id]


# Singleton instance for the application
user_memory = UserMemory()

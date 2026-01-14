"""
Abstract Base Classes for Quiz Engine Components
Enables swapping retrieval and generation backends without changing application code.
"""

from abc import ABC, abstractmethod
from typing import List


class BaseRetriever(ABC):
    """Abstract base class for context retrieval."""

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """
        Retrieve relevant context snippets for a query.

        Args:
            query: The search query/topic
            top_k: Number of results to retrieve

        Returns:
            List of relevant text snippets
        """
        pass


class BaseGenerator(ABC):
    """Abstract base class for quiz question generation."""

    @abstractmethod
    async def generate(self, topic: str, context: str) -> dict:
        """
        Generate a quiz question given a topic and context.

        Args:
            topic: The subject/topic for the quiz question
            context: Retrieved context text to base the question on

        Returns:
            Dict with 'question', 'options', 'correct_answer', 'explanation'
        """
        pass

"""
Captain's Review Feature
AI-powered answer grading using RAG + Vertex AI.
"""

import os
from typing import List, Dict, Any

from app.rag_engine import RAGEngine
from app.llm.vertex_client import VertexAIClient


class CaptainsReviewFeature:
    """
    Captain's Review: Grade user answers against training materials.
    Uses RAG to retrieve relevant context and Vertex AI for grading.
    """
    
    def __init__(self, rag_engine: RAGEngine):
        self.rag_engine = rag_engine
        self.llm = VertexAIClient()
    
    async def review(
        self,
        question: str,
        user_answer: str,
        document_ids: List[str],
    ) -> Dict[str, Any]:
        """
        Review a user's answer to a question.
        
        Args:
            question: The exam question
            user_answer: The user's answer
            document_ids: List of document IDs to search for context
            
        Returns:
            Dict with grade, feedback, textbook_answer, and citations
        """
        # Retrieve relevant context
        context_data = self.rag_engine.build_context(
            query=f"{question} {user_answer}",
            document_ids=document_ids,
            top_k=5,
        )
        
        # Build the prompt
        prompt = self._build_review_prompt(
            question=question,
            user_answer=user_answer,
            context=context_data["context"],
        )
        
        # Get LLM response
        response = await self.llm.generate(prompt)
        
        # Parse the response
        result = self._parse_response(response)
        result["citations"] = context_data["citations"]
        
        return result
    
    def _build_review_prompt(
        self,
        question: str,
        user_answer: str,
        context: str,
    ) -> str:
        """Build the prompt for Captain's Review."""
        return f"""You are a veteran Fire Captain with 20 years of experience. You are helping a firefighter candidate prepare for their written certification exam.

Your task is to grade the candidate's answer and provide constructive feedback.

RULES:
1. ONLY use information from the provided context
2. Be encouraging but accurate - lives depend on correct information
3. Grade as: "correct", "partial", or "incorrect"
4. Provide specific feedback on what was good and what was missing
5. Always provide the textbook-correct answer

CONTEXT FROM TRAINING MATERIALS:
{context if context else "[No relevant context found in uploaded documents]"}

EXAM QUESTION:
{question}

CANDIDATE'S ANSWER:
{user_answer}

Respond in the following JSON format exactly:
{{
    "grade": "correct" | "partial" | "incorrect",
    "feedback": "Your detailed feedback here...",
    "textbook_answer": "The complete correct answer based on the training materials..."
}}

Your response (JSON only):"""
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured data."""
        import json
        
        # Try to extract JSON from response
        try:
            # Find JSON in response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
                return {
                    "grade": data.get("grade", "incorrect"),
                    "feedback": data.get("feedback", "Unable to parse feedback"),
                    "textbook_answer": data.get("textbook_answer", "Unable to parse textbook answer"),
                }
        except json.JSONDecodeError:
            pass
        
        # Fallback if JSON parsing fails
        return {
            "grade": "incorrect",
            "feedback": response,
            "textbook_answer": "Please check the source materials for the correct answer.",
        }

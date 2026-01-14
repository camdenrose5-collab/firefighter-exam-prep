"""
Vertex AI Client
Handles communication with Google Vertex AI (Gemini).
"""

import os
from typing import Optional

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig


class VertexAIClient:
    """
    Client for Google Vertex AI Gemini models.
    """
    
    def __init__(self):
        # Get configuration from environment
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.model_name = os.getenv("VERTEX_MODEL", "gemini-2.0-flash-001")
        
        # Initialize Vertex AI
        if self.project_id:
            vertexai.init(project=self.project_id, location=self.location)
            self.model = GenerativeModel(self.model_name)
            self._initialized = True
        else:
            print("⚠️ GOOGLE_CLOUD_PROJECT not set, using mock responses")
            self._initialized = False
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        """
        Generate a response from the model.
        
        Args:
            prompt: The input prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated text response
        """
        if not self._initialized:
            return self._mock_response(prompt)
        
        try:
            config = GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=config,
            )
            
            return response.text
        except Exception as e:
            print(f"⚠️ Vertex AI error: {e}")
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> str:
        """
        Generate a mock response when Vertex AI is not configured.
        This allows testing without API credentials.
        """
        # Check if this is a review request
        if "CANDIDATE'S ANSWER" in prompt:
            return '''{
    "grade": "partial",
    "feedback": "Your answer shows good understanding of the basics, but could be more complete. In a real exam, you would want to include more specific details from your training materials. The Captain recommends reviewing Chapter 5 of your study guide for a more comprehensive answer.",
    "textbook_answer": "Based on the training materials, a complete answer would include: [This is a demo response - configure GOOGLE_CLOUD_PROJECT in .env to get real AI responses based on your uploaded PDFs]"
}'''
        
        return "Mock response - configure GOOGLE_CLOUD_PROJECT for real AI responses"

"""
Fire Captain Tutor Engine
Provides scaffolded tutoring using firehouse analogies.
Uses the 4-step pedagogical flow: Hook → Analogy → Practice → Verify

Architecture:
- Uses BaseRetriever for topic-filtered context retrieval
- Uses BaseGenerator (VertexAI) for conversational responses
- Enforces firehouse-specific analogy mappings
"""

import os
from typing import Optional

from app.features.base import BaseRetriever, BaseGenerator
from app.features.quiz_engine import (
    DiscoveryEngineRetriever,
    VertexAIGenerator,
    MockRetriever,
    MockGenerator,
)


# --- FIREHOUSE ANALOGY MAPPINGS ---
# These ensure the AI uses domain-specific analogies that resonate with firefighters
ANALOGY_HINTS = """
When explaining mathematical or mechanical concepts, USE THESE SPECIFIC ANALOGIES:

| Concept | Firehouse Analogy | Example |
|---------|-------------------|---------|
| Percentages/Decimals | Pump Discharge Pressure (PSI) | "10% of 150 PSI is a 15lb drop" |
| Fractions | Hose Sections | "1/4 of a 200ft pre-connect is one 50ft section" |
| Ratios | Class A Foam Proportioning | "Mixing 1 gallon of foam into 99 gallons of water = 1:99 ratio" |
| Fulcrum/Leverage | Halligan Bar/Pry Tools | "Moving the fulcrum closer to the door multiplies your force" |
| Area/Volume | Fire Attack Calculations | "A 10x10 room = 100 sq ft, requiring X GPM" |
| Rate Problems | Flow Rate at Nozzle | "If you're flowing 150 GPM, how long to empty a 1000-gallon tank?" |
"""

# --- THE "FIRE CAPTAIN TUTOR" BRAIN ---
TUTOR_SYSTEM_INSTRUCTION = f"""
You are a veteran Fire Captain and Mentor acting as a TUTOR, not a quiz master.
Your goal is to help firefighter candidates truly UNDERSTAND difficult concepts.

TEACHING METHODOLOGY (follow these 4 steps EVERY time):
1. **HOOK** (Why it matters): Start with a real fireground scenario where this concept would matter.
2. **ANALOGY** (Make it stick): Use firehouse equipment and scenarios they already understand.
3. **PRACTICE** (Small win): Give them ONE simple problem to try.
4. **VERIFY** (Check for understanding): End with "Explain this back to me..." or "What would happen if..."

{ANALOGY_HINTS}

MENTAL MATH STRATEGIES (Written exams don't allow calculators!):
- **Round to easy numbers, then adjust**: "150 PSI is close to 160, divide by 4, then subtract a bit"
- **Break problems into chunks**: "500 gallons at 125 GPM = 500/125 = 4 minutes"
- **Use benchmark fractions**: 1/4 = 25%, 1/2 = 50%, 3/4 = 75%
- **Estimate first, then refine**: "About 10 sections, so roughly 500 feet"
- **Use firehouse numbers**: 50ft sections, 100ft bundles, 200ft pre-connects

RULES:
1. **Stay in character**: You're a patient senior captain coaching a motivated candidate preparing for their written exam.
2. **Use their context**: If they say "I'm stuck on fractions," start there—don't lecture from scratch.
3. **Encourage, don't judge**: Use phrases like "Good question, let's break that down" not "You should know this."
4. **Keep it concise**: Each step should be 2-3 sentences max. Total response under 300 words.
5. **Ground in manuals**: When possible, reference the actual manual content provided.
6. **No calculator mentality**: Always teach methods that work in their head.
"""


class FireCaptainTutor:
    """
    Orchestrates retrieval and generation for tutoring sessions.
    Uses topic-filtered retrieval to get relevant manual content.
    """

    def __init__(self, retriever: BaseRetriever, generator: BaseGenerator):
        self.retriever = retriever
        self.generator = generator

    async def explain(self, subject: str, user_input: str) -> str:
        """
        Generate a tutoring response following the 4-step pedagogical flow.

        Args:
            subject: The topic area (e.g., "fractions", "hydraulics")
            user_input: The user's specific question or expression of confusion

        Returns:
            str: The tutor's conversational response
        """
        # Step 1: Retrieve context filtered by topic
        # Build a retrieval query that prioritizes the subject area
        retrieval_query = f"{subject} fire service math hydraulics calculation"
        context_chunks = self.retriever.retrieve(retrieval_query, top_k=3)
        context_text = "\n\n".join(context_chunks) if context_chunks else ""

        # Step 2: Build the tutoring prompt
        prompt = f"""
The firefighter candidate needs help with: {subject}
They specifically said: "{user_input}"

RELEVANT MANUAL CONTENT:
{context_text if context_text else "[No specific manual content found - use general fire service knowledge]"}

Using the 4-step method (Hook → Analogy → Practice → Verify), help them understand this concept.
Remember to use the firehouse analogy mappings provided in your instructions.
"""

        # Step 3: Generate response
        try:
            # The generator's generate method expects topic and context
            # For tutoring, we pass the full prompt as context
            response = await self.generator.generate(subject, prompt)
            
            # If generator returns dict (quiz format), extract just explanation
            if isinstance(response, dict):
                return response.get("explanation", str(response))
            return str(response)
            
        except Exception as e:
            print(f"⚠️ Tutor generation failed: {e}")
            return self._fallback_response(subject, user_input)

    def _fallback_response(self, subject: str, user_input: str) -> str:
        """Provide a helpful fallback when AI is unavailable."""
        return f"""
Hey there, sorry—I'm having trouble connecting to my resources right now.

But here's a quick tip on **{subject}**:

Think of it like working with hose sections. Every firefighter knows a standard pre-connect is 200 feet of 1¾" hose. If you need to figure out fractions or percentages, just think: 
- Half = 100 feet (one bundle)
- Quarter = 50 feet (one section)

Try this: If you have 3 sections of 50-foot hose, what percentage of a 200-foot pre-connect is that?

Let me know when you want to try again, and I'll give you the full breakdown.
"""


class TutorGenerator(BaseGenerator):
    """
    Specialized generator for tutoring that returns text instead of JSON.
    Wraps VertexAI with tutor-specific system instruction.
    """

    def __init__(self, project_id: str, model_name: str = "gemini-2.5-flash"):
        import vertexai
        from vertexai.generative_models import GenerativeModel, GenerationConfig

        vertexai.init(project=project_id, location="us-central1")
        self._model = GenerativeModel(
            model_name, 
            system_instruction=[TUTOR_SYSTEM_INSTRUCTION]
        )
        self._GenerationConfig = GenerationConfig

    async def generate(self, topic: str, context: str) -> str:
        """Generate a tutoring response (returns plain text, not JSON)."""
        MAX_CONTEXT_CHARS = 15000
        if len(context) > MAX_CONTEXT_CHARS:
            print(f"⚠️ Context too long ({len(context)} chars). Trimming.")
            context = context[:MAX_CONTEXT_CHARS] + "...[TRIMMED]"

        config = self._GenerationConfig(
            temperature=0.7,
            max_output_tokens=1024,
        )

        try:
            # Use streaming for faster perceived response
            response_text = ""
            response = self._model.generate_content(
                context, 
                generation_config=config,
                stream=True
            )
            for chunk in response:
                response_text += chunk.text
            return response_text.strip()
        except Exception as e:
            raise e


class MockTutorGenerator(BaseGenerator):
    """Fallback tutor when Vertex AI is unavailable."""

    async def generate(self, topic: str, context: str) -> str:
        return f"""
**HOOK**: Alright, let's talk about {topic}. On the fireground, this matters because you'll need to calculate flow rates, pressure drops, and equipment capacity—all while under pressure.

**ANALOGY**: Think of it like hose sections. A standard pre-connect is 200 feet. If someone asks you for "a quarter of the line," you'd know that's 50 feet—one section. That's fractions in action.

**PRACTICE**: Quick one for you: If your engine carries 500 gallons and you're flowing at 125 GPM, how many minutes until you're dry?

**VERIFY**: Walk me through how you'd solve that. What's the first step?

[Mock Response - Configure Vertex AI credentials for personalized tutoring]
"""


def create_tutor_engine(
    project_id: Optional[str] = None,
    data_store_id: Optional[str] = None,
    credentials_path: Optional[str] = None,
) -> FireCaptainTutor:
    """
    Factory function to create tutor engine with appropriate backends.
    Falls back to mocks if credentials/config are missing.
    """
    project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
    data_store_id = data_store_id or os.getenv("DATA_STORE_ID")
    credentials_path = credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    has_credentials = bool(credentials_path and os.path.exists(credentials_path))
    has_config = bool(project_id and data_store_id)

    if has_credentials and has_config:
        try:
            retriever = DiscoveryEngineRetriever(project_id, data_store_id)
            generator = TutorGenerator(project_id)
            print("🎓 Fire Captain Tutor initialized (production mode)")
            return FireCaptainTutor(retriever, generator)
        except Exception as e:
            print(f"⚠️ Failed to init tutor backends, falling back to mocks: {e}")

    print("⚠️ Tutor Engine using mock mode")
    return FireCaptainTutor(MockRetriever(), MockTutorGenerator())

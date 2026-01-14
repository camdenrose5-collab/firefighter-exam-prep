"""
Fire Captain Quiz Engine
Generates quiz questions using Vertex AI (Gemini) and Discovery Engine for retrieval.
Enforces the "Frictionless" culture for interpersonal conflict questions.

Architecture:
- DiscoveryEngineRetriever implements BaseRetriever
- VertexAIGenerator implements BaseGenerator
- FireCaptainQuizEngine orchestrates both via interfaces (swappable)
"""

import os
import json
from typing import List, Optional

from app.features.base import BaseRetriever, BaseGenerator

# Import HR training data for Human Relations questions
try:
    from app.features.hr_training import HR_PATTERNS, format_hr_examples
    HR_TRAINING_AVAILABLE = True
except ImportError:
    HR_TRAINING_AVAILABLE = False
    HR_PATTERNS = ""


# --- THE "FIRE CAPTAIN" BRAIN ---
SYSTEM_INSTRUCTION = """
You are a veteran Fire Captain and TEST DESIGNER creating original exam questions.
Your goal is to help candidates pass written firefighter exams.

QUESTION GENERATION RULES:
1. **Create ORIGINAL questions**: Use provided context as a STYLE REFERENCE only.
   - Vary the numbers (different PSI, GPM, percentages, distances)
   - Swap equipment types (Halligan, axe, pike pole, K-tool)
   - Change fire scenarios (structure, wildland, vehicle, hazmat)
   - Use different character names and situations
   DO NOT copy questions verbatim from the reference material.

2. **Frictionless Logic (Human Relations)**: For social/teamwork questions:
   - Frame as: "In a training video, you observe a firefighter who..."
   - Correct answer MUST prioritize resolving privately at the lowest level
   - Options should include: private conversation, supervisor report, ignore, confrontation
   
3. **Mental Math Focus**: For math questions:
   - Use "round numbers" that work in your head (50, 100, 150, 200)
   - No complex decimals or fractions requiring a calculator
   
4. **Subject Areas**:
   - Human Relations: teamwork, conflict, communication, leadership
   - Mechanical Aptitude: tools, leverage, hydraulics, troubleshooting
   - Reading Ability: comprehension, following instructions, SOPs
   - Math: percentages, fractions, flow rates, area calculations

5. **Format:** Return ONLY valid JSON with keys: 'question', 'options' (list of 4), 'correct_answer', 'explanation'.
"""

# Enhanced HR-specific instruction (used when topic is Human Relations)
HR_SYSTEM_INSTRUCTION = SYSTEM_INSTRUCTION + """

HUMAN RELATIONS SPECIFIC RULES:
- PRIVATE FIRST: Address coworker issues privately before escalating
- DE-ESCALATE: Redirect hostile bystanders/family productively (give them a task)
- PERSUADE, DON'T FORCE: For patient consent, respect autonomy while trying to help
- TEAM OVER SELF: Join group activities before personal improvement
- TRUST COLLEAGUES: Assume good intent unless you have real evidence otherwise
- BRIEF & PROFESSIONAL: Short explanations, no arguments with public
- USE AVAILABLE RESOURCES: Police for crowd control, supervisors for policy issues
- VOLUNTEER UP: Take initiative to resolve impasses and help rookies learn
- APOLOGIZE & FIX: Don't argue about minor issues - just resolve them
- SHOW COMPASSION: Offer support even to difficult colleagues
"""


# =============================================================================
# RETRIEVER IMPLEMENTATIONS
# =============================================================================

class MockRetriever(BaseRetriever):
    """Fallback retriever when Discovery Engine is unavailable."""

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        return [
            f"[Mock Context] Fire service personnel should handle interpersonal conflicts "
            f"at the lowest organizational level. When dealing with issues like '{query}', "
            f"approach the individual privately before escalating to supervisors.",
            "[Mock Context] Effective firefighters demonstrate teamwork, communication, "
            "and problem-solving. Direct, respectful communication resolves most conflicts.",
            "[Mock Context] Chain of command exists for formal issues. Informal peer "
            "resolution is preferred for day-to-day challenges in station life.",
        ][:top_k]


class DiscoveryEngineRetriever(BaseRetriever):
    """Retriever backed by Google Discovery Engine."""

    def __init__(self, project_id: str, data_store_id: str, location: str = "global"):
        from google.cloud import discoveryengine_v1 as discoveryengine

        self._client = discoveryengine.SearchServiceClient()
        self._serving_config = (
            f"projects/{project_id}/locations/{location}"
            f"/collections/default_collection/dataStores/{data_store_id}"
            f"/servingConfigs/default_search"
        )
        self._discoveryengine = discoveryengine

    def retrieve(self, query: str, top_k: int = 1) -> List[str]:
        request = self._discoveryengine.SearchRequest(
            serving_config=self._serving_config,
            query=query,
            page_size=top_k,
            content_search_spec=self._discoveryengine.SearchRequest.ContentSearchSpec(
                snippet_spec=self._discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                    return_snippet=True
                )
            ),
        )
        response = self._client.search(request=request)

        snippets = []
        for result in response.results:
            try:
                snippet = result.document.derived_struct_data["snippets"][0]["snippet"]
                snippets.append(snippet)
            except (KeyError, IndexError):
                continue

        return snippets


# =============================================================================
# GENERATOR IMPLEMENTATIONS
# =============================================================================

class MockGenerator(BaseGenerator):
    """Fallback generator when Vertex AI is unavailable."""

    async def generate(self, topic: str, context: str) -> dict:
        return {
            "question": f"When dealing with '{topic}' in the fire station, what is the BEST first step?",
            "options": [
                "Immediately report to the Station Captain",
                "Discuss the issue privately with the coworker first",
                "File a formal written complaint",
                "Ignore the situation and focus on your own work",
            ],
            "correct_answer": "Discuss the issue privately with the coworker first",
            "explanation": (
                "[Mock Response - Configure credentials for real AI responses] "
                "The 'Frictionless' approach prioritizes resolving conflicts at the lowest level."
            ),
        }


class VertexAIGenerator(BaseGenerator):
    """Generator backed by Google Vertex AI (Gemini)."""

    def __init__(self, project_id: str, model_name: str = "gemini-2.5-flash"):
        import vertexai
        from vertexai.generative_models import GenerativeModel, GenerationConfig

        vertexai.init(project=project_id, location="us-central1")
        # Standard model for most topics
        self._model = GenerativeModel(model_name, system_instruction=[SYSTEM_INSTRUCTION])
        # HR-specific model with enhanced training
        self._hr_model = GenerativeModel(model_name, system_instruction=[HR_SYSTEM_INSTRUCTION])
        self._GenerationConfig = GenerationConfig

    async def generate(self, topic: str, context: str) -> dict:
        import re
        
        # Check if this is a Human Relations question
        is_hr = "human" in topic.lower() or "relation" in topic.lower()
        
        # Token Management: Trim context if it's too long to prevent overflow
        MAX_CONTEXT_CHARS = 8000  # Reduced for speed
        if len(context) > MAX_CONTEXT_CHARS:
            context = context[:MAX_CONTEXT_CHARS] + "...[TRIMMED]"

        # Build prompt with optional HR examples
        hr_examples = ""
        if is_hr and HR_TRAINING_AVAILABLE:
            hr_examples = f"""
HERE ARE EXAMPLE HUMAN RELATIONS QUESTIONS FOR REFERENCE:
{format_hr_examples(3)}

Now create a NEW, ORIGINAL question following these patterns.
"""

        prompt = f"""
Based on the following Fire Service manual text, generate a challenging multiple-choice question about '{topic}'.

MANUAL TEXT:
{context}
{hr_examples}

CRITICAL: Return ONLY valid JSON. No markdown, no explanation, just JSON:
{{"question": "...", "options": ["A", "B", "C", "D"], "correct_answer": "...", "explanation": "..."}}
"""
        config = self._GenerationConfig(
            temperature=0.4, 
            max_output_tokens=1024
        )
        try:
            # Use HR-specific model for Human Relations questions
            model = self._hr_model if is_hr else self._model
            
            # Use streaming for faster response
            response_text = ""
            response = model.generate_content(
                prompt, 
                generation_config=config,
                stream=True
            )
            for chunk in response:
                response_text += chunk.text
            response_text = response_text.strip()
    
            # Robust JSON extraction
            # Try 1: Direct parse
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                pass
            
            # Try 2: Extract from markdown code block
            if "```" in response_text:
                match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
                if match:
                    try:
                        return json.loads(match.group(1))
                    except json.JSONDecodeError:
                        pass
            
            # Try 3: Find JSON object pattern
            match = re.search(r'\{[\s\S]*"question"[\s\S]*"options"[\s\S]*\}', response_text)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
            
            # All parsing failed
            print(f"⚠️ RAW RESPONSE TEXT: {response_text}")  # DEBUG LOG
            raise ValueError(f"Could not parse JSON from response: {response_text[:200]}")
            
        except Exception as e:
            print(f"⚠️ Generator error: {e}")
            raise e


# =============================================================================
# ORCHESTRATOR
# =============================================================================

class FireCaptainQuizEngine:
    """
    Orchestrates retrieval and generation to produce quiz questions.
    Uses injected interfaces - swap implementations without changing this class.
    """

    def __init__(self, retriever: BaseRetriever, generator: BaseGenerator):
        self.retriever = retriever
        self.generator = generator

    async def generate_quiz_question(self, topic: str) -> dict:
        """
        Generates a multiple-choice quiz question on the given topic.

        Args:
            topic: The subject/topic for the quiz question

        Returns:
            Dict with 'question', 'options', 'correct_answer', 'explanation'
        """
        # Step 1: Retrieve context
        context_chunks = self.retriever.retrieve(topic)
        context_text = "\n\n".join(context_chunks)

        # Step 2: Generate question
        try:
            return await self.generator.generate(topic, context_text)
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse JSON response: {e}")
            return await MockGenerator().generate(topic, context_text)
        except Exception as e:
            print(f"⚠️ Generation failed: {e}")
            return await MockGenerator().generate(topic, context_text)


# =============================================================================
# FACTORY
# =============================================================================

def create_quiz_engine(
    project_id: Optional[str] = None,
    data_store_id: Optional[str] = None,
    credentials_path: Optional[str] = None,
) -> FireCaptainQuizEngine:
    """
    Factory function to create quiz engine with appropriate backends.
    Falls back to mocks if credentials/config are missing.

    Args:
        project_id: Google Cloud project ID
        data_store_id: Discovery Engine data store ID
        credentials_path: Path to service account JSON (GOOGLE_APPLICATION_CREDENTIALS)

    Returns:
        Configured FireCaptainQuizEngine instance
    """
    project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
    data_store_id = data_store_id or os.getenv("DATA_STORE_ID")
    credentials_path = credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    # Check if we have valid Google Cloud credentials
    has_credentials = bool(credentials_path and os.path.exists(credentials_path))
    has_config = bool(project_id and data_store_id)

    if has_credentials and has_config:
        try:
            retriever = DiscoveryEngineRetriever(project_id, data_store_id)
            generator = VertexAIGenerator(project_id)
            print(f"🔥 Fire Captain Quiz Engine initialized (production mode)")
            print(f"   Project: {project_id}, DataStore: {data_store_id}")
            return FireCaptainQuizEngine(retriever, generator)
        except Exception as e:
            print(f"⚠️ Failed to init Google backends, falling back to mocks: {e}")

    # Fallback to mock implementations
    missing = []
    if not credentials_path:
        missing.append("GOOGLE_APPLICATION_CREDENTIALS")
    elif not os.path.exists(credentials_path):
        missing.append(f"credentials file at {credentials_path}")
    if not project_id:
        missing.append("GOOGLE_CLOUD_PROJECT")
    if not data_store_id:
        missing.append("DATA_STORE_ID")

    print(f"⚠️ Quiz Engine using mock mode. Missing: {', '.join(missing)}")
    return FireCaptainQuizEngine(MockRetriever(), MockGenerator())

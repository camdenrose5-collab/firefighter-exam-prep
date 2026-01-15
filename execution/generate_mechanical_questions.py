#!/usr/bin/env python3
"""
Mechanical Aptitude Question Generator with Imagen 4 Fast

Generates 250 mechanical aptitude multiple-choice questions using:
- Gemini 2.5 Flash for question content
- Imagen 4 Fast for technical diagram images

Usage:
    python generate_mechanical_questions.py --count 250
    python generate_mechanical_questions.py --count 10 --dry-run
"""

import os
import sys
import json
import uuid
import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher
from typing import List, Dict, Any, Optional

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")
load_dotenv(backend_path / ".env")

from app import db

# Image output directory
IMAGE_DIR = Path(__file__).parent.parent / "public" / "assets" / "mechanical"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

# Imagen error log
IMAGEN_ERRORS_PATH = Path(__file__).parent / "imagen_errors.json"


# =============================================================================
# SYSTEM PROMPTS
# =============================================================================

MECHANICAL_SYSTEM_PROMPT = """You are an expert mechanical aptitude test writer creating questions for firefighter entry exams.

**FOCUS AREAS (General Mechanical - NO fire-specific jargon):**
- Levers (Class 1, 2, 3): wheelbarrows, seesaws, crowbars, bottle openers
- Pulleys: flag poles, window blinds, rope systems, block and tackle
- Gears: bicycles, clocks, hand drills, mechanical toys
- Simple Machines: wedges, inclined planes, screws, wheel and axle
- Tool Logic: wrenches, pliers, scissors, screwdrivers

**OUTPUT FORMAT (JSON array, no markdown):**
[
  {
    "question": "The question text with reference to points A, B, C in the diagram",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "The exact text of the correct option",
    "explanation": "Clear 2-3 sentence explanation of WHY this is correct",
    "image_request_prompt": "Technical 2D diagram description with EXPLICIT label placement"
  }
]

**RULES:**
1. Use everyday objects (wheelbarrow, scissors, pliers, bicycle, etc.)
2. Questions MUST reference labeled points (A, B, C) in the diagram
3. image_request_prompt MUST specify exact positions for labels
4. All 4 options must be plausible; no obviously wrong answers
5. Explanation must teach the underlying principle
6. NEVER repeat the same scenario type within a batch

**EXAMPLE image_request_prompt:**
"Technical 2D line diagram of a Class 1 lever (seesaw). The fulcrum is at the center, labeled 'F'. On the left side, there is a 20kg weight labeled 'A'. On the right side, there is an empty position labeled 'B' where a force arrow points downward. The diagram uses black lines on white background with clear geometric shapes."
"""


# =============================================================================
# GENERATORS
# =============================================================================

def get_project_id() -> str:
    """Extract project ID from service account credentials."""
    creds_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if creds_file:
        # Handle relative paths
        if not os.path.isabs(creds_file):
            creds_file = str(Path(__file__).parent.parent / creds_file)
        if os.path.exists(creds_file):
            with open(creds_file) as f:
                return json.load(f).get("project_id")
    return os.environ.get("GOOGLE_CLOUD_PROJECT", "")


class MechanicalQuestionGenerator:
    """Generates mechanical aptitude questions using Gemini 2.5 Flash."""
    
    def __init__(self, project_id: str):
        import vertexai
        from vertexai.generative_models import GenerativeModel, GenerationConfig
        
        vertexai.init(project=project_id, location="us-central1")
        self.model = GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=[MECHANICAL_SYSTEM_PROMPT]
        )
        self._GenerationConfig = GenerationConfig
        self.previous_topics: List[str] = []
    
    def generate_batch(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate a batch of questions."""
        # Build prompt with deduplication context
        avoidance_note = ""
        if self.previous_topics:
            avoidance_note = f"\n\nAVOID these scenarios already used:\n- " + "\n- ".join(self.previous_topics[-50:])
        
        prompt = f"""Generate {count} unique mechanical aptitude questions.
        
Each question MUST:
1. Cover a DIFFERENT mechanical concept (mix of levers, pulleys, gears, tools)
2. Reference specific labeled points (A, B, C) that will appear in a diagram
3. Include a detailed image_request_prompt for the technical diagram
{avoidance_note}

Return ONLY a valid JSON array, no markdown code blocks."""

        response = self.model.generate_content(
            prompt,
            generation_config=self._GenerationConfig(
                response_mime_type="application/json",
                temperature=0.9,  # Higher for variety
            )
        )
        
        try:
            questions = json.loads(response.text)
            # Track topics for deduplication
            for q in questions:
                # Extract a short topic summary
                topic = q.get("question", "")[:80]
                self.previous_topics.append(topic)
            return questions
        except json.JSONDecodeError as e:
            print(f"  ⚠️ JSON parse error: {e}")
            return []


class ImagenDiagramGenerator:
    """Generates technical diagrams using Imagen 4 Fast."""
    
    def __init__(self, project_id: str):
        import vertexai
        from vertexai.preview.vision_models import ImageGenerationModel
        
        vertexai.init(project=project_id, location="us-central1")
        self.model = ImageGenerationModel.from_pretrained("imagen-4.0-fast-generate-001")
        self.errors: List[Dict] = []
    
    def generate_diagram(self, prompt: str, question_id: str) -> Optional[str]:
        """
        Generate a diagram image from the prompt.
        Returns the file path if successful, None if failed.
        """
        # Enhance prompt for technical diagram style
        enhanced_prompt = f"""Technical 2D schematic diagram. Black and white line art on white background.
Clean geometric shapes, clearly labeled points with letters (A, B, C).
Educational illustration style, no shading, no color.

{prompt}"""

        try:
            response = self.model.generate_images(
                prompt=enhanced_prompt,
                number_of_images=1,
                aspect_ratio="1:1",
            )
            
            if response and hasattr(response, 'images') and len(list(response.images)) > 0:
                # Save the image
                image = list(response.images)[0]
                filename = f"{question_id}.png"
                filepath = IMAGE_DIR / filename
                
                # Save image bytes
                image.save(str(filepath))
                
                # Return web-accessible path
                return f"/assets/mechanical/{filename}"
            else:
                self._log_error(question_id, prompt, "No image returned")
                return None
                
        except Exception as e:
            self._log_error(question_id, prompt, str(e))
            return None
    
    def _log_error(self, question_id: str, prompt: str, error: str):
        """Log Imagen errors for manual review."""
        self.errors.append({
            "question_id": question_id,
            "prompt": prompt[:200],
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
    
    def save_error_log(self):
        """Save all errors to JSON file."""
        if self.errors:
            existing = []
            if IMAGEN_ERRORS_PATH.exists():
                with open(IMAGEN_ERRORS_PATH) as f:
                    existing = json.load(f)
            
            existing.extend(self.errors)
            
            with open(IMAGEN_ERRORS_PATH, "w") as f:
                json.dump(existing, f, indent=2)


# =============================================================================
# QA CHECKS
# =============================================================================

def check_json_structure(question: dict) -> tuple[bool, str]:
    """Validate question has required fields."""
    required = ["question", "options", "correct_answer", "explanation", "image_request_prompt"]
    for field in required:
        if field not in question:
            return False, f"Missing field: {field}"
    
    if not isinstance(question["options"], list) or len(question["options"]) != 4:
        return False, "Options must be a list of 4 items"
    
    return True, "OK"


def check_correct_answer(question: dict) -> tuple[bool, str]:
    """Verify correct_answer exists in options."""
    if question["correct_answer"] not in question["options"]:
        return False, f"Correct answer not in options"
    return True, "OK"


def check_explanation_length(question: dict, min_words: int = 10) -> tuple[bool, str]:
    """Check explanation has minimum word count."""
    words = question["explanation"].split()
    if len(words) < min_words:
        return False, f"Explanation too short ({len(words)} words)"
    return True, "OK"


def check_duplicate(question: dict, existing: list, threshold: float = 0.85) -> tuple[bool, str]:
    """Check for duplicate questions using fuzzy matching."""
    new_text = question["question"].lower()
    
    for ex in existing:
        ex_text = ex.get("question", "").lower()
        ratio = SequenceMatcher(None, new_text, ex_text).ratio()
        if ratio > threshold:
            return False, f"Duplicate (similarity: {ratio:.0%})"
    
    return True, "OK"


def run_qa_checks(question: dict, existing: list) -> tuple[bool, list[str]]:
    """Run all QA checks on a question."""
    issues = []
    
    checks = [
        ("Structure", check_json_structure(question)),
        ("Answer", check_correct_answer(question)),
        ("Explanation", check_explanation_length(question)),
        ("Duplicate", check_duplicate(question, existing)),
    ]
    
    all_passed = True
    for name, (passed, msg) in checks:
        if not passed:
            issues.append(f"{name}: {msg}")
            all_passed = False
    
    return all_passed, issues


# =============================================================================
# MAIN GENERATION LOOP
# =============================================================================

async def generate_mechanical_questions(
    total_count: int = 250,
    batch_size: int = 10,
    dry_run: bool = False
) -> Dict[str, Any]:
    """Generate mechanical aptitude questions with images."""
    
    project_id = get_project_id()
    if not project_id:
        raise ValueError("Could not determine project ID from credentials")
    
    print(f"\n📍 Project ID: {project_id}")
    
    # Initialize generators
    question_gen = MechanicalQuestionGenerator(project_id)
    imagen_gen = ImagenDiagramGenerator(project_id) if not dry_run else None
    
    # Load existing questions for deduplication
    existing = db.get_random_questions(["mechanical-aptitude"], 1000, approved_only=False)
    generated: List[Dict] = []
    
    stats = {
        "total_attempted": 0,
        "questions_passed": 0,
        "questions_failed": 0,
        "images_generated": 0,
        "images_failed": 0,
        "saved_to_db": 0,
    }
    
    num_batches = (total_count + batch_size - 1) // batch_size
    
    for batch_num in range(num_batches):
        remaining = total_count - len(generated)
        if remaining <= 0:
            break
        
        current_batch_size = min(batch_size, remaining)
        
        print(f"\n{'='*60}")
        print(f"📦 Batch {batch_num + 1}/{num_batches} ({current_batch_size} questions)")
        print(f"{'='*60}")
        
        # Generate questions
        print("  🧠 Generating questions with Gemini...")
        questions = question_gen.generate_batch(current_batch_size)
        
        if not questions:
            print("  ❌ Batch generation failed")
            continue
        
        print(f"  ✅ Generated {len(questions)} questions")
        
        # Process each question
        for i, q in enumerate(questions):
            stats["total_attempted"] += 1
            q_num = batch_num * batch_size + i + 1
            
            # QA Checks
            passed, issues = run_qa_checks(q, existing + generated)
            
            if not passed:
                print(f"  ❌ Q{q_num}: FAIL - {', '.join(issues)}")
                stats["questions_failed"] += 1
                continue
            
            stats["questions_passed"] += 1
            
            # Generate image
            image_path = None
            if not dry_run and imagen_gen:
                print(f"  🎨 Q{q_num}: Generating diagram...")
                temp_id = str(uuid.uuid4())
                image_path = imagen_gen.generate_diagram(
                    q.get("image_request_prompt", ""),
                    temp_id
                )
                
                if image_path:
                    stats["images_generated"] += 1
                    print(f"  ✅ Q{q_num}: Image saved")
                else:
                    stats["images_failed"] += 1
                    print(f"  ⚠️ Q{q_num}: Image generation failed (flagged for review)")
            
            # Save to database
            if not dry_run:
                question_id = db.add_question(
                    subject="mechanical-aptitude",
                    question=q["question"],
                    options=q["options"],
                    correct_answer=q["correct_answer"],
                    explanation=q["explanation"],
                    is_approved=True,
                    image_path=image_path
                )
                q["id"] = question_id
                stats["saved_to_db"] += 1
                print(f"  💾 Q{q_num}: Saved to database")
            else:
                print(f"  ✅ Q{q_num}: PASS (dry run)")
            
            generated.append(q)
        
        # Rate limiting delay between batches
        if batch_num < num_batches - 1:
            print("\n  ⏳ Waiting 2s before next batch...")
            await asyncio.sleep(2)
    
    # Save Imagen error log
    if imagen_gen:
        imagen_gen.save_error_log()
    
    return stats


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate mechanical aptitude questions with Imagen diagrams"
    )
    parser.add_argument("--count", type=int, default=250,
                       help="Number of questions to generate (default: 250)")
    parser.add_argument("--batch-size", type=int, default=10,
                       help="Questions per batch (default: 10)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Run without saving to DB or generating images")
    
    args = parser.parse_args()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║      🔧 MECHANICAL APTITUDE QUESTION GENERATOR 🔧           ║
╠══════════════════════════════════════════════════════════════╣
║  Target Count: {args.count:<45} ║
║  Batch Size: {args.batch_size:<47} ║
║  Mode: {'DRY RUN' if args.dry_run else 'LIVE (Gemini + Imagen + DB)':<52} ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Show current bank stats
    print("📊 Current Question Bank:")
    for subject in ["human-relations", "mechanical-aptitude", "reading-ability", "math"]:
        count = db.get_question_count(subject)
        print(f"   {subject}: {count}")
    print(f"   TOTAL: {db.get_question_count()}")
    print()
    
    # Run generation
    start_time = datetime.now()
    stats = asyncio.run(generate_mechanical_questions(
        total_count=args.count,
        batch_size=args.batch_size,
        dry_run=args.dry_run
    ))
    duration = datetime.now() - start_time
    
    # Summary
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    📊 GENERATION SUMMARY                     ║
╠══════════════════════════════════════════════════════════════╣
║  Duration: {str(duration):<49} ║
║  Questions Attempted: {stats['total_attempted']:<38} ║
║  Questions Passed QA: {stats['questions_passed']:<38} ║
║  Questions Failed QA: {stats['questions_failed']:<38} ║
║  Images Generated: {stats['images_generated']:<41} ║
║  Images Failed: {stats['images_failed']:<44} ║
║  Saved to Database: {stats['saved_to_db']:<40} ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Updated bank stats
    if not args.dry_run:
        print("\n📊 Updated Question Bank:")
        for subject in ["human-relations", "mechanical-aptitude", "reading-ability", "math"]:
            count = db.get_question_count(subject)
            print(f"   {subject}: {count}")
        print(f"   TOTAL: {db.get_question_count()}")
    
    # Note about image errors
    if stats['images_failed'] > 0:
        print(f"\n⚠️  {stats['images_failed']} images failed - check: {IMAGEN_ERRORS_PATH}")


if __name__ == "__main__":
    main()

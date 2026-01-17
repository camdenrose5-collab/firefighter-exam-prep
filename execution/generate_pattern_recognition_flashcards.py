#!/usr/bin/env python3
"""
Pattern Recognition Flashcard Generator for Math and Mechanical Aptitude

Generates 100 flashcards per subject using the new pattern-recognition approach:
- Math: Decomposition methods, estimation, mental shortcuts, inverse verification
- Mechanical: FRE mnemonic, trade-off rules, gear ratios, lever classes with logic

Each card teaches the WHY, not just the WHAT.

Usage:
    python generate_pattern_recognition_flashcards.py --dry-run  # Preview
    python generate_pattern_recognition_flashcards.py            # Execute
"""

import os
import sys
import json
import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Load environment variables
from dotenv import load_dotenv

env_mode = os.environ.get("NODE_ENV", "development")
env_file = backend_path.parent / f".env.{env_mode}"
if not env_file.exists():
    env_file = backend_path.parent / ".env"
load_dotenv(env_file)

from app import db

import random

# Initialize Vertex AI directly
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
if project_id:
    vertexai.init(project=project_id, location="us-central1")



# =============================================================================
# PATTERN RECOGNITION TOPICS
# =============================================================================

MATH_TOPICS = [
    # Percentage calculations
    "Finding 10% of any number", "Finding 15% of any number", "Finding 25% of any number",
    "Finding 20% of any number", "Finding 5% of any number", "Finding 50% of any number",
    "Subtracting a percentage from a total", "Adding a percentage to a base",
    
    # Fraction operations
    "Converting fractions to decimals", "Converting decimals to fractions",
    "Finding 1/4 of a total", "Finding 1/3 of a total", "Finding 3/4 of a total",
    "Simplifying fractions", "Adding fractions with same denominator",
    
    # Division and multiplication
    "Division as inverse multiplication", "Estimating division with rounding",
    "Multiplying by 12", "Squaring numbers quickly", "Doubling and halving strategy",
    
    # Fire service calculations
    "GPM flow rate calculations", "Tank capacity problems", "Pump discharge time",
    "Hose length calculations", "Ladder height estimates", "Water supply duration",
    "Friction loss mental math", "Elevation pressure changes",
    
    # Estimation
    "Rounding for quick estimates", "Multiple choice estimation",
    "Mental math with friendly numbers", "Approximating division",
    
    # Unit conversions
    "Minutes to hours", "Gallons per minute calculations", "PSI conversions",
    "Feet to inches", "Percentage to decimal", "Decimal to percentage",
    
    # Ratios and proportions
    "Mixing ratios (foam)", "Proportional reasoning", "Scaling up quantities",
    "Scaling down quantities", "Ratio word problems",
    
    # Time calculations
    "Work rate problems", "How many units per hour", "Time to complete a task",
    "Combined work rates", "Schedule calculations",
    
    # Area and volume
    "Area of rectangles", "Volume calculations", "Perimeter problems",
    "Water volume in tanks", "Coverage area calculations",
    
    # Money math
    "Adding decimals like money", "Making change calculations",
    "Budget percentage allocations", "Cost per unit calculations",
]

MECHANICAL_TOPICS = [
    # Lever classes
    "Class 1 lever identification", "Class 2 lever identification", "Class 3 lever identification",
    "FRE mnemonic for levers", "Lever examples in fire service", "Halligan bar as lever",
    "Crowbar lever class", "Wheelbarrow lever class", "Shovel lever class",
    "Pliers lever class", "Nutcracker lever class", "See-saw lever principles",
    
    # Mechanical advantage
    "Calculating mechanical advantage", "Force vs distance trade-off",
    "Work input equals work output", "Effort force calculation",
    "Load force calculation", "MA ratio interpretation",
    
    # Pulleys
    "Fixed pulley purpose", "Moving pulley advantage", "2:1 pulley system",
    "3:1 pulley system", "Block and tackle principle", "Rope pull distance",
    "Direction of force with pulleys", "Pulley system friction",
    
    # Gears
    "Gear ratio calculation", "Driver vs driven gear", "Teeth count ratios",
    "Gear rotation direction", "Speed vs torque trade-off", "Gear train direction",
    "Odd vs even gears rotation", "Larger gear slower principle",
    
    # Torque and force
    "Torque calculation principle", "Longer handle more torque",
    "Wrench handle length effect", "Rotational force concepts",
    "Clockwise vs counterclockwise", "Moment arm principle",
    
    # Inclined planes
    "Ramp length vs effort", "Short steep vs long shallow ramp",
    "Inclined plane as simple machine", "Wedge principle",
    "Screw as inclined plane", "Height vs length ratio",
    
    # Hydraulics basics
    "Hydraulic pressure principle", "Hydraulic spreader operation",
    "Hydraulic cutter operation", "Fluid force multiplication",
    "Hydraulic ram principle", "Pascal's law application",
    
    # Fire service mechanical
    "Ladder mechanical advantage", "Hose friction principles",
    "Pump pressure concepts", "Nozzle reaction force",
    "Coupling torque", "Valve operation mechanics",
    
    # Applied physics
    "Force = Mass × Distance", "Work = Force × Distance",
    "Gravity effect on lifting", "Friction in mechanical systems",
    "Efficiency loss in systems", "Input vs output energy",
]


# =============================================================================
# PROMPT TEMPLATES
# =============================================================================

def get_math_prompt(topic: str, existing_fronts: set) -> str:
    """Generate a pattern-recognition math flashcard prompt."""
    return f"""Generate ONE pattern-recognition flashcard for firefighter exam math prep.

Topic: **{topic}**

IMPORTANT: This is NOT a simple Q&A card. The card must teach a MENTAL SHORTCUT or LOGIC METHOD.

Format your response EXACTLY like this:
QUESTION: [A practical math problem firefighters might encounter]
ANSWER: [The numerical answer]
LOGIC: [Step-by-step mental math method - teach HOW to solve it quickly, not just the answer. Include phrases like "Think:", "Mental shortcut:", or "Quick method:"]
HINT: [A one-line tip for remembering this technique]

Example structure:
QUESTION: What is 15% of $80?
ANSWER: $12.00
LOGIC: Find 10% (move decimal left = 8.0). Find 5% (half of 10% = 4.0). Add them: 8 + 4 = 12.
HINT: Decomposition: 15% = 10% + 5%

Make the problem realistic for fire service contexts when possible (GPM, tank capacity, hose lengths, etc.)
Avoid duplicating these existing questions: {list(existing_fronts)[:10]}"""


def get_mechanical_prompt(topic: str, existing_fronts: set) -> str:
    """Generate a pattern-recognition mechanical aptitude flashcard prompt."""
    return f"""Generate ONE pattern-recognition flashcard for firefighter exam mechanical aptitude prep.

Topic: **{topic}**

IMPORTANT: This is NOT a simple definition card. The card must teach LOGIC, REASONING, or a MNEMONIC.

Format your response EXACTLY like this:
QUESTION: [A conceptual question about mechanical principles]
ANSWER: [The correct answer]
LOGIC: [Clear explanation of WHY this is the answer - include physics principles, mnemonics (like FRE 1-2-3 for levers), or calculation methods]
HINT: [A one-line memory aid or quick rule]

Example structure:
QUESTION: A wheelbarrow is an example of which class of lever?
ANSWER: Class 2
LOGIC: The Load (Resistance) is in the middle between the handles (Effort) and the wheel (Fulcrum). Remember FRE 1-2-3: Class 2 has R (Resistance) in the middle.
HINT: Class 2 = Load in middle (wheelbarrow, nutcracker)

Focus on practical applications firefighters would encounter (ladders, tools, hose operations, hydraulics).
Avoid duplicating these existing questions: {list(existing_fronts)[:10]}"""


# =============================================================================
# QA CHECKS
# =============================================================================

def check_duplicate(new_front: str, existing_fronts: set, threshold: float = 0.80) -> tuple[bool, str]:
    """Check for duplicate cards using fuzzy matching."""
    new_text = new_front.lower().strip()
    
    for ex in existing_fronts:
        ex_text = ex.lower().strip()
        ratio = SequenceMatcher(None, new_text, ex_text).ratio()
        if ratio > threshold:
            return False, f"Duplicate detected (similarity: {ratio:.1%}) with: '{ex[:50]}...'"
    
    return True, "OK"


def check_required_fields(card: dict) -> tuple[bool, str]:
    """Validate card has required fields."""
    required = ["question", "answer", "logic"]
    for field in required:
        if field not in card or not card[field].strip():
            return False, f"Missing or empty field: {field}"
    return True, "OK"


def check_logic_quality(card: dict) -> tuple[bool, str]:
    """Check that logic field actually teaches something."""
    logic = card.get("logic", "")
    if len(logic.split()) < 10:
        return False, f"Logic too short ({len(logic.split())} words, need 10+)"
    
    # Check for teaching keywords
    teaching_keywords = ["because", "since", "therefore", "think", "method", "shortcut", 
                        "calculate", "divide", "multiply", "remember", "mnemonic", 
                        "formula", "rule", "principle", "ratio", "class"]
    if not any(kw in logic.lower() for kw in teaching_keywords):
        return False, "Logic doesn't appear to teach a method"
    
    return True, "OK"


def run_qa_checks(card: dict, existing_fronts: set) -> tuple[bool, list[str]]:
    """Run all QA checks on a flashcard."""
    issues = []
    
    checks = [
        check_required_fields(card),
        check_duplicate(card.get("question", ""), existing_fronts),
        check_logic_quality(card),
    ]
    
    all_passed = True
    for passed, message in checks:
        if not passed:
            issues.append(message)
            all_passed = False
    
    return all_passed, issues


# =============================================================================
# PARSING
# =============================================================================

def parse_response(response: str) -> dict | None:
    """Parse AI response into card dict."""
    lines = response.strip().split("\n")
    card = {}
    
    current_field = None
    current_content = []
    
    for line in lines:
        line_upper = line.upper()
        if line_upper.startswith("QUESTION:"):
            if current_field:
                card[current_field] = " ".join(current_content).strip()
            current_field = "question"
            current_content = [line.split(":", 1)[1].strip() if ":" in line else ""]
        elif line_upper.startswith("ANSWER:"):
            if current_field:
                card[current_field] = " ".join(current_content).strip()
            current_field = "answer"
            current_content = [line.split(":", 1)[1].strip() if ":" in line else ""]
        elif line_upper.startswith("LOGIC:"):
            if current_field:
                card[current_field] = " ".join(current_content).strip()
            current_field = "logic"
            current_content = [line.split(":", 1)[1].strip() if ":" in line else ""]
        elif line_upper.startswith("HINT:"):
            if current_field:
                card[current_field] = " ".join(current_content).strip()
            current_field = "hint"
            current_content = [line.split(":", 1)[1].strip() if ":" in line else ""]
        elif current_field:
            current_content.append(line.strip())
    
    # Add last field
    if current_field:
        card[current_field] = " ".join(current_content).strip()
    
    if card.get("question") and card.get("answer") and card.get("logic"):
        # Build front and back content
        card["front_content"] = card["question"]
        card["back_content"] = f"{card['answer']}\n\n**Logic:** {card['logic']}"
        return card
    
    return None


# =============================================================================
# GENERATION
# =============================================================================

async def generate_flashcards(
    subject: str,
    count: int,
    batch_size: int = 5,
    dry_run: bool = False
) -> dict:
    """Generate pattern-recognition flashcards for a subject."""
    
    # Initialize Gemini model directly
    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT not set. Check credentials.")
        return {"error": "No project ID"}
    
    model = GenerativeModel(
        "gemini-2.5-flash",
        system_instruction=["""You are a firefighter exam prep expert. Generate flashcards that teach 
pattern recognition and mental shortcuts, not just rote memorization. Each card should teach 
the LOGIC behind the answer, not just the answer itself."""]
    )
    
    topics = MATH_TOPICS if subject == "math" else MECHANICAL_TOPICS
    
    stats = {
        "generated": 0,
        "passed": 0,
        "failed": 0,
        "failures": []
    }
    
    # Load existing flashcards for duplicate detection
    existing = db.get_random_flashcards([subject], 1000, approved_only=False)
    existing_fronts = {c["front_content"] for c in existing}
    generated_fronts = set()
    
    print(f"\n📊 Existing {subject} flashcards: {len(existing)}")
    print(f"🎯 Target: {count} new cards")
    
    used_topics = set()
    attempts = 0
    max_attempts = count * 2  # Allow retries for failed cards
    
    while stats["passed"] < count and attempts < max_attempts:
        attempts += 1
        
        # Select a random topic
        available_topics = [t for t in topics if t not in used_topics]
        if not available_topics:
            used_topics.clear()  # Reset if we've used all topics
            available_topics = topics
        
        topic = random.choice(available_topics)
        used_topics.add(topic)
        
        try:
            # Generate prompt
            if subject == "math":
                prompt = get_math_prompt(topic, existing_fronts | generated_fronts)
            else:
                prompt = get_mechanical_prompt(topic, existing_fronts | generated_fronts)
            
            # Generate card using Gemini directly
            config = GenerationConfig(
                temperature=0.8,
                max_output_tokens=512,
            )
            response = model.generate_content(prompt, generation_config=config)
            response_text = response.text
            
            card = parse_response(response_text)
            
            if not card:
                print(f"  ⚠️ #{attempts} parse failed for topic: {topic[:30]}")
                stats["failed"] += 1
                continue
            
            stats["generated"] += 1
            
            # Run QA checks
            passed, issues = run_qa_checks(card, existing_fronts | generated_fronts)
            
            if passed:
                print(f"  ✅ #{stats['passed']+1}/{count}: {card['front_content'][:50]}...")
                
                if not dry_run:
                    flashcard_id = db.add_flashcard(
                        subject=subject,
                        card_type="pattern_recognition",
                        front_content=card["front_content"],
                        back_content=card["back_content"],
                        hint=card.get("hint"),
                        source="pattern_recognition_generator",
                        is_approved=True
                    )
                    card["id"] = flashcard_id
                
                generated_fronts.add(card["front_content"])
                stats["passed"] += 1
            else:
                print(f"  ❌ #{attempts} FAIL: {', '.join(issues)}")
                stats["failures"].append({"card": card, "issues": issues, "topic": topic})
                stats["failed"] += 1
            
            # Small delay between cards
            await asyncio.sleep(0.3)
            
        except Exception as e:
            print(f"  ⚠️ #{attempts} error: {e}")
            stats["failed"] += 1
            await asyncio.sleep(1)
    
    return stats



# =============================================================================
# MAIN
# =============================================================================

async def main_async(args):
    """Main async function."""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║     📇 PATTERN RECOGNITION FLASHCARD GENERATOR 📇            ║
╠══════════════════════════════════════════════════════════════╣
║  Subjects: math, mechanical-aptitude                         ║
║  Cards per subject: {args.count:<40} ║
║  Mode: {'DRY RUN' if args.dry_run else 'LIVE (saving to DB)':<52} ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Show current stats
    print("📊 Current Flashcard Bank:")
    for s in ["math", "mechanical-aptitude"]:
        count = db.get_flashcard_count(subject=s)
        print(f"   {s}: {count}")
    print()
    
    total_stats = {"passed": 0, "failed": 0, "by_subject": {}}
    
    for subject in ["math", "mechanical-aptitude"]:
        print(f"\n{'='*60}")
        print(f"🔄 Generating {args.count} {subject} pattern-recognition cards")
        print(f"{'='*60}")
        
        stats = await generate_flashcards(
            subject=subject,
            count=args.count,
            batch_size=args.batch_size,
            dry_run=args.dry_run
        )
        
        total_stats["by_subject"][subject] = stats
        total_stats["passed"] += stats.get("passed", 0)
        total_stats["failed"] += stats.get("failed", 0)
        
        print(f"\n📊 {subject}: {stats.get('passed', 0)} passed, {stats.get('failed', 0)} failed")
    
    # Print summary
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    📊 GENERATION SUMMARY                     ║
╠══════════════════════════════════════════════════════════════╣
║  Total Passed QA: {total_stats['passed']:<42} ║
║  Total Failed: {total_stats['failed']:<46} ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Show updated stats
    if not args.dry_run:
        print("\n📊 Updated Flashcard Bank:")
        for s in ["math", "mechanical-aptitude"]:
            count = db.get_flashcard_count(subject=s)
            print(f"   {s}: {count}")
    
    return total_stats


def main():
    parser = argparse.ArgumentParser(description="Generate pattern-recognition flashcards")
    parser.add_argument("--count", type=int, default=100,
                       help="Flashcards per subject (default: 100)")
    parser.add_argument("--batch-size", type=int, default=5,
                       help="Batch size for generation (default: 5)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Run without saving to database")
    
    args = parser.parse_args()
    
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()

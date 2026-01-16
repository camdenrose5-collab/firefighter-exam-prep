#!/usr/bin/env python3
"""
Flashcard Bank Generator

Batch generates flashcards using AI and stores them in the SQLite database with QA checks.
Supports three card types:
- term_definition: Classic vocabulary/terminology cards
- scenario_action: Human relations scenario -> best action cards
- fill_blank: Formula/procedure fill-in-the-blank cards

Usage:
    python generate_flashcard_bank.py --subjects all --count 100
    python generate_flashcard_bank.py --subjects human-relations --card-type scenario_action --count 50
    python generate_flashcard_bank.py --subjects math --count 20 --dry-run
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

from app.features.tutor import create_tutor_engine
from app import db


# =============================================================================
# CARD TYPE CONFIGURATIONS
# =============================================================================

CARD_TYPE_PROMPTS = {
    "term_definition": {
        "human-relations": """Generate ONE flashcard for firefighter exam prep on Human Relations.
Create a term/definition card about: teamwork, communication, leadership, conflict resolution, or station culture.

Return in this exact format:
TERM: [A specific fire service term or leadership concept]
DEFINITION: [A clear, concise definition in 1-2 sentences]
SOURCE: Human Relations""",

        "mechanical-aptitude": """Generate ONE flashcard for firefighter exam prep on Mechanical Aptitude.
Create a term/definition card about: fire tools, hydraulics, pumps, mechanical advantage, or leverage.

Return in this exact format:
TERM: [A specific tool, equipment, or mechanical concept]
DEFINITION: [A clear, concise definition in 1-2 sentences]
SOURCE: Mechanical Aptitude""",

        "reading-ability": """Generate ONE flashcard for firefighter exam prep on Reading Comprehension.
Create a term/definition card about: SOP terminology, fire codes, NFPA standards, or incident command.

Return in this exact format:
TERM: [A specific fire service term or acronym]
DEFINITION: [A clear, concise definition in 1-2 sentences]
SOURCE: SOPs & Standards""",

        "math": """Generate ONE flashcard for firefighter exam prep on Fire Math.
Create a term/definition card about: flow rates, friction loss, percentages, or pump calculations.

Return in this exact format:
TERM: [A specific formula name or calculation concept]
DEFINITION: [The formula and brief explanation]
SOURCE: Fire Math"""
    },

    "scenario_action": {
        "human-relations": """Generate ONE flashcard for firefighter exam prep on Human Relations.
Create a SCENARIO -> ACTION card testing decision-making.

IMPORTANT: Follow "Frictionless Logic" - always prioritize private, peer-to-peer resolution at the lowest level.

Return in this exact format:
SCENARIO: [A realistic firehouse scenario requiring judgment - 1-2 sentences]
ACTION: [The best response following frictionless logic - 1-2 sentences]
SOURCE: Human Relations""",

        "default": """Generate ONE flashcard for firefighter exam prep.
Create a SCENARIO -> ACTION card.

Return in this exact format:
SCENARIO: [A realistic fire service scenario - 1-2 sentences]
ACTION: [The correct response - 1-2 sentences]
SOURCE: Fire Service"""
    },

    "fill_blank": {
        "math": """Generate ONE flashcard for firefighter exam prep on Fire Math.
Create a FILL-IN-THE-BLANK card testing specific numeric knowledge.

Return in this exact format:
PROMPT: [A question with a blank, e.g., "Standard handline flow rate is ___ GPM"]
ANSWER: [The correct value, e.g., "150-200 GPM"]
SOURCE: Fire Math""",

        "mechanical-aptitude": """Generate ONE flashcard for firefighter exam prep on Mechanical Aptitude.
Create a FILL-IN-THE-BLANK card testing technical knowledge.

Return in this exact format:
PROMPT: [A question with a blank about tools or equipment]
ANSWER: [The correct answer]
SOURCE: Mechanical Aptitude""",

        "default": """Generate ONE flashcard for firefighter exam prep.
Create a FILL-IN-THE-BLANK card.

Return in this exact format:
PROMPT: [A question with a blank]
ANSWER: [The correct value]
SOURCE: Fire Service"""
    }
}

# Subject to card type mapping (which types work best for each subject)
SUBJECT_CARD_TYPES = {
    "human-relations": ["term_definition", "scenario_action"],
    "mechanical-aptitude": ["term_definition", "fill_blank"],
    "reading-ability": ["term_definition"],
    "math": ["term_definition", "fill_blank"]
}


# =============================================================================
# QA CHECKS
# =============================================================================

def check_required_fields(card: dict, card_type: str) -> tuple[bool, str]:
    """Validate card has required fields."""
    if card_type == "term_definition":
        required = ["term", "definition"]
    elif card_type == "scenario_action":
        required = ["scenario", "action"]
    elif card_type == "fill_blank":
        required = ["prompt", "answer"]
    else:
        return False, f"Unknown card type: {card_type}"
    
    for field in required:
        if field not in card or not card[field].strip():
            return False, f"Missing or empty field: {field}"
    
    return True, "OK"


def check_content_length(card: dict, min_words: int = 5) -> tuple[bool, str]:
    """Check back_content has minimum word count (terms can be short)."""
    back = card.get("back_content", card.get("definition", card.get("action", card.get("answer", ""))))
    if isinstance(back, str):
        words = back.split()
        if len(words) < min_words:
            return False, f"back_content too short ({len(words)} words, min {min_words})"
    return True, "OK"


def check_duplicate(card: dict, existing: list, threshold: float = 0.85) -> tuple[bool, str]:
    """Check for duplicate cards using fuzzy matching."""
    # Use front_content for comparison
    new_text = card.get("front_content", "").lower()
    if not new_text:
        new_text = card.get("term", card.get("scenario", card.get("prompt", ""))).lower()
    
    for ex in existing:
        ex_text = ex.get("front_content", "").lower()
        ratio = SequenceMatcher(None, new_text, ex_text).ratio()
        if ratio > threshold:
            return False, f"Duplicate detected (similarity: {ratio:.2%})"
    
    return True, "OK"


def run_qa_checks(card: dict, card_type: str, existing: list) -> tuple[bool, list[str]]:
    """Run all QA checks on a flashcard."""
    issues = []
    
    checks = [
        ("Required Fields", check_required_fields(card, card_type)),
        ("Content Length", check_content_length(card)),
        ("Duplicate Check", check_duplicate(card, existing)),
    ]
    
    all_passed = True
    for check_name, (passed, message) in checks:
        if not passed:
            issues.append(f"{check_name}: {message}")
            all_passed = False
    
    return all_passed, issues


# =============================================================================
# PARSING
# =============================================================================

def parse_response(response: str, card_type: str) -> dict | None:
    """Parse AI response into card dict."""
    lines = response.strip().split("\n")
    card = {}
    
    if card_type == "term_definition":
        for line in lines:
            if line.startswith("TERM:"):
                card["term"] = line.replace("TERM:", "").strip()
            elif line.startswith("DEFINITION:"):
                card["definition"] = line.replace("DEFINITION:", "").strip()
            elif line.startswith("SOURCE:"):
                card["source"] = line.replace("SOURCE:", "").strip()
        
        if card.get("term") and card.get("definition"):
            card["front_content"] = card["term"]
            card["back_content"] = card["definition"]
            return card
            
    elif card_type == "scenario_action":
        for line in lines:
            if line.startswith("SCENARIO:"):
                card["scenario"] = line.replace("SCENARIO:", "").strip()
            elif line.startswith("ACTION:"):
                card["action"] = line.replace("ACTION:", "").strip()
            elif line.startswith("SOURCE:"):
                card["source"] = line.replace("SOURCE:", "").strip()
        
        if card.get("scenario") and card.get("action"):
            card["front_content"] = card["scenario"]
            card["back_content"] = card["action"]
            return card
            
    elif card_type == "fill_blank":
        for line in lines:
            if line.startswith("PROMPT:"):
                card["prompt"] = line.replace("PROMPT:", "").strip()
            elif line.startswith("ANSWER:"):
                card["answer"] = line.replace("ANSWER:", "").strip()
            elif line.startswith("SOURCE:"):
                card["source"] = line.replace("SOURCE:", "").strip()
        
        if card.get("prompt") and card.get("answer"):
            card["front_content"] = card["prompt"]
            card["back_content"] = card["answer"]
            return card
    
    return None


# =============================================================================
# GENERATION
# =============================================================================

async def generate_flashcards(
    subjects: list[str],
    card_types: list[str],
    count_per_combo: int,
    batch_size: int = 5,
    dry_run: bool = False
) -> dict:
    """Generate flashcards for specified subjects and card types."""
    
    tutor_engine = create_tutor_engine()
    if not tutor_engine:
        print("❌ Failed to initialize tutor engine. Check credentials.")
        return {"error": "No tutor engine"}
    
    stats = {
        "total_generated": 0,
        "total_passed": 0,
        "total_failed": 0,
        "by_combo": {},
        "failures": []
    }
    
    for subject in subjects:
        # Filter card types to those applicable for this subject
        applicable_types = [ct for ct in card_types if ct in SUBJECT_CARD_TYPES.get(subject, ["term_definition"])]
        
        for card_type in applicable_types:
            combo_key = f"{subject}/{card_type}"
            print(f"\n{'='*60}")
            print(f"📝 Generating {count_per_combo} {card_type} cards for: {subject}")
            print(f"{'='*60}")
            
            # Load existing flashcards for duplicate detection
            existing = db.get_random_flashcards([subject], 1000, [card_type], approved_only=False)
            generated = []
            failed = []
            
            # Get prompt template
            prompts = CARD_TYPE_PROMPTS.get(card_type, {})
            prompt_template = prompts.get(subject, prompts.get("default", ""))
            
            if not prompt_template:
                print(f"  ⚠️ No prompt template for {combo_key}")
                continue
            
            batches = (count_per_combo + batch_size - 1) // batch_size
            
            for batch_num in range(batches):
                batch_start = batch_num * batch_size
                batch_end = min(batch_start + batch_size, count_per_combo)
                current_batch_size = batch_end - batch_start
                
                print(f"\n🔄 Batch {batch_num + 1}/{batches} ({current_batch_size} cards)")
                
                # Generate one at a time to avoid overwhelming the API
                for i in range(current_batch_size):
                    try:
                        response = await tutor_engine.explain("flashcard", prompt_template)
                        card = parse_response(response, card_type)
                        
                        if not card:
                            print(f"  ⚠️ Card {batch_start + i + 1} failed to parse")
                            stats["total_failed"] += 1
                            continue
                        
                        stats["total_generated"] += 1
                        
                        # Run QA checks
                        passed, issues = run_qa_checks(card, card_type, existing + generated)
                        
                        if passed:
                            print(f"  ✅ Card {batch_start + i + 1}: PASS - {card['front_content'][:40]}...")
                            
                            if not dry_run:
                                flashcard_id = db.add_flashcard(
                                    subject=subject,
                                    card_type=card_type,
                                    front_content=card["front_content"],
                                    back_content=card["back_content"],
                                    source=card.get("source"),
                                    is_approved=True
                                )
                                card["id"] = flashcard_id
                            
                            generated.append(card)
                            stats["total_passed"] += 1
                        else:
                            print(f"  ❌ Card {batch_start + i + 1}: FAIL - {', '.join(issues)}")
                            failed.append({"card": card, "issues": issues})
                            stats["total_failed"] += 1
                            
                    except Exception as e:
                        print(f"  ⚠️ Card {batch_start + i + 1} generation error: {e}")
                        stats["total_failed"] += 1
                    
                    # Small delay between cards
                    await asyncio.sleep(0.5)
                
                # Delay between batches
                if batch_num < batches - 1:
                    await asyncio.sleep(2)
            
            stats["by_combo"][combo_key] = {
                "generated": len(generated),
                "failed": len(failed)
            }
            stats["failures"].extend(failed)
            
            print(f"\n📊 {combo_key}: {len(generated)} passed, {len(failed)} failed")
    
    return stats


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Generate flashcards for the flashcard bank")
    parser.add_argument("--subjects", type=str, default="all",
                       help="Comma-separated subjects or 'all'")
    parser.add_argument("--card-types", type=str, default="all",
                       help="Comma-separated card types or 'all': term_definition, scenario_action, fill_blank")
    parser.add_argument("--count", type=int, default=50,
                       help="Flashcards per subject/card-type combo (default: 50)")
    parser.add_argument("--batch-size", type=int, default=5,
                       help="Batch size for generation (default: 5)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Run without saving to database")
    
    args = parser.parse_args()
    
    all_subjects = ["human-relations", "mechanical-aptitude", "reading-ability", "math"]
    all_card_types = ["term_definition", "scenario_action", "fill_blank"]
    
    # Parse subjects
    if args.subjects.lower() == "all":
        subjects = all_subjects
    else:
        subjects = [s.strip() for s in args.subjects.split(",")]
        for s in subjects:
            if s not in all_subjects:
                print(f"❌ Unknown subject: {s}")
                print(f"   Valid: {', '.join(all_subjects)}")
                sys.exit(1)
    
    # Parse card types
    if args.card_types.lower() == "all":
        card_types = all_card_types
    else:
        card_types = [ct.strip() for ct in args.card_types.split(",")]
        for ct in card_types:
            if ct not in all_card_types:
                print(f"❌ Unknown card type: {ct}")
                print(f"   Valid: {', '.join(all_card_types)}")
                sys.exit(1)
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           📇 FLASHCARD BANK GENERATOR 📇                     ║
╠══════════════════════════════════════════════════════════════╣
║  Subjects: {', '.join(subjects):<48} ║
║  Card Types: {', '.join(card_types):<46} ║
║  Count per combo: {args.count:<42} ║
║  Mode: {'DRY RUN' if args.dry_run else 'LIVE (saving to DB)':<52} ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Show current stats
    print("📊 Current Flashcard Bank:")
    for s in all_subjects:
        count = db.get_flashcard_count(subject=s)
        print(f"   {s}: {count}")
    print(f"   TOTAL: {db.get_flashcard_count()}")
    print()
    
    # Run generation
    start_time = datetime.now()
    stats = asyncio.run(generate_flashcards(
        subjects=subjects,
        card_types=card_types,
        count_per_combo=args.count,
        batch_size=args.batch_size,
        dry_run=args.dry_run
    ))
    end_time = datetime.now()
    duration = end_time - start_time
    
    # Print summary
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    📊 GENERATION SUMMARY                     ║
╠══════════════════════════════════════════════════════════════╣
║  Duration: {str(duration):<49} ║
║  Total Generated: {stats.get('total_generated', 0):<42} ║
║  Total Passed QA: {stats.get('total_passed', 0):<42} ║
║  Total Failed: {stats.get('total_failed', 0):<45} ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Save failure report if any
    if stats.get("failures"):
        report_path = Path(__file__).parent / "flashcard_generation_report.json"
        with open(report_path, "w") as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "stats": stats
            }, f, indent=2, default=str)
        print(f"📝 Failure report saved to: {report_path}")
    
    # Show updated stats
    if not args.dry_run:
        print("\n📊 Updated Flashcard Bank:")
        for s in all_subjects:
            count = db.get_flashcard_count(subject=s)
            print(f"   {s}: {count}")
        print(f"   TOTAL: {db.get_flashcard_count()}")


if __name__ == "__main__":
    main()

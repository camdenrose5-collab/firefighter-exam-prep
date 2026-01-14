#!/usr/bin/env python3
"""
Question Bank Generator

Batch generates quiz questions using the Fire Captain Quiz Engine
and stores them in the SQLite database with QA checks.

Usage:
    python generate_question_bank.py --subjects all --count 500
    python generate_question_bank.py --subjects human-relations --count 100 --dry-run
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

# Load environment variables from backend/.env
from dotenv import load_dotenv
load_dotenv(backend_path / ".env")

from app.features.quiz_engine import create_quiz_engine
from app import db


# =============================================================================
# QA CHECKS
# =============================================================================

def check_json_structure(question: dict) -> tuple[bool, str]:
    """Validate question has required fields."""
    required = ["question", "options", "correct_answer", "explanation"]
    for field in required:
        if field not in question:
            return False, f"Missing field: {field}"
    
    if not isinstance(question["options"], list) or len(question["options"]) != 4:
        return False, "Options must be a list of 4 items"
    
    return True, "OK"


def check_correct_answer(question: dict) -> tuple[bool, str]:
    """Verify correct_answer exists in options."""
    if question["correct_answer"] not in question["options"]:
        return False, f"Correct answer not in options: {question['correct_answer']}"
    return True, "OK"


def check_explanation_length(question: dict, min_words: int = 10) -> tuple[bool, str]:
    """Check explanation has minimum word count."""
    words = question["explanation"].split()
    if len(words) < min_words:
        return False, f"Explanation too short ({len(words)} words, min {min_words})"
    return True, "OK"


def check_duplicate(question: dict, existing_questions: list, threshold: float = 0.85) -> tuple[bool, str]:
    """Check for duplicate questions using fuzzy matching."""
    new_text = question["question"].lower()
    
    for existing in existing_questions:
        existing_text = existing["question"].lower()
        ratio = SequenceMatcher(None, new_text, existing_text).ratio()
        if ratio > threshold:
            return False, f"Duplicate detected (similarity: {ratio:.2%})"
    
    return True, "OK"


def run_qa_checks(question: dict, existing_questions: list) -> tuple[bool, list[str]]:
    """Run all QA checks on a question."""
    issues = []
    
    checks = [
        ("JSON Structure", check_json_structure(question)),
        ("Correct Answer", check_correct_answer(question)),
        ("Explanation Length", check_explanation_length(question)),
        ("Duplicate Check", check_duplicate(question, existing_questions)),
    ]
    
    all_passed = True
    for check_name, (passed, message) in checks:
        if not passed:
            issues.append(f"{check_name}: {message}")
            all_passed = False
    
    return all_passed, issues


# =============================================================================
# GENERATION
# =============================================================================

async def generate_questions(
    subjects: list[str],
    count_per_subject: int,
    batch_size: int = 10,
    dry_run: bool = False
) -> dict:
    """Generate questions for specified subjects."""
    
    # Create quiz engine
    quiz_engine = create_quiz_engine()
    
    stats = {
        "total_generated": 0,
        "total_passed": 0,
        "total_failed": 0,
        "by_subject": {},
        "failures": []
    }
    
    for subject in subjects:
        print(f"\n{'='*60}")
        print(f"📚 Generating {count_per_subject} questions for: {subject}")
        print(f"{'='*60}")
        
        # Load existing questions for duplicate detection
        existing = db.get_random_questions([subject], 1000, approved_only=False)
        generated = []
        failed = []
        
        batches = (count_per_subject + batch_size - 1) // batch_size
        
        for batch_num in range(batches):
            batch_start = batch_num * batch_size
            batch_end = min(batch_start + batch_size, count_per_subject)
            current_batch_size = batch_end - batch_start
            
            print(f"\n🔄 Batch {batch_num + 1}/{batches} ({current_batch_size} questions)")
            
            # Generate in parallel
            tasks = [quiz_engine.generate_quiz_question(subject) for _ in range(current_batch_size)]
            
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                print(f"  ❌ Batch failed: {e}")
                continue
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"  ⚠️ Question {batch_start + i + 1} failed to generate: {result}")
                    stats["total_failed"] += 1
                    continue
                
                stats["total_generated"] += 1
                
                # Run QA checks
                passed, issues = run_qa_checks(result, existing + generated)
                
                if passed:
                    print(f"  ✅ Q{batch_start + i + 1}: PASS")
                    
                    if not dry_run:
                        # Save to database
                        question_id = db.add_question(
                            subject=subject,
                            question=result["question"],
                            options=result["options"],
                            correct_answer=result["correct_answer"],
                            explanation=result["explanation"],
                            is_approved=True
                        )
                        result["id"] = question_id
                    
                    generated.append(result)
                    stats["total_passed"] += 1
                else:
                    print(f"  ❌ Q{batch_start + i + 1}: FAIL - {', '.join(issues)}")
                    failed.append({
                        "question": result,
                        "issues": issues
                    })
                    stats["total_failed"] += 1
            
            # Small delay between batches to avoid rate limiting
            if batch_num < batches - 1:
                await asyncio.sleep(2)
        
        stats["by_subject"][subject] = {
            "generated": len(generated),
            "failed": len(failed)
        }
        stats["failures"].extend(failed)
        
        print(f"\n📊 {subject}: {len(generated)} passed, {len(failed)} failed")
    
    return stats


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Generate quiz questions for the question bank")
    parser.add_argument("--subjects", type=str, default="all", 
                       help="Comma-separated subjects or 'all'")
    parser.add_argument("--count", type=int, default=500,
                       help="Questions per subject (default: 500)")
    parser.add_argument("--batch-size", type=int, default=10,
                       help="Batch size for parallel generation (default: 10)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Run without saving to database")
    
    args = parser.parse_args()
    
    all_subjects = ["human-relations", "mechanical-aptitude", "reading-ability", "math"]
    
    if args.subjects.lower() == "all":
        subjects = all_subjects
    else:
        subjects = [s.strip() for s in args.subjects.split(",")]
        for s in subjects:
            if s not in all_subjects:
                print(f"❌ Unknown subject: {s}")
                print(f"   Valid subjects: {', '.join(all_subjects)}")
                sys.exit(1)
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           🔥 QUESTION BANK GENERATOR 🔥                      ║
╠══════════════════════════════════════════════════════════════╣
║  Subjects: {', '.join(subjects):<48} ║
║  Count per subject: {args.count:<40} ║
║  Batch size: {args.batch_size:<47} ║
║  Mode: {'DRY RUN' if args.dry_run else 'LIVE (saving to DB)':<52} ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Show current bank stats
    print("📊 Current Question Bank:")
    for s in all_subjects:
        count = db.get_question_count(s)
        print(f"   {s}: {count}")
    print(f"   TOTAL: {db.get_question_count()}")
    print()
    
    # Run generation
    start_time = datetime.now()
    stats = asyncio.run(generate_questions(
        subjects=subjects,
        count_per_subject=args.count,
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
║  Total Generated: {stats['total_generated']:<42} ║
║  Total Passed QA: {stats['total_passed']:<42} ║
║  Total Failed: {stats['total_failed']:<45} ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Save failure report
    if stats["failures"]:
        report_path = Path(__file__).parent / "generation_report.json"
        with open(report_path, "w") as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "stats": stats,
                "failures": stats["failures"]
            }, f, indent=2)
        print(f"📝 Failure report saved to: {report_path}")
    
    # Show updated bank stats
    if not args.dry_run:
        print("\n📊 Updated Question Bank:")
        for s in all_subjects:
            count = db.get_question_count(s)
            print(f"   {s}: {count}")
        print(f"   TOTAL: {db.get_question_count()}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Question Bank Inspector
View random questions from the local database for quality review.
"""

import sys
import json
import textwrap
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from app import db

def inspect_questions(count=5):
    print(f"\n🔍 Inspecting {count} random questions from the bank...\n")
    
    questions = db.get_random_questions(
        subjects=["human-relations", "mechanical-aptitude", "reading-ability", "math"],
        count=count,
        approved_only=True
    )
    
    if not questions:
        print("❌ No questions found in database.")
        print("   Run: python execution/generate_question_bank.py --subjects all --count 10 --dry-run")
        return

    for i, q in enumerate(questions, 1):
        print(f"╔{'═'*78}╗")
        print(f"║ QUESTION {i}  ({q['subject']})")
        print(f"╠{'═'*78}╝")
        
        # Print Question
        print(textwrap.fill(q['question'], width=80))
        print(f"\nOPTIONS:")
        for idx, opt in enumerate(q['options']):
            marker = "✅" if opt == q['correct_answer'] else "  "
            print(f" {marker} {chr(65+idx)}. {opt}")
            
        print(f"\n📝 EXPLANATION:")
        print(textwrap.fill(q['explanation'], width=80))
        print("\n")

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    inspect_questions(count)

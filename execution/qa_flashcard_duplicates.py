#!/usr/bin/env python3
"""
QA Check: Find duplicate flashcards across all subjects.
"""

import sys
from pathlib import Path
from difflib import SequenceMatcher
from collections import defaultdict

backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))
from app import db


def find_duplicates(threshold: float = 0.85):
    """Find duplicate flashcards across all subjects."""
    
    subjects = ["math", "mechanical-aptitude", "fire-terms", "human-relations"]
    all_cards = []
    
    print("=" * 60)
    print("📇 FLASHCARD QA: DUPLICATE CHECK")
    print("=" * 60)
    
    # Load all cards
    print("\n📊 Flashcard counts by subject:")
    for subject in subjects:
        cards = db.get_random_flashcards([subject], 500, approved_only=False)
        for c in cards:
            c["subject"] = subject
        all_cards.extend(cards)
        print(f"   {subject}: {len(cards)}")
    
    print(f"\n   TOTAL: {len(all_cards)}")
    
    # Find duplicates
    print(f"\n🔍 Checking for duplicates (threshold: {threshold})...")
    duplicates = []
    checked = set()
    
    for i, card1 in enumerate(all_cards):
        for j, card2 in enumerate(all_cards[i+1:], i+1):
            pair_key = (card1["id"], card2["id"])
            if pair_key in checked:
                continue
            checked.add(pair_key)
            
            ratio = SequenceMatcher(
                None, 
                card1["front_content"].lower(), 
                card2["front_content"].lower()
            ).ratio()
            
            if ratio > threshold:
                duplicates.append({
                    "card1": card1,
                    "card2": card2,
                    "similarity": ratio
                })
    
    # Report
    if duplicates:
        print(f"\n⚠️ Found {len(duplicates)} potential duplicates:\n")
        for d in duplicates:
            print(f"  [{d['similarity']:.0%}] {d['card1']['subject']} ↔ {d['card2']['subject']}")
            print(f"    1: {d['card1']['front_content'][:60]}...")
            print(f"    2: {d['card2']['front_content'][:60]}...")
            print()
    else:
        print("\n✅ No duplicates found!")
    
    return duplicates


if __name__ == "__main__":
    find_duplicates(threshold=0.85)

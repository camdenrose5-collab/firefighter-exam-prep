#!/usr/bin/env python3
"""
Import pattern-recognition flashcards from JSON files into the database.
Creates 100 Math and 100 Mechanical aptitude flashcards.

Usage:
    python import_pattern_flashcards.py
"""

import sys
import json
from pathlib import Path
from difflib import SequenceMatcher

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))
from app import db


def check_duplicate(new_front: str, existing_fronts: set, threshold: float = 0.92) -> tuple[bool, str]:
    """Check for duplicate cards using fuzzy matching."""
    new_text = new_front.lower().strip()
    for ex in existing_fronts:
        ratio = SequenceMatcher(None, new_text, ex.lower().strip()).ratio()
        if ratio > threshold:
            return True, ex
    return False, ""


def import_flashcards(cards: list, subject: str, dry_run: bool = False) -> dict:
    """Import flashcards with duplicate detection."""
    # Load existing
    existing = db.get_random_flashcards([subject], 1000, approved_only=False)
    existing_fronts = {c["front_content"] for c in existing}
    
    stats = {"imported": 0, "duplicates": 0, "errors": 0}
    
    for card in cards:
        is_dup, match = check_duplicate(card["front_content"], existing_fronts)
        if is_dup:
            print(f"  ⚠️ Duplicate: '{card['front_content'][:40]}...' matches '{match[:40]}...'")
            stats["duplicates"] += 1
            continue
        
        try:
            if not dry_run:
                db.add_flashcard(
                    subject=subject,
                    card_type="pattern_recognition",
                    front_content=card["front_content"],
                    back_content=card["back_content"],
                    hint=card.get("hint"),
                    source="manual_pattern_recognition",
                    is_approved=True
                )
            existing_fronts.add(card["front_content"])
            stats["imported"] += 1
        except Exception as e:
            print(f"  ❌ Error: {e}")
            stats["errors"] += 1
    
    return stats


# =============================================================================
# MATH FLASHCARDS (100 cards)
# =============================================================================

MATH_CARDS = [
    # --- PERCENTAGES (25 cards) ---
    {"front_content": "Find 10% of 450.", "back_content": "45\n\n**Logic:** Move the decimal one place left. 450 → 45.0", "hint": "10% = move decimal left once"},
    {"front_content": "Find 10% of 1,200 gallons.", "back_content": "120 gallons\n\n**Logic:** Move decimal left: 1,200 → 120", "hint": "10% = ÷10"},
    {"front_content": "What is 5% of 800?", "back_content": "40\n\n**Logic:** Find 10% (80), then halve it: 80 ÷ 2 = 40", "hint": "5% = half of 10%"},
    {"front_content": "Calculate 5% of 240.", "back_content": "12\n\n**Logic:** 10% = 24, then half = 12", "hint": "5% = 10% ÷ 2"},
    {"front_content": "What is 15% of 200?", "back_content": "30\n\n**Logic:** 10% = 20, 5% = 10. Add: 20 + 10 = 30", "hint": "15% = 10% + 5%"},
    {"front_content": "Find 15% of 600.", "back_content": "90\n\n**Logic:** 10% = 60, 5% = 30. Total: 60 + 30 = 90", "hint": "Break into 10% + 5%"},
    {"front_content": "Calculate 20% of 350.", "back_content": "70\n\n**Logic:** 10% = 35, double it: 35 × 2 = 70", "hint": "20% = 10% × 2"},
    {"front_content": "What is 20% of 1,500?", "back_content": "300\n\n**Logic:** 10% = 150, × 2 = 300", "hint": "20% = double the 10%"},
    {"front_content": "Find 25% of 80.", "back_content": "20\n\n**Logic:** 25% = 1/4. 80 ÷ 4 = 20", "hint": "25% = ÷4"},
    {"front_content": "Calculate 25% of 400 gallons.", "back_content": "100 gallons\n\n**Logic:** Divide by 4: 400 ÷ 4 = 100", "hint": "25% = one quarter"},
    {"front_content": "What is 50% of 750?", "back_content": "375\n\n**Logic:** Half of 750 = 375", "hint": "50% = ÷2"},
    {"front_content": "Find 50% of 1,800.", "back_content": "900\n\n**Logic:** Divide by 2: 1,800 ÷ 2 = 900", "hint": "50% = half"},
    {"front_content": "Subtract 10% from 500.", "back_content": "450\n\n**Logic:** 10% = 50. 500 - 50 = 450", "hint": "Find %, then subtract"},
    {"front_content": "Reduce 800 by 25%.", "back_content": "600\n\n**Logic:** 25% = 200. 800 - 200 = 600", "hint": "25% off = keep 75%"},
    {"front_content": "A 200ft hose is cut by 15%. What's left?", "back_content": "170ft\n\n**Logic:** 10% = 20, 5% = 10. Cut = 30. 200 - 30 = 170", "hint": "Find the cut, then subtract"},
    {"front_content": "Add 10% to 300.", "back_content": "330\n\n**Logic:** 10% = 30. 300 + 30 = 330", "hint": "Find %, then add"},
    {"front_content": "Increase 450 by 20%.", "back_content": "540\n\n**Logic:** 20% = 90. 450 + 90 = 540", "hint": "20% = 10% × 2"},
    {"front_content": "What is 30% of 500?", "back_content": "150\n\n**Logic:** 10% = 50. 50 × 3 = 150", "hint": "30% = 10% × 3"},
    {"front_content": "Find 40% of 250.", "back_content": "100\n\n**Logic:** 10% = 25. 25 × 4 = 100", "hint": "40% = 10% × 4"},
    {"front_content": "Calculate 75% of 400.", "back_content": "300\n\n**Logic:** 25% = 100. 100 × 3 = 300. Or: 50% + 25%", "hint": "75% = 50% + 25%"},
    {"front_content": "What is 1% of 2,500?", "back_content": "25\n\n**Logic:** Move decimal left twice: 2500 → 25.00", "hint": "1% = ÷100"},
    {"front_content": "Find 2% of 1,500.", "back_content": "30\n\n**Logic:** 1% = 15, × 2 = 30", "hint": "2% = 1% × 2"},
    {"front_content": "What is 33% of 300?", "back_content": "~100 (99)\n\n**Logic:** 33% ≈ 1/3. 300 ÷ 3 = 100", "hint": "33% ≈ one-third"},
    {"front_content": "Calculate 90% of 500.", "back_content": "450\n\n**Logic:** 10% = 50. 500 - 50 = 450. (90% = 100% - 10%)", "hint": "90% = subtract 10%"},
    {"front_content": "Find 12.5% of 800.", "back_content": "100\n\n**Logic:** 12.5% = 1/8. 800 ÷ 8 = 100", "hint": "12.5% = ÷8"},
    
    # --- FRACTIONS (20 cards) ---
    {"front_content": "A tank is 1/4 full. Capacity: 800 gallons. How much water?", "back_content": "200 gallons\n\n**Logic:** 800 ÷ 4 = 200", "hint": "Divide by denominator"},
    {"front_content": "Find 1/3 of 900.", "back_content": "300\n\n**Logic:** 900 ÷ 3 = 300", "hint": "1/3 = ÷3"},
    {"front_content": "What is 3/4 of 200?", "back_content": "150\n\n**Logic:** 1/4 = 50. 50 × 3 = 150", "hint": "Find 1/4, then × 3"},
    {"front_content": "Calculate 2/5 of 500.", "back_content": "200\n\n**Logic:** 1/5 = 100. 100 × 2 = 200", "hint": "Find unit fraction first"},
    {"front_content": "What is 5/8 of 400?", "back_content": "250\n\n**Logic:** 1/8 = 50. 50 × 5 = 250", "hint": "1/8 = ÷8, then × numerator"},
    {"front_content": "Convert 3/4 to decimal.", "back_content": "0.75\n\n**Logic:** 3 ÷ 4 = 0.75. Or: 1/4 = 0.25, × 3 = 0.75", "hint": "Common: 1/4=0.25, 1/2=0.5, 3/4=0.75"},
    {"front_content": "Convert 0.625 to a fraction.", "back_content": "5/8\n\n**Logic:** 0.625 = 625/1000 = 5/8", "hint": "Know your eighths: 0.125, 0.25, 0.375..."},
    {"front_content": "What is 1/8 as a decimal?", "back_content": "0.125\n\n**Logic:** 1 ÷ 8 = 0.125", "hint": "Memorize: 1/8 = 0.125"},
    {"front_content": "Convert 2/3 to a percentage.", "back_content": "≈67% (66.67%)\n\n**Logic:** 2 ÷ 3 = 0.667 → 66.7%", "hint": "2/3 ≈ 67%"},
    {"front_content": "What fraction is equal to 40%?", "back_content": "2/5\n\n**Logic:** 40/100 = 4/10 = 2/5", "hint": "Simplify 40/100"},
    {"front_content": "Add: 1/4 + 1/2", "back_content": "3/4\n\n**Logic:** Convert 1/2 = 2/4. Then 1/4 + 2/4 = 3/4", "hint": "Find common denominator"},
    {"front_content": "Subtract: 3/4 - 1/4", "back_content": "1/2\n\n**Logic:** 3/4 - 1/4 = 2/4 = 1/2", "hint": "Same denominator: subtract numerators"},
    {"front_content": "What is 7/8 as a decimal?", "back_content": "0.875\n\n**Logic:** 1/8 = 0.125. 0.125 × 7 = 0.875", "hint": "7 × 0.125"},
    {"front_content": "Simplify 12/16.", "back_content": "3/4\n\n**Logic:** Divide both by 4: 12÷4=3, 16÷4=4", "hint": "Find GCF"},
    {"front_content": "Convert 0.6 to a fraction.", "back_content": "3/5\n\n**Logic:** 0.6 = 6/10 = 3/5", "hint": "6/10 simplified"},
    {"front_content": "What is 1/5 of 750?", "back_content": "150\n\n**Logic:** 750 ÷ 5 = 150", "hint": "1/5 = ÷5"},
    {"front_content": "Find 4/5 of 250.", "back_content": "200\n\n**Logic:** 1/5 = 50. 50 × 4 = 200", "hint": "Find 1/5, multiply by 4"},
    {"front_content": "What is 0.375 as a fraction?", "back_content": "3/8\n\n**Logic:** 0.375 = 375/1000 = 3/8", "hint": "0.375 = Three-eighths"},
    {"front_content": "Express 5/4 as a mixed number.", "back_content": "1 1/4\n\n**Logic:** 5÷4 = 1 remainder 1 = 1 1/4", "hint": "Divide, remainder becomes fraction"},
    {"front_content": "Convert 2 3/4 to an improper fraction.", "back_content": "11/4\n\n**Logic:** 2×4 + 3 = 11 → 11/4", "hint": "(whole × denom) + numer"},
    
    # --- DIVISION & ESTIMATION (20 cards) ---
    {"front_content": "Estimate: 792 ÷ 19", "back_content": "≈40\n\n**Logic:** Round to 800 ÷ 20 = 40. Actual: 41.7", "hint": "Round to friendly numbers"},
    {"front_content": "Estimate: 498 ÷ 12", "back_content": "≈40-42\n\n**Logic:** 500 ÷ 12 ≈ 500 ÷ 10 = 50, adjust down. Or 480÷12=40", "hint": "Find closest divisible number"},
    {"front_content": "If 144 ÷ 12 = X, what is 12 × X?", "back_content": "144\n\n**Logic:** Division and multiplication are inverses. X = 12, so 12 × 12 = 144", "hint": "Check division with multiplication"},
    {"front_content": "Estimate: 1,247 ÷ 25", "back_content": "≈50\n\n**Logic:** 1,250 ÷ 25 = 50. (25 × 4 = 100, so 1250 ÷ 25 = 50)", "hint": "25 goes into 100 four times"},
    {"front_content": "Divide 750 by 15 mentally.", "back_content": "50\n\n**Logic:** 750 ÷ 15 = 750 ÷ 3 ÷ 5 = 250 ÷ 5 = 50", "hint": "Break up divisor: 15 = 3 × 5"},
    {"front_content": "What is 360 ÷ 9?", "back_content": "40\n\n**Logic:** 36 ÷ 9 = 4, so 360 ÷ 9 = 40", "hint": "Use known facts, adjust zeros"},
    {"front_content": "Calculate 625 ÷ 25.", "back_content": "25\n\n**Logic:** 25 × 25 = 625", "hint": "25² = 625"},
    {"front_content": "Estimate: 3,800 ÷ 19", "back_content": "≈200\n\n**Logic:** 3,800 ÷ 20 = 190 ≈ 200", "hint": "Round 19 → 20"},
    {"front_content": "What is 12 × 12?", "back_content": "144\n\n**Logic:** Common square to memorize", "hint": "12² = 144"},
    {"front_content": "What is 15 × 15?", "back_content": "225\n\n**Logic:** Common square: 15² = 225", "hint": "15² = 225"},
    {"front_content": "Multiply 25 × 8 quickly.", "back_content": "200\n\n**Logic:** 25 × 4 = 100, × 2 = 200. Or: 8 × 25 = 8 × 100 ÷ 4 = 200", "hint": "25 × 4 = 100"},
    {"front_content": "Calculate 50 × 16.", "back_content": "800\n\n**Logic:** 50 × 16 = 100 × 8 = 800 (halve 16, double 50)", "hint": "Double/halve method"},
    {"front_content": "What is 125 × 8?", "back_content": "1,000\n\n**Logic:** 125 × 8 = 1,000 (memorize this)", "hint": "125 × 8 = 1,000"},
    {"front_content": "Estimate: 97 × 6", "back_content": "≈600\n\n**Logic:** 100 × 6 = 600 (actual: 582)", "hint": "Round 97 → 100"},
    {"front_content": "Calculate 99 × 7 using a shortcut.", "back_content": "693\n\n**Logic:** (100 × 7) - 7 = 700 - 7 = 693", "hint": "99 × n = 100n - n"},
    {"front_content": "What is 48 ÷ 4?", "back_content": "12\n\n**Logic:** 48 ÷ 4 = 12. Quick: 40÷4=10, 8÷4=2, sum=12", "hint": "Split: (40+8)÷4"},
    {"front_content": "Divide 84 by 7.", "back_content": "12\n\n**Logic:** 7 × 12 = 84", "hint": "Use times tables"},
    {"front_content": "Estimate: 405 ÷ 8", "back_content": "≈50\n\n**Logic:** 400 ÷ 8 = 50", "hint": "Round to nearest friendly number"},
    {"front_content": "What is 1,800 ÷ 30?", "back_content": "60\n\n**Logic:** 180 ÷ 3 = 60, adjust zeros: 1,800 ÷ 30 = 60", "hint": "Cancel zeros first"},
    {"front_content": "Calculate 720 ÷ 12.", "back_content": "60\n\n**Logic:** 72 ÷ 12 = 6, so 720 ÷ 12 = 60", "hint": "Scale up/down from known facts"},
    
    # --- FIRE SERVICE CALCULATIONS (20 cards) ---
    {"front_content": "Pump flows 250 GPM. How long to empty 2,500-gallon tank?", "back_content": "10 minutes\n\n**Logic:** Time = Volume ÷ Rate. 2,500 ÷ 250 = 10", "hint": "Time = Volume ÷ Rate"},
    {"front_content": "Engine carries 500 gallons, flowing 125 GPM. Water duration?", "back_content": "4 minutes\n\n**Logic:** 500 ÷ 125 = 4", "hint": "Gallons ÷ GPM = Minutes"},
    {"front_content": "At 200 GPM, how many gallons in 15 minutes?", "back_content": "3,000 gallons\n\n**Logic:** 200 × 15 = 3,000", "hint": "GPM × Minutes = Gallons"},
    {"front_content": "A 1,000-gallon tank at 50 GPM. Time to empty?", "back_content": "20 minutes\n\n**Logic:** 1,000 ÷ 50 = 20", "hint": "Divide capacity by flow rate"},
    {"front_content": "Nozzle flows 150 GPM. Gallons used in 8 minutes?", "back_content": "1,200 gallons\n\n**Logic:** 150 × 8 = 1,200", "hint": "Rate × Time = Total"},
    {"front_content": "4 minutes per hose section. How many in 1 hour?", "back_content": "15 sections\n\n**Logic:** 60 ÷ 4 = 15", "hint": "60 min ÷ time per unit"},
    {"front_content": "150ft ladder at 75° angle. Approximate height reached?", "back_content": "≈145ft\n\n**Logic:** At steep angles, height ≈ ladder length. cos(15°)≈0.97", "hint": "Steep angle = nearly full length"},
    {"front_content": "Hose is 200ft. Each section is 50ft. How many sections?", "back_content": "4 sections\n\n**Logic:** 200 ÷ 50 = 4", "hint": "Total ÷ Section length"},
    {"front_content": "Pre-connect is 200ft. Need 150ft. What % unused?", "back_content": "25%\n\n**Logic:** 50ft unused. 50/200 = 1/4 = 25%", "hint": "Unused ÷ Total"},
    {"front_content": "If water weighs 8.34 lbs/gallon, weight of 100 gallons?", "back_content": "834 lbs\n\n**Logic:** 8.34 × 100 = 834", "hint": "Water ≈ 8.3 lbs/gal"},
    {"front_content": "1 cubic foot = 7.48 gallons. Gallons in 10 cu ft?", "back_content": "74.8 gallons\n\n**Logic:** 7.48 × 10 = 74.8", "hint": "1 cu ft ≈ 7.5 gal"},
    {"front_content": "3% foam mix. How much concentrate for 200 gallons?", "back_content": "6 gallons\n\n**Logic:** 200 × 0.03 = 6", "hint": "3% = 0.03"},
    {"front_content": "1% foam ratio. Concentrate for 500 gallons?", "back_content": "5 gallons\n\n**Logic:** 500 × 0.01 = 5", "hint": "1% = ÷100"},
    {"front_content": "Head pressure: 1 PSI per 2.31 ft. PSI at 46ft elevation?", "back_content": "≈20 PSI\n\n**Logic:** 46 ÷ 2.31 ≈ 20", "hint": "Height ÷ 2.31 = PSI"},
    {"front_content": "Elevation 100ft. Pressure loss due to height?", "back_content": "≈43 PSI\n\n**Logic:** 100 ÷ 2.31 ≈ 43.3 PSI", "hint": "0.434 PSI per foot"},
    {"front_content": "Add: $1.25 + $0.75 + $3.50", "back_content": "$5.50\n\n**Logic:** $1.25 + $0.75 = $2.00. $2.00 + $3.50 = $5.50", "hint": "Make round numbers first"},
    {"front_content": "Engine costs $3.45/hr to run. Cost for 8 hours?", "back_content": "$27.60\n\n**Logic:** $3.45 × 8 = $27.60. Or: $3.50×8=$28, minus $0.40", "hint": "Round, then adjust"},
    {"front_content": "Room is 12ft × 15ft. Square footage?", "back_content": "180 sq ft\n\n**Logic:** 12 × 15 = 180", "hint": "Length × Width = Area"},
    {"front_content": "Rectangular tank: 5ft × 4ft × 3ft. Volume in cubic feet?", "back_content": "60 cu ft\n\n**Logic:** 5 × 4 × 3 = 60", "hint": "L × W × H = Volume"},
    {"front_content": "Same tank (60 cu ft). Gallons it holds?", "back_content": "≈449 gallons\n\n**Logic:** 60 × 7.48 = 448.8 ≈ 449", "hint": "Cu ft × 7.48 = gallons"},
    
    # --- TIME/RATE & UNIT CONVERSION (15 cards) ---
    {"front_content": "45 minutes = what fraction of an hour?", "back_content": "3/4 hour (0.75 hr)\n\n**Logic:** 45/60 = 3/4", "hint": "Divide by 60"},
    {"front_content": "2.5 hours = how many minutes?", "back_content": "150 minutes\n\n**Logic:** 2.5 × 60 = 150", "hint": "Hours × 60 = minutes"},
    {"front_content": "90 seconds = how many minutes?", "back_content": "1.5 minutes\n\n**Logic:** 90 ÷ 60 = 1.5", "hint": "Seconds ÷ 60"},
    {"front_content": "If a task takes 20 min, how many in 3 hours?", "back_content": "9 tasks\n\n**Logic:** 180 min ÷ 20 min = 9", "hint": "Convert to same units"},
    {"front_content": "Convert 36 inches to feet.", "back_content": "3 feet\n\n**Logic:** 36 ÷ 12 = 3", "hint": "Inches ÷ 12 = feet"},
    {"front_content": "7 feet = how many inches?", "back_content": "84 inches\n\n**Logic:** 7 × 12 = 84", "hint": "Feet × 12 = inches"},
    {"front_content": "Convert 0.25 to a percentage.", "back_content": "25%\n\n**Logic:** 0.25 × 100 = 25%", "hint": "Decimal × 100"},
    {"front_content": "Convert 85% to a decimal.", "back_content": "0.85\n\n**Logic:** 85 ÷ 100 = 0.85", "hint": "Move decimal 2 left"},
    {"front_content": "1 mile = 5,280 ft. Half mile in feet?", "back_content": "2,640 feet\n\n**Logic:** 5,280 ÷ 2 = 2,640", "hint": "Memorize: 1 mile = 5,280 ft"},
    {"front_content": "3 firefighters take 2 hrs to complete task. 6 firefighters?", "back_content": "1 hour\n\n**Logic:** Double crew = half time (inverse proportion)", "hint": "More workers = less time"},
    {"front_content": "If 2 pumps take 4 hours, how long with 4 pumps?", "back_content": "2 hours\n\n**Logic:** Double pumps = half time", "hint": "Inverse relationship"},
    {"front_content": "Convert 72°F to Celsius (quick estimate).", "back_content": "≈22°C\n\n**Logic:** (72-32) × 5/9 = 40 × 5/9 ≈ 22", "hint": "Subtract 32, multiply by 5/9"},
    {"front_content": "1 gallon ≈ 3.78 liters. Liters in 10 gallons?", "back_content": "≈38 liters\n\n**Logic:** 10 × 3.78 = 37.8 ≈ 38", "hint": "×3.78 or ×4 for estimate"},
    {"front_content": "100 meters ≈ how many feet?", "back_content": "≈328 feet\n\n**Logic:** 1 meter ≈ 3.28 ft. 100 × 3.28 = 328", "hint": "Multiply meters by 3.3"},
    {"front_content": "A shift is 24 hours. What fraction is 6 hours?", "back_content": "1/4 or 25%\n\n**Logic:** 6/24 = 1/4", "hint": "6 is quarter of 24"},
]


if __name__ == "__main__":
    print("=" * 60)
    print("📇 IMPORTING PATTERN RECOGNITION FLASHCARDS")
    print("=" * 60)
    
    # Delete old math flashcards first
    print("\n🗑️ Removing old math flashcards...")
    with db.get_db() as conn:
        result = conn.execute("DELETE FROM flashcards WHERE subject = 'math'")
        print(f"   Deleted existing math flashcards")
    
    # Import new math cards
    print(f"\n📝 Importing {len(MATH_CARDS)} Math flashcards...")
    stats = import_flashcards(MATH_CARDS, "math")
    print(f"   ✅ Imported: {stats['imported']}")
    print(f"   ⚠️ Duplicates: {stats['duplicates']}")
    print(f"   ❌ Errors: {stats['errors']}")
    
    # Final count
    print(f"\n📊 Final Math count: {db.get_flashcard_count(subject='math')}")
    print("\n✅ Math import complete!")
    print("\nNote: Run import_mechanical_flashcards.py for mechanical aptitude cards.")

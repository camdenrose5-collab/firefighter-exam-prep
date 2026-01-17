#!/usr/bin/env python3
"""
Replace Math Skills and Mechanical Aptitude flashcards with pattern-recognition cards.

This script removes existing rote-memorization flashcards and replaces them with
cards designed for pattern recognition and logical thinking.

Usage:
    python replace_math_mechanical_flashcards.py --dry-run  # Preview only
    python replace_math_mechanical_flashcards.py             # Execute replacement
"""

import sys
import argparse
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend" / "app"))
import db

# New pattern-recognition flashcards
NEW_FLASHCARDS = [
    # ==========================================================================
    # MATH SKILLS - Pattern Recognition Cards
    # ==========================================================================
    {
        "subject": "math",
        "card_type": "pattern_recognition",
        "front_content": "A fire engine's tank is 1/4 full. If the total capacity is 600 gallons, how many gallons are currently in the tank?",
        "back_content": "150 gallons.\n\n**Logic:** Divide the total (600) by the denominator (4). 600 ÷ 4 = 150.",
        "hint": "For fractions, divide by the bottom number."
    },
    {
        "subject": "math",
        "card_type": "pattern_recognition",
        "front_content": "What is 15% of $80.00?",
        "back_content": "$12.00\n\n**Logic:** Find 10% (move decimal left = 8.0). Find 5% (half of 8.0 = 4.0). Add them together: 8 + 4 = 12.",
        "hint": "Break percentages into 10% and 5% chunks."
    },
    {
        "subject": "math",
        "card_type": "pattern_recognition",
        "front_content": "If you need 4 minutes to roll one length of hose, how many lengths can you roll in 1 hour?",
        "back_content": "15 lengths.\n\n**Logic:** 60 minutes ÷ 4 minutes per length = 15 lengths.",
        "hint": "Convert to same units, then divide total by rate."
    },
    {
        "subject": "math",
        "card_type": "pattern_recognition",
        "front_content": "Express 3/5 as a percentage.",
        "back_content": "60%\n\n**Logic:** Convert the fraction so the denominator is 100. 5 × 20 = 100. Multiply the top by 20 as well: 3 × 20 = 60.",
        "hint": "Make the bottom 100, then the top is your percent."
    },
    {
        "subject": "math",
        "card_type": "pattern_recognition",
        "front_content": "Estimate 792 divided by 19.",
        "back_content": "Approximately 40.\n\n**Logic:** Round to friendly numbers: 800 divided by 20. 80 ÷ 2 = 40.",
        "hint": "Round to easy numbers for quick estimation."
    },
    {
        "subject": "math",
        "card_type": "pattern_recognition",
        "front_content": "Subtract 25% from 200.",
        "back_content": "150\n\n**Logic:** 25% is one quarter. 1/4 of 200 is 50. 200 - 50 = 150.",
        "hint": "25% = 1/4, which is easier to calculate."
    },
    {
        "subject": "math",
        "card_type": "pattern_recognition",
        "front_content": "If a pump discharges 250 gallons per minute (GPM), how long will it take to empty a 2,500-gallon pool?",
        "back_content": "10 minutes.\n\n**Logic:** Total Volume ÷ Rate = Time. 2,500 ÷ 250 = 10.",
        "hint": "Use the formula: Time = Volume ÷ Rate."
    },
    {
        "subject": "math",
        "card_type": "pattern_recognition",
        "front_content": "Solve: 1.25 + 0.75 + 3.50",
        "back_content": "5.50\n\n**Logic:** Think of it as money. $1.25 + $0.75 = $2.00. $2.00 + $3.50 = $5.50.",
        "hint": "Treat decimals like dollars and cents."
    },
    {
        "subject": "math",
        "card_type": "pattern_recognition",
        "front_content": "What is the product of 12 and 12?",
        "back_content": "144\n\n**Logic:** This is a fundamental multiplication fact often used in area and pressure calculations.",
        "hint": "12² is a common 'power fact' to memorize."
    },
    {
        "subject": "math",
        "card_type": "pattern_recognition",
        "front_content": "Convert 0.8 to a fraction in simplest form.",
        "back_content": "4/5\n\n**Logic:** 0.8 is 8/10. Divide both by 2 to simplify = 4/5.",
        "hint": "Decimals over 10 or 100, then simplify."
    },
    {
        "subject": "math",
        "card_type": "pattern_recognition",
        "front_content": "How do you find 15% of any number quickly?",
        "back_content": "Find 10% (move decimal), then add half of that (5%).\n\n**Example:** 10% of 80 is 8. Half is 4. 8 + 4 = 12.",
        "hint": "Decomposition: 15% = 10% + 5%"
    },
    {
        "subject": "math",
        "card_type": "pattern_recognition",
        "front_content": "Estimate 498 ÷ 12.",
        "back_content": "Think 500 ÷ 10 ≈ 50. (Actual: 41.5)\n\n**Logic:** Close enough for multiple choice! Rounding makes mental math faster.",
        "hint": "Round to nearest 'friendly' numbers."
    },
    {
        "subject": "math",
        "card_type": "pattern_recognition",
        "front_content": "If 144/12=X, then 12×X=?",
        "back_content": "144\n\n**Logic:** Use multiplication facts to verify division. Thinking backwards catches errors.",
        "hint": "Division and multiplication are inverse operations."
    },
    {
        "subject": "math",
        "card_type": "pattern_recognition",
        "front_content": "What is the decimal equivalent of 3/8?",
        "back_content": "0.375\n\n**Logic:** Think 1/8 is 0.125. 0.125 × 3 = 0.375.",
        "hint": "Know the eighths: 1/8=0.125, 2/8=0.25, 3/8=0.375..."
    },
    {
        "subject": "math",
        "card_type": "pattern_recognition",
        "front_content": "A 150ft hose is cut by 20%. How long is it now?",
        "back_content": "120ft.\n\n**Logic:** 10% = 15. 20% = 30. 150 - 30 = 120.",
        "hint": "Find 10%, double it for 20%, then subtract."
    },

    # ==========================================================================
    # MECHANICAL APTITUDE - Pattern Recognition Cards
    # ==========================================================================
    {
        "subject": "mechanical-aptitude",
        "card_type": "pattern_recognition",
        "front_content": "In a 3:1 mechanical advantage system, if you want to lift a 300lb load, how much force is needed at the pull end?",
        "back_content": "100 lbs (plus friction).\n\n**Logic:** Divide the Load by the Advantage: 300 ÷ 3 = 100.",
        "hint": "MA formula: Force = Load ÷ Mechanical Advantage"
    },
    {
        "subject": "mechanical-aptitude",
        "card_type": "pattern_recognition",
        "front_content": "Which lever class has the fulcrum in the middle?",
        "back_content": "Class 1\n\n**Mnemonic 'FRE 1-2-3':** F (Fulcrum) is in the middle for Class 1.\n\n**Examples:** A see-saw, pliers, crowbar.",
        "hint": "FRE = Fulcrum-Resistance-Effort for classes 1-2-3"
    },
    {
        "subject": "mechanical-aptitude",
        "card_type": "pattern_recognition",
        "front_content": "A wheelbarrow is an example of which class of lever?",
        "back_content": "Class 2\n\n**Logic:** The Load (Resistance) is in the middle between the handles (Effort) and the wheel (Fulcrum).",
        "hint": "Class 2: R (Resistance/Load) in middle. Think wheelbarrow, nutcracker."
    },
    {
        "subject": "mechanical-aptitude",
        "card_type": "pattern_recognition",
        "front_content": "Using a 2:1 pulley system, how much rope must you pull to lift a load 5 feet?",
        "back_content": "10 feet.\n\n**Logic:** You trade distance for ease. Mechanical Advantage × Distance = Pull Length. 2 × 5 = 10.",
        "hint": "The trade-off rule: more MA = more rope to pull."
    },
    {
        "subject": "mechanical-aptitude",
        "card_type": "pattern_recognition",
        "front_content": "If a small gear with 10 teeth drives a larger gear with 30 teeth, how many times must the small gear turn to rotate the large gear once?",
        "back_content": "3 times.\n\n**Logic:** Ratio is 30:10, which simplifies to 3:1.",
        "hint": "Count teeth. Large teeth ÷ Small teeth = turns needed."
    },
    {
        "subject": "mechanical-aptitude",
        "card_type": "pattern_recognition",
        "front_content": "Does a longer wrench handle increase or decrease the torque applied to a bolt?",
        "back_content": "Increases torque.\n\n**Logic:** Torque = Force × Distance. Increasing the distance (handle length) increases the rotational force.",
        "hint": "Longer lever arm = more torque with same effort."
    },
    {
        "subject": "mechanical-aptitude",
        "card_type": "pattern_recognition",
        "front_content": "Which requires more effort: rolling a barrel up a short, steep ramp or a long, shallow ramp?",
        "back_content": "Short, steep ramp.\n\n**Logic:** A longer ramp (inclined plane) spreads the work over a greater distance, requiring less force at any one time.",
        "hint": "Longer ramp = easier push but more distance."
    },
    {
        "subject": "mechanical-aptitude",
        "card_type": "pattern_recognition",
        "front_content": "In a series of three gears, if the first gear turns clockwise, which way does the third gear turn?",
        "back_content": "Clockwise.\n\n**Logic:** Gear 1 (CW) → Gear 2 (CCW) → Gear 3 (CW). Odd-numbered gears in a line turn the same direction.",
        "hint": "Gears alternate direction. Odd gears match, even gears opposite."
    },
    {
        "subject": "mechanical-aptitude",
        "card_type": "pattern_recognition",
        "front_content": "True or False: A Class 3 lever always requires more effort than the weight of the load being moved.",
        "back_content": "True.\n\n**Logic:** Class 3 levers (like a shovel or your arm) sacrifice force for speed and range of motion.",
        "hint": "Class 3 = Effort in middle. Good for speed, not force."
    },
    {
        "subject": "mechanical-aptitude",
        "card_type": "pattern_recognition",
        "front_content": "What is the purpose of a fixed pulley that does not provide mechanical advantage (1:1)?",
        "back_content": "To change the direction of the force.\n\n**Logic:** It allows you to pull down (using your body weight) to lift an object up.",
        "hint": "Fixed pulley = direction change only, no MA."
    },
    {
        "subject": "mechanical-aptitude",
        "card_type": "pattern_recognition",
        "front_content": "In a 2:1 pulley system, what is the relationship between Force and Distance?",
        "back_content": "You pull 2× the rope, but only use 1/2 the effort.\n\n**Logic:** Trade-off Rule: To move a load 10ft, you pull 20ft of rope.",
        "hint": "MA doubles = Effort halves, Distance doubles."
    },
    {
        "subject": "mechanical-aptitude",
        "card_type": "pattern_recognition",
        "front_content": "Load: 100 lbs. System: 2:1. Force required at the tip?",
        "back_content": "50 lbs.\n\n**Logic:** 100 ÷ 2 = 50 lbs.\n\n**Note:** Does not account for friction.",
        "hint": "Force = Load ÷ MA"
    },
    {
        "subject": "mechanical-aptitude",
        "card_type": "pattern_recognition",
        "front_content": "If a gear with 10 teeth drives a gear with 40 teeth, what is the gear ratio?",
        "back_content": "4:1\n\n**Logic:** The smaller gear must turn 4 times to turn the large gear once. (40 ÷ 10 = 4)",
        "hint": "Ratio = Driven teeth ÷ Driver teeth"
    },
    {
        "subject": "mechanical-aptitude",
        "card_type": "pattern_recognition",
        "front_content": "Which lever class is a pair of pliers?",
        "back_content": "Class 1\n\n**Logic:** The pivot point (fulcrum) is between the handles and the jaws.",
        "hint": "Class 1 = Fulcrum in middle (F-R-E)"
    },
    {
        "subject": "mechanical-aptitude",
        "card_type": "pattern_recognition",
        "front_content": "What are the three classes of levers and what's in the middle for each?",
        "back_content": "**FRE Mnemonic (1-2-3):**\n\n• Class 1: **F**ulcrum in middle (see-saw, crowbar)\n• Class 2: **R**esistance (Load) in middle (wheelbarrow, nutcracker)\n• Class 3: **E**ffort in middle (tweezers, shovel, your arm)",
        "hint": "Remember: F-R-E for 1-2-3"
    },
]


def replace_flashcards(dry_run: bool = False):
    """Delete old math/mechanical flashcards and insert new pattern-recognition ones."""
    
    # Count existing
    math_count = db.get_flashcard_count(subject="math")
    mech_count = db.get_flashcard_count(subject="mechanical-aptitude")
    
    print(f"📊 Current counts:")
    print(f"   - math: {math_count}")
    print(f"   - mechanical-aptitude: {mech_count}")
    print()
    
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made\n")
    
    # Delete existing
    if not dry_run:
        with db.get_db() as conn:
            conn.execute("DELETE FROM flashcards WHERE subject IN ('math', 'mechanical-aptitude')")
        print(f"🗑️  Deleted {math_count + mech_count} old flashcards")
    else:
        print(f"🗑️  Would delete {math_count + mech_count} old flashcards")
    
    # Count new cards by subject
    new_math = [c for c in NEW_FLASHCARDS if c["subject"] == "math"]
    new_mech = [c for c in NEW_FLASHCARDS if c["subject"] == "mechanical-aptitude"]
    
    print(f"\n📝 New cards to insert:")
    print(f"   - math: {len(new_math)} pattern-recognition cards")
    print(f"   - mechanical-aptitude: {len(new_mech)} pattern-recognition cards")
    print()
    
    # Insert new cards
    if not dry_run:
        for card in NEW_FLASHCARDS:
            db.add_flashcard(
                subject=card["subject"],
                card_type=card["card_type"],
                front_content=card["front_content"],
                back_content=card["back_content"],
                hint=card.get("hint"),
                source="pattern_recognition_revamp",
                is_approved=True
            )
        print(f"✅ Inserted {len(NEW_FLASHCARDS)} new pattern-recognition flashcards")
    else:
        print(f"✅ Would insert {len(NEW_FLASHCARDS)} new pattern-recognition flashcards")
        print("\n--- Sample cards preview ---\n")
        for card in NEW_FLASHCARDS[:3]:
            print(f"📋 {card['subject'].upper()}")
            print(f"   Front: {card['front_content'][:80]}...")
            print(f"   Back: {card['back_content'][:80]}...")
            print()
    
    # Final counts
    if not dry_run:
        final_math = db.get_flashcard_count(subject="math")
        final_mech = db.get_flashcard_count(subject="mechanical-aptitude")
        print(f"\n📊 Final counts:")
        print(f"   - math: {final_math}")
        print(f"   - mechanical-aptitude: {final_mech}")
    
    return {
        "deleted": math_count + mech_count,
        "inserted": len(NEW_FLASHCARDS),
        "new_math": len(new_math),
        "new_mech": len(new_mech)
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replace Math and Mechanical flashcards with pattern-recognition cards")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔄 FLASHCARD REPLACEMENT: Rote → Pattern Recognition")
    print("=" * 60)
    print()
    
    stats = replace_flashcards(dry_run=args.dry_run)
    
    print()
    print("=" * 60)
    print("Done!")

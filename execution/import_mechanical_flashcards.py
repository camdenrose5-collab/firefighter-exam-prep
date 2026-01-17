#!/usr/bin/env python3
"""
Import Mechanical Aptitude pattern-recognition flashcards.
"""

import sys
from pathlib import Path
from difflib import SequenceMatcher

backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))
from app import db


def check_duplicate(new_front: str, existing_fronts: set, threshold: float = 0.92) -> tuple[bool, str]:
    new_text = new_front.lower().strip()
    for ex in existing_fronts:
        ratio = SequenceMatcher(None, new_text, ex.lower().strip()).ratio()
        if ratio > threshold:
            return True, ex
    return False, ""


def import_flashcards(cards: list, subject: str) -> dict:
    existing = db.get_random_flashcards([subject], 1000, approved_only=False)
    existing_fronts = {c["front_content"] for c in existing}
    stats = {"imported": 0, "duplicates": 0, "errors": 0}
    
    for card in cards:
        is_dup, match = check_duplicate(card["front_content"], existing_fronts)
        if is_dup:
            print(f"  ⚠️ Duplicate: '{card['front_content'][:40]}...'")
            stats["duplicates"] += 1
            continue
        try:
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


MECHANICAL_CARDS = [
    # --- LEVERS (30 cards) ---
    {"front_content": "Which lever class has the FULCRUM in the middle?", "back_content": "Class 1\n\n**Logic:** Remember FRE 1-2-3: Class 1 = Fulcrum in middle.\nExamples: see-saw, crowbar, pliers", "hint": "FRE: Fulcrum-Resistance-Effort for classes 1-2-3"},
    {"front_content": "Which lever class has the RESISTANCE (load) in the middle?", "back_content": "Class 2\n\n**Logic:** FRE 1-2-3: Class 2 = Resistance in middle.\nExamples: wheelbarrow, nutcracker, bottle opener", "hint": "Class 2 = R in middle"},
    {"front_content": "Which lever class has the EFFORT in the middle?", "back_content": "Class 3\n\n**Logic:** FRE 1-2-3: Class 3 = Effort in middle.\nExamples: tweezers, tongs, fishing rod, your forearm", "hint": "Class 3 = E in middle"},
    {"front_content": "A see-saw is which class of lever?", "back_content": "Class 1\n\n**Logic:** The pivot (fulcrum) is in the middle between people (effort and resistance)", "hint": "Fulcrum in middle = Class 1"},
    {"front_content": "A wheelbarrow is which class of lever?", "back_content": "Class 2\n\n**Logic:** Load in the middle, wheel (fulcrum) at one end, handles (effort) at other end", "hint": "Load in middle = Class 2"},
    {"front_content": "Tweezers are which class of lever?", "back_content": "Class 3\n\n**Logic:** You squeeze in the middle (effort), pivot at one end, tips grip object", "hint": "Effort in middle = Class 3"},
    {"front_content": "A Halligan bar prying open a door is which lever class?", "back_content": "Class 1\n\n**Logic:** The fulcrum (door frame) is between your push (effort) and the door (resistance)", "hint": "Fulcrum between effort and load = Class 1"},
    {"front_content": "Pliers are which class of lever?", "back_content": "Class 1\n\n**Logic:** The pivot point (fulcrum) is between the handles (effort) and the jaws (resistance)", "hint": "Pivot in middle = Class 1"},
    {"front_content": "A nutcracker is which class of lever?", "back_content": "Class 2\n\n**Logic:** The nut (resistance) is between the hinge (fulcrum) and handles (effort)", "hint": "Nut in middle = Class 2"},
    {"front_content": "Your forearm lifting a weight is which lever class?", "back_content": "Class 3\n\n**Logic:** Bicep (effort) attaches in middle, elbow (fulcrum) at one end, hand holds load", "hint": "Muscle in middle = Class 3"},
    {"front_content": "A crowbar lifting a boulder is which lever class?", "back_content": "Class 1\n\n**Logic:** Fulcrum (rock under bar) is between your push and the boulder", "hint": "Fulcrum between ends = Class 1"},
    {"front_content": "A bottle opener is which lever class?", "back_content": "Class 2\n\n**Logic:** Cap (load) is between the pivot point and your hand", "hint": "Load in middle = Class 2"},
    {"front_content": "A fishing rod casting is which lever class?", "back_content": "Class 3\n\n**Logic:** Your hand (effort) is in the middle, butt of rod pivots, tip casts bait", "hint": "Hand in middle = Class 3"},
    {"front_content": "A shovel digging is which lever class?", "back_content": "Class 3\n\n**Logic:** Lower hand (effort) is between upper hand (fulcrum) and dirt (load)", "hint": "Effort hand in middle = Class 3"},
    {"front_content": "A stapler is which lever class?", "back_content": "Class 2\n\n**Logic:** Staple (resistance) is between hinge and where you press", "hint": "Resistance in middle = Class 2"},
    {"front_content": "True or False: Class 3 levers multiply force.", "back_content": "False\n\n**Logic:** Class 3 sacrifices force for speed/range. You apply MORE effort than the load weighs", "hint": "Class 3 = speed over power"},
    {"front_content": "Which lever class provides mechanical advantage greater than 1?", "back_content": "Classes 1 and 2\n\n**Logic:** When effort arm is longer than load arm, MA > 1. Class 3 always has MA < 1", "hint": "Long effort arm = force multiplier"},
    {"front_content": "In a lever, what happens if you move the fulcrum closer to the load?", "back_content": "Mechanical advantage increases\n\n**Logic:** Load arm shortens, effort arm lengthens → less effort needed", "hint": "Shorter load arm = easier lift"},
    {"front_content": "A teeter-totter balances when heavier person sits closer to...?", "back_content": "The fulcrum (center)\n\n**Logic:** Moment = Force × Distance. Shorter distance compensates for greater weight", "hint": "Balance: Heavy × Short = Light × Long"},
    {"front_content": "Pike pole pulling ceiling is which lever class?", "back_content": "Class 1\n\n**Logic:** Fulcrum is where pole contacts ceiling between hands and hook", "hint": "Pivot in middle = Class 1"},
    
    # --- PULLEYS (25 cards) ---
    {"front_content": "What does a single FIXED pulley do?", "back_content": "Changes direction of force only\n\n**Logic:** MA = 1:1. No force multiplication. Lets you pull DOWN to lift UP", "hint": "Fixed = direction change only"},
    {"front_content": "What does a single MOVABLE pulley provide?", "back_content": "2:1 mechanical advantage\n\n**Logic:** Load is supported by 2 rope segments. Effort = Load ÷ 2", "hint": "Movable = 2:1 MA"},
    {"front_content": "In a 2:1 pulley system, how much force to lift 100 lbs?", "back_content": "50 lbs\n\n**Logic:** Force = Load ÷ MA = 100 ÷ 2 = 50 lbs", "hint": "Divide load by MA"},
    {"front_content": "In a 3:1 pulley, force needed to lift 300 lbs?", "back_content": "100 lbs\n\n**Logic:** 300 ÷ 3 = 100 lbs (plus friction)", "hint": "Force = Load ÷ MA"},
    {"front_content": "In a 4:1 pulley, force to lift 200 lbs?", "back_content": "50 lbs\n\n**Logic:** 200 ÷ 4 = 50 lbs", "hint": "Higher MA = less force"},
    {"front_content": "2:1 pulley: To lift load 5 feet, how much rope to pull?", "back_content": "10 feet\n\n**Logic:** Trade-off: 2× MA means 2× rope pull. 5 × 2 = 10 ft", "hint": "Rope = Distance × MA"},
    {"front_content": "3:1 pulley: To lift 4 feet, rope pulled?", "back_content": "12 feet\n\n**Logic:** 4 × 3 = 12 feet of rope", "hint": "More MA = more rope to pull"},
    {"front_content": "In pulleys, what's the trade-off for mechanical advantage?", "back_content": "Distance (rope length)\n\n**Logic:** Less force but more rope distance. Work stays constant", "hint": "Force × Distance = constant"},
    {"front_content": "How do you count MA in a pulley system?", "back_content": "Count ropes supporting the load\n\n**Logic:** Each rope segment shares the load equally", "hint": "Ropes touching load block = MA"},
    {"front_content": "Block and tackle with 4 ropes on load block. MA?", "back_content": "4:1\n\n**Logic:** 4 ropes share the load → Force = Load ÷ 4", "hint": "Count supporting ropes"},
    {"front_content": "Fixed pulley at top, movable at bottom. Total MA?", "back_content": "2:1\n\n**Logic:** Fixed adds 0, movable adds 2:1. The fixed just changes direction", "hint": "Only movable pulleys add MA"},
    {"front_content": "Why use a fixed pulley if it has no MA?", "back_content": "To change force direction\n\n**Logic:** Pull DOWN using body weight instead of lifting UP", "hint": "Direction change = easier pull"},
    {"front_content": "2:1 system, load: 80 lbs. Effort force?", "back_content": "40 lbs\n\n**Logic:** 80 ÷ 2 = 40", "hint": "Halved with 2:1"},
    {"front_content": "Lift 6 feet with 4:1 system. Rope pulled?", "back_content": "24 feet\n\n**Logic:** 6 × 4 = 24 ft", "hint": "Height × MA = rope"},
    {"front_content": "5:1 pulley, 250 lb load. Effort needed?", "back_content": "50 lbs\n\n**Logic:** 250 ÷ 5 = 50", "hint": "Load ÷ MA"},
    
    # --- GEARS (25 cards) ---
    {"front_content": "If driver gear has 10 teeth and driven has 30 teeth, gear ratio?", "back_content": "3:1\n\n**Logic:** 30 ÷ 10 = 3. Driver turns 3 times for driven to turn once", "hint": "Driven teeth ÷ Driver teeth"},
    {"front_content": "Small gear (10 teeth) drives large (40 teeth). Ratio?", "back_content": "4:1\n\n**Logic:** 40 ÷ 10 = 4", "hint": "Large ÷ Small = ratio"},
    {"front_content": "Driver: 20 teeth. Driven: 20 teeth. Ratio?", "back_content": "1:1\n\n**Logic:** Same size = same speed, no advantage", "hint": "Equal teeth = 1:1"},
    {"front_content": "Driver: 15 teeth. Driven: 45 teeth. How many driver rotations per 1 driven rotation?", "back_content": "3 rotations\n\n**Logic:** 45 ÷ 15 = 3", "hint": "Driven ÷ Driver = rotations"},
    {"front_content": "Gear A (clockwise) meshes with Gear B. Which way does B turn?", "back_content": "Counter-clockwise\n\n**Logic:** Adjacent meshing gears always turn opposite directions", "hint": "Adjacent = opposite"},
    {"front_content": "3 gears in a row. Gear 1 turns clockwise. Gear 3 turns?", "back_content": "Clockwise\n\n**Logic:** 1→CW, 2→CCW, 3→CW. Odd numbered match direction", "hint": "Odd gears = same direction as first"},
    {"front_content": "4 gears in a row. Gear 1 turns CCW. Gear 4 turns?", "back_content": "Counter-clockwise\n\n**Logic:** Even number of gears = last turns same as first", "hint": "Even count = same direction"},
    {"front_content": "Small gear drives large gear. Which spins faster?", "back_content": "Small gear\n\n**Logic:** Small gear must turn multiple times for large to turn once", "hint": "Small = fast, Large = slow"},
    {"front_content": "Large gear drives small gear. Which has more torque?", "back_content": "Large gear\n\n**Logic:** Large gear is slower but stronger. Small is faster but weaker", "hint": "Large = torque, Small = speed"},
    {"front_content": "Driver: 8 teeth, 100 RPM. Driven: 24 teeth. Driven RPM?", "back_content": "33.3 RPM\n\n**Logic:** Ratio 24÷8=3. Speed = 100 ÷ 3 ≈ 33", "hint": "Speed decreases by ratio"},
    {"front_content": "What is an idler gear?", "back_content": "A gear placed between driver and driven to change direction only\n\n**Logic:** Doesn't change speed or torque, only reverses rotation", "hint": "Idler = direction changer"},
    {"front_content": "In gears, speed and torque have what relationship?", "back_content": "Inverse (trade-off)\n\n**Logic:** High speed = low torque. High torque = low speed", "hint": "Can't have both"},
    {"front_content": "Bicycle: large front gear, small rear. What happens?", "back_content": "High speed, more pedaling effort\n\n**Logic:** Rear spins faster than pedals, but harder to push", "hint": "High gear = speed but harder"},
    {"front_content": "Bicycle: small front gear, large rear. What happens?", "back_content": "Low speed, easier pedaling\n\n**Logic:** Good for hills. More torque, less speed", "hint": "Low gear = easy but slow"},
    {"front_content": "2 gears mesh. Can they turn the same direction?", "back_content": "No\n\n**Logic:** Teeth interlock and push opposite ways. Use belt/chain for same direction", "hint": "Meshed gears = opposite"},
    
    # --- TORQUE & FORCE (10 cards) ---
    {"front_content": "Longer wrench handle increases or decreases torque?", "back_content": "Increases\n\n**Logic:** Torque = Force × Distance. More distance = more rotational force", "hint": "Longer arm = more torque"},
    {"front_content": "Torque = Force × ___", "back_content": "Distance (lever arm length)\n\n**Logic:** Also called moment arm. Further from pivot = more turning power", "hint": "T = F × D"},
    {"front_content": "Same force applied. Which breaks bolt: 6\" wrench or 12\" wrench?", "back_content": "12\" wrench\n\n**Logic:** Double length = double torque with same effort", "hint": "Longer = stronger turn"},
    {"front_content": "Why add a pipe to a wrench handle?", "back_content": "To extend lever arm and increase torque\n\n**Logic:** Called a 'cheater bar'. More leverage", "hint": "Extension = more torque"},
    {"front_content": "Door hinges are at edge. Why push far from hinges?", "back_content": "Maximum torque with minimum effort\n\n**Logic:** Further from pivot = easier to open", "hint": "Push at handle, not hinges"},
    
    # --- INCLINED PLANES (10 cards) ---
    {"front_content": "Rolling barrel up: short steep ramp vs long shallow ramp. Which needs less force?", "back_content": "Long shallow ramp\n\n**Logic:** Longer distance = less force needed. Work is same, force is spread out", "hint": "Long ramp = easy, short = hard"},
    {"front_content": "Inclined plane reduces effort but increases what?", "back_content": "Distance traveled\n\n**Logic:** Trade-off: push less hard but push farther", "hint": "Force × Distance stays same"},
    {"front_content": "A wedge is what type of simple machine?", "back_content": "Two inclined planes back-to-back\n\n**Logic:** Axe, knife, chisel all use wedge principle", "hint": "Wedge = double inclined plane"},
    {"front_content": "A screw is what type of simple machine?", "back_content": "Inclined plane wrapped around a cylinder\n\n**Logic:** Threads are a spiral ramp. Many turns = high MA", "hint": "Screw = wrapped ramp"},
    {"front_content": "Ramp is 10ft long, rises 2ft. MA?", "back_content": "5:1\n\n**Logic:** MA = Length ÷ Height = 10 ÷ 2 = 5", "hint": "Ramp length ÷ rise = MA"},
    {"front_content": "Stairs vs ladder to same height. Stairs have...?", "back_content": "Higher mechanical advantage (less effort)\n\n**Logic:** Stairs = longer path = gentler incline", "hint": "Stairs easier than ladder"},
    {"front_content": "Wheelchair ramp must be 12:1 ratio. For 3ft rise, ramp length?", "back_content": "36 feet\n\n**Logic:** 12 × 3 = 36 ft", "hint": "Ratio × Rise = Length"},
    {"front_content": "Loading dock 4ft high. 2:1 ramp MA wanted. Ramp length?", "back_content": "8 feet\n\n**Logic:** 2 × 4 = 8 ft", "hint": "MA × Height = Length"},
    {"front_content": "Knife cuts because wedge does what to force?", "back_content": "Redirects downward force into sideways force\n\n**Logic:** Transforms push into split. Thin wedge = higher MA", "hint": "Down force → Spread apart"},
    {"front_content": "Fine-thread screw vs coarse-thread. Which needs less turning force?", "back_content": "Fine-thread (more turns but easier each turn)\n\n**Logic:** Fine = higher MA, slower progress", "hint": "More threads = easier but slower"},
]


if __name__ == "__main__":
    print("=" * 60)
    print("📇 IMPORTING MECHANICAL APTITUDE FLASHCARDS")
    print("=" * 60)
    
    # Delete old mechanical flashcards
    print("\n🗑️ Removing old mechanical-aptitude flashcards...")
    with db.get_db() as conn:
        conn.execute("DELETE FROM flashcards WHERE subject = 'mechanical-aptitude'")
        print("   Deleted existing mechanical-aptitude flashcards")
    
    # Import new cards
    print(f"\n📝 Importing {len(MECHANICAL_CARDS)} Mechanical Aptitude flashcards...")
    stats = import_flashcards(MECHANICAL_CARDS, "mechanical-aptitude")
    print(f"   ✅ Imported: {stats['imported']}")
    print(f"   ⚠️ Duplicates: {stats['duplicates']}")
    print(f"   ❌ Errors: {stats['errors']}")
    
    print(f"\n📊 Final Mechanical count: {db.get_flashcard_count(subject='mechanical-aptitude')}")
    print("\n✅ Mechanical import complete!")

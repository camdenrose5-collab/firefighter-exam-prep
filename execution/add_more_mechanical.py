#!/usr/bin/env python3
"""Add 35 more mechanical aptitude flashcards."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from app import db

ADDITIONAL_MECHANICAL = [
    # More lever applications
    {"f": "A hammer removing a nail is which lever class?", "b": "Class 1\n\n**Logic:** Claw acts as fulcrum between handle (effort) and nail (load)", "h": "Fulcrum in middle = Class 1"},
    {"f": "Scissors are which lever class?", "b": "Class 1\n\n**Logic:** Pivot (fulcrum) between handles and blades", "h": "Pivot in middle = Class 1"},
    {"f": "A door handle/lever is which class?", "b": "Class 1\n\n**Logic:** Pivot point is between where you push and where latch moves", "h": "Fulcrum between force and load"},
    {"f": "Tongs picking up ice are which lever class?", "b": "Class 3\n\n**Logic:** Your squeeze (effort) is in the middle between pivot and tips", "h": "Effort in middle = Class 3"},
    {"f": "A baseball bat swinging is which lever class?", "b": "Class 3\n\n**Logic:** Hands (effort) in middle, pivot near body, bat end hits ball", "h": "Hands in middle = Class 3"},
    
    # More pulley calculations
    {"f": "6:1 pulley system, 300 lb load. Effort needed?", "b": "50 lbs\n\n**Logic:** 300 ÷ 6 = 50 lbs", "h": "Load ÷ MA = Effort"},
    {"f": "5:1 pulley: lift load 8 feet. Rope to pull?", "b": "40 feet\n\n**Logic:** 8 × 5 = 40 feet of rope", "h": "Distance × MA = Rope"},
    {"f": "Using 2:1 pulley, you pull 30 ft of rope. Load rises how far?", "b": "15 feet\n\n**Logic:** 30 ÷ 2 = 15 ft. Trade distance for ease", "h": "Rope ÷ MA = Rise"},
    {"f": "Combination of 1 fixed + 1 movable pulley. Total MA?", "b": "2:1\n\n**Logic:** Fixed = 0 MA (direction only), movable = 2:1", "h": "Only movable adds MA"},
    {"f": "How many movable pulleys for 4:1 MA?", "b": "2 movable pulleys\n\n**Logic:** Each movable pulley doubles MA. 2^2 = 4", "h": "2^(movable count) = MA"},
    
    # More gear problems
    {"f": "Driver: 25 teeth, Driven: 75 teeth. Gear ratio?", "b": "3:1\n\n**Logic:** 75 ÷ 25 = 3", "h": "Driven ÷ Driver = Ratio"},
    {"f": "Driver: 12 teeth at 60 RPM. Driven: 36 teeth. Driven RPM?", "b": "20 RPM\n\n**Logic:** Ratio 36÷12=3. Speed: 60 ÷ 3 = 20", "h": "Speed drops by gear ratio"},
    {"f": "Driver: 50 teeth. Driven: 10 teeth. Which has more torque?", "b": "Driver (50 teeth)\n\n**Logic:** Larger gear = more torque, less speed", "h": "Big gear = high torque"},
    {"f": "5 gears in a row. First turns CW. Last gear turns?", "b": "Clockwise\n\n**Logic:** Odd number of gears = same as first. 1→CW, 2→CCW, 3→CW, 4→CCW, 5→CW", "h": "Odd gears = same direction"},
    {"f": "Belt connects two pulleys. Both turn which direction?", "b": "Same direction\n\n**Logic:** Belt doesn't reverse like meshed gears", "h": "Belt = same direction"},
    
    # Hydraulics
    {"f": "Pascal's Law states that pressure in a fluid...?", "b": "Transmits equally in all directions\n\n**Logic:** Push here, pressure appears everywhere equally", "h": "Pressure spreads evenly"},
    {"f": "Hydraulic jack: small piston 1 sq in, large piston 10 sq in. 10 lb input force gives?", "b": "100 lbs output\n\n**Logic:** Force multiplied by area ratio: 10 × 10 = 100 lbs", "h": "Force × Area ratio = Output"},
    {"f": "In hydraulics, what's the trade-off for force multiplication?", "b": "Distance (small piston travels farther)\n\n**Logic:** Work in = Work out. More force but less movement", "h": "More force = less travel"},
    {"f": "Hydraulic spreader works by...?", "b": "Fluid pressure pushing pistons apart\n\n**Logic:** Pascal's law - pump creates pressure that separates arms", "h": "Fluid pressure = force"},
    {"f": "Why use hydraulic tools instead of manual?", "b": "Fluid multiplies force without losing strength\n\n**Logic:** Small pump effort = massive spreading/cutting force", "h": "Mechanical advantage via fluid"},
    
    # Force and work
    {"f": "Work = Force × ___", "b": "Distance\n\n**Logic:** W = F × D. Push harder OR push farther = more work", "h": "W = F × D"},
    {"f": "You push 50 lbs for 10 feet. Work done?", "b": "500 ft-lbs\n\n**Logic:** 50 × 10 = 500 foot-pounds", "h": "F × D = Work"},
    {"f": "Power = Work ÷ ___", "b": "Time\n\n**Logic:** Same work faster = more power", "h": "Power = Work/Time"},
    {"f": "Two ramps: same height, one is longer. Which requires more WORK?", "b": "Same work\n\n**Logic:** Work = Weight × Height. Distance changes force, not total work", "h": "Work stays constant"},
    {"f": "Pushing a box with 20 lbs of friction for 100 ft. Work against friction?", "b": "2,000 ft-lbs\n\n**Logic:** 20 × 100 = 2,000", "h": "Friction work = friction × distance"},
    
    # Applied mechanical concepts
    {"f": "Archimedes screw lifts water using what principle?", "b": "Inclined plane wrapped in helix\n\n**Logic:** Rotating spiral acts as continuous ramp for water", "h": "Screw = wrapped inclined plane"},
    {"f": "Why does a spiral staircase take more steps than straight stairs?", "b": "Longer path = gentler incline = less effort per step\n\n**Logic:** Trading distance for reduced effort", "h": "Longer path = easier climb"},
    {"f": "A corkscrew uses which simple machine?", "b": "Screw (and lever for handle)\n\n**Logic:** Threaded spiral converts rotation to linear pull", "h": "Rotation → Linear motion"},
    {"f": "Can opener combines which simple machines?", "b": "Lever (handles) + Wedge (cutting wheel) + Wheel/axle (rotator)\n\n**Logic:** Compound machine = multiple simple machines", "h": "Multiple machines combined"},
    {"f": "Bicycle uses which simple machines?", "b": "Wheel/axle, lever (pedals), gears, pulley (chain)\n\n**Logic:** Complex machine combining many simple machines", "h": "Many machines in one"},
    
    # Friction and efficiency
    {"f": "In a real pulley system, actual force needed is always...?", "b": "Higher than calculated (due to friction)\n\n**Logic:** Friction wastes energy. Real MA < Ideal MA", "h": "Friction = extra effort"},
    {"f": "Efficiency = (Output work ÷ Input work) × 100. If 80% efficient means?", "b": "20% lost to friction/heat\n\n**Logic:** Not all input becomes useful output", "h": "100% - efficiency = loss"},
    {"f": "Oil/grease on machines does what to efficiency?", "b": "Increases efficiency (reduces friction)\n\n**Logic:** Less friction = less energy wasted = more output", "h": "Lubrication = less waste"},
    {"f": "Rubber tires on wet road have _____ friction than dry road.", "b": "Less friction\n\n**Logic:** Water reduces grip/traction", "h": "Wet = slippery"},
    {"f": "Which has more friction: rough surface or smooth surface?", "b": "Rough surface\n\n**Logic:** More contact points = more resistance to sliding", "h": "Rougher = more friction"},
]

print("📇 Adding 35 more mechanical flashcards...")
imported = 0
for c in ADDITIONAL_MECHANICAL:
    try:
        db.add_flashcard(
            "mechanical-aptitude", "pattern_recognition",
            c["f"], c["b"], c.get("h"), "manual", True
        )
        imported += 1
    except Exception as e:
        print(f"  ❌ Error: {e}")

print(f"✅ Imported: {imported}")
print(f"📊 Total Mechanical: {db.get_flashcard_count(subject='mechanical-aptitude')}")

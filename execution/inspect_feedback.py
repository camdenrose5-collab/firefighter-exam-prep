"""
Feedback Inspector Tool

Allows manual inspection of user feedback/ideas.
Usage: python execution/inspect_feedback.py
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app import db


def inspect_feedback():
    """Interactive feedback inspection."""
    try:
        feedback_list = db.get_pending_feedback()
        
        print("\n" + "=" * 80)
        print(f"║ 💡 FEEDBACK INSPECTOR - {len(feedback_list)} PENDING ENTRIES{' '*38}║")
        print("=" * 80)
        
        if not feedback_list:
            print("\n✅ No pending feedback! All caught up.")
            print("\nNew feedback from users will appear here.")
            return
        
        print("\nPENDING FEEDBACK:")
        for i, f in enumerate(feedback_list, 1):
            mode_emoji = {"quiz": "📝", "flashcards": "📇", "explain": "💬"}.get(f["study_mode"], "💡")
            print(f"  [{i}] {mode_emoji} {f['study_mode'].upper()} | {f['created_at'][:16]}")
            print(f"      → {f['message'][:60]}{'...' if len(f['message']) > 60 else ''}")
        
        print("\n" + "-" * 40)
        print(" [N] View Feedback #N (e.g., '1')")
        print(" [A] View all feedback")
        print(" [Q] Quit")
        
        choice = input("\nChoice: ").strip().upper()
        
        if choice == "Q":
            return
        elif choice == "A":
            view_all_feedback()
        elif choice.isdigit() and 1 <= int(choice) <= len(feedback_list):
            view_feedback_detail(feedback_list[int(choice) - 1])
            
    except Exception as e:
        print(f"Error: {e}")


def view_feedback_detail(feedback):
    """View detailed feedback entry."""
    try:
        mode_emoji = {"quiz": "📝", "flashcards": "📇", "explain": "💬"}.get(feedback["study_mode"], "💡")
        
        print("\n" + "=" * 80)
        print(f"║ FEEDBACK DETAILS{' '*61}║")
        print("=" * 80)
        
        print(f"\n📅 Submitted: {feedback['created_at']}")
        print(f"{mode_emoji} Study Mode: {feedback['study_mode'].upper()}")
        print(f"\n💬 MESSAGE:")
        print("-" * 40)
        print(feedback["message"])
        print("-" * 40)
        
        action = input("\n[M] Mark as Reviewed | [B] Back: ").strip().upper()
        if action == "M":
            db.mark_feedback_reviewed(feedback["id"])
            print("✅ Marked as reviewed!")
            
    except Exception as e:
        print(f"Error: {e}")


def view_all_feedback():
    """Display all feedback in table format."""
    all_feedback = db.get_all_feedback()
    
    print("\n" + "=" * 100)
    print("ALL FEEDBACK ENTRIES")
    print("=" * 100)
    print(f"{'#':<4} {'Mode':<12} {'Date':<18} {'Status':<10} {'Message'}")
    print("-" * 100)
    
    for i, f in enumerate(all_feedback, 1):
        status = "✅ Done" if f["reviewed"] else "🔴 New"
        msg_preview = f["message"][:50] + "..." if len(f["message"]) > 50 else f["message"]
        print(f"{i:<4} {f['study_mode']:<12} {f['created_at'][:16]:<18} {status:<10} {msg_preview}")
    
    print("-" * 100)
    print(f"Total: {len(all_feedback)} entries")
    input("\nPress Enter to continue...")


if __name__ == "__main__":
    inspect_feedback()

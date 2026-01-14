#!/usr/bin/env python3
"""
Report Inspector Tool

Allows manual inspection of reported questions.
Usage: python execution/inspect_reports.py
"""

import sys
import json
import textwrap
from pathlib import Path

# Add backend to path to import db
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from app import db

def clear_screen():
    print("\033[H\033[J", end="")

def inspect_reports():
    while True:
        reports = db.get_pending_reports()
        
        clear_screen()
        print(f"╔{'═'*78}╗")
        print(f"║ 🚩 REPORT INSPECTOR - {len(reports)} PENDING REPORTS{' '*40}║")
        print(f"╠{'═'*78}╝")
        
        if not reports:
            print("\n✅ No pending reports! Good job.")
            print("\nOnly newly reported questions will appear here.")
            input("\nPress Enter to exit...")
            break
            
        print("\nPENDING REPORTS:")
        for i, r in enumerate(reports, 1):
            reason_trunc = (r['reason'][:50] + '...') if r['reason'] and len(r['reason']) > 50 else (r['reason'] or "No reason provided")
            print(f" {i}. [{r['subject']}] {reason_trunc}")
            
        print(f"\n{'-'*80}")
        print("COMMANDS:")
        print(" [N] View Report #N (e.g., '1')")
        print(" [Q] Quit")
        
        choice = input("\nSelect > ").strip().lower()
        
        if choice == 'q':
            break
            
        if choice.isdigit() and 1 <= int(choice) <= len(reports):
            view_report(reports[int(choice)-1])
        else:
            input("❌ Invalid selection. Press Enter...")

def view_report(report):
    while True:
        clear_screen()
        print(f"╔{'═'*78}╗")
        print(f"║ REPORT DETAILS{' '*63}║")
        print(f"╠{'═'*78}╝")
        
        print(f"\n📅 Reported At: {report['reported_at']}")
        print(f"📝 Reason: {report['reason'] or 'None provided'}")
        
        print(f"\n{'='*80}")
        print(f"QUESTION ({report['subject']}):")
        print(f"{'-'*80}")
        print(textwrap.fill(report['question'], width=80))
        print(f"{'='*80}\n")
        
        print("ACTIONS:")
        print(" [M] Mark as Reviewed (Remove from list)")
        print(" [B] Back to List")
        
        choice = input("\nSelect > ").strip().lower()
        
        if choice == 'b':
            break
        elif choice == 'm':
            db.mark_report_reviewed(report['id'])
            print("\n✅ Marked as reviewed.")
            input("Press Enter...")
            break

if __name__ == "__main__":
    inspect_reports()

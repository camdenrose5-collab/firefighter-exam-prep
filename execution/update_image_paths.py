#!/usr/bin/env python3
"""
Update database image_path references from .png to .webp
Safe: only updates paths that contain '.png' in the mechanical folder
"""

import sqlite3
from pathlib import Path

# Database paths - try local first, then backend
DB_PATHS = [
    Path("backend/data/questions.db"),
    Path("data/firefighter_prep.db"),
]

def update_image_paths():
    # Find the database
    db_path = None
    for path in DB_PATHS:
        if path.exists():
            db_path = path
            break
    
    if not db_path:
        print("❌ Database not found. Checked:")
        for p in DB_PATHS:
            print(f"   - {p}")
        return
    
    print(f"📂 Found database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Find all rows with .png in image_path
    cursor.execute("""
        SELECT id, image_path FROM questions 
        WHERE image_path IS NOT NULL AND image_path LIKE '%.png%'
    """)
    rows = cursor.fetchall()
    
    print(f"📦 Found {len(rows)} questions with PNG image paths")
    
    if len(rows) == 0:
        print("✅ No PNG paths to update!")
        conn.close()
        return
    
    # Update each path
    updated = 0
    for row in rows:
        old_path = row['image_path']
        new_path = old_path.replace('.png', '.webp')
        
        cursor.execute("""
            UPDATE questions SET image_path = ? WHERE id = ?
        """, (new_path, row['id']))
        updated += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*50}")
    print(f"✅ Updated {updated} image paths from .png to .webp")
    print(f"{'='*50}")

if __name__ == "__main__":
    update_image_paths()

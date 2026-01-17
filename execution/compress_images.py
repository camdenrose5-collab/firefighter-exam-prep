#!/usr/bin/env python3
"""
Safe PNG to WebP compression script.
- Keeps original PNGs in backup directory
- Creates WebP versions with quality optimization
- Reports size savings
"""

import os
from pathlib import Path
from PIL import Image

# Paths
MECHANICAL_DIR = Path("public/assets/mechanical")
BACKUP_DIR = Path("public/assets/mechanical_png_backup")

def compress_images():
    if not MECHANICAL_DIR.exists():
        print(f"❌ Directory not found: {MECHANICAL_DIR}")
        return

    # Create backup directory
    BACKUP_DIR.mkdir(exist_ok=True)
    
    png_files = list(MECHANICAL_DIR.glob("*.png"))
    print(f"📦 Found {len(png_files)} PNG files to compress")
    
    total_original = 0
    total_compressed = 0
    converted = 0
    
    for png_path in png_files:
        try:
            # Get original size
            original_size = png_path.stat().st_size
            total_original += original_size
            
            # Open and convert to WebP
            img = Image.open(png_path)
            
            # WebP path
            webp_path = png_path.with_suffix(".webp")
            
            # Save as WebP with quality optimization
            img.save(webp_path, "WEBP", quality=80, method=6)
            
            # Get compressed size
            compressed_size = webp_path.stat().st_size
            total_compressed += compressed_size
            
            # Move original to backup
            backup_path = BACKUP_DIR / png_path.name
            png_path.rename(backup_path)
            
            converted += 1
            
            if converted % 50 == 0:
                print(f"   ✅ Converted {converted}/{len(png_files)} images...")
                
        except Exception as e:
            print(f"   ⚠️ Error converting {png_path.name}: {e}")
    
    # Summary
    savings = total_original - total_compressed
    savings_pct = (savings / total_original * 100) if total_original > 0 else 0
    
    print(f"\n{'='*50}")
    print(f"✅ Conversion complete!")
    print(f"   Original:   {total_original / 1024 / 1024:.1f} MB")
    print(f"   Compressed: {total_compressed / 1024 / 1024:.1f} MB")
    print(f"   Saved:      {savings / 1024 / 1024:.1f} MB ({savings_pct:.0f}%)")
    print(f"   Backups:    {BACKUP_DIR}")
    print(f"{'='*50}")

if __name__ == "__main__":
    compress_images()

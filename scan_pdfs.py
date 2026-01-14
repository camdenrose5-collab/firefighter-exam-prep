import os
import subprocess
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PDF_DIR = "data/pdfs"
OUTPUT_FILE = "scan_report.json"

# Thresholds for flagging
IMAGE_DENSITY_THRESHOLD = 2.0  # Images per page
TEXT_DENSITY_THRESHOLD_LOW = 500  # Chars per page (arbitrary low w/ images suggesting scan)
TEXT_DENSITY_THRESHOLD_HIGH = 5000 # Very high text density might indicate complex layouts/tables? (Maybe less useful)

def get_pdf_info(filepath):
    """Run pdfinfo to get basic metadata like page count."""
    try:
        result = subprocess.run(["pdfinfo", filepath], capture_output=True, text=True, check=True)
        info = {}
        for line in result.stdout.splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                info[key.strip()] = val.strip()
        return info
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running pdfinfo on {filepath}: {e}")
        return None

def get_image_count(filepath):
    """Run pdfimages -list to count images."""
    try:
        # -list prints a table of images. We verify one line per image (minus header output)
        result = subprocess.run(["pdfimages", "-list", filepath], capture_output=True, text=True, check=True)
        lines = result.stdout.splitlines()
        # Header is usually 2 lines (header + separator). If existing, image lines follow.
        # "   page   num  type   width height color comp bpc  enc interp  object ID x-ppi y-ppi size ratio"
        # "--------------------------------------------------------------------------------------------"
        image_count = 0
        for line in lines:
            # Heuristic: data lines start with a number (page num)
            parts = line.split()
            if len(parts) > 2 and parts[0].isdigit():
                image_count += 1
        return image_count
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running pdfimages on {filepath}: {e}")
        return 0

def get_text_content_stats(filepath):
    """Run pdftotext to analyze text content."""
    try:
        # extract to stdout
        result = subprocess.run(["pdftotext", filepath, "-"], capture_output=True, text=True, check=True)
        text = result.stdout
        char_count = len(text)
        
        # Simple heuristic for tables: presence of many vertical bars or tabs + newlines? 
        # Or keyword "Table".
        has_table_keywords = "Table " in text or "TABLE " in text
        
        return char_count, has_table_keywords
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running pdftotext on {filepath}: {e}")
        return 0, False

def scan_directory(directory):
    results = []
    
    # Check if directory exists
    if not os.path.isdir(directory):
        logging.error(f"Directory not found: {directory}")
        return []

    files = [f for f in os.listdir(directory) if f.lower().endswith(".pdf")]
    logging.info(f"Found {len(files)} PDF files to scan.")
    
    for filename in files:
        filepath = os.path.join(directory, filename)
        logging.info(f"Scanning {filename}...")
        
        info = get_pdf_info(filepath)
        if not info:
            continue
            
        try:
            pages = int(info.get("Pages", 0))
        except ValueError:
            pages = 0
            
        if pages == 0:
            logging.warning(f"File {filename} has 0 pages or failed to parse pages.")
            continue

        image_count = get_image_count(filepath)
        char_count, has_table_keywords = get_text_content_stats(filepath)
        
        image_density = image_count / pages
        text_density = char_count / pages
        
        flag_image_heavy = image_density > IMAGE_DENSITY_THRESHOLD
        flag_low_text = text_density < TEXT_DENSITY_THRESHOLD_LOW
        
        # "Potential Scan" if high image density + low text density
        is_potential_scan = flag_image_heavy and flag_low_text
        
        file_data = {
            "filename": filename,
            "pages": pages,
            "image_count": image_count,
            "char_count": char_count,
            "image_density": round(image_density, 2),
            "text_density": round(text_density, 2),
            "flags": {
                "image_heavy": flag_image_heavy,
                "low_text": flag_low_text,
                "potential_scan": is_potential_scan,
                "table_keywords": has_table_keywords
            }
        }
        results.append(file_data)
        
    return results

def main():
    print(f"Starting scan of {PDF_DIR}...")
    results = scan_directory(PDF_DIR)
    
    # Filter for interesting findings
    flagged_files = [
        r for r in results 
        if r['flags']['image_heavy'] or r['flags']['low_text'] or r['flags']['potential_scan']
    ]
    
    print("\n--- SCAN COMPLETE ---")
    print(f"Total Files Scanned: {len(results)}")
    print(f"Files Flagged for Review: {len(flagged_files)}")
    
    if flagged_files:
        print("\nPOTENTIAL ISSUES:")
        print(f"{'Filename':<50} | {'Pages':<6} | {'Img/Pg':<8} | {'Chars/Pg':<8} | {'Notes'}")
        print("-" * 100)
        for f in flagged_files:
            notes = []
            if f['flags']['potential_scan']: notes.append("Likely Scan")
            elif f['flags']['image_heavy']: notes.append("Image Heavy")
            if f['flags']['low_text']: notes.append("Low Text")
            
            print(f"{f['filename']:<50} | {f['pages']:<6} | {f['image_density']:<8} | {f['text_density']:<8} | {', '.join(notes)}")
            
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nFull JSON report saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

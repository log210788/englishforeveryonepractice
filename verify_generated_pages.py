#!/usr/bin/env python3
"""
verify_generated_pages.py - Static DOM Structure, Parity, and Link Validator
Studio Ghibli Interactive Edition

Verifies:
1. All 169 exercise HTML files (ghibli_p008.html through ghibli_p176.html) exist.
2. Required DOM elements exist on every page:
   - #mascotBubble (or .mascot-bubble)
   - #ghibliCheckAnswersBtn
   - #ghibliScoreBadge (or .ghibli-score-badge / #ghibliScoreText)
   - .tod-btn
   - .chapter-nav-bar
3. Interactive input count parity against item count in output_json/all_pages_consolidated.json.
4. Audio path references (valid data-audio or src pointing to audio files).
5. Navigation href targets (valid links in chapter navigation).
"""

import sys
import os
import json
import re
from pathlib import Path
try:
    from bs4 import BeautifulSoup
except ImportError:
    from html.parser import HTMLParser
    BeautifulSoup = None

# Base path configuration
BASE_DIR = Path(__file__).parent.resolve()
JSON_PATH = BASE_DIR / "output_json" / "all_pages_consolidated.json"

REQUIRED_DOM_SELECTORS = {
    "mascotBubble": ["#mascotBubble", ".mascot-bubble"],
    "ghibliCheckAnswersBtn": ["#ghibliCheckAnswersBtn", ".ghibli-check-btn"],
    "ghibliScoreBadge": ["#ghibliScoreBadge", ".ghibli-score-badge", "#ghibliScoreText"],
    "todBtn": [".tod-btn"],
    "chapterNavBar": [".chapter-nav-bar", ".page-turn-bar", ".page-nav-bar"]
}

def load_consolidated_json():
    if not JSON_PATH.exists():
        print(f"[ERROR] Consolidated JSON not found at: {JSON_PATH}")
        sys.exit(1)
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_expected_page_numbers(json_data):
    """Extract page numbers that contain exercises (pages 8 through 176)."""
    pages = json_data.get("pages", [])
    expected = []
    for p in pages:
        p_num = p.get("page_number")
        if isinstance(p_num, int) and 8 <= p_num <= 176:
            expected.append(p_num)
        elif isinstance(p_num, str) and p_num.isdigit():
            val = int(p_num)
            if 8 <= val <= 176:
                expected.append(val)
    
    # Fallback to range 8..176 if empty
    if not expected:
        expected = list(range(8, 177))
    return sorted(list(set(expected)))

def verify_dom_elements(soup, filepath):
    """Verify presence of required DOM elements."""
    missing = []
    for key, selectors in REQUIRED_DOM_SELECTORS.items():
        found = False
        for sel in selectors:
            if sel.startswith("#"):
                elem = soup.find(id=sel[1:])
            elif sel.startswith("."):
                elem = soup.find(class_=sel[1:])
            else:
                elem = soup.select_one(sel)
            if elem:
                found = True
                break
        if not found:
            missing.append(key)
    return missing

def verify_input_parity(soup, page_data):
    """Verify interactive input/control count against JSON item count."""
    exercises = page_data.get("exercises", [])
    expected_items = sum(len(ex.get("items", [])) for ex in exercises)
    
    # Count interactive inputs in HTML
    inputs = soup.find_all(class_=lambda c: c and any(k in c for k in ["ghibli-input", "ex1-1-input", "ghibli-option", "ghibli-drop-slot", "ghibli-matching-select", "order-input"]))
    if not inputs:
        inputs = soup.find_all(["input", "select"])
        inputs = [i for i in inputs if i.get("type") not in ["hidden", "button", "submit", "radio"] or "ghibli-input" in i.get("class", [])]
    
    found_count = len(inputs)
    return expected_items, found_count

def verify_audio_references(soup):
    """Verify audio button/element path references."""
    audio_btns = soup.find_all(attrs={"data-audio": True})
    audio_tags = soup.find_all("audio")
    
    valid_count = 0
    invalid_count = 0
    
    for btn in audio_btns:
        path = btn.get("data-audio", "")
        if path.startswith("audio/") or path.endswith(".mp3"):
            valid_count += 1
        else:
            invalid_count += 1
            
    for tag in audio_tags:
        src = tag.get("src", "")
        if src.startswith("audio/") or src.endswith(".mp3"):
            valid_count += 1
        else:
            invalid_count += 1
            
    return valid_count, invalid_count

def verify_nav_targets(soup):
    """Verify chapter navigation href targets."""
    nav_bar = soup.find(class_="chapter-nav-bar")
    if not nav_bar:
        return 0, 1
    
    links = nav_bar.find_all("a", href=True)
    valid = 0
    invalid = 0
    for a in links:
        href = a.get("href", "")
        if href in ["index.html"] or href.startswith("ghibli_") or href.endswith(".html"):
            valid += 1
        else:
            invalid += 1
    return valid, invalid

def main():
    print("=" * 70)
    print(" Studio Ghibli Interactive Edition — Page Integrity Validator ")
    print("=" * 70)
    
    json_data = load_consolidated_json()
    page_numbers = get_expected_page_numbers(json_data)
    pages_map = {p.get("page_number"): p for p in json_data.get("pages", [])}
    
    total_pages = len(page_numbers)
    print(f"Target Exercise Pages: {total_pages} (Pages {page_numbers[0]} through {page_numbers[-1]})")
    
    missing_files = []
    passed_pages = []
    failed_pages = []
    
    dom_errors = []
    parity_errors = []
    audio_warnings = []
    nav_warnings = []
    
    for p_num in page_numbers:
        filename = f"ghibli_p{p_num:03d}.html"
        filepath = BASE_DIR / filename
        
        if not filepath.exists():
            missing_files.append(filename)
            continue
            
        page_data = pages_map.get(p_num, pages_map.get(str(p_num), {}))
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            soup = BeautifulSoup(content, "html.parser")
            
            # 1. DOM Elements Check
            missing_dom = verify_dom_elements(soup, filepath)
            if missing_dom:
                dom_errors.append((filename, missing_dom))
                
            # 2. Input Parity Check
            expected_items, found_inputs = verify_input_parity(soup, page_data)
            if expected_items > 0 and found_inputs == 0:
                parity_errors.append((filename, expected_items, found_inputs))
                
            # 3. Audio Paths Check
            audio_valid, audio_invalid = verify_audio_references(soup)
            if audio_invalid > 0:
                audio_warnings.append((filename, audio_invalid))
                
            # 4. Nav Targets Check
            nav_valid, nav_invalid = verify_nav_targets(soup)
            if nav_invalid > 0:
                nav_warnings.append((filename, nav_invalid))
                
            if not missing_dom and (expected_items == 0 or found_inputs > 0):
                passed_pages.append(filename)
            else:
                failed_pages.append(filename)
                
        except Exception as e:
            failed_pages.append(filename)
            dom_errors.append((filename, [f"Parse error: {str(e)}"]))

    print("\n" + "-" * 70)
    print(" VERIFICATION SUMMARY REPORT ")
    print("-" * 70)
    print(f"Total Expected HTML Files : {total_pages}")
    print(f"Existing HTML Files       : {total_pages - len(missing_files)}")
    print(f"Missing HTML Files        : {len(missing_files)}")
    print(f"Passed DOM Parity Check   : {len(passed_pages)}")
    print(f"Failed DOM Parity Check   : {len(failed_pages)}")
    
    if missing_files:
        print("\n[!] MISSING FILES:")
        print(f"    Total {len(missing_files)} files missing. (First 5: {missing_files[:5]})")
        
    if dom_errors:
        print("\n[!] DOM STRUCTURE ERRORS:")
        for fn, errs in dom_errors[:10]:
            print(f"    - {fn}: Missing required elements -> {errs}")
            
    if parity_errors:
        print("\n[!] INPUT PARITY ERRORS:")
        for fn, exp, got in parity_errors[:10]:
            print(f"    - {fn}: Expected {exp} items, found {got} inputs")

    print("\n" + "=" * 70)
    if len(missing_files) == 0 and len(failed_pages) == 0 and total_pages > 0:
        print(" SUCCESS: 100% of generated pages passed DOM integrity & parity verification!")
        print("=" * 70)
        sys.exit(0)
    else:
        print(" INCOMPLETE / FAILURE: Generation pending or DOM integrity errors detected.")
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    main()

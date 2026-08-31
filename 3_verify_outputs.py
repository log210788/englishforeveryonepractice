#!/usr/bin/env python3
"""
Step 4: Verification & Consolidation Script
Verifies generated JSON files for required fields, non-emptiness, exercise counts,
and produces a comprehensive terminal summary report and consolidated output JSON.
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import List, Dict, Any


def parse_page_number(filename: str) -> int:
    """Extract page number from filename."""
    match = re.search(r"\d+", filename)
    return int(match.group()) if match else 0


def verify_and_consolidate(
    output_dir: Path,
    images_dir: Path,
    logs_dir: Path,
    consolidate_filename: str = "all_pages_consolidated.json"
):
    """
    Verifies all page JSON files and generates terminal report + consolidated JSON file.
    """
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    json_files = sorted(
        [f for f in output_dir.glob("page_*.json") if f.name != consolidate_filename and not f.name.endswith("_bbox.json")],
        key=lambda p: parse_page_number(p.name)
    )

    image_files = list(images_dir.glob("*.png")) if images_dir.exists() else []
    total_images_count = len(image_files)

    failed_log_path = logs_dir / "failed_pages.json"
    failed_log = []
    if failed_log_path.exists():
        try:
            with open(failed_log_path, "r", encoding="utf-8") as f:
                failed_log = json.load(f)
        except Exception:
            pass

    valid_pages: List[Dict[str, Any]] = []
    corrupted_pages: List[str] = []
    empty_pages: List[str] = []
    missing_keys_pages: List[str] = []

    exercise_type_counter = Counter()
    total_exercises_count = 0
    total_question_items_count = 0

    required_keys = {"page_number", "exercises"}

    print("🔍 Scanning and verifying JSON output files...\n")

    for json_file in json_files:
        if json_file.stat().st_size == 0:
            empty_pages.append(json_file.name)
            continue

        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            corrupted_pages.append(json_file.name)
            continue

        # Check required schema keys
        if not required_keys.issubset(data.keys()):
            missing_keys_pages.append(json_file.name)
            continue

        valid_pages.append(data)

        # Count exercises and items
        exercises = data.get("exercises", [])
        total_exercises_count += len(exercises)

        for ex in exercises:
            ex_type = ex.get("exercise_type", "unknown")
            exercise_type_counter[ex_type] += 1
            items = ex.get("items", [])
            total_question_items_count += len(items)

    total_json_files = len(json_files)
    successful_extractions = len(valid_pages)
    failed_extractions = len(empty_pages) + len(corrupted_pages) + len(missing_keys_pages) + len(failed_log)

    # Output Consolidated File
    consolidated_path = output_dir / consolidate_filename
    consolidated_data = {
        "metadata": {
            "total_pages_converted": total_images_count,
            "total_json_files": total_json_files,
            "successful_pages": successful_extractions,
            "failed_pages": failed_extractions,
            "total_exercises": total_exercises_count,
            "total_question_items": total_question_items_count,
            "exercise_types_breakdown": dict(exercise_type_counter)
        },
        "pages": valid_pages
    }

    with open(consolidated_path, "w", encoding="utf-8") as f:
        json.dump(consolidated_data, f, indent=2, ensure_ascii=False)

    # Printable Terminal Report
    print("=" * 60)
    print("      ENGLISG FOR EVERYONE - PIPELINE VERIFICATION REPORT     ")
    print("=" * 60)
    print(f" 📸 Total Page Images (images/):         {total_images_count if total_images_count else 'N/A'}")
    print(f" 📄 Total JSON Files Outputted:          {total_json_files}")
    print(f" ✅ Successfully Verified Pages:        {successful_extractions}")
    print(f" ❌ Failed / Corrupted / Missing Pages:  {failed_extractions}")
    print("-" * 60)
    print(f" 📚 Total Exercises Extracted:           {total_exercises_count}")
    print(f" ❓ Total Question Items Extracted:       {total_question_items_count}")
    print("-" * 60)
    print(" 📊 Breakdown by Exercise Type:")
    for ex_type, count in exercise_type_counter.most_common():
        print(f"    - {ex_type:<22}: {count} exercises")

    if empty_pages or corrupted_pages or missing_keys_pages:
        print("\n ⚠️ Detailed Issues Found:")
        if empty_pages:
            print(f"    - Empty JSON files ({len(empty_pages)}): {', '.join(empty_pages[:5])}")
        if corrupted_pages:
            print(f"    - Corrupted JSON files ({len(corrupted_pages)}): {', '.join(corrupted_pages[:5])}")
        if missing_keys_pages:
            print(f"    - Missing Keys ({len(missing_keys_pages)}): {', '.join(missing_keys_pages[:5])}")

    print("-" * 60)
    print(f" 💾 Consolidated Output Saved: {consolidated_path}")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Verify generated JSON files and create consolidated output report.")
    parser.add_argument("--output-dir", type=str, default="output_json", help="Directory containing JSON files.")
    parser.add_argument("--images-dir", type=str, default="images", help="Directory containing image files.")
    parser.add_argument("--logs-dir", type=str, default="logs", help="Directory containing log files.")
    parser.add_argument("--consolidate-name", type=str, default="all_pages_consolidated.json", help="Consolidated output filename.")
    args = parser.parse_args()

    verify_and_consolidate(
        output_dir=Path(args.output_dir),
        images_dir=Path(args.images_dir),
        logs_dir=Path(args.logs_dir),
        consolidate_filename=args.consolidate_name
    )


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    main()
